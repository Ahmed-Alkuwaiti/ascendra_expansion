"""Picks the smallest set of pack jars that lets the given mods run on a dedicated server: the targets plus everything they
require, recursively. Copies them into a folder and prints the choice.

python3 select_mods.py pack/mods run/mods antarchy integrated_superheroes ...
"""
import os, shutil, sys, zipfile

try:
    import tomllib
except ImportError:
    tomllib = None

src, dst, targets = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(dst, exist_ok=True)
by_id, deps_of = {}, {}
for f in os.listdir(src):
    if not f.endswith('.jar'):
        continue
    z = zipfile.ZipFile(os.path.join(src, f))
    for n in ('META-INF/neoforge.mods.toml', 'META-INF/mods.toml'):
        if n in z.namelist():
            try:
                t = tomllib.loads(z.read(n).decode('utf-8', 'replace'))
            except Exception:
                continue
            for m in t.get('mods', []):
                mid = m['modId']
                by_id[mid] = f
                deps_of[mid] = [d['modId'] for d in (t.get('dependencies', {}) or {}).get(mid, []) or []
                                if d.get('type', 'required' if d.get('mandatory', True) else 'optional') == 'required'
                                and d.get('side', 'BOTH') in ('BOTH', 'SERVER')]
            break
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
