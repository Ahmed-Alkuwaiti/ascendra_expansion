# Moving a world into ATM10

`clean_world.py` makes a vanilla-only copy of a modded world (Ascendra, Forge 1.20.1) so
it opens in All the Mods 10 (NeoForge 1.21.1). Mod blocks become air, mod items/mobs/biomes
and dimensions are removed, and Forge's mod list is cleared from `level.dat`. The original
world is not touched.

```
python3 -I tools/atm10_world/clean_world.py "<world folder or .zip>" cleaned_world --zip
```

Put the cleaned folder in the ATM10 instance's `saves/` folder and open it. Minecraft
upgrades it from 1.20.1 to 1.21.1 on first load. Keep a backup of the original either way.

`--keep create mekanism ...` keeps content from mods that are also in ATM10. Content kept this
way relies on that mod to upgrade its own data from 1.20.1.
