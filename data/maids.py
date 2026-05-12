"""Maid card definitions.

20 maids across 8 elements and 6 rarities. The 6 named maids from the
design doc (Mina, Bria, Mimi, Vexa, Luna, Aurelia) are included verbatim
with their canonical abilities; 14 more fill out the roster.

Stats budget by rarity (CP+P+C+S):
    Common     ~18  |  Uncommon  ~22  |  Rare      ~26
    Epic       ~28  |  Legendary ~32  |  Mythic    ~38

The `ability_id` is the lookup key in engine/abilities.py.
`ability_name` and `ability_text` are cosmetic, shown on the card embed.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Maid:
    id: str
    name: str
    rarity: str         # rarity.id
    element: str        # element.id
    role: str           # free-text label
    clean_power: int    # damage
    poise: int          # HP / defense
    charm: int          # buff strength / utility
    speed: int          # turn order
    ability_id: str
    ability_name: str
    ability_text: str
    flavor: str = ""


# ── Common (6) ──────────────────────────────────────────────────────────────

mina = Maid(
    id="mina", name="Mina, Starter Maid",
    rarity="common", element="light", role="Balanced",
    clean_power=3, poise=6, charm=4, speed=5,
    ability_id="fresh_start",
    ability_name="Fresh Start",
    ability_text="Heal herself for 2 Poise.",
    flavor="Her apron is suspiciously stain-resistant.",
)

dusty = Maid(
    id="dusty", name="Dusty, Apprentice Tinker",
    rarity="common", element="clockwork", role="Utility",
    clean_power=3, poise=5, charm=5, speed=5,
    ability_id="buff_self_speed_1",
    ability_name="Spring-Loaded",
    ability_text="Gains +1 Speed for the rest of the battle.",
    flavor="Built entirely from forgotten cuckoo clocks.",
)

pip = Maid(
    id="pip", name="Pip, Frostling",
    rarity="common", element="frost", role="Skirmisher",
    clean_power=4, poise=4, charm=3, speed=7,
    ability_id="slow_enemy_speed_2",
    ability_name="Cold Shoulder",
    ability_text="Reduce one enemy's Speed by 2 for 2 turns.",
    flavor="Carries a feather duster forged from icicles.",
)

wren = Maid(
    id="wren", name="Wren, Garden Helper",
    rarity="common", element="garden", role="Healer",
    clean_power=2, poise=7, charm=5, speed=4,
    ability_id="heal_ally_2",
    ability_name="Sprouting Care",
    ability_text="Heal one ally for 2 Poise.",
    flavor="Talks to the houseplants. They talk back.",
)

em = Maid(
    id="em", name="Em, Moonlit Sweep",
    rarity="common", element="moon", role="Debuffer",
    clean_power=3, poise=5, charm=6, speed=4,
    ability_id="debuff_enemy_cp_1",
    ability_name="Hush Hush",
    ability_text="Reduce one enemy's Clean Power by 1 for 2 turns.",
    flavor="Cleans by moonlight. Strictly.",
)

tabby = Maid(
    id="tabby", name="Tabby, Hearthside Maid",
    rarity="common", element="fire", role="Attacker",
    clean_power=5, poise=4, charm=3, speed=5,
    ability_id="attack_bonus_1",
    ability_name="Quick Singe",
    ability_text="Deal 3 damage to one enemy.",
    flavor="Smells faintly of woodsmoke and tea biscuits.",
)


# ── Uncommon (5) ────────────────────────────────────────────────────────────

sage = Maid(
    id="sage", name="Sage, Herb Witch",
    rarity="uncommon", element="garden", role="Support",
    clean_power=3, poise=7, charm=7, speed=5,
    ability_id="heal_all_2",
    ability_name="Sage Advice",
    ability_text="Heal all allies for 2 Poise.",
    flavor="Her cupboard contains more rosemary than is legal.",
)

yuki = Maid(
    id="yuki", name="Yuki, Snowfall Maid",
    rarity="uncommon", element="frost", role="Controller",
    clean_power=4, poise=6, charm=6, speed=6,
    ability_id="freeze_enemy_skip_turn",
    ability_name="Drifting Hush",
    ability_text="One enemy is frozen and skips their next turn.",
    flavor="Snowflakes follow her like loyal pets.",
)

bram = Maid(
    id="bram", name="Bram, Kitchen Brawler",
    rarity="uncommon", element="fire", role="Attacker",
    clean_power=6, poise=6, charm=4, speed=6,
    ability_id="attack_4",
    ability_name="Skillet Swing",
    ability_text="Deal 4 damage with a cast-iron pan.",
    flavor="Yes, the pan is the ability. He just hits things.",
)

sera = Maid(
    id="sera", name="Sera, Lamplighter",
    rarity="uncommon", element="light", role="Cleanser",
    clean_power=4, poise=7, charm=6, speed=5,
    ability_id="cleanse_ally",
    ability_name="Steady Flame",
    ability_text="Remove one negative effect from an ally and heal 1.",
    flavor="Carries an oil lamp that never runs out.",
)

cog = Maid(
    id="cog", name="Cog, Cogsworth Junior",
    rarity="uncommon", element="clockwork", role="Combo",
    clean_power=5, poise=6, charm=5, speed=6,
    ability_id="bonus_action_to_ally",
    ability_name="Wind-Up",
    ability_text="Give one ally an extra basic attack this turn.",
    flavor="His pockets click softly when he walks.",
)


# ── Rare (3) ────────────────────────────────────────────────────────────────

bria = Maid(
    id="bria", name="Bria, Broomblade Captain",
    rarity="rare", element="fire", role="Attacker",
    clean_power=8, poise=7, charm=4, speed=7,
    ability_id="sweep_strike",
    ability_name="Sweep Strike",
    ability_text="Deal 5 damage. If this defeats an enemy, attack again for 2.",
    flavor="Her broom has its own footnotes in the rulebook.",
)

stella = Maid(
    id="stella", name="Stella, Royal Page",
    rarity="rare", element="royal", role="Buffer",
    clean_power=5, poise=8, charm=7, speed=6,
    ability_id="buff_ally_cp_2",
    ability_name="Crown Polish",
    ability_text="Give one ally +2 Clean Power for 2 turns.",
    flavor="Curtsies before delivering devastating news.",
)

drosera = Maid(
    id="drosera", name="Drosera, Thornkeeper",
    rarity="rare", element="garden", role="Bruiser",
    clean_power=6, poise=9, charm=5, speed=5,
    ability_id="thorns_self",
    ability_name="Bramble Shroud",
    ability_text="Until your next turn, attackers take 2 damage.",
    flavor="She insists the thorns are decorative.",
)


# ── Epic (3) ────────────────────────────────────────────────────────────────

luna = Maid(
    id="luna", name="Luna, the Moonlit Maid",
    rarity="epic", element="moon", role="Support",
    clean_power=4, poise=7, charm=9, speed=6,
    ability_id="silver_polish",
    ability_name="Silver Polish",
    ability_text="Heal one ally for 4 Poise and give +2 Charm for 1 turn.",
    flavor="The dust does not vanish. It simply respects her boundaries.",
)

mimi = Maid(
    id="mimi", name="Mimi, Tea Witch",
    rarity="epic", element="garden", role="Poison Support",
    clean_power=4, poise=7, charm=9, speed=6,
    ability_id="tea_heal_poison",
    ability_name="Suspiciously Perfect Tea",
    ability_text="Heal one ally for 3 and poison one enemy for 2 turns.",
    flavor="Nobody can prove anything. Nobody.",
)

indra = Maid(
    id="indra", name="Indra, Mainspring Engineer",
    rarity="epic", element="clockwork", role="Combo",
    clean_power=6, poise=7, charm=8, speed=7,
    ability_id="all_allies_plus_speed_2",
    ability_name="Synchronize",
    ability_text="All allies gain +2 Speed for 2 turns.",
    flavor="She thinks of the team as one large, polite machine.",
)


# ── Legendary (2) ───────────────────────────────────────────────────────────

vexa = Maid(
    id="vexa", name="Vexa, Shadow Butler-Maid",
    rarity="legendary", element="shadow", role="Assassin",
    clean_power=9, poise=7, charm=7, speed=9,
    ability_id="borrowed_silverware",
    ability_name="Borrowed Silverware",
    ability_text="Steal 2 Clean Power from an enemy for 2 turns.",
    flavor="If you cannot find it, she did not take it. Probably.",
)

solene = Maid(
    id="solene", name="Solene, Dawnward",
    rarity="legendary", element="light", role="Guardian",
    clean_power=7, poise=11, charm=8, speed=6,
    ability_id="shield_all_3",
    ability_name="Morning Aegis",
    ability_text="Grant all allies a 3-Poise shield until your next turn.",
    flavor="Has not been late in seventeen consecutive sunrises.",
)


# ── Mythic (1) ──────────────────────────────────────────────────────────────

aurelia = Maid(
    id="aurelia", name="Aurelia, Head Maid of the Golden Hall",
    rarity="mythic", element="royal", role="Leader",
    clean_power=8, poise=12, charm=10, speed=8,
    ability_id="order_restored",
    ability_name="Order Restored",
    ability_text="All allies gain +2 Clean Power, +2 Poise, and cleanse one effect.",
    flavor="The chaos is not banished. It has merely been corrected.",
)


# ── Registry ────────────────────────────────────────────────────────────────

ALL: tuple[Maid, ...] = (
    mina, dusty, pip, wren, em, tabby,
    sage, yuki, bram, sera, cog,
    bria, stella, drosera,
    luna, mimi, indra,
    vexa, solene,
    aurelia,
)
assert len(ALL) == 20, f"expected 20 maids, got {len(ALL)}"

BY_ID: dict[str, Maid] = {m.id: m for m in ALL}
BY_RARITY: dict[str, list[Maid]] = {}
for _m in ALL:
    BY_RARITY.setdefault(_m.rarity, []).append(_m)
