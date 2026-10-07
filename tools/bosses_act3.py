"""Act three Wardens: Vexor, the Hour Eater (the Clockwork Rift) and the Bloom Mother (the Mycelial Deep).

Same conventions as bosses_v3 and bosses_act2: units of 1/16 block, y up, front toward +z; a child's pivot is relative to
its parent's pivot in the parent's rotated frame; rotation is Rz * Ry * Rx. A part rotated by (0, -a + pi/2, 0) has its
local +x along the tangent and its local +z pointing outward, at angle a round the y axis.
"""
import math

from bosses_act2 import scale_subtree


def ring(P, add, name, parent, radius, segs, style, tilt, anim, teeth_style='brass_d', studs='gold_glow', gap=()):
    """A rotating armillary ring: a tilted root, a spinning child, and segments laid round it with gear teeth and glowing studs."""
    add(P(name, (2, 2, 2), (-1, -1, -1), (0, 0, 0), rot=tilt, parent=parent, style='void'))
    add(P(name + 'Spin', (2, 2, 2), (-1, -1, -1), (0, 0, 0), parent=name, style='void', anim=anim))
    seg_len = int(2 * math.pi * radius / segs) + 2
    for i in range(segs):
        if i in gap:
            continue
        a = i * 2 * math.pi / segs
        s = f'{name}Seg{i}'
        add(P(s, (seg_len, 5, 4), (-seg_len / 2, -2.5, -2), (radius * math.cos(a), 0, radius * math.sin(a)), rot=(0, -a + math.pi / 2, 0),
              parent=name + 'Spin', style=style))
        if i % 2 == 0:
            add(P(s + 'Tooth', (4, 5, 4), (-2, -2.5, 1.5), parent=s, style=teeth_style))
        else:
            add(P(s + 'Stud', (2, 1, 2), (-1, 2.4, -1), parent=s, style=studs))


# ====================================================================================== VEXOR
def vexor(P):
    """A colossal clockwork eye: an iron core split by a burning violet iris and a slit pupil, a ring of brass fangs round it,
    three armillary rings turning on three axes, six clock-hand blades orbiting outside them, and pendulums on chains below."""
    parts = []
    add = parts.append
    IRON, BRASS = 'iron_dk', 'brass_d'

    add(P('core', (40, 40, 34), (-20, -20, -17), (0, 66, 0), style=IRON, anim='head'))
    add(P('coreX', (46, 28, 26), (-23, -14, -13), parent='core', style=IRON))
    add(P('coreY', (28, 46, 26), (-14, -23, -13), parent='core', style=IRON))
    add(P('coreZ', (28, 28, 40), (-14, -14, -22), parent='core', style=IRON))
    for k, (x, y, z) in enumerate([(-23, 6, -4), (22, -6, 3), (2, 23, -8), (-6, -23, 5), (13, 13, -17), (-14, -6, -17)]):
        add(P(f'seam{k}', (1, 9, 1), (x, y - 4, z), rot=(0, 0, 0.6 * (k % 3 - 1)), parent='core', style='rift_glow'))
    for k, (x, y, z, s) in enumerate([(-24, -4, -6, 8), (22, 2, -4, 8), (-4, 22, -5, 9), (4, -24, -4, 8), (-4, -4, -23, 10)]):
        add(P(f'rivet{k}', (s, s, 2) if z == -23 else ((2, s, s) if abs(x) >= 22 else (s, 2, s)), (x, y, z), parent='core', style=BRASS))
    # ---- the eye: a burning iris, a slit pupil, brass lids, and fangs all round the socket
    for k, (w, h) in enumerate([(36, 22), (30, 30), (22, 36)]):            # a round socket, built from three crossing plates
        add(P(f'socket{k}', (w, h, 3), (-w / 2, -h / 2, 16), parent='core', style='void'))
    for k, (w, h) in enumerate([(30, 18), (25, 25), (18, 30)]):
        add(P(f'iris{k}', (w, h, 1), (-w / 2, -h / 2, 18.2 + k * 0.01), parent='core', style='rift_glow', anim='pulse'))
    for k, (w, h) in enumerate([(18, 12), (15, 15), (12, 18)]):
        add(P(f'irisInner{k}', (w, h, 1), (-w / 2, -h / 2, 18.6 + k * 0.01), parent='core', style='rift_glow2'))
    for i in range(8):
        a = i * math.pi / 8
        add(P(f'irisRay{i}', (28, 1, 1), (-14, -0.5, 18.9), rot=(0, 0, a), parent='core', style='rift_glow'))
    add(P('pupil', (5, 24, 1), (-2.5, -12, 19.2), parent='core', style='void'))
    add(P('glint', (3, 3, 1), (5, 6, 19.4), parent='core', style='glow_w'))
    add(P('lidUp', (44, 8, 12), (-22, -4, 0), (0, 18, 12), rot=(-0.35, 0, 0), parent='core', style=BRASS))
    add(P('lidLow', (42, 7, 11), (-21, -3.5, 0), (0, -18, 12), rot=(0.35, 0, 0), parent='core', style=BRASS))
    for i in range(20):
        a = i * 2 * math.pi / 20
        ln = 12 if i % 2 == 0 else 8
        add(P(f'fang{i}', (3, ln, 3), (-1.5, -ln, -1.5), (19 * math.cos(a), 19 * math.sin(a), 18), rot=(0.3, 0, a - math.pi / 2),
              parent='core', style='bone'))
    # spikes from the back of the core, venting violet
    for k, (rx, rz, ln) in enumerate([(-0.9, 0.0, 20), (-1.2, 0.6, 16), (-1.2, -0.6, 16), (-0.6, 1.1, 14), (-0.6, -1.1, 14)]):
        add(P(f'vent{k}', (6, ln + 8, 6), (-3, 0, -3), (0, 0, -18), rot=(rx, 0, rz), parent='core', style=IRON))
        add(P(f'vent{k}Glow', (4, 5, 4), (-2, ln + 8, -2), parent=f'vent{k}', style='rift_glow'))

    # ---- three armillary rings on three axes, turning at different speeds
    ring(P, add, 'ringA', 'core', 44, 24, BRASS, (math.pi / 2 - 0.75, 0.0, 0.0), 'spin', gap=(7,))
    ring(P, add, 'ringB', 'core', 52, 28, BRASS, (math.pi / 2, 0.8, 0.0), 'spinR', gap=(3, 15))
    ring(P, add, 'ringC', 'core', 60, 32, IRON, (math.pi / 2 + 0.45, -0.7, 0.0), 'spinS', teeth_style=BRASS, gap=(10,))
    for k, (r, a) in enumerate([(44, 0.4), (44, 2.5), (44, 4.6)]):           # numerals hung from the inner ring
        add(P(f'numeral{k}', (3, 6, 1), (-1.5, -9, -0.5), (r * math.cos(a), 0, r * math.sin(a)), parent='ringASpin', style='gold_glow'))

    # ---- six clock-hand blades orbiting outside the rings
    add(P('bladeRoot', (2, 2, 2), (-1, -1, -1), (0, 0, -6), rot=(math.pi / 2 - 0.2, 0, 0), parent='core', style='void', anim='spinS'))
    for i in range(6):
        a = i * 2 * math.pi / 6
        h = f'hand{i}'
        ln = 34 if i % 2 == 0 else 26
        add(P(h, (7, 3, ln), (-3.5, -1.5, 0), (70 * math.cos(a), (i % 2) * 10 - 5, 70 * math.sin(a)), rot=(0, -a + math.pi / 2, 0),
              parent='bladeRoot', style=IRON))
        add(P(h + 'Edge', (1, 1, ln - 2), (-0.5, 1.5, 1), parent=h, style='gold_glow'))
        add(P(h + 'Edge2', (1, 1, ln - 2), (2.5, -0.5, 1), parent=h, style='gold_glow'))
        add(P(h + 'Tip', (13, 3, 13), (-6.5, -1.5, -6.5), (0, 0, ln + 5), rot=(0, math.pi / 4, 0), parent=h, style=BRASS))
        add(P(h + 'TipGlow', (5, 4, 5), (-2.5, -2, -2.5), (0, 0, ln + 5), rot=(0, math.pi / 4, 0), parent=h, style='rift_glow'))
        add(P(h + 'Hub', (12, 4, 12), (-6, -2, -6), parent=h, style=BRASS))
        add(P(h + 'HubGlow', (4, 5, 4), (-2, -2.5, -2), parent=h, style='rift_glow'))
        add(P(h + 'Tail', (5, 3, 14), (-2.5, -1.5, -16), parent=h, style=IRON))

    # ---- chains and pendulums hanging from the core
    for k, (x, z) in enumerate([(-10, -6), (10, -6), (0, -12), (-6, 8), (7, 8)]):
        c = f'chain{k}'
        add(P(c, (2, 7, 2), (-1, -7, -1), (x * 1.5, -21, z * 1.5), parent='core', style='steel', anim='sway'))
        prev = c
        for j in range(1, 4 + k % 2):
            add(P(f'{c}L{j}', (2, 7, 2), (-1, -7, -1), (0, -7, 0), rot=(0.05, 0, 0.05 * (-1) ** j), parent=prev, style='steel'))
            prev = f'{c}L{j}'
        add(P(c + 'Weight', (10, 10, 3), (-5, -10, -1.5), (0, -7, 0), parent=prev, style=BRASS))
        add(P(c + 'Face', (8, 8, 1), (-4, -9, 1.6), (0, -7, 0), parent=prev, style='clockface'))
        add(P(c + 'FaceHand', (1, 4, 1), (-0.5, -5, 2.4), (0, -7, 0), parent=prev, style='void'))
    return parts


# ====================================================================================== THE BLOOM MOTHER
def bloom_mother(P):
    """A fungal horror rooted in the floor: a ring of thick roots, a ribbed stalk swollen with spore sacs, and a crown of ten
    clawed petals that open on a maw ringed with teeth, three barbed tongues and a beating magenta throat."""
    parts = []
    add = parts.append
    ROOT, FLESH = 'root_c', 'flesh_p'

    add(P('rootMass', (44, 9, 44), (-22, 0, -22), (0, 0, 0), style=ROOT))
    add(P('rootMass2', (34, 6, 34), (-17, 9, -17), parent='rootMass', style='flesh_d'))
    for i in range(16):
        a = i * 2 * math.pi / 16 + (0.1 if i % 2 else 0)
        r = f'root{i}'
        w = 9 if i % 2 == 0 else 7
        add(P(r, (w, 6, 22), (-w / 2, -3, 0), (19 * math.cos(a), 4, 19 * math.sin(a)), rot=(0.12, -a + math.pi / 2, 0), parent='rootMass',
              style=ROOT, anim='sway'))
        add(P(r + 'B', (w - 2, 5, 22), (-(w - 2) / 2, -2.5, 0), (0, 0, 20), rot=(0.12, 0.25 * (-1) ** i, 0), parent=r, style=ROOT))
        add(P(r + 'C', (w - 4, 4, 18), (-(w - 4) / 2, -2, 0), (0, 0, 21), rot=(0.1, -0.3 * (-1) ** i, 0), parent=r + 'B', style='flesh_d'))
        add(P(r + 'Barb', (2, 5, 2), (-1, 0, -1), (0, 2, 14), rot=(-0.6, 0, 0), parent=r + 'C', style='bone'))
        if i % 3 == 0:
            add(P(r + 'Vein', (1, 1, 18), (-0.5, 3, 1), parent=r, style='bloom_glow'))

    # ---- the stalk, leaning forward, swollen with glowing spore sacs
    add(P('stemA', (30, 24, 30), (-15, 0, -15), (0, 9, 0), style=FLESH))
    for k in range(4):
        add(P(f'ribA{k}', (32, 3, 32), (-16, 3 + 6 * k, -16), parent='stemA', style=ROOT))
    add(P('stemB', (24, 22, 24), (-12, 0, -12), (0, 23, 1), rot=(0.18, 0, 0), parent='stemA', style=FLESH))
    for k in range(3):
        add(P(f'ribB{k}', (26, 3, 26), (-13, 3 + 6 * k, -13), parent='stemB', style=ROOT))
    for k, (x, z) in enumerate([(-15.5, -5), (15.5, 3), (-6, -15.5), (7, 15.5), (15.5, -10), (-15.5, 10)]):
        add(P(f'veinA{k}', (1, 22, 1), (x, 1, z), parent='stemA', style='bloom_glow'))
    for k, (a, y) in enumerate([(0.4, 8), (1.7, 14), (2.9, 6), (4.0, 16), (5.2, 10), (6.0, 18)]):
        s = f'sac{k}'
        add(P(s, (3, 8, 3), (-1.5, 0, -1.5), (15 * math.cos(a), y, 15 * math.sin(a)), rot=(0.7 * math.sin(a), 0, -0.7 * math.cos(a)),
              parent='stemA', style=ROOT))
        add(P(s + 'Bulb', (7, 7, 7), (-3.5, 7, -3.5), parent=s, style='bloom_glow', anim='pulse'))
    for k in range(12):                                         # gills hanging under the head
        a = k * 2 * math.pi / 12
        add(P(f'gill{k}', (5, 14 + (k % 3) * 4, 1), (-2.5, -14 - (k % 3) * 4, -0.5), (17 * math.cos(a), 18, 17 * math.sin(a)),
              rot=(0, -a + math.pi / 2, 0), parent='stemB', style='root_c' if k % 2 else 'flesh_d', anim='sway'))

    # ---- the head: a calyx and a maw with two rings of teeth, a burning throat, three tongues
    add(P('head', (38, 10, 38), (-19, -4, -19), (0, 20, 2), rot=(1.05, 0, 0), parent='stemB', style=FLESH, anim='head'))
    add(P('maw', (26, 12, 26), (-13, -3, -13), parent='head', style='void'))
    add(P('throat', (12, 6, 12), (-6, -2, -6), parent='head', style='bloom_glow', anim='pulse'))
    for row, (r, n, ln) in enumerate([(13, 20, 8), (9, 14, 6)]):
        for i in range(n):
            a = i * 2 * math.pi / n + row * 0.2
            add(P(f'tooth{row}_{i}', (2, ln, 2), (-1, 0, -1), (r * math.cos(a), 5 - row * 2, r * math.sin(a)),
                  rot=(-0.9, -a + math.pi / 2, 0), parent='head', style='bone'))
    for t, (x, z, lean) in enumerate([(-4, 2, -0.3), (4, 2, 0.3), (0, -4, 0.0)]):
        prev, piv = 'head', (x, 2, z)
        for j in range(6):
            n = f'tongue{t}_{j}'
            add(P(n, (4 - j // 2, 9, 4 - j // 2), (-(4 - j // 2) / 2, 0, -(4 - j // 2) / 2), piv,
                  rot=(0.18 if j else -0.3, 0, lean if j == 0 else 0.12 * (-1) ** (j + t)), parent=prev, style=FLESH if j % 2 else 'maw',
                  anim='sway' if j == 0 else 'none'))
            prev, piv = n, (0, 8, 0)
        add(P(f'tongue{t}Barb', (4, 6, 4), (-2, 0, -2), piv, rot=(0, math.pi / 4, 0), parent=prev, style='bloom_glow'))
    # stamens: thin stalks round the maw with glowing heads
    for i in range(5):
        a = i * 2 * math.pi / 5 + 0.2
        s = f'stamen{i}'
        add(P(s, (1, 22 + (i % 3) * 5, 1), (-0.5, 0, -0.5), (10 * math.cos(a), 4, 10 * math.sin(a)), rot=(0.35 * math.sin(a), 0, -0.35 * math.cos(a)),
              parent='head', style=ROOT, anim='sway'))
        add(P(s + 'Head', (3, 4, 3), (-1.5, 22 + (i % 3) * 5, -1.5), parent=s, style='bloom_glow', anim='pulse'))

    # ---- ten clawed petals, alternating cream and violet, lined with teeth and glowing veins
    for i in range(10):
        a = i * 2 * math.pi / 10
        p = f'petal{i}'
        st = 'petal_c' if i % 2 else 'petal_p'
        add(P(p, (20, 30, 4), (-10, 0, -2), (17 * math.cos(a), 3, 17 * math.sin(a)), rot=(0.95, -a + math.pi / 2, 0),
              parent='head', style=st, anim='bloom'))
        add(P(p + 'Vein', (1, 26, 1), (-0.5, 2, -2.6), parent=p, style='bloom_glow'))
        add(P(p + 'B', (16, 24, 3), (-8, 0, -1.5), (0, 29, 0), rot=(0.25, 0, 0), parent=p, style=st))
        add(P(p + 'C', (10, 18, 3), (-5, 0, -1.5), (0, 23, 0), rot=(-0.85, 0, 0), parent=p + 'B', style=st))
        add(P(p + 'Claw', (4, 12, 3), (-2, 0, -1.5), (0, 17, 0), rot=(-0.9, 0, 0), parent=p + 'C', style='bone'))
        for k in range(3):
            add(P(f'{p}Tooth{k}', (2, 5, 2), (-1, 0, -1), (-6 + 6 * k, 6 + 7 * k, -2), rot=(-1.1, 0, 0), parent=p, style='bone'))
        for k in range(2):
            add(P(f'{p}BTooth{k}', (2, 4, 2), (-1, 0, -1), (-4 + 8 * k, 10, -1.5), rot=(-1.1, 0, 0), parent=p + 'B', style='bone'))
        add(P(p + 'Spot', (4, 4, 1), (-2, 12, 2.1), parent=p, style='bloom_glow'))
    scale_subtree(parts, 'head', 1.15)
    return parts
