"""Chaos enemy definitions.

10 enemies that appear in PvE battles. The named ones from the doc
(Laundry Hydra, Drama Spirit, Infinite Dishes, Dust Goblin, Sock Gremlin,
Mold Mimic) ship verbatim; 4 more round out the tier curve.

Tier (1=easy, 5=raid-boss) is used by engine/drops to pick which enemies
appear in a given encounter. MVP only uses tiers 1-3.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChaosEnemy:
    id: str
    name: str
    tier: int           # 1..5
    element: str        # element.id
    poise: int          # HP
    clean_power: int    # attack damage
    speed: int
    ability_id: str     # may be "basic_attack"
    ability_name: str
    ability_text: str
    flavor: str = ""


dust_goblin = ChaosEnemy(
    id="dust_goblin", name="Dust Goblin",
    tier=1, element="shadow",
    poise=6, clean_power=3, speed=5,
    ability_id="basic_attack",
    ability_name="Bite",
    ability_text="Deal 3 damage.",
    flavor="Made of lint and bad attitude.",
)

sock_gremlin = ChaosEnemy(
    id="sock_gremlin", name="Sock Gremlin",
    tier=1, element="shadow",
    poise=4, clean_power=4, speed=7,
    ability_id="basic_attack",
    ability_name="Snatch",
    ability_text="Deal 4 damage and skitter away (high speed).",
    flavor="Has stolen exactly one of every pair you own.",
)

drama_spill = ChaosEnemy(
    id="drama_spill", name="Drama Spill",
    tier=1, element="moon",
    poise=5, clean_power=2, speed=4,
    ability_id="debuff_charm_all",
    ability_name="Awkward Silence",
    ability_text="All player maids lose 1 Charm for 1 turn.",
    flavor="It just sits there. Judging.",
)

mold_mimic = ChaosEnemy(
    id="mold_mimic", name="Mold Mimic",
    tier=2, element="garden",
    poise=10, clean_power=4, speed=3,
    ability_id="basic_attack",
    ability_name="Slop",
    ability_text="Deal 4 damage.",
    flavor="Looks like a teapot. Is not a teapot.",
)

snack_gremlin = ChaosEnemy(
    id="snack_gremlin", name="Snack Gremlin",
    tier=2, element="fire",
    poise=8, clean_power=5, speed=6,
    ability_id="basic_attack",
    ability_name="Crumb Storm",
    ability_text="Deal 5 damage in a shower of crumbs.",
    flavor="Lives in the couch. Mostly.",
)

infinite_dishes = ChaosEnemy(
    id="infinite_dishes", name="Infinite Dishes",
    tier=2, element="frost",
    poise=12, clean_power=3, speed=2,
    ability_id="slow_all_1",
    ability_name="Clatter",
    ability_text="All player maids lose 1 Speed at end of turn.",
    flavor="There were six. Now there are twenty-six. There were six.",
)

possessed_kettle = ChaosEnemy(
    id="possessed_kettle", name="Possessed Kettle",
    tier=2, element="fire",
    poise=9, clean_power=6, speed=5,
    ability_id="basic_attack",
    ability_name="Boilover",
    ability_text="Deal 6 damage.",
    flavor="Steam is profanity in a clean kitchen.",
)

unread_emails = ChaosEnemy(
    id="unread_emails", name="The Unread Emails",
    tier=3, element="clockwork",
    poise=11, clean_power=5, speed=4,
    ability_id="basic_attack",
    ability_name="Backlog",
    ability_text="Deal 5 damage. There are always more.",
    flavor="They have been waiting. They are still waiting.",
)

laundry_hydra = ChaosEnemy(
    id="laundry_hydra", name="Laundry Hydra",
    tier=3, element="shadow",
    poise=18, clean_power=5, speed=4,
    ability_id="summon_sock_on_hit",
    ability_name="Tangle",
    ability_text="When damaged but not defeated, summons a Sock Gremlin.",
    flavor="Cut off one sleeve. Two grow back. Three of them are damp.",
)

mold_king = ChaosEnemy(
    id="mold_king", name="Mold King Maximus",
    tier=3, element="garden",
    poise=22, clean_power=7, speed=3,
    ability_id="basic_attack",
    ability_name="Royal Mildew",
    ability_text="Deal 7 damage with smug entitlement.",
    flavor="He sees himself as a connoisseur. Of damp.",
)


ALL: tuple[ChaosEnemy, ...] = (
    dust_goblin, sock_gremlin, drama_spill,
    mold_mimic, snack_gremlin, infinite_dishes, possessed_kettle,
    unread_emails, laundry_hydra, mold_king,
)
assert len(ALL) == 10, f"expected 10 chaos enemies, got {len(ALL)}"

BY_ID: dict[str, ChaosEnemy] = {c.id: c for c in ALL}
BY_TIER: dict[int, list[ChaosEnemy]] = {}
for _c in ALL:
    BY_TIER.setdefault(_c.tier, []).append(_c)
