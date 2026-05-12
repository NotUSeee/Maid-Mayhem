"""Tool card definitions.

10 tools, equipped one-per-maid in a deck. The named tools from the
design doc (Golden Feather Duster, Cursed Mop, Tea Tray of Diplomacy)
ship verbatim; 7 more fill out the slate.

Effects on a Maid are stat bonuses (cp / poise / charm / speed) applied
at battle start, plus an optional `passive_id` for tools whose flavor
goes beyond flat numbers (handled by engine/abilities.py later).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Tool:
    id: str
    name: str
    rarity: str
    cp_bonus: int = 0
    poise_bonus: int = 0
    charm_bonus: int = 0
    speed_bonus: int = 0
    passive_id: str = ""   # optional fancy effect — empty = pure stat tool
    description: str = ""
    flavor: str = ""


golden_feather_duster = Tool(
    id="golden_feather_duster", name="Golden Feather Duster",
    rarity="rare",
    cp_bonus=3, speed_bonus=1,
    description="+3 Clean Power. +1 Speed if equipped to a Light or Royal maid.",
    flavor="Shimmers self-importantly between battles.",
)

cursed_mop = Tool(
    id="cursed_mop", name="Cursed Mop",
    rarity="uncommon",
    cp_bonus=5,
    passive_id="drain_1_per_turn",
    description="+5 Clean Power. Wielder loses 1 Poise each turn.",
    flavor="It whispers cleaning tips. Mostly threats.",
)

tea_tray_of_diplomacy = Tool(
    id="tea_tray_of_diplomacy", name="Tea Tray of Diplomacy",
    rarity="epic",
    poise_bonus=2,
    passive_id="block_next_debuff",
    description="+2 Poise. Prevents the next negative effect targeting this maid.",
    flavor="Loaded with biscuits of unimpeachable etiquette.",
)

spare_broom = Tool(
    id="spare_broom", name="Spare Broom",
    rarity="common",
    cp_bonus=1,
    description="+1 Clean Power. Nothing fancy.",
    flavor="The handle has bite marks. Don't ask.",
)

lavender_sachet = Tool(
    id="lavender_sachet", name="Lavender Sachet",
    rarity="common",
    charm_bonus=2,
    description="+2 Charm.",
    flavor="The smell calms even cursed laundry. Briefly.",
)

silver_polish_rag = Tool(
    id="silver_polish_rag", name="Silver Polish Rag",
    rarity="uncommon",
    cp_bonus=2, charm_bonus=1,
    description="+2 Clean Power, +1 Charm.",
    flavor="Glints with the optimism of a thousand fingerprints.",
)

clockwork_dustpan = Tool(
    id="clockwork_dustpan", name="Clockwork Dustpan",
    rarity="rare",
    poise_bonus=2, speed_bonus=2,
    description="+2 Poise, +2 Speed.",
    flavor="Empties itself at exactly 3:42pm. Always.",
)

bonded_apron = Tool(
    id="bonded_apron", name="Bonded Apron of Service",
    rarity="rare",
    poise_bonus=4,
    description="+4 Poise.",
    flavor="Reinforced with the stubbornness of seven generations.",
)

heart_of_the_manor = Tool(
    id="heart_of_the_manor", name="Heart of the Manor",
    rarity="legendary",
    cp_bonus=2, poise_bonus=3, charm_bonus=3, speed_bonus=2,
    description="+2 CP, +3 Poise, +3 Charm, +2 Speed.",
    flavor="A small amulet. Faintly hums with the bricks' approval.",
)

eternal_kettle = Tool(
    id="eternal_kettle", name="Eternal Kettle",
    rarity="epic",
    poise_bonus=3, charm_bonus=2,
    passive_id="heal_self_1_per_turn",
    description="+3 Poise, +2 Charm. Heal 1 Poise at the start of each turn.",
    flavor="Has never been empty. Has never been clean.",
)


ALL: tuple[Tool, ...] = (
    spare_broom, lavender_sachet,
    cursed_mop, silver_polish_rag,
    golden_feather_duster, clockwork_dustpan, bonded_apron,
    tea_tray_of_diplomacy, eternal_kettle,
    heart_of_the_manor,
)
assert len(ALL) == 10, f"expected 10 tools, got {len(ALL)}"

BY_ID: dict[str, Tool] = {t.id: t for t in ALL}
BY_RARITY: dict[str, list[Tool]] = {}
for _t in ALL:
    BY_RARITY.setdefault(_t.rarity, []).append(_t)
