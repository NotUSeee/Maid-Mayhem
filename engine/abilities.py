"""Maid ability registry.

Each maid card's ``ability_id`` (defined in data/maids.py) maps to an
``Ability`` record here. An ability is resolved as a one-shot effect on
the current battle state — no multi-turn buff/debuff machinery in v1.1
(deferred for v1.2 to keep the engine surface small).

Cooldowns: 2 or 3 turns. The first turn of battle, every ability is
ready (cooldown 0). Cooldowns are stored on the battle state as a list
parallel to ``player_team`` (engine/battle.py).
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Callable

# An ability's effect: takes (state, source_idx, rng) and mutates state in
# place, returning a list of human-readable log lines.
AbilityFn = Callable[[dict[str, Any], int, random.Random], list[str]]


@dataclass(frozen=True)
class Ability:
    id: str
    name: str
    cooldown: int        # turns until reusable; 0 = always ready
    description: str     # shown on the battle button tooltip
    apply: AbilityFn


# ── Generic helpers ─────────────────────────────────────────────────────────

def _alive(units: list[dict[str, Any]]) -> list[int]:
    return [i for i, u in enumerate(units) if int(u.get("poise", 0)) > 0]


def _heal(unit: dict[str, Any], amount: int) -> int:
    """Heal unit, capped at max_poise. Returns actual amount healed."""
    cur = int(unit.get("poise", 0))
    mx  = int(unit.get("max_poise", cur))
    new = min(mx, cur + max(0, amount))
    healed = new - cur
    unit["poise"] = new
    return healed


def _damage(unit: dict[str, Any], amount: int) -> int:
    """Deal raw damage (bypasses defending — abilities go through)."""
    cur = int(unit.get("poise", 0))
    new = max(0, cur - max(0, amount))
    unit["poise"] = new
    return cur - new


def _weakest_idx(units: list[dict[str, Any]], *, exclude: int | None = None) -> int | None:
    cands = [(i, int(u.get("poise", 0))) for i, u in enumerate(units)
             if int(u.get("poise", 0)) > 0 and i != exclude]
    if not cands:
        return None
    cands.sort(key=lambda x: x[1])
    return cands[0][0]


def _name(unit: dict[str, Any]) -> str:
    return str(unit.get("name", "?"))


# ── Ability implementations ────────────────────────────────────────────────

def _self_heal(amount: int) -> AbilityFn:
    def fn(state, src, rng):
        m = state["player_team"][src]
        healed = _heal(m, amount)
        return [f"{_name(m)} uses their special. +{healed} Poise."]
    return fn


def _heal_ally(amount: int, *, prefer_other: bool = True) -> AbilityFn:
    def fn(state, src, rng):
        team = state["player_team"]
        idx = _weakest_idx(team, exclude=src if prefer_other else None)
        if idx is None:
            idx = src
        target = team[idx]
        healed = _heal(target, amount)
        return [f"{_name(team[src])} heals {_name(target)} for {healed} Poise."]
    return fn


def _heal_all(amount: int) -> AbilityFn:
    def fn(state, src, rng):
        team = state["player_team"]
        lines = [f"{_name(team[src])} mends the whole crew."]
        total = 0
        for u in team:
            if int(u.get("poise", 0)) > 0:
                total += _heal(u, amount)
        lines.append(f"Healed +{total} Poise across the team.")
        return lines
    return fn


def _strike(amount: int) -> AbilityFn:
    def fn(state, src, rng):
        enemies = state["enemy_team"]
        idx = _weakest_idx(enemies)
        if idx is None:
            return [f"{_name(state['player_team'][src])} winds up, but there's nothing to hit."]
        target = enemies[idx]
        dealt = _damage(target, amount)
        line = f"{_name(state['player_team'][src])} hits {_name(target)} for {dealt}."
        if int(target["poise"]) == 0:
            line += f" {_name(target)} is cleaned up."
        return [line]
    return fn


def _sweep_strike() -> AbilityFn:
    """Deal 7; if the target dies, deal 4 to the next-weakest enemy."""
    def fn(state, src, rng):
        enemies = state["enemy_team"]
        first_idx = _weakest_idx(enemies)
        if first_idx is None:
            return [f"{_name(state['player_team'][src])} sweeps, but the floor is clean."]
        first = enemies[first_idx]
        dealt1 = _damage(first, 7)
        lines = [f"{_name(state['player_team'][src])} sweeps {_name(first)} for {dealt1}."]
        if int(first["poise"]) == 0:
            lines.append(f"{_name(first)} is cleaned up.")
            second_idx = _weakest_idx(enemies)
            if second_idx is not None:
                second = enemies[second_idx]
                dealt2 = _damage(second, 4)
                lines.append(f"Follow-through on {_name(second)} for {dealt2}.")
                if int(second["poise"]) == 0:
                    lines.append(f"{_name(second)} is cleaned up.")
        return lines
    return fn


def _heal_ally_and_strike(heal: int, strike: int) -> AbilityFn:
    def fn(state, src, rng):
        team = state["player_team"]
        enemies = state["enemy_team"]
        lines = []
        ally_idx = _weakest_idx(team, exclude=src)
        if ally_idx is None:
            ally_idx = src
        ally = team[ally_idx]
        healed = _heal(ally, heal)
        lines.append(f"{_name(team[src])} restores {_name(ally)} for {healed}.")
        en_idx = _weakest_idx(enemies)
        if en_idx is not None:
            enemy = enemies[en_idx]
            dealt = _damage(enemy, strike)
            lines.append(f"...and dishes a {dealt} to {_name(enemy)}.")
            if int(enemy["poise"]) == 0:
                lines.append(f"{_name(enemy)} is cleaned up.")
        return lines
    return fn


def _double_tap(amount: int) -> AbilityFn:
    """Hit the same enemy twice (or chain to a second if the first dies)."""
    def fn(state, src, rng):
        enemies = state["enemy_team"]
        idx = _weakest_idx(enemies)
        if idx is None:
            return [f"{_name(state['player_team'][src])} winds up, but the room is empty."]
        target = enemies[idx]
        d1 = _damage(target, amount)
        lines = [f"{_name(state['player_team'][src])} cracks {_name(target)} for {d1}."]
        if int(target["poise"]) == 0:
            lines.append(f"{_name(target)} is cleaned up.")
            nxt = _weakest_idx(enemies)
            if nxt is not None:
                target = enemies[nxt]
        if int(target["poise"]) > 0:
            d2 = _damage(target, amount)
            lines.append(f"...and again on {_name(target)} for {d2}.")
            if int(target["poise"]) == 0:
                lines.append(f"{_name(target)} is cleaned up.")
        return lines
    return fn


def _all_allies_small_heal() -> AbilityFn:
    return _heal_all(2)


def _self_buff_speed(amount: int) -> AbilityFn:
    """Permanent (for the battle) speed gain."""
    def fn(state, src, rng):
        m = state["player_team"][src]
        m["speed"] = int(m.get("speed", 0)) + amount
        return [f"{_name(m)} winds up — +{amount} Speed for the battle."]
    return fn


# ── Registry ────────────────────────────────────────────────────────────────

REGISTRY: dict[str, Ability] = {
    # Heal / support
    "fresh_start":         Ability("fresh_start",         "Fresh Start",        2,
        "Heal yourself for 3.",                                  _self_heal(3)),
    "heal_ally_2":         Ability("heal_ally_2",         "Sprouting Care",     2,
        "Heal an ally for 4.",                                   _heal_ally(4)),
    "heal_all_2":          Ability("heal_all_2",          "Sage Advice",        3,
        "Heal all allies for 3.",                                _heal_all(3)),
    "silver_polish":       Ability("silver_polish",       "Silver Polish",      3,
        "Heal an ally for 6.",                                   _heal_ally(6)),
    "tea_heal_poison":     Ability("tea_heal_poison",     "Perfect Tea",        3,
        "Heal an ally for 3 and deal 5 to an enemy.",            _heal_ally_and_strike(3, 5)),
    "cleanse_ally":        Ability("cleanse_ally",        "Steady Flame",       2,
        "Heal an ally for 4.",                                   _heal_ally(4)),
    "shield_all_3":        Ability("shield_all_3",        "Morning Aegis",      3,
        "Heal all allies for 4.",                                _heal_all(4)),
    "buff_ally_cp_2":      Ability("buff_ally_cp_2",      "Crown Polish",       2,
        "Heal an ally for 5.",                                   _heal_ally(5)),
    "all_allies_plus_speed_2": Ability("all_allies_plus_speed_2", "Synchronize", 3,
        "Heal all allies for 2.",                                _all_allies_small_heal()),
    "order_restored":      Ability("order_restored",      "Order Restored",     3,
        "Heal all allies for 5.",                                _heal_all(5)),

    # Damage
    "attack_bonus_1":      Ability("attack_bonus_1",      "Quick Singe",        2,
        "Deal 5 damage to the weakest enemy.",                   _strike(5)),
    "attack_4":            Ability("attack_4",            "Skillet Swing",      2,
        "Deal 7 damage to the weakest enemy.",                   _strike(7)),
    "sweep_strike":        Ability("sweep_strike",        "Sweep Strike",       3,
        "Deal 7; if it kills, deal 4 to the next.",              _sweep_strike()),
    "bonus_action_to_ally":Ability("bonus_action_to_ally","Wind-Up",            3,
        "Hit twice for 4 each.",                                 _double_tap(4)),
    "borrowed_silverware": Ability("borrowed_silverware", "Borrowed Silverware",3,
        "Deal 9 damage to the weakest enemy.",                   _strike(9)),

    # Damage-substitutes (these flavored as debuffs in v1; v1.2 will add
    # real multi-turn debuff machinery and rewire these).
    "slow_enemy_speed_2":  Ability("slow_enemy_speed_2",  "Cold Shoulder",      2,
        "Deal 4 damage to an enemy.",                            _strike(4)),
    "debuff_enemy_cp_1":   Ability("debuff_enemy_cp_1",   "Hush Hush",          2,
        "Deal 4 damage to an enemy.",                            _strike(4)),
    "freeze_enemy_skip_turn": Ability("freeze_enemy_skip_turn", "Drifting Hush",3,
        "Deal 6 damage to an enemy.",                            _strike(6)),

    # Self
    "buff_self_speed_1":   Ability("buff_self_speed_1",   "Spring-Loaded",      3,
        "Permanently gain +2 Speed this battle.",                _self_buff_speed(2)),
    "thorns_self":         Ability("thorns_self",         "Bramble Shroud",     2,
        "Heal yourself for 4.",                                  _self_heal(4)),
}


def get(ability_id: str) -> Ability | None:
    return REGISTRY.get(ability_id)
