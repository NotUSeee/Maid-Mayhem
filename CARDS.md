# Maid & Mayhem — Card Spec

Complete card reference for artwork. Every entry includes the in-game
name, rarity (with hex color for frame design), element, stats, the
**actual** ability mechanic (synced with `engine/abilities.py`), and
flavor text.

There are **40 cards total**: 20 maids, 10 tools, 10 chaos enemies.
Plus 3 raid bosses (server-shared, not collectible).

---

## Style guide for artwork

Anime-influenced semi-realistic illustration. Clean cel-shaded linework, soft painted gradients, vertical card-art composition. Subject centered with the background fading to a soft glow in their element's color. Maid uniforms are variations on the classic black-and-white frilly base with element-themed accents and trim. Mood is cute, competitive, and a little ridiculous — confident expressions, not blank or generic. Lighting matches the element (warm flame for Fire, cool moonlight for Moon, etc.). When prompting an AI generator, prepend this paragraph to each card's `visual` field.

Machine-readable mirror of every card spec (including the same visual prompts) lives in [`CARDS.json`](CARDS.json) — feed entries straight into a procedural card-art pipeline.

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
- **Visual:** A cheerful young maid with shoulder-length blonde hair and warm brown eyes. Crisp white apron over a soft-cream dress with subtle gold trim. Holds a plain wooden broom resting over one shoulder. Slightly nervous-but-eager smile, round friendly face. Warm sunlit background with faint candle motifs and dust motes catching the light.

### Dusty, Apprentice Tinker
- **Rarity:** Common · **Element:** Clockwork ⚙️ · **Role:** Utility
- **Stats:** CP 3 · Poise 5 · Charm 5 · Speed 5
- **Ability — Spring-Loaded** *(cooldown 3)* — Permanently gain +2 Speed this battle.
- **Flavor:** "Built entirely from forgotten cuckoo clocks."
- **Visual:** A wiry brown-haired maid with messy braids, brass-rimmed goggles pushed up on her forehead, and a small oil smudge on one cheek. Brass-and-leather apron over a grey workshop dress. Pockets bristling with tiny screwdrivers, wind-up keys at her belt. Mid-action with a tool in hand. Workshop-amber background with floating cogs and tiny brass mechanisms.

### Pip, Frostling
- **Rarity:** Common · **Element:** Frost ❄️ · **Role:** Skirmisher
- **Stats:** CP 4 · Poise 4 · Charm 3 · Speed 7
- **Ability — Cold Shoulder** *(cooldown 2)* — Reduce an enemy's Clean Power by 2 for 2 turns.
- **Flavor:** "Carries a feather duster forged from icicles."
- **Visual:** A petite, fast-looking maid with pale-blue pixie-cut hair and brilliant cyan eyes. Navy-and-ice-white frilled uniform with crystal-shard buttons. Holds an oversized feather duster whose fibers are actual glittering icicles. A small puff of cold breath drifts from her smirking mouth. Pale-blue background with drifting snow and faint frost-rune patterns.

### Wren, Garden Helper
- **Rarity:** Common · **Element:** Garden 🌿 · **Role:** Healer
- **Stats:** CP 2 · Poise 7 · Charm 5 · Speed 4
- **Ability — Sprouting Care** *(cooldown 2)* — Heal an ally for 4.
- **Flavor:** "Talks to the houseplants. They talk back."
- **Visual:** A soft-eyed maid with leaf-green hair tied in two short braids, tiny sprouts growing from the braids. Moss-green dress with a cream apron criss-crossed with delicate vines. Cradles a small potted plant in one arm; holds a copper watering can in the other. Gentle, focused expression as if mid-conversation with the plant. Sunlit greenhouse background with ferns and hanging flowers.

### Em, Moonlit Sweep
- **Rarity:** Common · **Element:** Moon 🌙 · **Role:** Debuffer
- **Stats:** CP 3 · Poise 5 · Charm 6 · Speed 4
- **Ability — Hush Hush** *(cooldown 2)* — Reduce an enemy's Clean Power by 2 for 2 turns.
- **Flavor:** "Cleans by moonlight. Strictly."
- **Visual:** A quiet, watchful maid with long straight violet hair half-covering one eye. Crescent-moon silver earrings. Dark indigo dress with silver thread trim and a moon-pattern apron. Holds an old wooden broom upright. Faintly luminous pale eyes. Deep midnight-blue background with stars and a thin crescent moon.

### Tabby, Hearthside Maid
- **Rarity:** Common · **Element:** Fire 🔥 · **Role:** Attacker
- **Stats:** CP 5 · Poise 4 · Charm 3 · Speed 5
- **Ability — Quick Singe** *(cooldown 2)* — Deal 5 damage to the weakest enemy.
- **Flavor:** "Smells faintly of woodsmoke and tea biscuits."
- **Visual:** A scrappy auburn-haired maid with bright green eyes and a constellation of freckles, hair pulled into a messy side-ponytail. Copper-and-red apron over a white shirt; the apron's edges are singed brown. A soot smudge on her nose. Wields a long iron fireplace poker like a sword in a ready stance. Confident smirk. Hearthfire-orange glow behind her with leaping flames.

## Uncommon — 5 cards

### Sage, Herb Witch
- **Rarity:** Uncommon · **Element:** Garden 🌿 · **Role:** Support
- **Stats:** CP 3 · Poise 7 · Charm 7 · Speed 5
- **Ability — Sage Advice** *(cooldown 3)* — Heal all allies for 3.
- **Flavor:** "Her cupboard contains more rosemary than is legal."
- **Visual:** An olive-skinned maid with dark green hair in a long loose braid, gold-rimmed wireframe glasses. Deep forest-green dress, apron lined with pinned sprigs of rosemary, lavender, and dried sage. Holds a wooden mortar and pestle, mid-grind. Calm, slightly conspiratorial smile. Background: warm-lit apothecary kitchen, hanging bunches of herbs and copper pots.

### Yuki, Snowfall Maid
- **Rarity:** Uncommon · **Element:** Frost ❄️ · **Role:** Controller
- **Stats:** CP 4 · Poise 6 · Charm 6 · Speed 6
- **Ability — Drifting Hush** *(cooldown 3)* — Freeze an enemy for 1 turn (they skip their next attack).
- **Flavor:** "Snowflakes follow her like loyal pets."
- **Visual:** A tall maid with very long flowing white hair, pale skin, and luminous ice-blue eyes. Deep blue dress with a delicate snowflake-pattern apron in silver-white. Six perfectly formed snowflakes orbit her outstretched palm. Serene, slightly mysterious smile. Background: a quiet blue snowstorm, soft blurred falling flakes.

### Bram, Kitchen Brawler
- **Rarity:** Uncommon · **Element:** Fire 🔥 · **Role:** Attacker
- **Stats:** CP 6 · Poise 6 · Charm 4 · Speed 6
- **Ability — Skillet Swing** *(cooldown 2)* — Deal 7 damage to the weakest enemy.
- **Flavor:** "Yes, the pan is the ability. He just hits things."
- **Visual:** A broad-shouldered male maid with cropped fiery red hair, friendly squint, soot smudges across his forearms. Black-and-red apron over a white chef's shirt with rolled-up sleeves. Wields an enormous cast-iron skillet like a war-club, mid-swing. Big toothy grin like he's enjoying the fight. Sparks and smoke trailing behind him; backdrop is a roaring kitchen stove.

### Sera, Lamplighter
- **Rarity:** Uncommon · **Element:** Light 🕯 · **Role:** Cleanser
- **Stats:** CP 4 · Poise 7 · Charm 6 · Speed 5
- **Ability — Steady Flame** *(cooldown 2)* — Heal an ally for 4 and cleanse their afflictions.
- **Flavor:** "Carries an oil lamp that never runs out."
- **Visual:** A calm gold-haired maid with hair tucked into a high bun, soft amber eyes. Honey-yellow dress with warm-white apron, brass cuff bracelets. Holds up an antique brass oil lamp; the flame inside casts a soft golden halo around her. Gentle, reassuring expression. Twilight cobblestone-street backdrop, blurred lamp-posts behind.

### Cog, Cogsworth Junior
- **Rarity:** Uncommon · **Element:** Clockwork ⚙️ · **Role:** Combo
- **Stats:** CP 5 · Poise 6 · Charm 5 · Speed 6
- **Ability — Wind-Up** *(cooldown 3)* — Hit twice for 4 damage each.
- **Flavor:** "His pockets click softly when he walks."
- **Visual:** A neat younger male maid with combed brown hair and round wire-frame glasses, polite but focused expression. Crisp brass-buttoned vest over a white shirt and dark trousers, half-apron at his waist. Holds a gold pocket watch in one hand and a small jeweler's screwdriver in the other. Faint clockwork gears float around him in slow rotation. Warm wood-panelled study backdrop.

## Rare — 3 cards

### Bria, Broomblade Captain
- **Rarity:** Rare · **Element:** Fire 🔥 · **Role:** Attacker
- **Stats:** CP 8 · Poise 7 · Charm 4 · Speed 7
- **Ability — Sweep Strike** *(cooldown 3)* — Deal 7 damage; if it kills, deal 4 to the next enemy.
- **Flavor:** "Her broom has its own footnotes in the rulebook."
- **Visual:** A tall, athletic woman with crimson hair pulled into a high disciplined ponytail, sharp gold eyes. Crimson-and-black uniform with gold sergeant's epaulets and a long swallow-tail coat over a maid-apron. Wields a long broom like a polearm, the bristled head glowing with embers. Stand-at-attention pose, slight forward lean. Battle banner and embers swirling in the deep-red background.

### Stella, Royal Page
- **Rarity:** Rare · **Element:** Royal 👑 · **Role:** Buffer
- **Stats:** CP 5 · Poise 8 · Charm 7 · Speed 6
- **Ability — Crown Polish** *(cooldown 2)* — Give an ally +2 Clean Power for 2 turns.
- **Flavor:** "Curtsies before delivering devastating news."
- **Visual:** A poised blonde-haired maid with hair styled in elegant waves, sharp blue eyes, slight knowing smile. White-and-gold dress with a small embroidered crown insignia on the apron, gold-trimmed lace cuffs. Holds a silk polishing cloth in one hand and a five-branch silver candelabra in the other, mid-curtsy. Royal hall backdrop with chandeliers and red-carpeted marble.

### Drosera, Thornkeeper
- **Rarity:** Rare · **Element:** Garden 🌿 · **Role:** Bruiser
- **Stats:** CP 6 · Poise 9 · Charm 5 · Speed 5
- **Ability — Bramble Shroud** *(cooldown 2)* — Gain a 4-Poise shield.
- **Flavor:** "She insists the thorns are decorative."
- **Visual:** A tall, watchful maid with dark green hair in a long braid woven with thorny vines, intricate vine tattoos along her bare forearms. Deep forest-green dress with brown leather harness, thorn-wrapped apron. Holds a pair of long, barbed pruning shears. Cool, unreadable expression. Background: shadowed greenhouse with carnivorous plants, dim emerald light filtering through leaves.

## Epic — 3 cards

### Luna, the Moonlit Maid
- **Rarity:** Epic · **Element:** Moon 🌙 · **Role:** Support
- **Stats:** CP 4 · Poise 7 · Charm 9 · Speed 6
- **Ability — Silver Polish** *(cooldown 3)* — Heal an ally for 6.
- **Flavor:** "The dust does not vanish. It simply respects her boundaries."
- **Visual:** An elegant, ethereal maid with long flowing silver hair and pale glowing pale-blue eyes. Deep-indigo dress with moonlight-silver trim and an apron embroidered with delicate constellations. A small crescent-moon hair ornament rests above her ear. Holds a folded polishing cloth that ripples like liquid moonlight. Slightly floating pose, hem of her dress drifting weightlessly. Starry-night background with a full moon haloing her head.

### Mimi, Tea Witch
- **Rarity:** Epic · **Element:** Garden 🌿 · **Role:** Poison Support
- **Stats:** CP 4 · Poise 7 · Charm 9 · Speed 6
- **Ability — Perfect Tea** *(cooldown 3)* — Heal an ally for 3 and poison an enemy (2 damage/turn × 3 turns).
- **Flavor:** "Nobody can prove anything. Nobody."
- **Visual:** A mischievous brown-haired maid with hair in two messy buns, pointed black witch's hat tilted rakishly over one eye, golden cat-like eyes. Dark-green apron embroidered with little teacups, over a black-and-purple striped dress. Holds a steaming patterned teapot in one hand; the other hand hides a small vial of suspicious bubbling green liquid behind her back. Coy, conspiratorial smile. Background: warm tea-shop with hanging dried flowers and shelves of bottled herbs.

### Indra, Mainspring Engineer
- **Rarity:** Epic · **Element:** Clockwork ⚙️ · **Role:** Combo
- **Stats:** CP 6 · Poise 7 · Charm 8 · Speed 7
- **Ability — Synchronize** *(cooldown 3)* — Heal all allies for 2.
- **Flavor:** "She thinks of the team as one large, polite machine."
- **Visual:** A tall focused woman with platinum-blonde hair in a high precise bun, sharp grey eyes, a thin pair of magnifying spectacles. Brass-and-leather engineer's vest over a steel-grey dress, tool belt of micro-instruments. Wields an enormous torque wrench like a staff. Large interlocking brass gears float around her in perfectly synchronized rotation. Steampunk-workshop backdrop with intricate machinery and exposed pipework.

## Legendary — 2 cards

### Vexa, Shadow Butler-Maid
- **Rarity:** Legendary · **Element:** Shadow 🕸 · **Role:** Assassin
- **Stats:** CP 9 · Poise 7 · Charm 7 · Speed 9
- **Ability — Borrowed Silverware** *(cooldown 3)* — Deal 5 damage and steal 2 Clean Power from an enemy for 2 turns.
- **Flavor:** "If you cannot find it, she did not take it. Probably."
- **Visual:** A tall slender androgynous figure with sleek black hair streaked with deep purple, sharp violet eyes, knowing smirk. Hybrid uniform: butler's long-tailed coat with maid-apron over it, immaculate white gloves, black leather knee-boots. A small array of polished silver utensils (forks, butter knives, sugar tongs) floats around them like throwing-blades poised to strike. Dim candlelit hallway backdrop with long stretched shadows.

### Solene, Dawnward
- **Rarity:** Legendary · **Element:** Light 🕯 · **Role:** Guardian
- **Stats:** CP 7 · Poise 11 · Charm 8 · Speed 6
- **Ability — Morning Aegis** *(cooldown 3)* — Grant all allies a 4-Poise shield.
- **Flavor:** "Has not been late in seventeen consecutive sunrises."
- **Visual:** A tall regal woman with elaborately braided golden hair, kind sky-blue eyes, calm determined expression. Cream-and-gold half-armor (pauldrons, gauntlets, breastplate) layered OVER a white maid uniform — a paladin-maid hybrid. Holds a glowing tower shield etched with sunrise rays in one hand and a feather duster in the other. Light radiates around her. Dawn-bathed background of a manor courtyard, soft pink-gold sunrise behind her.

## Mythic — 1 card

### Aurelia, Head Maid of the Golden Hall
- **Rarity:** Mythic · **Element:** Royal 👑 · **Role:** Leader
- **Stats:** CP 8 · Poise 12 · Charm 10 · Speed 8
- **Ability — Order Restored** *(cooldown 3)* — Heal all allies for 5 and cleanse the whole team of debuffs.
- **Flavor:** "The chaos is not banished. It has merely been corrected."
- **Visual:** A stunning auburn-haired woman with hair in an elaborate updo, intense amber eyes, serene commanding presence. Flowing gold-and-white gown layered over a regal maid uniform — ornate gold trim everywhere, lace cuffs, jeweled apron pin. Wears a tiara-like golden headpiece. Carries an ornate golden key like a sceptre, vertical. The air around her shimmers with literal golden glow. Background: vast marble ballroom with chandeliers, columns, polished gold floors reflecting her radiance.

---

# Tools (10)

Tools equip to maids in their matching deck slot. The bonuses below stack on top of the maid's base stats. A few tools also carry a `passive_id` flag for future status hooks (unused in v1; the bonuses above are what actually fire).

## Common — 2 tools

### Spare Broom
- **Rarity:** Common
- **Bonuses:** +1 Clean Power
- **Effect text:** "+1 Clean Power. Nothing fancy."
- **Flavor:** "The handle has bite marks. Don't ask."
- **Visual:** A plain wooden broom with worn rough-hewn handle, bristles slightly bent and frayed. Leaning against a chipped stone wall. Tiny faint bite-marks visible on the handle near the top. Neutral warm-grey background with soft dust particles in the air.

### Lavender Sachet
- **Rarity:** Common
- **Bonuses:** +2 Charm
- **Effect text:** "+2 Charm."
- **Flavor:** "The smell calms even cursed laundry. Briefly."
- **Visual:** A small embroidered linen pouch in soft pale lavender, drawn closed with a violet silk ribbon. Sprigs of dried lavender peek out the top. Resting on a polished wood surface. Faint purple aroma swirls drift up. Warm sunlit cottage backdrop.

## Uncommon — 2 tools

### Cursed Mop
- **Rarity:** Uncommon
- **Bonuses:** +5 Clean Power
- **Effect text:** "+5 Clean Power. Wielder loses 1 Poise each turn." *(passive `drain_1_per_turn` — reserved for v1.1)*
- **Flavor:** "It whispers cleaning tips. Mostly threats."
- **Visual:** An aged wooden mop with frayed grey strands, head soaked through with a sickly-green ooze. A faint dark-green glow emanates from it, with whorls of shadow swirling slowly around the handle. Tiny faintly-glowing runic etchings carved along the handle. Dim, dripping background — a haunted utility closet.

### Silver Polish Rag
- **Rarity:** Uncommon
- **Bonuses:** +2 Clean Power, +1 Charm
- **Effect text:** "+2 Clean Power, +1 Charm."
- **Flavor:** "Glints with the optimism of a thousand fingerprints."
- **Visual:** A folded silk rag in pale silver, shimmering faintly. Resting beside a small glass bottle of silver polish with a cork stopper. Light catches the silver flecks woven into the cloth, scattering tiny highlights. Polished wooden tabletop background.

## Rare — 3 tools

### Golden Feather Duster
- **Rarity:** Rare
- **Bonuses:** +3 Clean Power, +1 Speed
- **Effect text:** "+3 Clean Power. +1 Speed if equipped to a Light or Royal maid."
- **Flavor:** "Shimmers self-importantly between battles."
- **Visual:** An ornate ceremonial feather duster — fibers are spun golden filaments rather than real bird feathers, turned ebony handle inlaid with mother-of-pearl arabesques. A soft golden radiance pulses from its tip. Floating slightly above a velvet display cushion. Royal-blue background with subtle gold-dust particles.

### Clockwork Dustpan
- **Rarity:** Rare
- **Bonuses:** +2 Poise, +2 Speed
- **Effect text:** "+2 Poise, +2 Speed."
- **Flavor:** "Empties itself at exactly 3:42pm. Always."
- **Visual:** A polished brass dustpan with an intricate clockwork mechanism mounted on its back — visible gears, exposed mainspring, and a small wind-up key in motion. Tiny puffs of dust spiral up from the floor and INTO the pan as if drawn magnetically. Warm copper-toned background with diffuse workshop lighting.

### Bonded Apron of Service
- **Rarity:** Rare
- **Bonuses:** +4 Poise
- **Effect text:** "+4 Poise."
- **Flavor:** "Reinforced with the stubbornness of seven generations."
- **Visual:** A heavy linen apron in faded cream, hanging on a brass hook against weathered wood. Seven different family crests embroidered down the front in faded but proud thread. Reinforced cross-stitching on the seams, deep pockets bulging with small tools and cleaning rags. Slight sense of dignified history.

## Epic — 2 tools

### Tea Tray of Diplomacy
- **Rarity:** Epic
- **Bonuses:** +2 Poise
- **Effect text:** "+2 Poise. Prevents the next negative effect targeting this maid." *(passive `block_next_debuff` — reserved for v1.1)*
- **Flavor:** "Loaded with biscuits of unimpeachable etiquette."
- **Visual:** An ornate silver tea tray carved with vine motifs around the rim. Holds a delicate porcelain teapot, three matching teacups, and a geometric arrangement of perfectly stacked shortbread biscuits. A soft golden peace-aura radiates from it. Floating gently. Pale-purple background with faint gold sparkles.

### Eternal Kettle
- **Rarity:** Epic
- **Bonuses:** +3 Poise, +2 Charm
- **Effect text:** "+3 Poise, +2 Charm. Heal 1 Poise at the start of each turn." *(passive `heal_self_1_per_turn` — reserved for v1.1)*
- **Flavor:** "Has never been empty. Has never been clean."
- **Visual:** A copper-and-brass kettle covered in elaborate engraved runes and floral motifs, slightly tarnished from centuries of use. Steam rises perpetually from the spout in delicate spirals. A small glass viewing window in its side reveals a soft reddish glow within. Sitting on a glowing stone hearth. Warm orange-pink background.

## Legendary — 1 tool

### Heart of the Manor
- **Rarity:** Legendary
- **Bonuses:** +2 CP, +3 Poise, +3 Charm, +2 Speed
- **Effect text:** "+2 CP, +3 Poise, +3 Charm, +2 Speed."
- **Flavor:** "A small amulet. Faintly hums with the bricks' approval."
- **Visual:** A glowing amber crystal pendant suspended on a delicate silver chain. The pendant pulses softly like a slow heartbeat. Etched within the crystal: tiny Roman numerals, miniature floor plans of the manor, and delicate filigree. Warm gold light from inside the gem illuminates a soft halo around it. Dark background with gold motes drifting outward.

---

# Chaos Enemies (10)

These spawn during PvE battles, scaled by tier. Tier 1 is starter chaos, tier 3 is mid-game; raid bosses live in their own file.

## Tier 1 — 3 enemies

### Dust Goblin
- **Element:** Shadow 🕸 · **Poise:** 6 · **CP:** 3 · **Speed:** 5
- **Ability — Bite:** Deal 3 damage.
- **Flavor:** "Made of lint and bad attitude."
- **Visual:** A small mischievous goblin entirely formed from clumped grey dust and lint, with two glowing yellow pinprick eyes. A stolen bottle cap perched on its head like a tiny helmet. Hunched menacing posture, tiny needle-claws bared, mouth pulled into a malicious grin. Background: a dim dusty under-the-furniture space.

### Sock Gremlin
- **Element:** Shadow 🕸 · **Poise:** 4 · **CP:** 4 · **Speed:** 7
- **Ability — Snatch:** Deal 4 damage and skitter away (high speed).
- **Flavor:** "Has stolen exactly one of every pair you own."
- **Visual:** A skinny twitchy gremlin made of mismatched tangled socks (stripes, polka-dots, plain) sewn together messily. Holds a single brightly-colored sock high like a stolen trophy. Long thin tongue lolls out greedily. Half-crouched behind an upturned laundry basket. Background: dim laundry room with scattered orphan socks.

### Drama Spill
- **Element:** Moon 🌙 · **Poise:** 5 · **CP:** 2 · **Speed:** 4
- **Ability — Awkward Silence:** All player maids lose 1 Charm for 1 turn.
- **Flavor:** "It just sits there. Judging."
- **Visual:** A spreading purple liquid stain on an ornate cream-colored rug. Two large judgmental eyes and a downturned disapproving mouth have formed in the surface tension of the liquid. Faint wisps of shadowy emotional vapor leak upward from it. The rug pattern is slightly warped near the stain. Background: an embarrassed dim living room corner.

## Tier 2 — 4 enemies

### Mold Mimic
- **Element:** Garden 🌿 · **Poise:** 10 · **CP:** 4 · **Speed:** 3
- **Ability — Slop:** Deal 4 damage.
- **Flavor:** "Looks like a teapot. Is not a teapot."
- **Visual:** A creature shaped almost like a porcelain teapot, but coated entirely in fuzzy black-and-green mold, with patches of slime. One side has cracked open into a wide jagged-toothed mouth and a single glowing yellow eye peers from within. Slime drips down its sides into a small puddle. Dim grimy pantry-shelf backdrop.

### Snack Gremlin
- **Element:** Fire 🔥 · **Poise:** 8 · **CP:** 5 · **Speed:** 6
- **Ability — Crumb Storm:** Deal 5 damage in a shower of crumbs.
- **Flavor:** "Lives in the couch. Mostly."
- **Visual:** A round potato-shaped gremlin with crumbs and food smears stuck all over its lumpy body, beady greedy eyes squinted, sharp little teeth. Holds a half-eaten chocolate-chip cookie possessively in both hands. Surrounded by a small swirl of flying crumbs and food debris. Background: between dimly-lit couch cushions.

### Infinite Dishes
- **Element:** Frost ❄️ · **Poise:** 12 · **CP:** 3 · **Speed:** 2
- **Ability — Clatter:** All player maids lose 1 Speed at end of turn.
- **Flavor:** "There were six. Now there are twenty-six. There were six."
- **Visual:** An impossibly tall precarious stack of porcelain plates, bowls, soup tureens, and teacups balancing on top of each other, reaching off the top of the frame. Frost crystallizes around their edges. Subtle face-patterns formed in the blue china glaze, all of them staring outward with a tired, dead-eyed gaze. Background: a cold sink overflowing with more dishes.

### Possessed Kettle
- **Element:** Fire 🔥 · **Poise:** 9 · **CP:** 6 · **Speed:** 5
- **Ability — Boilover:** Deal 6 damage.
- **Flavor:** "Steam is profanity in a clean kitchen."
- **Visual:** A black cast-iron kettle with two malevolent glowing red eyes embedded in its body. Furious red-tinged steam shoots in violent jets from its spout. A jagged crack runs across its porcelain handle. Floating slightly off the ground, surrounded by leaping flames. Stove backdrop, scorched.

## Tier 3 — 3 enemies

### The Unread Emails
- **Element:** Clockwork ⚙️ · **Poise:** 11 · **CP:** 5 · **Speed:** 4
- **Ability — Backlog:** Deal 5 damage. There are always more.
- **Flavor:** "They have been waiting. They are still waiting."
- **Visual:** A looming amorphous entity made of hundreds of folded paper envelopes, each stamped URGENT in red. Many small glowing yellow eyes peer out from between the layers. Brass clockwork pieces and small mechanical arms keep more envelopes flowing endlessly out from inside the mass. Faint ticking aura. Dim office backdrop with overflowing inbox trays.

### Laundry Hydra
- **Element:** Shadow 🕸 · **Poise:** 18 · **CP:** 5 · **Speed:** 4
- **Ability — Tangle:** When damaged but not defeated, summons a Sock Gremlin.
- **Flavor:** "Cut off one sleeve. Two grow back. Three of them are damp."
- **Visual:** A massive multi-headed monster — three writhing 'heads' formed from tangled wet shirt-sleeves and pillowcases, twisting and dripping. Its body is a swelling mass of damp clothes and bedsheets. Six smaller sock-puppet heads on its limbs all snarl with cloth-button eyes. Water drips menacingly. Dark shadowy laundry-room backdrop.

### Mold King Maximus
- **Element:** Garden 🌿 · **Poise:** 22 · **CP:** 7 · **Speed:** 3
- **Ability — Royal Mildew:** Deal 7 damage with smug entitlement.
- **Flavor:** "He sees himself as a connoisseur. Of damp."
- **Visual:** The RAID-BOSS version of Mold King Maximus — significantly larger and more imposing than his standard form. Sitting on a colossal throne of fungal growths and rotting wood. A massive mushroom crown radiates a haze of glowing spores. His cape is a flowing curtain of green-black slime dripping down the throne steps. Carries his ornate moldy scepter raised. Cathedral-sized chamber filled with rotting splendor, glowing spores drifting like motes, broken stained-glass windows depicting his moldy victories. Light filters through in green-gold beams.

---

# Raid Bosses (3)

Server-wide chaos events; everyone in the server attacks the same boss. These are **not** collectible cards — they're event banners.

### The Great Unwashed One
- **Tier:** 1 · **Element:** Shadow 🕸 · **HP:** 1,500
- **Flavor:** "A mountain of laundry possessed by ancient laziness."
- **Visual:** A COLOSSAL mountain of tangled, dirty laundry — bedsheets, towels, socks, undergarments — piled like a small geological feature. Many baleful glowing yellow eyes peek from between the folds. A wide malevolent grin forms in one of the larger creases. The pile slumps menacingly. A tiny lone laundry room is visible at its base for scale. Backdrop: a dark, ominous basement-laundry-room with a single bare bulb.

### Laundry Hydra Prime
- **Tier:** 2 · **Element:** Shadow 🕸 · **HP:** 4,000
- **Flavor:** "Three sleeves. Six socks. None of them match."
- **Visual:** An APEX version of the Laundry Hydra — much larger and more menacing, with six massive towering 'heads' of wet sleeves writhing in different directions, each open at the cuff like a hungry maw. Six secondary sock-puppet limbs lash about. Dripping with foul soapy water. Body of soaked sheets piled like a hulking torso. Background: a vast flooded laundry-temple with overflowing washing machines.

### Mold King Maximus
- **Tier:** 3 · **Element:** Garden 🌿 · **HP:** 8,000
- **Flavor:** "He sees himself as a connoisseur. Of damp."
- **Visual:** The RAID-BOSS version of Mold King Maximus — significantly larger and more imposing than his standard form. Sitting on a colossal throne of fungal growths and rotting wood. A massive mushroom crown radiates a haze of glowing spores. His cape is a flowing curtain of green-black slime dripping down the throne steps. Carries his ornate moldy scepter raised. Cathedral-sized chamber filled with rotting splendor, glowing spores drifting like motes, broken stained-glass windows depicting his moldy victories. Light filters through in green-gold beams.

---

## Quick visual-design notes

- **Card border:** color from the rarity hex above.
- **Element badge:** small icon in a top corner using the element emoji + hex.
- **Stat block:** four icons (🧹 CP, 🛡 Poise, ✨ Charm, ⚡ Speed) on maids; three (🛡 Poise, 🧹 CP, ⚡ Speed) on chaos.
- **Ability text:** the in-game canonical version is what's listed under each card here (some differ slightly from `data/maids.py`'s `ability_text` — Phase 6 status-effect rewire). When in doubt, use what's in this file.
- **Flavor:** italicized at the bottom of the card.
- **Tool art:** no element badge (tools are element-neutral). The bonus block replaces the stat block.
