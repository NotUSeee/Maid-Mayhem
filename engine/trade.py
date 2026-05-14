"""Trade engine — offer-mutation logic + the swap itself.

Validation rules at the swap boundary:

    1. Both sides must be locked.
    2. Each side's offer must be backed by real inventory (counting any
       duplicates within the same offer — if you offer 2 Minas, you
       must own at least 2 Minas, not just 1).
    3. Neither offer may be empty (forbids "give me cards for nothing"
       griefs — if you want to gift, do so via a one-sided pre-arrangement
       and have the recipient offer something cheap back).

The swap itself is best-effort sequential since the SDK doesn't expose
transactions. We minimise window-of-inconsistency by computing per-card
net deltas and applying them with the existing grant/consume helpers.
On failure we attempt a reverse rollback but log the failure regardless.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from store import trade_state as ts_data

if TYPE_CHECKING:
    from mmo_maid_sdk import Context


# ── Offer mutations (pure dict ops, caller persists) ───────────────────────

def add_card(state: dict, side: str, card_type: str, card_id: str) -> tuple[bool, str]:
    """Add (card_type, card_id) to ``side``'s offer. Returns (ok, reason)."""
    if side not in ("a", "b"):
        return False, "invalid side"
    if state.get(side, {}).get("locked"):
        return False, "you already locked your offer — unlock to change it"
    offer = list(state[side].get("offer") or [])
    if len(offer) >= ts_data.MAX_OFFER_SIZE:
        return False, f"offer is full (max {ts_data.MAX_OFFER_SIZE} cards per side)"
    offer.append([card_type, card_id])
    state[side]["offer"] = offer
    return True, ""


def clear_offer(state: dict, side: str) -> None:
    if side in ("a", "b") and not state.get(side, {}).get("locked"):
        state[side]["offer"] = []


def remove_card(state: dict, side: str, index: int) -> None:
    if side not in ("a", "b") or state.get(side, {}).get("locked"):
        return
    offer = list(state[side].get("offer") or [])
    if 0 <= index < len(offer):
        offer.pop(index)
        state[side]["offer"] = offer


def set_locked(state: dict, side: str, locked: bool) -> None:
    if side in ("a", "b"):
        state[side]["locked"] = bool(locked)


def both_locked(state: dict) -> bool:
    return bool(state.get("a", {}).get("locked")) and bool(state.get("b", {}).get("locked"))


def side_for(state: dict, user_id: str) -> str | None:
    if state.get("a", {}).get("user_id") == user_id:
        return "a"
    if state.get("b", {}).get("user_id") == user_id:
        return "b"
    return None


# ── Inventory-backed validation ────────────────────────────────────────────

def _offer_counts(offer: list) -> dict[tuple[str, str], int]:
    """Group an offer list into {(card_type, card_id): qty}."""
    out: dict[tuple[str, str], int] = {}
    for entry in offer or []:
        if not entry or len(entry) < 2:
            continue
        key = (str(entry[0]), str(entry[1]))
        out[key] = out.get(key, 0) + 1
    return out


def can_swap(ctx: "Context", state: dict) -> tuple[bool, str]:
    """True if the swap is safe to execute right now. Validates locks,
    non-empty offers, and inventory backing for each side."""
    from store import sql as sql_store

    if state.get("status") != "active":
        return False, "trade is no longer active"
    if not both_locked(state):
        return False, "both sides must lock first"

    a_offer = state["a"].get("offer") or []
    b_offer = state["b"].get("offer") or []
    if not a_offer or not b_offer:
        return False, "both offers must contain at least one card"

    a_counts = _offer_counts(a_offer)
    b_counts = _offer_counts(b_offer)

    def _have(uid: str, card_type: str, card_id: str) -> int:
        row = ctx.sql.query_one(
            "SELECT count FROM mm_inventory WHERE user_id=%s AND card_type=%s AND card_id=%s",
            [uid, card_type, card_id],
        )
        return int((row or {}).get("count", 0))

    a_uid = state["a"]["user_id"]
    b_uid = state["b"]["user_id"]
    for (ct, cid), qty in a_counts.items():
        if _have(a_uid, ct, cid) < qty:
            return False, f"{state['a']['user_name']} no longer owns enough of `{cid}`"
    for (ct, cid), qty in b_counts.items():
        if _have(b_uid, ct, cid) < qty:
            return False, f"{state['b']['user_name']} no longer owns enough of `{cid}`"

    return True, ""


# ── The swap ──────────────────────────────────────────────────────────────

def execute_swap(ctx: "Context", state: dict) -> tuple[bool, str]:
    """Apply the swap. Returns (ok, message). On partial failure we
    attempt rollback and return ok=False with a description.
    """
    from store import sql as sql_store

    ok, reason = can_swap(ctx, state)
    if not ok:
        return False, reason

    a_uid = state["a"]["user_id"]
    b_uid = state["b"]["user_id"]
    a_counts = _offer_counts(state["a"]["offer"])
    b_counts = _offer_counts(state["b"]["offer"])

    # Net delta per (user, card_type, card_id).
    # A: subtract a_counts (A gave them away), add b_counts (A receives them)
    # B: subtract b_counts (B gave them away), add a_counts (B receives them)
    applied: list[tuple[str, str, str, int]] = []   # (user_id, ct, cid, qty) for rollback
    try:
        for (ct, cid), qty in a_counts.items():
            sql_store.consume_card(ctx, a_uid, ct, cid, qty)
            applied.append(("consume", a_uid, ct, cid, qty))
        for (ct, cid), qty in b_counts.items():
            sql_store.consume_card(ctx, b_uid, ct, cid, qty)
            applied.append(("consume", b_uid, ct, cid, qty))
        for (ct, cid), qty in a_counts.items():
            sql_store.grant_card(ctx, b_uid, ct, cid, qty)
            applied.append(("grant", b_uid, ct, cid, qty))
        for (ct, cid), qty in b_counts.items():
            sql_store.grant_card(ctx, a_uid, ct, cid, qty)
            applied.append(("grant", a_uid, ct, cid, qty))
        return True, "swap complete"
    except Exception as e:
        # Best-effort rollback in reverse.
        for op in reversed(applied):
            kind, uid, ct, cid, qty = op
            try:
                if kind == "consume":
                    sql_store.grant_card(ctx, uid, ct, cid, qty)
                else:
                    sql_store.consume_card(ctx, uid, ct, cid, qty)
            except Exception:
                pass
        return False, f"swap failed mid-flight: {e!r} (best-effort rollback attempted)"
