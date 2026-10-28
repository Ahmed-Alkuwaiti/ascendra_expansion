# Test report — Unstable Frontiers 0.3.0

Everything below comes from automated runs on GitHub Actions (Ubuntu, Java 21). I cannot run the Minecraft client, so
nothing here was seen on screen or played by a person. "Pass" means the check in the script passed, not that the fight
feels right.

There are two kinds of check, reported separately as asked.

## 1. Standalone checks (no Integrated Boogaloo)

Workflow `Build Unstable Frontiers` (`.github/workflows/unstable_frontiers.yml`), every push.

| Check | Result |
|---|---|
| `tools/check_data.py`: every JSON parses; every roster, chest loot table, reward item, gate, required zone and template a landmark names exists; spawn points lie in their zones; every item has a model and texture; every translation key the code uses and every sound event exists | **pass** (19 rosters, 17 loot tables, 10 items, 0 problems) |
| Compile against NeoForge 21.1.264 (the version Integrated Boogaloo 1.0.8 ships) | **pass** |
| Boot a dedicated server with only this addon: NeoForge must refuse and name Antarchy (the actionable error; no vanilla stand-ins) | **pass** |

## 2. Pack checks (Integrated Boogaloo 1.0.8)

Workflow `Integrated Boogaloo server test` (`.github/workflows/pack_server.yml`, `ci/pack_server.sh`).

**What runs:** the pack's real files, downloaded from CurseForge's CDN by `ci/pack/fetch_pack.py` from the pack's manifest
(project 1501592, file 9325863). The server loads **138 of the pack's 165 jars**: every jar except 27 client-only mods
(Sodium, Iris, shaders, menus, tooltips, loading screens, Better Clouds, Enhanced Block Entities, damage indicators and
similar; listed in the run's `pack_selection.txt`). These refuse to load on a dedicated server, and they do not touch
gameplay. It also loads the pack's `config`, `defaultconfigs` and the whole `kubejs` folder (including Boogaloo Core's
MobScaling scripts). It is a dedicated server, not the single-player client, at Normal difficulty.

**Result of the last run: 19 of 19 checks pass.**

| Check | Result |
|---|---|
| Server boots with the pack and runs the whole test script | pass |
| Antarchy 2.2.9 loads with the addon | pass |
| All 19 rosters resolve against the installed Antarchy (no missing creature) | pass |
| The addon reports no data-load problems | pass |
| Gibbet Spire builds; its wave floor spawns creatures (5); its crown guardian spawns with escorts (3) | pass |
| Clearing the crown opens its gate (`gates open [crown]`) | pass |
| Hanging Gaol: a cell prisoner spawns (emperor scorpion); the Gaoler spawns with escorts | pass |
| Rookery: the roost spawns (9: ground and perched flyers); the Rookmother spawns | pass |
| Brood Hive: the brood counts its clutches and spawns its first wave (4 waves left); the Hive Tyrant spawns | pass |
| Great Cage: opening the lock removes the lock gate; the finale spawns the beast and escorts | pass |
| Landmarks generate naturally in a fresh frontier: camps, any landmark, the Great Cage | pass |

**Measured numbers** (from `/frontier debug dump`, after the pack's scaling, Normal difficulty):

* Antarchy creatures (health / attack): wasp 40/8, scorpion 75/10, stratoshark 100/10, mantis 125/18, manticore 150/22,
  springbug 250/24, basilisk 800/72, alpha mantis 950/36, nightmare 950/32, emperor scorpion 1050/56, toreterror 1125/16,
  brutalfly 1250/30, Hercules beetle 1625/60, king 8500/150, queen 10750/90. Red ants and termites are passive (12.5).
* Antarchy weapons: Nightmare Sword 50, Ultimate Sword 100, Royal Guardian Sword 500 attack damage.
* This addon's Swarmbreaker: 40 (1 base + 39). It was 8 before this run; the numbers above are why it changed.

These numbers changed the design: the Gaol's warden had been a manticore (150) guarding a Hercules beetle (1625); the
cells now hold mid-tier prisoners and the Gaoler is the brutalfly. Elite slams now scale from the elite's own attack.

**Landmark density** (fresh world, seed `frontiers`). The first runs found the nearest landmark 166–800 blocks away;
`/frontier debug sites` showed that two thirds of all candidate sites were rejected for standing in water. The frontier now
uses vanilla's overworld terrain with the sea drained (`worldgen/noise_settings/frontier.json`, derived from the game's own
file), and the last run measured:

| | |
|---|---|
| Nearest landmark of any kind, from four points 3000 blocks out | 17, 17, 43 and 58 blocks |
| Nearest expedition camp, from two points | 281 and 370 blocks |
| Nearest Great Cage, from (0, 3000) | 2239 blocks |
| Candidate sites rejected for water / slope / height | 0 / 25–57% (small waysides on rough ground) / 0 |

**Errors in the log that are not this addon's:** four pack recipes fail to parse (Pastel's waystones pedestal recipe, a
Create Cybernetics recipe, two Infinity Gauntlet smithing recipes) and Moonlight skips two Quark colour sets. They appear
with or without this addon.

## What these tests do not cover

* **The client**: models, textures, sounds, particles, titles, boss bars and the in-game look of the structures are not
  rendered by any test. Textures and structure renders were drawn and checked as images; see `docs/renders`.
* **Real play**: no person has fought these fights. In the test, fights are started by command with a stand-in fake player.
  Creatures spawn and the zone states change as they should, but elite abilities only fire near real players, so slams,
  rallies, pounces and screeches are untested in game, as are the pylon shield and the Shackle.
* **How Antarchy's creatures behave inside the structures**: whether flyers get stuck under the Spire's cages, whether the
  emperor scorpion fits its cell, whether the basilisk paths around the Great Cage plinth. None of that has been watched.
* **Mods that act on spawns**: Infernal Mobs may give landmark creatures extra modifiers. That is not tested either way.
* **Lootr**: chests use loot tables, which Lootr converts, but per-player opening was not exercised.
* **Multiplayer**, and **performance on your PC**: the CI server is not your i3-12100, and the test does not measure tick
  times.
