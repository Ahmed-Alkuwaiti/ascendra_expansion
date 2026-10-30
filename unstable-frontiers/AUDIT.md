# Audit — Unstable Frontiers 0.6.0-rc1

One mod (`unstable_frontiers`, one jar). The frontier (0.3–0.4), the cosmic expansion (0.5) and the Drowned Expanse (0.6)
share one registry set, one event bus registration (`UnstableFrontiers.java`), one encounter system
(`encounter/EncounterManager.java`), one data pack and one creative tab. There is no second mod or second jar.

Classes:
* **Verified** — implemented, and a scripted CI check on the Integrated Boogaloo 1.0.8 server (or client) exercised it
  and passed. The check names are the `check` lines in `ci/pack_server.sh`.
* **Untested** — implemented and registered, reachable in survival, but no automated check plays it.
* **Partial** — present but incomplete.
* **Missing** — not there.

"Survival route" says how a player without commands gets to it.

## The frontier

| Feature | Evidence (registration / file) | Survival route | Class |
|---|---|---|---|
| Frontier dimension, 4 regions | `data/unstable_frontiers/dimension/frontier.json`, `worldgen/biome/*`; `travel/RiftTravel.java` | Rift Shard (recipe `recipe/rift_shard.json`) | Verified (server boots it; landmarks locate in it) |
| Cage towers (Gibbet Spire, Hanging Gaol) | `worldgen/structure/gibbet_spire.json`, `hanging_gaol.json`; zones in `landmark/*.json` | natural generation; Rift Lens | Verified ("spire wave floor", "gaol warden" checks) |
| Nests (Rookery, Brood Hive, Carrion Field) | `worldgen/structure/rookery.json`, `brood_hive.json`, `carrion_field.json` | natural generation | Verified (roost, rookmother, brood, tyrant checks) |
| Camps, waysides (landmarks) | `camp_*.json`, `wayside_*.json` | natural generation | Verified ("natural camps generate") |
| Great Cage + Chained Matriarch | `great_cage.json`; `entity/ChainedMatriarchEntity.java` | Cagewright's Key (`recipe/cagewright_key.json`) | Verified (15 matriarch checks) |
| Rivalries, overflights | `ecology/Rivalry.java`, `ecology/Overflight.java` | automatic near players | Untested (no trial plays them) |
| Gnashback, Shrikewing | `registry/ModEntities.java` | natural spawns | Verified (tell / dodge / hit checks) |
| Rewards: trophies, key, Shackle, Swarmbreaker, Cage Beacon, Rift Lens, Carapace, Impaler, Mantle | `registry/ModItems.java`; recipes in `recipe/` | zone rewards and recipes | Items verified obtainable by the data check (every reward names an item); in-hand behaviour of the Carapace set bonus, Impaler and Mantle: **Untested** |
| Advancement tab | `advancement/*.json` | — | **Fixed in 0.6**: the root was granted only after crafting the Rift Shard, so the tab (and the hint how to start) was invisible to a new player. It is now granted on the first tick and its text gives the recipe. |

## The cosmic expansion

| Feature | Evidence | Survival route | Class |
|---|---|---|---|
| Rift Observatory (landmark, 4 fights, seal) | `worldgen/structure/rift_observatory.json`, `landmark/rift_observatory.json` | natural generation; Rift Lens after the Great Cage | Verified ("observatory …" checks, natural locate) |
| Restoration (engine, 3 parts, gate) | `block/RiftEngineBlock.java`, `block/AbyssGateBlock.java` | parts from the observatory's fights | Verified (engine and gate checks) |
| Astral Abyss dimension, sky | `abyss/*`, `dimension/astral_abyss.json`, `client/AbyssSkyEffects.java` | through the opened gate | Verified (client run walked through the gate) |
| Abyss places, travel, void safety | `abyss/AbyssPlaces.java`, `abyss/AbyssTravel.java` | arrival; stepping stones; Astrolabe | Verified (places, arrival, void catch, item rescue) |
| Lumen Mite, Orrery Warden | `ModEntities` | natural spawns and fights | Verified |
| Eclipse Leviathan | `entity/EclipseLeviathanEntity.java`, `abyss/EclipseEncounter.java` | Eclipse Sigil (3 shards + eye, or forged) | Verified (13 checks: phases, cap, reset, rewards) |
| Rewards: Blinkstone, Corona, Astrolabe, Starmetal, Updraft Vent | `registry/AbyssRegistry.java`, recipes | places, the boss, ore | Obtainable (data check); in-hand behaviour **Untested** |

Gaps looked for and not found: every item has a recipe, a loot table or a fight that gives it (the data check enforces
reward and loot references); every structure block a player must not break (gates, engine, altar, bells) is unbreakable;
JEI and EMI (both in the pack) show every recipe. No dimension id, item id or block id changed in 0.6, so worlds and
progress carry over with no migration.

## The Drowned Expanse (new in 0.6)

Filled in from the 0.6.0 CI run — see the table in TESTING.md.
