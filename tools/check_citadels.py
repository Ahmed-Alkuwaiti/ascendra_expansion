"""Route and flooding checks for the act two and act three citadels (seals treated as open, as they are once their guards fall)."""
import check_struct as cs

STRUCT = __import__('paths').RES + '/data/aurelia/structures/'
CASES = [('tidewrack_citadel', 'coral_seal', (32, 24, 58), 22), ('rimefast_citadel', 'rime_seal', (32, 13, 59), None),
         ('sunscar_citadel', 'sun_seal', (32, 9, 62), None),
         ('paradox_keep', 'paradox_seal', (48, 10, 95), None), ('spore_cathedral', 'root_seal', (48, 7, 90), None),
         ('convergence_gate', 'none', (40, 7, 76), None)]
import json
import os
OFFS = json.load(open(os.path.join(os.path.dirname(__file__), '_cores', 'offsets.json')))   # how far fortify.py moved each keep
ok = True
for name, seal, start, water in CASES:
    b, size = cs.load(STRUCT + name + '.nbt')
    m = OFFS.get(name, 0)
    start = (start[0] + m, start[1], start[2] + m)
    b = {k: ('air' if v == seal else v) for k, v in b.items()}
    targets = [k for k, v in b.items() if v in ('waygate', 'chest', 'hush_stone', 'tide_bell', 'lectern', 'sun_mirror', 'sunwell', 'clock_dial', 'spore_valve', 'relic_pedestal')]
    bad = []
    for k in targets:
        if not cs.walk(b, start, lambda p, k=k: abs(p[0] - k[0]) + abs(p[2] - k[2]) <= 2 and -1 <= k[1] - p[1] <= 4)[0]:
            bad.append((b[k], k))
    gate = (size[0] // 2, 1, size[2] - 2)                             # and from outside the fortress gate to the keep's door
    while gate[1] < size[1] and not (cs.passable(b.get(gate)) and not cs.passable(b.get((gate[0], gate[1] - 1, gate[2])))):
        gate = (gate[0], gate[1] + 1, gate[2])
    if m and not cs.walk(b, gate, lambda p: abs(p[0] - start[0]) + abs(p[2] - start[2]) <= 2 and abs(p[1] - start[1]) <= 3)[0]:
        bad.append(('fortress gate to keep', gate))
    leaks = cs.leaks(b, water) if water is not None else []
    ok &= not bad and not leaks
    print(f'{name}: {len(targets)} targets, unreachable {bad if bad else "none"}' + (f', flood risks {len(leaks)}' if water is not None else ''))
print('ALL OK' if ok else 'PROBLEMS')
