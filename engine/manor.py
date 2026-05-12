"""Manor bonus calculations.

Reads the player's manor levels from KV and returns concrete multipliers
the reward-granting sites consult. All effects are additive (a Kitchen
L5 + Tea Room L3 doesn't multiply — it gives +10% coins AND +6% XP).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mmo_maid_sdk import Context


def _level(manor: dict, room_id: str) -> int:
    return int(manor.get(room_id, 1))


def apply_reward_bonuses(
    manor: dict, *, coins: int, xp: int, is_battle_win: bool = False,
) -> tuple[int, int]:
    """Apply Tea Room / Kitchen / Training Hall bonuses to a reward pair."""
    tea = _level(manor, "tea_room")
    kit = _level(manor, "kitchen")
    train = _level(manor, "training_hall")

    coin_mult = 1.0 + 0.02 * kit
    xp_mult   = 1.0 + 0.02 * tea

    boosted_coins = int(round(coins * coin_mult))
    boosted_xp    = int(round(xp * xp_mult))

    if is_battle_win:
        boosted_xp += 5 * train

    return boosted_coins, boosted_xp


def daily_cooldown_reduction_s(manor: dict) -> int:
    """Garden trims ``10 * level`` minutes off the daily cooldown."""
    return 10 * 60 * _level(manor, "garden")


def daily_pack_extra_cards(manor: dict) -> int:
    """Summoning Room adds +1 card every 5 levels (so +1 at L5, +2 at L10)."""
    return _level(manor, "summoning_room") // 5


# ── Wrappers that load from KV — convenience for handlers ──────────────────

def reward_bonuses_for_user(
    ctx: "Context", user_id: str,
    *, coins: int, xp: int, is_battle_win: bool = False,
) -> tuple[int, int]:
    from store import kv
    manor = kv.load_manor(ctx, user_id)
    return apply_reward_bonuses(manor, coins=coins, xp=xp, is_battle_win=is_battle_win)


def daily_cooldown_for_user(ctx: "Context", user_id: str, base_seconds: int) -> int:
    from store import kv
    manor = kv.load_manor(ctx, user_id)
    reduced = base_seconds - daily_cooldown_reduction_s(manor)
    return max(60, reduced)  # never under 1 minute


def daily_pack_size_for_user(ctx: "Context", user_id: str, base_size: int) -> int:
    from store import kv
    manor = kv.load_manor(ctx, user_id)
    return base_size + daily_pack_extra_cards(manor)
