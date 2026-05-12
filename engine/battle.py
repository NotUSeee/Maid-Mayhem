"""Turn-based PvE battle engine.

Pure functions over a state dict. The handler (handlers/battle.py)
owns I/O — load state, call take_turn, render, save state.

State shape::

    {
      "user_id": "...",
      "turn": 1,
      "defending": False,         # True if player chose Defend this turn
      "player_team": [unit, ...], # 1-3 maids
      "enemy_team": [unit, ...],  # 1-3 chaos
      "log": ["...", ...],        # human-readable lines
      "rewards": {"coins": 0, "xp": 0},
      "result": None,             # 'win' | 'loss' | 'flee' once terminal
    }

Unit shape::

    {
      "kind": "maid" | "chaos",
      "id": "luna",
      "name": "Luna, the Moonlit Maid",
      "element": "moon",
      "cp": 4, "charm": 9, "speed": 6,
      "poise": 7, "max_poise": 7,
      "tool_id": "..."  # maids only, may be ""
    }
"""
from __future__ import annotations

import random
from typing import Any

from data import chaos as chaos_data
from data import maids as maids_data
from data import tools as tools_data
from engine import abilities as abilities_engine
from engine import damage as damage_engine
from engine import status as status_engine


# ── State setup ─────────────────────────────────────────────────────────────

def _maid_unit(maid_id: str, tool_id: str = "") -> dict[str, Any] | None:
    m = maids_data.BY_ID.get(maid_id)
    if not m:
        return None
    cp, poise, charm, speed = m.clean_power, m.poise, m.charm, m.speed
    if tool_id:
        t = tools_data.BY_ID.get(tool_id)
        if t:
            cp    += t.cp_bonus
            poise += t.poise_bonus
            charm += t.charm_bonus
            speed += t.speed_bonus
    return {
        "kind": "maid",
        "id": m.id,
        "name": m.name,
        "element": m.element,
        "cp": cp, "charm": charm, "speed": speed,
        "poise": poise, "max_poise": poise,
        "tool_id": tool_id,
        "ability_id": m.ability_id,
        "ability_name": m.ability_name,
        "status": {},
    }


def _chaos_unit(chaos_id: str) -> dict[str, Any] | None:
    c = chaos_data.BY_ID.get(chaos_id)
    if not c:
        return None
    return {
        "kind": "chaos",
        "id": c.id,
        "name": c.name,
        "element": c.element,
        "cp": c.clean_power, "charm": 0, "speed": c.speed,
        "poise": c.poise, "max_poise": c.poise,
        "tool_id": "",
        "status": {},
    }


def start_battle(
    user_id: str,
    deck: dict[str, list[str]],
    *,
    rng: random.Random | None = None,
) -> dict[str, Any]:
    """Compose a fresh battle state from the user's deck."""
    r = rng or random
    maid_ids = [c for c in (deck.get("maids") or []) if c][:3]
    tool_ids = [c for c in (deck.get("tools") or []) if c][:3]

    player_team: list[dict[str, Any]] = []
    for i, mid in enumerate(maid_ids):
        tool = tool_ids[i] if i < len(tool_ids) else ""
        u = _maid_unit(mid, tool)
        if u:
            player_team.append(u)

    if not player_team:
        return {
            "user_id": user_id, "turn": 0, "defending": False,
            "player_team": [], "enemy_team": [], "log": [],
            "rewards": {"coins": 0, "xp": 0},
            "result": "no_deck",
        }

    # Enemy roster: 3 chaos enemies, biased toward lower tiers
    tier_weights = {1: 5, 2: 3, 3: 1}
    pool: list[str] = []
    for tier, weight in tier_weights.items():
        for c in chaos_data.BY_TIER.get(tier, []):
            pool.extend([c.id] * weight)
    enemy_ids = [r.choice(pool) for _ in range(3)]
    enemy_team = [u for u in (_chaos_unit(cid) for cid in enemy_ids) if u]

    return {
        "user_id": user_id,
        "turn": 1,
        "defending": False,
        "player_team": player_team,
        "enemy_team": enemy_team,
        # Per-maid ability cooldown counters, parallel to player_team.
        # 0 = ready; decrements by 1 each round after the player phase.
        "ability_cooldowns": [0 for _ in player_team],
        "log": [f"You face: {', '.join(u['name'] for u in enemy_team)}."],
        "rewards": {"coins": 0, "xp": 0},
        "result": None,
    }


# ── Turn resolution ─────────────────────────────────────────────────────────

def _alive(units: list[dict[str, Any]]) -> list[int]:
    return [i for i, u in enumerate(units) if int(u.get("poise", 0)) > 0]


def _pick_target(units: list[dict[str, Any]], rng: random.Random) -> int | None:
    alive = _alive(units)
    if not alive:
        return None
    # Target the one with the lowest current poise (try to finish them).
    alive.sort(key=lambda i: int(units[i].get("poise", 0)))
    return alive[0]


def _check_terminal(state: dict[str, Any]) -> str | None:
    if not _alive(state["enemy_team"]):
        return "win"
    if not _alive(state["player_team"]):
        return "loss"
    return None


def _basic_attack_team(
    player: list[dict[str, Any]],
    enemies: list[dict[str, Any]],
    log: list[str],
    r: random.Random,
    *,
    skip_idx: int | None = None,
) -> None:
    """Each living player maid takes one basic attack against the lowest-poise
    living enemy. Mutates ``enemies`` and ``log`` in place. Frozen units
    skip and consume one freeze stack; shield absorbs before poise.
    """
    for i, m in enumerate(player):
        if i == skip_idx:
            continue
        if int(m.get("poise", 0)) <= 0:
            continue
        if status_engine.is_frozen_skip(m):
            log.append(f"{m['name']} is frozen and skips their turn.")
            continue
        t_idx = _pick_target(enemies, r)
        if t_idx is None:
            break
        target = enemies[t_idx]
        dmg = damage_engine.attack_damage(
            status_engine.effective_cp(m), str(m.get("element", "")),
            str(target.get("element", "")), rng=r,
        )
        landed = status_engine.apply_raw_damage(target, dmg)
        absorbed = dmg - landed
        if absorbed > 0:
            log.append(f"{m['name']} hits {target['name']} for {dmg} ({absorbed} blocked by shield).")
        else:
            log.append(f"{m['name']} hits {target['name']} for {dmg}.")
        if int(target.get("poise", 0)) == 0:
            log.append(f"{target['name']} is cleaned up.")


def take_turn(
    state: dict[str, Any],
    action: str,
    *,
    rng: random.Random | None = None,
) -> dict[str, Any]:
    """Apply one full round (player phase + enemy phase) and return new state.

    ``action`` is one of:
      - "attack"        whole team basic-attacks
      - "defend"        no attacks; halve damage taken this round
      - "flee"          end battle, minimal rewards
      - "ability:N"     player maid N uses their ability; others basic-attack
    """
    r = rng or random
    if state.get("result"):
        return state

    log: list[str] = list(state.get("log") or [])
    player = list(state["player_team"])
    enemies = list(state["enemy_team"])
    cooldowns = list(state.get("ability_cooldowns") or [0] * len(player))
    # Pad cooldowns if state predates the field (defensive).
    while len(cooldowns) < len(player):
        cooldowns.append(0)

    if action == "flee":
        log.append("You flee the battle.")
        return {**state, "log": log[-12:], "result": "flee",
                "rewards": {"coins": 0, "xp": 5}}

    defending = (action == "defend")
    if defending:
        log.append("Your maids brace for impact (incoming damage halved).")

    # Status tick for player team at the start of their phase.
    status_engine.tick_phase_start(player, log)

    # ── Player phase ────────────────────────────────────────────────────────
    ability_maid_idx: int | None = None
    if action.startswith("ability:"):
        try:
            ability_maid_idx = int(action.split(":", 1)[1])
        except ValueError:
            ability_maid_idx = None

    if ability_maid_idx is not None:
        # Validate the ability use; fall back to basic attack on any issue
        # so the player doesn't lose their turn to bad input.
        valid = (
            0 <= ability_maid_idx < len(player)
            and int(player[ability_maid_idx].get("poise", 0)) > 0
            and cooldowns[ability_maid_idx] == 0
        )
        if not valid:
            log.append("(Ability unavailable — attacking instead.)")
            _basic_attack_team(player, enemies, log, r)
        else:
            m = player[ability_maid_idx]
            ability = abilities_engine.get(str(m.get("ability_id", "")))
            if ability is None:
                log.append(f"{m['name']} has no recorded ability — attacking instead.")
                _basic_attack_team(player, enemies, log, r)
            else:
                ability_state = {"player_team": player, "enemy_team": enemies}
                ability_lines = ability.apply(ability_state, ability_maid_idx, r)
                log.extend(ability_lines)
                cooldowns[ability_maid_idx] = int(ability.cooldown)
                # Other maids still get their basic attack this round.
                _basic_attack_team(player, enemies, log, r,
                                   skip_idx=ability_maid_idx)
    elif action == "attack":
        _basic_attack_team(player, enemies, log, r)

    # Decrement cooldowns once per round (they were "spent" on this turn).
    next_cooldowns = [max(0, c - 1) for c in cooldowns]

    # Check victory before enemy phase
    if not _alive(enemies):
        coins = 25 + 10 * sum(1 for m in player if int(m.get("poise", 0)) > 0)
        xp = 30 + 5 * state["turn"]
        return {
            **state,
            "turn": int(state["turn"]) + 1,
            "defending": False,
            "player_team": player,
            "enemy_team": enemies,
            "ability_cooldowns": next_cooldowns,
            "log": log[-12:],
            "rewards": {"coins": coins, "xp": xp},
            "result": "win",
        }

    # ── Enemy phase ─────────────────────────────────────────────────────────
    # Status tick for enemy team at the start of their phase.
    status_engine.tick_phase_start(enemies, log)

    for e in enemies:
        if int(e.get("poise", 0)) <= 0:
            continue
        if status_engine.is_frozen_skip(e):
            log.append(f"{e['name']} is frozen and skips their turn.")
            continue
        t_idx = _pick_target(player, r)
        if t_idx is None:
            break
        target = player[t_idx]
        dmg = damage_engine.attack_damage(
            status_engine.effective_cp(e), str(e.get("element", "")),
            str(target.get("element", "")),
            defending=defending, rng=r,
        )
        landed = status_engine.apply_raw_damage(target, dmg)
        absorbed = dmg - landed
        if absorbed > 0:
            log.append(f"{e['name']} strikes {target['name']} for {dmg} ({absorbed} blocked by shield).")
        else:
            log.append(f"{e['name']} strikes {target['name']} for {dmg}.")
        if int(target.get("poise", 0)) == 0:
            log.append(f"{target['name']} is overwhelmed.")

    result = _check_terminal({**state, "player_team": player, "enemy_team": enemies})
    rewards = {"coins": 0, "xp": 0}
    if result == "win":
        rewards = {"coins": 25, "xp": 30 + 5 * state["turn"]}
    elif result == "loss":
        rewards = {"coins": 0, "xp": 5}

    return {
        **state,
        "turn": int(state["turn"]) + 1,
        "defending": False,
        "player_team": player,
        "enemy_team": enemies,
        "ability_cooldowns": next_cooldowns,
        "log": log[-12:],
        "rewards": rewards,
        "result": result,
    }
