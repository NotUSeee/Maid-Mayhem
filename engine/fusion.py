"""Fusion engine — pure logic for selecting cards to consume and rolling
the output. The handler (handlers/fuse.py) does I/O.

Selection rule: consume copies greedily from the inventory rows with the
highest ``count`` first. This consolidates inventory (dupes burned first)
and keeps unique cards intact when possible.
"""
from __future__ import annotations

import random
from typing import Any

from data import fusion as fusion_data
from data import maids as maids_data
from data import tools as tools_data


def _rarity_of(card_type: str, card_id: str) -> str:
    if card_type == "maid":
        m = maids_data.BY_ID.get(card_id)
        return m.rarity if m else ""
    t = tools_data.BY_ID.get(card_id)
    return t.rarity if t else ""


def usable_inventory(rows: list[dict[str, Any]], rarity: str) -> list[dict[str, Any]]:
    """Filter inventory rows to those matching ``rarity`` with count > 0."""
    out = []
    for row in rows:
        if int(row.get("count", 0)) <= 0:
            continue
        if _rarity_of(str(row.get("card_type", "")), str(row.get("card_id", ""))) != rarity:
            continue
        out.append(row)
    # highest-count first so dupes get burned before unique cards
    out.sort(key=lambda r: int(r.get("count", 0)), reverse=True)
    return out


def total_at_rarity(rows: list[dict[str, Any]], rarity: str) -> int:
    return sum(int(r.get("count", 0)) for r in usable_inventory(rows, rarity))


def plan_consumption(
    rows: list[dict[str, Any]], rarity: str, cost: int,
) -> list[tuple[str, str, int]]:
    """Greedy consumption plan: returns (card_type, card_id, qty) tuples
    summing to ``cost``. Returns empty list if the user lacks enough.
    """
    eligible = usable_inventory(rows, rarity)
    if sum(int(r.get("count", 0)) for r in eligible) < cost:
        return []
    plan: list[tuple[str, str, int]] = []
    remaining = cost
    for row in eligible:
        if remaining <= 0:
            break
        take = min(int(row["count"]), remaining)
        plan.append((str(row["card_type"]), str(row["card_id"]), take))
        remaining -= take
    return plan


def roll_output(to_rarity: str, rng: random.Random | None = None) -> tuple[str, str]:
    """Pick a uniformly random card (maid or tool) at the target rarity."""
    r = rng or random
    pool: list[tuple[str, str]] = []
    for m in maids_data.BY_RARITY.get(to_rarity, []):
        pool.append(("maid", m.id))
    for t in tools_data.BY_RARITY.get(to_rarity, []):
        pool.append(("tool", t.id))
    if not pool:
        # No cards at target rarity (e.g. mythic tools don't exist) — should
        # never happen for fusion since recipes only target rarities that
        # have at least one maid. Defensive only.
        raise ValueError(f"No cards available at rarity {to_rarity!r}")
    return r.choice(pool)


def recipe_for(from_rarity: str):
    return fusion_data.BY_FROM.get(from_rarity)
