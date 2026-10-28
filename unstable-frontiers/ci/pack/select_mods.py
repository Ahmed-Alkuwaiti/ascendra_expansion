"""Picks the smallest set of pack jars that lets the given mods run on a dedicated server: the targets plus everything they
require, recursively. Copies them into a folder and prints the choice.

python3 select_mods.py pack/mods run/mods antarchy integrated_superheroes ...
"""
import io, os, shutil, sys, zipfile

try:
    import tomllib
except ImportError:
    tomllib = None

src, dst, targets = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(dst, exist_ok=True)
by_id, deps_of = {}, {}
def index(z, f, nested=False):
    """Reads one jar's mod list (and the jars it bundles in META-INF/jarjar, which ship inside it)."""
    for n in ('META-INF/neoforge.mods.toml', 'META-INF/mods.toml'):
        if n in z.namelist():
            try:
                t = tomllib.loads(z.read(n).decode('utf-8', 'replace'))
            except Exception:
                continue
            loader = t.get('modLoader', 'javafml')
            for m in t.get('mods', []):
                mid = m['modId']
                if nested and mid in by_id:
                    continue
                by_id[mid] = f
                deps = [d['modId'] for d in (t.get('dependencies', {}) or {}).get(mid, []) or []
                        if d.get('type', 'required' if d.get('mandatory', True) else 'optional') == 'required'
                        and d.get('side', 'BOTH') in ('BOTH', 'SERVER')]
                # A mod written in another language needs its language provider (e.g. Kotlin for Forge).
                if loader not in ('javafml', 'lowcodefml'):
                    deps.append(loader)
                deps_of[mid] = deps
            break
    for n in z.namelist():
        if n.startswith('META-INF/jarjar/') and n.endswith('.jar'):
            try:
                index(zipfile.ZipFile(io.BytesIO(z.read(n))), f, nested=True)
            except Exception:
                pass


for f in sorted(os.listdir(src)):
    if f.endswith('.jar'):
        index(zipfile.ZipFile(os.path.join(src, f)), f)


def by_name(mid):
    """Language providers and some libraries declare no mod id we can read; fall back to the jar's file name."""
    key = mid.replace('_', '').replace('-', '').lower()
    for f in sorted(os.listdir(src)):
        if f.endswith('.jar') and key in f.replace('_', '').replace('-', '').lower():
            return f
    return None
want, todo, missing = set(), [t for t in targets if t in by_id], [t for t in targets if t not in by_id]
while todo:
    m = todo.pop()
    if m in want:
        continue
    want.add(m)
    for d in deps_of.get(m, []):
        if d in ('minecraft', 'neoforge', 'forge', 'java'):
            continue
        if d in by_id:
            todo.append(d)
        elif by_name(d):
            by_id[d] = by_name(d)
            todo.append(d)
        else:
            missing.append(f'{d} (needed by {m})')
jars = sorted({by_id[m] for m in want})
for j in jars:
    shutil.copy(os.path.join(src, j), dst)
print('SELECTED', len(jars), 'jars for', ', '.join(sorted(want)))
for j in jars:
    print('  ', j)
if missing:
    print('MISSING', '; '.join(missing))
