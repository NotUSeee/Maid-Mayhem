"""Rank tiers + per-season reward table.

Ranked Points (RP) are earned/lost across the month. A new season starts
on the 1st of every calendar month (UTC). At rollover:

  - The previous month's peak rank is read.
  - Rewards are credited (coins + free packs + sometimes a guaranteed
    mythic from the rolltop tier).
  - RP resets to 0; current season ID flips to the new month.

RP economy (applied at the source sites — see engine/ranks.py):

  daily claim         +5 RP
  /maid battle win    +5 RP   (PvE)
  /maid duel  win    +25 RP   (PvP)
  /maid duel  loss   -10 RP   (PvP, floored at 0)
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rank:
    id: str
    name: str
    threshold: int   # minimum RP to be at this rank
    emoji: str
    color: int       # embed color


TIERS: tuple[Rank, ...] = (
    Rank("dust_bunny",        "Dust Bunny",        0,    "\U0001F9F9", 0x9CA3AF),
    Rank("apprentice_maid",   "Apprentice Maid",   100,  "\U0001F9F9", 0x22C55E),
    Rank("polished_maid",     "Polished Maid",     250,  "\U0001F9F9", 0x3B82F6),
    Rank("senior_maid",       "Senior Maid",       500,  "✨",     0x8B5CF6),
    Rank("head_maid",         "Head Maid",         1000, "\U0001F451", 0xA855F7),
    Rank("royal_attendant",   "Royal Attendant",   2000, "\U0001F451", 0xCA8A04),
    Rank("chaos_cleaner",     "Chaos Cleaner",     4000, "⚡",     0xF59E0B),
    Rank("mythic_housekeeper","Mythic Housekeeper",8000, "❤️‍\U0001F525", 0xEF4444),
)

BY_ID: dict[str, Rank] = {r.id: r for r in TIERS}


@dataclass(frozen=True)
class SeasonReward:
    rank_id: str
    coins: int
    polished_packs: int
    royal_packs: int
    guaranteed_mythic: bool


# Indexed by peak rank reached during the season just ended.
SEASON_REWARDS: dict[str, SeasonReward] = {
    "dust_bunny":         SeasonReward("dust_bunny",          50, 0, 0, False),
    "apprentice_maid":    SeasonReward("apprentice_maid",    150, 1, 0, False),
    "polished_maid":      SeasonReward("polished_maid",      300, 0, 1, False),
    "senior_maid":        SeasonReward("senior_maid",        500, 0, 1, False),
    "head_maid":          SeasonReward("head_maid",         1000, 0, 2, False),
    "royal_attendant":    SeasonReward("royal_attendant",   1500, 0, 3, False),
    "chaos_cleaner":      SeasonReward("chaos_cleaner",     2500, 0, 4, False),
    "mythic_housekeeper": SeasonReward("mythic_housekeeper",5000, 0, 5, True),
}
