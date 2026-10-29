"""Answers the questions in api_probe.txt from the pack's jars. Each line is one of:
  javap <jar substring> <class>          public signatures of a class (javap -public)
  list  <jar substring> <regex>          entries of the jar matching the regex
  cat   <jar substring> <entry>          the text of one entry
  jars  <substring>                       jar file names containing the substring
"""
import fnmatch, os, re, subprocess, sys, zipfile

mods, spec = sys.argv[1], sys.argv[2]
jars = sorted(f for f in os.listdir(mods) if f.endswith('.jar'))


def find(sub):
    for j in jars:
        if sub.lower() in j.lower():
            return os.path.join(mods, j)
    return None


for line in open(spec):
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    cmd, *rest = line.split(None, 2)
    print(f'##### {line}')
    if cmd == 'jars':
        print('\n'.join(j for j in jars if rest[0].lower() in j.lower()))
        continue
    jar = find(rest[0])
    if jar is None:
        print('NO JAR', rest[0])
        continue
    z = zipfile.ZipFile(jar)
    if cmd == 'list':
        rx = re.compile(rest[1])
        print('\n'.join(n for n in z.namelist() if rx.search(n))[:20000])
    elif cmd == 'cat':
        try:
            print(z.read(rest[1]).decode('utf-8', 'replace')[:20000])
        except KeyError:
            print('NO ENTRY')
    elif cmd == 'javap':
        r = subprocess.run(['javap', '-public', '-cp', jar, rest[1]], capture_output=True, text=True)
        print((r.stdout + r.stderr)[:20000])
print('##### END')
