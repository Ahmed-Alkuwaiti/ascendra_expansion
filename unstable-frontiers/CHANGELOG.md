# Changelog

## 0.5.0-rc1 — the Rift Observatory and the Astral Abyss

For Integrated Boogaloo 1.0.8 (Minecraft 1.21.1, NeoForge 21.1.264), with Antarchy 2.2.9 and GeckoLib 4.9.3 from the pack.
Replaces 0.4.0-rc1; worlds carry over. Everything from 0.4.0 is unchanged apart from the notes under "Other changes".

### The Rift Observatory (a new major landmark in the frontier)
* A ruined observatory and containment fortress split by a cosmic rift: an octagonal containment wall, a courtyard torn
  by a fissure, the roofless Containment Well with the rift engine and its sealed gate, the tear of the rift itself
  hanging above it inside three broken containment rings, the Lens Tower with its shattered dome and great telescope,
  the Orrery Hall, the Archive, the Gatehouse and the Coolant Vaults under the courtyard. Hushed Barrens, Talon Spires
  and Gnashwood Wilds; rarer than the other major landmarks.
* Four fights, each laid out differently: an ambush in the gate passage; waves round the hanging orrery (flyers among
  the planets); a brood fight in the vault tunnels, where every Void Cyst you break is one fewer hatching; and the
  Astronomer's Warden in the Lens Dome, sealed until the Hall and the Vaults are cleared.
* Three engine components come from those fights (Star Chart, Coolant Heart, Focusing Lens). Set them into the engine
  in any order: the gate opens to the Astral Abyss for good, and the updraft lift up the Lens Tower unseals.
* Six journals tell what happened, in the order you find them. The Archive holds an Astrolabe.
* Flight gets you in through the breaches, the rings and the broken bridge, but not past the sealed dome.

### The Astral Abyss (a new dimension)
* Floating islands over the void under a fixed night sky: a starfield, a nebula band, an eclipsed world and drifting
  silhouettes, coloured light beams over each place. Drawn by the mod (no shaders, no extra render distance).
* Five places: the Landing (where you arrive, beside the gate home), the Starwell (waves; the Blinkstone and a Sigil
  Shard), the Drifting Archive (the Archivist on a floating reading room; a Sigil Shard), the Tether Spire (an ambush on
  chained platforms you climb by updraft; a Sigil Shard) and the Hollow Crown, the boss arena.
* Stepping-stone paths join the islands for players without flight; updraft vents lift you; the Astrolabe shows the way.
* Void safety without changing inventory rules: falling below the islands, the rift sets you back on the last safe
  ground you stood on for a fifth of your health (never the last of it); items that fall drift to the nearest place;
  what you drop when you die keeps for fifteen minutes and you are told where. The landing gate, the Rift Shard and
  `/frontier return` all take you back to where you came in.

### Creatures (original models, textures, animations and sounds)
* **Lumen Mite**: small flying lantern-insects; a swelling tell, then a slow star bolt (gone after 3 s).
* **Orrery Warden**: a floating orrery; its rings align and its lens flares, then a beam that blocks stop. After the
  beam it stalls and takes double damage. A close-range pulse that barely pushes in the Abyss.
* **The Eclipse Leviathan**: the Hollow Crown's boss, called with an Eclipse Sigil (three Sigil Shards and an eye of
  ender) at the altar. Eclipse Beam (the sweep is drawn on the floor first; the obelisks stop it), Gravity Wells (rings
  close on each fighter; they pull inward, never out), Low Pass (marked in soul fire, then a melee window), mites in the
  second phase (never more than four), and in the third the Eclipse: it crashes down in a ring of fire and lies open for
  double damage. Phases at two thirds and one third, each with a roar. Health grows by half for each extra fighter.
  Nothing it does throws anyone outward. If everyone leaves, it sinks after 30 s and the altar keeps the charge.

### Rewards
* Exploration before the boss: the Astrolabe, the Blinkstone (a short blink through the air, never into blocks), Starmetal
  (ore on the islands), Lumen Cores, caches at each place.
* The boss: the **Corona** (once per player), a sword that stores light with each melee hit and releases it as a
  piercing beam; Eclipse Scales raise its tier. Every victory: Eclipse Scales and Starmetal. Rewards for fighters who
  are offline at the victory wait for them.
* Seven new advancements, from Stargazers to Totality.

### Testing
* 38 new server checks for the observatory, the Abyss, its creatures and the Leviathan; all 78 pass with the pack.
  They found one bug before release (a summoned Leviathan was refused by its own fight), fixed here.
* In-game screenshots of all of it from the pack client: `docs/screenshots/ingame/abyss`.

### Other changes
* The Rift Lens finds Rift Observatories once the Great Cage has fallen; the last camp journal points to them.
* Roster elites can have a health multiplier (used by the Astronomer's Warden and the Archivist).
* Landmark rewards are now given per zone, so a landmark can reward several fights.

## 0.4.0-rc1 — the frontier's own creatures

For Integrated Boogaloo 1.0.8 (Minecraft 1.21.1, NeoForge 21.1.264). Requires Antarchy 2.2.9 and GeckoLib 4.9.3, both in
the pack. Replaces 0.3.0; worlds carry over (frontier landmarks already conquered stay conquered). A Great Cage conquered in
0.3.0 stays conquered, so its Matriarch fight and Mantle are not offered there again; another Great Cage further out
has them.

### New creatures (original models, textures, animations and sounds)
* **Gnashback** — a giant territorial beetle. Telegraphed charge (head down, shell cracked open, two ground scrapes);
  it fixes its line half a second before running. A charge into a wall or tree stuns it for 4 s with its back open
  (double damage). Bites up close. Lives in the Gnashwood Wilds, Hushed Barrens and Rustbone Scar, in Gibbet Spire pens
  and on Carrion Fields.
* **Shrikewing** — a diving sky predator. Circles high over its home, perches on high points, hunts players and now and
  then insects (Gnashbacks, Antarchy's arthropods). Telegraphed dive (wings raised, screech, a ring on the ground that
  stops following you half way through). A missed dive leaves it climbing (+50% damage) or grounded (double damage).
  Lives in the Talon Spires and Rustbone Scar, rookery roosts, spire aeries, Carrion Fields, night overflights and the
  Great Cage dome.
* **The Chained Matriarch** — the Great Cage's boss, replacing the basilisk there. Waits visibly in her chains before the
  fight and cannot be hurt until the key turns. While the four pylons stand she is tethered to the middle of the cage
  and takes a third of the damage. Scythe Sweep (fixed 120° arc, traced in sparks), Acid Volley (three globs and poison
  puddles; she holds her ground at mid range to use it), Brood Call (her escorts climb out; the open sac takes 150%
  damage, even chained). Breaking the last pylon snaps the chains: she roars, takes full damage and gains the Leap
  (landing ring fixed before she jumps, shockwave on landing). No enrage, no hidden phases. Her boss bar shows the
  pylons left.

### New gear
* **Gnashback Carapace** (helm, carapace, greaves, boots): a netherite piece + 3 Gnashback Plates. Netherite's protection
  with toughness 3.5 and knockback resistance 0.15; full set: no knockback, insects deal 25% less.
* **Shrike Impaler**: 3 Shrike Talons + netherite ingot + stick. 34 damage, double against anything airborne; drives
  flyers down and grounds Shrikewings. Better Combat spear moves in the pack.
* **Matriarch's Mantle** (the Great Cage's reward with the Heart, once per player): Wingsail (long falls become a glide,
  no fall damage) and the brood truce (wild insects leave you alone until you strike them).
* Gnashback Plates and Shrike Talons drop from their creatures (Looting applies) and from the Matriarch.

### Other changes
* Each creature gives a one-line hint in chat the first time it hunts you.
* Five new advancements: Hard Shell, Shell Game, Grounded, Anti-Air and Wingsail.
* Landmark rewards can name several items; the Great Cage gives the Heart and the Mantle.
* Bane of Arthropods works on the Gnashback and the Matriarch (`minecraft:arthropod` tag); the Matriarch is in
  `c:bosses`, so the Shackle and other mods treat her as a boss.

### Testing added
* Scripted creature trials on a server with the pack's mods (`/frontier debug trial`).
* In-game screenshots from the full pack client (`docs/screenshots/ingame`).

## 0.3.0 — the adventure expansion
Regions, landmarks (Gibbet Spire, Hanging Gaol, Rookery, Brood Hive, Carrion Field, camps, waysides, the Great Cage),
the encounter system, rewards built on Antarchy's progression. See the README.
