"""The finale: the Unmaker, the thing behind the worlds.

Same conventions as the other boss files: units of 1/16 block, y up, front toward +z, a child's pivot is relative to its parent's
pivot in the parent's rotated frame, rotation Rz * Ry * Rx. rot=(-lat, lon, 0) turns a part's local +z to point outward along
latitude lat and longitude lon of a sphere.
"""
import math
import random

from bosses_act2 import scale_subtree
from bosses_act3 import ring

REALM_SHARDS = ['shard_g', 'shard_c', 'shard_v', 'shard_t', 'shard_i', 'shard_r', 'shard_y', 'shard_m']   # the eight borrowed gods


def unmaker(P):
    """A broken colossus round a black hole. A shell of bone-white and black plates bursting outward from the Last Heart, a
    blazing accretion ring, a tall cracked mask with a single burning slit, a halo of eight stolen relic-shards, two vast
    detached hands reaching forward, and a tail of debris falling into the heart."""
    parts = []
    add = parts.append
    rnd = random.Random(9001)
    W, B = 'unmade_w', 'unmade_b'
    HY = 150                                                     # the heart's height above the feet

    # ---- the Last Heart: a black sphere (three crossing blocks), a white-hot core seen through it, two accretion rings
    add(P('heart', (34, 34, 34), (-17, -17, -17), (0, HY, 0), style='abyss'))
    add(P('heartX', (40, 24, 24), (-20, -12, -12), parent='heart', style='abyss'))
    add(P('heartY', (24, 40, 24), (-12, -20, -12), parent='heart', style='abyss'))
    add(P('heartZ', (24, 24, 40), (-12, -12, -20), parent='heart', style='abyss'))
    add(P('heartLight', (10, 10, 2), (-5, -5, 20.2), parent='heart', style='accretion2', anim='pulse'))
    ring(P, add, 'diskA', 'heart', 34, 26, 'accretion', (math.pi / 2 - 0.35, 0.0, 0.25), 'spin', teeth_style='accretion2', studs='accretion2')
    ring(P, add, 'diskB', 'heart', 46, 30, 'accretion3', (math.pi / 2 - 0.35, 0.0, 0.25), 'spinR', teeth_style='accretion', studs='accretion2',
         gap=(4, 11, 19, 26))
    # matter spiralling in
    add(P('infall', (2, 2, 2), (-1, -1, -1), (0, 0, 0), parent='heart', style='void', anim='spinS'))
    for k in range(14):
        a = k * 0.9
        r = 56 - k * 2.4
        s = 7 - k // 3
        add(P(f'infall{k}', (s, s, s), (-s / 2, -s / 2, -s / 2), (r * math.cos(a), (k % 3 - 1) * 6, r * math.sin(a)), rot=(a, a * 0.7, 0),
              parent='infall', style=W if k % 2 else B))

    # ---- the shell: plates on a sphere, blown outward, the front torn open over the heart
    add(P('shell', (2, 2, 2), (-1, -1, -1), (0, 0, 0), parent='heart', style='void', anim='sway'))
    k = 0
    for lat_deg in (-54, -30, -8, 14, 36, 58):
        lat = math.radians(lat_deg)
        n = max(4, int(11 * math.cos(lat)))
        for j in range(n):
            lon = j * 2 * math.pi / n + (0.3 if lat_deg % 2 else 0.0)
            front = math.cos(lon) * math.cos(lat)                  # +z is the front: tear it open
            if front > 0.62 and abs(lat_deg) < 40:
                continue
            if rnd.random() < 0.12:
                continue
            r = 64 + rnd.uniform(0, 14) + (10 if front > 0.3 else 0)
            w = int(30 * max(0.55, math.cos(lat)) + rnd.uniform(-4, 4))
            h = int(26 + rnd.uniform(-4, 6))
            name = f'plate{k}'
            pos = (r * math.cos(lat) * math.sin(lon), r * math.sin(lat), r * math.cos(lat) * math.cos(lon))
            add(P(name, (w, h, 9), (-w / 2, -h / 2, -4.5), pos, rot=(-lat + rnd.uniform(-0.15, 0.15), lon + rnd.uniform(-0.12, 0.12),
                                                                         rnd.uniform(-0.2, 0.2)), parent='shell', style=W if k % 3 else B))
            add(P(name + 'Rim', (w - 4, 3, 4), (-(w - 4) / 2, h / 2 - 1, -2), parent=name, style=B if k % 3 else W))
            ang = rnd.uniform(-0.9, 0.9)
            add(P(name + 'Crack', (2, int(h * 0.8), 1), (-1, -h * 0.4, 4.6), rot=(0, 0, ang), parent=name, style='rift_glow'))
            if k % 4 == 0:
                add(P(name + 'Spike', (5, 5, 16), (-2.5, -2.5, 4), parent=name, style=B))
            k += 1
    # a ribcage of black bars bracing the open front
    for i in range(5):
        y = -30 + i * 15
        add(P(f'rib{i}L', (6, 6, 44), (-3, -3, 0), (-34 + abs(i - 2) * 3, y, 30), rot=(0, 0.75, 0), parent='heart', style=B))
        add(P(f'rib{i}R', (6, 6, 44), (-3, -3, 0), (34 - abs(i - 2) * 3, y, 30), rot=(0, -0.75, 0), parent='heart', style=B))
        add(P(f'rib{i}Tip', (3, 3, 10), (-1.5, -1.5, 0), (0, 0, 44), parent=f'rib{i}L', style='rift_glow'))

    # ---- the mask: a tall cracked crest with one burning slit, swept-back horns, a collar of black spikes
    add(P('neck', (2, 2, 2), (-1, -1, -1), (0, HY + 84, 4), style='void'))
    add(P('head', (36, 44, 26), (-18, 0, -13), (0, 0, 0), parent='neck', style=W, anim='head'))
    for i, (w, h, d) in enumerate([(30, 30, 22), (22, 26, 18), (14, 24, 13), (7, 22, 8)]):
        y0 = 44 + sum(hh for (_, hh, _) in [(30, 30, 22), (22, 26, 18), (14, 24, 13), (7, 22, 8)][:i]) - 2 * i
        add(P(f'crest{i}', (w, h, d), (-w / 2, y0, -d / 2 + 1), parent='head', style=W if i % 2 == 0 else 'unmade_w2'))
    add(P('slit', (5, 92, 2), (-2.5, 6, 13.2), parent='head', style='accretion2'))
    add(P('slitGlow', (11, 70, 1), (-5.5, 16, 12.8), parent='head', style='rift_glow'))
    for sx in (-1, 1):
        sn = 'L' if sx < 0 else 'R'
        add(P(f'cheek{sn}', (8, 30, 22), (-4, 0, -11), (sx * 21, 6, 1), rot=(0, 0, sx * 0.12), parent='head', style=B))
        add(P(f'horn{sn}', (8, 8, 46), (-4, -4, -46), (sx * 16, 40, -6), rot=(-0.55, sx * 0.35, 0), parent='head', style=B))
        add(P(f'horn{sn}Tip', (5, 5, 20), (-2.5, -2.5, -20), (0, 0, -46), rot=(-0.4, 0, 0), parent=f'horn{sn}', style=W))
        for c in range(3):
            add(P(f'crack{sn}{c}', (1, 18, 1), (-0.5, 0, 0), (sx * (6 + 4 * c), 8 + 14 * c, 13.4), rot=(0, 0, sx * (0.4 - 0.25 * c)),
                  parent='head', style='rift_glow'))
    for i in range(10):
        a = math.pi * (0.1 + 0.8 * i / 9)
        add(P(f'collar{i}', (6, 30, 6), (-3, 0, -3), (40 * math.cos(a), -4, -18 + 22 * math.sin(a) - 22), rot=(-0.9 * math.sin(a), 0, -1.1 * math.cos(a)),
              parent='neck', style=B))

    scale_subtree(parts, 'neck', 1.3)

    # ---- the halo: eight stolen shards in an arc behind the mask, one per Warden
    add(P('halo', (2, 2, 2), (-1, -1, -1), (0, HY + 132, -44), style='void'))
    for i, st in enumerate(REALM_SHARDS):
        a = math.radians(200 - i * (220 / 7))                    # from lower left, over the top, to lower right
        r = 108
        name = f'shard{i}'
        add(P(name, (11, 30, 11), (-5.5, -15, -5.5), (r * math.cos(a), r * math.sin(a), 0), rot=(0, 0, a - math.pi / 2), parent='halo',
              style=st, anim='sway'))
        add(P(name + 'Tip', (6, 14, 6), (-3, 15, -3), parent=name, style=st))
        add(P(name + 'Mount', (15, 8, 15), (-7.5, -21, -7.5), parent=name, style=B))
        add(P(name + 'Chain', (2, 30, 2), (-1, -51, -1), parent=name, style='iron_dk'))

    # ---- the hands: detached, colossal, reaching. Each: three broken arm-blocks, a palm, five jointed fingers
    for sx in (-1, 1):
        sn = 'L' if sx < 0 else 'R'
        root = f'arm{sn}'
        add(P(root, (2, 2, 2), (-1, -1, -1), (sx * 104, HY + 40, 6), rot=(-0.55, sx * -0.35, sx * 0.55), style='void',
              anim='reachA' if sx < 0 else 'reachB'))
        y = 0
        for s, (w, h, st) in enumerate([(30, 34, B), (26, 30, W), (24, 30, B)]):
            add(P(f'{root}Seg{s}', (w + 6, h, w + 6), (-w / 2, -h, -w / 2), (rnd.uniform(-2, 2), y, rnd.uniform(-2, 2)), rot=(0, 0.3 * s, 0),
                  parent=root, style=st))
            add(P(f'{root}Seg{s}Glow', (w - 6, 3, w - 6), (-(w - 6) / 2, -h - 3, -(w - 6) / 2), (rnd.uniform(-2, 2), y, rnd.uniform(-2, 2)),
                  parent=root, style='rift_glow'))
            y -= h + 8
        hand = f'{root}Hand'
        add(P(hand, (40, 44, 16), (-20, -44, -8), (0, y, 0), rot=(0.35, 0, 0), parent=root, style=W))
        add(P(hand + 'Back', (34, 38, 6), (-17, -40, -12), parent=hand, style=B))
        add(P(hand + 'Rune', (12, 12, 1), (-6, -28, 8.2), parent=hand, style='accretion2'))
        for f in range(4):
            fx = -15 + f * 10
            fl = [22, 26, 24, 19][f]
            fn = f'{hand}F{f}'
            add(P(fn, (10, fl, 10), (-5, -fl, -5), (fx, -44, 0), rot=(0.35, 0, (f - 1.5) * 0.08), parent=hand, style=B if f % 2 else W))
            add(P(fn + 'B', (9, fl - 2, 9), (-4.5, -fl + 2, -4.5), (0, -fl - 1, 0), rot=(0.55, 0, 0), parent=fn, style=W if f % 2 else B))
            add(P(fn + 'C', (8, 14, 8), (-4, -14, -4), (0, -fl + 1, 0), rot=(0.6, 0, 0), parent=fn + 'B', style=B))
            add(P(fn + 'Claw', (3, 8, 3), (-1.5, -8, -1.5), (0, -14, 0), rot=(0.5, 0, 0), parent=fn + 'C', style='rift_glow'))
        th = f'{hand}Thumb'
        add(P(th, (9, 18, 10), (-4.5, -18, -5), (sx * -22, -18, 4), rot=(0.6, 0, sx * -0.9), parent=hand, style=B))
        add(P(th + 'B', (7, 14, 8), (-3.5, -14, -4), (0, -18, 0), rot=(0.5, 0, 0), parent=th, style=W))

    # ---- debris: a slow storm of blocks round the whole thing, and a tail falling up into the heart from below
    add(P('storm', (2, 2, 2), (-1, -1, -1), (0, HY, 0), style='void', anim='spinS'))
    for i in range(22):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(100, 140)
        s = rnd.randint(5, 13)
        add(P(f'debris{i}', (s, s, s), (-s / 2, -s / 2, -s / 2), (r * math.cos(a), rnd.uniform(-90, 110), r * math.sin(a)),
              rot=(rnd.uniform(0, 3), rnd.uniform(0, 3), 0), parent='storm', style=[W, B, B, 'unmade_w2'][i % 4]))
    for i in range(10):
        s = 12 - i
        add(P(f'tail{i}', (s, s, s), (-s / 2, -s / 2, -s / 2), (math.sin(i * 1.3) * (6 + i * 2), -60 - i * 10, math.cos(i * 1.3) * (6 + i * 2)),
              rot=(i * 0.5, i * 0.7, 0), parent='heart', style=B if i % 2 else W, anim='sway'))
    return parts
