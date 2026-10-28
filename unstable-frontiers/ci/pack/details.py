"""Targeted dump of the pack details the addon design depends on. python3 details.py pack"""
import json, os, re, sys, zipfile, glob

P = sys.argv[1]
MODS = f'{P}/mods'
OV = f'{P}/overrides'


def jar(prefix):
    for f in os.listdir(MODS):
        if f.lower().startswith(prefix):
            return zipfile.ZipFile(os.path.join(MODS, f))
    return None


def section(t):
    print(f'\n######## {t}', flush=True)


def show(path, keep=None, limit=400):
    if not os.path.exists(path):
        print('  (missing)', path)
        return
    lines = open(path, encoding='utf-8', errors='replace').read().splitlines()
    out = [l for l in lines if (keep is None or re.search(keep, l))]
    print(f'  {path} ({len(lines)} lines, showing {min(len(out), limit)})')
    for l in out[:limit]:
        print('   ', l[:300])


section('pack override files (all)')
for root, dirs, files in os.walk(OV):
    for f in files:
        p = os.path.join(root, f)
        print('  ', os.path.relpath(p, OV), os.path.getsize(p))

section('antarchy mob config as shipped by the pack (health / damage / spawn lines)')
show(f'{OV}/config/antarchy/antarchy_mobs.toml', r'^\s*\[|health|attackDamage|armor|followRange|Spawn|spawn|enabled|Range', 900)
section('antarchy tools config')
show(f'{OV}/config/antarchy/antarchy_tools.toml', None, 500)
section('antarchy misc config')
show(f'{OV}/config/antarchy/antarchy_misc.toml', None, 300)

for name in ('morph', 'infernal', 'lootr', 'integrated', 'boogaloo', 'apothic', 'bettercombat', 'waystones', 'iceandfire', 'viltrumite', 'marvel', 'curios'):
    hits = [p for p in glob.glob(f'{OV}/config/**/*', recursive=True) if name in p.lower() and os.path.isfile(p)]
    for p in hits[:6]:
        section(f'config {os.path.relpath(p, OV)}')
        show(p, None, 160)

section('kubejs scripts')
for p in sorted(glob.glob(f'{OV}/kubejs/**/*.js', recursive=True)):
    print('  ---', os.path.relpath(p, OV))
    for l in open(p, encoding='utf-8', errors='replace').read().splitlines()[:80]:
        print('    ', l[:240])

z = jar('antarchy-')
section('antarchy: Better Combat weapon attributes')
for n in z.namelist():
    if '/weapon_attributes/' in n and n.endswith('.json'):
        print('  ', n, z.read(n).decode()[:200].replace('\n', ' '))
section('antarchy: gear recipes (ultimate, nightmare, blood crystal, royal, primordial, tigers eye, wings, elytra, springy)')
for n in sorted(z.namelist()):
    if n.startswith('data/antarchy/recipe/') and re.search(r'ultimate|nightmare|blood|royal|primordial|tigers_eye|wing|elytra|springy|bertha|whip|critter|bug_spray|temporal|scorpion|hercules|mantis|chitin', n):
        try:
            d = json.loads(z.read(n))
        except Exception:
            print('  (unreadable)', n)
            continue
        keys = d.get('key') or {}
        ing = d.get('ingredients') or []
        def nm(x):
            if isinstance(x, dict):
                return x.get('item') or x.get('tag') or str(x)
            if isinstance(x, list):
                return '|'.join(nm(i) for i in x)
            return str(x)
        desc = ' '.join(d.get('pattern', [])) + ' ' + ', '.join(f'{k}={nm(v)}' for k, v in keys.items()) + ' ' + ', '.join(nm(i) for i in ing)
        for k in ('base', 'addition', 'template'):
            if k in d:
                desc += f' {k}={nm(d[k])}'
        print(f'  {n.split("/")[-1]}: [{d.get("type")}] {desc} -> {nm(d.get("result"))}')
section('antarchy: entity loot tables of the frontier creatures')
for e in ('mantis', 'alpha_mantis', 'scorpion', 'emperor_scorpion', 'springbug', 'wasp', 'brutalfly', 'stratoshark', 'nightmare', 'hercules_beetle', 'basilisk', 'manticore', 'toreterror', 'spit_bug', 'stink_bug', 'bed_bug', 'termite', 'red_ant', 'flytrap', 'crawling_blight', 'skulking_fright', 'molevore'):
    n = f'data/antarchy/loot_table/entities/{e}.json'
    if n in z.namelist():
        try:
            d = json.loads(z.read(n))
        except Exception:
            print('  (unreadable)', n)
            continue
        items = []
        for pool in d.get('pools', []):
            for en in pool.get('entries', []):
                items.append(en.get('name', en.get('type')))
        print(f'  {e}: {", ".join(items)}')
    else:
        print(f'  {e}: (no loot table at {n})')
section('antarchy: tags that matter (c:bosses, horde, arthropods, nightmare_no_attack)')
for n in z.namelist():
    if re.search(r'tags/entity_type/(arthropods|horde_bosses|nightmare_no_attack|spell_resistant_boss)\.json$', n) or n == 'data/c/tags/entity_type/bosses.json':
        try:
            print('  ', n, json.loads(z.read(n)).get('values'))
        except Exception:
            print('  (unreadable)', n)
section('antarchy: morph data files')
print('  ', ', '.join(sorted(n.split('/')[-1][:-5] for n in z.namelist() if n.startswith('data/antarchy/morph/'))))
mz = jar('morph-')
for n in mz.namelist():
    if n.startswith('data/antarchy/morph/') and re.search(r'nightmare|mantis|brutalfly|stratoshark|scorpion|wasp', n):
        print('  ', n, mz.read(n).decode()[:600].replace('\n', ' '))
section('antarchy: structures and worldgen structure sets')
print('  ', ', '.join(sorted({n.split('/')[3] for n in z.namelist() if n.startswith('data/antarchy/structure/') and n.count('/') > 3})))

bz = jar('boogaloo_core')
section('boogaloo_core: integrated_boogaloo worldgen and structure spawners')
for n in sorted(bz.namelist()):
    if n.startswith('data/integrated_boogaloo/') or 'integrated_structure_spawners' in n or n.startswith('data/antarchy/'):
        print('  ', n, bz.read(n).decode()[:300].replace('\n', ' ') if n.endswith('.json') and ('spawners' in n or 'biome_modifier' in n or 'dimension' in n) else '')

sz = jar('integrated_superheroes')
section('integrated_superheroes: what serums and the gauntlet cost (recipe ingredients)')
for n in sorted(sz.namelist()):
    if n.startswith('data/integrated_superheroes/recipe/') and re.search(r'syringe|gauntlet|stone|reactor', n):
        try:
            d = json.loads(sz.read(n))
        except Exception:
            print('  (unreadable)', n)
            continue
        def nm(x):
            if isinstance(x, dict):
                return x.get('item') or x.get('tag') or str(x)
            if isinstance(x, list):
                return '|'.join(nm(i) for i in x)
            return str(x)
        keys = d.get('key') or {}
        print(f'  {n.split("/")[-1]}: {" ".join(d.get("pattern", []))} ' + ', '.join(f'{k}={nm(v)}' for k, v in keys.items()) + ' ' + ', '.join(nm(i) for i in d.get('ingredients', [])))
section('integrated_superheroes: loot modifiers and tags')
for n in sorted(sz.namelist()):
    if 'loot_modifiers' in n or '/tags/' in n:
        print('  ', n, sz.read(n).decode()[:300].replace('\n', ' '))
