"""Combat status effects.

Each unit carries a ``status`` dict. Keys are absent when inactive.

    poison_dmg, poison_turns   poison_dmg damage applied at owner's
                               phase-start; poison_turns decrements there
    frozen_turns               skip own attack this many turns
    shield                     flat raw-damage absorption (no timer; depletes)
    cp_mod, cp_mod_turns       +/- CP applied to outgoing damage for
                               cp_mod_turns. Decrements at owner phase-start.

Per-turn ordering at the start of a side's turn:
    1. tick_phase_start          — poison damage, timer decrements
    2. for each unit's attack:
         - is_frozen_skip(unit)  — frozen consumes one stack and skips
         - effective_cp(unit)    — applied to damage calc
         - apply_raw_damage      — runs through shield then poise
"""
from __future__ import annotations

from typing import Any


def _s(unit: dict[str, Any]) -> dict[str, Any]:
    """Return (and create if missing) the status dict on a unit."""
    st = unit.get("status")
    if not isinstance(st, dict):
        st = {}
        unit["status"] = st
    return st


# ── Read helpers (used during damage calc + attack flow) ────────────────────

def effective_cp(unit: dict[str, Any]) -> int:
    """Unit's CP modified by any active cp_mod buff/debuff."""
    base = int(unit.get("cp", 0))
    st = unit.get("status") or {}
    return max(0, base + int(st.get("cp_mod", 0)))


def is_frozen_skip(unit: dict[str, Any]) -> bool:
    """If the unit is frozen, consumes one turn-of-freeze and returns True
    so the caller skips its attack. Mutates the unit in place."""
    st = _s(unit)
    if int(st.get("frozen_turns", 0)) > 0:
        st["frozen_turns"] = int(st["frozen_turns"]) - 1
        if st["frozen_turns"] <= 0:
            st.pop("frozen_turns", None)
        return True
    return False


def apply_raw_damage(unit: dict[str, Any], damage: int) -> int:
    """Apply ``damage`` to a unit, absorbing through ``shield`` first.

    Returns the amount of damage that actually landed on Poise (after the
    shield ate its share). Both unit and unit['status'] are mutated.
    """
    if damage <= 0:
        return 0
    st = _s(unit)
    absorbed = 0
    if int(st.get("shield", 0)) > 0:
        absorbed = min(int(st["shield"]), damage)
        st["shield"] = int(st["shield"]) - absorbed
        if st["shield"] <= 0:
            st.pop("shield", None)
        damage -= absorbed
    if damage > 0:
        unit["poise"] = max(0, int(unit.get("poise", 0)) - damage)
    return damage


# ── Applier helpers (used by abilities to GRANT status) ─────────────────────

def add_shield(unit: dict[str, Any], amount: int) -> None:
    if amount <= 0:
        return
    st = _s(unit)
    st["shield"] = int(st.get("shield", 0)) + amount


def add_poison(unit: dict[str, Any], dmg_per_turn: int, turns: int) -> None:
    if dmg_per_turn <= 0 or turns <= 0:
        return
    st = _s(unit)
    # If already poisoned, take the stronger dot and the longer duration.
    st["poison_dmg"]   = max(int(st.get("poison_dmg", 0)), dmg_per_turn)
    st["poison_turns"] = max(int(st.get("poison_turns", 0)), turns)


def add_freeze(unit: dict[str, Any], turns: int) -> None:
    if turns <= 0:
        return
    st = _s(unit)
    st["frozen_turns"] = max(int(st.get("frozen_turns", 0)), turns)


def add_cp_mod(unit: dict[str, Any], amount: int, turns: int) -> None:
    """Stack-with-max for amount; refresh duration. Positive = buff,
    negative = debuff."""
    if turns <= 0 or amount == 0:
        return
    st = _s(unit)
    if amount > 0:
        st["cp_mod"] = max(int(st.get("cp_mod", 0)), amount)
    else:
        st["cp_mod"] = min(int(st.get("cp_mod", 0)), amount)
    st["cp_mod_turns"] = max(int(st.get("cp_mod_turns", 0)), turns)


def clear_negative(unit: dict[str, Any]) -> bool:
    """Remove poison / frozen / negative cp_mod. Returns True if anything
    was actually cleared (handy for log lines)."""
    st = unit.get("status") or {}
    cleared = False
    if "poison_dmg" in st or "poison_turns" in st:
        st.pop("poison_dmg", None); st.pop("poison_turns", None); cleared = True
    if "frozen_turns" in st:
        st.pop("frozen_turns", None); cleared = True
    if int(st.get("cp_mod", 0)) < 0:
        st.pop("cp_mod", None); st.pop("cp_mod_turns", None); cleared = True
    return cleared


# ── Tick at start of owner's phase ──────────────────────────────────────────

def tick_phase_start(team: list[dict[str, Any]], log: list[str]) -> None:
    """Apply poison damage and decrement timers for the side whose turn
    is starting. Removes expired statuses. Skips dead units.
    """
    for unit in team:
        if int(unit.get("poise", 0)) <= 0:
            continue
        st = _s(unit)
        # Poison damage
        if int(st.get("poison_dmg", 0)) > 0 and int(st.get("poison_turns", 0)) > 0:
            dmg = int(st["poison_dmg"])
            apply_raw_damage(unit, dmg)
            log.append(f"{unit.get('name', '?')} takes {dmg} poison damage.")
            if int(unit.get("poise", 0)) == 0:
                log.append(f"{unit.get('name', '?')} succumbs to poison.")
            st["poison_turns"] = int(st["poison_turns"]) - 1
            if st["poison_turns"] <= 0:
                st.pop("poison_dmg", None)
                st.pop("poison_turns", None)
        # cp_mod timer
        if int(st.get("cp_mod_turns", 0)) > 0:
            st["cp_mod_turns"] = int(st["cp_mod_turns"]) - 1
            if st["cp_mod_turns"] <= 0:
                st.pop("cp_mod", None)
                st.pop("cp_mod_turns", None)
