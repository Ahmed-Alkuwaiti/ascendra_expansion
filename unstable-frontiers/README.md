# Unstable Frontiers 0.3.0 — an adventure expansion for Integrated Boogaloo

**Target: [Integrated Boogaloo](https://www.curseforge.com/minecraft/modpacks/integrated-boogaloo) 1.0.8** (CurseForge
project 1501592, file 9325863): Minecraft 1.21.1, NeoForge 21.1.264, with the pack's
**Antarchy 2.2.9+1.21.1** (required). The addon is built against exactly that NeoForge version and was tested against the
pack's own jars, configs and KubeJS server scripts (see [Testing](#testing-what-was-checked-and-what-was-not)).

It adds the **Unstable Frontier**: a wilderness the Cagewright once fenced in to hold Antarchy's monsters. You enter with a
Rift Shard, follow a surveyor's journals from camp to camp, break open cages, rookeries and hives for the three parts of
the Cagewright's Key, and use it on the **Great Cage** in the Rustbone Scar.

All structure pictures in this repository are **renders of the actual template files the game places**, drawn by
`tools/structures/view.py`. They are not in-game screenshots.

---

## Install

1. Install Integrated Boogaloo **1.0.8** from CurseForge (or use your existing instance of that version).
2. Put `unstable_frontiers-0.3.0.jar` in the instance's `mods` folder. Nothing else is needed: Antarchy is in the pack.
3. Start the game. In a world, craft an **Unstable Rift Shard** (amethyst shards in the corners, crying obsidian on the
   sides, an eye of ender in the middle) and use it.

If Antarchy is missing or too old, NeoForge stops at the loading screen and names it. If a datapack breaks a roster (or a
future Antarchy renames a creature), the affected fight refuses to start and says which creature is missing, in chat and in
`latest.log`; operators are told on login. The addon never swaps in other creatures.

Existing worlds: the frontier is generated fresh the first time you enter it, so an existing Integrated Boogaloo world is
fine. Only frontier chunks you have not visited get the new landmarks.

## The adventure

### Regions

| Region | Look | What you find there |
|---|---|---|
| **Gnashwood Wilds** | dark choked forest, blood-red leaves, falling ash | Gibbet Spires, Brood Hives, Carrion Fields, camps |
| **Hushed Barrens** | grey, sparse, quiet | Gibbet Spires, the Hanging Gaol, Carrion Fields, camps |
| **Talon Spires** | pale sky, hooked rock needles, floating islets | Rookeries, Carrion Fields, camps |
| **Rustbone Scar** | red ground, bleached rib arches, crimson spores | the Great Cage (only here) |

Terrain is standard overworld-style noise (hills, mountains, rivers, some sea). Earlier versions used amplified terrain,
which left no room for the large landmarks.

### Landmarks

| Landmark | Size | The fight | Reward |
|---|---|---|---|
| **Gibbet Spire** ([render](docs/renders/gibbet_spire.png)) | 47×100×47 | an octagonal birdcage spire: waves in the Swarm Pen, a Hatchery whose waves come from its egg clutches, an Aerie ambush from the hanging gibbets, and the **Crowned Mantis** (Antarchy alpha mantis) in the crown | Cage Trophy; the crown vault opens |
| **Hanging Gaol** ([render](docs/renders/hanging_gaol.png)) | 65×82×49 | five cells hung over a pit on chains and rope bridges. Each prisoner (Hercules beetle, wasps, emperor scorpion, brutalfly…) is visible and dormant until you step aboard. Free four cells to unseal **the Gaoler** (manticore) | Cage Trophy; the warden's vault |
| **Rookery** ([render](docs/renders/rookery.png)) | 55×104×55 | a leaning white crag with a nest of whole trees on top. Stratosharks roost on the perches, asleep until you land in the nest or strike one. Clear the roost and **the Rookmother** (Antarchy nightmare) comes in from the sky. Scavengers wait in the tunnel | Rookery Talon |
| **Brood Hive** ([render](docs/renders/brood_hive.png)) | 61×54×61 | a mud-and-chitin mound: an ambush in the hall, a brood chamber that keeps hatching while its clutches stand, and **the Hive Tyrant** (Hercules beetle) on a chitin throne. The resin wall behind it opens when it dies | Hive Heart |
| **Carrion Field** ([render](docs/renders/carrion_field.png)) | 67×34×41 | not a fight you start: a giant's skeleton still being eaten. Insects live in the ribs, predators on the spine, and they fight each other whether or not you are there | the gullet's chest |
| **Expedition camps** (3 kinds) ([render](docs/renders/camp_torn.png)) | 29×16×29 | Ilsa Vane's camps: intact, ransacked from below, torn open from above. Each has a different journal on its lectern | supplies; the Rift Lens (60%) |
| **Waysides** (4 kinds) ([render](docs/renders/wayside_impaled.png)) | ≤11 wide | a fallen gibbet, an impaled carcass, an egg cluster, a claw-raked stone: small marks between the big landmarks | — |
| **The Great Cage** ([render](docs/renders/great_cage.png), [cutaway](docs/renders/great_cage_section.png)) | 115×100×115 | a ring-walled prison with drum towers, eight cell blocks and a domed birdcage. The Cagewright's Key opens the lock by the south door and wakes **the Cagewright's Beast** (Antarchy basilisk). While its four pylons stand it takes only a sixth of the damage; the pylon cores break quickly once the fight is on, and every one that falls brings flyers down from the dome | Heart of the Great Cage; the vault below |

### How fights behave

* **Situated, not spawned around you.** Prisoners, roosting flyers and residents are already in their places when you
  arrive. A fight only starts when you enter its part of the landmark (or strike one of its creatures).
* **Bounded.** No constant spawning: every fight has a fixed number of waves, and residents that are all killed move back
  in only after a Minecraft day. Creature health and damage are each creature's own; nothing is inflated. Integrated
  Boogaloo's own difficulty scaling (Boogaloo Core's KubeJS MobScaling) applies to these creatures as it does to any spawn.
* **Telegraphed elites.** Guardians have a boss bar and abilities that are always announced first: a ring drawn on the
  ground before a **slam**, a call before a **rally**, a crouch before a **pounce**, a breath before a **screech**
  (slowness and darkness). Each can be avoided by reacting.
* **Leave and it resets.** A fight nobody is near for 20 seconds resets; its creatures leave and you can try again.
  Cleared parts stay cleared.
* **Per-player loot.** Chests use loot tables, which Lootr (in the pack) turns into per-player chests. Trophies are given
  once per player per landmark, to everyone who fought in it.
* **Drops only from your kills.** A frontier creature drops loot and experience only if a player hurt it, so creatures
  killing each other never pile up items.

### Rewards and how they connect to the pack

The rewards are built around Antarchy's own progression rather than bigger numbers.

| Item | Where from | Use |
|---|---|---|
| **Cage Trophy** | Gibbet Spire, Hanging Gaol guardians | key part; repairs the Swarmbreaker |
| **Rookery Talon** | the Rookmother | key part; forges and repairs the Shackle |
| **Hive Heart** | the Hive Tyrant | key part; forges the Swarmbreaker |
| **Cagewright's Key** | trophy + talon + heart + Antarchy uranium ingot + tripwire hook | opens the Great Cage |
| **Heart of the Great Cage** | the Cagewright's Beast | builds a Cage Beacon |
| **Rift Lens** | camps (60%), or spyglass + amethyst + Antarchy chitin | in the frontier: names the nearest cage, lair and camp with distance, direction and whether you have conquered it; shows the Great Cage once you carry the key |
| **Swarmbreaker** | Hive Heart + 2 Antarchy mantis claws + netherite sword | brood-breaker glaive (Better Combat glaive moves in the pack). Hits like a netherite sword; +50% vs insects; Pounce lands in a shockwave that smashes egg clutches (ending a hatchery's waves sooner) and staggers insects. It is a crowd and nest tool, not a replacement for Antarchy's Ultimate or Big Bertha weapons |
| **Cagewright's Shackle** | Rookery Talon + chains + lead | binds a hostile creature below a third of its health as an ally for 60 s; it then crumbles with no drops. Not on bosses (`c:bosses`, Antarchy's spell-resistant bosses) or elites. 6 uses |
| **Cage Beacon** | Heart of the Great Cage + crying obsidian + iron bars | safe ground: no natural frontier spawns within 48 blocks and residents do not return there; anchors your Rift Shard so you arrive beside it |

**Antarchy materials as bounties.** Landmark chests and creatures yield what Antarchy's own recipes need: mantis claws,
springbug legs, stratoshark fins, brutalfly wings (Brutalfly Elytra), nightmare scales, emperor scorpion stingers and
Hercules horns (Big Bertha parts), basilisk fangs, primordial scutes, uranium and titanium nuggets and ingots (Ultimate
gear). The Gaol's cells are where to hunt for specific Big Bertha creatures.

**Superheroes.** The Hulk serum in Marvel Superheroes wants Antarchy uranium; the Great Cage vault always holds uranium
ingots, and when Marvel Superheroes is installed it has a 35% chance of an X-Gene (`marvel:x_genes`) for the serums. That
entry lives in a loot table that only loads when that mod is present.

**Flight, powers and transformations.** Nothing in the addon disables flight (Viltrumite Flight, Brutalfly Elytra,
Manticore Wings) or powers. Flying past a climb does not skip a fight: sealed parts open only when the parts before them
are cleared, and gates and vaults open only when their fight is won. Flyers in the Aerie, the roost and the Great Cage
dome make the sky part of the fight.

### Commands

* `/frontier return` — everyone, in the frontier: go home (60 s cooldown). For when your shard is lost.
* Operators: `/frontier go`, `/frontier locate <any|cage|lair|camp|great_cage>`, `/frontier stats`,
  `/frontier landmark build <id> [rotation]`, `/frontier landmark info`, `/frontier landmark zone <zone> start|clear|reset`,
  `/frontier landmark forget`, `/frontier debug rosters`, `/frontier debug dump <namespace>`.

## Performance

`config/unstable_frontiers-common.toml`. The limits protect the **server thread** (in single player, the integrated
server on your CPU); your GPU is not what they affect.

| Limit | CONSERVATIVE | **STANDARD** | HIGH_DENSITY |
|---|---|---|---|
| Landmark creatures alive per player / per landmark | 6 / 10 | 10 / 16 | 16 / 28 |
| Fights running at once (server) | 2 | 3 | 6 |
| Waves in a wave fight (unless the landmark sets its own) | 2 | 3 | 4 |
| Creatures per wave | 3 | 5 | 8 |
| Ticks between waves | 300 | 200 | 140 |
| Residents per landmark | 4 | 6 | 10 |
| Night overflight interval (ticks) | 12000 | 6000 | 3600 |
| Rivalry search radius / update interval / fights per player | 16 / 60 / 1 | 24 / 40 / 2 | 32 / 20 / 4 |
| Particle multiplier | 0.4 | 1.0 | 1.0 |

**For your machine (32 GB RAM, Radeon RX 6650 XT, Core i3-12100-series):** use **STANDARD** (the default). The i3-12100 has
four cores, and Integrated Boogaloo's 174 mods already load the server thread; HIGH_DENSITY is meant for 6+ cores. Give
Minecraft 8–10 GB in the launcher (more than that does not help and lengthens garbage-collection pauses). If you see lag
during the Great Cage fight, set `simultaneousEncounters = 1` and `particleDensity = 0.5` rather than switching preset.

The addon's cost when nothing is fighting: one structure-reference lookup per player every 2 seconds and a short loop over
known landmarks every half second. It never scans the world: every search is a box around one landmark or one player.

## Testing: what was checked and what was not

See [TESTING.md](TESTING.md) for the full report from the last CI runs. In short:

* **Standalone checks** (no pack): data cross-references, compile, and "without Antarchy the server refuses to start and
  names Antarchy".
* **Pack checks** (Integrated Boogaloo 1.0.8's own jars for Antarchy, Integrated Superheroes, Marvel, Morph, Boogaloo Core,
  Electric Boogaloo, KubeJS, Lootr, Curios, Better Combat, Witchery and their dependencies, plus the pack's configs and
  KubeJS server scripts) on a dedicated server: every roster resolves, every landmark builds, every kind of fight starts
  with real Antarchy creatures, gates open, and the landmarks generate naturally.
* **Not tested**: the game client (I cannot run one), the full 174-mod pack at once, and actual play. How Antarchy's
  creatures move and fight inside these structures has not been watched by a person.

## Building from source

```
cd unstable-frontiers
python3 tools/structures/<landmark>.py    # regenerate a template + its sidecar (needs nbtlib, Pillow)
python3 tools/datagen.py                  # rosters, worldgen, loot, recipes, advancements, lang, sounds
python3 tools/textures.py                 # item and block textures
python3 tools/check_data.py               # standalone data checks
gradle build                              # Java 21, Gradle 8.10.2
```

The jar is `build/libs/unstable_frontiers-0.3.0.jar`.

## Licence and credits

Original code, structures, textures and writing. Antarchy (All Rights Reserved) is referenced by id only: no Antarchy code
or assets are included. Sounds are vanilla sound events played through this mod's own sound definitions.
