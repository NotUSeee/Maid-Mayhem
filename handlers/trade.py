"""/maid trade @opponent — player-to-player card swaps.

Flow:
    1. /maid trade @B           A's challenge posts publicly, mentioning B
                                with [Accept] / [Decline] buttons.
    2. B clicks Accept          Trade panel opens publicly; both sides have
                                empty offers. Each user sees the same panel.
    3. Edit phase               Buttons: [Add Maid] [Add Tool] [Clear] [Lock]
                                [Cancel]. Add buttons open a SelectMenu of
                                the clicker's inventory. Lock pins your side.
    4. Confirm                  Once both sides locked, a [Confirm Trade]
                                button appears. Either party can press it.
                                Server re-validates ownership, then runs the
                                atomic-ish swap via engine/trade.execute_swap.

Off-trade clicks get an ephemeral "this isn't your trade" reply.
Either party can Cancel at any phase; the trade is wiped.
"""
from __future__ import annotations

from typing import Any

from mmo_maid_sdk import ActionRow, Button, Context, SelectMenu, SelectOption

from data import maids as maids_data
from data import rarities as rarities_data
from data import tools as tools_data
from engine import achievements as ach_engine
from engine import trade as trade_engine
from store import kv, sql as store_sql, trade_state
from ui import embeds


# ── User extraction + name resolution ───────────────────────────────────────

def _extract_user_option(event: dict, name: str = "opponent") -> str | None:
    opts = event.get("command_options") or []
    if not opts:
        return None
    sub = opts[0]
    for o in (sub.get("options") or []):
        if o.get("name") == name:
            return str(o.get("value") or "") or None
    return None


def _resolve_name(ctx: Context, user_id: str) -> str:
    try:
        m = ctx.discord.get_member(user_id=user_id)
    except Exception:
        return user_id
    if not isinstance(m, dict):
        return user_id
    return m.get("display_name") or m.get("username") or m.get("name") or user_id


# ── UI builders ─────────────────────────────────────────────────────────────

def _challenge_components(trade_id: str) -> ActionRow:
    return ActionRow(
        Button("✅ Accept",  custom_id=f"mm:trade:accept:{trade_id}",  style="success"),
        Button("❌ Decline", custom_id=f"mm:trade:decline:{trade_id}", style="danger"),
    )


def _panel_components(state: dict[str, Any]) -> list[ActionRow]:
    """Row 1: Add Maid / Add Tool / Clear Mine / Lock / Cancel.
       Row 2: Confirm (only when both sides locked)."""
    both = trade_engine.both_locked(state)
    rows = [
        ActionRow(
            Button("➕ Maid",  custom_id="mm:trade:add:maid",  style="secondary", disabled=both),
            Button("➕ Tool",  custom_id="mm:trade:add:tool",  style="secondary", disabled=both),
            Button("🧹 Clear", custom_id="mm:trade:clear",     style="secondary", disabled=both),
            Button("🔒 Lock",  custom_id="mm:trade:lock",      style="primary",   disabled=both),
            Button("✖ Cancel", custom_id="mm:trade:cancel",    style="danger"),
        ),
    ]
    if both:
        rows.append(ActionRow(
            Button("✅ Confirm trade", custom_id="mm:trade:confirm", style="success"),
        ))
    return rows


def _add_card_picker(ctx: Context, user_id: str, want_type: str) -> ActionRow | None:
    """SelectMenu of inventory cards of `want_type` (`maid` or `tool`)."""
    rows = store_sql.get_inventory(ctx, user_id)
    options = []
    for r in rows:
        if r.get("card_type") != want_type:
            continue
        owned = int(r.get("count", 0))
        if owned <= 0:
            continue
        cid = str(r.get("card_id", ""))
        if want_type == "maid":
            m = maids_data.BY_ID.get(cid)
            if not m:
                continue
            r_rarity = rarities_data.BY_ID.get(m.rarity)
            tag = r_rarity.emoji if r_rarity else ""
            options.append(SelectOption(
                f"{tag} {m.name}"[:100], cid,
                description=f"You have {owned}"[:100],
            ))
        else:
            t = tools_data.BY_ID.get(cid)
            if not t:
                continue
            r_rarity = rarities_data.BY_ID.get(t.rarity)
            tag = r_rarity.emoji if r_rarity else ""
            options.append(SelectOption(
                f"{tag} {t.name}"[:100], cid,
                description=f"You have {owned}"[:100],
            ))
        if len(options) >= 25:
            break
    if not options:
        return None
    return ActionRow(SelectMenu(
        f"mm:trade:pick:{want_type}", options=options,
        placeholder=f"Pick a {want_type} to add...",
    ))


def _render_panel(ctx: Context, state: dict[str, Any]) -> tuple[list[dict], list[ActionRow]]:
    return ([embeds.trade_panel_embed(state)], _panel_components(state))


# ── /maid trade @opponent ───────────────────────────────────────────────────

def run(ctx: Context, event: dict) -> None:
    challenger_id = str(event.get("user_id") or "")
    challenger_name = event.get("user_name") or "Maid"
    target_id = _extract_user_option(event, "opponent")

    if not challenger_id:
        ctx.interaction.respond(content="Could not identify you.", ephemeral=True)
        return
    if not target_id:
        ctx.interaction.respond(content="Pick an opponent — `/maid trade opponent:@user`.", ephemeral=True)
        return
    if target_id == challenger_id:
        ctx.interaction.respond(content="You can't trade with yourself.", ephemeral=True)
        return

    # Guard against double-booking.
    if trade_state.get_pending_for(ctx, challenger_id) or trade_state.get_active_for(ctx, challenger_id):
        ctx.interaction.respond(content="You already have a pending or active trade.", ephemeral=True)
        return
    if trade_state.get_pending_for(ctx, target_id) or trade_state.get_active_for(ctx, target_id):
        ctx.interaction.respond(content=f"<@{target_id}> already has a pending or active trade.", ephemeral=True)
        return

    target_name = _resolve_name(ctx, target_id)
    trade_id = trade_state.new_trade_id()
    pending = {
        "trade_id":   trade_id,
        "channel_id": str(event.get("channel_id") or ""),
        "status":     "pending",
        "a": {"user_id": challenger_id, "user_name": challenger_name, "offer": [], "locked": False},
        "b": {"user_id": target_id,     "user_name": target_name,     "offer": [], "locked": False},
    }
    trade_state.save(ctx, trade_id, pending, ttl_seconds=trade_state.PENDING_TTL_S)
    trade_state.set_pending_for(ctx, challenger_id, trade_id)
    trade_state.set_pending_for(ctx, target_id, trade_id)

    ctx.interaction.respond(
        content=f"<@{target_id}>",
        embeds=[embeds.trade_challenge_embed(
            challenger_id, challenger_name, target_id, target_name,
            expires_in_s=trade_state.PENDING_TTL_S,
        )],
        components=[_challenge_components(trade_id)],
        ephemeral=False,
    )


# ── Component dispatcher ────────────────────────────────────────────────────

def on_component(ctx: Context, event: dict, tail: list[str]) -> None:
    if not tail:
        return
    action = tail[0]
    clicker_id = str(event.get("user_id") or "")
    if not clicker_id:
        return

    if action == "accept":
        if len(tail) < 2: return
        _handle_accept(ctx, event, clicker_id, tail[1])
    elif action == "decline":
        if len(tail) < 2: return
        _handle_decline(ctx, event, clicker_id, tail[1])
    elif action == "add":
        if len(tail) < 2: return
        _handle_add_button(ctx, event, clicker_id, tail[1])
    elif action == "pick":
        if len(tail) < 2: return
        _handle_pick(ctx, event, clicker_id, tail[1])
    elif action == "clear":
        _handle_clear(ctx, event, clicker_id)
    elif action == "lock":
        _handle_lock(ctx, event, clicker_id)
    elif action == "cancel":
        _handle_cancel(ctx, event, clicker_id)
    elif action == "confirm":
        _handle_confirm(ctx, event, clicker_id)


# ── Helpers ─────────────────────────────────────────────────────────────────

def _load_active_for(ctx: Context, user_id: str) -> dict | None:
    tid = trade_state.get_active_for(ctx, user_id)
    if not tid:
        return None
    return trade_state.load(ctx, tid)


def _is_party(state: dict, user_id: str) -> bool:
    return trade_engine.side_for(state, user_id) is not None


def _not_yours(ctx: Context) -> None:
    ctx.interaction.respond(content="This isn't your trade.", ephemeral=True)


# ── Accept / Decline ────────────────────────────────────────────────────────

def _handle_accept(ctx: Context, event: dict, clicker_id: str, trade_id: str) -> None:
    state = trade_state.load(ctx, trade_id)
    if not state or state.get("status") != "pending":
        ctx.interaction.respond(content="That trade invitation has expired.", ephemeral=True)
        return
    if clicker_id != state["b"]["user_id"]:
        ctx.interaction.respond(content="Only the invited player can accept.", ephemeral=True)
        return

    state["status"] = "active"
    trade_state.save(ctx, trade_id, state)
    trade_state.clear_pending_for(ctx, state["a"]["user_id"])
    trade_state.clear_pending_for(ctx, state["b"]["user_id"])
    trade_state.set_active_for(ctx, state["a"]["user_id"], trade_id)
    trade_state.set_active_for(ctx, state["b"]["user_id"], trade_id)

    out_embeds, components = _render_panel(ctx, state)
    ctx.interaction.respond(
        content=f"<@{state['a']['user_id']}> <@{state['b']['user_id']}>",
        embeds=out_embeds,
        components=components,
        ephemeral=False,
    )


def _handle_decline(ctx: Context, event: dict, clicker_id: str, trade_id: str) -> None:
    state = trade_state.load(ctx, trade_id)
    if not state or state.get("status") != "pending":
        ctx.interaction.respond(content="That trade invitation has expired.", ephemeral=True)
        return
    if clicker_id != state["b"]["user_id"]:
        ctx.interaction.respond(content="Only the invited player can decline.", ephemeral=True)
        return
    a_id = state["a"]["user_id"]; b_id = state["b"]["user_id"]
    trade_state.clear_pending_for(ctx, a_id)
    trade_state.clear_pending_for(ctx, b_id)
    trade_state.clear(ctx, trade_id)
    ctx.interaction.respond(
        content=f"<@{b_id}> declined <@{a_id}>'s trade request.",
        ephemeral=False,
    )


# ── Edit-phase actions ──────────────────────────────────────────────────────

def _handle_add_button(ctx: Context, event: dict, clicker_id: str, want_type: str) -> None:
    if want_type not in ("maid", "tool"):
        return
    state = _load_active_for(ctx, clicker_id)
    if not state or not _is_party(state, clicker_id):
        _not_yours(ctx); return
    side = trade_engine.side_for(state, clicker_id)
    if state[side].get("locked"):
        ctx.interaction.respond(content="Unlock your offer to change it.", ephemeral=True)
        return
    picker = _add_card_picker(ctx, clicker_id, want_type)
    if picker is None:
        ctx.interaction.respond(content=f"You don't own any {want_type} cards.", ephemeral=True)
        return
    ctx.interaction.respond(
        content=f"Pick a {want_type} to add:",
        components=[picker],
        ephemeral=True,
    )


def _handle_pick(ctx: Context, event: dict, clicker_id: str, want_type: str) -> None:
    if want_type not in ("maid", "tool"):
        return
    values = event.get("values") or []
    if not values:
        return
    card_id = str(values[0])
    state = _load_active_for(ctx, clicker_id)
    if not state or not _is_party(state, clicker_id):
        _not_yours(ctx); return
    side = trade_engine.side_for(state, clicker_id)

    # Verify the user still owns enough for THIS new entry on top of
    # any duplicates already offered.
    already_offered_same = sum(
        1 for e in (state[side].get("offer") or [])
        if len(e) >= 2 and e[0] == want_type and e[1] == card_id
    )
    row = ctx.sql.query_one(
        "SELECT count FROM mm_inventory WHERE user_id=%s AND card_type=%s AND card_id=%s",
        [clicker_id, want_type, card_id],
    )
    owned = int((row or {}).get("count", 0))
    if owned - already_offered_same <= 0:
        ctx.interaction.respond(
            content=f"You only own {owned} cop{'y' if owned == 1 else 'ies'} of that — already in your offer.",
            ephemeral=True,
        )
        return

    ok, reason = trade_engine.add_card(state, side, want_type, card_id)
    if not ok:
        ctx.interaction.respond(content=reason, ephemeral=True)
        return
    trade_state.save(ctx, state["trade_id"], state)
    out_embeds, components = _render_panel(ctx, state)
    ctx.interaction.respond(
        content=f"<@{state['a']['user_id']}> <@{state['b']['user_id']}>",
        embeds=out_embeds, components=components, ephemeral=False,
    )


def _handle_clear(ctx: Context, event: dict, clicker_id: str) -> None:
    state = _load_active_for(ctx, clicker_id)
    if not state or not _is_party(state, clicker_id):
        _not_yours(ctx); return
    side = trade_engine.side_for(state, clicker_id)
    if state[side].get("locked"):
        ctx.interaction.respond(content="Unlock first.", ephemeral=True)
        return
    trade_engine.clear_offer(state, side)
    trade_state.save(ctx, state["trade_id"], state)
    out_embeds, components = _render_panel(ctx, state)
    ctx.interaction.respond(
        content=f"<@{state['a']['user_id']}> <@{state['b']['user_id']}>",
        embeds=out_embeds, components=components, ephemeral=False,
    )


def _handle_lock(ctx: Context, event: dict, clicker_id: str) -> None:
    state = _load_active_for(ctx, clicker_id)
    if not state or not _is_party(state, clicker_id):
        _not_yours(ctx); return
    side = trade_engine.side_for(state, clicker_id)
    # Toggle: clicking Lock while already locked unlocks.
    cur = bool(state[side].get("locked"))
    trade_engine.set_locked(state, side, not cur)
    trade_state.save(ctx, state["trade_id"], state)
    out_embeds, components = _render_panel(ctx, state)
    ctx.interaction.respond(
        content=f"<@{state['a']['user_id']}> <@{state['b']['user_id']}>",
        embeds=out_embeds, components=components, ephemeral=False,
    )


def _handle_cancel(ctx: Context, event: dict, clicker_id: str) -> None:
    state = _load_active_for(ctx, clicker_id)
    if not state or not _is_party(state, clicker_id):
        _not_yours(ctx); return
    a_id = state["a"]["user_id"]; b_id = state["b"]["user_id"]
    trade_state.clear_active_for(ctx, a_id)
    trade_state.clear_active_for(ctx, b_id)
    trade_state.clear(ctx, state["trade_id"])
    canceller = state["a"]["user_name"] if clicker_id == a_id else state["b"]["user_name"]
    ctx.interaction.respond(
        content=f"<@{a_id}> <@{b_id}> — **{canceller}** cancelled the trade.",
        ephemeral=False,
    )


def _handle_confirm(ctx: Context, event: dict, clicker_id: str) -> None:
    state = _load_active_for(ctx, clicker_id)
    if not state or not _is_party(state, clicker_id):
        _not_yours(ctx); return
    if not trade_engine.both_locked(state):
        ctx.interaction.respond(content="Both sides must lock first.", ephemeral=True)
        return

    # Dedup so a double-click can't double-swap.
    if not ctx.ephemeral.dedup(f"mm:trade:confirm:{state['trade_id']}", ttl_seconds=5):
        return

    ok, message = trade_engine.execute_swap(ctx, state)

    # Recount unique cards for achievement tracking (both users).
    a_id = state["a"]["user_id"]; b_id = state["b"]["user_id"]
    unlocked: list[str] = []
    if ok:
        for uid in (a_id, b_id):
            try:
                row = ctx.sql.query_one(
                    "SELECT COUNT(*) AS n FROM mm_inventory WHERE user_id=%s AND count > 0",
                    [uid],
                )
                n = int((row or {}).get("n", 0))
                unlocked.extend(ach_engine.set_counter(ctx, uid, "unique_owned", n))
            except Exception:
                pass

    trade_state.clear_active_for(ctx, a_id)
    trade_state.clear_active_for(ctx, b_id)
    trade_state.clear(ctx, state["trade_id"])

    out = [embeds.trade_result_embed(state, ok=ok, message=message)]
    if unlocked:
        out.append(embeds.achievement_unlock_embed(unlocked))
    ctx.interaction.respond(
        content=f"<@{a_id}> <@{b_id}>",
        embeds=out,
        components=[],
        ephemeral=False,
    )
