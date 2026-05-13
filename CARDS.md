# Maid & Mayhem — Card Spec

Complete card reference for artwork. Every entry includes the in-game
name, rarity (with hex color for frame design), element, stats, the
**actual** ability mechanic (synced with `engine/abilities.py`), and
flavor text.

There are **40 cards total**: 20 maids, 10 tools, 10 chaos enemies.
Plus 3 raid bosses (server-shared, not collectible).

---

## Rarity reference

| Tier | Color | Hex | Drop % | Border emoji |
|---|---|---|---|---|
| Common | grey | `#9CA3AF` | 55.0% | ⬜ |
| Uncommon | green | `#22C55E` | 25.0% | 🟩 |
| Rare | blue | `#3B82F6` | 12.0% | 🟦 |
| Epic | purple | `#A855F7` | 6.0% | 🟪 |
| Legendary | gold | `#F59E0B` | 1.8% | 🟧 |
| Mythic | red | `#EF4444` | 0.2% | ❤️‍🔥 |

## Element reference (combat triangle)

Each beats the next; e.g. Fire deals **1.5×** vs Frost, **0.75×** vs Clockwork, **1.0×** vs Fire.

```
Fire → Frost → Garden → Shadow → Light → Moon → Royal → Clockwork → (loop)
```

| Element | Icon | Hex |
|---|---|---|
| Light | 🕯 | `#FEF3C7` |
| Moon | 🌙 | `#6366F1` |
| Fire | 🔥 | `#EF4444` |
| Frost | ❄️ | `#60A5FA` |
| Garden | 🌿 | `#16A34A` |
| Clockwork | ⚙️ | `#B45309` |
| Royal | 👑 | `#CA8A04` |
| Shadow | 🕸 | `#4B5563` |

## Stat glossary

| Stat | Glyph | What it does |
|---|---|---|
| Clean Power | 🧹 | Outgoing damage on basic attacks |
| Poise | 🛡 | Max HP — when this hits 0 the maid is KO'd |
| Charm | ✨ | Buff strength / utility scaling (mostly cosmetic in v1) |
| Speed | ⚡ | Total team Speed decides who acts first in PvP |

Cards level **1 → 50** in-game. At level 50, a maid gains **+9 Max Poise** and **+4 Clean Power** above their base.

---

# Maids (20)

## Common — 6 cards

### Mina, Starter Maid
- **Rarity:** Common · **Element:** Light 🕯 · **Role:** Balanced
- **Stats:** CP 3 · Poise 6 · Charm 4 · Speed 5
- **Ability — Fresh Start** *(cooldown 2)* — Heal yourself for 3.
- **Flavor:** "Her apron is suspiciously stain-resistant."

### Dusty, Apprentice Tinker
- **Rarity:** Common · **Element:** Clockwork ⚙️ · **Role:** Utility
- **Stats:** CP 3 · Poise 5 · Charm 5 · Speed 5
- **Ability — Spring-Loaded** *(cooldown 3)* — Permanently gain +2 Speed this battle.
- **Flavor:** "Built entirely from forgotten cuckoo clocks."

### Pip, Frostling
- **Rarity:** Common · **Element:** Frost ❄️ · **Role:** Skirmisher
- **Stats:** CP 4 · Poise 4 · Charm 3 · Speed 7
- **Ability — Cold Shoulder** *(cooldown 2)* — Reduce an enemy's Clean Power by 2 for 2 turns.
- **Flavor:** "Carries a feather duster forged from icicles."

### Wren, Garden Helper
- **Rarity:** Common · **Element:** Garden 🌿 · **Role:** Healer
- **Stats:** CP 2 · Poise 7 · Charm 5 · Speed 4
- **Ability — Sprouting Care** *(cooldown 2)* — Heal an ally for 4.
- **Flavor:** "Talks to the houseplants. They talk back."

### Em, Moonlit Sweep
- **Rarity:** Common · **Element:** Moon 🌙 · **Role:** Debuffer
- **Stats:** CP 3 · Poise 5 · Charm 6 · Speed 4
- **Ability — Hush Hush** *(cooldown 2)* — Reduce an enemy's Clean Power by 2 for 2 turns.
- **Flavor:** "Cleans by moonlight. Strictly."

### Tabby, Hearthside Maid
- **Rarity:** Common · **Element:** Fire 🔥 · **Role:** Attacker
- **Stats:** CP 5 · Poise 4 · Charm 3 · Speed 5
- **Ability — Quick Singe** *(cooldown 2)* — Deal 5 damage to the weakest enemy.
- **Flavor:** "Smells faintly of woodsmoke and tea biscuits."

## Uncommon — 5 cards

### Sage, Herb Witch
- **Rarity:** Uncommon · **Element:** Garden 🌿 · **Role:** Support
- **Stats:** CP 3 · Poise 7 · Charm 7 · Speed 5
- **Ability — Sage Advice** *(cooldown 3)* — Heal all allies for 3.
- **Flavor:** "Her cupboard contains more rosemary than is legal."

### Yuki, Snowfall Maid
- **Rarity:** Uncommon · **Element:** Frost ❄️ · **Role:** Controller
- **Stats:** CP 4 · Poise 6 · Charm 6 · Speed 6
- **Ability — Drifting Hush** *(cooldown 3)* — Freeze an enemy for 1 turn (they skip their next attack).
- **Flavor:** "Snowflakes follow her like loyal pets."

### Bram, Kitchen Brawler
- **Rarity:** Uncommon · **Element:** Fire 🔥 · **Role:** Attacker
- **Stats:** CP 6 · Poise 6 · Charm 4 · Speed 6
- **Ability — Skillet Swing** *(cooldown 2)* — Deal 7 damage to the weakest enemy.
- **Flavor:** "Yes, the pan is the ability. He just hits things."

### Sera, Lamplighter
- **Rarity:** Uncommon · **Element:** Light 🕯 · **Role:** Cleanser
- **Stats:** CP 4 · Poise 7 · Charm 6 · Speed 5
- **Ability — Steady Flame** *(cooldown 2)* — Heal an ally for 4 and cleanse their afflictions.
- **Flavor:** "Carries an oil lamp that never runs out."

### Cog, Cogsworth Junior
- **Rarity:** Uncommon · **Element:** Clockwork ⚙️ · **Role:** Combo
- **Stats:** CP 5 · Poise 6 · Charm 5 · Speed 6
- **Ability — Wind-Up** *(cooldown 3)* — Hit twice for 4 damage each.
- **Flavor:** "His pockets click softly when he walks."

## Rare — 3 cards

### Bria, Broomblade Captain
- **Rarity:** Rare · **Element:** Fire 🔥 · **Role:** Attacker
- **Stats:** CP 8 · Poise 7 · Charm 4 · Speed 7
- **Ability — Sweep Strike** *(cooldown 3)* — Deal 7 damage; if it kills, deal 4 to the next enemy.
- **Flavor:** "Her broom has its own footnotes in the rulebook."

### Stella, Royal Page
- **Rarity:** Rare · **Element:** Royal 👑 · **Role:** Buffer
- **Stats:** CP 5 · Poise 8 · Charm 7 · Speed 6
- **Ability — Crown Polish** *(cooldown 2)* — Give an ally +2 Clean Power for 2 turns.
- **Flavor:** "Curtsies before delivering devastating news."

### Drosera, Thornkeeper
- **Rarity:** Rare · **Element:** Garden 🌿 · **Role:** Bruiser
- **Stats:** CP 6 · Poise 9 · Charm 5 · Speed 5
- **Ability — Bramble Shroud** *(cooldown 2)* — Gain a 4-Poise shield.
- **Flavor:** "She insists the thorns are decorative."

## Epic — 3 cards

### Luna, the Moonlit Maid
- **Rarity:** Epic · **Element:** Moon 🌙 · **Role:** Support
- **Stats:** CP 4 · Poise 7 · Charm 9 · Speed 6
- **Ability — Silver Polish** *(cooldown 3)* — Heal an ally for 6.
- **Flavor:** "The dust does not vanish. It simply respects her boundaries."

### Mimi, Tea Witch
- **Rarity:** Epic · **Element:** Garden 🌿 · **Role:** Poison Support
- **Stats:** CP 4 · Poise 7 · Charm 9 · Speed 6
- **Ability — Perfect Tea** *(cooldown 3)* — Heal an ally for 3 and poison an enemy (2 damage/turn × 3 turns).
- **Flavor:** "Nobody can prove anything. Nobody."

### Indra, Mainspring Engineer
- **Rarity:** Epic · **Element:** Clockwork ⚙️ · **Role:** Combo
- **Stats:** CP 6 · Poise 7 · Charm 8 · Speed 7
- **Ability — Synchronize** *(cooldown 3)* — Heal all allies for 2.
- **Flavor:** "She thinks of the team as one large, polite machine."

## Legendary — 2 cards

### Vexa, Shadow Butler-Maid
- **Rarity:** Legendary · **Element:** Shadow 🕸 · **Role:** Assassin
- **Stats:** CP 9 · Poise 7 · Charm 7 · Speed 9
- **Ability — Borrowed Silverware** *(cooldown 3)* — Deal 5 damage and steal 2 Clean Power from an enemy for 2 turns.
- **Flavor:** "If you cannot find it, she did not take it. Probably."

### Solene, Dawnward
- **Rarity:** Legendary · **Element:** Light 🕯 · **Role:** Guardian
- **Stats:** CP 7 · Poise 11 · Charm 8 · Speed 6
- **Ability — Morning Aegis** *(cooldown 3)* — Grant all allies a 4-Poise shield.
- **Flavor:** "Has not been late in seventeen consecutive sunrises."

## Mythic — 1 card

### Aurelia, Head Maid of the Golden Hall
- **Rarity:** Mythic · **Element:** Royal 👑 · **Role:** Leader
- **Stats:** CP 8 · Poise 12 · Charm 10 · Speed 8
- **Ability — Order Restored** *(cooldown 3)* — Heal all allies for 5 and cleanse the whole team of debuffs.
- **Flavor:** "The chaos is not banished. It has merely been corrected."

---

# Tools (10)

Tools equip to maids in their matching deck slot. The bonuses below stack on top of the maid's base stats. A few tools also carry a `passive_id` flag for future status hooks (unused in v1; the bonuses above are what actually fire).

## Common — 2 tools

### Spare Broom
- **Rarity:** Common
- **Bonuses:** +1 Clean Power
- **Effect text:** "+1 Clean Power. Nothing fancy."
- **Flavor:** "The handle has bite marks. Don't ask."

### Lavender Sachet
- **Rarity:** Common
- **Bonuses:** +2 Charm
- **Effect text:** "+2 Charm."
- **Flavor:** "The smell calms even cursed laundry. Briefly."

## Uncommon — 2 tools

### Cursed Mop
- **Rarity:** Uncommon
- **Bonuses:** +5 Clean Power
- **Effect text:** "+5 Clean Power. Wielder loses 1 Poise each turn." *(passive `drain_1_per_turn` — reserved for v1.1)*
- **Flavor:** "It whispers cleaning tips. Mostly threats."

### Silver Polish Rag
- **Rarity:** Uncommon
- **Bonuses:** +2 Clean Power, +1 Charm
- **Effect text:** "+2 Clean Power, +1 Charm."
- **Flavor:** "Glints with the optimism of a thousand fingerprints."

## Rare — 3 tools

### Golden Feather Duster
- **Rarity:** Rare
- **Bonuses:** +3 Clean Power, +1 Speed
- **Effect text:** "+3 Clean Power. +1 Speed if equipped to a Light or Royal maid."
- **Flavor:** "Shimmers self-importantly between battles."

### Clockwork Dustpan
- **Rarity:** Rare
- **Bonuses:** +2 Poise, +2 Speed
- **Effect text:** "+2 Poise, +2 Speed."
- **Flavor:** "Empties itself at exactly 3:42pm. Always."

### Bonded Apron of Service
- **Rarity:** Rare
- **Bonuses:** +4 Poise
- **Effect text:** "+4 Poise."
- **Flavor:** "Reinforced with the stubbornness of seven generations."

## Epic — 2 tools

### Tea Tray of Diplomacy
- **Rarity:** Epic
- **Bonuses:** +2 Poise
- **Effect text:** "+2 Poise. Prevents the next negative effect targeting this maid." *(passive `block_next_debuff` — reserved for v1.1)*
- **Flavor:** "Loaded with biscuits of unimpeachable etiquette."

### Eternal Kettle
- **Rarity:** Epic
- **Bonuses:** +3 Poise, +2 Charm
- **Effect text:** "+3 Poise, +2 Charm. Heal 1 Poise at the start of each turn." *(passive `heal_self_1_per_turn` — reserved for v1.1)*
- **Flavor:** "Has never been empty. Has never been clean."

## Legendary — 1 tool

### Heart of the Manor
- **Rarity:** Legendary
- **Bonuses:** +2 CP, +3 Poise, +3 Charm, +2 Speed
- **Effect text:** "+2 CP, +3 Poise, +3 Charm, +2 Speed."
- **Flavor:** "A small amulet. Faintly hums with the bricks' approval."

---

# Chaos Enemies (10)

These spawn during PvE battles, scaled by tier. Tier 1 is starter chaos, tier 3 is mid-game; raid bosses live in their own file.

## Tier 1 — 3 enemies

### Dust Goblin
- **Element:** Shadow 🕸 · **Poise:** 6 · **CP:** 3 · **Speed:** 5
- **Ability — Bite:** Deal 3 damage.
- **Flavor:** "Made of lint and bad attitude."

### Sock Gremlin
- **Element:** Shadow 🕸 · **Poise:** 4 · **CP:** 4 · **Speed:** 7
- **Ability — Snatch:** Deal 4 damage and skitter away (high speed).
- **Flavor:** "Has stolen exactly one of every pair you own."

### Drama Spill
- **Element:** Moon 🌙 · **Poise:** 5 · **CP:** 2 · **Speed:** 4
- **Ability — Awkward Silence:** All player maids lose 1 Charm for 1 turn.
- **Flavor:** "It just sits there. Judging."

## Tier 2 — 4 enemies

### Mold Mimic
- **Element:** Garden 🌿 · **Poise:** 10 · **CP:** 4 · **Speed:** 3
- **Ability — Slop:** Deal 4 damage.
- **Flavor:** "Looks like a teapot. Is not a teapot."

### Snack Gremlin
- **Element:** Fire 🔥 · **Poise:** 8 · **CP:** 5 · **Speed:** 6
- **Ability — Crumb Storm:** Deal 5 damage in a shower of crumbs.
- **Flavor:** "Lives in the couch. Mostly."

### Infinite Dishes
- **Element:** Frost ❄️ · **Poise:** 12 · **CP:** 3 · **Speed:** 2
- **Ability — Clatter:** All player maids lose 1 Speed at end of turn.
- **Flavor:** "There were six. Now there are twenty-six. There were six."

### Possessed Kettle
- **Element:** Fire 🔥 · **Poise:** 9 · **CP:** 6 · **Speed:** 5
- **Ability — Boilover:** Deal 6 damage.
- **Flavor:** "Steam is profanity in a clean kitchen."

## Tier 3 — 3 enemies

### The Unread Emails
- **Element:** Clockwork ⚙️ · **Poise:** 11 · **CP:** 5 · **Speed:** 4
- **Ability — Backlog:** Deal 5 damage. There are always more.
- **Flavor:** "They have been waiting. They are still waiting."

### Laundry Hydra
- **Element:** Shadow 🕸 · **Poise:** 18 · **CP:** 5 · **Speed:** 4
- **Ability — Tangle:** When damaged but not defeated, summons a Sock Gremlin.
- **Flavor:** "Cut off one sleeve. Two grow back. Three of them are damp."

### Mold King Maximus
- **Element:** Garden 🌿 · **Poise:** 22 · **CP:** 7 · **Speed:** 3
- **Ability — Royal Mildew:** Deal 7 damage with smug entitlement.
- **Flavor:** "He sees himself as a connoisseur. Of damp."

---

# Raid Bosses (3)

Server-wide chaos events; everyone in the server attacks the same boss. These are **not** collectible cards — they're event banners.

### The Great Unwashed One
- **Tier:** 1 · **Element:** Shadow 🕸 · **HP:** 1,500
- **Flavor:** "A mountain of laundry possessed by ancient laziness."

### Laundry Hydra Prime
- **Tier:** 2 · **Element:** Shadow 🕸 · **HP:** 4,000
- **Flavor:** "Three sleeves. Six socks. None of them match."

### Mold King Maximus
- **Tier:** 3 · **Element:** Garden 🌿 · **HP:** 8,000
- **Flavor:** "He sees himself as a connoisseur. Of damp."

---

## Quick visual-design notes

- **Card border:** color from the rarity hex above.
- **Element badge:** small icon in a top corner using the element emoji + hex.
- **Stat block:** four icons (🧹 CP, 🛡 Poise, ✨ Charm, ⚡ Speed) on maids; three (🛡 Poise, 🧹 CP, ⚡ Speed) on chaos.
- **Ability text:** the in-game canonical version is what's listed under each card here (some differ slightly from `data/maids.py`'s `ability_text` — Phase 6 status-effect rewire). When in doubt, use what's in this file.
- **Flavor:** italicized at the bottom of the card.
- **Tool art:** no element badge (tools are element-neutral). The bonus block replaces the stat block.
