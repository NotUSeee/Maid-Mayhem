"""Pack catalog.

The Daily Dust Pack is free, given out by ``/maid daily`` — not listed
here. The shop packs below are purchased with coins via ``/maid pack``.

Each pack has a rarity ``floor``: any roll below the floor gets bumped
up to the floor tier. So a Polished Pack with floor=uncommon never
drops Commons; everything is Uncommon or better.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Pack:
    id: str
    name: str
    price: int        # in coins
    n_cards: int      # how many cards the pack contains
    floor: str        # rarity id — drops below this tier are re-rolled up
    emoji: str
    description: str
    flavor: str = ""


POLISHED = Pack(
    id="polished",
    name="Polished Pack",
    price=100,
    n_cards=5,
    floor="uncommon",
    emoji="\U0001F4E6",
    description="5 cards. No Commons — everything is Uncommon or better.",
    flavor="Wrapped in cloth that smells faintly of beeswax.",
)

ROYAL_SERVICE = Pack(
    id="royal_service",
    name="Royal Service Pack",
    price=500,
    n_cards=7,
    floor="rare",
    emoji="\U0001F451",
    description="7 cards. Guaranteed Rare+. Boosted chance for Epic / Legendary / Mythic.",
    flavor="Sealed with the Head Maid's personal silver crest.",
)

ALL: tuple[Pack, ...] = (POLISHED, ROYAL_SERVICE)
BY_ID: dict[str, Pack] = {p.id: p for p in ALL}
