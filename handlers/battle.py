"""/maid battle — PvE turn-based combat.

Whole-team turns: every round the player picks Attack / Defend / Flee.
All living maids act, then all living enemies counter. Element triangle +
random variance create the swing. Battle state is stored ephemerally per
user; abandoned battles auto-expire after 30 minutes.
"""
from __future__ import annotations

from typing import Any

from mmo_maid_sdk import ActionRow, Button, Context

from engine import abilities as abilities_engine
from engine import battle as battle_engine
from engine import manor as manor_engine
from engine import ranks as ranks_engine
from store import battle_state, kv, sql as store_sql
from ui import embeds


def _action_rows(state: dict[str, Any]) -> list[ActionRow]:
    """Two rows: main actions + per-maid ability buttons."""
    terminal = state.get("result") is not None
    main = ActionRow(
        Button("⚔ Attack", custom_id="mm:battle:attack",
               style="danger", disabled=terminal),
        Button("🛡 Defend", custom_id="mm:battle:defend",
               style="primary", disabled=terminal),
        Button("🏃 Flee",   custom_id="mm:battle:flee",
               style="secondary", disabled=terminal),
    )

    # One ability button per player maid slot. Disabled when the maid is
    # KO'd, the ability is on cooldown, or the battle has ended.
    player = state.get("player_team") or []
    cooldowns = state.get("ability_cooldowns") or [0] * len(player)
    ability_buttons: list[Button] = []
    for i, m in enumerate(player):
        ability = abilities_engine.get(str(m.get("ability_id", "")))
        cd = int(cooldowns[i]) if i < len(cooldowns) else 0
        alive = int(m.get("poise", 0)) > 0
        if ability is None:
            label = f"M{i + 1}: —"
            disabled = True
        elif not alive:
            label = f"M{i + 1}: KO"
            disabled = True
        elif cd > 0:
            label = f"M{i + 1}: {ability.name} ({cd})"
            disabled = True
        else:
            label = f"M{i + 1}: {ability.name}"
            disabled = terminal
        ability_buttons.append(Button(
            label[:80],
            custom_id=f"mm:battle:ability:{i}",
            style="success",
            disabled=disabled,
        ))

    rows: list[ActionRow] = [main]
    if ability_buttons:
        rows.append(ActionRow(*ability_buttons))
    return rows


def _finalize_if_terminal(ctx: Context, state: dict[str, Any]) -> dict[str, Any] | None:
    """If state is terminal, write rewards + return the result embed dict.
    Returns None if the battle is still in progress."""
    result = state.get("result")
    if not result:
        return None
    user_id = str(state.get("user_id") or "")
    rewards = state.get("rewards") or {"coins": 0, "xp": 0}
    coins = int(rewards.get("coins", 0))
    xp = int(rewards.get("xp", 0))
    won = (result == "win")
    levelups: list[tuple[str, int, int]] = []
    if user_id:
        # Apply manor bonuses (Tea Room XP %, Kitchen coin %, Training Hall
        # flat XP on wins) before crediting the player.
        coins, xp = manor_engine.reward_bonuses_for_user(
            ctx, user_id, coins=coins, xp=xp, is_battle_win=won,
        )
        kv.add_rewards(ctx, user_id, coins=coins, xp=xp, won=won)
        store_sql.record_battle(
            ctx, user_id, result=result, coins=coins, xp=xp,
        )
        # Card XP: every deck maid gets a share regardless of survival.
        # Win pays better than loss / flee.
        per_maid_xp = 50 if won else (10 if result == "loss" else 5)
        deck = kv.load_deck(ctx, user_id)
        levelups = store_sql.grant_deck_maid_xp(ctx, user_id, deck, per_maid_xp)
        if won:
            ranks_engine.award_rp(ctx, user_id, 5)   # PvE win: +5 RP
        battle_state.clear(ctx, user_id)
    return embeds.battle_result_embed(state, won=won, coins=coins, xp=xp, levelups=levelups)


def run(ctx: Context, event: dict) -> None:
    """Start a new battle (or resume if one is already in flight)."""
    user_id = str(event.get("user_id") or "")
    if not user_id:
        ctx.interaction.respond(content="Could not identify user.", ephemeral=True)
        return

    deck = kv.load_deck(ctx, user_id)
    if not [c for c in (deck.get("maids") or []) if c]:
        ctx.interaction.respond(
            content="Your deck is empty. Build one with `/maid deck` first.",
            ephemeral=True,
        )
        return

    # Resume if a battle is still in flight
    existing = battle_state.load(ctx, user_id)
    if existing and not existing.get("result"):
        ctx.interaction.respond(
            content="Resuming your battle in progress.",
            embeds=[embeds.battle_embed(existing)],
            components=[_action_row(existing)],
            ephemeral=True,
        )
        return

    state = battle_engine.start_battle(user_id, deck, ctx=ctx)
    if state.get("result") == "no_deck":
        ctx.interaction.respond(
            content="Your deck has no maids. Set one with `/maid deck`.",
            ephemeral=True,
        )
        return

    battle_state.save(ctx, user_id, state)
    ctx.interaction.respond(
        embeds=[embeds.battle_embed(state)],
        components=_action_rows(state),
        ephemeral=True,
    )


def on_component(ctx: Context, event: dict, tail: list[str]) -> None:
    if not tail:
        return
    head = tail[0]

    # Resolve the engine-level action string from the button's custom_id tail.
    # Buttons use "mm:battle:attack" | "defend" | "flee" | "ability:<idx>".
    if head == "ability" and len(tail) >= 2:
        try:
            int(tail[1])
        except ValueError:
            return
        action = f"ability:{tail[1]}"
    elif head in ("attack", "defend", "flee"):
        action = head
    else:
        return

    user_id = str(event.get("user_id") or "")
    state = battle_state.load(ctx, user_id)
    if not state or state.get("result"):
        ctx.interaction.respond(
            content="No battle in progress. Start one with `/maid battle`.",
            ephemeral=True,
        )
        return

    # Drop accidental double-clicks within ~2s
    if not ctx.ephemeral.dedup(f"mm:battle:click:{user_id}:{state['turn']}:{action}",
                                ttl_seconds=2):
        return

    new_state = battle_engine.take_turn(state, action)
    final_embed = _finalize_if_terminal(ctx, new_state)

    if final_embed is not None:
        ctx.interaction.respond(
            embeds=[embeds.battle_embed(new_state), final_embed],
            components=[],
            ephemeral=True,
        )
        return

    battle_state.save(ctx, user_id, new_state)
    ctx.interaction.respond(
        embeds=[embeds.battle_embed(new_state)],
        components=_action_rows(new_state),
        ephemeral=True,
    )
