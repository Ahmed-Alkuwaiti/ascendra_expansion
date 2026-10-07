"""Checks that every vanilla constant the Java uses (SoundEvents, ParticleTypes, MobEffects, Blocks, Items, EntityType) and every vanilla id
in the act two biome files exists in Minecraft 1.20.1."""
import glob
import json
import re

import paths

V = paths.VANILLA
reg = {k: set(json.load(open(f'{V}/reg_{k}.json'))) for k in ('sound_event', 'particle_type', 'mob_effect', 'block', 'item', 'entity_type',
                                                             'worldgen_placed_feature')}
EFFECT_ALIAS = {'MOVEMENT_SLOWDOWN': 'slowness', 'MOVEMENT_SPEED': 'speed', 'DIG_SLOWDOWN': 'mining_fatigue', 'DIG_SPEED': 'haste',
                'DAMAGE_BOOST': 'strength', 'DAMAGE_RESISTANCE': 'resistance', 'HARM': 'instant_damage', 'HEAL': 'instant_health',
                'CONFUSION': 'nausea', 'JUMP': 'jump_boost'}


def const_ids(ids):
    return {i.upper().replace('.', '_'): i for i in ids}


tables = {'SoundEvents': const_ids(reg['sound_event']), 'ParticleTypes': const_ids(reg['particle_type']),
          'MobEffects': {**const_ids(reg['mob_effect']), **{k: v for k, v in EFFECT_ALIAS.items()}},
          'Blocks': const_ids(reg['block']), 'Items': const_ids(reg['item'])}
tables['EntityType'] = {**const_ids(reg['entity_type']), 'Builder': 'x'}
SOUND_FIX = {'BELL_BLOCK': 'block.bell.use', 'BELL_RESONATE': 'block.bell.resonate', 'GENERIC_SPLASH': 'entity.generic.splash',
             'GLASS_BREAK': 'block.glass.break', 'SAND_BREAK': 'block.sand.break', 'CHAIN_BREAK': 'block.chain.break',
             'ARMOR_EQUIP_NETHERITE': 'item.armor.equip_netherite', 'GENERIC_EXPLODE': 'entity.generic.explode'}
bad = []
for f in sorted(glob.glob(paths.JAVA + '/**/*.java', recursive=True)):
    src = open(f).read()
    for cls, table in tables.items():
        for name in set(re.findall(r'\b' + cls + r'\.([A-Z][A-Z0-9_]+)\b', src)):
            if name in table:
                continue
            if cls == 'SoundEvents':
                guess = SOUND_FIX.get(name)
                if guess and guess in reg['sound_event']:
                    continue
                # vanilla names most sounds TYPE_THING_EVENT for "type.thing.event"; accept any id whose parts rejoin to the name
                if any(i.replace('.', '_').replace('/', '_').upper().endswith(name) or name.endswith(i.split('.', 1)[-1].replace('.', '_').upper())
                       for i in reg['sound_event'] if i.split('.')[0] in ('entity', 'block', 'item', 'ambient')):
                    continue
            bad.append((f.split('/')[-1], cls, name))
for b in ('drowned', 'pale', 'scarlet'):
    j = json.load(open(f'{paths.RES}/data/aurelia/worldgen/biome/{b}.json'))
    for step in j['features']:
        for feat in step:
            if feat.startswith('minecraft:') and feat.split(':')[1] not in reg['worldgen_placed_feature']:
                bad.append((b, 'feature', feat))
    for cat, lst in j['spawners'].items():
        for s in lst:
            if s['type'].startswith('minecraft:') and s['type'].split(':')[1] not in reg['entity_type']:
                bad.append((b, 'spawn', s['type']))
    eff = j['effects']
    if 'particle' in eff and eff['particle']['options']['type'].split(':')[1] not in reg['particle_type']:
        bad.append((b, 'particle', eff['particle']['options']['type']))
    for key in ('ambient_sound',):
        if key in eff and eff[key].split(':')[1] not in reg['sound_event']:
            bad.append((b, 'sound', eff[key]))
    if 'mood_sound' in eff and eff['mood_sound']['sound'].split(':')[1] not in reg['sound_event']:
        bad.append((b, 'sound', eff['mood_sound']['sound']))
print('vanilla references:', 'all exist' if not bad else bad)
