"""Names the jars in a mods folder that tried to load client-only classes on a dedicated server, from a server console
log (stack frames 'TRANSFORMER/<modid>@<version>' near 'invalid dist DEDICATED_SERVER') and crash reports ('Mod file:').

python3 client_only_culprits.py run/mods server_console.log run/crash-reports/*.txt
"""
import os
import re
import sys
import zipfile

try:
    import tomllib
except ImportError:
    tomllib = None

mods_dir, logs = sys.argv[1], sys.argv[2:]
ids = set()
files = set()
for path in logs:
    try:
        lines = open(path, errors='replace').read().splitlines()
    except OSError:
        continue
    for i, line in enumerate(lines):
        if 'invalid dist DEDICATED_SERVER' not in line:
            continue
        for near in lines[max(0, i - 8):i + 40]:
            m = re.search(r'run/mods/([^ ]+\.jar)', near)
            if m:
                files.add(m.group(1))
            for mid in re.findall(r'TRANSFORMER/([a-z0-9_]+)@', near):
                if mid not in ('minecraft', 'neoforge'):
                    ids.add(mid)
            if 'Caused by' in near and near is not line:
                pass
for f in os.listdir(mods_dir):
    if not f.endswith('.jar') or f in files:
        continue
    try:
        z = zipfile.ZipFile(os.path.join(mods_dir, f))
        for n in ('META-INF/neoforge.mods.toml', 'META-INF/mods.toml'):
            if n in z.namelist():
                t = tomllib.loads(z.read(n).decode('utf-8', 'replace'))
                if any(m.get('modId') in ids for m in t.get('mods', [])):
                    files.add(f)
                break
    except Exception:
        pass
for f in sorted(files):
    if f != 'unstable_frontiers' and os.path.exists(os.path.join(mods_dir, f)):
        print(os.path.join(mods_dir, f))
