"""Route check for the lieutenants' lairs: from the way in to the Lair Seal, on foot."""
import re

import check_struct as cs
import paths
from lieutenants import LIEUTENANTS

STRUCT = paths.RES + '/data/aurelia/structures/'
LAYOUT = open(paths.JAVA + '/world/LairLayout.java').read()
INSET = {'arena': 2, 'temple': 2, 'spire': 8, 'pit': 3, 'maw': 2}
ok = True
for lt in LIEUTENANTS:
    m = re.search(r'case "%s" -> new int\[\] \{([^}]*)\}' % lt['id'], LAYOUT)
    w, h, l, floor, sx, sy, sz, bx, by, bz = (int(v) for v in m.group(1).split(','))
    b, size = cs.load(STRUCT + f'lair_{lt["id"]}.nbt')
    start = (w // 2, floor, l - INSET[lt['lair']])
    while start[1] < h and not (cs.passable(b.get(start)) and not cs.passable(b.get((start[0], start[1] - 1, start[2])))):
        start = (start[0], start[1] + 1, start[2])
    found, n = cs.walk(b, start, lambda p: abs(p[0] - sx) + abs(p[2] - sz) <= 2 and -1 <= sy - p[1] <= 2)
    ok &= found is not None
    print(f'lair_{lt["id"]:20s} {lt["lair"]:7s} seal {"reached" if found else "UNREACHABLE"} ({n} cells searched)')
print('ALL OK' if ok else 'PROBLEMS')
