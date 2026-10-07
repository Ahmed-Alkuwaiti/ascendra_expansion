"""Menacing boss models. Units of 1/16 block, y up, front toward +z.

A part with a parent has its pivot relative to the parent's pivot and moves with it. Rotation about x: a positive
angle swings a point above the pivot forward (+z); a negative angle swings a hanging limb forward.
"""
import math


def mossback(P):
    """A hunched rot-wood horror: deer skull, open ribcage with a beating heart, claws that reach the ground."""
    parts = []
    add = parts.append

    # ---- legs: bent, thorned, clawed
    for side, sx in (('R', -1), ('L', 1)):
        n = 'leg' + side
        add(P(n, (15, 18, 16), (-7.5, -18, -8), (sx * 14, 42, -2), rot=(-0.25, 0, 0), style='bark_rot', anim='legA' if sx < 0 else 'legB'))
        add(P(n + 'Knee', (17, 7, 17), (-8.5, -22, -8.5), parent=n, style='thorn'))
        add(P(n + 'KneeSpike', (4, 5, 9), (-2, -21, 8), parent=n, style='bone'))
        add(P(n + 'Plate', (4, 14, 14), (sx * 7.5 - 2, -16, -7), parent=n, style='thorn'))
        add(P(n + 'Tatter', (3, 13, 2), (-1.5, -13, -1), (sx * 6, -4, -9), parent=n, style='moss_dk', anim='sway'))
        add(P(n + 'Shin', (12, 20, 12), (-6, -20, -6), (0, -18, 0), rot=(0.5, 0, 0), parent=n, style='bark_d'))
        add(P(n + 'ShinThorn', (3, 4, 7), (-1.5, -12, -13), parent=n + 'Shin', style='bone'))
        add(P(n + 'Foot', (16, 5, 24), (-8, -5, -8), (0, -20, 0), rot=(-0.25, 0, 0), parent=n + 'Shin', style='bark_rot'))
        for i in range(3):
            add(P(f'{n}Claw{i}', (4, 4, 10), (-7 + 5 * i, -5, 16), parent=n + 'Foot', style='bone'))
        add(P(n + 'Spur', (4, 4, 6), (-2, -4, -14), parent=n + 'Foot', style='bone'))

    # ---- torso, leaning forward: pelvis, bare spine, open ribcage around a glowing heart
    add(P('torso', (30, 10, 20), (-15, -2, -10), (0, 42, 0), rot=(0.38, 0, 0), style='bark_rot'))
    add(P('gut', (14, 14, 12), (-7, 8, -6), parent='torso', style='void'))
    for i in range(4):
        add(P(f'vert{i}', (6, 3, 5), (-3, 9 + 3.5 * i, -10), parent='torso', style='bone'))
    add(P('yoke', (42, 12, 24), (-21, 34, -12), parent='torso', style='bark_rot'))
    add(P('backPlate', (36, 16, 4), (-18, 20, -12), parent='torso', style='bark_d'))
    add(P('hollow', (30, 14, 14), (-15, 20, -8), parent='torso', style='void'))
    add(P('heart', (8, 9, 8), (-4, -4, -4), (0, 27, 2), parent='torso', style='glow_y', anim='pulse'))
    for i in range(5):
        y = 20 + 3.1 * i
        for sx, nm in ((-1, 'R'), (1, 'L')):
            add(P(f'rib{nm}{i}', (15, 2, 3), (4 if sx > 0 else -19, y, 7), parent='torso', style='bone'))
            add(P(f'ribSide{nm}{i}', (3, 2, 17), (16 if sx > 0 else -19, y, -9), parent='torso', style='bone'))
    add(P('sternum', (4, 15, 2), (-2, 20, 9), parent='torso', style='bone_d'))
    add(P('mound', (34, 8, 18), (-17, 44, -13), parent='torso', style='moss_dk'))
    for i, (x, ln, rx, rz) in enumerate([(-16, 20, -0.7, 0.5), (-10, 26, -0.6, 0.25), (-4, 18, -0.9, 0.1), (3, 28, -0.5, -0.05),
                                         (9, 22, -0.8, -0.25), (15, 18, -0.6, -0.5), (-7, 14, -1.2, 0.2), (6, 15, -1.2, -0.2), (0, 12, -1.5, 0.0)]):
        add(P(f'spike{i}', (4, ln, 4), (-2, 0, -2), (x, 46, -8), rot=(rx, 0, rz), parent='torso', style='thorn'))
        add(P(f'spike{i}Tip', (2, 6, 2), (-1, 0, -1), (0, ln, 0), parent=f'spike{i}', style='bone'))
    for i, (x, y, z) in enumerate([(-13, 30, 11), (12, 24, 11), (-18, 40, 8)]):
        add(P(f'crack{i}', (1, 7, 1), (x, y, z), parent='torso', style='glow_y'))
    for i, (x, z) in enumerate([(-15, -2), (14, -6)]):
        add(P(f'fungus{i}S', (2, 4, 2), (x - 1, 52, z - 1), parent='torso', style='stem'))
        add(P(f'fungus{i}C', (7, 2, 7), (x - 3.5, 56, z - 3.5), parent='torso', style='cap_pale'))

    # ---- arms: huge shoulders with thorns, long forearms, four hooked claws and a thumb
    for side, sx in (('R', -1), ('L', 1)):
        n = 'arm' + side
        add(P(n, (13, 26, 13), (-6.5, -26, -6.5), (sx * 25, 40, 2), rot=(-0.55, 0, -sx * 0.12), parent='torso', style='bark_rot', anim='armA' if sx < 0 else 'armB'))
        add(P(n + 'Shoulder', (24, 14, 24), (-12, -5, -12), parent=n, style='bark_d'))
        add(P(n + 'Moss', (20, 4, 20), (-10, 9, -10), parent=n, style='moss_dk'))
        for k, (x, z, ln) in enumerate([(-7, -5, 14), (0, 0, 19), (7, -5, 13), (-4, 6, 12), (5, 6, 15)]):
            add(P(f'{n}Thorn{k}', (4, ln, 4), (-2, 0, -2), (x, 10, z), rot=(z * 0.05, 0, -x * 0.07 - sx * 0.25), parent=n, style='thorn'))
        add(P(n + 'Fore', (15, 28, 15), (-7.5, -28, -7.5), (0, -26, 0), rot=(-0.35, 0, 0), parent=n, style='bark_d'))
        add(P(n + 'Bracer', (17, 9, 17), (-8.5, -24, -8.5), parent=n + 'Fore', style='thorn'))
        for k in range(4):
            add(P(f'{n}ForeSpike{k}', (3, 3, 9), (-1.5, -7 - 6 * k, -16), parent=n + 'Fore', style='bone'))
        for k in range(3):
            add(P(f'{n}Tatter{k}', (3, 14 + 3 * k, 1), (-1.5, -14 - 3 * k, 0), (-5 + 5 * k, -6, 8), parent=n + 'Fore', style='moss_dk', anim='sway'))
        add(P(n + 'Hand', (16, 9, 14), (-8, -9, -7), (0, -28, 0), parent=n + 'Fore', style='bark_rot'))
        for k in range(4):
            add(P(f'{n}Claw{k}', (3, 12, 3), (-1.5, -12, -1.5), (-6 + 4 * k, -9, 5), rot=(0.35, 0, 0), parent=n + 'Hand', style='thorn'))
            add(P(f'{n}Claw{k}Tip', (2, 11, 2), (-1, -11, -1), (0, -12, 0), rot=(0.6, 0, 0), parent=f'{n}Claw{k}', style='bone'))
        add(P(n + 'Thumb', (3, 10, 3), (-1.5, -10, -1.5), (-sx * 8, -4, 3), rot=(0.2, 0, -sx * 0.8), parent=n + 'Hand', style='thorn'))
        add(P(n + 'ThumbTip', (2, 8, 2), (-1, -8, -1), (0, -10, 0), rot=(0.5, 0, 0), parent=n + 'Thumb', style='bone'))

    # ---- head: a deer skull with burning sockets, hanging jaw, fangs, and a huge antler rack
    add(P('neck', (12, 10, 12), (-6, 44, 0), parent='torso', style='bark_rot'))
    add(P('head', (16, 14, 16), (-8, 0, -6), (0, 50, 10), rot=(-0.2, 0, 0), parent='torso', style='bone', anim='head'))
    add(P('snout', (10, 9, 14), (-5, -1, 10), parent='head', style='bone'))
    add(P('nose', (4, 3, 1), (-2, 5, 24), parent='head', style='void'))
    add(P('brow', (18, 3, 5), (-9, 11, 7), parent='head', style='bone_d'))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        add(P('socket' + nm, (5, 5, 1), (sx * 5.5 - 2.5, 6, 10), parent='head', style='void'))
        add(P('eye' + nm, (3, 3, 1), (sx * 5.5 - 1.5, 7, 10.6), parent='head', style='glow_y'))
        add(P('cheek' + nm, (2, 7, 10), (sx * 8 - 1, 0, 0), parent='head', style='bone_d'))
    for i in range(4):
        add(P(f'fang{i}', (2, 5 + (i % 3 == 0) * 2, 2), (-4.2 + 2.6 * i, -6 - (i % 3 == 0) * 2, 20), parent='head', style='bone'))
    add(P('jaw', (9, 4, 20), (-4.5, -4, 0), (0, -1, 2), rot=(0.3, 0, 0), parent='head', style='bone_d', anim='jaw'))
    for i in range(4):
        add(P(f'jawFang{i}', (2, 4, 2), (-3.6 + 2.3 * i, 0, 16), parent='jaw', style='bone'))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        a1 = 'antler' + nm + '1'
        add(P(a1, (4, 16, 4), (-2, 0, -2), (sx * 6, 13, -2), rot=(-0.3, 0, -sx * 0.95), parent='head', style='thorn'))
        add(P('antler' + nm + '2', (4, 18, 4), (-2, 0, -2), (0, 16, 0), rot=(0, 0, sx * 0.6), parent=a1, style='thorn'))
        add(P('antler' + nm + '3', (3, 16, 3), (-1.5, 0, -1.5), (0, 18, 0), rot=(0.2, 0, sx * 0.25), parent='antler' + nm + '2', style='thorn'))
        add(P('antler' + nm + '3Tip', (2, 8, 2), (-1, 0, -1), (0, 16, 0), parent='antler' + nm + '3', style='bone'))
        for k, (py, rz, ln) in enumerate([(6, 0.9, 11), (12, 1.0, 9)]):
            add(P(f'{a1}Tine{k}', (3, ln, 3), (-1.5, 0, -1.5), (0, py, 0), rot=(0, 0, sx * rz), parent=a1, style='thorn'))
        for k, (py, rz, ln) in enumerate([(5, -0.9, 13), (10, 0.8, 10), (15, -0.8, 9)]):
            add(P(f'antler{nm}2Tine{k}', (2, ln, 2), (-1, 0, -1), (0, py, 0), rot=(0.15 * k, 0, sx * rz), parent='antler' + nm + '2', style='thorn'))
        for k, (x, y, ln) in enumerate([(15, 22, 14), (24, 30, 18), (30, 40, 12)]):
            add(P(f'hang{nm}{k}', (2, ln, 1), (-1, -ln, -0.5), (sx * x, y, -2), parent='head', style='moss_dk', anim='sway'))
        add(P('trophy' + nm, (5, 5, 5), (-2.5, -5, -2.5), (sx * 20, 14, -1), parent='head', style='bone', anim='sway'))
        add(P('trophy' + nm + 'Eyes', (3, 2, 1), (-1.5, -3, 2.6), parent='trophy' + nm, style='void'))
    return parts


def roc(P):
    """A storm-black raptor in a horned skull mask, with a snapping beak, bone spikes and ragged rune-tipped wings."""
    parts = []
    add = parts.append

    add(P('body', (20, 17, 36), (-10, -8.5, -18), (0, 28, 0), style='storm'))
    add(P('belly', (16, 5, 28), (-8, -12, -12), parent='body', style='storm_l'))
    add(P('keel', (22, 18, 13), (-11, -10, 9), parent='body', style='storm_l'))
    for i in range(3):
        add(P(f'cage{i}', (24, 2, 14), (-12, -8 + 6 * i, 9.5), parent='body', style='bone'))
    add(P('stormCore', (6, 6, 2), (-3, -3, -1), (0, -1, 23), parent='body', style='rune_cyan', anim='pulse'))
    for i in range(7):
        ln = 12 - abs(i - 2) * 1.2
        add(P(f'spine{i}', (3, ln, 3), (-1.5, 0, -1.5), (0, 8, 13 - 5 * i), rot=(-0.5, 0, 0), parent='body', style='bone'))
    for i in range(3):
        add(P(f'backPlate{i}', (16, 2, 8), (-8, 8.5, -16 + 11 * i), parent='body', style='steel'))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        add(P('flank' + nm, (4, 11, 24), (sx * 10 - 2, -6, -13), parent='body', style='navy_d'))
        add(P('flankVein' + nm, (1, 1, 18), (sx * 12 - 0.5, 1, -10), parent='body', style='rune_cyan'))
    for i, (x, y, z) in enumerate([(-14, 6, 6), (15, -4, -2), (-13, -8, -12), (12, 10, -9), (0, 14, 2), (-3, -14, 8)]):
        add(P(f'spark{i}', (1, 6, 1), (-0.5, -3, -0.5), (x, y, z), rot=(0.4 * i, 0, 0.7 * i), parent='body', style='glow_w', anim='sway'))

    # ---- tail: nine ragged feathers and two bone blades
    add(P('tailRoot', (9, 5, 7), (-4.5, -2.5, -7), (0, 2, -18), rot=(0.25, 0, 0), parent='body', style='storm'))
    for i in range(9):
        ln = 34 - abs(i - 4) * 3 - (i % 2) * 3
        add(P(f'tail{i}', (5, 2, ln), (-2.5, -1, -ln), (0, 0, -5), rot=(0, (i - 4) * 0.15, 0), parent='tailRoot', style='storm' if i % 2 else 'navy_d'))
        add(P(f'tail{i}Tip', (5, 2, 5), (-2.5, -1, -5), (0, 0, -ln), parent=f'tail{i}', style='rune_cyan' if i % 2 == 0 else 'storm_l'))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        add(P('tailBlade' + nm, (3, 2, 38), (-1.5, -1, -38), (0, 1, -5), rot=(0, sx * 0.72, 0), parent='tailRoot', style='bone'))

    # ---- legs: heavy talons with hooked two-segment claws
    for sx, nm in ((-1, 'R'), (1, 'L')):
        L = 'leg' + nm
        add(P(L, (7, 11, 7), (-3.5, -11, -3.5), (sx * 7, -8, 3), parent='body', style='storm_l'))
        add(P(L + 'Shin', (4, 11, 4), (-2, -11, -2), (0, -11, 0), parent=L, style='steel'))
        for k, ang in enumerate((-0.4, 0, 0.4)):
            t = f'{L}Toe{k}'
            add(P(t, (3, 3, 11), (-1.5, -3, 0), (0, -11, 0), rot=(0, ang, 0), parent=L + 'Shin', style='steel'))
            add(P(t + 'Claw', (2, 3, 6), (-1, -1.5, 0), (0, -1.5, 11), rot=(0.6, 0, 0), parent=t, style='bone'))
            add(P(t + 'ClawTip', (1, 2, 5), (-0.5, -1, 0), (0, 0, 6), rot=(0.6, 0, 0), parent=t + 'Claw', style='bone'))
        add(P(L + 'Back', (3, 3, 7), (-1.5, -3, -7), (0, -11, 0), parent=L + 'Shin', style='steel'))
        add(P(L + 'BackClaw', (2, 2, 6), (-1, -1, -6), (0, -1.5, -7), rot=(-0.6, 0, 0), parent=L + 'Back', style='bone'))

    # ---- neck, ruff, masked head, horns, snapping beak with a glowing throat
    add(P('neck', (11, 11, 12), (-5.5, -5.5, 0), (0, 4, 16), rot=(-0.4, 0, 0), parent='body', style='storm'))
    for i in range(14):
        a = i * math.pi / 7
        add(P(f'ruff{i}', (3, 9, 3), (-1.5, 0, -1.5), (6.5 * math.cos(a), 6.5 * math.sin(a), 3), rot=(-0.5, 0, a - math.pi / 2), parent='neck', style='storm' if i % 2 else 'navy_d'))
        if i % 2 == 0:
            add(P(f'ruff{i}Tip', (2, 3, 2), (-1, 0, -1), (0, 9, 0), parent=f'ruff{i}', style='rune_cyan'))
    add(P('head', (11, 11, 13), (-5.5, -5.5, 0), (0, 0, 11), rot=(0.4, 0, 0), parent='neck', style='storm', anim='head'))
    add(P('mask', (12, 5, 13), (-6, 2, 1), parent='head', style='bone'))
    add(P('maskNose', (6, 4, 6), (-3, -1, 9), parent='head', style='bone'))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        add(P('socket' + nm, (1, 4, 5), (sx * 5.6 - 0.5, -1, 4), parent='head', style='void'))
        add(P('eye' + nm, (1, 2, 3), (sx * 6.1 - 0.5, 0, 5), parent='head', style='glow_w'))
        add(P('brow' + nm, (3, 2, 9), (sx * 5 - 1.5, 3.5, 3), rot=(0.25, 0, 0), parent='head', style='bone_d'))
        add(P('cheek' + nm, (2, 6, 7), (sx * 5.5 - 1, -5.5, 2), parent='head', style='bone_d'))
        h = 'horn' + nm
        add(P(h, (3, 3, 13), (-1.5, -1.5, -13), (sx * 4, 6, 5), rot=(0.4, -sx * 0.3, 0), parent='head', style='bone_d'))
        add(P(h + '2', (2, 2, 11), (-1, -1, -11), (0, 0, -13), rot=(0.35, 0, 0), parent=h, style='bone'))
        add(P('hornSmall' + nm, (2, 2, 8), (-1, -1, -8), (sx * 5.5, 1, 3), rot=(0.15, -sx * 0.5, 0), parent='head', style='bone'))
    for i in range(3):
        add(P(f'headSpine{i}', (2, 6 - i, 2), (-1, 0, -1), (0, 7, 9 - 4 * i), rot=(-0.6, 0, 0), parent='head', style='bone'))
    add(P('beakUp', (7, 5, 13), (-3.5, -3, 13), parent='head', style='steel'))
    add(P('beakRidge', (3, 2, 12), (-1.5, 2, 13), parent='head', style='bone'))
    add(P('beakHook', (5, 7, 4), (-2.5, -9, 23), parent='head', style='bone'))
    for i in range(3):
        for sx, nm in ((-1, 'R'), (1, 'L')):
            add(P(f'tooth{nm}{i}', (1, 2, 1), (sx * 3 - 0.5, -5, 15 + 3 * i), parent='head', style='bone'))
    add(P('throat', (4, 2, 9), (-2, -4.5, 12), parent='head', style='rune_cyan'))
    add(P('beakLow', (5, 3, 11), (-2.5, -3, 0), (0, -4, 12), rot=(0.3, 0, 0), parent='head', style='steel', anim='jaw'))
    add(P('beakLowTip', (3, 2, 3), (-1.5, 0, 9), parent='beakLow', style='bone'))

    # ---- wings: bone-spiked leading edge, a wrist claw, ragged secondaries and primaries with glowing tips
    for sx, nm in ((1, 'L'), (-1, 'R')):
        W = 'wing' + nm

        def bx(length):                       # x origin for a box that extends outward from the pivot
            return 0 if sx > 0 else -length
        add(P(W, (20, 6, 12), (bx(20), -3, -6), (sx * 10, 31, 3), style='storm', anim='wingL' if sx > 0 else 'wingR'))
        add(P(W + 'Cov0', (20, 2, 14), (bx(20), 3, -8), parent=W, style='navy_d'))
        add(P(W + 'Cov1', (17, 2, 10), (sx * 1 + bx(17), 5, -6), parent=W, style='storm_l'))
        add(P(W + 'Plate', (8, 4, 12), (sx * 1 + bx(8), 3, -6), parent=W, style='steel'))
        add(P(W + 'Vein', (16, 1, 2), (sx * 2 + bx(16), 3.2, 4), parent=W, style='rune_cyan'))
        for k in range(3):
            add(P(f'{W}Spike{k}', (2, 2, 8), (sx * (4 + 6 * k) - 1, -1, 6), rot=(0, 0, 0), parent=W, style='bone'))
        add(P(W + 'Fore', (26, 5, 12), (bx(26), -2.5, -6), (sx * 20, 0, 0), parent=W, style='storm'))
        add(P(W + 'ForeCov', (24, 2, 10), (sx * 1 + bx(24), 2.5, -6), parent=W + 'Fore', style='navy_d'))
        add(P(W + 'ForeVein', (22, 1, 2), (sx * 2 + bx(22), 4.5, 3), parent=W + 'Fore', style='rune_cyan'))
        for k in range(4):
            add(P(f'{W}ForeSpike{k}', (2, 2, 7), (sx * (3 + 6 * k) - 1, -1, 6), parent=W + 'Fore', style='bone'))
        for i in range(9):
            ln = 22 + int(1.6 * i) - (i % 2) * 3
            s = f'{W}Sec{i}'
            add(P(s, (3, 1, ln), (-1.5, -0.5, -ln), (sx * (2 + 2.8 * i), -1, -5), rot=(0, -sx * 0.04 * i, 0), parent=W + 'Fore', style='storm' if i % 2 else 'navy_d'))
            add(P(s + 'Tip', (3, 1, 4), (-1.5, -0.5, -4), (0, 0, -ln), parent=s, style='rune_cyan' if i % 3 == 0 else 'storm_l'))
        add(P(W + 'Hand', (16, 4, 9), (bx(16), -2, -4.5), (sx * 26, 0, 0), parent=W + 'Fore', style='storm'))
        add(P(W + 'WristClaw', (3, 3, 11), (-1.5, -1.5, 0), (sx * 1, 0, 4), rot=(0, sx * 0.5, 0), parent=W + 'Hand', style='bone'))
        add(P(W + 'WristClawTip', (2, 2, 6), (-1, -1, 0), (0, 0, 11), rot=(0.5, 0, 0), parent=W + 'WristClaw', style='bone'))
        for i in range(11):
            ln = 28 + int(2.4 * min(i, 7)) - max(0, i - 7) * 5 - (i % 2) * 3
            pr = f'{W}Pri{i}'
            add(P(pr, (3, 1, ln), (-1.5, -0.5, -ln), (sx * (1 + 1.4 * i), -1, -3), rot=(0, -sx * (0.05 + 0.105 * i), 0), parent=W + 'Hand', style='navy_d' if i % 2 else 'storm'))
            add(P(pr + 'Tip', (3, 1, 5), (-1.5, -0.5, -5), (0, 0, -ln), parent=pr, style='rune_cyan' if i % 2 == 0 else 'storm_l'))
    return parts


def king(P):
    """A towering dead king: skull in an open helm, forward horns, skull pauldrons, burning greatsword, orbiting soul shards."""
    parts = []
    add = parts.append
    ARM, BR, CAPE = 'king_armor', 'plate_dk', 'cape_d'

    def skull(name, size, origin, parent, pivot=(0, 0, 0), eyes='rune_orange'):
        w, h, d = size
        add(P(name, size, origin, pivot, parent=parent, style='bone'))
        ox, oy, oz = (0, 0, 0)
        add(P(name + 'EyeR', (max(1, w // 4), max(1, h // 4), 1), (origin[0] + w * 0.15, origin[1] + h * 0.5, origin[2] + d), parent=name, style=eyes))
        add(P(name + 'EyeL', (max(1, w // 4), max(1, h // 4), 1), (origin[0] + w * 0.6, origin[1] + h * 0.5, origin[2] + d), parent=name, style=eyes))

    # ---- legs
    for side, sx in (('R', -1), ('L', 1)):
        n = 'leg' + side
        add(P(n, (12, 20, 12), (-6, -20, -6), (sx * 10, 50, 0), style=ARM, anim='legA' if sx < 0 else 'legB'))
        add(P(n + 'Knee', (14, 8, 14), (-7, -24, -7), parent=n, style=BR))
        add(P(n + 'KneeSpike', (3, 3, 11), (-1.5, -22, 7), parent=n, style='bone'))
        add(P(n + 'Shin', (11, 20, 11), (-5.5, -40, -5.5), parent=n, style=ARM))
        add(P(n + 'Greave', (13, 12, 3), (-6.5, -37, 5.5), parent=n, style=BR))
        add(P(n + 'GreaveFin', (2, 12, 6), (sx * 6 - 1, -38, -3), parent=n, style='blade'))
        add(P(n + 'Boot', (13, 10, 20), (-6.5, -50, -7), parent=n, style=ARM))
        add(P(n + 'Cuff', (14, 3, 14), (-7, -41, -7), parent=n, style=BR))
        for i in range(3):
            add(P(f'{n}ToeClaw{i}', (2, 3, 6), (-5 + 4 * i, -50, 13), parent=n, style='bone'))

    # ---- waist, belt, skull buckle, tassets, chains with soul lanterns
    add(P('waist', (28, 10, 18), (-14, 0, -9), (0, 50, 0), style=ARM))
    add(P('belt', (30, 4, 20), (-15, 3, -10), parent='waist', style=BR))
    skull('buckle', (8, 8, 3), (-4, 0, 10), 'waist')
    for i in range(3):
        add(P(f'tassF{i}', (9, 18, 2), (-14 + 9.5 * i, -16, 10), parent='waist', style=ARM))
        add(P(f'tassF{i}Edge', (9, 2, 3), (-14 + 9.5 * i, -17, 9.5), parent='waist', style=BR))
        add(P(f'tassB{i}', (9, 18, 2), (-14 + 9.5 * i, -16, -12), parent='waist', style=ARM))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        c = 'chain' + nm
        add(P(c, (2, 5, 2), (-1, -5, -1), (sx * 14, 2, 8), parent='waist', style='steel', anim='sway'))
        for k in range(1, 4):
            add(P(f'{c}{k}', (2, 5, 2), (-1, -5, -1), (0, -5, 0), rot=(0.1, 0, 0), parent=c if k == 1 else f'{c}{k - 1}', style='steel'))
        add(P('lantern' + nm, (6, 7, 6), (-3, -7, -3), (0, -5, 0), parent=f'{c}3', style='soul_light'))

    # ---- chest: bone ribs over black plate, a burning core, a spiked collar
    add(P('chest', (34, 24, 20), (-17, 0, -10), (0, 60, 0), style=ARM))
    add(P('core', (8, 10, 2), (-4, -5, -1), (0, 12, 10.2), parent='chest', style='rune_orange', anim='pulse'))
    add(P('sternum', (4, 18, 2), (-2, 3, 11), parent='chest', style='bone'))
    for i in range(4):
        for sx, nm in ((-1, 'R'), (1, 'L')):
            add(P(f'rib{nm}{i}', (13, 2, 2), (3 if sx > 0 else -16, 5 + 4.5 * i, 10.5), parent='chest', style='bone'))
            add(P(f'ribSide{nm}{i}', (2, 2, 16), (16.5 if sx > 0 else -18.5, 5 + 4.5 * i, -8), parent='chest', style='bone_d'))
    add(P('backPlate', (28, 20, 3), (-14, 2, -13), parent='chest', style=ARM))
    add(P('collar', (22, 8, 20), (-11, 24, -10), parent='chest', style=BR))
    add(P('fur', (40, 7, 12), (-20, 20, -12), parent='chest', style='fur'))
    for i in range(5):
        add(P(f'collarSpike{i}', (3, 13, 3), (-1.5, 0, -1.5), (-10 + 5 * i, 30, -9), rot=(-0.45, 0, -(i - 2) * 0.22), parent='chest', style='bone'))
    for i in range(6):
        add(P(f'spineSpike{i}', (3, 9 + (i % 2) * 4, 3), (-1.5, 0, -1.5), (0, 3 + 3.6 * i, -13), rot=(-1.0, 0, 0), parent='chest', style='bone'))

    # ---- arms: stacked pauldrons with a skull and long spikes, bladed vambraces, clawed gauntlets
    for side, sx in (('R', -1), ('L', 1)):
        n = 'arm' + side
        add(P(n, (12, 20, 12), (-6, -20, -6), (sx * 24, 82, 0), rot=(-0.15, 0, -sx * 0.06), style=ARM, anim='armA' if sx < 0 else 'armB'))
        for k, (w, y) in enumerate([(22, -1), (19, 4), (16, 9)]):
            add(P(f'{n}Pauldron{k}', (w, 6, w), (-w / 2, y, -w / 2), parent=n, style=ARM if k != 1 else BR))
        skull(n + 'Skull', (7, 7, 3), (-3.5, 0, 11), n)
        for k, (x, z, ln) in enumerate([(-6, 0, 13), (0, 0, 18), (6, 0, 13), (0, -6, 12), (0, 6, 11)]):
            add(P(f'{n}Spike{k}', (3, ln, 3), (-1.5, 0, -1.5), (x, 14, z), rot=(z * 0.06, 0, -x * 0.06 - sx * 0.35), parent=n, style='bone'))
        add(P(n + 'Fore', (11, 20, 11), (-5.5, -20, -5.5), (0, -20, 0), parent=n, style=ARM))
        add(P(n + 'Elbow', (3, 3, 12), (-1.5, -1.5, -14), parent=n + 'Fore', style='bone'))
        add(P(n + 'Vambrace', (13, 8, 13), (-6.5, -12, -6.5), parent=n + 'Fore', style=BR))
        for k in range(2):
            add(P(f'{n}Fin{k}', (2, 9, 7), (sx * 6.5 - 1, -10 - 7 * k, -5), parent=n + 'Fore', style='blade'))
        add(P(n + 'Hand', (12, 10, 12), (-6, -10, -6), (0, -20, 0), parent=n + 'Fore', style=ARM))
        for k in range(4):
            f = f'{n}Finger{k}'
            add(P(f, (2, 8, 2), (-1, -8, -1), (-4.5 + 3 * k, -10, 5), rot=(0.6, 0, 0), parent=n + 'Hand', style=ARM))
            add(P(f + 'Claw', (1, 6, 1), (-0.5, -6, -0.5), (0, -8, 0), rot=(0.5, 0, 0), parent=f, style='bone'))

    # ---- left hand: a hovering soul orb
    add(P('orb', (6, 6, 6), (-3, -3, -3), (0, -18, 6), parent='armLHand', style='rune_cyan', anim='pulse'))
    for k, (x, y, z) in enumerate([(5, 2, 0), (-5, -1, 1), (0, 5, -2), (1, -6, 2)]):
        add(P(f'orbShard{k}', (1, 3, 1), (x, y, z), parent='orb', style='soul_light'))

    # ---- the burning greatsword in the right hand
    add(P('swordGrip', (4, 20, 4), (-2, -10, -2), (0, -5, 0), rot=(-0.55, 0, 0), parent='armRHand', style='fur'))
    add(P('swordGuard', (36, 6, 6), (-18, 10, -3), parent='swordGrip', style=BR))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        add(P('swordHorn' + nm, (4, 12, 4), (sx * 18 - 2, 10, -2), parent='swordGrip', style='bone'))
    skull('swordPommel', (6, 6, 6), (-3, -16, -3), 'swordGrip')
    add(P('swordBlade', (11, 84, 3), (-5.5, 16, -1.5), parent='swordGrip', style='blade'))
    add(P('swordCoreF', (3, 70, 1), (-1.5, 18, 1.5), parent='swordGrip', style='rune_orange'))
    add(P('swordCoreB', (3, 70, 1), (-1.5, 18, -2.5), parent='swordGrip', style='rune_orange'))
    for i in range(7):
        add(P(f'swordToothR{i}', (4, 5, 2), (5.5, 22 + 10 * i, -1), parent='swordGrip', style='blade'))
        add(P(f'swordToothL{i}', (4, 5, 2), (-9.5, 27 + 10 * i, -1), parent='swordGrip', style='blade'))
    for i in range(8):
        add(P(f'swordFlame{i}', (3, 6, 2), (-1.5, 0, -1), ((7 if i % 2 else -7), 24 + 9 * i, 0), parent='swordGrip', style='flame', anim='sway'))
    add(P('swordTip', (7, 8, 3), (-3.5, 100, -1.5), parent='swordGrip', style='blade'))

    # ---- head: skull face in an open helm, moving jaw, iron crown spikes with burning tips, forward horns
    add(P('head', (12, 13, 11), (-6, 0, -5), (0, 90, 0), style='bone', anim='head'))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        add(P('socket' + nm, (3, 3, 1), (sx * 3 - 1.5, 6, 6), parent='head', style='void'))
        add(P('pupil' + nm, (1, 2, 1), (sx * 3 - 0.5, 6.5, 6.4), parent='head', style='rune_orange'))
        add(P('helmSide' + nm, (3, 15, 15), (sx * 7.5 - 1.5, -1, -8), parent='head', style=ARM))
        h = 'horn' + nm
        add(P(h, (5, 12, 5), (-2.5, 0, -2.5), (sx * 8, 7, 0), rot=(0, 0, -sx * 1.0), parent='head', style='horn'))
        add(P(h + '2', (4, 12, 4), (-2, 0, -2), (0, 12, 0), rot=(0.5, 0, sx * 0.7), parent=h, style='horn'))
        add(P(h + '3', (3, 10, 3), (-1.5, 0, -1.5), (0, 12, 0), rot=(0.5, 0, sx * 0.3), parent=h + '2', style='bone'))
    add(P('noseHole', (2, 3, 1), (-1, 2.5, 6), parent='head', style='void'))
    add(P('teethUp', (8, 2, 1), (-4, 0, 5.6), parent='head', style='bone_d'))
    add(P('jaw', (10, 4, 9), (-5, -4, -2), (0, 1, 0), rot=(0.12, 0, 0), parent='head', style='bone', anim='jaw'))
    add(P('teethLow', (8, 1, 1), (-4, 0, 6.4), parent='jaw', style='bone_d'))
    add(P('helmTop', (16, 6, 16), (-8, 12, -8), parent='head', style=ARM))
    add(P('helmBack', (16, 15, 3), (-8, -1, -8), parent='head', style=ARM))
    add(P('helmBrow', (16, 3, 4), (-8, 10, 5), parent='head', style=BR))
    add(P('helmNasal', (2, 8, 2), (-1, 3, 7), parent='head', style=ARM))
    for i in range(7):
        a = math.pi * (i / 6.0)
        ln = 16 - abs(i - 3) * 2
        c = f'crown{i}'
        add(P(c, (3, ln, 3), (-1.5, 0, -1.5), (-7 * math.cos(a), 18, 2 - 6 * math.sin(a) + 3), rot=(0, 0, 0.12 * (i - 3)), parent='head', style='blade'))
        add(P(c + 'Fire', (2, 4, 2), (-1, 0, -1), (0, ln, 0), parent=c, style='flame', anim='sway'))

    # ---- cape: nine long torn strips under a fur mantle
    add(P('capeRoot', (40, 3, 3), (-20, -1, -2), (0, 82, -12), rot=(0.14, 0, 0), style='fur'))
    for i in range(9):
        ln = 50 - (i % 2) * 7 - abs(i - 4)
        add(P(f'cape{i}', (5, ln, 2), (-2.5, -ln, -1), (-20 + 5 * i, 0, 0), rot=(0.04 * abs(i - 4), 0, (i - 4) * 0.035), parent='capeRoot', style=CAPE, anim='sway'))
        add(P(f'cape{i}Tip', (3, 7, 2), (-1.5, -7, -1), ((i % 2) * 2 - 1, -ln, 0), rot=(0.25, 0, 0), parent=f'cape{i}', style=CAPE))

    # ---- soul shards orbiting his chest, and a broken halo of iron above the crown
    add(P('orbitRoot', (2, 2, 2), (-1, -1, -1), (0, 72, 0), style='void', anim='spin'))
    for i in range(6):
        a = i * math.pi / 3
        add(P(f'shard{i}', (2, 9, 2), (-1, -4.5, -1), (30 * math.cos(a), (i % 2) * 8 - 4, 30 * math.sin(a)), rot=(0.3, 0, 0.3), parent='orbitRoot', style='rune_cyan'))
        add(P(f'shard{i}Core', (1, 4, 1), (-0.5, -2, 1), parent=f'shard{i}', style='soul_light'))
    add(P('haloRoot', (2, 2, 2), (-1, 0, -1), (0, 126, 0), style='void', anim='spin'))
    for i in range(16):
        if i in (3, 4, 11):
            continue                                            # the halo is broken
        a = i * math.pi / 8
        add(P(f'halo{i}', (7, 2, 3), (-3.5, -1, -1.5), (15 * math.cos(a), 0, 15 * math.sin(a)), rot=(0, -a + math.pi / 2, 0), parent='haloRoot', style='blade'))
        if i % 4 == 0:
            add(P(f'halo{i}Fire', (2, 5, 2), (-1, 1, -1), parent=f'halo{i}', style='flame'))
    return parts
