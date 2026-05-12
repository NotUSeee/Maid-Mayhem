"""Rank logic + season rollover.

Read-side helpers are pure (current_rank, progress_to_next). Write-side
helpers (award_rp, ensure_season_current) take a Context because they
mutate KV state and may deliver season-end rewards.
"""
from __future__ import annotations

import datetime as _dt
import random
from typing import Any, TYPE_CHECKING

from data import ranks as ranks_data
from data import packs as packs_data
from engine import drops

if TYPE_CHECKING:
    from mmo_maid_sdk import Context


def current_season_id(now: _dt.datetime | None = None) -> str:
    """Return the current season identifier ('YYYY-MM' UTC)."""
    n = now or _dt.datetime.utcnow()
    return n.strftime("%Y-%m")


def current_rank(rp: int) -> ranks_data.Rank:
    """Return the highest rank whose threshold <= rp."""
    rp = max(0, int(rp))
    cur = ranks_data.TIERS[0]
    for tier in ranks_data.TIERS:
        if rp >= tier.threshold:
            cur = tier
        else:
            break
    return cur


def next_rank(rp: int) -> ranks_data.Rank | None:
    """Return the next tier above the player's current rank, or None at top."""
    cur = current_rank(rp)
    found = False
    for tier in ranks_data.TIERS:
        if found:
            return tier
        if tier.id == cur.id:
            found = True
    return None


def progress_to_next(rp: int) -> tuple[int, int, int]:
    """Return (rp_into_tier, span_of_tier, percent_0_100)."""
    cur = current_rank(rp)
    nxt = next_rank(rp)
    if nxt is None:
        return (0, 0, 100)
    span = nxt.threshold - cur.threshold
    into = max(0, rp - cur.threshold)
    pct = int(round(100 * into / max(1, span)))
    return (into, span, min(100, pct))


# ── Load / save ─────────────────────────────────────────────────────────────

_DEFAULT_STATE = {
    "season": "",
    "rp": 0,
    "peak_rank": "dust_bunny",   # peak this season
    "career_peak": "dust_bunny", # peak across all seasons
}


def _key(user_id: str) -> str:
    return f"rank:{user_id}"


def load_state(ctx: "Context", user_id: str) -> dict[str, Any]:
    raw = ctx.kv.get(_key(user_id))
    if not isinstance(raw, dict):
        return {**_DEFAULT_STATE}
    return {**_DEFAULT_STATE, **raw}


def save_state(ctx: "Context", user_id: str, state: dict[str, Any]) -> None:
    ctx.kv.set(_key(user_id), state)


# ── Season rollover ─────────────────────────────────────────────────────────

def ensure_season_current(ctx: "Context", user_id: str) -> dict[str, Any] | None:
    """If the user's last seen season is older than the current calendar
    month, perform the rollover: credit rewards for the peak rank reached
    last season, reset RP, update the saved season ID. Returns a summary
    dict on rollover, or ``None`` if no rollover happened.

    Summary shape::

        {
          "prior_season": "2026-04",
          "prior_peak": "head_maid",
          "coins": 1000,
          "polished_packs": 0,
          "royal_packs": 2,
          "guaranteed_mythic": False,
          "card_grants": [(card_type, card_id), ...],
        }
    """
    state = load_state(ctx, user_id)
    cur_season = current_season_id()

    if not state["season"]:
        # First time the user is seen — initialize, no rollover.
        state["season"] = cur_season
        save_state(ctx, user_id, state)
        return None

    if state["season"] == cur_season:
        return None

    # ── rollover ────────────────────────────────────────────────────────────
    prior_season = state["season"]
    prior_peak = state.get("peak_rank", "dust_bunny")
    reward = ranks_data.SEASON_REWARDS.get(prior_peak)
    summary: dict[str, Any] = {
        "prior_season": prior_season,
        "prior_peak": prior_peak,
        "coins": 0,
        "polished_packs": 0,
        "royal_packs": 0,
        "guaranteed_mythic": False,
        "card_grants": [],
    }

    if reward is not None:
        # Credit coins via KV profile
        from store import kv as kv_store, sql as sql_store
        profile = kv_store.load_profile(ctx, user_id)
        profile["coins"] = int(profile.get("coins", 0)) + int(reward.coins)
        # Polish: scale with peak tier. Mid tiers get a touch; top gets a fat stack.
        polish_bonus = {
            "polished_maid":      3,
            "senior_maid":        5,
            "head_maid":          8,
            "royal_attendant":   12,
            "chaos_cleaner":     20,
            "mythic_housekeeper":40,
        }.get(prior_peak, 0)
        if polish_bonus:
            profile["polish"] = int(profile.get("polish", 0)) + polish_bonus
            summary["polish"] = polish_bonus
        kv_store.save_profile(ctx, user_id, profile)
        summary["coins"] = reward.coins

        # Open the free packs and grant cards
        rng = random.Random()
        for _ in range(reward.polished_packs):
            for ct, cid in drops.roll_pack_with_floor(packs_data.POLISHED.n_cards, packs_data.POLISHED.floor, rng):
                sql_store.grant_card(ctx, user_id, ct, cid, qty=1)
                summary["card_grants"].append((ct, cid))
        summary["polished_packs"] = reward.polished_packs
        for _ in range(reward.royal_packs):
            for ct, cid in drops.roll_pack_with_floor(packs_data.ROYAL_SERVICE.n_cards, packs_data.ROYAL_SERVICE.floor, rng):
                sql_store.grant_card(ctx, user_id, ct, cid, qty=1)
                summary["card_grants"].append((ct, cid))
        summary["royal_packs"] = reward.royal_packs

        if reward.guaranteed_mythic:
            # Pick any mythic card (maid first; we have no mythic tools)
            from data import maids as maids_data
            mythics = maids_data.BY_RARITY.get("mythic", [])
            if mythics:
                pick = rng.choice(mythics)
                sql_store.grant_card(ctx, user_id, "maid", pick.id, qty=1)
                summary["card_grants"].append(("maid", pick.id))
                summary["guaranteed_mythic"] = True

    # Reset RP for the new season; keep career_peak untouched.
    state["season"] = cur_season
    state["rp"] = 0
    state["peak_rank"] = "dust_bunny"
    save_state(ctx, user_id, state)
    return summary


# ── Award + update peak ─────────────────────────────────────────────────────

def award_rp(ctx: "Context", user_id: str, delta: int) -> tuple[int, ranks_data.Rank, bool]:
    """Apply an RP change (positive or negative, floored at 0). Updates the
    saved peak_rank and career_peak if this push reached a new tier.

    Returns (new_rp, current_rank_after, promoted_to_new_tier).
    """
    # Make sure the season is current before crediting.
    ensure_season_current(ctx, user_id)
    state = load_state(ctx, user_id)

    old_rp = int(state.get("rp", 0))
    old_rank = current_rank(old_rp)
    new_rp = max(0, old_rp + int(delta))
    new_rank = current_rank(new_rp)
    promoted = (new_rank.threshold > old_rank.threshold)

    state["rp"] = new_rp
    # Track the season peak (highest tier reached during the current season)
    peak = ranks_data.BY_ID.get(state.get("peak_rank", "dust_bunny")) or ranks_data.TIERS[0]
    if new_rank.threshold > peak.threshold:
        state["peak_rank"] = new_rank.id
    # Track career peak across all seasons
    career = ranks_data.BY_ID.get(state.get("career_peak", "dust_bunny")) or ranks_data.TIERS[0]
    if new_rank.threshold > career.threshold:
        state["career_peak"] = new_rank.id

    save_state(ctx, user_id, state)
    return new_rp, new_rank, promoted
