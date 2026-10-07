import nbtlib, glob, json, urllib.request, os, re, collections
R = __import__('paths').RES; A = R + '/assets/aurelia'; D = R + '/data/aurelia'; J = __import__('paths').JAVA
reg = set(json.load(urllib.request.urlopen('https://raw.githubusercontent.com/misode/mcmeta/1.20.1-registries/block/data.json')))
props = json.load(urllib.request.urlopen('https://raw.githubusercontent.com/misode/mcmeta/1.20.1-summary/blocks/data.json'))
src = {c: open(f'{J}/registry/{c}.java').read() for c in ('ModBlocks', 'ModItems', 'ModEntities')}
mod_blocks = set(re.findall(r'BLOCKS\.register\("([a-z_]+)"', src['ModBlocks'])); mod_items = set(re.findall(r'ITEMS\.register\("([a-z_]+)"', src['ModItems']))
mod_ents = set(re.findall(r'register\("([a-z_]+)"', src['ModEntities']))
CUSTOM = {'waygate': {'realm': ['grove', 'skyreach', 'hollow'], 'active': ['true', 'false']}, 'spore_planter': {'filled': ['true', 'false']},
          'storm_pylon': {'filled': ['true', 'false']}, 'soul_socket': {'filled': ['true', 'false']}}
PASS = {'minecraft:air', 'minecraft:cobweb', 'minecraft:moss_carpet', 'minecraft:red_mushroom', 'minecraft:brown_mushroom', 'minecraft:soul_campfire', 'minecraft:lightning_rod',
        'minecraft:soul_lantern', 'minecraft:fern', 'minecraft:grass', 'minecraft:tall_grass', 'minecraft:large_fern', 'minecraft:vine', 'minecraft:azalea', 'minecraft:flowering_azalea',
        'minecraft:lantern', 'minecraft:chain', 'minecraft:hanging_roots', 'minecraft:red_carpet', 'minecraft:lily_pad', 'minecraft:sweet_berry_bush', 'minecraft:end_rod',
        'minecraft:cave_vines', 'minecraft:cave_vines_plant', 'minecraft:skeleton_skull', 'minecraft:ladder', 'minecraft:cornflower', 'minecraft:blue_orchid', 'minecraft:allium',
        'minecraft:azure_bluet', 'minecraft:oxeye_daisy', 'minecraft:lily_of_the_valley', 'minecraft:poppy', 'minecraft:wither_rose', 'minecraft:soul_fire', 'minecraft:water'}
loot = {os.path.relpath(f, D + '/loot_tables')[:-5] for f in glob.glob(D + '/loot_tables/**/*.json', recursive=True)}
problems = []; ents = collections.Counter(); n = 0
for f in sorted(glob.glob(D + '/structures/*.nbt')):
    t = nbtlib.load(f); n += 1; base = os.path.basename(f); names = [str(p['Name']) for p in t['palette']]
    for p in t['palette']:
        name = str(p['Name']); ns, key = name.split(':')
        if ns == 'minecraft':
            if key not in reg: problems.append((base, 'unknown block', name))
            elif 'Properties' in p:
                valid = props.get(key, [{}])[0]
                for k, v in p['Properties'].items():
                    if k not in valid or str(v) not in valid[k]: problems.append((base, 'bad property', name, k, str(v), valid.get(k)))
        else:
            if key not in mod_blocks: problems.append((base, 'unknown mod block', name))
            for k, v in (p['Properties'].items() if 'Properties' in p else []):
                if str(v) not in CUSTOM.get(key, {}).get(k, []): problems.append((base, 'bad mod property', name, k, str(v)))
    blocks = {tuple(int(v) for v in b['pos']): names[int(b['state'])] for b in t['blocks']}
    for b in t['blocks']:
        if 'nbt' in b and 'LootTable' in b['nbt'] and str(b['nbt']['LootTable']).split(':')[1] not in loot: problems.append((base, 'missing loot table', str(b['nbt']['LootTable'])))
    for e in t['entities']:
        eid = str(e['nbt']['id']).split(':')[1]; ents[eid] += 1; x, y, z = (int(v) for v in e['blockPos'])
        if eid not in mod_ents: problems.append((base, 'unknown entity', eid))
        if eid not in ('storm_wisp', 'gale_talon'):
            here, below = blocks.get((x, y, z)), blocks.get((x, y - 1, z))
            if here is not None and here not in PASS: problems.append((base, eid, (x, y, z), 'inside', here))
            if below is None or below in PASS: problems.append((base, eid, (x, y, z), 'no ground', below))
    if base.endswith('_citadel.nbt'):
        c = collections.Counter(blocks.values())
        print(' ', base, f'{os.path.getsize(f)//1024} KB palette {len(names)}', {k.split(':')[1]: v for k, v in c.items() if k.startswith('aurelia:') and 'ore' not in k}, 'chests', c['minecraft:chest'])
print(f'structures: {n} files; problems:', problems if problems else 'none')
print('guards:', dict(ents))
lang = json.load(open(A + '/lang/en_us.json', encoding='utf-8')); miss = []
for b in mod_blocks:
    if not os.path.exists(f'{A}/blockstates/{b}.json'): miss.append(('blockstate', b))
    if f'block.aurelia.{b}' not in lang: miss.append(('lang', b))
for i in mod_items:
    if not os.path.exists(f'{A}/models/item/{i}.json'): miss.append(('item model', i))
print('registry assets:', 'complete' if not miss else miss)
names = {c: set(re.findall(r'public static final RegistryObject<.*> (\w+) =', s)) for c, s in src.items()}
bad = [(os.path.basename(f), c, m) for f in glob.glob(J + '/**/*.java', recursive=True) for c, known in names.items()
       for m in re.findall(c + r'\.([A-Z_]+)\b', open(f).read()) if m not in known and m not in ('BLOCKS', 'ITEMS', 'ENTITIES')]
print('java registry references:', 'all resolve' if not bad else bad)
allj = glob.glob(R + '/**/*.json', recursive=True); badj = 0
for f in allj:
    try: json.load(open(f, encoding='utf-8'))
    except Exception as e: badj += 1; print('BAD JSON', f, e)
files = {os.path.relpath(os.path.join(r, f), D) for r, _, fs in os.walk(D) for f in fs}
def known(x):
    if x in mod_blocks or x in mod_items or x in mod_ents: return True
    c = [f'{d}/{x}.json' for d in ('dimension', 'dimension_type', 'worldgen/biome', 'worldgen/noise_settings', 'worldgen/structure', 'loot_tables', 'tags/worldgen/biome',
                                   'worldgen/placed_feature', 'worldgen/configured_feature', 'worldgen/structure_set')] + [f'structures/{x}.nbt']
    return any(y in files for y in c) or (x.endswith('/start') and f'worldgen/template_pool/{x}.json' in files)
missing = {(os.path.relpath(f, R), m) for f in glob.glob(R + '/data/**/*.json', recursive=True) for m in re.findall(r'aurelia:([a-z0-9_/]+)', open(f).read()) if not known(m)}
print(f'JSON: {len(allj)} files, {"all valid" if not badj else badj}; data ids:', 'all resolve' if not missing else sorted(missing))
mm = open(J + '/client/MobModels.java').read(); pr = []
for key, nm in re.findall(r'public static final String\[\] (\w+)_NAMES = \{([^}]*)\}', mm):
    a = nm.count('"') // 2; b = re.search(r'%s_ANIMS = \{([^}]*)\}' % key, mm).group(1).count('"') // 2
    body = mm[mm.index(f'public static LayerDefinition {key.lower()}()'):]; body = body[:body.index('return LayerDefinition')]
    if not (a == b == body.count('addOrReplaceChild')): pr.append((key, a, b))
    if not os.path.exists(f'{A}/textures/entity/{key.lower()}_glow.png'): pr.append((key, 'no glow texture'))
print('MobModels:', 'consistent, glow textures present' if not pr else pr)
