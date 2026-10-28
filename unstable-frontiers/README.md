# Antarchy: Unstable Frontiers

A companion addon for [Antarchy](https://www.curseforge.com/minecraft/mc-mods/antarchy) (by CraisinLord) on Minecraft 1.20.1 Forge.
It adds the **Unstable Frontier**, a dangerous wilderness dimension in the spirit of OreSpawn's Danger Dimension: huge
terrain, an ash-grey sky, cage towers on the skyline, and flying predators hunting giant insects at the foot of them.

This is **milestone 1**. It is a playable slice: the dimension, travel, one region, one cage tower design, bounded fights,
one rivalry, one reward. The roadmap at the bottom covers the rest.

## Compatibility: what is verified and what is not

| | Status |
|---|---|
| Minecraft 1.20.1, Forge 47.x, Java 17 | Built against Forge 47.3.0; runs on any 47.x (your pack runs 47.4.20). |
| Antarchy | **Optional dependency** (`[2.2.0,)`). Without it the addon uses vanilla stand-ins and says so in the log. |
| Antarchy entity ids used | Read from Antarchy's public source, `forge-1.20.1` module, version 2.2.9 (commit `f3e73b1e`): `mantis`, `alpha_mantis`, `scorpion`, `springbug`, `wasp`, `brutalfly`, `stratoshark`, `nightmare` and more (see the tags). **Not yet tested in a game with Antarchy installed.** |
| Dedicated server | Smoke-tested in CI **without Antarchy** (see "Automated checks"). |
| Client | Not tested by me; I cannot run a Minecraft client here. Client code is resources only (models, textures, lang). |
| Superhero / Transformers mods | Not integrated yet (milestone 4). Nothing in this addon disables powers or flight. |

Antarchy is "All Rights Reserved". This addon contains none of its code or assets; it refers to its creatures by id only,
through config lists and optional tag entries, so nothing breaks when Antarchy is missing or renames something.

Antarchy's own dimensions (Cavaryn, Elythia, Thoraxis) are a termite horde world, a peaceful sky world and an inverted
dream world. None plays the role of a danger dimension, so this addon adds its own rather than changing Antarchy's.

## Getting there and back

* **Unstable Rift Shard**: amethyst shards in the corners, crying obsidian on the sides, an eye of ender in the middle.
  Use it anywhere to cross into the frontier, at the same x/z you left. Use it in the frontier to go back to where you left.
  It is never used up (5 second cooldown).
* **Safe arrival**: you land on the top solid block of your column. If that is water, lava, magma or nothing, a 3x3 deepslate
  platform is built under you.
* **Recovery**: lost your shard? `/frontier return` works for every player in the frontier (60 s cooldown). It takes you to
  where you left; if that dimension is gone, to your respawn point; failing that, to world spawn. Your return point is
  saved with your player data and survives death.
* On arrival you are told how far, and which way, the nearest tower is.

## The frontier

Amplified terrain (towering cliffs and peaks) in two biomes:

* **Gnashwood Wilds**: dark, choked forest of dark oak, giant pines and huge mushrooms, purple grass and blood-red leaves,
  falling ash, a bruised violet sky. Wild skirmishes are common.
* **Hushed Barrens**: sparse, grey and quiet. The breathing room: wild skirmishes are rare here unless a tower is near.

Nights are dark but not blinding (ambient light 0.06), and night changes who is out: by day mostly insects with the odd
stratoshark or brutalfly, by night more predators, and Antarchy's **Nightmare**.

## The cage tower

Original design, built from vanilla blocks. 25 x 25 footprint, 62 blocks tall, three stacked cages that step inward, and
an open crown lit like a beacon so you can see it from far off.

| Stage | Height | Who lives there (Antarchy / without Antarchy) | Chest |
|---|---|---|---|
| The Swarm Pen | floor 0 | mantises, scorpions / spiders, cave spiders | iron, gold, pearls, a diamond or three |
| The Hatchery | floor 1 | scorpions, wasps, a springbug / cave spiders, spiders | diamonds, enchanted book, 20% netherite scrap |
| The Aerie | floor 2 | stratosharks, wasps, a brutalfly, a blaze / phantoms, a blaze | diamonds, level-30 book, 35% scrap, 8% totem |
| The Crown | top | an alpha mantis and two mantises / a ravager and two spiders | the vault: diamonds, scrap, a Cage Trophy, 25% netherite ingot, 20% enchanted golden apple |

Every floor's chest sits on a pedestal in a small cage in the middle, visible through the bars from outside.

**Ways in**: the south door; the ladder up the iron spine on the east face, with a bridge to every floor; the ladder inside
each floor up through the ceiling; a bent-bar gap in every wall; flying in over the crown; or breaking the bars. **Nothing is
unbreakable.** Robbing chests without fighting is allowed; the completion reward needs the fights.

**How a fight works**

1. Step inside a cage that is not cleared and it wakes (creative mode never wakes one).
2. It sends `wavesPerFloor` waves (the crown sends one). Each wave waits for the cooldown and for the floor to thin out.
3. The floor is cleared when every wave has come and every creature is dead. Cleared floors stay cleared for good.
4. Clear all four stages and the tower is complete. Every player who fought there and is within 96 blocks gets 2 or 3
   **Cage Trophies** and 150 experience, and on their first tower ever, the **Swarmbreaker**. Each player is rewarded once
   per tower.

**Limits and persistence**

* One stage per tower fights at a time, however many players come. Several players share one fight; it is not duplicated.
* The number of towers fighting at once on the server is capped.
* Creatures spawn only while a player is near. If nobody is near for `disengageTicks` (20 s), the unfinished floor resets:
  its creatures are removed and it can be fought again later. Cleared floors, completion and rewards are untouched.
* Tower creatures are leashed: past `towerLeashRadius` they drop their target and walk back; far past it they are put back.
* Tower state is saved in the frontier's `data/unstable_frontiers_towers.dat` (versioned). Unloading, reloading and
  restarting cannot reset rewards. A creature from a fight that was reset while its chunk was unloaded is removed when the
  chunk loads (each creature carries its tower id and fight session).
* Towers are at least 9 chunks apart, on a 22-chunk grid (`worldgen/structure_set/cage_towers.json`), never over deep water.
  Generation reads five heights per site and builds only the chunk being generated.

## Living monster conflict

The one rivalry in this milestone: **flying predators hunt ground insects** (entity tags `unstable_frontiers:raptors` and
`unstable_frontiers:swarm`). Every few seconds near each player, if there are fewer wild creatures than the cap, a small
skirmish is staged: two or three insects, and (always at night, 40% of the time by day) a predator above them. A predator with
nothing to do is pointed at the nearest insect; the insect fights back with its own AI. Skirmishes favour the foot of a
nearby tower.

What keeps it bounded:

* Only creatures this addon spawned take part. Pets, Antarchy's bosses and everything else are never touched, and no
  creature's AI is replaced.
* Searches are boxes around players (`rivalrySearchRadius`), never world scans, every `aiUpdateIntervalTicks`.
* At most `rivalryFightsPerPlayer` fights near each player. A fight ends after `pursuitTicks` or when the two drift apart,
  and the predator then rests for `rivalryCooldownTicks`.
* Unloaded chunks do not tick, so no fight happens off-screen. Wild creatures are not persistent, so normal despawning clears
  them when you leave, and the director restocks only near players. The frontier can't be emptied for good.
* **Loot eligibility**: a frontier creature drops items and experience only if a player hurt it recently, and at most
  `maxDropsPerMob` stacks. Predator-on-prey kills and unwatched fights leave no items on the ground.

Antarchy's Nightmare also hunts other mobs on its own, through its own AI. This addon does not change that.

## Rewards and progression

* **Cage Trophy**: from tower completion (2 or 3) and every crown vault (1). Repairs the Swarmbreaker.
* **Swarmbreaker** (glaive): 8 attack damage like a netherite sword, 1800 durability, fire-proof, +50% damage to insects
  (`unstable_frontiers:frontier_insects` plus every vanilla arthropod). **Pounce**: use it to leap forward and up, then land in a
  shockwave (6 damage, 9 to insects, knockback) with no fall damage. 8 second cooldown.
  Won from your first tower, or crafted later from a netherite sword surrounded by four Cage Trophies.
* Advancements, under their own tab: craft a shard, enter the frontier, step into a tower, take a trophy, own a Swarmbreaker.
* Item tooltips are the in-game guide.

Diamond or netherite gear is the starting point. The floors pay in diamonds, books and scrap, and only the vault gives
netherite ingots. I have not compared this against Antarchy's own gear in play yet.

## Configuration and presets

`config/unstable_frontiers-common.toml`. Set `density.preset`, then override single values (-1 = use the preset).
Every value is range-checked; Forge resets an out-of-range value to its default.

| Limit | Conservative | **Standard** | High density |
|---|---|---|---|
| encounterMobsPerPlayer | 6 | **10** | 16 |
| encounterMobsPerTower | 10 | **16** | 28 |
| simultaneousTowerEncounters | 2 | **3** | 6 |
| wavesPerFloor | 2 | **3** | 4 |
| mobsPerWave | 3 | **5** | 8 |
| waveCooldownTicks | 300 | **200** | 140 |
| ambientMobsPerPlayer | 5 | **9** | 16 |
| ambientSpawnIntervalTicks | 400 | **240** | 140 |
| rivalrySearchRadius | 16 | **24** | 32 |
| aiUpdateIntervalTicks | 60 | **40** | 20 |
| rivalryFightsPerPlayer | 1 | **2** | 4 |
| maxDropsPerMob | 3 | **4** | 6 |
| particleDensity | 0.4 | **1.0** | 1.0 |

Also: `pursuitTicks`, `rivalryCooldownTicks`, `towerLeashRadius`, `disengageTicks`, `towerChancePercent` (new chunks
only), `returnCommandCooldownSeconds`, and every roster (entity ids, `@N` = at most N per wave). The tower spacing lives in
the structure set JSON; a data pack can override it.

These numbers are a starting point. They have **not been profiled** on your machine. Profile with Spark
(`/spark profiler start`, fight a tower, `/spark profiler stop`) and send me the link. Many Antarchy creatures are large
GeckoLib models; on an RX 6650 XT the render cost of a crowded floor is the thing to watch, and I can't predict a frame rate.

**Memory**: give the pack 8 to 10 GB (CurseForge > Settings > Minecraft > Allocated Memory). Not more than about 12 GB of
your 32: a larger heap means longer garbage-collection pauses, not more speed.

## Commands

| Command | Who | What |
|---|---|---|
| `/frontier return` | everyone, in the frontier | the recovery route home (cooldown) |
| `/frontier go` | op | travel in, like the shard |
| `/frontier locate` | op | nearest generated tower (up to 64 chunks) |
| `/frontier stats` | op | towers known, fighting, tracked creatures, rivalry fights, effective limits |
| `/frontier tower info` | op, standing in a tower's footprint | cleared stages, active stage, wave, alive, session, participants, rewarded |
| `/frontier tower start <0-3>` | op | wake a stage now (runs even with nobody near, until it resets) |
| `/frontier tower reset` | op | un-clear every stage and remove its creatures (rewarded players stay rewarded) |
| `/frontier tower forget` | op | delete the tower's record entirely (it can reward everyone again) |
| `/frontier tower build` | op | build a tower here, registered like a generated one |

Use `/frontier tower build`, not `/place structure`: the vanilla command builds the blocks but saves no structure record,
so the encounter system cannot see that tower.

## Building

Needs Java 17 and Gradle 8.8 (or the Gradle that ships with your IDE). From this folder:

```
gradle build
```

The jar is `build/libs/unstable_frontiers-0.1.0.jar`. Every push to this folder also builds it on GitHub Actions
("Build Unstable Frontiers" workflow); the jar is the `unstable-frontiers-jar` artifact of the run.

Textures are drawn by `python3 tools/gen_textures.py` (needs Pillow).

## Installing

Put the jar in the instance's `mods` folder next to Antarchy and its dependencies (Anthology, AntOS, Integrated API,
GeckoLib, Sizeable Foliage, Pehkui). Use a **new world, or a new region of an old one**: the frontier is a new dimension, so
existing worlds are not changed, but towers only appear in newly generated frontier chunks.

## Automated checks

`ci/smoke.sh` boots a dedicated server with the addon and **without Antarchy**, then:
builds a tower, finds it with the encounter lookup, wakes the Swarm Pen and checks that creatures spawned, waits for the
idle floor to reset itself, wakes the Aerie and the Crown, resets the tower, and locates a naturally generated tower. It
fails on any failed command, any exception in the log, or any missing step.

## In-game test checklist

Please try these and tell me what happens (with `logs/latest.log` if anything goes wrong):

1. Craft a Rift Shard, use it. Do you arrive safely? Does chat point you to a tower? Can you see it?
2. Use the shard again: are you back where you left? Then go in and try `/frontier return`.
3. Walk around for a few minutes in each biome, by day and by night. Do predators fight insects? Do fights end on their own?
4. Enter the tower's ground floor. Do waves come? Do creatures stay in or near the tower? Can you climb the outside ladder
   and use the gaps?
5. Clear all four stages. Do you get trophies and the Swarmbreaker? Try Pounce.
6. Leave a floor half-fought for 30 seconds, come back: did it reset cleanly?
7. Log out mid-fight, log back in: `/frontier tower info` should show the same state.
8. With F3 open, note the FPS and the entity count (E:) in a busy fight, on STANDARD and on CONSERVATIVE.

## Known limitations and placeholders

* **No original creatures yet.** Fights use Antarchy's creatures (or vanilla stand-ins). The stand-ins (spiders, phantoms,
  a ravager crown guardian) are placeholders, not finished content.
* Item textures are original but simple 16x16 pixel art. Not final.
* The sky is a biome tint on the overworld sky; no custom sky renderer yet. No floating islands yet.
* One tower size only (the "small/medium/enormous" variants come after you've tested this one).
* Rewards go only to participants online and within 96 blocks when the tower completes.
* Antarchy creatures' own behaviour (despawn rules, special abilities, the Nightmare's hunting) is theirs; the leash and caps
  bound tower fights around them, but I could not watch them in a game.
* Balance against Antarchy's equipment is untested.

## Roadmap

1. **Milestone 1 (this)**: dimension, travel, one region, the three-floor tower, bounded fights, one rivalry, one reward,
   limits, debug commands.
2. **Regions and towers**: floating landforms, two more regions with their own creature communities and landmarks, medium and
   rare enormous tower variants, a custom sky with an eerie night.
3. **Creatures and nests**: three original creatures (a charging ground insect, a swooping flying predator with a telegraph,
   a nest guardian miniboss) with their own models, sounds, drops and weaknesses; nests with clues, optional fights, loot
   and limited reinforcements; more rivalries (nest defenders against intruders).
4. **Equipment and progression**: movement gear, more weapons with abilities, rare treasures, trophy unlocks, a harder
   region and a major challenge.
5. **Optional integrations**: superhero and Transformers mods, only after checking their real item ids. Disabled
   automatically when they are absent. Encounters account for flight with ranged threats and objectives, not by turning
   powers off.
6. **Polish**: sounds, particles, music, visuals.
