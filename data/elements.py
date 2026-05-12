"""Element types and the element triangle.

Ring (each beats the next):
    Fire -> Frost -> Garden -> Shadow -> Light -> Moon -> Royal -> Clockwork -> Fire

Multiplier rules:
    advantage     1.5x
    disadvantage  0.75x
    neutral / same 1.0x
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Element:
    id: str
    label: str
    emoji: str
    color: int


LIGHT     = Element("light",     "Light",     "\U0001F56F️", 0xFEF3C7)
MOON      = Element("moon",      "Moon",      "\U0001F319",       0x6366F1)
FIRE      = Element("fire",      "Fire",      "\U0001F525",       0xEF4444)
FROST     = Element("frost",     "Frost",     "❄️",     0x60A5FA)
GARDEN    = Element("garden",    "Garden",    "\U0001F33F",       0x16A34A)
CLOCKWORK = Element("clockwork", "Clockwork", "⚙️",     0xB45309)
ROYAL     = Element("royal",     "Royal",     "\U0001F451",       0xCA8A04)
SHADOW    = Element("shadow",    "Shadow",    "\U0001F578️", 0x4B5563)

ALL: tuple[Element, ...] = (LIGHT, MOON, FIRE, FROST, GARDEN, CLOCKWORK, ROYAL, SHADOW)
BY_ID: dict[str, Element] = {e.id: e for e in ALL}

# Ring: key beats value
_BEATS: dict[str, str] = {
    "fire":      "frost",
    "frost":     "garden",
    "garden":    "shadow",
    "shadow":    "light",
    "light":     "moon",
    "moon":      "royal",
    "royal":     "clockwork",
    "clockwork": "fire",
}


def multiplier(attacker: str, defender: str) -> float:
    """Damage multiplier from attacker element vs defender element."""
    if not attacker or not defender or attacker == defender:
        return 1.0
    if _BEATS.get(attacker) == defender:
        return 1.5
    if _BEATS.get(defender) == attacker:
        return 0.75
    return 1.0
