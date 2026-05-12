"""Raid boss roster.

Bosses cycle in order. When one dies, the next in ``CYCLE`` spawns
immediately. Each boss has an element (used for damage matchups
against the leading maid of the attacker's deck) and a flat HP pool.

HP is tuned for a small/medium server contributing ~30-60 total attacks
per kill given a mix of common and rare decks. Tier 3 bosses are real
slogs intentionally — they're the late-month challenge.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RaidBoss:
    id: str
    name: str
    tier: int             # 1 .. 3 — sets reward magnitude
    element: str
    hp: int
    emoji: str
    flavor: str


GREAT_UNWASHED_ONE = RaidBoss(
    id="great_unwashed_one",
    name="The Great Unwashed One",
    tier=1, element="shadow",
    hp=1500, emoji="\U0001F9FA",
    flavor="A mountain of laundry possessed by ancient laziness.",
)

LAUNDRY_HYDRA_PRIME = RaidBoss(
    id="laundry_hydra_prime",
    name="Laundry Hydra Prime",
    tier=2, element="shadow",
    hp=4000, emoji="\U0001F40D",
    flavor="Three sleeves. Six socks. None of them match.",
)

MOLD_KING_MAXIMUS = RaidBoss(
    id="mold_king_maximus",
    name="Mold King Maximus",
    tier=3, element="garden",
    hp=8000, emoji="\U0001F451",
    flavor="He sees himself as a connoisseur. Of damp.",
)


CYCLE: tuple[RaidBoss, ...] = (GREAT_UNWASHED_ONE, LAUNDRY_HYDRA_PRIME, MOLD_KING_MAXIMUS)
BY_ID: dict[str, RaidBoss] = {b.id: b for b in CYCLE}


def next_boss(current_id: str) -> RaidBoss:
    """Return the boss after ``current_id`` in the cycle; loops at the end."""
    ids = [b.id for b in CYCLE]
    try:
        idx = ids.index(current_id)
    except ValueError:
        return CYCLE[0]
    return CYCLE[(idx + 1) % len(CYCLE)]
