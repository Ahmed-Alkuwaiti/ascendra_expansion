"""Route and flooding checks for the three act two citadels (seals treated as open, as they are once their guards fall)."""
import check_struct as cs

STRUCT = __import__('paths').RES + '/data/aurelia/structures/'
CASES = [('tidewrack_citadel', 'coral_seal', (32, 24, 58), 22), ('rimefast_citadel', 'rime_seal', (32, 13, 59), None),
         ('sunscar_citadel', 'sun_seal', (32, 9, 62), None)]
ok = True
for name, seal, start, water in CASES:
    b, size = cs.load(STRUCT + name + '.nbt')
    b = {k: ('air' if v == seal else v) for k, v in b.items()}
    targets = [k for k, v in b.items() if v in ('waygate', 'chest', 'hush_stone', 'tide_bell', 'lectern', 'sun_mirror', 'sunwell')]
    bad = []
    for k in targets:
        if not cs.walk(b, start, lambda p, k=k: abs(p[0] - k[0]) + abs(p[2] - k[2]) <= 2 and -1 <= k[1] - p[1] <= 4)[0]:
            bad.append((b[k], k))
    leaks = cs.leaks(b, water) if water is not None else []
    ok &= not bad and not leaks
    print(f'{name}: {len(targets)} targets, unreachable {bad if bad else "none"}' + (f', flood risks {len(leaks)}' if water is not None else ''))
print('ALL OK' if ok else 'PROBLEMS')
