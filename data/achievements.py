"""Achievement catalog.

Unlike quests, achievements never reset. Each one is a counter (or
boolean) with a single target value; the moment progress hits the
target, the achievement unlocks and the reward is credited. There is
no claim button — unlocks are auto-credited the instant they happen,
with an ephemeral notification on the triggering interaction.

Categories (purely cosmetic — used to group the embed):

    foundation   first-time milestones (your first daily, first battle…)
    combat       win-count + raid-strike progression
    collection   unique cards owned + rarities pulled
    economy      coins spent, packs opened, fusions completed
    manor        room-upgrade milestones
    cosmetics    Polish-earned + items bought
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Achievement:
    id: str
    name: str
    description: str
    category: str
    counter: str         # which counter advances this; see engine/achievements.py
    target: int
    reward_coins: int = 0
    reward_xp: int = 0
    reward_polish: int = 0


# ── Foundation ──────────────────────────────────────────────────────────────
FOUNDATION = (
    Achievement("first_daily",         "First Steps",
                "Claim your first daily.",                "foundation",
                "daily_claim",       1, reward_coins=25,  reward_xp=20, reward_polish=1),
    Achievement("first_battle",        "Skirmisher",
                "Win your first PvE battle.",             "foundation",
                "pve_win",           1, reward_coins=50,  reward_xp=40),
    Achievement("first_pack",          "Pack Rat",
                "Open your first shop pack.",             "foundation",
                "pack_buy",          1, reward_coins=50,  reward_xp=20),
    Achievement("first_duel",          "Friendly Rivalry",
                "Win your first PvP duel.",               "foundation",
                "pvp_win",           1, reward_coins=100, reward_xp=80, reward_polish=2),
    Achievement("first_raid",          "First Strike",
                "Land your first raid attack.",           "foundation",
                "raid_attack",       1, reward_coins=50,  reward_xp=30),
    Achievement("first_fuse",          "Apprentice Alchemist",
                "Fuse your first card.",                  "foundation",
                "card_fuse",         1, reward_coins=80,  reward_xp=50),
)

# ── Combat ──────────────────────────────────────────────────────────────────
COMBAT = (
    Achievement("pve_10",     "Going Pro",
                "Win 10 PvE battles.",                    "combat",
                "pve_win",          10, reward_coins=200,  reward_xp=150),
    Achievement("pve_50",     "Manor Defender",
                "Win 50 PvE battles.",                    "combat",
                "pve_win",          50, reward_coins=750,  reward_xp=600, reward_polish=3),
    Achievement("pvp_10",     "Tournament Hopeful",
                "Win 10 PvP duels.",                      "combat",
                "pvp_win",          10, reward_coins=400,  reward_xp=300, reward_polish=5),
    Achievement("raid_50",    "Raid Veteran",
                "Land 50 raid attacks.",                  "combat",
                "raid_attack",      50, reward_coins=500,  reward_xp=400, reward_polish=5),
)

# ── Collection ──────────────────────────────────────────────────────────────
COLLECTION = (
    Achievement("unique_10",  "Starting a Collection",
                "Own 10 unique cards.",                   "collection",
                "unique_owned",     10, reward_coins=150,  reward_xp=100),
    Achievement("unique_25",  "Serious Collector",
                "Own 25 unique cards.",                   "collection",
                "unique_owned",     25, reward_coins=400,  reward_xp=300, reward_polish=3),
    Achievement("unique_40",  "Manor Curator",
                "Own all 40 collectible cards.",          "collection",
                "unique_owned",     40, reward_coins=2000, reward_xp=1500, reward_polish=15),
    Achievement("pull_mythic","Mythic Pull",
                "Acquire any Mythic card.",               "collection",
                "mythic_owned",      1, reward_coins=500,  reward_xp=300, reward_polish=10),
)

# ── Economy ─────────────────────────────────────────────────────────────────
ECONOMY = (
    Achievement("pack_25",    "Polished Pursuit",
                "Open 25 shop packs.",                    "economy",
                "pack_buy",         25, reward_coins=500,  reward_xp=300),
    Achievement("fuse_10",    "Master Crafter",
                "Fuse 10 cards.",                         "economy",
                "card_fuse",        10, reward_coins=400,  reward_xp=250),
)

# ── Manor ───────────────────────────────────────────────────────────────────
MANOR = (
    Achievement("manor_l5_any","Renovator",
                "Upgrade any room to L5.",                "manor",
                "manor_room_l5",     1, reward_coins=300,  reward_xp=200),
    Achievement("manor_l10_any","Manor Master",
                "Max any room to L10.",                   "manor",
                "manor_room_l10",    1, reward_coins=1000, reward_xp=600, reward_polish=5),
    Achievement("manor_all_l5","Architect",
                "Bring every room to at least L5.",       "manor",
                "manor_all_l5",      1, reward_coins=2000, reward_xp=1200, reward_polish=10),
)

# ── Cosmetics ───────────────────────────────────────────────────────────────
COSMETICS = (
    Achievement("cosmetic_first","Maid of Style",
                "Buy your first cosmetic.",               "cosmetics",
                "cosmetic_buy",      1, reward_coins=50,   reward_xp=30, reward_polish=2),
)


ALL: tuple[Achievement, ...] = (
    *FOUNDATION, *COMBAT, *COLLECTION, *ECONOMY, *MANOR, *COSMETICS,
)
BY_ID: dict[str, Achievement] = {a.id: a for a in ALL}


def by_category(category: str) -> tuple[Achievement, ...]:
    return tuple(a for a in ALL if a.category == category)


CATEGORIES: tuple[str, ...] = (
    "foundation", "combat", "collection", "economy", "manor", "cosmetics",
)
CATEGORY_LABELS: dict[str, str] = {
    "foundation": "🌱 Foundation",
    "combat":     "⚔️ Combat",
    "collection": "📚 Collection",
    "economy":    "🪙 Economy",
    "manor":      "🏰 Manor",
    "cosmetics":  "✨ Cosmetics",
}
