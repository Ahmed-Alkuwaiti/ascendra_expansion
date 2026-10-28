"""Prints what every mod jar in a folder declares, and digs into the pack's own mods and anything relevant to the addon.

python3 inspect_jars.py pack/mods
"""
import json, re, sys, zipfile, os, collections

try:
    import tomllib
except ImportError:
    tomllib = None

FOCUS = ('antarchy', 'anthology', 'antos', 'integrated', 'boogaloo', 'morph', 'hero', 'super', 'transform', 'suit', 'power')
DIR = sys.argv[1]


def toml_of(z):
    for n in ('META-INF/neoforge.mods.toml', 'META-INF/mods.toml'):
        if n in z.namelist():
            raw = z.read(n).decode('utf-8', 'replace')
            try:
                return tomllib.loads(raw), raw
            except Exception:
                return None, raw
    if 'fabric.mod.json' in z.namelist():
        return {'fabric': json.loads(z.read('fabric.mod.json'))}, ''
    return None, ''


mods = {}
for f in sorted(os.listdir(DIR)):
    if not f.endswith('.jar'):
        continue
    z = zipfile.ZipFile(os.path.join(DIR, f))
    t, raw = toml_of(z)
    entries = []
    if t and 'mods' in t:
        for m in t['mods']:
            mid = m.get('modId')
            deps = []
            for d in (t.get('dependencies', {}) or {}).get(mid, []) or []:
                req = d.get('type', 'required' if d.get('mandatory', True) else 'optional')
                deps.append((d.get('modId'), req, d.get('versionRange'), d.get('side', 'BOTH')))
            entries.append((mid, str(m.get('version')), m.get('displayName'), deps))
            mods[mid] = (f, deps)
    elif t and 'fabric' in t:
        entries.append((t['fabric'].get('id'), t['fabric'].get('version'), 'FABRIC MOD', []))
    names = z.namelist()
    ns_data = sorted({n.split('/')[1] for n in names if n.startswith('data/') and n.count('/') > 1})
    print(f'JAR {f}')
    for mid, ver, disp, deps in entries:
        manifest_ver = ''
        if '${file.jarVersion}' in ver and 'META-INF/MANIFEST.MF' in names:
            mf = z.read('META-INF/MANIFEST.MF').decode('utf-8', 'replace')
            mm = re.search(r'Implementation-Version: (\S+)', mf)
            manifest_ver = mm.group(1) if mm else ''
        print(f'  MOD {mid} {manifest_ver or ver} "{disp}"')
        req = [f'{d[0]}{d[2] or ""}' for d in deps if d[1] in ('required', True) and d[0] not in ('minecraft', 'neoforge')]
        if req:
            print('    requires:', ', '.join(req))
    if ns_data:
        print('  data namespaces:', ', '.join(ns_data))

print('\n==== FOCUS: the pack\'s own and relevant mods ====')
for f in sorted(os.listdir(DIR)):
    if not f.endswith('.jar') or not any(k in f.lower() for k in FOCUS):
        continue
    z = zipfile.ZipFile(os.path.join(DIR, f))
    names = z.namelist()
    print(f'\n### {f}')
    langs = [n for n in names if re.match(r'assets/[^/]+/lang/en_us\.json$', n)]
    for ln in langs:
        ns = ln.split('/')[1]
        try:
            lang = json.loads(z.read(ln))
        except Exception:
            continue
        groups = collections.defaultdict(list)
        for k, v in lang.items():
            parts = k.split('.')
            if len(parts) == 3 and parts[1] == ns and parts[0] in ('entity', 'item', 'block', 'effect', 'enchantment', 'biome', 'dimension'):
                groups[parts[0]].append(f'{parts[2]}={v}')
        for kind in ('entity', 'item', 'effect', 'enchantment', 'dimension', 'biome'):
            if groups[kind]:
                print(f'  {ns} {kind} ({len(groups[kind])}): ' + '; '.join(groups[kind]))
        print(f'  {ns} blocks: {len(groups["block"])}')
        keys = [k for k in lang if any(w in k.lower() for w in ('ability', 'power', 'suit', 'transform', 'morph', 'hero'))]
        if keys:
            print(f'  {ns} ability-like lang keys ({len(keys)}):', '; '.join(f'{k}={lang[k]}' for k in keys[:120]))
    kinds = collections.Counter()
    for n in names:
        m = re.match(r'data/([^/]+)/([^/]+)/', n)
        if m:
            kinds[(m.group(1), m.group(2))] += 1
    for (ns, kind), c in sorted(kinds.items()):
        print(f'  data {ns}/{kind}: {c}')
    for n in names:
        if re.match(r'data/[^/]+/(dimension|worldgen/structure)/[^/]+\.json$', n) or re.match(r'data/[^/]+/tags/entity_types?/[^/]+\.json$', n):
            print('   ', n)
