"""Rarity tiers and drop weights.

Weights are the percentages from the design doc. Order is also the
display order (Common first, Mythic last).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rarity:
    id: str
    label: str
    weight: float    # percent — sum across all tiers = 100.0
    color: int       # Discord embed color (0xRRGGBB)
    emoji: str       # leading icon for embeds/menus


COMMON    = Rarity("common",    "Common",    55.0,  0x9CA3AF, "⬜")
UNCOMMON  = Rarity("uncommon",  "Uncommon",  25.0,  0x22C55E, "\U0001F7E9")
RARE      = Rarity("rare",      "Rare",      12.0,  0x3B82F6, "\U0001F7E6")
EPIC      = Rarity("epic",      "Epic",       6.0,  0xA855F7, "\U0001F7EA")
LEGENDARY = Rarity("legendary", "Legendary",  1.8,  0xF59E0B, "\U0001F7E7")
MYTHIC    = Rarity("mythic",    "Mythic",     0.2,  0xEF4444, "❤️‍\U0001F525")

ALL: tuple[Rarity, ...] = (COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, MYTHIC)
BY_ID: dict[str, Rarity] = {r.id: r for r in ALL}
