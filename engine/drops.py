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
