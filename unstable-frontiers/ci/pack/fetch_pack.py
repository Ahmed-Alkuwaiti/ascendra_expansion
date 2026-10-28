"""Finds the Integrated Boogaloo modpack, downloads its newest release and every mod in it, and prints what it contains.

Run on CI (it needs CurseForge and Modrinth). Writes pack/manifest.json, pack/mods/*.jar, pack/overrides/ and pack/report.txt.
Tries Modrinth first (open API, direct file URLs), then CurseForge's public website API (no key).
"""
import json, os, sys, time, urllib.request, urllib.parse, zipfile, io

OUT = sys.argv[1] if len(sys.argv) > 1 else 'pack'
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) unstable-frontiers-ci', 'Accept': 'application/json'}
os.makedirs(f'{OUT}/mods', exist_ok=True)
log = open(f'{OUT}/report.txt', 'w')


def say(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True)
    log.write(s + '\n')


def get(url, binary=False, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
                return data if binary else json.loads(data)
        except Exception as e:
            say(f'  GET {url} failed ({e}); try {i + 1}/{tries}')
            time.sleep(3 * (i + 1))
    return None


def modrinth():
    q = urllib.parse.quote('integrated boogaloo')
    res = get(f'https://api.modrinth.com/v2/search?query={q}&facets=%5B%5B%22project_type%3Amodpack%22%5D%5D')
    if not res:
        return False
    say('modrinth search hits:', len(res.get('hits', [])))
    for h in res.get('hits', [])[:5]:
        say('modrinth hit:', h['slug'], '|', h['title'], '| by', h.get('author'))
    hits = [h for h in res.get('hits', []) if 'boogaloo' in h['slug']]
    if not hits:
        return False
    slug = hits[0]['slug']
    vers = get(f'https://api.modrinth.com/v2/project/{slug}/version')
    v = vers[0]
    say('MODRINTH PACK', slug, 'version', v['version_number'], v['game_versions'], v['loaders'], v['date_published'])
    f = [x for x in v['files'] if x['filename'].endswith('.mrpack')][0]
    z = zipfile.ZipFile(io.BytesIO(get(f['url'], binary=True)))
    idx = json.loads(z.read('modrinth.index.json'))
    json.dump(idx, open(f'{OUT}/manifest.json', 'w'), indent=1)
    say('dependencies:', idx.get('dependencies'))
    for fe in idx['files']:
        env = fe.get('env', {})
        name = os.path.basename(fe['path'])
        if not fe['path'].startswith('mods/'):
            continue
        data = get(fe['downloads'][0], binary=True)
        if data:
            open(f'{OUT}/mods/{name}', 'wb').write(data)
        say('MOD', name, '| server:', env.get('server', '?'), '| client:', env.get('client', '?'))
    for n in z.namelist():
        for pre in ('overrides/', 'server-overrides/'):
            if n.startswith(pre) and not n.endswith('/'):
                p = f'{OUT}/overrides/' + n[len(pre):]
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, 'wb').write(z.read(n))
    return True


def curseforge():
    base = 'https://www.curseforge.com/api/v1/mods'
    res = get(f'{base}/search?gameId=432&index=0&classId=4471&filterText=integrated%20boogaloo&pageSize=10&sortField=1')
    if not res:
        return False
    data = res.get('data', res)
    for m in data[:5]:
        say('curseforge hit:', m.get('id'), m.get('slug'), m.get('name'))
    pick = [m for m in data if 'boogaloo' in (m.get('slug') or '')]
    if not pick:
        return False
    pid = pick[0]['id']
    files = get(f'{base}/{pid}/files?pageIndex=0&pageSize=20&sort=dateCreated&sortDescending=true&removeAlphas=false')
    fl = files.get('data', files)
    for f in fl[:8]:
        say('pack file:', f.get('id'), f.get('fileName') or f.get('displayName'), f.get('dateCreated') or f.get('fileDate'),
            'server pack:', f.get('serverPackFileId'))
    f = fl[0]
    say('CURSEFORGE PACK', pid, f.get('fileName') or f.get('displayName'), f.get('id'))
    z = zipfile.ZipFile(io.BytesIO(get(f'{base}/{pid}/files/{f["id"]}/download', binary=True)))
    man = json.loads(z.read('manifest.json'))
    json.dump(man, open(f'{OUT}/manifest.json', 'w'), indent=1)
    say('minecraft:', man['minecraft'])
    for e in man['files']:
        info = get(f'{base}/{e["projectID"]}/files/{e["fileID"]}')
        info = (info or {}).get('data', info) or {}
        name = info.get('fileName') or f'{e["projectID"]}-{e["fileID"]}.jar'
        if name.endswith('.jar'):
            data = get(f'{base}/{e["projectID"]}/files/{e["fileID"]}/download', binary=True)
            if data:
                open(f'{OUT}/mods/{name}', 'wb').write(data)
        say('MOD', name, '| project', e['projectID'], '| file', e['fileID'], '| required', e.get('required'))
    over = man.get('overrides', 'overrides') + '/'
    for n in z.namelist():
        if n.startswith(over) and not n.endswith('/'):
            p = f'{OUT}/overrides/' + n[len(over):]
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'wb').write(z.read(n))
    return True


def cdn(fid, name):
    q = urllib.parse.quote(name)
    return f'https://mediafilez.forgecdn.net/files/{fid // 1000}/{fid % 1000}/{q}'


def cfwidget():
    """CFWidget mirrors CurseForge project and file listings without an API key; files come from CurseForge's CDN."""
    proj = get('https://api.cfwidget.com/minecraft/modpacks/integrated-boogaloo')
    if not proj or 'files' not in proj:
        say('cfwidget: no project', str(proj)[:300])
        return False
    say('CFWIDGET PACK', proj.get('id'), proj.get('title'), '| files listed:', len(proj['files']))
    files = sorted(proj['files'], key=lambda f: f.get('uploaded_at', ''), reverse=True)
    for f in files[:8]:
        say('  pack file:', f['id'], f['name'], f.get('uploaded_at'), f.get('versions'), f.get('type'))
    main = [f for f in files if f['name'].endswith('.zip') and 'server' not in f['name'].lower()] or files
    f = main[0]
    data = get(cdn(f['id'], f['name']), binary=True)
    if not data:
        return False
    z = zipfile.ZipFile(io.BytesIO(data))
    man = json.loads(z.read('manifest.json'))
    json.dump(man, open(f'{OUT}/manifest.json', 'w'), indent=1)
    say('PACK FILE', f['name'], '| minecraft', man['minecraft'], '| pack version', man.get('version'))
    names = {}
    for e in man['files']:
        pid, fid = e['projectID'], e['fileID']
        info = get(f'https://api.cfwidget.com/{pid}', tries=3) or {}
        hit = [x for x in info.get('files', []) if x.get('id') == fid]
        title = info.get('title', '?')
        if not hit:
            say('MOD ?', pid, fid, title, '(file not in mirror listing)')
            continue
        name = hit[0]['name']
        names[pid] = name
        jar = get(cdn(fid, name), binary=True, tries=3)
        if jar:
            open(f'{OUT}/mods/{name}', 'wb').write(jar)
        say('MOD', name, '|', title, '| project', pid, '| file', fid, '| ok' if jar else '| DOWNLOAD FAILED')
    over = man.get('overrides', 'overrides') + '/'
    for n in z.namelist():
        if n.startswith(over) and not n.endswith('/'):
            p = f'{OUT}/overrides/' + n[len(over):]
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'wb').write(z.read(n))
    return True


ok = modrinth() or cfwidget() or curseforge()
say('PACK FETCHED' if ok else 'PACK NOT FOUND')
sys.exit(0 if ok else 1)
