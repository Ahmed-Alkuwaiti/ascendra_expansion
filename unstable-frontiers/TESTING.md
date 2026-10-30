# Test report — Unstable Frontiers 0.6.0-rc1

Everything below comes from automated runs on GitHub Actions (Ubuntu, Java 21). Nobody has played it: "pass" means a
scripted check passed, not that a fight feels right. The in-game screenshots come from a scripted client (section 4), not
from play.

There are four kinds of check, reported separately.

## 0.6.0: the Drowned Expanse

Same pack server (138 of Integrated Boogaloo 1.0.8's jars, its configs and KubeJS scripts) with `debug/DrownedTrial.java`
added. **Result: all 113 checks pass (the 78 from 0.5.0 and 35 new), runs 41019501430 and 41019667244.** Real numbers from those runs:

| Area | What was checked | Result |
|---|---|---|
| Sunken Gate | generates naturally in the frontier (`frontier locate sunken`) | pass |
| Tide gate | without goggles and a rig it stays shut and the diver stays where they stood; goggles alone are refused; goggles and a rig pass | pass |
| The sea | water up to y 299 with air above and a solid floor under five sampled columns (shallows, kelpwood, reach, trench) | pass |
| Places | all five build over their pads: Tidewatch (origin −20, 259, −20), Deepwork (−355, 193, 125), Choir (272, 155, −278), wreck (−178, 108, −588), vault (53, 27, −837) | pass |
| | arrivals stand on a dry floor inside Tidewatch's dome (0, 269, 1); the dome's return gate is there; every place has its bell; the vault's dome is flooded at the arena's middle; no hostile natural spawns inside a place | pass |
| | Deepwork's pump-hall ambush starts with creatures | pass |
| Rig | 180 s (deep rig 420 s), cannot overfill; below y 100 a plain rig drains ×3, a deep rig ×1; a vent refills through open water but not through rock; water breathing from elsewhere takes over; a black-out returns the diver to their shelter, at most once a minute | pass |
| Murkjaw | 75 health after the pack's scaling; swims in open water; the jaw tell comes before the lunge; an undodged lunge hits (28.8); a dodged lunge into a wall stuns it and it then takes 8 from a hit that deals 4 | pass |
| Lanternray | fed glow berries it leads toward the nearest uncharted place (12 blocks closer in 59 ticks); struck, it stops leading and flees | pass |
| Deepcaller | the bell wakes it (1500 health after the pack's scaling, armour 10); it cannot be hurt while rising; one at a time | pass |
| | phase one: lure flash, charge and vortex, each told first (the stand-in lost 83); it keeps to its dome | pass |
| | phase two at half health with a roar; its brood (2 alive, cap 3, 45 health each); a charge that misses into the dome wall stuns it: 20 from a hit that deals 10 | pass |
| | its phase, dome and brood survive a save and load; an orphan Deepcaller is refused; with nobody in the vault for 30 s it resets and its brood goes; the bell calls it again at full health | pass |
| | victory: 2 Abyssal Pearls and the Undertow owed to a fighter who is away; a second victory pays pearls but no second Undertow | pass |

**Bugs these runs found, fixed in this release:**
* *The arrival dome flooded.* Placing a template keeps the sea that stood there, so it waterlogged the gate, sign and bell
  inside Tidewatch's dome, and they poured water into it (the trial found flowing water at the arrival point). The places
  now set those blocks back to their dry template state in the same tick. The template generator also refuses any build
  where air would touch water from the side or above.
* *Winning a place's fight charted nothing.* The three fights were not marked as their places' final fights. Fixed.
* *The trials' own races:* a creature that began its tell in the step before the one watching for it was reported as
  attacking without one (Murkjaw, and once the 0.5 Lumen Mite). The creatures only attack from their tell state; the
  trials now count an earlier tell.

**Client screenshots** (`docs/screenshots/ingame/drowned/`), the whole pack's client, software rendering, no shaders,
no night vision: the Sunken Gate; the gate refusing a diver without gear (the chat shows what it wants, and the
"Sunken Stair" advancement fired); with goggles and a rig worn, the walk into the gate and arrival in Tidewatch's dry
dome (so the gate travel ran for real); the station, the moon pool from below, the routes and kelpwood, Deepwork's pump
hall and diving bell, the Choir Temple's nave and rose window, the wreck, the trench and the vault; the creatures posed;
the Deepcaller woken in the vault with its boss bar.

**Not tested in 0.6.0:** a person diving (how far a swim feels, whether the fog is pleasant on your screen); the rig's
drain on a real player under water (the trials check the rules it follows; a fake player cannot swim); Curios slots in
the real client (the gear was worn in armour slots in the screenshots; the Curios tags and slot file load without
errors, but equipping through the Curios screen was not scripted); Swim Fins, Deep-Sight glow, the Undertow and the Breath
Charm in someone's hands; tide-bell travel and the echo sounder in use; two real players; Alex's Caves' own diving gear
worn together with this rig (both mods are in the pack; no conflict is expected since the rig only tops up air while worn,
but it was not tried); frame rate on your PC.

## 0.5.0: the Rift Observatory and the Astral Abyss

Same pack server as sections 2 and 3 (138 of Integrated Boogaloo 1.0.8's jars, its configs and KubeJS scripts), with
`debug/AbyssTrial.java` added to the trials. **Result of the last run: all 78 checks pass (the 40 from 0.4.0 and 38 new), run 40931695160.** Real numbers from that run:

| Area | What was checked | Result |
|---|---|---|
| Observatory | generates naturally (nearest from two points: 471 and 388 blocks); builds; the gatehouse ambush, the Hall's waves and the Vaults' brood start with creatures | pass |
| | the Lens Dome is sealed at first; clearing the Hall and the Vaults unseals it; its guardian then spawns | pass |
| | the engine takes the three parts in any order and wakes; the gate beside it was closed and is now open; the lift unseals; a woken engine takes no more parts | pass |
| Abyss | all five places build on their islands, each with safe ground found (landing 0,102,5; Starwell 232,95,−148; Archive −224,124,−72; Tether Spire 68,98,268; Crown 24,114,560) | pass |
| | arrivals stand on solid ground; the landing's return gate is open; the Crown's floor is solid at its middle | pass |
| | a fall into the void is caught: back on safe ground for a fifth of max health (4 of 20); on 1 health the catch does not kill | pass |
| | an item dropped into the void is moved to safe ground at the nearest place | pass |
| | no natural spawns on the landing; the Starwell's waves start with creatures | pass |
| Orrery Warden | 150 health, armour 8 after the pack's scaling; ring tell before the beam; the beam hits in the open (12); it stalls after and takes 20 from a 10 hit; cover taken during the tell stops the beam | pass |
| Lumen Mite | 25 health; stays aloft; swells before it spits; its bolts are gone within 3 s | pass |
| Eclipse Leviathan | the altar takes the sigil and it rises (1750 health, armour 12 after scaling); it cannot be hurt while rising; a second call while it is awake does nothing | pass |
| | phase one: beam, low pass and gravity wells, each told first; it stays inside the arena (9.4 blocks from the middle at the check) | pass |
| | phase two at two thirds with a roar; calls mites (2 alive, cap 4) | pass |
| | phase three: the eclipse dive leaves it exposed, 20 from a 10 hit | pass |
| | its phase, arena and mites survive a save and load; a Leviathan with no fight to belong to is refused | pass |
| | with nobody in the arena for 30 s the fight resets: boss and mites removed, altar charged; the charged altar calls it again without a sigil, at full health | pass |
| | victory: Eclipse Scales, Starmetal and the Corona are owed to a fighter who is away, kept until they log in | pass |

**A bug these trials found and that is fixed in this release:** the first run showed the altar taking the sigil while no
Leviathan appeared. The check that refuses a Leviathan with no fight was running before the fight recorded its boss, so it
refused the fight's own Leviathan. The fight now records the boss first.

**Client screenshots** (`docs/screenshots/ingame/abyss/`), scripted with the whole pack's client: the observatory from
outside and inside, the engine restored, then the player walks into the gate and arrives in the Abyss. The "Through the
Rift" advancement fired, so the gate travel ran for real. Then the Abyss's sky and places, the creatures posed, and the
Leviathan called at the Hollow Crown. Software rendering, no shaders.

**Not tested in 0.5.0:** a person playing the fights (timing, feel); the Blinkstone, Corona beam and tiers, Astrolabe
guidance and updraft vents in someone's hands; two real players (health scaling and shared rewards are code paths the
trials touch only with one stand-in); sounds by ear; frame rate and tick time on your PC; how Antarchy's elite abilities
behave in the observatory; how often you meet an observatory across many worlds (the locate run measures two distances in one world: the nearest observatory was 471 and 388 blocks away).

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

**Result of the last run (40871127131): all 21 trial checks pass, and all 19 landmark checks of section 2.**

| Trial step | Result |
|---|---|
| Matriarch waits in her chains before the fight (1750 health after the pack's scaling); she cannot be hurt then | pass |
| The key wakes the same Matriarch, chained; chained she takes 7 of a 20 hit | pass |
| Scythe sweep: tell, then strike | pass |
| Acid volley at mid range: tell, globs, poison puddles | pass |
| Brood call: the open sac takes 30 of a 20 hit even while chained; escorts arrive (6 creatures in the fight) | pass |
| Breaking the pylons snaps the chains (roar); free, she takes 20 of 20 | pass |
| Leap: crouch with landing ring, then the jump (landed 3.7 blocks from the target's spot) | pass |
| Killing her clears the Great Cage and opens its gates | pass |
| Gnashback tells its charge; a charge dodged late in the tell runs into the wall and stuns it | pass |
| The stunned Gnashback takes 20 from a hit that deals 10 normally; an undodged charge hits for 33.6 | pass |
| Shrikewing stays aloft; screeches and marks the spot before diving | pass |
| A dodged dive leaves it climbing and open; an undodged dive hits | pass |

**What the trials found and changed** (earlier runs):
* The Gnashback re-aimed at its target until the very last tick of its tell, so stepping aside during the tell did not
  work. It now fixes its line half a second before running.
* After a sweep, the Matriarch walked back into scythe range during her cooldown, so her acid was almost never used
  against someone standing a few blocks off. She now holds her ground at mid range and spits; she only walks after
  prey more than 12 blocks away.
* Health was set from these runs: the pack multiplied the Matriarch's base health by 2.5 (900 → 2250, too much next to
  the Hive Tyrant's 1625), so her base is now 700 (1750 measured).

**Measured numbers** (from `/frontier debug dump`, after the pack's scaling, Normal difficulty):

* Antarchy creatures (health / attack): wasp 40/8, scorpion 75/10, stratoshark 100/10, mantis 125/18, manticore 150/22,
  springbug 250/24, basilisk 800/72, alpha mantis 950/36, nightmare 950/32, emperor scorpion 1050/56, toreterror 1125/16,
  brutalfly 1250/30, Hercules beetle 1625/60, king 8500/150, queen 10750/90. Red ants and termites are passive (12.5).
* Antarchy weapons: Nightmare Sword 50, Ultimate Sword 100, Royal Guardian Sword 500 attack damage.
* This addon's Swarmbreaker: 40 (1 base + 39). It was 8 before this run; the numbers above are why it changed.
* This addon's creatures (last run): Gnashback 275 / 24, Shrikewing 150 / 28, Chained Matriarch 1750 / 40. The pack
  multiplied health by 2.5 and attack by 2 in every run but one, where a Shrikewing read 5× health, so the pack's
  scaling is not always the same factor.

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
