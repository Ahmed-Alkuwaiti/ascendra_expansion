"""Standalone data checks (no Minecraft needed): every JSON parses; every roster, loot table, reward item, gate and
template a landmark references exists; every item has a model and texture; every translation key the code uses is in
en_us.json. Exits non-zero on any problem. Run from the addon folder: python3 tools/check_data.py"""
import glob
import json
import os
import re
import sys

import nbtlib

R = 'src/main/resources'
D = R + '/data/unstable_frontiers'
A = R + '/assets/unstable_frontiers'
problems = []


def load(path):
    try:
        return json.load(open(path))
    except Exception as e:
        problems.append(f'{path}: {e}')
        return None


for f in glob.glob(R + '/**/*.json', recursive=True):
    load(f)

rosters = {os.path.basename(f)[:-5] for f in glob.glob(D + '/roster/*.json')}
loot = {f[len(D) + len('/loot_table/'):-5] for f in glob.glob(D + '/loot_table/**/*.json', recursive=True)}
items = set()
for f in glob.glob('src/main/java/**/ModItems.java', recursive=True):
    items |= set(re.findall(r'ITEMS\.register(?:SimpleBlockItem)?\("([a-z_]+)"', open(f).read()))

for f in sorted(glob.glob(D + '/landmark/*.json')):
    name = os.path.basename(f)[:-5]
    lm = load(f)
    if lm is None:
        continue
    nbt = D + '/structure/' + lm['template'].split(':')[1] + '.nbt'
    if not os.path.exists(nbt):
        problems.append(f'{name}: template {nbt} missing')
    else:
        t = nbtlib.load(nbt)
        for b in t['blocks']:
            if 'nbt' in b and 'LootTable' in b['nbt']:
                table = str(b['nbt']['LootTable']).split(':')[1]
                if table not in loot:
                    problems.append(f'{name}: chest loot table {table} missing')
        size = [int(v) for v in t['size']]
        if size != lm['size']:
            problems.append(f'{name}: sidecar size {lm["size"]} != template {size}')
    if not os.path.exists(D + '/worldgen/structure/' + name + '.json'):
        problems.append(f'{name}: no worldgen structure')
    ids = {z['id'] for z in lm['zones']}
    for z in lm['zones']:
        if z['roster'] not in rosters:
            problems.append(f'{name}/{z["id"]}: roster {z["roster"]} missing')
        if z.get('reward') and z['reward'] not in items:
            problems.append(f'{name}/{z["id"]}: reward {z["reward"]} is not an item of this mod')
        for g in (z.get('gate'), z.get('lock_gate')):
            if g and g not in lm.get('gates', {}):
                problems.append(f'{name}/{z["id"]}: gate {g} not defined')
        for r in z.get('requires', []):
            if r not in ids:
                problems.append(f'{name}/{z["id"]}: requires unknown zone {r}')
        if not z['spawns'] and z['kind'] != 'finale':
            problems.append(f'{name}/{z["id"]}: no spawn points')
        x0, y0, z0, x1, y1, z1 = z['box']
        for p in z['spawns']:
            if p in z.get('flyer_spawns', []):
                continue      # flyers may arrive from outside (the Rookmother comes in from the sky)
            if not (x0 - 2 <= p[0] <= x1 + 2 and y0 - 2 <= p[1] <= y1 + 2 and z0 - 2 <= p[2] <= z1 + 2):
                problems.append(f'{name}/{z["id"]}: spawn {p} outside its zone box')
    for r in lm.get('residents', []):
        if r['roster'] not in rosters:
            problems.append(f'{name}: resident roster {r["roster"]} missing')

for i in items:
    model = A + '/models/item/' + i + '.json'
    if not os.path.exists(model):
        problems.append(f'item {i}: no model')
    elif i != 'cage_beacon' and not os.path.exists(A + '/textures/item/' + i + '.png'):
        problems.append(f'item {i}: no texture')

lang = load(A + '/lang/en_us.json') or {}
for i in items:
    key = ('block' if i == 'cage_beacon' else 'item') + '.unstable_frontiers.' + i
    if key not in lang:
        problems.append(f'lang: {key} missing')
for f in glob.glob('src/main/java/**/*.java', recursive=True):
    for key in re.findall(r'translatable\("([a-z_.]+)"', open(f).read()):
        if key.endswith('.') or key.endswith('_') or any(k.startswith(key) for k in lang):
            continue      # a prefix the code completes (tooltip lines, per-kind keys)
        if key not in lang:
            problems.append(f'lang: {key} (used in {os.path.basename(f)}) missing')
for f in glob.glob(D + '/advancement/*.json'):
    a = load(f) or {}
    for k in ('title', 'description'):
        key = a.get('display', {}).get(k, {}).get('translate')
        if key and key not in lang:
            problems.append(f'lang: {key} missing')
sounds = load(A + '/sounds.json') or {}
for f in glob.glob('src/main/java/**/ModSounds.java', recursive=True):
    for s in re.findall(r'event\("([a-z_.]+)"\)', open(f).read()):
        if s not in sounds:
            problems.append(f'sound {s} not in sounds.json')

for p in problems:
    print('PROBLEM', p)
print(f'checked {len(rosters)} rosters, {len(loot)} loot tables, {len(items)} items: {len(problems)} problems')
sys.exit(1 if problems else 0)
