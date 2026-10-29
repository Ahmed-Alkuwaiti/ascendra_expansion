# Changelog

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
