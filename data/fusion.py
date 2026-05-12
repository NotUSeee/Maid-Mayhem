"""Fusion recipes.

Each entry: consume N cards of rarity ``from_rarity`` to get 1 random card
of rarity ``to_rarity``. Cards consumed can be either maids or tools as
long as they share the rarity tier. The output is a random card from the
target tier (any type).

Legendary -> Mythic costs 5 instead of 3 so Mythics stay rare even when
players have a deep collection.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FusionRecipe:
    from_rarity: str
    to_rarity: str
    cost: int      # number of cards consumed


RECIPES: tuple[FusionRecipe, ...] = (
    FusionRecipe("common",    "uncommon",  3),
    FusionRecipe("uncommon",  "rare",      3),
    FusionRecipe("rare",      "epic",      3),
    FusionRecipe("epic",      "legendary", 3),
    FusionRecipe("legendary", "mythic",    5),
)

BY_FROM: dict[str, FusionRecipe] = {r.from_rarity: r for r in RECIPES}
