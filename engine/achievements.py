"""Achievement tracker + auto-unlock + reward credit.

Counters live in KV under ``achievements:{user_id}`` as::

    {
      "counters":  {"pve_win": 12, "card_fuse": 3, ...},
      "unlocked":  ["first_daily", "first_battle", ...],
    }

The handler calls ``bump(ctx, user_id, counter, amount)`` at the action
site. The engine increments the counter, scans every achievement that
keys on that counter, and unlocks any whose target was just crossed —
crediting their reward in the same transaction. The list of newly
unlocked achievement IDs is returned so the caller can surface them in
an embed.

There's no claim step; the moment an achievement unlocks, the reward
is in the player's wallet.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from data import achievements as ach_data

if TYPE_CHECKING:
    from mmo_maid_sdk import Context


_DEFAULT_STATE = {"counters": {}, "unlocked": []}


def _key(user_id: str) -> str:
    return f"achievements:{user_id}"


def load(ctx: "Context", user_id: str) -> dict:
    raw = ctx.kv.get(_key(user_id))
    if not isinstance(raw, dict):
        return {"counters": {}, "unlocked": []}
    return {
        "counters": dict(raw.get("counters") or {}),
        "unlocked": list(raw.get("unlocked") or []),
    }


def save(ctx: "Context", user_id: str, state: dict) -> None:
    ctx.kv.set(_key(user_id), {
        "counters": state.get("counters") or {},
        "unlocked": state.get("unlocked") or [],
    })


def progress(state: dict, counter: str) -> int:
    return int((state.get("counters") or {}).get(counter, 0))


def is_unlocked(state: dict, ach_id: str) -> bool:
    return ach_id in (state.get("unlocked") or [])


def _credit_reward(ctx: "Context", user_id: str, ach: ach_data.Achievement) -> None:
    """Land coins + xp + polish from an unlock. Mirrors the manor-aware
    pattern from other handlers so achievement rewards stack with the
    Kitchen / Tea Room multipliers."""
    from engine import manor as manor_engine
    from store import kv as kv_store
    coins, xp = manor_engine.reward_bonuses_for_user(
        ctx, user_id,
        coins=int(ach.reward_coins), xp=int(ach.reward_xp),
        is_battle_win=False,
    )
    kv_store.add_rewards(ctx, user_id, coins=coins, xp=xp, won=False)
    if int(ach.reward_polish) > 0:
        kv_store.add_polish(ctx, user_id, int(ach.reward_polish))


def bump(ctx: "Context", user_id: str, counter: str, amount: int = 1) -> list[str]:
    """Advance ``counter`` by ``amount``. Auto-unlocks any achievements
    that newly reached their target. Returns the list of unlocked IDs.
    """
    if amount == 0 or not user_id or not counter:
        return []
    state = load(ctx, user_id)
    counters = state.setdefault("counters", {})
    unlocked = list(state.setdefault("unlocked", []))
    unlocked_set = set(unlocked)

    old = int(counters.get(counter, 0))
    new = max(0, old + int(amount))
    counters[counter] = new

    newly: list[str] = []
    for a in ach_data.ALL:
        if a.counter != counter:
            continue
        if a.id in unlocked_set:
            continue
        if new >= int(a.target) and old < int(a.target):
            unlocked.append(a.id)
            unlocked_set.add(a.id)
            newly.append(a.id)

    state["unlocked"] = unlocked
    save(ctx, user_id, state)

    # Credit rewards AFTER saving so the unlocked list is authoritative
    # even if the reward path raises.
    for aid in newly:
        a = ach_data.BY_ID.get(aid)
        if a is not None:
            try:
                _credit_reward(ctx, user_id, a)
            except Exception as e:
                ctx.log(f"achievement reward credit failed ({aid}): {e!r}", level="error")
    return newly


# ── "set absolute" counter (for stateful values like unique_owned) ──────────

def set_counter(ctx: "Context", user_id: str, counter: str, value: int) -> list[str]:
    """Set a counter to an absolute value (used for "unique cards owned"
    which is computed from a SELECT, not incremented per event). Triggers
    the same unlock-check logic as ``bump``."""
    if not user_id or not counter:
        return []
    state = load(ctx, user_id)
    counters = state.setdefault("counters", {})
    unlocked = list(state.setdefault("unlocked", []))
    unlocked_set = set(unlocked)
    old = int(counters.get(counter, 0))
    new = max(0, int(value))
    if new == old:
        return []
    counters[counter] = new
    newly: list[str] = []
    for a in ach_data.ALL:
        if a.counter != counter:
            continue
        if a.id in unlocked_set:
            continue
        if new >= int(a.target) and old < int(a.target):
            unlocked.append(a.id)
            unlocked_set.add(a.id)
            newly.append(a.id)
    state["unlocked"] = unlocked
    save(ctx, user_id, state)
    for aid in newly:
        a = ach_data.BY_ID.get(aid)
        if a is not None:
            try:
                _credit_reward(ctx, user_id, a)
            except Exception as e:
                ctx.log(f"achievement reward credit failed ({aid}): {e!r}", level="error")
    return newly
