"""Chaos Raid engine — pure logic over a state dict.

Damage model: the attacker's deck does ONE all-out hit per raid action.
We sum the deck's effective CP (post-tool bonuses), apply the element
triangle using the leading maid's element vs the boss element, multiply
by a flat alpha-strike coefficient, and apply random variance.

Reward distribution at kill time uses % damage contributed:

    >= 30%   "champion"   300 coins, 150 XP, 1 Royal Service Pack
    >= 10%   "officer"    150 coins,  75 XP, 1 Polished Pack
    >   0%   "helper"      50 coins,  30 XP
    killing blow                +50 RP bonus
"""
from __future__ import annotations

import datetime as _dt
import random
from typing import Any

from data import elements as elements_data
from data import maids as maids_data
from data import raid_bosses as bosses_data
from data import tools as tools_data
from store import sql as sql_store


ALPHA_STRIKE_MULTIPLIER = 4
CHAMPION_THRESHOLD_PCT = 30.0
OFFICER_THRESHOLD_PCT  = 10.0


def fresh_raid(boss_id: str) -> dict[str, Any]:
    """Build a new raid state for the given boss id."""
    boss = bosses_data.BY_ID.get(boss_id) or bosses_data.CYCLE[0]
    return {
        "boss_id": boss.id,
        "hp": boss.hp,
        "max_hp": boss.hp,
        "contributors": {},
        "started_at": _dt.datetime.utcnow().isoformat(timespec="seconds") + "+00:00",
    }


def _deck_effective_cp_and_element(
    deck: dict[str, list[str]],
    levels: dict[tuple[str, str], int] | None = None,
) -> tuple[int, str]:
    """Total CP of every maid in the deck (with tool + level bonuses)
    plus the lead maid's element for matchup purposes.
    """
    levels = levels or {}
    maid_ids = [c for c in (deck.get("maids") or []) if c][:3]
    tool_ids = [c for c in (deck.get("tools") or []) if c][:3]
    total = 0
    lead_element = ""
    for i, mid in enumerate(maid_ids):
        m = maids_data.BY_ID.get(mid)
        if not m:
            continue
        cp = m.clean_power
        tool = tool_ids[i] if i < len(tool_ids) else ""
        if tool:
            t = tools_data.BY_ID.get(tool)
            if t:
                cp += t.cp_bonus
        lvl = int(levels.get(("maid", mid), 1))
        if lvl > 1:
            cp += sql_store.level_bonus_cp(lvl)
        total += cp
        if not lead_element:
            lead_element = m.element
    return total, lead_element


def attack(
    state: dict[str, Any], user_id: str, deck: dict[str, list[str]],
    *, rng: random.Random | None = None,
    ctx=None,
) -> tuple[dict[str, Any], int, bool]:
    """Apply one attack to the raid. Returns (new_state, damage_dealt, killed).

    ``killed`` is True if this attack reduced HP to zero. The caller is
    responsible for distributing rewards and starting the next raid.
    """
    r = rng or random
    boss = bosses_data.BY_ID.get(state.get("boss_id", ""))
    if not boss:
        return state, 0, False
    if int(state.get("hp", 0)) <= 0:
        return state, 0, False

    levels: dict[tuple[str, str], int] = {}
    if ctx is not None and user_id:
        try:
            levels = sql_store.get_deck_levels(ctx, user_id, deck)
        except Exception:
            levels = {}
    cp, lead_el = _deck_effective_cp_and_element(deck, levels)
    mult = elements_data.multiplier(lead_el, boss.element)
    variance = r.uniform(0.8, 1.2)
    base = max(1, cp * ALPHA_STRIKE_MULTIPLIER)
    damage = max(1, int(round(base * mult * variance)))

    new_hp = max(0, int(state["hp"]) - damage)
    state = {**state, "hp": new_hp}
    contributors = dict(state.get("contributors") or {})
    contributors[str(user_id)] = int(contributors.get(str(user_id), 0)) + damage
    state["contributors"] = contributors

    killed = new_hp == 0
    return state, damage, killed


def reward_tier(damage_pct: float) -> str:
    """Bucket name for a contributor at a given percent of total damage."""
    if damage_pct >= CHAMPION_THRESHOLD_PCT:
        return "champion"
    if damage_pct >= OFFICER_THRESHOLD_PCT:
        return "officer"
    return "helper"


def distribute_rewards(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Compute per-user reward bundles. Caller writes them.

    Returns ``{user_id: {tier, coins, xp, polished_packs, royal_packs}}``.
    """
    contribs: dict[str, int] = state.get("contributors") or {}
    total_dmg = max(1, sum(int(v) for v in contribs.values()))
    out: dict[str, dict[str, Any]] = {}
    for uid, dmg in contribs.items():
        pct = 100.0 * int(dmg) / total_dmg
        tier = reward_tier(pct)
        if tier == "champion":
            bundle = {"tier": tier, "coins": 300, "xp": 150,
                      "polished_packs": 0, "royal_packs": 1, "damage": int(dmg), "pct": pct}
        elif tier == "officer":
            bundle = {"tier": tier, "coins": 150, "xp":  75,
                      "polished_packs": 1, "royal_packs": 0, "damage": int(dmg), "pct": pct}
        else:
            bundle = {"tier": tier, "coins":  50, "xp":  30,
                      "polished_packs": 0, "royal_packs": 0, "damage": int(dmg), "pct": pct}
        out[uid] = bundle
    return out


def top_contributors(state: dict[str, Any], limit: int = 5) -> list[tuple[str, int]]:
    contribs = (state.get("contributors") or {}).items()
    return sorted([(str(k), int(v)) for k, v in contribs], key=lambda x: x[1], reverse=True)[:limit]
