"""PvP turn-based duel engine.

Two-team turn machine: side ``a`` and side ``b`` alternate, each acting
fully on their own turn. Unlike PvE, the engine does NOT auto-counter —
the opponent's turn only fires when that player clicks a button.

State shape::

    {
      "duel_id": "abc123",
      "channel_id": "...",
      "a": {"user_id": "...", "user_name": "...", "team": [unit, ...],
            "ability_cooldowns": [int, ...], "defending": False},
      "b": {"user_id": "...", "user_name": "...", "team": [unit, ...],
            "ability_cooldowns": [int, ...], "defending": False},
      "turn_owner": "a" | "b",       # whose turn it is now
      "turn": 1,                      # increments each time turn_owner cycles back to "a"
      "log": [...],
      "result": None | "a_wins" | "b_wins" | "a_fled" | "b_fled",
    }
"""
from __future__ import annotations

import random
from typing import Any

from engine import abilities as abilities_engine
from engine import battle as battle_engine
from engine import damage as damage_engine


OTHER = {"a": "b", "b": "a"}


def _alive(team: list[dict[str, Any]]) -> list[int]:
    return [i for i, u in enumerate(team) if int(u.get("poise", 0)) > 0]


def _lowest_poise_idx(team: list[dict[str, Any]]) -> int | None:
    alive = _alive(team)
    if not alive:
        return None
    alive.sort(key=lambda i: int(team[i].get("poise", 0)))
    return alive[0]


def start_duel(
    duel_id: str, channel_id: str,
    a_user_id: str, a_user_name: str, a_deck: dict[str, list[str]],
    b_user_id: str, b_user_name: str, b_deck: dict[str, list[str]],
    *,
    rng: random.Random | None = None,
) -> dict[str, Any]:
    """Compose a fresh PvP duel from two decks."""
    def _build(deck):
        maid_ids = [c for c in (deck.get("maids") or []) if c][:3]
        tool_ids = [c for c in (deck.get("tools") or []) if c][:3]
        team = []
        for i, mid in enumerate(maid_ids):
            tool = tool_ids[i] if i < len(tool_ids) else ""
            u = battle_engine._maid_unit(mid, tool)
            if u:
                team.append(u)
        return team

    team_a = _build(a_deck)
    team_b = _build(b_deck)

    # Higher total speed acts first. Tie -> challenger ('a').
    speed_a = sum(int(u.get("speed", 0)) for u in team_a)
    speed_b = sum(int(u.get("speed", 0)) for u in team_b)
    first = "a" if speed_a >= speed_b else "b"

    return {
        "duel_id": duel_id,
        "channel_id": str(channel_id),
        "a": {
            "user_id": str(a_user_id), "user_name": str(a_user_name),
            "team": team_a, "ability_cooldowns": [0] * len(team_a),
            "defending": False,
        },
        "b": {
            "user_id": str(b_user_id), "user_name": str(b_user_name),
            "team": team_b, "ability_cooldowns": [0] * len(team_b),
            "defending": False,
        },
        "turn_owner": first,
        "turn": 1,
        "log": [
            f"⚔ Duel begins: {a_user_name} vs {b_user_name}.",
            f"{a_user_name if first == 'a' else b_user_name} acts first (more team Speed).",
        ],
        "result": None,
    }


# ── Turn resolution ─────────────────────────────────────────────────────────

def _basic_attack(
    attackers: list[dict[str, Any]], defenders: list[dict[str, Any]],
    log: list[str], r: random.Random, *,
    defender_defending: bool, skip_idx: int | None = None,
) -> None:
    for i, m in enumerate(attackers):
        if i == skip_idx:
            continue
        if int(m.get("poise", 0)) <= 0:
            continue
        t = _lowest_poise_idx(defenders)
        if t is None:
            break
        target = defenders[t]
        dmg = damage_engine.attack_damage(
            int(m["cp"]), str(m.get("element", "")), str(target.get("element", "")),
            defending=defender_defending, rng=r,
        )
        target["poise"] = max(0, int(target["poise"]) - dmg)
        log.append(f"{m['name']} hits {target['name']} for {dmg}.")
        if target["poise"] == 0:
            log.append(f"{target['name']} is cleaned up.")


def take_turn(
    state: dict[str, Any], action: str,
    *,
    rng: random.Random | None = None,
) -> dict[str, Any]:
    """Apply one side's action. ``action`` is one of:

      - "attack"        active side's team basic-attacks the other side
      - "defend"        active side braces; opponent's next-turn damage halved
      - "ability:N"     active side's maid N uses ability; others basic-attack
      - "flee"          active side forfeits; opponent wins
    """
    r = rng or random
    if state.get("result"):
        return state

    me = state["turn_owner"]
    them = OTHER[me]
    side_me = state[me]
    side_them = state[them]
    log = list(state.get("log") or [])

    if action == "flee":
        log.append(f"{side_me['user_name']} flees the duel.")
        new_state = {**state, "log": log[-12:],
                     "result": f"{me}_fled"}
        return new_state

    if action == "defend":
        side_me["defending"] = True
        log.append(f"{side_me['user_name']} braces (their damage taken next is halved).")
        # End-of-turn cooldown decrement still happens
        side_me["ability_cooldowns"] = [max(0, c - 1) for c in side_me["ability_cooldowns"]]
        return _advance(state, log)

    # Defender's "defending" applies once, then drops
    defender_defending = bool(side_them.get("defending", False))

    if action.startswith("ability:"):
        try:
            idx = int(action.split(":", 1)[1])
        except ValueError:
            idx = -1
        if (0 <= idx < len(side_me["team"])
                and int(side_me["team"][idx].get("poise", 0)) > 0
                and side_me["ability_cooldowns"][idx] == 0):
            user = side_me["team"][idx]
            ability = abilities_engine.get(str(user.get("ability_id", "")))
            if ability is not None:
                # The ability functions expect "player_team" / "enemy_team" keys.
                ability_state = {"player_team": side_me["team"], "enemy_team": side_them["team"]}
                lines = ability.apply(ability_state, idx, r)
                log.extend(lines)
                side_me["ability_cooldowns"][idx] = int(ability.cooldown)
                # The other living maids still basic-attack
                _basic_attack(side_me["team"], side_them["team"], log, r,
                              defender_defending=defender_defending, skip_idx=idx)
            else:
                log.append("(Ability not found; attacking instead.)")
                _basic_attack(side_me["team"], side_them["team"], log, r,
                              defender_defending=defender_defending)
        else:
            log.append("(Ability unavailable; attacking instead.)")
            _basic_attack(side_me["team"], side_them["team"], log, r,
                          defender_defending=defender_defending)
    else:  # "attack" or anything else falls through to basic attack
        _basic_attack(side_me["team"], side_them["team"], log, r,
                      defender_defending=defender_defending)

    # Defender's brace dropped this turn
    side_them["defending"] = False

    # End-of-turn cooldown decrement for the active side only
    side_me["ability_cooldowns"] = [max(0, c - 1) for c in side_me["ability_cooldowns"]]

    return _advance(state, log)


def _advance(state: dict[str, Any], log: list[str]) -> dict[str, Any]:
    """Check terminal conditions; otherwise flip turn_owner."""
    me = state["turn_owner"]
    them = OTHER[me]
    side_me = state[me]
    side_them = state[them]

    if not _alive(side_them["team"]):
        log.append(f"🏆 {side_me['user_name']} wins!")
        return {**state, "log": log[-12:], "result": f"{me}_wins"}
    if not _alive(side_me["team"]):
        # Shouldn't normally happen on the active side's turn, but defensive
        log.append(f"🏆 {side_them['user_name']} wins by attrition.")
        return {**state, "log": log[-12:], "result": f"{them}_wins"}

    new_owner = OTHER[me]
    new_turn = state["turn"] + (1 if new_owner == "a" else 0)
    return {**state, "log": log[-12:], "turn_owner": new_owner, "turn": new_turn}
