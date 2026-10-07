# Aurelia: The Shattered Crown (Forge 1.20.1)

Three realms, three Wardens, one broken crown. Built for Ascendra (Forge 1.20.1); depends on nothing except Forge.

## The shape of it

Aurelia was a kingdom of three realms bound by one crown. The Sovereign vanished, the crown broke, and each realm's Warden went wrong guarding its shard.

You find each realm's way in inside an **independent Citadel** out in the overworld. Fight your way through the guards, solve the citadel's puzzle to wake its portal, then beat the realm's Warden. Beat all three to reforge the **Crown of Aurelia**.

| Citadel | Portal to | Where it generates | Puzzle |
|---|---|---|---|
| **Rootbound Citadel**: a castle grown into a giant tree | The Gaudy Grove | forest biomes | **Plant four Spore Hearts** in four planters |
| **Stormwatch Citadel**: quartz spires on a rock crag | Skyreach | mountain biomes | **Lure Storm Wisps** so their lightning charges three pylons |
| **Ashen Citadel**: a fortress in a lava cavern, underground | The Hollow | badlands, desert, savanna, taiga, swamp | **Place twelve Soul Sigils** in twelve sockets |

Find one with `/locate structure aurelia:rootbound_citadel` (also `aurelia:stormwatch_citadel`, `aurelia:ashen_citadel`).

## The citadels

### Rootbound (65 x 65 x 76)
A giant dark-oak tree with a leafy canopy, branches, shelf mushrooms and roots running into the ground. A mossy outer wall with a south gate, four mushroom-capped towers on the diagonals, and a path to an arched entrance into the trunk. Inside the trunk is the portal hall: four **Spore Planters** around a glowing froglight circuit, the portal in a lime-glass alcove, and a lectern with lore.
- **Guards (14):** 4 Bramble Sentinels, 6 Sporecaps, 4 Rootstalkers.
- **Puzzle supply:** every Sporecap drops a Spore Heart, and each of the four towers holds a chest with 2 spare hearts, so it is solvable without killing anything.

### Stormwatch (65 x 65 x 92)
A rock crag topped with a quartz plaza, an octagon storm-sigil inlay, a tall central spire, four satellite spires joined by arched bridges, lightning rods on every tip, and waterfalls off the crag. The portal room is at the base of the central spire: three **Storm Pylons** wired to the portal by a copper circuit.
- **Guards (13):** 4 Calcite Sentinels, 5 Storm Wisps, 4 Gale Talons.
- **Puzzle:** a Storm Wisp's lightning charges every pylon within 4 blocks of the strike. Lure a wisp into the room and stand beside a pylon when it fires. Pylons stay charged.

### Ashen (81 x 81 x 76)
A huge cavern carved under the surface and lined with blackstone, with a lava lake, magma pillars and a basalt plateau holding a keep with four spired towers. A crater shaft opens to the surface, with a spiral ramp winding down its walls to a landing and a causeway across the lava. The portal hall has a recessed pit ringed by twelve **Soul Sockets**, the portal in a crying-obsidian alcove, soul-fire pillars and four chests.
- **Guards (12):** 4 Ashbound Knights, 4 Soul Jailers, 4 Cinder Hounds.
- **Puzzle supply:** Soul Jailers drop Soul Sigils, and each of the four hall chests holds 3, so 12 are guaranteed without a single kill.

All three have a lectern in the portal room with lore. Puzzle blocks, portals and altars are unbreakable in survival so nobody can soft-lock a citadel (creative can still remove them).

## The guards

| | Heavy | Special | Fast |
|---|---|---|---|
| **Rootbound** | **Bramble Sentinel** (90 HP): thorns hurt melee attackers, hard to knock back | **Sporecap** (34 HP): keeps its distance, throws poison spore clouds, heals nearby guards | **Rootstalker** (40 HP): pounces from range, its bite roots you |
| **Stormwatch** | **Calcite Sentinel** (100 HP): shield cuts frontal damage by 60%, flank it | **Storm Wisp** (30 HP): floats overhead, telegraphed lightning | **Gale Talon** (30 HP): circles, then dives with heavy knockback |
| **Ashen** | **Ashbound Knight** (110 HP): fire immune, greatsword ignites you | **Soul Jailer** (60 HP): chains you in place (slowness, weakness), calls Shades | **Cinder Hound** (50 HP): pounces, fiery bite |

## The Wardens (three phases each, at 66% and 33% health)

The Wardens were redesigned to be frightening. Each is a hierarchical model of 185 to 253 parts.

- **Mossback** (2500 HP): a hunched rot-wood horror with a deer-skull head, burning eye sockets, a jaw that hangs and works, a huge thorned antler rack hung with moss and skull trophies, an open ribcage around a beating glowing heart, broken branches jutting from its back, and arms long enough for its hooked claws to drag on the ground.
  **Gimmick: Root Hearts.** He plants 3 (4 in phase 3) around the arena. While any stands he heals 1.2% per heart per second and takes only 30% damage. Break them.
- **Tempest Roc** (3000 HP, flies): a storm-black raptor in a horned bone mask with white burning eyes, a snapping beak with a glowing throat, bone spikes down its spine and along the leading edge of each wing, wrist claws, two-jointed talons, a ragged nine-feather tail with two bone blades, and crackling sparks.
  **Gimmick: crash and stun.** Half damage in the air. A dive that misses leaves it stunned on the ground for about 3.5 seconds with the damage caps raised 2.5x. From phase 2 it throws gusts.
- **The Hollow King** (4000 HP): a towering dead king with a skull face in an open helm, a moving jaw, forward-curving horns, iron crown spikes with burning tips, skull-faced pauldrons with long spikes, bone ribs over black plate around a pulsing core, a spiked fur collar, a nine-strip torn cape, a soul orb in his left hand, a burning serrated greatsword taller than he is, six soul shards orbiting his chest, and a broken iron halo.
  **Gimmick: Annihilation.** He channels for 5 seconds. Deal 6% of his health in that window to stagger him (caps doubled for 5 seconds); fail and everyone within 28 blocks loses 60% of their max health.

Menace effects shared by all three:
- **Glow**: eyes, hearts, runes, soul fire and lava cracks are drawn at full brightness, so they shine in the dark (all nine guards get this too).
- **The sky darkens and fog rolls in** while a Warden's health bar is on screen (the same effect the Wither uses).
- **A heartbeat** sounds while he has a target, faster in the final phase.
- **Dread pulse**: at each phase change he roars, nearby players are blinded by Darkness for 5 seconds and thrown back.
- Hearts and cores visibly pulse; jaws and beaks open and close.

Damage limits: one hit removes at most 2% of a Warden's health and total damage is capped at 4% per second (`HIT_CAP`, `SECOND_CAP` in `AureliaBoss`). Stun and stagger windows raise those caps.

## Progression

1. **Rootbound Citadel**: plant four Spore Hearts, then right-click the portal. In the Grove, crouch and touch the altar to wake Mossback.
2. Mossback drops a **Grove Shard**. The **Stormwatch** portal will only open for someone **holding a Grove Shard**.
3. The Roc drops a **Storm Shard**. The **Ashen** portal needs a **Storm Shard** in hand.
4. The King drops a **Void Shard**. **Crown of Aurelia** = 3 shards + Block of Verdant Shards + Block of Stormglass + Block of Emberheart.

The Crown (helmet, never breaks) gives creative-style flight, Regeneration, Resistance, Night Vision, Water Breathing, toughness 4 and some knockback resistance.

## Citadel gimmicks

Each citadel has three layers: a **sealed door**, a **floor mechanism**, and the **portal puzzle** inside.

| Citadel | Seal (touch it to check) | Floor mechanism | Portal puzzle |
|---|---|---|---|
| Rootbound | **Bramble Seal** across the trunk entrance. Falls when all 4 Bramble Sentinels are dead. | **Spore Vents** on the path: poison and slowness when stepped on. | Plant four Spore Hearts. |
| Stormwatch | **Storm Seal** across the spire door. Falls when all 4 Calcite Sentinels are dead. | **Gale Plates** on the plaza: launch you about 20 blocks up with slow falling. Two bridges hold loot caches you can only reach this way. | Lure Wisp lightning onto three pylons. |
| Ashen | **Ash Seal** across the keep door. Falls when all 4 Ashbound Knights are dead. | **Ember Vents** on the causeway: fire and damage when stepped on. | Place twelve Soul Sigils. |

A seal counts its guardians within 48 blocks. Touching it tells you how many remain.

### Citadel architecture

**Rootbound**: a timber wall-walk on log brackets inside the curtain wall, reached by ladders and by doors from each tower; buttresses and arrow slits; a gatehouse with two roofed turrets and banners; three furnished floors in every tower (barrels, bookshelves, hay, lanterns) joined by a ladder; a lamp-lit path under root arches; a ring path, lily pond, fenced berry garden and an idol of the Warden in the courtyard; a carved door frame on the trunk with two glowing eyes above it; glow-berry vines and bee nests in the canopy; three roofed lookout platforms off the terrace; mushroom huts; weathered and cracked stonework.

**Stormwatch**: weathered copper roofs with bright bands on all five spires; arches under the four bridges with end-rod lamps; stained glass rings up the central spire; buttress fins and a balcony ring; a plaza with lamp posts, two reflecting pools lit from below, two winged statues, a fountain, hedges and flower beds; three tethered islets with pavilions; amethyst veins in the crag; a ring of floating rune stones; angel wings over the gate.

**Ashen**: stepped buttress piers and glowing furnace windows on every keep wall; a chiseled gate frame with fang spikes and hanging lanterns; battlement spikes; pyramid roofs and hanging soul lanterns on the towers; skulls on pikes, bone piles and basalt columns across the plateau; a colonnade of lantern pillars; inside the hall, two rows of columns, lava glowing under glass along the walls, banners, vaulted ribs, and a throne of crying obsidian against the east wall.

## Outposts, ores and materials

Each realm has two kinds of randomly generated outpost, each with guards and a loot chest:

- **Grove**
  - **Watchtower camp**: a spiked log palisade with a gatehouse, a cross-braced tower with a windowed cabin and stepped roof on top, two tents, a campfire with seats, log piles, barrels, an archery target, a grindstone, an iron cage. Guards: Bramble Sentinel, 2 Rootstalkers, Sporecap.
  - **Sporecap hamlet**: a great mushroom hall with a seven-block cap, four huts joined to it by paths, a roofed well, a fenced berry garden, a market stall with a striped awning, lamp posts, wild giant mushrooms. Guards: 4 Sporecaps, Rootstalker, Bramble Sentinel.
- **Skyreach**
  - **Watch island**: a three-floor quartz tower with a ladder, stained glass, a balcony ring, banners, a conical copper roof and lightning rod; a lamp-lit quartz path; a gale plate; broken pillars. The chest is on the top floor. Guards: Calcite Sentinel, 2 Storm Wisps.
  - **Wind shrine**: eight pillars joined by a lintel ring hung with bells, a three-tier dais with candles, and a crystal floating above the chest. Guards: 2 Gale Talons, Storm Wisp.
- **Hollow**
  - **Ashen fort**: a curtain wall with a wall-walk and battlements, a gate with banners, four round turrets with fire on top, a three-floor keep with furnace windows (chest on the roof), a forge with a lava cauldron, prison cages, sunken lava pools, skull pikes. Guards: Ashbound Knight, 2 Cinder Hounds, Soul Jailer.
  - **Soul shrine**: eight obsidian pillars with lantern arms, a stepped altar with candles, a ring of soul sand with wither roses and soul fire, a gate arch, skull pikes. Guards: 2 Soul Jailers, Cinder Hound.

Other realm structures gained detail too: two new Grove ruins (a **tower stump** with a broken stair and a **fallen colonnade**), a pillared **temple on every ziggurat summit** with corner obelisks and skull pikes, and **hanging lanterns and gate arches** on the Hollow bridges.

Each realm has its own ore (iron pickaxe or better, Fortune works, Silk Touch drops the ore block):

| Ore | Where | Drops | Storage block |
|---|---|---|---|
| Verdant Ore | Grove stone, pillar faces | Verdant Shard | Block of Verdant Shards |
| Stormglass Ore | The rock of every Skyreach island (glows faintly) | Stormglass Shard | Block of Stormglass (light source) |
| Emberheart Ore | Hollow blackstone and basalt, stalactites, rock plugs | Emberheart | Block of Emberheart (light source) |

Outpost chests hold 3 to 7 of their realm's material. **The Crown recipe changed**: it is now the three shards plus one storage block of each material (9 of each), so exploring all three realms is part of the goal.

## The realms

Each realm combines vanilla terrain generation with structures and features the mod adds.

**The Gaudy Grove**: amplified terrain (towering hills) covered in moss, jungle forest and giant mushrooms. On top of that, the mod adds:
- **Forested stone pillars** (4 variants, 40 to 70+ blocks tall): flared mesa tops with a pond, a waterfall that spills down the face, jungle trees, mushrooms, flowers and ferns, vine curtains, and mossy boulders at the foot.
- **Mossy ruins** (3 variants): a broken stone arch, pillars, a wall and stair, overgrown with vines and flowers.
- **Cliff waterfalls and vine curtains** everywhere (custom spring and vine features), jungle mega-trees, large ferns, flower fields, drifting spores, permanent noon.

**Skyreach**: a true void world. The islands are structures:
- **Floating islands** in four sizes (3 small, 3 medium, 2 large, 1 spired castle island) at random heights between y=30 and y=170. Each has a calcite cone underside with hanging spikes, a grass top with white and pink blossom trees, flowers, ferns and tall grass, hanging vines, and satellite rocks.
- Medium and large islands have **a pond and a waterfall** that spills off the edge. Large islands carry a **ruined quartz tower**. The castle island has a **spire cluster** and a quartz plaza.
- Sparkling air, phantoms and Sky Sentinels.

**The Hollow**: a closed Nether-style cavern under a black ceiling, with basalt floors, soul-soil drifts, lava lakes, falling ash, and:
- **Ziggurats** (2 variants, 4 to 5 tiers) on lava-island plugs, with stairs on every side, braziers, crimson fungi, a lava pool and a crying-obsidian altar at the top.
- **Arched bridges** (2 variants, 34 to 40 blocks) on broad piers, with railings and soul-fire posts.
- **Hanging stalactites** (5 variants, 24 to 46 blocks) fixed to the bedrock ceiling, with glowstone nodules.
- **Giant red fungi** on basalt, **lava falls** (custom springs), soul-fire patches and glowstone clusters.

## Building the jar

1. Install **JDK 17**.
2. Download the official **Forge MDK for 1.20.1** (47.x) from files.minecraftforge.net and extract it.
3. Delete the MDK's example code at `src/main/java/com/example` and its example resources.
4. Copy this project's `src/` folder into the MDK (merge, overwrite `mods.toml` and `pack.mcmeta`).
5. In the MDK's `gradle.properties` set `mod_id=aurelia`, `mod_name=Aurelia`, `mod_version=1.0.0`, `mod_group_id=com.aurelia`.
   (If your MDK keeps `mods.toml` in `src/main/templates`, put the provided one there instead.)
6. Run `./gradlew build` (Windows: `gradlew build`). The jar is in `build/libs/`.
7. Drop the jar into your Ascendra `mods` folder.

## Testing plan (in this order)

1. **A throwaway world first**, Forge only if you can, then Ascendra. A bad datapack file can stop a world from loading.
2. In creative, open the *Aurelia* tab: every block, item and spawn egg is there. Spawn each guard and check how it looks and moves.
3. **Solve the puzzles without finding a citadel**: `/place structure aurelia:rootbound_citadel ~ ~ ~` (also `stormwatch_citadel`). The Ashen Citadel is built to sit 66 blocks below the surface, so for a quick look use `/locate structure aurelia:ashen_citadel` and travel there instead.
   - To see a realm structure without exploring: `/place structure aurelia:skyreach_large_islands ~ ~ ~` (inside the Skyreach dimension), `aurelia:grove_pillars` or `aurelia:grove_ruins` (Grove), `aurelia:hollow_ziggurats` (Hollow).
   - To skip a puzzle: `/setblock <x> <y> <z> aurelia:waygate[realm=grove,active=true]` (realm is `grove`, `skyreach` or `hollow`).
4. Check each realm loads: `/execute in aurelia:grove run tp @s 0 150 0` (also `aurelia:skyreach`, `aurelia:hollow`).
5. Fight each Warden at its altar (crouch and touch it) with your real Ascendra gear.
6. Craft the Crown and check flight and effects.

If something fails, send me `logs/latest.log` (and the file from `crash-reports/` if there is one).

## Tuning

- **Citadel rarity**: `spacing` and `separation` in `data/aurelia/worldgen/structure_set/*.json` (smaller means more).
- **Which biomes**: `data/aurelia/tags/worldgen/biome/has_structure/*.json`.
- **Citadel loot**: `data/aurelia/loot_tables/chests/rootbound_hearts.json` and `ashen_sigils.json`. I could not see Ascendra's items, so the extras are vanilla.
- **Guard stats**: `createAttributes()` in each guard class, plus the effect numbers in the class body.
- **Guard drops**: `data/aurelia/loot_tables/entities/*.json`.
- **Warden stats and damage limits**: see above.
- **Realm structure frequency**: `spacing` and `separation` in the matching `structure_set` files (`skyreach_*_islands`, `grove_pillars`, `grove_ruins`, `hollow_*`).
- **Mob shapes and textures**: generated from box-by-box specs (`tools/mobspecs.py` and `tools/bosses_v2.py`); ask me and I will change a model and regenerate it.

## Known risks (I could not launch Minecraft)

- **The glow layer** uses a second texture per mob (`<name>_glow.png`). If a mob renders with a white or black overlay, that layer is the cause; remove the `addLayer` line in `SpecRenderer` to turn it off.
- **Pulsing hearts** use the model part scale fields (`xScale`, `yScale`, `zScale`). I believe 1.20.1 has them; if the build fails in `SpecModel` on those names, delete the `pulse` case.
- **The boss models are now 185 to 253 parts** with nested limbs (the Mossback's arms hang from a leaning torso). A wrongly placed limb in game would come from the parent/child position conversion.
- **Bosses are larger**; their hitboxes grew to match (Mossback 3.4 x 6.6, Roc 4.0 x 2.4, King 2.2 x 7.4).

- **Seals depend on the heavy guards staying nearby.** If one wanders more than 48 blocks away or dies to the environment, it stops counting, which only makes the seal easier. If a seal ever refuses to open, `/kill @e[type=aurelia:bramble_sentinel]` (or `calcite_sentinel`, `ashbound_knight`) clears it.
- **Gale Plates** launch with an upward speed of 1.9. I estimated the height at about 20 blocks; if you overshoot or fall short of the bridges, change the number in `TrapBlock`.
- **Root Hearts** are placed on the first air block above ground near the arena centre. On very uneven ground a heart may fail to place; the fight still works.

- **Skyreach is a void world.** Every block is air except the island structures, and the landing pad is built at y=120 at (0, 0). If the structure sets fail to load, Skyreach would be empty. Check `latest.log` first if the sky looks bare.
- **The boss models are big** (about 170 parts each, 512x512 textures). They render fine in principle, but the hierarchy conversion (a child part's position relative to its parent) is new and the most likely place for a part to look misplaced.
- **Giant red fungi** rely on a copy of vanilla's crimson fungus with its valid base changed to basalt. If they never appear, that block check is the reason.
- **Skyreach waterfalls and pond water** are placed as water sources and will flow once the chunk ticks. Expect them to settle over a few seconds.

- **Untested in game.** The Java has no syntax errors and I checked several Forge signatures against Forge's source. Every vanilla block, property, feature, particle and item ID is checked against 1.20.1 data. Every structure, model, texture, loot table and ID cross-reference resolves. But none of it has run.
- **Custom mob models** are built in code (`MobModels`) from box specs. The coordinate conversion from my preview space to Minecraft's model space is the most likely place for a surprise, such as a mirrored limb or a part sitting a little off. It is easy to correct.
- **Animation** is generic (walking legs, swinging arms, flapping wings, turning heads, orbiting plates). Attacks have no special animation.
- **The Ashen Citadel** is carved into the ground and lined with blackstone. If a world has an aquifer or lava pocket in the wrong place, expect a little spill. It is also the heaviest structure to generate.
- **Puzzle scan**: waking a portal scans a 73 x 49 x 73 area around the last node you filled. Fine for one interaction, but it is the heaviest bit of puzzle code.
- **Citadel placement** uses vanilla's jigsaw system and flattens a circular or square area. On a steep slope it will look blocky.
- **Biome mods in Ascendra** change which biomes are common. If a citadel is hard to find, raise its frequency or widen its biome tag.
