# Test report — Unstable Frontiers 0.4.0-rc1

Everything below comes from automated runs on GitHub Actions (Ubuntu, Java 21). Nobody has played it: "pass" means a
scripted check passed, not that a fight feels right. The in-game screenshots come from a scripted client (section 4), not
from play.

There are four kinds of check, reported separately.

## 1. Standalone checks (no Integrated Boogaloo)

Workflow `Build Unstable Frontiers` (`.github/workflows/unstable_frontiers.yml`), every push.

| Check | Result |
|---|---|
| `tools/check_data.py`: every JSON parses; every roster, chest loot table, reward item, gate, required zone and template a landmark names exists; spawn points lie in their zones; every item has a model and texture; every translation key the code uses and every sound event exists | **pass** (19 rosters, 20 loot tables, 19 items, 0 problems) |
| …and for the creatures: every entity has its model, animation file, texture, name and loot table; every animation the code plays exists in its animation file; every sound file `sounds.json` names exists; the armour layers exist | **pass** |
| Compile against NeoForge 21.1.264 (the version Integrated Boogaloo 1.0.8 ships) and GeckoLib 4.9.3 (the pack's own jar in the pack runs, the same version from GeckoLib's Maven otherwise) | **pass** |
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

## 3. Creature trials (Integrated Boogaloo 1.0.8 server)

Same server as section 2. `/frontier debug trial <creature>` (`debug/CreatureTrial.java`) plays each fight against a
motionless iron golem standing in for the player, moving it the way a player would dodge, and logs each step.

| Trial step | Result (run 40866196539) |
|---|---|
| Matriarch waits in her chains before the fight; she cannot be hurt then | pass |
| The key wakes the same Matriarch, chained; chained she takes 7 of a 20 hit | pass |
| Scythe sweep: tell, then strike | pass |
| Acid volley: tell, globs, poison puddles | pass |
| Brood call: the open sac takes 30 of a 20 hit even while chained; escorts arrive (6 creatures in the fight) | pass |
| Breaking the pylons snaps the chains (roar); free, she takes 20 of 20 | pass |
| Leap: crouch with landing ring, then the jump (landed 4.3 blocks from the target's spot) | pass |
| Killing her clears the Great Cage and opens its gates | pass |
| Shrikewing stays aloft; screeches and marks the spot before diving | pass |
| A dodged dive leaves it climbing and open; an undodged dive hits (28) | pass |
| Gnashback tells its charge; an undodged charge hits (24) | pass |
| A dodged charge into a wall stuns the Gnashback; its stunned back takes double | **failed in that run**: it re-aimed at the target until the very end of the tell, so stepping aside during the tell did not work. Fixed (it now fixes its line half a second before running); see the result of the following run below |

**Measured numbers** (from `/frontier debug dump`, after the pack's scaling, Normal difficulty):

* Antarchy creatures (health / attack): wasp 40/8, scorpion 75/10, stratoshark 100/10, mantis 125/18, manticore 150/22,
  springbug 250/24, basilisk 800/72, alpha mantis 950/36, nightmare 950/32, emperor scorpion 1050/56, toreterror 1125/16,
  brutalfly 1250/30, Hercules beetle 1625/60, king 8500/150, queen 10750/90. Red ants and termites are passive (12.5).
* Antarchy weapons: Nightmare Sword 50, Ultimate Sword 100, Royal Guardian Sword 500 attack damage.
* This addon's Swarmbreaker: 40 (1 base + 39). It was 8 before this run; the numbers above are why it changed.
* This addon's creatures: the pack multiplied health by 2.5 and attack by 2 in every run here (Gnashback 110 → 275,
  attack 12 → 24; Matriarch 700 base). One earlier dump read a Shrikewing at 5× health, so the pack's scaling is not
  always the same factor; the base values were set from these measurements.

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

## 4. Client screenshots (Integrated Boogaloo 1.0.8 client)

Workflow `Integrated Boogaloo client screenshots` (`.github/workflows/pack_client.yml`, `ci/pack_client.sh`). A pack
server builds the Great Cage into a world; then the **full client with all of the pack's jars** opens that world under a
virtual display with software OpenGL (Mesa llvmpipe) and plays `ci/client_shots.txt`: teleports, summons, poses
(`/frontier debug pose`), and screenshots. The pictures are committed to `docs/screenshots/ingame/`.

They show what GeckoLib renders from the models and textures, in the real pack. They are not representative of frame rate
or of how the game looks on your GPU (no shaders, software rendering), and creatures in "pose" shots have their AI off.

## What these tests do not cover

* **Sound**: the sounds were checked as spectrograms and load without errors; nobody has listened to them in game.
* **Real play**: no person has fought these fights. The trials prove the mechanics (tells come first, dodges work, openings
  take the damage promised), not that the timing feels fair with a mouse and keyboard and 150 ms of latency. The Antarchy
  elites' abilities (slam, rally, pounce, screech) only fire near real players and remain untested in game, as do the
  Shackle, the Carapace set bonus, the Impaler's anti-air bonus and the Mantle's glide and truce.
* **How Antarchy's creatures behave inside the structures**: whether flyers get stuck under the Spire's cages, whether the
  emperor scorpion fits its cell, whether the basilisk paths around the Great Cage plinth. None of that has been watched.
* **Mods that act on spawns**: Infernal Mobs may give landmark creatures extra modifiers. That is not tested either way.
* **Lootr**: chests use loot tables, which Lootr converts, but per-player opening was not exercised.
* **Multiplayer**, and **performance on your PC**: the CI server is not your i3-12100, and the test does not measure tick
  times. Rewards are given once per player per landmark (by UUID, saved with the world), so two players each get theirs
  and nobody can claim twice, but that has not been exercised with two real clients.
