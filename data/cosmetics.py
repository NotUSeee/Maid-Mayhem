"""Cosmetic catalog.

Cosmetics never touch gameplay numbers — only how your /maid profile
embed looks. Bought with Polish, the slow-trickle premium currency:

    /maid daily             +1 Polish
    /maid duel win          +2 Polish
    raid champion           +5 Polish
    Mythic Housekeeper      +5 Polish (end-of-season bonus)
    Mythic pack pull        +3 Polish (one-shot when you first pull a Mythic)

Three slots, one cosmetic equipped each: ``title``, ``badge``, ``color``.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Cosmetic:
    id: str
    slot: str           # "title" | "badge" | "color"
    name: str           # what shows in the shop
    polish_cost: int
    value: str | int    # title text, emoji, or color int — depends on slot
    flavor: str = ""


# ── Titles ──────────────────────────────────────────────────────────────────
TITLES = (
    Cosmetic("title_polished",      "title", "The Polished",          50,   "The Polished",
             "For maids who never miss a spot."),
    Cosmetic("title_dust_walker",   "title", "The Dust Walker",       100,  "Dust Walker",
             "You move through chaos without a scuff mark."),
    Cosmetic("title_broomblade",    "title", "The Broomblade",        150,  "Broomblade",
             "Carries a broom into board meetings."),
    Cosmetic("title_head_of_hall",  "title", "Head of the Hall",      250,  "Head of the Hall",
             "A title earned, not given."),
    Cosmetic("title_mythic",        "title", "Mythic Housekeeper",    500,  "Mythic Housekeeper",
             "The manor itself bows when you enter."),
)

# ── Badges (a single emoji prefix on your title line) ──────────────────────
BADGES = (
    Cosmetic("badge_sparkle",   "badge", "Sparkle Badge",     30,  "✨", "A modest twinkle."),
    Cosmetic("badge_diamond",   "badge", "Diamond Badge",     80,  "\U0001F48E", "Cleaner than your floors."),
    Cosmetic("badge_trophy",    "badge", "Trophy Badge",      150, "\U0001F3C6", "Earned the old-fashioned way."),
    Cosmetic("badge_bolt",      "badge", "Bolt Badge",        200, "⚡", "Reserved for the genuinely fast."),
    Cosmetic("badge_moon",      "badge", "Moon Badge",        250, "\U0001F319", "Loaned, never given."),
    Cosmetic("badge_crown",     "badge", "Crown Badge",       400, "\U0001F451", "Worn lightly."),
)

# ── Profile embed colors ───────────────────────────────────────────────────
COLORS = (
    Cosmetic("color_gold",      "color", "Gold",         40,  0xCA8A04,  "Classic, polished."),
    Cosmetic("color_sky",       "color", "Sky Blue",     40,  0x60A5FA,  "Calm and steady."),
    Cosmetic("color_amethyst",  "color", "Amethyst",     80,  0x8B5CF6,  "Faintly suspicious."),
    Cosmetic("color_garden",    "color", "Garden Green", 80,  0x16A34A,  "Smells like herbs."),
    Cosmetic("color_chaos",     "color", "Chaos Red",    150, 0xDC2626,  "Reserved for the unhinged."),
    Cosmetic("color_mythic",    "color", "Mythic Gold",  400, 0xEF4444,  "Glows softly when no one is watching."),
)


ALL: tuple[Cosmetic, ...] = TITLES + BADGES + COLORS
BY_ID: dict[str, Cosmetic] = {c.id: c for c in ALL}

SLOTS: tuple[str, ...] = ("title", "badge", "color")


def by_slot(slot: str) -> tuple[Cosmetic, ...]:
    return tuple(c for c in ALL if c.slot == slot)
