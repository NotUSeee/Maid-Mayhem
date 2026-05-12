"""Damage calculation for the battle engine.

Pure: no SDK, no I/O. The battle engine composes these.
"""
from __future__ import annotations

import random

from data import elements as elements_data


def attack_damage(
    attacker_cp: int,
    attacker_element: str,
    defender_element: str,
    *,
    defending: bool = False,
    rng: random.Random | None = None,
) -> int:
    """Compute damage from one attack.

    Element advantage = 1.5x, disadvantage = 0.75x.
    Variance: 0.85x .. 1.15x.
    Defending halves damage (rounded up).
    Minimum damage 1 (so battles always progress).
    """
    r = rng or random
    mult = elements_data.multiplier(attacker_element, defender_element)
    variance = r.uniform(0.85, 1.15)
    raw = max(1.0, attacker_cp * mult * variance)
    if defending:
        raw = max(1.0, raw / 2.0)
    return max(1, int(round(raw)))
