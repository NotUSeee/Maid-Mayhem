"""Maid Manor rooms.

Five rooms, each level 1-10. Every player starts at level 1 on every
room. Upgrade cost scales geometrically — L9 -> L10 is the deepest
sink in the game.

Effects per level (applied at the reward / cooldown sites):

    Tea Room       +2% XP from ALL sources (caps at +20% at L10)
    Kitchen        +2% coins from ALL sources (caps at +20% at L10)
    Training Hall  +5 flat bonus XP on each battle/duel win (max +50)
    Garden         -10 minutes off /maid daily cooldown (max -100)
    Summoning Room +1 daily pack card every 5 levels (L1-4: 3, L5-9: 4, L10: 5)

Upgrade pricing follows ``cost(L -> L+1) = 100 * 2 ** L`` coins. Total
across all rooms to max is ~510,000 coins — intentionally a long-term
sink so manor progression is meaningful well past v1.
"""
from __future__ import annotations

from dataclasses import dataclass


MAX_LEVEL = 10


@dataclass(frozen=True)
class Room:
    id: str
    name: str
    emoji: str
    description: str   # short blurb shown on the manor page
    bonus_per_level: str  # human description of one level's effect


TEA_ROOM = Room(
    id="tea_room",
    name="Tea Room",
    emoji="\U0001F375",
    description="Refines XP into experience faster.",
    bonus_per_level="+2% XP gain",
)

KITCHEN = Room(
    id="kitchen",
    name="Kitchen",
    emoji="\U0001F373",
    description="A well-fed maid earns more.",
    bonus_per_level="+2% coin gain",
)

TRAINING_HALL = Room(
    id="training_hall",
    name="Training Hall",
    emoji="\U0001F94B",
    description="Combat experience compounds with practice.",
    bonus_per_level="+5 bonus XP on battle/duel wins",
)

GARDEN = Room(
    id="garden",
    name="Garden",
    emoji="\U0001F33F",
    description="Restorative herbs shorten the daily wait.",
    bonus_per_level="-10 min off /maid daily cooldown",
)

SUMMONING_ROOM = Room(
    id="summoning_room",
    name="Summoning Room",
    emoji="\U0001F52E",
    description="Every five levels, your daily pack pulls one extra card.",
    bonus_per_level="L5/L10 = +1 daily-pack card",
)


ALL: tuple[Room, ...] = (TEA_ROOM, KITCHEN, TRAINING_HALL, GARDEN, SUMMONING_ROOM)
BY_ID: dict[str, Room] = {r.id: r for r in ALL}


def upgrade_cost(current_level: int) -> int:
    """Cost in coins to upgrade from ``current_level`` -> ``current_level + 1``.

    Returns 0 when already at MAX_LEVEL (caller should treat as "maxed").
    """
    if current_level >= MAX_LEVEL:
        return 0
    if current_level < 1:
        current_level = 1
    return 100 * (2 ** current_level)
