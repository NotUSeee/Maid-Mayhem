"""Rarity-weighted card drops for daily packs.

Each drop picks a rarity from the doc-defined weights, then picks a card
of that rarity uniformly. If a card_type has no entries at the rolled
rarity, it falls back to the nearest filled rarity.
"""
from __future__ import annotations

import random
from typing import Optional

from data import maids as maids_data
from data import rarities as rarities_data
from data import tools as tools_data


def roll_rarity(rng: Optional[random.Random] = None) -> str:
    """Roll a rarity id by weight."""
    r = rng or random
    total = sum(x.weight for x in rarities_data.ALL)
    pick = r.uniform(0.0, total)
    cum = 0.0
    for rarity in rarities_data.ALL:
        cum += rarity.weight
        if pick <= cum:
            return rarity.id
    return rarities_data.ALL[0].id  # fallback


def _nearest_rarity_with_pool(card_type: str, rolled: str) -> str:
    """If we rolled a rarity that has no cards of card_type, walk down."""
    pool = maids_data.BY_RARITY if card_type == "maid" else tools_data.BY_RARITY
    if pool.get(rolled):
        return rolled
    # walk the global rarity order, prefer lower tiers (commoner)
    order = [r.id for r in rarities_data.ALL]
    if rolled in order:
        idx = order.index(rolled)
        for offset in range(1, len(order)):
            for direction in (-1, 1):
                j = idx + direction * offset
                if 0 <= j < len(order) and pool.get(order[j]):
                    return order[j]
    return next(iter(pool.keys()))


def roll_card(rng: Optional[random.Random] = None) -> tuple[str, str]:
    """Roll (card_type, card_id) for one drop.

    70% chance maid, 30% chance tool — gives variety without flooding decks
    with tools that go unused early.
    """
    r = rng or random
    rarity = roll_rarity(r)
    card_type = "maid" if r.random() < 0.7 else "tool"
    rarity = _nearest_rarity_with_pool(card_type, rarity)
    pool = (maids_data.BY_RARITY if card_type == "maid" else tools_data.BY_RARITY)[rarity]
    card = r.choice(pool)
    return card_type, card.id


def roll_pack(n: int = 3, rng: Optional[random.Random] = None) -> list[tuple[str, str]]:
    """Roll a pack of `n` cards."""
    return [roll_card(rng) for _ in range(n)]


def roll_rarity_with_floor(
    floor: str,
    rng: Optional[random.Random] = None,
) -> str:
    """Roll a rarity id, restricted to tiers at or above ``floor``.

    The weight of sub-floor tiers is redistributed proportionally across
    the eligible tiers, not dumped into the floor — so a Royal Service
    Pack (floor=rare) gives a meaningfully bumped chance of Epic /
    Legendary / Mythic, not 90%+ Rare.
    """
    r = rng or random
    order = [rarity.id for rarity in rarities_data.ALL]
    try:
        floor_idx = order.index(floor)
    except ValueError:
        floor_idx = 0
    eligible = rarities_data.ALL[floor_idx:]
    total = sum(rarity.weight for rarity in eligible)
    if total <= 0:
        return eligible[0].id
    pick = r.uniform(0.0, total)
    cum = 0.0
    for rarity in eligible:
        cum += rarity.weight
        if pick <= cum:
            return rarity.id
    return eligible[-1].id


def roll_card_with_floor(
    floor: str,
    rng: Optional[random.Random] = None,
) -> tuple[str, str]:
    """Roll one card, never below ``floor`` rarity."""
    r = rng or random
    rarity = roll_rarity_with_floor(floor, r)
    card_type = "maid" if r.random() < 0.7 else "tool"
    rarity = _nearest_rarity_with_pool(card_type, rarity)
    pool = (maids_data.BY_RARITY if card_type == "maid" else tools_data.BY_RARITY)[rarity]
    return card_type, r.choice(pool).id


def roll_pack_with_floor(
    n: int,
    floor: str,
    rng: Optional[random.Random] = None,
) -> list[tuple[str, str]]:
    """Roll ``n`` cards with a rarity floor (shop packs)."""
    return [roll_card_with_floor(floor, rng) for _ in range(n)]
