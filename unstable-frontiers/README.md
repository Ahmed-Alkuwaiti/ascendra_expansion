# Unstable Frontiers 0.5.0-rc1 — an adventure expansion for Integrated Boogaloo

**Target: [Integrated Boogaloo](https://www.curseforge.com/minecraft/modpacks/integrated-boogaloo) 1.0.8** (CurseForge
project 1501592, file 9325863): Minecraft 1.21.1, NeoForge 21.1.264, with the pack's
**Antarchy 2.2.9+1.21.1** and **GeckoLib 4.9.3** (both required, both already in the pack). The addon is built against exactly that NeoForge version and was tested against the
pack's own jars, configs and KubeJS server scripts (see [Testing](#testing-what-was-checked-and-what-was-not)).

It adds the **Unstable Frontier**: a wilderness the Cagewright once fenced in to hold Antarchy's monsters. You enter with a
Rift Shard, follow a surveyor's journals from camp to camp, break open cages, rookeries and hives for the three parts of
the Cagewright's Key, and use it on the **Great Cage** in the Rustbone Scar, where the **Chained Matriarch** waits.

0.4.0 adds the frontier's own animals, made for this addon: the **Gnashback** (a giant charging beetle), the **Shrikewing**
(a diving sky predator that hunts the insects below) and the **Chained Matriarch** (the Great Cage's boss), with their gear.

0.5.0 adds the **Rift Observatory**, a ruined observatory split by a cosmic rift, and through its restored engine the
**Astral Abyss**: a dimension of floating islands under a fixed night sky, five places to explore, and the **Eclipse
Leviathan** at the Hollow Crown. See [the Rift Observatory and the Astral Abyss](#the-rift-observatory-and-the-astral-abyss).

**About the pictures.** Three kinds, each labelled:
* `docs/screenshots/ingame/` (0.4.0) and `docs/screenshots/ingame/abyss/` (0.5.0) — **in-game screenshots** taken by CI from the real Integrated Boogaloo 1.0.8 client (all of
  its mods, software rendering under a virtual display, so no shaders and plain lighting). See
  [the client test](#testing-what-was-checked-and-what-was-not).
* `docs/renders/creature_*_model_sheet.png` — **model previews** drawn offline from the creature model files by
  `tools/models/render.py` (not the game's renderer).
* `docs/renders/<landmark>.png` — **structure renders** of the template files the game places, by `tools/structures/view.py`.

---

## Install

1. Install Integrated Boogaloo **1.0.8** from CurseForge (or use your existing instance of that version).
2. Download `unstable-frontiers/dist/unstable_frontiers-0.5.0-rc1.jar` from this branch (its SHA-256 is in the
   `.sha256` file next to it) and put it in the instance's `mods` folder. Nothing else is needed: Antarchy and GeckoLib
   are in the pack. Remove any older `unstable_frontiers-*.jar` first.
3. Start the game. In a world, craft an **Unstable Rift Shard** (amethyst shards in the corners, crying obsidian on the
   sides, an eye of ender in the middle) and use it.

If Antarchy or GeckoLib is missing or too old, NeoForge stops at the loading screen and names it. If a datapack breaks a roster (or a
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

Terrain is vanilla's overworld terrain with the sea drained: hills and mountains as usual, and where the overworld would
have oceans and rivers, dry basins and canyons. Earlier versions used amplified terrain (no room for the large landmarks),
and plain overworld terrain put two thirds of landmark sites under water. A landmark of some kind is now typically within
20–60 blocks, a camp within a few hundred, and the Great Cage a long journey (one run: about 2200 blocks).

### Landmarks

| Landmark | Size | The fight | Reward |
|---|---|---|---|
| **Gibbet Spire** ([render](docs/renders/gibbet_spire.png)) | 47×100×47 | an octagonal birdcage spire: waves in the Swarm Pen, a Hatchery whose waves come from its egg clutches, an Aerie ambush from the hanging gibbets, and the **Crowned Mantis** (Antarchy alpha mantis) in the crown | Cage Trophy; the crown vault opens |
| **Hanging Gaol** ([render](docs/renders/hanging_gaol.png)) | 65×82×49 | cells hung over a pit on chains and rope bridges. Each prisoner (a springbug and mantis, wasps, a manticore, an emperor scorpion) is visible and dormant until you step aboard. Free the four cells to unseal **the Gaoler** (Antarchy brutalfly) | Cage Trophy; the warden's vault |
| **Rookery** ([render](docs/renders/rookery.png)) | 55×104×55 | a leaning white crag with a nest of whole trees on top. Stratosharks roost on the perches, asleep until you land in the nest or strike one. Clear the roost and **the Rookmother** (Antarchy nightmare) comes in from the sky. Scavengers wait in the tunnel | Rookery Talon |
| **Brood Hive** ([render](docs/renders/brood_hive.png)) | 61×54×61 | a mud-and-chitin mound: an ambush in the hall, a brood chamber that keeps hatching while its clutches stand, and **the Hive Tyrant** (Hercules beetle) on a chitin throne. The resin wall behind it opens when it dies | Hive Heart |
| **Carrion Field** ([render](docs/renders/carrion_field.png)) | 67×34×41 | not a fight you start: a giant's skeleton still being eaten. Insects live in the ribs, predators on the spine, and they fight each other whether or not you are there | the gullet's chest |
| **Expedition camps** (3 kinds) ([render](docs/renders/camp_torn.png)) | 29×16×29 | Ilsa Vane's camps: intact, ransacked from below, torn open from above. Each has a different journal on its lectern | supplies; the Rift Lens (60%) |
| **Waysides** (4 kinds) ([render](docs/renders/wayside_impaled.png)) | ≤11 wide | a fallen gibbet, an impaled carcass, an egg cluster, a claw-raked stone: small marks between the big landmarks | — |
| **The Great Cage** ([render](docs/renders/great_cage.png), [cutaway](docs/renders/great_cage_section.png)) | 115×100×115 | a ring-walled prison with drum towers, eight cell blocks and a domed birdcage. **The Chained Matriarch** hangs in her chains in the middle, visible from the walls before anything starts. The Cagewright's Key at the lock by the south door wakes her (see [the boss](#the-chained-matriarch)) | Heart of the Great Cage and the Matriarch's Mantle (each fighter); the vault below |

### The frontier's own creatures

Original creatures made for this addon (models, textures, animations and sounds all made here; see
[how they were made](#how-the-creatures-were-made)). They belong together: the Shrikewing hunts what the Gnashback is, and
the Matriarch is what both came from.

| | The Gnashback | The Shrikewing | The Chained Matriarch |
|---|---|---|---|
| What | a giant beetle whose shell grew around old cage bars | a pale, hook-beaked flyer with ragged membrane wings | the brood queen the Cagewright shackled in the Great Cage |
| Where | Gnashwood Wilds, Hushed Barrens, Rustbone Scar; Gibbet Spire pens; Carrion Fields | Talon Spires, Rustbone Scar; rookery roosts, spire aeries, Carrion Fields, night overflights, the Great Cage dome | the Great Cage only |
| Behaviour | territorial: ignores you beyond ~10 blocks unless hit | circles high over its home ground, perches on high points, hunts players and (now and then) insects | waits in her chains; the key starts the fight |
| Its attack and tell | **Charge**: lowers its head, cracks its shell open and scrapes the ground twice (about 1.25 s, with a scraping sound and dust), then runs straight at where you stood. Close in, it bites | **Dive**: circles you, then hangs with wings raised and screeches while a ring marks the spot. The ring stops following you half way through the tell; then it dives | see below |
| Weakness | dodge the charge so it hits a wall or tree: stunned for 4 s with its back open, **double damage** | a missed dive leaves it climbing slowly (+50% damage) or, if it hits the ground, **grounded for 3 s (double damage)**. The Shrike Impaler knocks it out of the sky | the brood sac, and her chains |
| Measured in the pack | 275 health, 24 attack (charge ×1.4) | 150 health, 28 attack | 1750 health, 40 attack, armour 14 |
| Drops | 2–4 Gnashback Plates (+Looting), bug meat, chitin | 1–2 Shrike Talons (+Looting), phantom membrane, feathers | 6–10 plates, 2–3 talons, diamonds, netherite scrap |

Health and attack are after Integrated Boogaloo's own mob scaling (Boogaloo Core), read from a pack server by CI. The first
time each creature hunts you, a one-line hint in chat says how to fight it.

### The Chained Matriarch

The fight is decided by what you do, not by her health:

* **Chained** (while any of the four pylons stands): she is tethered within about 9 blocks of the middle of the cage and
  takes a **third** of the damage. Lines of light show which pylons hold her. Pylon cores break quickly during the fight,
  and each one that falls brings flyers (Shrikewings, stratosharks) down from the dome.
* **Scythe Sweep** — she rears with both scythes back and sparks trace a 120° arc in front of her (1.1 s). The arc is fixed
  when the tell ends: get behind her or out of reach (7 blocks).
* **Acid Volley** — at mid range she holds her ground; her sac swells and her head draws back (0.9 s), then three globs
  land around where you stand, each leaving a poison puddle for a few seconds. Keep moving, or close in (and face the
  scythes).
* **Brood Call** — the plates on her sac lift and it pulses for 3 s while young (from the cage's roster) climb out. She does
  not attack and the open sac takes **150% damage, even while chained**: this is the opening.
* **The chains snap** when the last pylon falls: she roars, takes full damage, moves faster and gains the **Leap**: she
  crouches while a ring of flame marks where she will land (fixed half a second before she jumps). Leave the ring; the
  landing throws back everything near it, and she pauses after it.

There is no enrage and no hidden phase: the only change in the fight is the one the players cause by breaking the chains.
Leave the cage for 20 s and the fight resets (she is back in her chains, at full health). Her own health bar shows how many
pylons still stand.

### Who you fight, and when to come

Numbers measured in Integrated Boogaloo 1.0.8 (Boogaloo Core's scaling applied, Normal difficulty):

| Creature | Health / attack | Where |
|---|---|---|
| wasp, scorpion, mantis, stratoshark, manticore | 40–150 / 8–22 | waves, cells, roosts, escorts |
| springbug | 250 / 24 | hatchery, cells, the Great Cage |
| **Crowned Mantis** (alpha mantis) | 950 / 36 | Gibbet Spire crown |
| **Rookmother** (nightmare) | 950 / 32 | Rookery |
| emperor scorpion | 1050 / 56 | the Gaol's heavy cell |
| **The Gaoler** (brutalfly) | 1250 / 30 | Hanging Gaol |
| **Hive Tyrant** (Hercules beetle) | 1625 / 60 | Brood Hive |
| Gnashback / Shrikewing | 275 / 24, 150 / 28 | the wilds, roosts, aeries, Carrion Fields |
| **The Chained Matriarch** | 1750 / 40; a third of the damage while chained, 150% on the open sac | the Great Cage |

The frontier is **mid-to-late game**: come with Antarchy gear at least at the Nightmare tier, or a superhero suit. The Rift
Shard needs an eye of ender, which keeps early players out. Antarchy's King and Queen are not used: they stay where Antarchy
puts them.

### How fights behave

* **Situated, not spawned around you.** Prisoners, roosting flyers and residents are already in their places when you
  arrive. A fight only starts when you enter its part of the landmark (or strike one of its creatures).
* **Bounded.** No constant spawning: every fight has a fixed number of waves, and residents that are all killed move back
  in only after a Minecraft day. Creature health and damage are each creature's own; nothing is inflated. Integrated
  Boogaloo's own difficulty scaling (Boogaloo Core's KubeJS MobScaling) applies to these creatures as it does to any spawn.
* **Telegraphed elites.** Guardians have a boss bar and abilities that are always announced first: a ring drawn on the
  ground before a **slam** (damage scaled from the elite's own attack), a call before a **rally**, a crouch before a **pounce**, a breath before a **screech**
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
| **Heart of the Great Cage** | the Chained Matriarch (each fighter) | builds a Cage Beacon |
| **Matriarch's Mantle** | the Chained Matriarch (each fighter) | in the hotbar or off hand: **Wingsail** (long falls become a slow glide, sneak to drop; no fall damage) and the **brood truce** (wild insects, Antarchy's arthropods included, leave you alone until you strike them; landmark fights and bosses are not wild). It changes how you travel the frontier's spires and cliffs |
| **Gnashback Carapace** (4 pieces) | a netherite piece + 3 Gnashback Plates, any grid | netherite's protection (3/8/6/3) with toughness 3.5 and knockback resistance 0.15; **full set**: no knockback at all, and insects deal 25% less. Repaired with plates |
| **Shrike Impaler** | 3 Shrike Talons + netherite ingot + stick | a spear (Better Combat spear moves and reach in the pack): 34 damage, **double against anything airborne** (flyers, leaping or knocked-up creatures); a struck flyer is driven down and a Shrikewing is grounded. Repaired with talons |
| **Rift Lens** | camps (60%), or spyglass + amethyst + Antarchy chitin | in the frontier: names the nearest cage, lair and camp with distance, direction and whether you have conquered it; shows the Great Cage once you carry the key |
| **Swarmbreaker** | Hive Heart + 2 Antarchy mantis claws + netherite sword | brood-breaker glaive (Better Combat glaive moves in the pack). 40 damage (60 vs insects); Pounce lands in a shockwave (24, 36 vs insects) that smashes egg clutches (ending a hatchery's waves sooner) and staggers insects. Below Antarchy's Nightmare Sword (50) and Ultimate Sword (100) as measured in the pack: a crowd and nest tool, not a replacement |
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
* Operators: `/frontier go`, `/frontier locate <any|cage|lair|camp|great_cage|observatory>`, `/frontier stats`,
  `/frontier landmark build <id> [rotation]`, `/frontier landmark info`, `/frontier landmark zone <zone> start|clear|reset`,
  `/frontier landmark forget`, `/frontier debug rosters`, `/frontier debug dump <namespace>`,
  `/frontier debug trial <gnashback|shrikewing|matriarch|warden|mite|observatory|abyss|leviathan>` (CI's scripted fights),
  `/frontier debug pose <entities> <state>`, `/frontier abyss` (go to the Abyss), `/frontier abyss restore` (the nearest
  rift engine takes all three parts), `/frontier abyss summon|reset` (call or dismiss the Leviathan).
* `/frontier return` also works in the Astral Abyss: back to where you came in.

## The Rift Observatory and the Astral Abyss

The arc: **find a Rift Observatory in the frontier → learn what happened there → win the engine's three parts back →
restore the engine and open the rift → explore the Astral Abyss's places for the Sigil Shards and the Blinkstone → call
and defeat the Eclipse Leviathan → the Corona, and Eclipse Scales to grow it.**

### Finding the observatory

Rift Observatories generate in the Hushed Barrens, Talon Spires and Gnashwood Wilds, about half as often as the other
major landmarks (they never overlap them). Once the Great Cage has fallen, the **Rift Lens** also names the nearest
observatory; the last camp journal says so. Whoever holds an **Astrolabe** (the observatory's Archive has one) gets the
direction from it too.

### The observatory ([render](docs/renders/rift_observatory.png), [west side](docs/renders/rift_observatory_west.png), [cutaway](docs/renders/rift_observatory_section.png))

81×98×81. An octagonal containment wall around a courtyard split diagonally by a fissure (it falls through into the
vaults). In the middle the roofless **Containment Well**: the rift engine on its dais, the sealed gate beside it, two inner
galleries, copper containment pylons, and above it the **tear** — a jagged sheet of rift glass and crying obsidian rising
70 blocks — inside three broken **containment rings** that float with nothing holding them (the widest is a walkable band).
Behind it the **Lens Tower** with its shattered observing dome, the great telescope still aimed at the tear, and a broken
bridge to the Well's upper gallery. The **Orrery Hall** (west) has a ring fragment through its roof; the **Archive**
(east); the **Gatehouse** (south); the **Coolant Vaults** run under the courtyard. Void tendrils, lumen crystal, starmoss
and amethyst grow where the rift touched the stone.

| Section | Fight | Layout | Reward |
|---|---|---|---|
| The Gatehouse | ambush, once | narrow gate passage, mites from the towers and the air | — |
| The Orrery Hall | waves | long hall, mezzanine, flyers among the hanging planets | **Star Chart**; the workshop chest |
| The Coolant Vaults | brood | ring tunnels and four tank chambers; mites hatch from Void Cysts until you break them | **Coolant Heart**; two caches |
| The Lens Dome | guardian: **the Astronomer's Warden** (an Orrery Warden at 3× health with escorts) | open dome, instrument consoles as cover from its beam; **sealed until the Hall and the Vaults are cleared** | **Focusing Lens**; the vault chest |

Six journals tell the story in the order you meet them (the Standing Orders in the courtyard, the Engine Log beside the
engine, Notes on the Hollow Star in the Hall, the Survey of the Far Side in the Archive, Coolant Maintenance in the vaults,
The Last Watch in the dome). The Archive's chest always holds an **Astrolabe**.

**The engine.** Use the three parts on it, in any order (using it empty-handed says what is still missing). When the third
goes in, the gate beside it opens to the Astral Abyss **for good**, and the **updraft lift** up the Lens Tower is unsealed:
the permanent shortcut. The gate in the Abyss brings you back to the same spot.

**Flight.** Breaches in the Well, the rings, the broken bridge and the fissure all give other ways in. None of them skips a
part: the dome stays sealed until the Hall and the Vaults are won, and the parts come only from their fights.

### The Astral Abyss ([map of the islands](docs/renders/abyss_map.png))

A void dimension of floating islands at fixed night. The sky is drawn by the mod: 2600 stars, a nebula band, a great
eclipsed world, drifting silhouettes, and a coloured beam of light over each place (fading in from 200 blocks). No
shaders or extra render distance are needed; it was made for render distance 8–12.

The islands come from a fixed recipe (the same in every world), with three layers of floating land, ores (Astral Ore →
Starmetal), lumen crystal, starmoss and starbloom on top and void tendrils underneath. Paths of stepping stones join the
places, so no flight is needed; updraft vents lift you where the routes climb.

| Place | Where | What |
|---|---|---|
| **The Landing** ([render](docs/renders/abyss_landing.png)) | 0, 0 | where you arrive, in front of the gate home; a guide on the lectern, signposts to the other places |
| **The Starwell** ([render](docs/renders/abyss_starwell.png)) | 232, −148 | standing stones round a well of light (stairs down, an updraft back up): waves of mites with a warden; **the Blinkstone** and a **Sigil Shard**; a cache at the bottom |
| **The Drifting Archive** ([render](docs/renders/abyss_archive.png)) | −236, −72 | a roofless library; climb to the walkway, ride the draught to the floating reading room: **the Archivist** (an Orrery Warden at 3.5× health with escorts) among the shelves; a **Sigil Shard** |
| **The Tether Spire** ([render](docs/renders/abyss_tether_spire.png)) | 64, 268 | a needle chained to three platforms you climb by updraft (a pool at its foot breaks a fall from the lower ones): an ambush on the wing at the top; a **Sigil Shard** |
| **The Hollow Crown** ([render](docs/renders/abyss_hollow_crown.png)) | 24, 560 | the boss arena: 80 blocks across, six obelisks, a knee-high rim with gaps, a crown of broken spires, the **Eclipse Altar** at the north edge |

The **Astrolabe** shows the way to a place while you hold it (use it to pick the next; sneak-use lists them all, visited or
not). Places are built when someone first comes within 96 blocks.

**Void safety** (changes nothing outside the Abyss):
* Falling below the islands: the rift sets you back on the last solid ground you stood on, costing a fifth of your
  maximum health (never the last of it), with a moment of slow falling.
* Items that fall drift to safe ground at the nearest place.
* Dying there: your drops keep for fifteen minutes (vanilla is five), and on respawn you are told where they are.
* Ways home: the Landing's gate, the Rift Shard (used in the Abyss), or `/frontier return`. All take you back to where you
  came in; if that place is gone, to the frontier. Losing everything still leaves `/frontier return`.
* Disconnecting or restarting: fights, places and the Leviathan's state are saved with the world.

### The creatures ([mite](docs/renders/creature_lumen_mite_model_sheet.png), [warden](docs/renders/creature_orrery_warden_model_sheet.png), [Leviathan](docs/renders/creature_eclipse_leviathan_model_sheet.png))

* **Lumen Mite**: a lantern-insect that circles you. Its lantern swells (tell), then it spits a slow star bolt (expires
  after 3 s, no knockback). Fragile up close.
* **Orrery Warden**: a floating orrery that guards a place (it never chases more than 48 blocks from home). Its rings stop
  and its lens flares (1 s tell, the aim line drawn), then a beam that turns slowly after you and stops at any block. After
  firing it stalls and takes double damage. Up close, a short pulse that in the Abyss barely nudges.
* Each gives a one-line hint the first time it hunts you. At most 8 of them near any spot from natural spawning, none on
  the Landing or the Hollow Crown.

### The Eclipse Leviathan

Three Sigil Shards and an eye of ender make the **Eclipse Sigil** (later ones can be forged from Starmetal and a Lumen
Core). Use it on the Hollow Crown's altar and the Leviathan rises from the void; it cannot be hurt while it rises.

| Attack | Tell | Answer |
|---|---|---|
| **Eclipse Beam** | it hangs at the edge, its corona flares, and the whole sweep is drawn on the floor (1.5 s) | get behind an obelisk or where the line has passed; in phase 2+ it sweeps back again |
| **Gravity Wells** | violet rings close on each fighter (1.5 s) | step out of your ring; the pull goes to the ring's middle, never outward |
| **Low Pass** | a line of soul fire across the arena (1.25 s) | step off the line; it then hangs low at the far end: the melee window |
| **Brood** (phase 2+) | it rears and calls | up to two Lumen Mites at a time, never more than four alive |
| **Eclipse** (phase 3) | it climbs, the arena darkens, a ring of fire marks the middle (2.5 s) | leave the ring; it crashes down there and lies **exposed** for 6 s (double damage) |

Phases change at two thirds and one third of its health, each with a roar (half damage while it roars). Its health grows
by half for each extra fighter in the arena (up to three extra). Nothing it does pushes anyone outward, and its landing
deals damage without knockback. It never leaves the arena. Ranged builds have the whole arena and the obelisks; melee
builds have the low pass, the wells and the eclipse windows.

If everyone leaves the arena (or logs off) for 30 s, it sinks back: it and its mites are removed and the altar keeps the
charge, so the next call costs nothing. A Leviathan that somehow loads without a fight (an old save) is turned away.

**Rewards** (each fighter in the arena during the fight; rewards for anyone offline at the end wait for their next login):
the **Corona** the first time, and every time two **Eclipse Scales** and two **Starmetal Ingots**.

### Rewards of the Abyss

| Item | From | Use |
|---|---|---|
| **Astrolabe** | the observatory's Archive (always); Starmetal + compass + Lumen Core | in the frontier points to the nearest observatory; in the Abyss to its places |
| **Blinkstone** | the Starwell | a 10-block step through the air, never into a block; 3 s cooldown, 240 uses, repaired with Starmetal |
| **Starmetal** | Astral Ore on the islands (iron pickaxe; Fortune works), wardens, caches | forges Eclipse Sigils, repairs the Blinkstone |
| **Lumen Core** | Orrery Wardens (50%), Lumen Mites (6%), caches | sigils, astrolabes, updraft vents |
| **Updraft Vent** | astral bricks + Lumen Core + phantom membrane | build your own lifts (24 blocks, sneak to sink, no fall damage) |
| **Corona** | the Leviathan, once per player | a sword (38 damage, Better Combat glaive moves) that stores light with each melee hit (5 charges, +2 per tier) and releases it as a piercing beam (10 per charge, 20+ blocks, stopped by blocks). Sneak-use with an Eclipse Scale in the off hand to raise its tier (up to 3). Below Antarchy's Nightmare Sword (50) and Ultimate Sword (100) in melee; its point is reach |
| **Eclipse Scale** | the Leviathan, every victory | Corona tiers and repair |
| Astral blocks | the islands, crafting | building: astral shale, bricks, chiseled bricks, rift glass, lumen crystal, starmoss |

Seven advancements: Stargazers, Parts of the Engine, Through the Rift, Between the Stars, The Eclipse Sigil, Fallen Metal and
Totality.

### About the reference

The request pointed to Stellaria (a Fabric 1.21.1 mod on Modrinth) as an inspiration. Modrinth could not be reached from
the build environment (blocked by its network policy), so its pages, gallery and footage were **not** viewed; what is
known about it here comes only from search-engine summaries. It is a Fabric mod and is not installable in this NeoForge
pack. Nothing from it is used: the names, the dimension, the structures, the creatures, the models, the textures, the
sounds and the code here are all original.

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

The creatures: natural Gnashbacks and Shrikewings count against the normal monster cap (spawn weights are low: they
are meant to be met, not swarmed by). Their AI looks only at their own target; a Shrikewing picking a perch reads ten
heightmap columns once every 45–90 seconds, and its prey check runs once every 20 seconds. The Matriarch exists only in
a Great Cage with a player near it, and her brood call is capped at the cage's escort count plus two. Acid puddles
last 4 seconds.

The Abyss: nothing is force-loaded. Its places are built once, when a player first comes near; its fights run only near
players; the Leviathan exists only while its fight is active and never leaves the arena. Star bolts last 3 s, the
Leviathan's mites are capped at four, natural spawns at eight within 48 blocks. The sky is a few hundred quads per frame;
the particle multiplier applies to all its effects.

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
* **Creature trials** on the same pack server: each creature's fight is played against a stand-in target, checking that
  every tell comes before its attack, that dodging works and leaves the creature open, that openings take the damage
  promised, and that the Matriarch's chains, brood call, acid, leap and death work in the Great Cage. Last run: all 40
  server checks pass.
* **0.5.0** (see TESTING.md): the observatory's seal and engine, the Abyss's places, safe arrival, void catch and item
  rescue, the Orrery Warden and Lumen Mite, and the Eclipse Leviathan's whole fight (summon, phases, mites, eclipse,
  arena bounds, save and load, abandonment reset, free recall, rewards): all 78 server checks pass. The client run
  walked through the restored gate into the Abyss and called the Leviathan: [screenshots](docs/screenshots/ingame/abyss).
* **In-game screenshots** from the full Integrated Boogaloo client (every jar of the pack), scripted, under software
  rendering: [docs/screenshots/ingame](docs/screenshots/ingame).
* **Not tested**: real play by a person (timing with a mouse and keyboard, how it feels), sound by ear, multiplayer with
  two clients, frame rate on your PC, and the Carapace set bonus, Impaler bonus and Mantle in actual use.

## Building from source

```
cd unstable-frontiers
python3 tools/structures/<landmark>.py    # regenerate a template + its sidecar (needs nbtlib, Pillow)
python3 tools/datagen.py                  # rosters, worldgen, loot, recipes, advancements, lang, sounds
python3 tools/textures.py                 # item and block textures
python3 tools/check_data.py               # standalone data checks
gradle build                              # Java 21, Gradle 8.10.2
python3 tools/models/<gnashback|shrikewing|matriarch>.py   # creature model, texture, glow mask and animations
python3 tools/models/preview.py <creature> <out_dir>      # offline preview renders of every pose
python3 tools/sounds/synth.py                             # the creatures' sounds (needs numpy and ffmpeg)
python3 tools/gen_creature_textures.py                    # gear icons and Carapace armour layers
python3 tools/structures/rift_observatory.py              # the observatory template
python3 tools/structures/abyss_places.py                  # the abyss's five place templates
python3 tools/abyss_textures.py                           # abyss blocks, items, sky textures
python3 tools/abyss/preview.py                            # map and section of the abyss's islands (same maths as the game)
python3 tools/models/<lumen_mite|orrery_warden|eclipse_leviathan>.py
```
`tools/abyss_data.py` holds the observatory's and the abyss's data (dimension, biomes, loot, recipes, advancements,
text, sounds); `datagen.py` folds it in.

The jar is `build/libs/unstable_frontiers-0.5.0-rc1.jar`.

## How the creatures were made

No Blockbench or Blender was used, and no other creator's models, animations or sounds. Each creature is written as a
Python script (`tools/models/*.py`) that builds a Bedrock-format GeckoLib model (`geo/entity/*.geo.json`, box UV, bones
and pivots), paints its texture and glow mask procedurally from named materials (chitin, rusted plate, membrane, bone,
eye), and writes its keyframe animations (`animations/entity/*.animation.json`). The `.geo.json` and `.animation.json`
files are standard GeckoLib formats, so they open and can be edited in Blockbench (GeckoLib Animation Utils plugin).
`tools/models/render.py` draws previews using GeckoLib's own bone maths, which is how every pose was checked before it
went into the game; the in-game screenshots then show how GeckoLib actually renders them.

The 25 sounds are synthesised from noise, oscillators and filters by `tools/sounds/synth.py` (seeded, so re-running gives
the same files) and were checked as spectrograms, not by ear.

The landmark cues (discovery, gates, waves) still play vanilla sound events at other pitches through this mod's own sound
definitions.

## Licence and credits

Original code, structures, creature models, animations, textures, sounds and writing. Antarchy (All Rights Reserved) is
referenced by id only: no Antarchy code or assets are included. GeckoLib (MIT) is a runtime dependency, not bundled.
