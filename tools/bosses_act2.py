"""Act two Wardens: Vorath the Tide Devourer, the White Silence, Kharzul the Glass Reaper.

Units of 1/16 block, y up, front toward +z. Same rules as bosses_v3: a part with a parent has its pivot relative to the
parent's pivot and moves with it; rotation is Rz * Ry * Rx; positive x-rotation swings a point above the pivot forward.
"""
import math


def scale_subtree(parts, root, k):
    """Scale a part and all its descendants about the root's pivot (the root keeps its pivot)."""
    kids = {root}
    for p in parts:
        if p.get('parent') in kids:
            kids.add(p['name'])
    for p in parts:
        if p['name'] in kids:
            p['size'] = tuple(max(1, int(round(v * k))) for v in p['size'])
            p['origin'] = tuple(v * k for v in p['origin'])
            if p['name'] != root:
                p['pivot'] = tuple(v * k for v in p['pivot'])


def side_box(sx, length):
    """x origin for a box that extends outward (away from the body) from its pivot."""
    return 0 if sx > 0 else -length


# ====================================================================================== VORATH
def vorath(P):
    """An abyssal leviathan: a barnacled skull-head with a gaping maw of needle teeth, a glowing lure, six eyes,
    spined gill frills, webbed claw-flippers, and a long undulating body that ends in a bladed fluke."""
    parts = []
    add = parts.append

    # ---- the body: eight segments chained backwards, each a little smaller, all undulating
    W = [36, 33, 30, 27, 23, 19, 15, 11]
    H = [26, 24, 22, 20, 17, 14, 11, 8]
    LEN = [26, 24, 23, 22, 20, 18, 16, 14]
    SPINE = [22, 20, 17, 14, 11, 9, 7, 5]
    CURVE = [(0.0, 0.0), (0.06, 0.22), (0.04, 0.26), (0.0, 0.12), (-0.05, -0.2), (-0.06, -0.3), (-0.04, -0.26), (0.0, -0.14)]
    for i in range(8):
        w, h, ln = W[i], H[i], LEN[i]
        n = f'seg{i}'
        if i == 0:
            add(P(n, (w, h, ln), (-w / 2, -h / 2, -ln + 6), (0, 30, 0), style='abyss', anim='undulate'))
        else:
            add(P(n, (w, h, ln + 1), (-w / 2, -h / 2, -ln), (0, 0, -LEN[i - 1] + 7 if i == 1 else -LEN[i - 1] + 1), rot=(CURVE[i][0], CURVE[i][1], 0),
                  parent=f'seg{i - 1}', style='abyss', anim='undulate'))
        zc = -ln / 2 + (6 if i == 0 else 0)
        add(P(n + 'Belly', (w - 6, 2, ln - 3), (-(w - 6) / 2, -h / 2 - 1, -ln + 1.5 + (6 if i == 0 else 0)), parent=n, style='belly_p'))
        for sx, nm in ((-1, 'R'), (1, 'L')):
            add(P(n + 'Plate' + nm, (2, h - 6, ln - 5), (sx * w / 2 - 1, -h / 2 + 3, -ln + 2.5 + (6 if i == 0 else 0)), parent=n, style='abyss_l'))
            for k, (y, dz) in enumerate([(2, -0.3), (-4, -0.7)]):
                if i < 7 and (i + k) % 2 == 0:
                    add(P(f'{n}Glow{nm}{k}', (1, 2, 3), (sx * (w / 2 + 0.4) - 0.5, y, -ln * (0.25 - dz * 0.5) + (6 if i == 0 else 0) - 2), parent=n, style='abyss_glow'))
        add(P(n + 'Spine', (3, SPINE[i], 3), (-1.5, 0, -1.5), (0, h / 2 - 1, zc), rot=(-0.55, 0, 0), parent=n, style='bone_d'))
        add(P(n + 'SpineTip', (2, max(3, SPINE[i] // 3), 2), (-1, 0, -1), (0, SPINE[i], 0), parent=n + 'Spine', style='bone'))
        add(P(n + 'Fin', (1, max(3, int(SPINE[i] * 0.7)), max(4, int(ln * 0.7))), (-0.5, h / 2 - 1, zc - ln * 0.35), parent=n, style='fin'))
        if i % 2 == 0 and i < 6:
            for k, (x, z, s) in enumerate([(-w * 0.3, zc + 3, 4), (-w * 0.22, zc - 2, 3), (w * 0.28, zc - 4, 3)]):
                add(P(f'{n}Barn{k}', (s, 2, s), (x - s / 2, h / 2 - 0.5, z - s / 2), parent=n, style='barnacle'))
    # tail fluke and blade
    last = 'seg7'
    add(P('fluke', (6, 4, 6), (-3, -2, -6), (0, 0, -LEN[7] + 1), parent=last, style='abyss'))
    for k in range(7):
        a = (k - 3) * 0.24
        ln = 30 - abs(k - 3) * 3
        fb = f'flukeBlade{k}'
        add(P(fb, (4, 1, ln), (-2, -0.5, -ln), (0, 0, -4), rot=(0, a, 0), parent='fluke', style='fin', anim='flutter'))
        add(P(fb + 'Ridge', (1, 2, ln - 2), (-0.5, -1, -ln + 1), parent=fb, style='bone_d'))
        add(P(fb + 'Tip', (3, 1, 3), (-1.5, -0.5, -3), (0, 0, -ln), parent=fb, style='abyss_glow' if k % 2 == 0 else 'abyss_l'))
    add(P('tailBlade', (3, 4, 30), (-1.5, -2, -30), (0, 3, -4), rot=(-0.25, 0, 0), parent='fluke', style='bone'))

    # ---- pectoral claw-flippers on the first segment
    for sx, nm in ((1, 'L'), (-1, 'R')):
        F = 'flipper' + nm
        add(P(F, (22, 5, 11), (side_box(sx, 22), -2.5, -5.5), (sx * 16, -8, -4), rot=(0.15, sx * 0.55, -sx * 0.3),
              parent='seg0', style='abyss', anim='finL' if sx > 0 else 'finR'))
        add(P(F + 'Web', (20, 1, 14), (side_box(sx, 20), -0.5, -12), parent=F, style='fin'))
        add(P(F + 'Fore', (16, 4, 8), (side_box(sx, 16), -2, -4), (sx * 21, 0, 0), rot=(0, sx * 0.35, 0), parent=F, style='abyss_l'))
        for k in range(3):
            fg = f'{F}Finger{k}'
            add(P(fg, (14, 2, 2), (side_box(sx, 14), -1, -1), (sx * 15, 0, 2 - 4 * k), rot=(0, sx * (0.15 + 0.3 * k), 0), parent=F + 'Fore', style='bone_d'))
            add(P(fg + 'Claw', (6, 2, 2), (side_box(sx, 6), -1, -1), (sx * 14, 0, 0), rot=(0, 0, -sx * 0.5), parent=fg, style='bone'))
        add(P(F + 'ForeWeb', (14, 1, 12), (side_box(sx, 14), -0.5, -10), (sx * 14, 0, 0), parent=F + 'Fore', style='fin'))

    # ---- head
    add(P('head', (38, 18, 32), (-19, -2, 0), (0, 2, 5), parent='seg0', style='abyss', anim='head'))
    add(P('crest', (30, 4, 24), (-15, 16, 2), parent='head', style='shell'))
    add(P('crest2', (20, 3, 16), (-10, 20, 5), parent='head', style='shell'))
    for k, (x, z, s) in enumerate([(-9, 10, 4), (7, 6, 3), (-2, 22, 3), (11, 18, 4), (-13, 20, 2), (3, 14, 2)]):
        add(P(f'headBarn{k}', (s, 2, s), (x - s / 2, 19.5 + (k % 2), z - s / 2), parent='head', style='barnacle'))
    add(P('snout', (30, 11, 24), (-15, -2, 32), parent='head', style='abyss'))
    add(P('snoutPlate', (24, 3, 20), (-12, 9, 34), parent='head', style='shell'))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        add(P('nostril' + nm, (3, 2, 1), (sx * 7 - 1.5, 4, 55.6), parent='head', style='void'))
    add(P('maw', (26, 5, 44), (-13, -6, 10), parent='head', style='maw'))
    for k in range(8):
        z = 16 + 5 * k
        ln = 6 + (k % 2) * 3
        for sx, nm in ((-1, 'R'), (1, 'L')):
            hw = 13 if z > 32 else 16
            add(P(f'tooth{nm}{k}', (2, ln, 2), (sx * (hw - 1.5) - 1, -2 - ln, z), parent='head', style='bone'))
            if k % 2 == 0:
                add(P(f'toothIn{nm}{k}', (1, 5, 1), (sx * (hw - 5) - 0.5, -7, z + 1), parent='head', style='bone_d'))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        add(P('fang' + nm, (3, 14, 3), (sx * 6 - 1.5, -15, 50), parent='head', style='bone'))
        # six eyes, three a side, in dark sockets
        for k, z in enumerate((9, 17, 25)):
            add(P(f'socket{nm}{k}', (1, 5 - k, 6 - k), (sx * 19.1 - 0.5, 4, z - 1), parent='head', style='void'))
            add(P(f'eye{nm}{k}', (1, 3 - (k == 2), 3), (sx * 19.6 - 0.5, 5, z), parent='head', style='abyss_glow'))
        # back-swept horns
        h1 = 'horn' + nm
        add(P(h1, (5, 5, 20), (-2.5, -2.5, -20), (sx * 13, 15, 8), rot=(0.55, sx * 0.35, 0), parent='head', style='bone_d'))
        add(P(h1 + '2', (4, 4, 16), (-2, -2, -16), (0, 0, -20), rot=(0.35, sx * 0.15, 0), parent=h1, style='bone_d'))
        add(P(h1 + '3', (2, 2, 11), (-1, -1, -11), (0, 0, -16), rot=(-0.3, 0, 0), parent=h1 + '2', style='bone'))
        add(P('hornSmall' + nm, (3, 3, 12), (-1.5, -1.5, -12), (sx * 17, 9, 6), rot=(0.2, sx * 0.6, 0), parent='head', style='bone'))
        # spined gill frills, five blades a side
        for k in range(5):
            g = f'gill{nm}{k}'
            add(P(g, (18 - abs(k - 2) * 2, 5, 1), (side_box(sx, 18 - abs(k - 2) * 2), -2.5, -0.5), (sx * 18.5, 6, 2),
                  rot=(0, sx * 0.55, sx * (-0.7 + 0.35 * k)), parent='head', style='fin', anim='flutter'))
            add(P(g + 'Ray', (18 - abs(k - 2) * 2, 1, 1), (side_box(sx, 18 - abs(k - 2) * 2), 2.5, -0.5), parent=g, style='bone_d'))
            add(P(g + 'Glow', (2, 2, 1), (sx * (16 - abs(k - 2) * 2) - 1, 0, -0.6), parent=g, style='abyss_glow'))
        # whisker barbels trailing back from the snout
        wb = 'whisker' + nm
        add(P(wb, (1, 1, 26), (-0.5, -0.5, -26), (sx * 15, 2, 44), rot=(0.1, sx * 0.5, 0), parent='head', style='fin', anim='sway'))
        add(P(wb + 'Tip', (1, 1, 14), (-0.5, -0.5, -14), (0, 0, -26), rot=(0.3, 0, 0), parent=wb, style='abyss_glow'))

    # ---- the lure, arching forward from the crest over the maw
    add(P('lure', (2, 2, 16), (-1, -1, 0), (0, 21, 22), rot=(-0.95, 0, 0), parent='head', style='abyss_l', anim='sway'))
    add(P('lure2', (2, 2, 15), (-1, -1, 0), (0, 0, 16), rot=(0.95, 0, 0), parent='lure', style='abyss_l'))
    add(P('lure3', (2, 2, 10), (-1, -1, 0), (0, 0, 15), rot=(0.75, 0, 0), parent='lure2', style='abyss_l'))
    add(P('lureBulb', (6, 6, 6), (-3, -3, -1), (0, 0, 10), parent='lure3', style='abyss_glow', anim='pulse'))
    for k, (x, y) in enumerate([(-4, 1), (3, 2), (0, -5)]):
        add(P(f'lureHook{k}', (1, 4, 1), (x, y, 1), parent='lureBulb', style='bone'))

    # ---- the lower jaw, hanging open, lined with teeth, with barbels under the chin
    add(P('jaw', (32, 7, 48), (-16, -7, -2), (0, -4, 6), rot=(0.5, 0, 0), parent='head', style='abyss', anim='jaw'))
    add(P('jawBelly', (26, 2, 40), (-13, -8.5, 2), parent='jaw', style='belly_p'))
    add(P('tongue', (22, 2, 34), (-11, -1, 4), parent='jaw', style='maw'))
    for k in range(8):
        z = 8 + 5 * k
        ln = 5 + ((k + 1) % 2) * 3
        for sx, nm in ((-1, 'R'), (1, 'L')):
            add(P(f'jawTooth{nm}{k}', (2, ln, 2), (sx * 13.5 - 1, 0, z), parent='jaw', style='bone'))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        add(P('jawFang' + nm, (3, 12, 3), (sx * 5 - 1.5, 0, 41), parent='jaw', style='bone'))
    for k, x in enumerate((-9, -3, 3, 9)):
        b = f'barbel{k}'
        add(P(b, (1, 16, 1), (-0.5, -16, -0.5), (x, -7, 34 - abs(x)), parent='jaw', style='fin', anim='sway'))
        add(P(b + 'Tip', (2, 3, 2), (-1, -3, -1), (0, -16, 0), parent=b, style='abyss_glow'))
    scale_subtree(parts, 'head', 1.3)
    return parts


# ====================================================================================== THE WHITE SILENCE
def white_silence(P):
    """A gaunt, faceless shape in a torn shroud. Porcelain mask with no mouth, a halo of icicles, arms that reach its
    knees, a cold lantern on a chain, an icicle lance, and a frozen heart in an open ribcage. It does not touch the ground."""
    parts = []
    add = parts.append
    SH, SHD, ICE = 'shroud', 'shroud_d', 'ice'

    # ---- the robe: a tapering bell of shroud that ends above the ground, and a ring of long tatters that brushes it
    add(P('waist', (16, 14, 11), (-8, 0, -5.5), (0, 40, 0), style=SHD))
    for k, (w, d, y) in enumerate([(18, 13, -6), (20, 15, -12), (23, 18, -18), (26, 20, -23)]):
        add(P(f'robe{k}', (w, 7, d), (-w / 2, y, -d / 2), parent='waist', style=SH if k % 2 else SHD))
    for i in range(20):
        a = i * 2 * math.pi / 20
        ln = 22 - (i % 3) * 4 + (4 if math.cos(a) < 0 else 0)
        t = f'tatter{i}'
        add(P(t, (4, ln, 1), (-2, -ln, -0.5), (14 * math.sin(a), -22, 10.5 * math.cos(a)), rot=(0.18 * math.cos(a), a, -0.18 * math.sin(a)),
              parent='waist', style=SH if i % 2 else SHD, anim='sway'))
        if i % 3 == 0:
            add(P(t + 'Ice', (1, 5, 1), (-0.5, -5, -0.5), (1, -ln, 0), parent=t, style=ICE))
    # ---- chest: torn open over a cage of ice ribs and a frozen heart
    add(P('chest', (22, 24, 12), (-11, 0, -6), (0, 54, 0), style=SH))
    add(P('cavity', (12, 14, 2), (-6, 5, 5), parent='chest', style='void'))
    add(P('heart', (6, 7, 6), (-3, -3.5, -3), (0, 12, 4), parent='chest', style='frost_glow', anim='pulse'))
    for k in range(4):
        for sx, nm in ((-1, 'R'), (1, 'L')):
            add(P(f'rib{nm}{k}', (6, 1, 1), (2 if sx > 0 else -8, 6 + 3 * k, 6.4), parent='chest', style=ICE))
    add(P('sternum', (2, 14, 1), (-1, 5, 6.6), parent='chest', style='ice_d'))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        add(P('chestTear' + nm, (5, 20, 1), (sx * 8.5 - 2.5, 2, 6.2), rot=(0, 0, sx * 0.08), parent='chest', style=SHD))
    add(P('mantle', (30, 8, 18), (-15, 20, -9), parent='chest', style=SHD))
    add(P('mantle2', (34, 4, 20), (-17, 18, -10), parent='chest', style=SH))
    for i in range(9):
        x = -16 + 4 * i
        ln = 18 + (i % 3) * 6
        add(P(f'mantleTatter{i}', (4, ln, 1), (-2, -ln, -0.5), (x, 18, -10.5), rot=(-0.06, 0, 0), parent='chest', style=SHD if i % 2 else SH, anim='sway'))
    for i in range(9):                                        # a long cloak from the shoulders to the ground
        ln = 66 - (i % 2) * 6 - abs(i - 4) * 2
        add(P(f'cloak{i}', (5, ln, 2), (-2.5, -ln, -1), (-20 + 5 * i, 20, -9), rot=(0.1 + 0.03 * abs(i - 4), 0, (i - 4) * 0.05),
              parent='chest', style=SH if i % 2 else SHD, anim='sway'))
        add(P(f'cloak{i}Tip', (3, 6, 2), (-1.5, -6, -1), ((i % 2) * 2 - 1, -ln, 0), rot=(0.2, 0, 0), parent=f'cloak{i}', style=SHD))
    for k in range(5):                                        # ice breaking out of the back
        add(P(f'backIce{k}', (3, 12 + 3 * (k % 2), 3), (-1.5, 0, -1.5), (-8 + 4 * k, 14 - abs(k - 2) * 2, -8),
              rot=(-0.9, 0, (k - 2) * 0.3), parent='chest', style=ICE))

    # ---- neck and head: a long neck, a hood, and a smooth white mask with two slits and a glowing crack
    add(P('neck', (6, 12, 6), (-3, 0, -3), (0, 80, 0), style='bone_d'))
    add(P('head', (14, 17, 4), (-7, -1, 3), (0, 90, 0), style='mask', anim='head'))
    add(P('hood', (18, 22, 14), (-9, -3, -10), parent='head', style=SHD))
    add(P('hoodPeak', (12, 6, 10), (-6, 18, -8), parent='head', style=SHD))
    add(P('chin', (8, 4, 3), (-4, -4, 4), parent='head', style='mask'))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        add(P('slit' + nm, (4, 1, 1), (sx * 3.5 - 2, 9, 6.6), parent='head', style='void'))
        add(P('slitGlow' + nm, (2, 1, 1), (sx * 3.5 - 1, 9, 6.8), parent='head', style='frost_glow'))
        add(P('hoodSide' + nm, (2, 20, 10), (sx * 9 - 1, -6, -4), parent='head', style=SH))
    add(P('crack', (1, 7, 1), (2, 2, 6.7), parent='head', style='frost_glow'))
    add(P('crack2', (1, 4, 1), (3, -1, 6.7), parent='head', style='frost_glow'))
    # a halo of icicles fanning out behind the head
    add(P('crownRoot', (4, 4, 2), (-2, -2, -1), (0, 10, -9), parent='head', style='ice_d'))
    for i in range(13):
        a = (i - 6) * 0.26
        ln = 30 - abs(i - 6) * 2 + (4 if i % 2 == 0 else 0)
        c = f'icicle{i}'
        add(P(c, (2, ln, 2), (-1, 0, -1), (0, 0, 0), rot=(-0.25, 0, a), parent='crownRoot', style=ICE))
        add(P(c + 'Tip', (1, 6, 1), (-0.5, 0, -0.5), (0, ln, 0), parent=c, style='frost_glow' if i % 3 == 0 else ICE))

    # ---- arms: shrouded shoulders and sleeves, bone-thin arms to the knees, long frozen fingers
    for side, sx in (('R', -1), ('L', 1)):
        n = 'arm' + side
        add(P(n, (5, 28, 5), (-2.5, -28, -2.5), (sx * 15, 76, 0), rot=(-0.12, 0, -sx * 0.16), style='bone_d', anim='armA' if sx < 0 else 'armB'))
        add(P(n + 'Sleeve', (10, 16, 10), (-5, -16, -5), parent=n, style=SH))
        for k in range(3):
            add(P(f'{n}SleeveTatter{k}', (3, 14 + 4 * k, 1), (-1.5, -14 - 4 * k, -0.5), (-3 + 3 * k, -14, 4.5 - 9 * (k % 2)),
                  parent=n, style=SHD, anim='sway'))
        add(P(n + 'Fore', (4, 26, 4), (-2, -26, -2), (0, -28, 0), rot=(-0.2, 0, sx * 0.08), parent=n, style='bone_d'))
        add(P(n + 'Bracer', (6, 6, 6), (-3, -6, -3), parent=n + 'Fore', style=ICE))
        add(P(n + 'Hand', (6, 6, 3), (-3, -6, -1.5), (0, -26, 0), parent=n + 'Fore', style='bone'))
        for k in range(4):
            f = f'{n}Finger{k}'
            add(P(f, (1, 12, 1), (-0.5, -12, -0.5), (-2.25 + 1.5 * k, -6, 0.5), rot=(0.18, 0, (k - 1.5) * 0.08), parent=n + 'Hand', style='bone'))
            add(P(f + 'Claw', (1, 6, 1), (-0.5, -6, -0.5), (0, -12, 0), rot=(0.35, 0, 0), parent=f, style=ICE))
    # left hand: a cold lantern on a chain
    add(P('chain', (1, 9, 1), (-0.5, -9, -0.5), (0, -4, 2), parent='armLHand', style='steel', anim='sway'))
    add(P('lantern', (7, 9, 7), (-3.5, -9, -3.5), (0, -9, 0), parent='chain', style='steel'))
    add(P('lanternFlame', (5, 6, 5), (-2.5, -7.5, -2.5), parent='lantern', style='frost_glow', anim='pulse'))
    add(P('lanternCap', (9, 2, 9), (-4.5, -1, -4.5), parent='lantern', style='steel'))
    # right hand: an icicle lance, taller than a man
    add(P('lance', (2, 74, 2), (-1, -30, -1), (0, -4, 3), rot=(0.18, 0, 0), parent='armRHand', style=ICE))
    add(P('lanceHead', (4, 14, 2), (-2, 44, -1), parent='lance', style='ice_d'))
    add(P('lanceTip', (2, 8, 2), (-1, 58, -1), parent='lance', style='frost_glow'))
    add(P('lanceGuard', (10, 2, 2), (-5, 42, -1), parent='lance', style=ICE))
    for k in range(3):
        add(P(f'lanceRibbon{k}', (2, 16 - 3 * k, 1), (-1, -16 + 3 * k, -0.5), (-3 + 3 * k, 42, 1), parent='lance', style=SH, anim='sway'))
    return parts


# ====================================================================================== KHARZUL
def kharzul(P):
    """A hunched four-armed reaper of bone and red glass in a torn crimson shroud. An hourglass burns in his open
    ribcage, a crown of glass blades turns behind his horned skull, and his scythe is a single curved pane of red glass."""
    parts = []
    add = parts.append
    GL, GG, ROBE = 'glass_red', 'glass_glow', 'robe_red'

    # ---- legs: digitigrade bone with glass greaves
    for side, sx in (('R', -1), ('L', 1)):
        n = 'leg' + side
        add(P(n, (7, 22, 8), (-3.5, -22, -4), (sx * 8, 44, 0), rot=(-0.45, 0, -sx * 0.06), style='bone_d', anim='legA' if sx < 0 else 'legB'))
        add(P(n + 'Greave', (8, 10, 3), (-4, -14, 3.5), parent=n, style=GL))
        add(P(n + 'Shin', (5, 22, 5), (-2.5, -22, -2.5), (0, -22, 0), rot=(0.95, 0, 0), parent=n, style='bone'))
        add(P(n + 'ShinShard', (2, 9, 3), (-1, -10, -5), rot=(-0.3, 0, 0), parent=n + 'Shin', style=GL))
        add(P(n + 'Ankle', (5, 14, 5), (-2.5, -14, -2.5), (0, -22, 0), rot=(-0.5, 0, 0), parent=n + 'Shin', style='bone_d'))
        add(P(n + 'Foot', (8, 3, 9), (-4, -3, -2), (0, -14, 0), parent=n + 'Ankle', style='bone_d'))
        for k in range(3):
            add(P(f'{n}Toe{k}', (2, 2, 7), (-1, -2, 0), (-3 + 3 * k, -1, 6), rot=(0.4, (k - 1) * 0.3, 0), parent=n + 'Foot', style='bone'))

    # ---- pelvis, spine, open ribcage with the hourglass, glass growing from the back
    add(P('pelvis', (18, 8, 11), (-9, 0, -5.5), (0, 42, 0), style='bone_d'))
    add(P('robeBelt', (20, 4, 13), (-10, 4, -6.5), parent='pelvis', style='sand'))
    for i in range(12):
        a = math.pi * 0.15 + i * (math.pi * 1.7) / 11           # leaves the front open over the legs
        ln = 32 - (i % 3) * 6
        t = f'robe{i}'
        add(P(t, (5, ln, 1), (-2.5, -ln, -0.5), (11 * math.sin(a + math.pi), 6, 8 * math.cos(a + math.pi)),
              rot=(0.15 * math.cos(a + math.pi), a + math.pi, 0.1 * math.sin(a)), parent='pelvis', style=ROBE if i % 2 else 'robe_d', anim='sway'))
    add(P('torso', (6, 26, 6), (-3, 0, -3), (0, 50, -2), rot=(0.45, 0, 0), style='bone_d'))
    for k in range(5):
        add(P(f'vert{k}', (5, 3, 4), (-2.5, 2 + 5 * k, -6), parent='torso', style='bone'))
    for k in range(5):
        y = 6 + 4 * k
        w = 22 - abs(k - 2) * 2
        for sx, nm in ((-1, 'R'), (1, 'L')):
            add(P(f'ribSide{nm}{k}', (2, 2, 13), (sx * (w / 2) - 1, y, -6), parent='torso', style='bone'))
            add(P(f'ribFront{nm}{k}', (w / 2 - 4, 2, 2), (sx > 0 and 3 or -(w / 2 - 1), y, 6), parent='torso', style='bone'))
    # the hourglass: gold caps, four posts, two glass bulbs, burning sand
    add(P('hgTop', (12, 2, 12), (-6, 22, -2), parent='torso', style='gold_d'))
    add(P('hgBot', (12, 2, 12), (-6, 4, -2), parent='torso', style='gold_d'))
    for k, (x, z) in enumerate([(-5.5, -1.5), (4.5, -1.5), (-5.5, 8.5), (4.5, 8.5)]):
        add(P(f'hgPost{k}', (1, 16, 1), (x, 6, z), parent='torso', style='gold_d'))
    add(P('hgUpper', (8, 7, 8), (-4, 15, 0), parent='torso', style=GL))
    add(P('hgLower', (8, 7, 8), (-4, 6, 0), parent='torso', style=GL))
    add(P('hgNeck', (2, 2, 2), (-1, 13, 3), parent='torso', style=GG))
    add(P('sandUp', (4, 3, 4), (-2, 15.5, 2), parent='torso', style='sand_glow', anim='pulse'))
    add(P('sandLow', (6, 3, 6), (-3, 6.5, 1), parent='torso', style='sand_glow', anim='pulse'))
    for k, (x, y, ln, rx, rz) in enumerate([(-6, 18, 14, -1.0, 0.5), (0, 22, 18, -1.2, 0.0), (6, 18, 13, -0.9, -0.5),
                                             (-3, 10, 10, -1.3, 0.3), (4, 12, 11, -1.4, -0.3), (0, 4, 8, -1.5, 0.0)]):
        c = f'backGlass{k}'
        add(P(c, (3, ln, 3), (-1.5, 0, -1.5), (x, y, -6), rot=(rx, 0, rz), parent='torso', style=GL))
        add(P(c + 'Tip', (1, 4, 1), (-0.5, 0, -0.5), (0, ln, 0), parent=c, style=GG))

    # ---- shoulders: a yoke of bone under a torn mantle, red glass clusters bursting through
    add(P('yoke', (30, 6, 12), (-15, 24, -6), parent='torso', style='bone_d'))
    add(P('mantle', (34, 7, 16), (-17, 27, -8), parent='torso', style=ROBE))
    for i in range(8):
        ln = 14 + (i % 3) * 5
        add(P(f'mantleTatter{i}', (4, ln, 1), (-2, -ln, -0.5), (-14 + 4 * i, 27, -8.5), parent='torso', style='robe_d', anim='sway'))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        for k, (dx, ln, rz, rx) in enumerate([(0, 16, 0.35, -0.2), (3, 11, 0.8, 0.3), (-3, 12, 0.1, -0.6), (5, 8, 1.2, -0.1)]):
            c = f'shoulderGlass{nm}{k}'
            add(P(c, (4, ln, 4), (-2, 0, -2), (sx * (13 + dx), 31, -1 + k), rot=(rx, 0, -sx * rz), parent='torso', style=GL))
            add(P(c + 'Tip', (2, 4, 2), (-1, 0, -1), (0, ln, 0), parent=c, style=GG))

    # ---- head: a long horned skull under a crimson cowl, burning eyes, and a turning crown of glass blades
    add(P('neck', (4, 8, 4), (-2, 0, -2), (0, 28, 2), rot=(-0.3, 0, 0), parent='torso', style='bone'))
    add(P('head', (11, 11, 12), (-5.5, 0, -5), (0, 34, 4), rot=(-0.35, 0, 0), parent='torso', style='bone', anim='head'))
    add(P('snout', (8, 6, 6), (-4, 0, 7), parent='head', style='bone'))
    add(P('cowl', (15, 15, 12), (-7.5, -2, -8), parent='head', style=ROBE))
    add(P('cowlPeak', (9, 6, 8), (-4.5, 12, -7), parent='head', style=ROBE))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        add(P('socket' + nm, (3, 3, 1), (sx * 2.7 - 1.5, 5, 6.6), parent='head', style='void'))
        add(P('eye' + nm, (2, 2, 1), (sx * 2.7 - 1, 5.5, 6.9), parent='head', style=GG))
        add(P('cowlSide' + nm, (2, 15, 10), (sx * 7.5 - 1, -4, -5), parent='head', style='robe_d'))
        h = 'horn' + nm
        add(P(h, (3, 3, 12), (-1.5, -1.5, -12), (sx * 5, 10, -2), rot=(0.6, sx * 0.5, 0), parent='head', style='bone_d'))
        add(P(h + '2', (2, 2, 11), (-1, -1, -11), (0, 0, -12), rot=(-0.7, 0, 0), parent=h, style='bone_d'))
        add(P(h + '3', (1, 1, 8), (-0.5, -0.5, -8), (0, 0, -11), rot=(-0.6, 0, 0), parent=h + '2', style=GL))
    add(P('noseHole', (2, 2, 1), (-1, 3, 12.6), parent='head', style='void'))
    add(P('teeth', (7, 2, 1), (-3.5, 0, 12.6), parent='head', style='bone_d'))
    add(P('jaw', (8, 3, 11), (-4, -3, -1), (0, 0, 1), rot=(0.2, 0, 0), parent='head', style='bone', anim='jaw'))
    add(P('crownRoot', (2, 2, 2), (-1, -1, -1), (0, 14, -9), parent='head', style='void', anim='spin'))
    for i in range(10):
        a = i * 2 * math.pi / 10
        c = f'crownBlade{i}'
        add(P(c, (2, 11 + (i % 2) * 4, 1), (-1, -5, -0.5), (14 * math.cos(a), 0, 14 * math.sin(a)), rot=(0, -a, 0.25), parent='crownRoot', style=GL))
        add(P(c + 'Edge', (1, 9 + (i % 2) * 4, 1), (-0.5, -4, 0.6), parent=c, style=GG))

    # ---- four arms: the upper pair wields the scythe and reaches; the lower pair holds two glass sickles
    for side, sx in (('R', -1), ('L', 1)):
        n = 'arm' + side
        add(P(n, (5, 22, 5), (-2.5, -22, -2.5), (sx * 16, 29, 0), rot=(-0.55 if sx < 0 else -1.0, 0, -sx * 0.22), parent='torso',
              style='bone_d', anim='armA' if sx < 0 else 'armB'))
        add(P(n + 'Pauldron', (9, 6, 9), (-4.5, -3, -4.5), parent=n, style=GL))
        add(P(n + 'Fore', (4, 22, 4), (-2, -22, -2), (0, -22, 0), rot=(-0.55 if sx < 0 else -0.3, 0, 0), parent=n, style='bone'))
        add(P(n + 'Wrap', (6, 8, 6), (-3, -10, -3), parent=n + 'Fore', style='sand'))
        add(P(n + 'Hand', (6, 5, 4), (-3, -5, -2), (0, -22, 0), parent=n + 'Fore', style='bone_d'))
        for k in range(4):
            f = f'{n}Finger{k}'
            add(P(f, (1, 8, 1), (-0.5, -8, -0.5), (-2.25 + 1.5 * k, -5, 1), rot=(0.5, 0, 0), parent=n + 'Hand', style='bone'))
            add(P(f + 'Claw', (1, 5, 1), (-0.5, -5, -0.5), (0, -8, 0), rot=(0.6, 0, 0), parent=f, style=GL))
        m = 'lowArm' + side
        add(P(m, (4, 16, 4), (-2, -16, -2), (sx * 11, 12, 2), rot=(-0.9, 0, -sx * 0.3), parent='torso', style='bone', anim='armB' if sx < 0 else 'armA'))
        add(P(m + 'Fore', (3, 15, 3), (-1.5, -15, -1.5), (0, -16, 0), rot=(-0.6, 0, sx * 0.2), parent=m, style='bone'))
        add(P(m + 'Hand', (4, 4, 3), (-2, -4, -1.5), (0, -15, 0), parent=m + 'Fore', style='bone_d'))
        sk = m + 'Sickle'
        add(P(sk, (2, 8, 2), (-1, -2, -1), (0, -3, 0), rot=(-1.2, 0, 0), parent=m + 'Hand', style='bone_d'))
        for k in range(4):
            add(P(f'{sk}Blade{k}', (1, 5, 3), (-0.5, 0, 0), (0, 6 + 3.5 * k, 1 + k * 1.2), rot=(0.45 * k, 0, 0), parent=sk, style=GL if k < 3 else GG))

    # ---- the scythe, gripped in the upper right hand: a long dark haft, gold bindings, a curved pane of red glass
    add(P('scythe', (3, 100, 3), (-1.5, -40, -1.5), (0, -4, 1), rot=(0.75, 0, 0), parent='armRHand', style='haft'))
    for k, y in enumerate((-38, -10, 20, 52)):
        add(P(f'scytheBand{k}', (5, 3, 5), (-2.5, y, -2.5), parent='scythe', style='gold_d'))
    add(P('scytheSocket', (6, 8, 6), (-3, 54, -3), parent='scythe', style='gold_d'))
    add(P('scythePommel', (4, 6, 4), (-2, -46, -2), parent='scythe', style=GL))
    prev, ang = 'scythe', 0.0
    pivot = (0, 58, 2)
    for k in range(8):
        ln = 13 - k
        b = f'scytheBlade{k}'
        add(P(b, (2, 7 - k * 0.5, ln), (-1, -3, 0), pivot, rot=(0.22 if k else 0.15, 0, 0), parent=prev, style=GL))
        add(P(b + 'Edge', (1, 2, ln), (-0.5, -5 + k * 0.25, 0), parent=b, style=GG))
        prev, pivot = b, (0, 0, ln - 1)
    add(P('scytheSpike', (2, 2, 10), (-1, -1, -10), (0, 58, -2), rot=(-0.4, 0, 0), parent='scythe', style=GL))
    return parts
