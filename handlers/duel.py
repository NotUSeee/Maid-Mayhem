"""/maid duel @opponent — PvP duels.

Flow:
    1. /maid duel @B           Challenger A sends an ephemeral confirmation;
                               a public message in the channel @-mentions B
                               with [Accept] / [Decline] buttons.
    2. B clicks Accept         Battle starts; state is created in KV under a
                               duel_id; first turn is rendered publicly with
                               action buttons. Only the current turn_owner
                               can act (button clicks from the other side
                               get an ephemeral "not your turn" reply).
    3. Turn loop               Active user clicks Attack / Defend / Flee /
                               Ability. State advances, turn_owner flips.
    4. End                     Rewards credited to KV profile + mm_player_stats;
                               battle_log entry written for both players;
                               duel state cleared.

All messages in this flow are non-ephemeral (visible to both players in
the channel) because there's no other way to keep the two clients in
sync without additional capabilities.
"""
from __future__ import annotations

from typing import Any

from mmo_maid_sdk import ActionRow, Button, Context

from engine import abilities as abilities_engine
from engine import manor as manor_engine
from engine import pvp as pvp_engine
from engine import quests as quests_engine
from engine import ranks as ranks_engine
from store import duel_state, kv, sql as store_sql
from ui import embeds


# ── Helpers ─────────────────────────────────────────────────────────────────

def _extract_user_option(event: dict, name: str = "opponent") -> str | None:
    """Find the resolved user_id for a USER-typed slash option named `name`."""
    opts = event.get("command_options") or []
    if not opts:
        return None
    sub = opts[0]
    for o in (sub.get("options") or []):
        if o.get("name") == name:
            v = o.get("value")
            return str(v) if v is not None else None
    return None


def _resolve_name(ctx: Context, user_id: str) -> str:
    try:
        m = ctx.discord.get_member(user_id=user_id)
    except Exception:
        return user_id
    if not isinstance(m, dict):
        return user_id
    return (m.get("display_name") or m.get("username") or m.get("name") or user_id)


def _challenge_components(duel_id: str) -> ActionRow:
    return ActionRow(
        Button("✅ Accept", custom_id=f"mm:duel:accept:{duel_id}", style="success"),
        Button("❌ Decline", custom_id=f"mm:duel:decline:{duel_id}", style="danger"),
    )


def _turn_components(state: dict[str, Any]) -> list[ActionRow]:
    """Two rows: main actions + per-maid ability buttons for the active side."""
    terminal = state.get("result") is not None
    owner = state.get("turn_owner")
    side = state.get(owner) if owner else {}
    team = side.get("team") or []
    cds = side.get("ability_cooldowns") or [0] * len(team)

    main = ActionRow(
        Button("⚔ Attack", custom_id="mm:duel:act:attack", style="danger",  disabled=terminal),
        Button("🛡 Defend", custom_id="mm:duel:act:defend", style="primary", disabled=terminal),
        Button("🏃 Flee",   custom_id="mm:duel:act:flee",   style="secondary", disabled=terminal),
    )

    ability_buttons: list[Button] = []
    for i, m in enumerate(team):
        ability = abilities_engine.get(str(m.get("ability_id", "")))
        cd = int(cds[i]) if i < len(cds) else 0
        alive = int(m.get("poise", 0)) > 0
        if ability is None:
            label, disabled = f"M{i + 1}: —", True
        elif not alive:
            label, disabled = f"M{i + 1}: KO", True
        elif cd > 0:
            label, disabled = f"M{i + 1}: {ability.name} ({cd})", True
        else:
            label, disabled = f"M{i + 1}: {ability.name}", terminal
        ability_buttons.append(Button(
            label[:80], custom_id=f"mm:duel:act:ability:{i}",
            style="success", disabled=disabled,
        ))
    rows = [main]
    if ability_buttons:
        rows.append(ActionRow(*ability_buttons))
    return rows


def _award_and_log(ctx: Context, state: dict[str, Any]) -> None:
    """Credit rewards and write battle_log rows for both sides. Idempotent
    by virtue of being called once on terminal state and then state cleared.
    """
    result = state.get("result", "")
    a = state["a"]; b = state["b"]
    if result in ("a_wins", "b_fled"):
        winner, loser = a, b
    elif result in ("b_wins", "a_fled"):
        winner, loser = b, a
    else:
        return

    base_coins_win, base_xp_win   = 60, 50
    base_coins_lose, base_xp_lose = 0, 10

    coins_win, xp_win = manor_engine.reward_bonuses_for_user(
        ctx, winner["user_id"], coins=base_coins_win, xp=base_xp_win, is_battle_win=True,
    )
    coins_lose, xp_lose = manor_engine.reward_bonuses_for_user(
        ctx, loser["user_id"], coins=base_coins_lose, xp=base_xp_lose, is_battle_win=False,
    )

    kv.add_rewards(ctx, winner["user_id"], coins=coins_win,  xp=xp_win,  won=True)
    kv.add_rewards(ctx, loser["user_id"],  coins=coins_lose, xp=xp_lose, won=False)
    store_sql.record_battle(ctx, winner["user_id"], result="win",  coins=coins_win,  xp=xp_win)
    store_sql.record_battle(ctx, loser["user_id"],  result="loss", coins=coins_lose, xp=xp_lose)

    # PvP ranked-points: winner +25, loser -10 (engine floors at 0).
    ranks_engine.award_rp(ctx, winner["user_id"], 25)
    ranks_engine.award_rp(ctx, loser["user_id"], -10)

    # Polish: winner-only premium currency trickle.
    kv.add_polish(ctx, winner["user_id"], 2)

    # Quest counter — only counted on a true win, not a forfeit-by-flee.
    quests_engine.bump(ctx, winner["user_id"], "pvp_win")

    # Card XP for everyone who fought. PvP pays more than PvE.
    win_deck = kv.load_deck(ctx, winner["user_id"])
    lose_deck = kv.load_deck(ctx, loser["user_id"])
    win_levelups = store_sql.grant_deck_maid_xp(ctx, winner["user_id"], win_deck, 80)
    lose_levelups = store_sql.grant_deck_maid_xp(ctx, loser["user_id"],  lose_deck, 20)
    state.setdefault("_levelups", {})
    state["_levelups"][winner["user_id"]] = win_levelups
    state["_levelups"][loser["user_id"]]  = lose_levelups


# ── /maid duel @opponent ────────────────────────────────────────────────────

def run(ctx: Context, event: dict) -> None:
    challenger_id = str(event.get("user_id") or "")
    challenger_name = event.get("user_name") or "Maid"
    target_id = _extract_user_option(event, "opponent")

    if not challenger_id:
        ctx.interaction.respond(content="Could not identify you.", ephemeral=True)
        return
    if not target_id:
        ctx.interaction.respond(content="Pick an opponent — `/maid duel opponent:@user`.", ephemeral=True)
        return
    if target_id == challenger_id:
        ctx.interaction.respond(content="You can't duel yourself.", ephemeral=True)
        return

    # Both players need a non-empty deck.
    challenger_deck = kv.load_deck(ctx, challenger_id)
    if not [c for c in (challenger_deck.get("maids") or []) if c]:
        ctx.interaction.respond(
            content="Your deck is empty. Build one with `/maid deck` first.",
            ephemeral=True,
        )
        return
    target_deck = kv.load_deck(ctx, target_id)
    if not [c for c in (target_deck.get("maids") or []) if c]:
        ctx.interaction.respond(
            content=f"<@{target_id}> doesn't have a deck yet — they need to run `/maid deck`.",
            ephemeral=True,
        )
        return

    # Block duplicate challenges
    if duel_state.get_pending_for(ctx, challenger_id):
        ctx.interaction.respond(
            content="You already have a pending challenge. Wait for it to resolve.",
            ephemeral=True,
        )
        return
    if duel_state.get_pending_for(ctx, target_id):
        ctx.interaction.respond(
            content=f"<@{target_id}> already has a pending challenge.",
            ephemeral=True,
        )
        return
    if duel_state.get_active_for(ctx, challenger_id) or duel_state.get_active_for(ctx, target_id):
        ctx.interaction.respond(
            content="One of you is already in a duel.",
            ephemeral=True,
        )
        return

    target_name = _resolve_name(ctx, target_id)
    duel_id = duel_state.new_duel_id()
    pending_state = {
        "duel_id": duel_id,
        "channel_id": str(event.get("channel_id") or ""),
        "challenger": {"user_id": challenger_id, "user_name": challenger_name},
        "target":     {"user_id": target_id,     "user_name": target_name},
        "result": "pending",
    }
    duel_state.save(ctx, duel_id, pending_state, ttl_seconds=duel_state.PENDING_TTL_S)
    duel_state.set_pending_for(ctx, challenger_id, duel_id)
    duel_state.set_pending_for(ctx, target_id, duel_id)

    ctx.interaction.respond(
        content=f"<@{target_id}>",
        embeds=[embeds.duel_challenge_embed(
            challenger_id, challenger_name, target_id, target_name,
            expires_in_s=duel_state.PENDING_TTL_S,
        )],
        components=[_challenge_components(duel_id)],
        ephemeral=False,
    )


# ── Component handlers ──────────────────────────────────────────────────────

def on_component(ctx: Context, event: dict, tail: list[str]) -> None:
    if not tail:
        return
    action = tail[0]
    clicker_id = str(event.get("user_id") or "")

    if action == "accept":
        if len(tail) < 2:
            return
        duel_id = tail[1]
        _handle_accept(ctx, event, clicker_id, duel_id)
        return

    if action == "decline":
        if len(tail) < 2:
            return
        duel_id = tail[1]
        _handle_decline(ctx, event, clicker_id, duel_id)
        return

    if action == "act":
        if len(tail) < 2:
            return
        engine_action = tail[1]
        if engine_action == "ability" and len(tail) >= 3:
            engine_action = f"ability:{tail[2]}"
        _handle_turn(ctx, event, clicker_id, engine_action)
        return


def _handle_accept(ctx: Context, event: dict, clicker_id: str, duel_id: str) -> None:
    pending = duel_state.load(ctx, duel_id)
    if not pending or pending.get("result") != "pending":
        ctx.interaction.respond(content="That challenge has expired.", ephemeral=True)
        return
    if clicker_id != pending["target"]["user_id"]:
        ctx.interaction.respond(content="Only the challenged player can accept.", ephemeral=True)
        return

    a_id = pending["challenger"]["user_id"]; a_name = pending["challenger"]["user_name"]
    b_id = pending["target"]["user_id"];     b_name = pending["target"]["user_name"]
    a_deck = kv.load_deck(ctx, a_id)
    b_deck = kv.load_deck(ctx, b_id)
    if not [c for c in (a_deck.get("maids") or []) if c]:
        ctx.interaction.respond(content="The challenger's deck is empty.", ephemeral=True)
        _cleanup_pointers(ctx, a_id, b_id)
        duel_state.clear(ctx, duel_id)
        return
    if not [c for c in (b_deck.get("maids") or []) if c]:
        ctx.interaction.respond(content="Your deck is empty — set one with `/maid deck`.", ephemeral=True)
        return

    state = pvp_engine.start_duel(
        duel_id, pending.get("channel_id", ""),
        a_id, a_name, a_deck,
        b_id, b_name, b_deck,
        ctx=ctx,
    )
    duel_state.save(ctx, duel_id, state)
    duel_state.clear_pending_for(ctx, a_id)
    duel_state.clear_pending_for(ctx, b_id)
    duel_state.set_active_for(ctx, a_id, duel_id)
    duel_state.set_active_for(ctx, b_id, duel_id)

    ctx.interaction.respond(
        content=f"<@{a_id}> vs <@{b_id}>",
        embeds=[embeds.duel_embed(state)],
        components=_turn_components(state),
        ephemeral=False,
    )


def _handle_decline(ctx: Context, event: dict, clicker_id: str, duel_id: str) -> None:
    pending = duel_state.load(ctx, duel_id)
    if not pending or pending.get("result") != "pending":
        ctx.interaction.respond(content="That challenge has expired.", ephemeral=True)
        return
    if clicker_id != pending["target"]["user_id"]:
        ctx.interaction.respond(content="Only the challenged player can decline.", ephemeral=True)
        return
    a_id = pending["challenger"]["user_id"]
    b_id = pending["target"]["user_id"]
    _cleanup_pointers(ctx, a_id, b_id)
    duel_state.clear(ctx, duel_id)
    ctx.interaction.respond(
        content=f"<@{b_id}> declined <@{a_id}>'s duel.",
        ephemeral=False,
    )


def _handle_turn(ctx: Context, event: dict, clicker_id: str, engine_action: str) -> None:
    duel_id = duel_state.get_active_for(ctx, clicker_id)
    if not duel_id:
        ctx.interaction.respond(content="No active duel.", ephemeral=True)
        return
    state = duel_state.load(ctx, duel_id)
    if not state or state.get("result"):
        ctx.interaction.respond(content="That duel is no longer active.", ephemeral=True)
        return

    owner = state.get("turn_owner")
    if clicker_id != state[owner]["user_id"]:
        ctx.interaction.respond(content="It's not your turn yet.", ephemeral=True)
        return

    # Dedup hard double-clicks on the same turn
    if not ctx.ephemeral.dedup(
        f"mm:duel:act:{duel_id}:{state['turn']}:{owner}:{engine_action}",
        ttl_seconds=2,
    ):
        return

    new_state = pvp_engine.take_turn(state, engine_action)
    duel_state.save(ctx, duel_id, new_state)

    if new_state.get("result"):
        _award_and_log(ctx, new_state)
        duel_state.clear_active_for(ctx, new_state["a"]["user_id"])
        duel_state.clear_active_for(ctx, new_state["b"]["user_id"])
        duel_state.clear(ctx, duel_id)
        ctx.interaction.respond(
            content=f"<@{new_state['a']['user_id']}> <@{new_state['b']['user_id']}>",
            embeds=[embeds.duel_embed(new_state), embeds.duel_result_embed(new_state)],
            components=[],
            ephemeral=False,
        )
        return

    ctx.interaction.respond(
        content=f"<@{new_state[new_state['turn_owner']]['user_id']}> — your turn.",
        embeds=[embeds.duel_embed(new_state)],
        components=_turn_components(new_state),
        ephemeral=False,
    )


def _cleanup_pointers(ctx: Context, *user_ids: str) -> None:
    for uid in user_ids:
        if not uid:
            continue
        duel_state.clear_pending_for(ctx, uid)
        duel_state.clear_active_for(ctx, uid)
