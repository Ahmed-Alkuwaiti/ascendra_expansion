"""Each realm's kit, defined once: its material, armor set, signature weapon, wildlife and food.
Used by gen_realm_kit.py (assets and data), mobs_act5.py (models) and the preview gallery. The Java mirrors these names."""

REALMS = ['grove', 'skyreach', 'hollow', 'drowned', 'pale', 'scarlet', 'clockwork', 'mycelial']

KIT = {
    'grove': dict(material='verdant_shard', block='verdant_block', armor='verdant', armor_name='Verdant',
                  palette=[(34, 60, 28), (70, 120, 46), (128, 190, 80), (210, 240, 150)], accent=(120, 255, 90),
                  bonus='Regeneration I; poison cannot touch you; anyone who strikes you takes 4 damage and is rooted. Green spores drift round you.',
                  weapon='rootbreaker', weapon_name='Rootbreaker', weapon_power='Roots the target (Slowness III), poisons it, and heals you a heart.', weapon_ability='Bramble Eruption: thorns tear up through the ground in a line ahead (10 damage, rooted). 8 s.',
                  critter='mossling', critter_name='Mossling', critter_desc='A slow little tortoise with a garden growing on its shell.',
                  food='verdant_fig', food_name='Verdant Fig', food_power='Regeneration for 5 seconds.', ore=None),
    'skyreach': dict(material='stormglass_shard', block='stormglass_block', armor='stormglass', armor_name='Stormglass',
                     palette=[(40, 70, 110), (90, 150, 210), (170, 220, 250), (240, 252, 255)], accent=(140, 230, 255),
                     bonus='Jump Boost III, Speed I, no fall damage; a third of those who strike you are struck by lightning. Sparks crackle round you.',
                     weapon='stormpiercer', weapon_name='Stormpiercer', weapon_power='Throws the target into the air with a crack of thunder.', weapon_ability='Tempest Dash: you are flung eight blocks forward and lightning strikes everything you pass (12 damage). 6 s.',
                     critter='cloud_ray', critter_name='Cloud Ray', critter_desc='A pale manta that swims through the open sky between islands.',
                     food='sky_jelly', food_name='Sky Jelly', food_power='Slow Falling for 15 seconds.', ore=None),
    'hollow': dict(material='emberheart', block='emberheart_block', armor='emberheart', armor_name='Emberheart',
                   palette=[(24, 18, 22), (60, 36, 34), (200, 80, 30), (255, 180, 70)], accent=(255, 130, 40),
                   bonus='Fire Resistance and Strength I; anyone who strikes you burns for 6 seconds. Embers rise off you.',
                   weapon='soulcleaver', weapon_name='Soulcleaver', weapon_power='Sets the target on fire and withers it.', weapon_ability='Soul Inferno: a ring of soul fire bursts out round you (14 damage, burning, thrown back). 10 s.',
                   critter='ember_beetle', critter_name='Ember Beetle', critter_desc='A black beetle that glows through the cracks in its shell.',
                   food='charred_morsel', food_name='Charred Morsel', food_power='Fire Resistance for 30 seconds.', ore=None),
    'drowned': dict(material='tidestone_shard', block='tidestone_block', armor='tidestone', armor_name='Tidestone',
                    palette=[(16, 50, 52), (40, 110, 104), (90, 190, 170), (190, 250, 230)], accent=(80, 240, 210),
                    bonus="Water Breathing; Dolphin's Grace, Conduit Power and Regeneration in water or rain. Bubbles stream off you.",
                    weapon='tidebinder', weapon_name='Tidebinder', weapon_power='Drags the target toward you; half again as hard in water.', weapon_ability='Maelstrom: every enemy within 12 blocks is dragged to you and half-drowned (8 damage, slowed). 10 s.',
                    critter='lantern_jelly', critter_name='Lantern Jelly', critter_desc='A glowing jellyfish that drifts in the drowned forests.',
                    food='glowing_gel', food_name='Glowing Gel', food_power='Water Breathing and Night Vision for 30 seconds.', ore=None),
    'pale': dict(material='rime_crystal', block='rime_block', armor='rime', armor_name='Rime',
                 palette=[(70, 90, 120), (140, 170, 210), (210, 230, 250), (250, 254, 255)], accent=(200, 240, 255),
                 bonus='Immune to freezing, walk on powder snow, Resistance I; water freezes under your feet; anyone who strikes you is frozen. Snow falls round you.',
                 weapon='silent_requiem', weapon_name='Silent Requiem', weapon_power='Freezes the target; strikes twice as hard from a crouch.', weapon_ability='Whiteout Step: you vanish and reappear behind whatever you are looking at, striking it (18 damage, frozen). 6 s.',
                 critter='frost_hare', critter_name='Frost Hare', critter_desc='A white hare that freezes still when it hears you.',
                 food='frost_hare_haunch', food_name='Frost Hare Haunch', food_power='Very filling.', ore=None),
    'scarlet': dict(material='sunglass_shard', block='sunglass_block', armor='sunglass', armor_name='Sunglass',
                    palette=[(80, 24, 18), (160, 50, 30), (230, 110, 50), (255, 210, 120)], accent=(255, 90, 60),
                    bonus='By day Haste II and Strength I, by night Night Vision; a third of arrows and projectiles glance off you. Sunlight glints round you.',
                    weapon='venomfangs', weapon_name='Venomfangs', weapon_power='Very fast. Poisons the target, and half the blow cuts everything else within reach.', weapon_ability='Fang Flurry: you whirl through everything within 6 blocks (16 damage, Poison II). 8 s.',
                    critter='sand_skink', critter_name='Sand Skink', critter_desc='A red lizard that swims through the dunes.',
                    food='sunbaked_tail', food_name='Sunbaked Tail', food_power='Haste for 20 seconds.', ore=None),
    'clockwork': dict(material='chronite_shard', block='chronite_block', armor='chronite', armor_name='Chronite',
                      palette=[(30, 26, 40), (90, 60, 140), (180, 130, 60), (255, 220, 120)], accent=(180, 100, 255),
                      bonus='Speed II and Haste II. Borrowed Time: a killing blow throws you back to where you stood five seconds ago at half health instead (once every 90 s).',
                      weapon='hourshatter', weapon_name='Hourshatter', weapon_power='Its bladed limbs slow and weaken whatever they cut.', weapon_ability='Hour Volley: fires five chronite bolts in a fan; whatever they hit is frozen in time for 4 seconds. 3 s.',
                      critter='cogling', critter_name='Cogling', critter_desc='A brass clockwork beetle, ticking quietly as it wanders.',
                      food='tickberry', food_name='Tickberry', food_power='Speed for 20 seconds.', ore='chronite_ore'),
    'mycelial': dict(material='bloomspore', block='bloomspore_block', armor='bloomspore', armor_name='Bloomspore',
                     palette=[(50, 20, 60), (120, 40, 130), (210, 80, 200), (250, 200, 240)], accent=(255, 90, 230),
                     bonus='Night Vision; poison and wither cannot touch you; it feeds you when hungry; allies near you regenerate; anyone who strikes you is poisoned.',
                     weapon='sporethorn', weapon_name='Sporethorn', weapon_power='Poisons and sickens the target and everything near it.', weapon_ability='Bloom Burst: a cloud of spores bursts out (Poison III, nausea) and you heal for every enemy it catches. 10 s.',
                     critter='spore_puff', critter_name='Spore Puff', critter_desc='A floating puffball that sighs out glowing spores.',
                     food='puffcap', food_name='Puffcap', food_power='Saturation and Regeneration.', ore='bloomspore_ore'),
}
PIECES = ['helmet', 'chestplate', 'leggings', 'boots']

# ===================================================================================================================
# The Arsenals of the Tenfold Seal: per realm, an armor set, a signature weapon, three tools, an ore and two materials.
# Existing ids are kept where a thing already existed (the ores, their raw drops, the armor sets); only names and art change.
#   ore        the realm's ore block (id), and what it drops (raw)
#   metal      what armor, tools and the weapon are made from; made from raw by smelting or by crafting with iron or gold
#   special    the realm's second material, the heart of its weapon
ARSENAL = {
    'grove': dict(armor_name='Mossbound', weapon='rootbreaker', weapon_name='Rootbreaker', weapon_kind='warhammer',
                  tool='verdantite', tool_name='Verdantite', ore='verdant_ore', ore_name='Verdantite Ore', raw='verdant_shard',
                  raw_name='Raw Verdantite', block_name='Block of Raw Verdantite',
                  metal='verdantite_ingot', metal_name='Verdantite Ingot', metal_from='smelt',
                  special='living_root_fiber', special_name='Living Root Fiber'),
    'skyreach': dict(armor_name='Tempest', weapon='stormpiercer', weapon_name='Stormpiercer', weapon_kind='spear',
                     tool='aetherium', tool_name='Aetherium', ore='stormglass_ore', ore_name='Fulgurite Ore', raw='stormglass_shard',
                     raw_name='Sky Crystal Shard', block_name='Block of Sky Crystal',
                     metal='aetherium_ingot', metal_name='Aetherium Ingot', metal_from='gold',
                     special='stormglass_shard', special_name='Sky Crystal Shard'),
    'hollow': dict(armor_name='Sovereign', weapon='soulcleaver', weapon_name='Soulcleaver', weapon_kind='cleaver',
                   tool='soulsteel', tool_name='Soulsteel', ore='emberheart_ore', ore_name='Soulsteel Ore', raw='emberheart',
                   raw_name='Raw Soulsteel', block_name='Block of Raw Soulsteel',
                   metal='soulsteel_ingot', metal_name='Soulsteel Ingot', metal_from='smelt',
                   special='caged_soul_ember', special_name='Caged Soul Ember'),
    'drowned': dict(armor_name='Abyssal', weapon='tidebinder', weapon_name='Tidebinder', weapon_kind='trident',
                    tool='tidesteel', tool_name='Tidesteel', ore='tidestone_ore', ore_name='Abyssal Pearlstone', raw='tidestone_shard',
                    raw_name='Abyssal Pearl', block_name='Block of Abyssal Pearl',
                    metal='tidesteel_ingot', metal_name='Tidesteel Ingot', metal_from='iron',
                    special='tidestone_shard', special_name='Abyssal Pearl'),
    'pale': dict(armor_name='Rimebound', weapon='silent_requiem', weapon_name='Silent Requiem', weapon_kind='scythe',
                 tool='rimecrystal', tool_name='Rimecrystal', ore='rime_ore', ore_name='Hushcrystal Ore', raw='rime_crystal',
                 raw_name='Rime Crystal', block_name='Block of Rime Crystal',
                 metal='rime_crystal', metal_name='Rime Crystal', metal_from=None,
                 special='frozen_black_flame_core', special_name='Frozen Black-Flame Core'),
    'scarlet': dict(armor_name='Glasscarapace', weapon='venomfangs', weapon_name='Venomfangs', weapon_kind='twin daggers',
                    tool='scarlet', tool_name='Scarlet Glass', ore='sunglass_ore', ore_name='Scarlet Glass Ore', raw='sunglass_shard',
                    raw_name='Scarlet Shard', block_name='Block of Scarlet Shards',
                    metal='sunglass_shard', metal_name='Scarlet Shard', metal_from=None,
                    special='amber_venom_vial', special_name='Amber Venom Vial'),
    'clockwork': dict(armor_name='Paradox', weapon='hourshatter', weapon_name='Hourshatter', weapon_kind='repeating crossbow',
                      tool='chronite', tool_name='Chronite', ore='chronite_ore', ore_name='Chronite Ore', raw='chronite_shard',
                      raw_name='Raw Chronite', block_name='Block of Raw Chronite',
                      metal='chronite_ingot', metal_name='Chronite Ingot', metal_from='smelt',
                      special='temporal_core', special_name='Temporal Core'),
    'mycelial': dict(armor_name='Bloomguard', weapon='sporethorn', weapon_name='Sporethorn', weapon_kind='staff',
                     tool='mycelial', tool_name='Mycelial', ore='bloomspore_ore', ore_name='Mycoryte Ore', raw='bloomspore',
                     raw_name='Spore Cluster', block_name='Block of Spore Clusters',
                     metal='mycelial_ingot', metal_name='Mycelial Ingot', metal_from='iron',
                     special='bloomspore', special_name='Spore Cluster'),
}
# The specials that are crafted: four of the realm's metal round a catalyst.
SPECIAL_RECIPE = {'caged_soul_ember': 'minecraft:soul_lantern', 'frozen_black_flame_core': 'minecraft:soul_campfire',
                  'amber_venom_vial': 'minecraft:honey_bottle', 'temporal_core': 'minecraft:clock'}
TOOLS = ['pickaxe', 'axe', 'shovel']
SPECIAL_LORE = {
    'living_root_fiber': 'Still growing, slowly, even cut.', 'caged_soul_ember': 'A soul that would not stop burning, kept.',
    'frozen_black_flame_core': 'Black fire, frozen mid-flicker. It is very cold to hold and it is still burning.',
    'amber_venom_vial': 'The sands\' oldest poison, set like amber.', 'temporal_core': 'It ticks a little faster than the world does.',
    'genesis_ingot': 'Metal that remembers being every metal at once.',
    'fractured_genesis': 'What was left in the Unmaker when the worlds were taken back. Three fall with it every time it dies.',
}

# The Unmaker's arsenal: Genesis armor and Worldsunder. Tuned above everything else in the mod and above the usual endgame of a
# pack like Ascendra (netherite: 8 attack, 20 armor, 12 toughness).
GENESIS = dict(
    armor='genesis', armor_name='Genesis',
    stats='30 armor (the game\'s cap), 20 toughness (the cap), full knockback immunity, +5 max health per piece (+10 hearts in all).',
    bonus=[
        'Strength II, Resistance I, Fire Resistance, Night Vision, Water Breathing; poison, wither, freezing and falling cannot touch you.',
        'Event Horizon: no single blow can take more than 30% of your health, and half of all arrows and projectiles are swallowed.',
        'Eightfold Retaliation: whatever strikes you takes 6 damage and one realm\'s curse: rooted, struck, burned, dragged, frozen, cut, slowed or poisoned.',
        'The Last Heart: a killing blow leaves you at half health instead, with Absorption IV and a shockwave that throws back and hurts everything near you (once every 2 minutes).',
        'Crouch in mid-air to drift down slowly.',
    ],
    weapon='worldsunder', weapon_name='Worldsunder',
    weapon_stats='24 attack damage, 1.0 speed, 1.5 blocks of extra reach.',
    weapon_power='Unmaking: every hit also deals 3% of the target\'s max health (up to 15 more), and carries the next of the eight realm powers in turn: root, storm, fire, tide, frost, sweep, time, spores.',
    weapon_ability='Singularity: a black hole opens six blocks ahead, drags in everything within twelve blocks, then collapses (30 damage, Wither II, slowed). 20 s.',
    tool='genesis', tool_name='Genesis', metal='genesis_ingot', metal_name='Genesis Ingot', special='fractured_genesis',
    special_name='Fractured Genesis',
)
for _r in REALMS:
    KIT[_r]['armor_name'] = ARSENAL[_r]['armor_name']
