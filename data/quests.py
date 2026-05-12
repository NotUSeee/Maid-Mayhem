"""Quest catalog.

Every day a small set of quests is rolled — date-seeded so every player
on the server sees the same lineup. Same for weekly quests (week-keyed).

Quests are simple counters. The handler bumps the counter at the action
site (battle win, raid attack, etc.). When ``progress >= target``, the
player can press Claim to credit the reward.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuestTemplate:
    id: str
    name: str
    description: str       # uses {target} placeholder
    counter: str           # "pve_win" | "pvp_win" | "raid_attack" | "pack_open" | "card_fuse"
    target_choices: tuple[int, ...]   # the planner picks one of these uniformly
    reward_coins: int
    reward_xp: int
    reward_polish: int = 0


# ── Daily pool ──────────────────────────────────────────────────────────────
DAILY = (
    QuestTemplate(
        id="d_pve_wins",
        name="Daily Patrol",
        description="Win {target} PvE battles.",
        counter="pve_win",
        target_choices=(2, 3, 4),
        reward_coins=120, reward_xp=80,
    ),
    QuestTemplate(
        id="d_raid_attacks",
        name="Civic Duty",
        description="Strike the chaos raid {target} times.",
        counter="raid_attack",
        target_choices=(1, 2, 3),
        reward_coins=100, reward_xp=60,
    ),
    QuestTemplate(
        id="d_pack_open",
        name="Polished Pursuit",
        description="Open {target} packs (daily or shop).",
        counter="pack_open",
        target_choices=(1, 2),
        reward_coins=80, reward_xp=50,
    ),
    QuestTemplate(
        id="d_pvp_win",
        name="Sparring Etiquette",
        description="Win {target} PvP duel(s).",
        counter="pvp_win",
        target_choices=(1, 2),
        reward_coins=160, reward_xp=100, reward_polish=1,
    ),
    QuestTemplate(
        id="d_card_fuse",
        name="Spring Cleaning",
        description="Fuse {target} card(s).",
        counter="card_fuse",
        target_choices=(1, 2),
        reward_coins=100, reward_xp=70,
    ),
)


# ── Weekly pool ─────────────────────────────────────────────────────────────
WEEKLY = (
    QuestTemplate(
        id="w_pve_run",
        name="Weekly Sweep",
        description="Win {target} PvE battles this week.",
        counter="pve_win",
        target_choices=(15, 20, 25),
        reward_coins=500, reward_xp=400, reward_polish=2,
    ),
    QuestTemplate(
        id="w_raids",
        name="Raid Veteran",
        description="Land {target} raid strikes this week.",
        counter="raid_attack",
        target_choices=(8, 12, 16),
        reward_coins=600, reward_xp=350, reward_polish=3,
    ),
    QuestTemplate(
        id="w_pvp",
        name="Tournament Hopeful",
        description="Win {target} duels this week.",
        counter="pvp_win",
        target_choices=(3, 5, 7),
        reward_coins=700, reward_xp=500, reward_polish=4,
    ),
)


# How many of each we surface to the player.
DAILY_PICKS = 3
WEEKLY_PICKS = 1


def by_id(qid: str) -> QuestTemplate | None:
    for t in DAILY + WEEKLY:
        if t.id == qid:
            return t
    return None
