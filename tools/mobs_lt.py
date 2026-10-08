"""The lieutenants' models (lieutenants.py): three per realm and two Heralds, built in the usual box-model space (units of 1/16
block, y up from the feet, front toward +z). Each is authored at a natural size and scaled to its hitbox height on registration.
Built to frighten: hunched shoulders, spines, horns, too many eyes, glowing wounds."""
import math

from mobs_act2 import side_box, side_name

STYLES = {
    'bark_black': dict(base=(40, 30, 24), var=6, patches=[((60, 44, 32), 14, (1, 3)), ((24, 18, 14), 12, (1, 2))], cracks=(120, 255, 90)),
    'briar': dict(base=(60, 40, 26), var=8, patches=[((90, 60, 34), 12, (1, 2)), ((40, 90, 30), 10, (1, 2))]),
    'wolf_fur': dict(base=(52, 46, 40), var=8, patches=[((70, 62, 52), 14, (1, 3)), ((34, 30, 26), 12, (1, 2))]),
    'rot_flesh': dict(base=(92, 70, 60), var=8, patches=[((120, 90, 70), 12, (1, 2)), ((60, 40, 36), 12, (1, 2))], dots=((150, 200, 80), 8, (1, 1))),
    'storm_stone': dict(base=(120, 128, 140), var=8, patches=[((160, 168, 180), 12, (1, 3)), ((80, 86, 98), 12, (1, 2))], cracks=(140, 230, 255)),
    'storm_feather': dict(base=(70, 80, 96), var=8, patches=[((110, 120, 140), 14, (1, 3)), ((40, 46, 58), 10, (1, 2))]),
    'magma_hide': dict(base=(44, 22, 18), var=6, patches=[((70, 34, 24), 12, (1, 2))], cracks=(255, 120, 30)),
    'chain_iron': dict(base=(70, 70, 76), var=8, patches=[((100, 100, 108), 12, (1, 2)), ((40, 40, 46), 12, (1, 1))]),
    'skull': dict(base=(214, 204, 180), var=8, patches=[((180, 168, 140), 12, (1, 2)), ((240, 234, 214), 10, (1, 1))]),
    'crab_shell': dict(base=(150, 60, 50), var=10, patches=[((190, 90, 70), 12, (1, 3)), ((100, 36, 34), 12, (1, 2))], dots=((90, 200, 180), 8, (1, 1))),
    'drowned_coat': dict(base=(30, 50, 60), var=6, patches=[((50, 80, 86), 12, (1, 2)), ((20, 30, 36), 10, (1, 2))]),
    'eel_skin': dict(base=(30, 80, 86), var=8, patches=[((60, 130, 130), 12, (1, 3)), ((16, 50, 56), 12, (1, 2))]),
    'yeti_fur': dict(base=(224, 228, 236), var=7, patches=[((196, 202, 214), 14, (1, 3)), ((250, 252, 255), 10, (1, 2))]),
    'black_ice': dict(base=(30, 40, 60), var=6, patches=[((50, 66, 96), 12, (1, 3)), ((80, 110, 160), 8, (1, 1))], cracks=(170, 220, 255)),
    'veil': dict(base=(200, 210, 226), var=6, patches=[((170, 180, 200), 12, (1, 3)), ((230, 236, 246), 10, (1, 2))]),
    'red_glass': dict(base=(170, 30, 40), var=10, patches=[((220, 70, 70), 12, (1, 2)), ((110, 16, 26), 12, (1, 2))]),
    'grave_cloth': dict(base=(196, 180, 140), var=8, patches=[((160, 140, 100), 14, (1, 3)), ((220, 206, 170), 10, (1, 2))]),
    'pharaoh_gold': dict(base=(220, 170, 60), var=10, patches=[((250, 210, 110), 12, (1, 2)), ((160, 110, 30), 12, (1, 2))]),
    'pharaoh_blue': dict(base=(30, 60, 140), var=6, patches=[((50, 90, 180), 10, (1, 2))]),
    'gear_iron': dict(base=(56, 54, 62), var=6, patches=[((84, 80, 90), 12, (1, 2)), ((36, 34, 42), 12, (1, 2))], dots=((200, 150, 70), 8, (1, 1))),
    'myco_hide': dict(base=(150, 120, 130), var=8, patches=[((180, 150, 160), 12, (1, 3)), ((110, 80, 96), 12, (1, 2))], dots=((240, 120, 230), 8, (1, 1))),
    'pale_stalk': dict(base=(226, 220, 214), var=6, patches=[((200, 190, 184), 12, (1, 3)), ((246, 242, 236), 10, (1, 2))]),
    'lumen': dict(base=(190, 90, 220), var=12, patches=[((240, 150, 250), 12, (1, 3)), ((130, 50, 170), 10, (1, 2))]),
    'void_plate': dict(base=(20, 18, 26), var=4, patches=[((36, 32, 46), 14, (1, 3))], cracks=(170, 90, 255)),
    'eye_white': dict(base=(236, 232, 226), var=4, patches=[((214, 206, 196), 10, (1, 2))]),
    'eye_red': dict(base=(255, 50, 40), var=10, patches=[((255, 160, 120), 8, (1, 1))]),
    'eye_green': dict(base=(120, 255, 80), var=10, patches=[((220, 255, 180), 8, (1, 1))]),
    'eye_cyan': dict(base=(90, 230, 255), var=10, patches=[((220, 250, 255), 8, (1, 1))]),
    'eye_orange': dict(base=(255, 140, 30), var=10, patches=[((255, 220, 120), 8, (1, 1))]),
    'eye_violet': dict(base=(190, 100, 255), var=10, patches=[((240, 210, 255), 8, (1, 1))]),
    'eye_pink': dict(base=(255, 90, 230), var=10, patches=[((255, 210, 250), 8, (1, 1))]),
    'eye_ice': dict(base=(200, 240, 255), var=6, patches=[((255, 255, 255), 8, (1, 1))]),
    'eye_amber': dict(base=(255, 190, 40), var=10, patches=[((255, 240, 160), 8, (1, 1))]),
    'lightning': dict(base=(200, 240, 255), var=10, patches=[((140, 200, 255), 10, (1, 2))]),
}
GLOW = {'eye_red', 'eye_green', 'eye_cyan', 'eye_orange', 'eye_violet', 'eye_pink', 'eye_ice', 'eye_amber', 'lightning', 'lumen'}
S = side_name


def spikes_along(P, add, base, parent, n, x0, x1, y, z, h0, h1, style, rx=-0.5, w=2):
    """A row of n spikes along a back, from (x0..x1) at height y, tapering from h0 to h1 and leaning back by rx."""
    for i in range(n):
        t = i / max(1, n - 1)
        x = x0 + (x1 - x0) * t
        h = h0 + (h1 - h0) * t
        add(P(f'{base}{i}', (w, h, w), (-w / 2, 0, -w / 2), (x, y, z), rot=(rx, 0, 0), parent=parent, style=style))


def eyes(P, add, parent, y, z, style, n=2, spread=2.4, w=2, h=1, base='eye', x0=0.0):
    xs = [x0 + (i - (n - 1) / 2) * spread for i in range(n)]
    for i, x in enumerate(xs):
        add(P(f'{base}{i}', (w, h, 1), (x - w / 2, y, z), parent=parent, style=style))


def horns(P, add, parent, x, y, z, segs, style, tip, base='horn', out=1.0, up=0.0, back=-0.3):
    """A pair of curling horns: segs is a list of (w, length) from the root out."""
    for sx in (-1, 1):
        prev = parent
        for i, (w, ln) in enumerate(segs):
            name = f'{base}{S(sx)}{i}'
            piv = (sx * x, y, z) if i == 0 else (0, segs[i - 1][1] - 0.5, 0)
            rz = -sx * (out if i == 0 else -0.55)
            rx = back if i == 0 else (up if up else -0.2)
            add(P(name, (w, ln, w), (-w / 2, 0, -w / 2), piv, rot=(rx, 0, rz), parent=prev, style=tip if i == len(segs) - 1 else style))
            prev = name


def legs2(P, add, x, hip, thigh, shin, style, foot_style, claw=None, z=0, anim=True):
    for sx in (-1, 1):
        n = 'leg' + S(sx)
        add(P(n, thigh, (-thigh[0] / 2, -thigh[1], -thigh[2] / 2), (sx * x, hip, z), style=style, anim=('legA' if sx < 0 else 'legB') if anim else 'none'))
        add(P(n + 'Shin', shin, (-shin[0] / 2, -thigh[1] - shin[1] + 1, -shin[2] / 2), parent=n, style=style))
        add(P(n + 'Foot', (shin[0] + 2, 3, shin[2] + 4), (-(shin[0] + 2) / 2, -thigh[1] - shin[1] - 1, -shin[2] / 2), parent=n, style=foot_style))
        if claw:
            for k in (-1, 0, 1):
                add(P(f'{n}Claw{k + 1}', (1, 1, 3), (k * 1.6 - 0.5, -thigh[1] - shin[1] - 1, shin[2] / 2 + 3.5), parent=n, style=claw))


def arms2(P, add, x, y, upper, fore, style, hand_style, reach=(-0.35, -0.35), anim=True, base='arm'):
    names = []
    for i, sx in enumerate((-1, 1)):
        n = base + S(sx)
        add(P(n, upper, (-upper[0] / 2, -upper[1], -upper[2] / 2), (sx * x, y, 0), rot=(reach[i], 0, -sx * 0.12), style=style,
              anim=('armA' if sx < 0 else 'armB') if anim else 'none'))
        add(P(n + 'Fore', fore, (-fore[0] / 2, -upper[1] - fore[1] + 1, -fore[2] / 2), parent=n, style=style))
        names.append(n)
    return names


# ============================================================================================== the Gaudy Grove
def thornmaw(P):
    """A wolf the size of a cart, grown through with briars: a ridge of thorns down its spine, a jaw full of splinters, green eyes."""
    parts = []
    add = parts.append
    add(P('body', (16, 14, 30), (-8, -7, -15), (0, 20, 0), style='wolf_fur'))
    add(P('chest', (18, 16, 12), (-9, -9, 6), parent='body', style='wolf_fur'))
    add(P('mane', (20, 8, 10), (-10, 4, 8), parent='body', style='briar'))
    spikes_along(P, add, 'thorn', 'body', 7, 0, 0, 6, 0, 8, 4, 'thorn', rx=-0.6)
    for k, z in enumerate((10, 2, -6, -12)):
        add(P(f'thornRow{k}', (2, 6, 2), (-1, 0, -1), (0, 6, z), rot=(-0.6, 0, 0), parent='body', style='thorn'))
        for sx in (-1, 1):
            add(P(f'flank{k}{S(sx)}', (2, 5, 2), (-1, 0, -1), (sx * 7, 3, z), rot=(0, 0, -sx * 0.9), parent='body', style='thorn'))
    add(P('neck', (10, 10, 10), (-5, -5, 0), (0, 2, 14), rot=(-0.3, 0, 0), parent='body', style='wolf_fur'))
    add(P('head', (12, 10, 12), (-6, -5, 0), (0, 4, 8), parent='neck', style='wolf_fur', anim='head'))
    add(P('snout', (8, 6, 10), (-4, -6, 10), parent='head', style='wolf_fur'))
    add(P('jaw', (8, 3, 10), (-4, -9, 9), parent='head', style='bark_d', anim='jaw'))
    for k in range(4):
        add(P(f'fangU{k}', (1, 3, 1), (-3 + k * 2, -9, 18), parent='head', style='bone'))
    eyes(P, add, 'head', 1, 12.1, 'eye_green', spread=6)
    for sx in (-1, 1):
        add(P('ear' + S(sx), (3, 6, 2), (-1.5, 0, -1), (sx * 4, 5, 2), rot=(-0.3, 0, -sx * 0.3), parent='head', style='briar'))
        add(P('antler' + S(sx), (2, 8, 2), (-1, 0, -1), (sx * 4, 4, 0), rot=(-0.5, 0, -sx * 0.6), parent='head', style='bark_black'))
        add(P('antlerB' + S(sx), (2, 6, 2), (-1, 0, -1), (0, 7, 0), rot=(0.3, 0, sx * 0.9), parent='antler' + S(sx), style='thorn'))
    for i, (x, z) in enumerate([(-6, 10), (6, 10), (-6, -10), (6, -10)]):
        n = f'leg{i}'
        add(P(n, (6, 12, 6), (-3, -12, -3), (x, -4, z), parent='body', style='wolf_fur', anim='legA' if i in (0, 3) else 'legB'))
        add(P(n + 'Paw', (7, 3, 8), (-3.5, -16, -3), parent=n, style='bark_d'))
        for k in (-1, 1):
            add(P(f'{n}Claw{k}', (1, 2, 3), (k * 2 - 0.5, -16, 5), parent=n, style='bone'))
    add(P('tail', (4, 4, 14), (-2, -2, -14), (0, 4, -15), rot=(0.4, 0, 0), parent='body', style='briar', anim='sway'))
    add(P('tailThorns', (6, 6, 6), (-3, -3, -18), (0, 4, -15), rot=(0.4, 0, 0), parent='body', style='thorn'))
    return parts


def hollowbark(P):
    """The oldest tree in the Grove, dead and walking: a split trunk of black bark with a glowing green hollow for a chest, ants in it,
    branch-claw arms dragging on the ground, a crown of dead limbs and a face of knots with two green eyes."""
    parts = []
    add = parts.append
    legs2(P, add, 6, 30, (9, 16, 9), (8, 14, 8), 'bark_black', 'root_c', claw='root_c')
    add(P('body', (22, 30, 14), (-11, 0, -7), (0, 30, 0), style='bark_black'))
    add(P('hollow', (10, 14, 2), (-5, 6, 6), parent='body', style='glowg'))
    add(P('hollowRim', (14, 18, 1), (-7, 4, 7), parent='body', style='bark_d'))
    for k in range(3):
        add(P(f'ant{k}', (2, 1, 1), (-4 + k * 3, 10 + k * 2, 8), parent='body', style='void'))
    add(P('moss', (24, 4, 16), (-12, 24, -8), parent='body', style='moss_dk'))
    add(P('shoulders', (30, 8, 16), (-15, 26, -8), parent='body', style='bark_black'))
    add(P('head', (14, 14, 12), (-7, 0, -6), (0, 34, 1), parent='body', style='bark_black', anim='head'))
    add(P('face', (10, 8, 1), (-5, 2, 6), parent='head', style='bark_d'))
    eyes(P, add, 'head', 6, 6.5, 'eye_green', spread=5, w=2, h=2)
    add(P('maw', (6, 3, 1), (-3, 1, 6.5), parent='head', style='void'))
    for k, (x, rz, ln) in enumerate([(-6, 0.5, 14), (-2, 0.15, 18), (3, -0.25, 16), (6, -0.6, 12)]):
        add(P(f'crown{k}', (3, ln, 3), (-1.5, 0, -1.5), (x, 12, -1), rot=(-0.2, 0, rz), parent='head', style='bark_black'))
        add(P(f'crownTwig{k}', (2, 7, 2), (-1, 0, -1), (0, ln - 2, 0), rot=(0.4, 0, -rz * 1.8), parent=f'crown{k}', style='bark_d'))
    for sx in (-1, 1):
        a = 'arm' + S(sx)
        add(P(a, (8, 22, 8), (-4, -22, -4), (sx * 16, 54, 0), rot=(-0.25, 0, -sx * 0.2), style='bark_black', anim='armA' if sx < 0 else 'armB'))
        add(P(a + 'Fore', (7, 20, 7), (-3.5, -41, -3.5), parent=a, style='bark_black'))
        for k in range(4):
            add(P(f'{a}Claw{k}', (2, 12, 2), (-1, -12, -1), (-3 + k * 2, -40, 2), rot=(0.5, 0, (k - 1.5) * 0.25), parent=a, style='root_c'))
        add(P(a + 'Shroom', (6, 3, 6), (-3, 0, -3), (0, 2, 0), parent=a, style='cap'))
    spikes_along(P, add, 'backBranch', 'body', 4, -6, 6, 24, -7, 14, 10, 'bark_d', rx=-0.8, w=3)
    return parts


def rot_matron(P):
    """A spider like a fallen log: a swollen abdomen sprouting mushrooms and rot, eight jointed legs of bark, a cluster of
    green eyes, mandibles of bone."""
    parts = []
    add = parts.append
    add(P('body', (16, 10, 16), (-8, -5, -8), (0, 16, 4), style='bark_black'))
    add(P('abdomen', (24, 18, 26), (-12, -6, -28), parent='body', style='rot_flesh'))
    for k, (x, z, st) in enumerate([(-6, -14, 'cap'), (5, -20, 'cap_brown'), (0, -8, 'cap'), (-4, -24, 'cap_m'), (7, -10, 'cap')]):
        add(P(f'shroomS{k}', (2, 4, 2), (-1, 0, -1), (x, 11, z), parent='body', style='stem'))
        add(P(f'shroomC{k}', (6, 2, 6), (-3, 4, -3), (x, 11, z), parent='body', style=st))
    add(P('rot', (20, 2, 20), (-10, 11, -26), parent='body', style='moss_dk'))
    add(P('head', (12, 9, 10), (-6, -5, 0), (0, 0, 8), parent='body', style='bark_black', anim='head'))
    for k, (x, y) in enumerate([(-4, 1), (4, 1), (-2, 3), (2, 3), (-5, -1), (5, -1), (0, 0)]):
        add(P(f'eye{k}', (2, 2, 1), (x - 1, y, 10), parent='head', style='eye_green'))
    for sx in (-1, 1):
        add(P('mandible' + S(sx), (2, 3, 7), (-1, -3, 0), (sx * 3, -3, 9), rot=(0.3, -sx * 0.4, 0), parent='head', style='bone', anim='jaw'))
    for i in range(4):
        for sx in (-1, 1):
            n = f'leg{i}{S(sx)}'
            z = 5 - i * 4
            add(P(n, (14, 3, 3), (side_box(sx, 14), -1.5, -1.5), (sx * 7, 0, z), rot=(0, sx * (0.6 - i * 0.4), -sx * -0.6), parent='body',
                  style='bark_black', anim='legA' if (i + (sx > 0)) % 2 else 'legB'))
            add(P(n + 'Low', (3, 18, 3), (-1.5, -18, -1.5), (sx * 13, 0, 0), rot=(0, 0, sx * 0.25), parent=n, style='bark_d'))
    add(P('spinneret', (6, 6, 4), (-3, -2, -32), parent='body', style='rot_flesh'))
    return parts


# ============================================================================================== Skyreach
def galeclaw(P):
    """A storm hawk: slate feathers, wings like thunderheads crackling at the tips, a hooked beak, talons, a crest of lightning."""
    parts = []
    add = parts.append
    add(P('body', (12, 12, 22), (-6, -6, -11), (0, 16, 0), style='storm_feather'))
    add(P('chest', (14, 12, 10), (-7, -8, 4), parent='body', style='storm_l'))
    add(P('head', (10, 10, 10), (-5, -3, 0), (0, 3, 12), parent='body', style='storm_feather', anim='head'))
    add(P('beak', (4, 5, 6), (-2, -3, 9), parent='head', style='gold_d'))
    add(P('beakHook', (2, 4, 2), (-1, -6, 13), parent='head', style='gold_d'))
    eyes(P, add, 'head', 2, 10.1, 'eye_cyan', spread=6, w=2, h=2)
    for k in range(4):
        add(P(f'crest{k}', (1, 8 - k, 2), (-0.5, 0, -1), (0, 6, 4 - k * 2.5), rot=(-0.7 - k * 0.1, 0, 0), parent='head', style='lightning'))
    for sx in (-1, 1):
        w = 'wing' + S(sx)
        add(P(w, (26, 2, 16), (side_box(sx, 26), -1, -8), (sx * 6, 4, 0), parent='body', style='storm_feather', anim='wingL' if sx < 0 else 'wingR'))
        add(P(w + 'Tip', (16, 1, 12), (side_box(sx, 16), -0.5, -6), (sx * 26, 0, -2), rot=(0, 0, sx * 0.2), parent=w, style='storm_l'))
        for k in range(4):
            add(P(f'{w}Bolt{k}', (3, 1, 1), (side_box(sx, 3), 0.5, -0.5), (sx * (16 + k * 4), 0, -6 - k), parent=w, style='lightning'))
        add(P('leg' + S(sx), (3, 8, 3), (-1.5, -8, -1.5), (sx * 3, -6, 2), parent='body', style='gold_d'))
        for k in range(3):
            add(P(f'talon{S(sx)}{k}', (1, 2, 4), (-0.5, -10, k * 0 - 1), (sx * 3 + (k - 1) * 1.5, -6, 2), rot=(0.5, 0, 0), parent='body', style='bone'))
    add(P('tail', (10, 2, 14), (-5, -1, -14), (0, 2, -11), rot=(0.2, 0, 0), parent='body', style='storm_feather', anim='sway'))
    add(P('tailBolt', (2, 1, 10), (-1, 1, -12), (0, 2, -11), rot=(0.2, 0, 0), parent='body', style='lightning'))
    return parts


def thunder_colossus(P):
    """Calcite and stormcloud stacked into a giant: a cracked stone body seamed with lightning, a head of cloud with two burning
    eyes, fists like boulders, and a crown of lightning rods."""
    parts = []
    add = parts.append
    legs2(P, add, 7, 28, (10, 14, 10), (11, 14, 11), 'storm_stone', 'storm_stone')
    add(P('pelvis', (22, 8, 14), (-11, 0, -7), (0, 28, 0), style='storm_stone'))
    add(P('body', (30, 26, 18), (-15, 0, -9), (0, 34, 0), style='storm_stone'))
    add(P('core', (8, 8, 1), (-4, 10, 9), parent='body', style='lightning'))
    for k in range(5):
        add(P(f'seam{k}', (1, 9, 1), (-12 + k * 6, 4 + (k % 2) * 6, 9.1), rot=(0, 0, 0.4 * (1 if k % 2 else -1)), parent='body', style='lightning'))
    add(P('cloud', (40, 10, 24), (-20, 22, -12), parent='body', style='storm'))
    add(P('head', (16, 14, 14), (-8, 0, -7), (0, 30, 2), parent='body', style='storm', anim='head'))
    add(P('brow', (18, 4, 4), (-9, 7, 5), parent='head', style='storm_stone'))
    eyes(P, add, 'head', 4, 7.1, 'lightning', spread=8, w=3, h=2)
    for k, (x, ln) in enumerate([(-6, 12), (-2, 16), (2, 18), (6, 14)]):
        add(P(f'rod{k}', (2, ln, 2), (-1, 0, -1), (x, 13, -1), rot=(-0.15, 0, -x * 0.03), parent='head', style='gold_d'))
        add(P(f'rodTip{k}', (2, 2, 2), (-1, ln, -1), (x, 13, -1), rot=(-0.15, 0, -x * 0.03), parent='head', style='lightning'))
    for sx in (-1, 1):
        a = 'arm' + S(sx)
        add(P(a, (11, 22, 11), (-5.5, -22, -5.5), (sx * 20, 56, 0), rot=(-0.2, 0, -sx * 0.15), style='storm_stone', anim='armA' if sx < 0 else 'armB'))
        add(P(a + 'Fist', (15, 14, 15), (-7.5, -36, -7.5), parent=a, style='storm_stone'))
        add(P(a + 'Bolt', (2, 12, 1), (-1, -30, 7.6), rot=(0, 0, 0.3), parent=a, style='lightning'))
        add(P('shoulder' + S(sx), (14, 8, 14), (-7, 0, -7), (sx * 20, 56, 0), rot=(0, 0, -sx * 0.25), style='storm_stone'))
        add(P('shoulderSpike' + S(sx), (3, 10, 3), (-1.5, 6, -1.5), (sx * 20, 56, 0), rot=(0, 0, -sx * 0.45), style='gold_d'))
    return parts


def squall_seraph(P):
    """A winged knight of wind: white plate, a faceless helm with a slit of storm-light, a halo of hail, six wings of feathered
    sleet, and a long spear of wind."""
    parts = []
    add = parts.append
    add(P('body', (12, 18, 8), (-6, 0, -4), (0, 22, 0), style='quartz'))
    add(P('skirt', (14, 14, 10), (-7, -14, -5), parent='body', style='quartz'))
    add(P('trail', (8, 14, 6), (-4, -28, -3), parent='body', style='storm_l', anim='sway'))
    add(P('trailTip', (4, 10, 4), (-2, -38, -2), parent='body', style='lightning', anim='sway'))
    add(P('plate', (14, 10, 10), (-7, 8, -5), parent='body', style='gold_d'))
    add(P('head', (8, 10, 8), (-4, 0, -4), (0, 18, 0), parent='body', style='quartz', anim='head'))
    add(P('visor', (6, 1, 1), (-3, 5, 4), parent='head', style='lightning'))
    add(P('crest', (2, 8, 8), (-1, 8, -4), parent='head', style='gold_d'))
    for k in range(10):
        a = k * math.pi / 5
        add(P(f'hail{k}', (2, 2, 2), (-1, -1, -1), (math.cos(a) * 9, 14 + math.sin(a) * 9, -4), parent='head', style='eye_ice', anim='spin'))
    for i, (y, ln, rz) in enumerate([(14, 24, 0.5), (10, 30, 0.2), (6, 22, -0.15)]):
        for sx in (-1, 1):
            add(P(f'wing{i}{S(sx)}', (ln, 2, 10), (side_box(sx, ln), -1, -5), (sx * 4, y, -4), rot=(0, sx * 0.25, sx * rz), parent='body',
                  style='feather_w' if i != 1 else 'storm_l', anim='wingL' if sx < 0 else 'wingR'))
    a = arms2(P, add, 8, 37, (4, 10, 4), (4, 10, 4), 'quartz', 'gold_d', reach=(-1.0, -0.2))
    add(P('spear', (2, 46, 2), (-1, -30, -1), (0, -18, 2), rot=(1.4, 0, 0), parent=a[0], style='gold_d'))
    add(P('spearHead', (4, 10, 2), (-2, 16, -1), (0, -18, 2), rot=(1.4, 0, 0), parent=a[0], style='lightning'))
    return parts


# ============================================================================================== the Hollow
def cinderjaw(P):
    """A hound of cooling magma: black crust cracked with orange, a forge-mouth glowing inside, flaming mane, obsidian claws."""
    parts = []
    add = parts.append
    add(P('body', (18, 16, 30), (-9, -8, -15), (0, 22, 0), style='magma_hide'))
    add(P('chest', (20, 18, 12), (-10, -10, 6), parent='body', style='magma_hide'))
    add(P('mane', (22, 10, 14), (-11, 4, 4), parent='body', style='flame'))
    spikes_along(P, add, 'crag', 'body', 6, 0, 0, 7, -2, 9, 5, 'iron_dk', rx=-0.6, w=3)
    add(P('head', (14, 12, 14), (-7, -6, 0), (0, 4, 16), parent='body', style='magma_hide', anim='head'))
    add(P('forge', (8, 4, 1), (-4, -6, 14), parent='head', style='ember_glow'))
    add(P('jaw', (12, 4, 12), (-6, -10, 2), parent='head', style='magma_hide', anim='jaw'))
    for k in range(5):
        add(P(f'fang{k}', (1, 3, 1), (-4 + k * 2, -9, 14), parent='head', style='bone'))
    eyes(P, add, 'head', 1, 14.1, 'eye_orange', spread=7, w=3, h=2)
    for sx in (-1, 1):
        add(P('horn' + S(sx), (3, 10, 3), (-1.5, 0, -1.5), (sx * 5, 5, 4), rot=(-0.8, 0, -sx * 0.4), parent='head', style='iron_dk'))
    for i, (x, z) in enumerate([(-7, 11), (7, 11), (-7, -10), (7, -10)]):
        n = f'leg{i}'
        add(P(n, (7, 14, 7), (-3.5, -14, -3.5), (x, -4, z), parent='body', style='magma_hide', anim='legA' if i in (0, 3) else 'legB'))
        add(P(n + 'Paw', (8, 3, 9), (-4, -18, -3), parent=n, style='iron_dk'))
        add(P(n + 'Crack', (1, 8, 1), (-0.5, -12, 3.6), parent=n, style='ember_glow'))
    add(P('tail', (5, 5, 16), (-2.5, -2.5, -16), (0, 4, -15), rot=(0.5, 0, 0), parent='body', style='magma_hide', anim='sway'))
    add(P('tailFire', (7, 7, 8), (-3.5, -3.5, -22), (0, 4, -15), rot=(0.5, 0, 0), parent='body', style='flame'))
    return parts


def chainwarden(P):
    """The Hollow King's gaoler: a hulking armored jailer hung with chains and shackles, a cage for a head with an orange eye
    inside, a great hook on a chain in one hand and a ring of keys like a mace in the other."""
    parts = []
    add = parts.append
    legs2(P, add, 6, 26, (9, 13, 9), (9, 13, 9), 'ash_armor', 'iron_dk')
    add(P('body', (24, 24, 14), (-12, 0, -7), (0, 26, 0), style='ash_armor'))
    add(P('belly', (18, 10, 2), (-9, 2, 7), parent='body', style='chain_iron'))
    for k in range(6):
        add(P(f'chainV{k}', (1, 18, 1), (-11 + k * 4.2, -10, 7.4), parent='body', style='chain_iron', anim='sway'))
    for k in range(3):
        add(P(f'shackle{k}', (3, 3, 2), (-9 + k * 7, -13, 7), parent='body', style='iron_dk', anim='sway'))
    add(P('hunch', (26, 10, 16), (-13, 18, -9), parent='body', style='ash_armor'))
    spikes_along(P, add, 'back', 'body', 5, -9, 9, 22, -7, 10, 10, 'iron_dk', rx=-0.9, w=3)
    add(P('head', (14, 14, 14), (-7, 0, -7), (0, 28, 2), parent='body', style='chain_iron', anim='head'))
    for k in range(5):
        add(P(f'bar{k}', (1, 14, 1), (-6 + k * 3, 0, 7), parent='head', style='iron_dk'))
    add(P('inner', (10, 10, 10), (-5, 2, -5), parent='head', style='void'))
    add(P('eyeBig', (4, 4, 1), (-2, 6, 4.5), parent='head', style='eye_orange'))
    add(P('cageTop', (16, 3, 16), (-8, 13, -8), parent='head', style='iron_dk'))
    for sx in (-1, 1):
        add(P('pauldron' + S(sx), (12, 8, 14), (-6, 0, -7), (sx * 16, 48, 0), rot=(0, 0, -sx * 0.25), style='iron_dk'))
        add(P('pSpike' + S(sx), (3, 12, 3), (-1.5, 6, -1.5), (sx * 16, 48, 0), rot=(0, 0, -sx * 0.5), style='iron_dk'))
    a = arms2(P, add, 17, 46, (9, 18, 9), (9, 16, 9), 'ash_armor', 'iron_dk', reach=(-0.4, -0.2))
    add(P('hookChain', (1, 18, 1), (-0.5, -18, -0.5), (0, -33, 0), parent=a[0], style='chain_iron', anim='sway'))
    add(P('hook', (3, 10, 3), (-1.5, -28, -1.5), (0, -33, 0), parent=a[0], style='iron_dk', anim='sway'))
    add(P('hookBarb', (3, 3, 8), (-1.5, -28, 1.5), (0, -33, 0), parent=a[0], style='iron_dk', anim='sway'))
    add(P('keyring', (12, 12, 2), (-6, -42, -1), parent=a[1], style='gold_d'))
    for k in range(4):
        add(P(f'key{k}', (2, 6, 1), (-6 + k * 4, -48, -0.5), parent=a[1], style='gold_d'))
    return parts


def ashen_choir(P):
    """Three burning skulls bound by one long tattered shroud: the middle skull larger and crowned, each with a mouth of orange
    fire, the shroud trailing smoke and chains."""
    parts = []
    add = parts.append
    add(P('body', (16, 14, 10), (-8, -8, -5), (0, 30, 0), style='soul_robe'))
    add(P('shroud', (22, 18, 12), (-11, -26, -6), parent='body', style='shroud_d', anim='sway'))
    add(P('shroudTail', (14, 14, 8), (-7, -40, -4), parent='body', style='shroud', anim='sway'))
    for k in range(5):
        add(P(f'tatter{k}', (3, 10, 1), (-10 + k * 5, -50, 4), parent='body', style='shroud_d', anim='flutter'))
    for i, (x, y, k) in enumerate([(-14, 4, 0.8), (0, 10, 1.0), (14, 4, 0.8)]):
        n = f'skull{i}'
        s = k
        add(P(n, (12 * s, 12 * s, 12 * s), (-6 * s, 0, -6 * s), (x, y, 2), parent='body', style='skull', anim='head'))
        add(P(n + 'Jaw', (10 * s, 4 * s, 10 * s), (-5 * s, -4 * s, -4 * s), parent=n, style='skull', anim='jaw'))
        add(P(n + 'Fire', (6 * s, 3 * s, 1), (-3 * s, -3 * s, 6 * s), parent=n, style='flame'))
        for sx in (-1, 1):
            add(P(f'{n}Eye{S(sx)}', (3 * s, 3 * s, 1), (sx * 3 * s - 1.5 * s, 4 * s, 6 * s), parent=n, style='eye_orange'))
        add(P(n + 'Flame', (8 * s, 8 * s, 8 * s), (-4 * s, 12 * s, -4 * s), parent=n, style='flame', anim='pulse'))
    for k in range(5):
        a = -1.0 + k * 0.5
        add(P(f'crown{k}', (2, 7, 2), (-1, 0, -1), (math.sin(a) * 6, 22, math.cos(a) * 6 - 2), rot=(0.2, 0, -a * 0.5), parent='body', style='gold_d'))
    for sx in (-1, 1):
        add(P('chain' + S(sx), (1, 24, 1), (-0.5, -24, -0.5), (sx * 9, -2, 0), parent='body', style='chain_iron', anim='sway'))
        add(P('censer' + S(sx), (5, 5, 5), (-2.5, -29, -2.5), (sx * 9, -2, 0), parent='body', style='ember_glow', anim='sway'))
    return parts


# ============================================================================================== the Drowned Expanse
def reef_crusher(P):
    """A crab as wide as a house: a domed shell crusted with coral, barnacles and a broken mast, one claw far bigger than the
    other, stalked cyan eyes, eight spined legs."""
    parts = []
    add = parts.append
    add(P('body', (30, 12, 24), (-15, -6, -12), (0, 18, 0), style='crab_shell'))
    add(P('dome', (26, 8, 20), (-13, 6, -10), parent='body', style='crab_shell'))
    for k, (x, z, st) in enumerate([(-8, -4, 'coral'), (6, 2, 'coral_b'), (-2, 6, 'coral'), (9, -6, 'barnacle'), (-10, 5, 'barnacle')]):
        add(P(f'coral{k}', (3, 6, 3), (-1.5, 0, -1.5), (x, 13, z), rot=(0.2 * k - 0.4, 0, 0.3 - k * 0.15), parent='body', style=st))
    add(P('mast', (2, 22, 2), (-1, 0, -1), (-4, 13, -4), rot=(-0.4, 0, 0.3), parent='body', style='wood'))
    add(P('rag', (8, 6, 1), (0, 12, -0.5), (-4, 13, -4), rot=(-0.4, 0, 0.3), parent='body', style='robe_sea', anim='flutter'))
    for sx in (-1, 1):
        add(P('stalk' + S(sx), (2, 8, 2), (-1, 0, -1), (sx * 4, 4, 11), rot=(0.3, 0, -sx * 0.2), parent='body', style='crab_shell'))
        add(P('stalkEye' + S(sx), (3, 3, 3), (-1.5, 8, -1.5), (sx * 4, 4, 11), rot=(0.3, 0, -sx * 0.2), parent='body', style='eye_cyan'))
    big = (-1, 1)
    for sx in big:
        k = 1.6 if sx < 0 else 1.0
        a = 'claw' + S(sx)
        add(P(a, (5 * k, 5 * k, 14 * k), (-2.5 * k, -2.5 * k, 0), (sx * 13, 0, 10), rot=(0.1, -sx * 0.4, 0), parent='body', style='crab_shell', anim='armA' if sx < 0 else 'armB'))
        add(P(a + 'Pincer', (10 * k, 8 * k, 12 * k), (-5 * k, -4 * k, 13 * k), parent=a, style='crab_shell'))
        add(P(a + 'Finger', (4 * k, 3 * k, 10 * k), (-2 * k, -7 * k, 15 * k), parent=a, style='crab_shell', anim='jaw'))
        for t in range(3):
            add(P(f'{a}Tooth{t}', (1, 2, 1), (-3 * k + t * 3 * k, -4 * k, 24 * k), parent=a, style='bone'))
    for i in range(4):
        for sx in (-1, 1):
            n = f'leg{i}{S(sx)}'
            add(P(n, (14, 3, 3), (side_box(sx, 14), -1.5, -1.5), (sx * 14, -2, 6 - i * 6), rot=(0, sx * (0.3 - i * 0.25), -sx * -0.5), parent='body',
                  style='crab_shell', anim='legA' if (i + (sx > 0)) % 2 else 'legB'))
            add(P(n + 'Low', (3, 16, 3), (-1.5, -16, -1.5), (sx * 13, 0, 0), rot=(0, 0, sx * 0.3), parent=n, style='crab_shell'))
            add(P(n + 'Spine', (1, 3, 1), (-0.5, 0, -0.5), (sx * 8, 1, 0), parent=n, style='bone'))
    return parts


def drowned_admiral(P):
    """Vorath's admiral: a drowned captain in a rotting blue greatcoat and tricorne, kelp hanging off him, a lantern-cyan eye,
    a ship's anchor on a chain for a weapon, a cutlass in the other hand."""
    parts = []
    add = parts.append
    legs2(P, add, 4, 24, (6, 12, 6), (6, 12, 6), 'drowned_coat', 'iron_dk')
    add(P('body', (16, 20, 10), (-8, 0, -5), (0, 24, 0), style='drowned'))
    add(P('coat', (18, 22, 12), (-9, -14, -6), parent='body', style='drowned_coat'))
    add(P('coatTail', (16, 10, 2), (-8, -22, -6), parent='body', style='drowned_coat', anim='sway'))
    for k in range(4):
        add(P(f'button{k}', (1, 1, 1), (-0.5, 4 + k * 3, 6.1), parent='body', style='gold_d'))
        add(P(f'kelp{k}', (2, 10, 1), (-8 + k * 5, -18, 6.2), parent='body', style='kelp', anim='sway'))
    for sx in (-1, 1):
        add(P('epaulet' + S(sx), (8, 3, 10), (-4, 0, -5), (sx * 10, 44, 0), style='gold_d'))
        for k in range(3):
            add(P(f'fringe{S(sx)}{k}', (1, 4, 1), (-3 + k * 3, -4, 4.6), (sx * 10, 44, 0), style='gold_d'))
    add(P('head', (10, 10, 10), (-5, 0, -5), (0, 20, 0), parent='body', style='drowned', anim='head'))
    add(P('beard', (8, 6, 2), (-4, -4, 4), parent='head', style='kelp'))
    add(P('eyeL', (2, 2, 1), (1, 5, 5), parent='head', style='eye_cyan'))
    add(P('eyePatch', (3, 2, 1), (-4, 5, 5), parent='head', style='void'))
    add(P('hat', (18, 3, 12), (-9, 10, -6), parent='head', style='navy_d'))
    add(P('hatTop', (12, 5, 8), (-6, 12, -4), parent='head', style='navy_d'))
    add(P('hatSkull', (4, 3, 1), (-2, 13, 4), parent='head', style='skull'))
    a = arms2(P, add, 11, 42, (6, 12, 6), (6, 12, 6), 'drowned_coat', 'drowned', reach=(-0.5, -0.6))
    add(P('anchorChain', (1, 14, 1), (-0.5, -14, -0.5), (0, -23, 0), parent=a[0], style='chain_iron', anim='sway'))
    add(P('anchor', (3, 20, 3), (-1.5, -34, -1.5), (0, -23, 0), parent=a[0], style='iron_rust', anim='sway'))
    add(P('anchorArm', (18, 3, 3), (-9, -36, -1.5), (0, -23, 0), parent=a[0], style='iron_rust', anim='sway'))
    for sx in (-1, 1):
        add(P('fluke' + S(sx), (4, 6, 3), (sx * 8 - 2, -34, -1.5), (0, -23, 0), parent=a[0], style='iron_rust', anim='sway'))
    add(P('cutlass', (2, 18, 4), (-1, -38, -2), parent=a[1], style='steel'))
    add(P('guard', (6, 2, 6), (-3, -24, -3), parent=a[1], style='gold_d'))
    return parts


def abyssal_siren(P):
    """Half eel, half drowned queen: a long coiling eel tail where legs should be, a gaunt pale torso, hair of kelp floating up,
    webbed claws, a crown of coral and a jaw that opens too wide."""
    parts = []
    add = parts.append
    add(P('body', (12, 14, 8), (-6, 0, -4), (0, 36, 0), style='pearl'))
    add(P('ribs', (10, 6, 1), (-5, 2, 3.6), parent='body', style='bone_d'))
    prev = 'body'
    for i in range(6):
        w = 9 - i
        n = f'tail{i}'
        add(P(n, (w, 9, w), (-w / 2, -9, -w / 2), (0, 0 if i == 0 else -8, 0), rot=(0.25 if i % 2 else -0.15, 0, 0.12 * (1 if i % 2 else -1)),
              parent=prev, style='eel_skin', anim='undulate'))
        add(P(n + 'Fin', (1, 7, 6), (-0.5, -8, -w / 2 - 3), parent=n, style='fin'))
        prev = n
    add(P('head', (9, 10, 9), (-4.5, 0, -4.5), (0, 14, 0), parent='body', style='pearl', anim='head'))
    eyes(P, add, 'head', 5, 4.6, 'eye_cyan', spread=4, w=2, h=2)
    add(P('maw', (6, 5, 1), (-3, 0, 4.6), parent='head', style='void', anim='jaw'))
    for k in range(4):
        add(P(f'fang{k}', (1, 2, 1), (-2.5 + k * 1.6, 3, 4.8), parent='head', style='bone'))
    for k in range(6):
        add(P(f'hair{k}', (2, 16, 2), (-1, 0, -1), (-4 + k * 1.6, 9, -3), rot=(-0.4 - (k % 2) * 0.2, 0, (k - 2.5) * 0.15), parent='head', style='kelp', anim='flutter'))
    for k in range(5):
        a = -0.9 + k * 0.45
        add(P(f'crown{k}', (2, 6, 2), (-1, 0, -1), (math.sin(a) * 4, 9, math.cos(a) * 4), rot=(0.2, 0, -a * 0.6), parent='head', style='coral'))
    a = arms2(P, add, 7, 48, (3, 12, 3), (3, 12, 3), 'pearl', 'eel_skin', reach=(-1.1, -1.4))
    for i, n in enumerate(a):
        for k in range(3):
            add(P(f'{n}Claw{k}', (1, 6, 1), (-1.5 + k * 1.5, -28, -0.5), parent=n, style='bone'))
        add(P(n + 'Web', (5, 6, 1), (-2.5, -28, 0), parent=n, style='fin'))
    add(P('waterRing', (26, 1, 26), (-13, -10, -13), parent='body', style='water_glow', anim='spin'))
    return parts


# ============================================================================================== the Pale Wastes
def frostmaw(P):
    """A starving yeti: a hunched white giant, ribs showing through matted fur, arms to the ground with black-ice claws, a skull-
    like face with a long jaw, ice-blue eyes, icicles hanging off its back."""
    parts = []
    add = parts.append
    legs2(P, add, 6, 22, (9, 11, 9), (8, 11, 8), 'yeti_fur', 'black_ice', claw='black_ice')
    add(P('body', (24, 22, 16), (-12, 0, -8), (0, 22, -2), rot=(0.45, 0, 0), style='yeti_fur'))
    add(P('ribs', (14, 10, 1), (-7, 4, 8), parent='body', style='bone_d'))
    add(P('hump', (26, 12, 18), (-13, 16, -10), parent='body', style='yeti_fur'))
    spikes_along(P, add, 'icicle', 'body', 6, -10, 10, 26, -8, 10, 10, 'ice', rx=-0.9, w=3)
    add(P('head', (14, 14, 14), (-7, -4, 0), (0, 22, 8), rot=(-0.35, 0, 0), parent='body', style='skull', anim='head'))
    add(P('fur', (16, 6, 12), (-8, 6, -2), parent='head', style='yeti_fur'))
    add(P('jaw', (12, 6, 12), (-6, -10, 2), parent='head', style='skull', anim='jaw'))
    for k in range(6):
        add(P(f'tooth{k}', (1, 3, 1), (-5 + k * 2, -7, 13), parent='head', style='ice'))
    eyes(P, add, 'head', 3, 14.1, 'eye_ice', spread=6, w=3, h=2)
    for sx in (-1, 1):
        add(P('horn' + S(sx), (3, 12, 3), (-1.5, 0, -1.5), (sx * 6, 8, 4), rot=(-0.6, 0, -sx * 0.9), parent='head', style='black_ice'))
    a = arms2(P, add, 16, 40, (10, 22, 10), (9, 20, 9), 'yeti_fur', 'black_ice', reach=(-0.5, -0.5))
    for n in a:
        for k in range(4):
            add(P(f'{n}Claw{k}', (2, 9, 2), (-4 + k * 2.4, -48, 2), rot=(0.4, 0, 0), parent=n, style='black_ice'))
    return parts


def rime_knight(P):
    """A knight in armor of black ice: a tall narrow helm with no face, only two pale points of light; a frayed white cape; a
    greatsword of ice taller than it is; frost spikes on the pauldrons."""
    parts = []
    add = parts.append
    legs2(P, add, 4, 26, (6, 13, 6), (6, 13, 6), 'black_ice', 'black_ice')
    add(P('body', (14, 20, 8), (-7, 0, -4), (0, 26, 0), style='black_ice'))
    add(P('breast', (12, 10, 2), (-6, 8, 4), parent='body', style='ice_armor'))
    add(P('tasset', (16, 10, 10), (-8, -8, -5), parent='body', style='black_ice'))
    add(P('cape', (16, 34, 1), (-8, -32, -5), rot=(0.12, 0, 0), parent='body', style='veil', anim='flutter'))
    add(P('head', (8, 13, 8), (-4, 0, -4), (0, 20, 0), parent='body', style='black_ice', anim='head'))
    add(P('helmCrest', (2, 10, 10), (-1, 10, -5), parent='head', style='ice'))
    for sx in (-1, 1):
        add(P('point' + S(sx), (1, 1, 1), (sx * 1.6 - 0.5, 7, 4.1), parent='head', style='eye_ice'))
        add(P('pauldron' + S(sx), (8, 6, 10), (-4, 0, -5), (sx * 9, 44, 0), rot=(0, 0, -sx * 0.25), style='black_ice'))
        for k in range(3):
            add(P(f'frost{S(sx)}{k}', (2, 8 - k * 2, 2), (-1, 4, -1), (sx * 9, 44, -3 + k * 3), rot=(0, 0, -sx * (0.4 + k * 0.15)), style='ice'))
    a = arms2(P, add, 9, 42, (5, 12, 5), (5, 12, 5), 'black_ice', 'ice', reach=(-0.6, -0.3))
    add(P('sword', (3, 56, 1), (-1.5, -70, -0.5), parent=a[0], style='ice'))
    add(P('swordEdge', (1, 56, 2), (-0.5, -70, -1), parent=a[0], style='eye_ice'))
    add(P('crossguard', (12, 2, 3), (-6, -14, -1.5), parent=a[0], style='black_ice'))
    return parts


def the_mourner(P):
    """A veiled figure floating over the snow, weeping ice: a long hood with a void where the face should be and two streams of
    frozen tears, sleeves to the ground, fingers too long, a lantern of cold light."""
    parts = []
    add = parts.append
    add(P('body', (12, 16, 10), (-6, 0, -5), (0, 30, 0), style='veil'))
    add(P('robe', (16, 22, 14), (-8, -22, -7), parent='body', style='veil', anim='sway'))
    add(P('hem', (18, 10, 16), (-9, -32, -8), parent='body', style='shroud', anim='sway'))
    for k in range(6):
        add(P(f'tatter{k}', (3, 9, 1), (-9 + k * 3.4, -40, 7), parent='body', style='veil', anim='flutter'))
    add(P('hood', (12, 14, 12), (-6, 0, -6), (0, 15, 0), parent='body', style='veil', anim='head'))
    add(P('hoodPeak', (8, 6, 8), (-4, 12, -6), rot=(-0.4, 0, 0), parent='hood', style='veil'))
    add(P('face', (8, 9, 1), (-4, 2, 5.6), parent='hood', style='void'))
    for sx in (-1, 1):
        add(P('eye' + S(sx), (2, 1, 1), (sx * 2 - 1, 7, 6), parent='hood', style='eye_ice'))
        add(P('tear' + S(sx), (1, 10, 1), (sx * 2 - 0.5, -4, 6.2), parent='hood', style='ice'))
        s = 'sleeve' + S(sx)
        add(P(s, (6, 22, 6), (-3, -22, -3), (sx * 8, 14, 0), rot=(-0.9, 0, -sx * 0.3), parent='body', style='veil', anim='reachA' if sx < 0 else 'reachB'))
        for k in range(4):
            add(P(f'{s}Finger{k}', (1, 10, 1), (-2 + k * 1.3, -32, 0), parent=s, style='skull'))
    add(P('lantern', (5, 6, 5), (-2.5, -28, -2.5), (0, 0, 0), parent='sleeveR', style='eye_ice'))
    add(P('veilCrown', (14, 2, 14), (-7, 13, -7), parent='hood', style='ice'))
    for k in range(6):
        a = k * math.pi / 3
        add(P(f'icicle{k}', (1, 6, 1), (-0.5, -6, -0.5), (math.cos(a) * 6, 13, math.sin(a) * 6), parent='hood', style='ice'))
    return parts


# ============================================================================================== the Scarlet Sands
def dune_tyrant(P):
    """A scorpion of red glass and old bone: a segmented tail arching over its back to a barbed sting dripping amber, two great
    pincers, eight legs, a cluster of red eyes."""
    parts = []
    add = parts.append
    add(P('body', (20, 9, 26), (-10, -4, -13), (0, 14, 0), style='red_glass'))
    for k in range(4):
        add(P(f'plate{k}', (22, 3, 6), (-11, 5, 8 - k * 6.5), parent='body', style='bone'))
    add(P('head', (14, 8, 10), (-7, -4, 0), (0, 0, 13), parent='body', style='red_glass', anim='head'))
    for k, (x, y) in enumerate([(-4, 2), (4, 2), (-2, 3), (2, 3), (-6, 0), (6, 0)]):
        add(P(f'eye{k}', (2, 1, 1), (x - 1, y, 10), parent='head', style='eye_red'))
    prev, y, z = 'body', 4, -13
    for i in range(6):
        n = f'tail{i}'
        add(P(n, (7 - i * 0.5, 7, 7 - i * 0.5), (-(7 - i * 0.5) / 2, 0, -(7 - i * 0.5) / 2), (0, y, z), rot=(-0.35 if i == 0 else 0.42, 0, 0), parent=prev,
              style='red_glass' if i % 2 else 'bone', anim='sway' if i == 0 else 'none'))
        prev, y, z = n, 6, 0
    add(P('sting', (4, 8, 4), (-2, 6, -2), (0, 0, 0), rot=(0.9, 0, 0), parent=prev, style='bone'))
    add(P('venom', (2, 3, 2), (-1, 13, -1), (0, 0, 0), rot=(0.9, 0, 0), parent=prev, style='eye_amber'))
    for sx in (-1, 1):
        a = 'claw' + S(sx)
        add(P(a, (5, 5, 14), (-2.5, -2.5, 0), (sx * 9, -1, 12), rot=(0.1, -sx * 0.5, 0), parent='body', style='red_glass', anim='armA' if sx < 0 else 'armB'))
        add(P(a + 'Pincer', (10, 7, 12), (-5, -3.5, 13), parent=a, style='bone'))
        add(P(a + 'Finger', (4, 3, 10), (-2, -6.5, 15), parent=a, style='red_glass', anim='jaw'))
    for i in range(4):
        for sx in (-1, 1):
            n = f'leg{i}{S(sx)}'
            add(P(n, (12, 3, 3), (side_box(sx, 12), -1.5, -1.5), (sx * 9, -1, 7 - i * 5), rot=(0, sx * (0.4 - i * 0.3), -sx * -0.55), parent='body',
                  style='red_glass', anim='legA' if (i + (sx > 0)) % 2 else 'legB'))
            add(P(n + 'Low', (2, 14, 2), (-1, -14, -1), (sx * 11, 0, 0), rot=(0, 0, sx * 0.3), parent=n, style='bone'))
    return parts


def sand_pharaoh(P):
    """A pharaoh wrapped in gold and grave-cloth: a tall striped headdress, a gold death-mask with burning amber eyes, a
    broad collar, a crook and an hourglass of red sand, bandages trailing."""
    parts = []
    add = parts.append
    legs2(P, add, 4, 24, (6, 12, 6), (6, 12, 6), 'grave_cloth', 'pharaoh_gold')
    add(P('body', (14, 22, 8), (-7, 0, -4), (0, 24, 0), style='grave_cloth'))
    add(P('kilt', (16, 12, 10), (-8, -10, -5), parent='body', style='pharaoh_gold'))
    add(P('collar', (20, 6, 12), (-10, 16, -6), parent='body', style='pharaoh_blue'))
    add(P('collarGold', (22, 3, 13), (-11, 15, -6.5), parent='body', style='pharaoh_gold'))
    for k in range(4):
        add(P(f'wrap{k}', (2, 14, 1), (-6 + k * 4, -24, 5.2), parent='body', style='grave_cloth', anim='flutter'))
    add(P('head', (10, 11, 10), (-5, 0, -5), (0, 22, 0), parent='body', style='pharaoh_gold', anim='head'))
    add(P('nemes', (14, 14, 12), (-7, -3, -7), parent='head', style='pharaoh_blue'))
    for k in range(4):
        add(P(f'stripe{k}', (14.4, 1, 12.4), (-7.2, -2 + k * 3, -7.2), parent='head', style='pharaoh_gold'))
    add(P('lappetL', (3, 12, 3), (3, -12, 2), parent='head', style='pharaoh_blue'))
    add(P('lappetR', (3, 12, 3), (-6, -12, 2), parent='head', style='pharaoh_blue'))
    add(P('mask', (8, 8, 1), (-4, 1, 5), parent='head', style='pharaoh_gold'))
    eyes(P, add, 'head', 5, 5.6, 'eye_amber', spread=4, w=2, h=1)
    add(P('cobra', (2, 5, 2), (-1, 10, 4), parent='head', style='pharaoh_gold'))
    add(P('beardP', (2, 6, 2), (-1, -5, 4), parent='head', style='pharaoh_blue'))
    a = arms2(P, add, 9, 40, (5, 12, 5), (5, 12, 5), 'grave_cloth', 'pharaoh_gold', reach=(-0.9, -0.5))
    add(P('crook', (2, 30, 2), (-1, -40, -1), parent=a[1], style='pharaoh_gold'))
    add(P('crookHook', (6, 2, 2), (-1, -12, -1), parent=a[1], style='pharaoh_gold'))
    add(P('hourglass', (8, 12, 8), (-4, -36, -4), parent=a[0], style='pharaoh_gold'))
    add(P('sand', (6, 8, 6), (-3, -34, -3), parent=a[0], style='sand_glow'))
    return parts


def glass_djinn(P):
    """A spirit of molten glass: a broad red-glass torso with a furnace glowing through it, arms of flowing fire, a horned head
    of glass with white-hot eyes, and a whirling tail of flame instead of legs, glass shards orbiting."""
    parts = []
    add = parts.append
    add(P('body', (16, 18, 10), (-8, 0, -5), (0, 32, 0), style='red_glass'))
    add(P('furnace', (8, 8, 1), (-4, 6, 5), parent='body', style='sun_glow'))
    add(P('waist', (10, 8, 8), (-5, -8, -4), parent='body', style='flame', anim='sway'))
    add(P('tail', (8, 12, 8), (-4, -20, -4), parent='body', style='flame', anim='sway'))
    add(P('tailTip', (4, 10, 4), (-2, -30, -2), parent='body', style='glass_glow', anim='sway'))
    add(P('head', (10, 11, 10), (-5, 0, -5), (0, 18, 0), parent='body', style='red_glass', anim='head'))
    eyes(P, add, 'head', 5, 5.1, 'eye_amber', spread=4, w=3, h=1)
    add(P('mouth', (6, 2, 1), (-3, 1, 5.1), parent='head', style='sun_glow'))
    horns(P, add, 'head', 4, 8, 0, [(3, 7), (2, 6), (1, 5)], 'red_glass', 'gold_d', out=1.0)
    add(P('topknot', (4, 8, 4), (-2, 10, -4), rot=(-0.4, 0, 0), parent='head', style='flame'))
    a = arms2(P, add, 11, 48, (5, 14, 5), (5, 14, 5), 'red_glass', 'flame', reach=(-1.2, -0.6))
    for n in a:
        add(P(n + 'Fire', (7, 10, 7), (-3.5, -34, -3.5), parent=n, style='flame', anim='pulse'))
    for k in range(8):
        r = k * math.pi / 4
        add(P(f'shard{k}', (2, 4, 1), (-1, -2, -0.5), (math.cos(r) * 18, 6 + (k % 3) * 4, math.sin(r) * 18), rot=(0, r, 0.4), parent='body',
              style='glass_red', anim='spin'))
    return parts


# ============================================================================================== the Clockwork Rift
def pendulum_butcher(P):
    """An iron executioner: a barrel chest with a pendulum swinging inside a cage, a hood of riveted iron with one brass eye,
    two arms that end in great pendulum blades, gear-teeth along its back."""
    parts = []
    add = parts.append
    legs2(P, add, 6, 26, (9, 13, 9), (8, 13, 8), 'gear_iron', 'brass_d')
    add(P('body', (24, 24, 14), (-12, 0, -7), (0, 26, 0), style='gear_iron'))
    add(P('cage', (14, 14, 1), (-7, 4, 7), parent='body', style='void'))
    for k in range(4):
        add(P(f'cageBar{k}', (1, 14, 1), (-6 + k * 4, 4, 7.4), parent='body', style='brass_d'))
    add(P('pendulum', (1, 10, 1), (-0.5, -10, -0.5), (0, 17, 6), parent='body', style='brass_d', anim='sway'))
    add(P('bob', (4, 4, 1), (-2, -14, -0.5), (0, 17, 6), parent='body', style='rift_glow', anim='sway'))
    for k in range(5):
        add(P(f'gearTooth{k}', (3, 6, 3), (-1.5, 0, -1.5), (-10 + k * 5, 22, -6), rot=(-0.7, 0, 0), parent='body', style='brass_d'))
    add(P('head', (12, 12, 12), (-6, 0, -6), (0, 24, 1), parent='body', style='gear_iron', anim='head'))
    add(P('hoodPeak', (12, 6, 10), (-6, 9, -6), rot=(-0.3, 0, 0), parent='head', style='gear_iron'))
    add(P('eyeBrass', (4, 4, 1), (-2, 5, 6), parent='head', style='brass_d'))
    add(P('eyeCore', (2, 2, 1), (-1, 6, 6.5), parent='head', style='rift_glow'))
    for sx in (-1, 1):
        a = 'arm' + S(sx)
        add(P(a, (8, 20, 8), (-4, -20, -4), (sx * 16, 46, 0), rot=(-0.3, 0, -sx * 0.2), style='gear_iron', anim='armA' if sx < 0 else 'armB'))
        add(P(a + 'Rod', (2, 18, 2), (-1, -36, -1), parent=a, style='brass_d'))
        add(P(a + 'Blade', (20, 14, 2), (-10, -50, -1), parent=a, style='steel'))
        add(P(a + 'Edge', (22, 2, 1), (-11, -52, -0.5), parent=a, style='glow_w'))
        add(P('shoulderGear' + S(sx), (2, 12, 12), (-1, -6, -6), (sx * 16, 50, 0), rot=(0.785, 0, 0), style='brass_d', anim='spinS'))
    return parts


def gearwyrm(P):
    """A centipede of gears and pistons: a long chain of riveted segments each with a turning cog and a pair of piston legs,
    a head of iron mandibles with a cluster of violet lenses, sparks at the joints."""
    parts = []
    add = parts.append
    add(P('body', (14, 10, 12), (-7, -5, -6), (0, 10, 18), style='gear_iron'))
    add(P('head', (14, 10, 12), (-7, -4, 0), (0, 0, 6), parent='body', style='gear_iron', anim='head'))
    for k, (x, y) in enumerate([(-4, 2), (4, 2), (0, 3), (-2, 0), (2, 0)]):
        add(P(f'lens{k}', (2, 2, 1), (x - 1, y, 12), parent='head', style='eye_violet'))
    for sx in (-1, 1):
        add(P('mandible' + S(sx), (3, 3, 10), (-1.5, -2, 0), (sx * 5, -2, 11), rot=(0, -sx * 0.5, 0), parent='head', style='brass_d', anim='jaw'))
    prev = 'body'
    for i in range(7):
        n = f'seg{i}'
        add(P(n, (13 - i * 0.6, 9, 10), (-(13 - i * 0.6) / 2, -4.5, -10), (0, 0, -6 if i == 0 else -10), rot=(0, 0.1 * (1 if i % 2 else -1), 0),
              parent=prev, style='gear_iron', anim='undulate'))
        add(P(n + 'Cog', (2, 9, 9), (-1, -4.5, -4.5), (0, 6, -5), rot=(0.785, 0, 0), parent=n, style='brass_d', anim='spin'))
        for sx in (-1, 1):
            add(P(f'{n}Leg{S(sx)}', (2, 10, 2), (-1, -10, -1), (sx * 6, -2, -5), rot=(0, 0, -sx * 0.6), parent=n, style='steel',
                  anim='legA' if (i + (sx > 0)) % 2 else 'legB'))
        prev = n
    add(P('stinger', (4, 4, 10), (-2, -2, -10), (0, 0, -10), rot=(0.3, 0, 0), parent=prev, style='brass_d'))
    add(P('stingerGlow', (2, 2, 3), (-1, -1, -13), (0, 0, -10), rot=(0.3, 0, 0), parent=prev, style='rift_glow'))
    return parts


def hourless_oracle(P):
    """A floating seer: a great clock face for a body with too many hands, a hooded head of brass with a single violet lens,
    six thin arms ending in fingers like clock hands, and rings of numerals orbiting."""
    parts = []
    add = parts.append
    add(P('body', (20, 20, 4), (-10, -10, -2), (0, 30, 0), style='clockface'))
    add(P('rim', (22, 22, 3), (-11, -11, -2.5), parent='body', style='brass_d'))
    for k in range(5):
        add(P(f'hand{k}', (1, 9 - k, 1), (-0.5, 0, 2.2), rot=(0, 0, k * 1.25), parent='body', style='void', anim='spin' if k % 2 else 'spinR'))
    add(P('hub', (3, 3, 2), (-1.5, -1.5, 2), parent='body', style='rift_glow'))
    add(P('robe', (14, 16, 10), (-7, -26, -5), parent='body', style='robe_d', anim='sway'))
    add(P('head', (10, 10, 10), (-5, 0, -5), (0, 12, 0), parent='body', style='brass_d', anim='head'))
    add(P('hood', (12, 9, 12), (-6, 4, -6), parent='head', style='robe_d'))
    add(P('lens', (4, 4, 1), (-2, 3, 5), parent='head', style='eye_violet'))
    for i in range(3):
        for sx in (-1, 1):
            n = f'arm{i}{S(sx)}'
            add(P(n, (2, 14, 2), (-1, -14, -1), (sx * 10, 6 - i * 6, 0), rot=(-0.6 + i * 0.3, 0, -sx * (0.8 - i * 0.2)), parent='body',
                  style='brass_d', anim='reachA' if sx < 0 else 'reachB'))
            add(P(n + 'Finger', (1, 10, 1), (-0.5, -24, -0.5), parent=n, style='void'))
    for k in range(12):
        a = k * math.pi / 6
        add(P(f'numeral{k}', (2, 3, 1), (-1, -1.5, -0.5), (math.cos(a) * 18, math.sin(a) * 18, -4), parent='body', style='rift_glow', anim='spinS'))
    return parts


# ============================================================================================== the Mycelial Deep
def rot_behemoth(P):
    """A beast buried under its own fungal forest: a huge low body furred with mycelium, a forest of caps on its back, a blind
    face of folded flesh with a ring of pink eyes and a lamprey mouth, tusks of bone, legs like stumps."""
    parts = []
    add = parts.append
    add(P('body', (30, 20, 38), (-15, -10, -19), (0, 26, 0), style='myco_hide'))
    for k, (x, z, h, w, st) in enumerate([(-8, -8, 14, 12, 'cap_m'), (8, 4, 18, 14, 'cap'), (0, -16, 10, 10, 'cap_m'), (-10, 10, 8, 8, 'cap'),
                                          (10, -12, 12, 10, 'cap_m'), (2, 12, 6, 8, 'puff')]):
        add(P(f'stem{k}', (3, h, 3), (-1.5, 0, -1.5), (x, 10, z), parent='body', style='stem'))
        add(P(f'cap{k}', (w, 3, w), (-w / 2, h, -w / 2), (x, 10, z), parent='body', style=st))
        add(P(f'gill{k}', (w - 2, 1, w - 2), (-(w - 2) / 2, h - 0.6, -(w - 2) / 2), (x, 10, z), parent='body', style='bloom_glow'))
    add(P('head', (20, 16, 14), (-10, -8, 0), (0, -2, 19), parent='body', style='myco_hide', anim='head'))
    add(P('mouth', (8, 8, 1), (-4, -6, 14), parent='head', style='void'))
    for k in range(8):
        a = k * math.pi / 4
        add(P(f'tooth{k}', (1, 2, 1), (math.cos(a) * 3 - 0.5, -2 + math.sin(a) * 3 - 1, 14.4), parent='head', style='bone'))
    for k in range(6):
        a = math.pi * 0.15 + k * math.pi * 0.14
        add(P(f'eye{k}', (2, 2, 1), (math.cos(a) * 8 - 1, math.sin(a) * 5 + 1, 14), parent='head', style='eye_pink'))
    for sx in (-1, 1):
        add(P('tusk' + S(sx), (3, 3, 12), (-1.5, -1.5, 0), (sx * 7, -6, 12), rot=(-0.3, -sx * 0.3, 0), parent='head', style='bone'))
    for i, (x, z) in enumerate([(-11, 13), (11, 13), (-11, -13), (11, -13)]):
        n = f'leg{i}'
        add(P(n, (10, 16, 10), (-5, -16, -5), (x, -6, z), parent='body', style='myco_hide', anim='legA' if i in (0, 3) else 'legB'))
        add(P(n + 'Root', (12, 3, 12), (-6, -20, -6), parent=n, style='root_c'))
    return parts


def pale_gardener(P):
    """A tall, thin thing of white stalk: legs like stilts, a narrow body of pale fungus with a pink glow in its ribs, a long head
    under a drooping cap with a slit of light, and two arms ending in long scythe blades."""
    parts = []
    add = parts.append
    legs2(P, add, 4, 40, (4, 20, 4), (4, 20, 4), 'pale_stalk', 'root_c', claw='root_c')
    add(P('body', (10, 24, 6), (-5, 0, -3), (0, 40, 0), rot=(0.15, 0, 0), style='pale_stalk'))
    for k in range(4):
        add(P(f'rib{k}', (10, 1, 1), (-5, 6 + k * 4, 3.2), parent='body', style='bone_d'))
    add(P('glow', (6, 12, 1), (-3, 6, 3), parent='body', style='bloom_glow'))
    add(P('head', (8, 16, 8), (-4, 0, -4), (0, 24, 0), parent='body', style='pale_stalk', anim='head'))
    add(P('slit', (4, 1, 1), (-2, 9, 4.1), parent='head', style='eye_pink'))
    add(P('cap', (18, 3, 18), (-9, 14, -9), parent='head', style='cap_pale'))
    add(P('capDroop', (16, 6, 16), (-8, 9, -8), parent='head', style='cap_pale'))
    for k in range(8):
        a = k * math.pi / 4
        add(P(f'drip{k}', (1, 8, 1), (-0.5, -8, -0.5), (math.cos(a) * 8, 10, math.sin(a) * 8), parent='head', style='bloom_glow', anim='sway'))
    for sx in (-1, 1):
        a = 'arm' + S(sx)
        add(P(a, (3, 22, 3), (-1.5, -22, -1.5), (sx * 7, 62, 0), rot=(-0.6, 0, -sx * 0.3), style='pale_stalk', anim='armA' if sx < 0 else 'armB'))
        add(P(a + 'Fore', (3, 18, 3), (-1.5, -39, -1.5), parent=a, style='pale_stalk'))
        add(P(a + 'Scythe', (2, 4, 26), (-1, -42, 0), rot=(0.2, 0, 0), parent=a, style='bone'))
        add(P(a + 'Edge', (1, 2, 24), (-0.5, -44, 1), rot=(0.2, 0, 0), parent=a, style='eye_pink'))
    return parts


def lumen_horror(P):
    """A drifting jellyfish-cap of glowing flesh: a huge pulsing bell with a ring of eyes, a frill of gills, and a curtain of
    long trailing threads, two of them ending in barbed hooks."""
    parts = []
    add = parts.append
    add(P('body', (28, 16, 28), (-14, 0, -14), (0, 40, 0), style='lumen', anim='pulse'))
    add(P('top', (20, 8, 20), (-10, 16, -10), parent='body', style='lumen'))
    add(P('crown', (10, 6, 10), (-5, 24, -5), parent='body', style='cap_m'))
    add(P('frill', (32, 2, 32), (-16, -1, -16), parent='body', style='bloom_glow', anim='spinS'))
    for k in range(8):
        a = k * math.pi / 4
        add(P(f'eye{k}', (3, 3, 1), (math.cos(a) * 14 - 1.5, 6, math.sin(a) * 14 - 0.5), rot=(0, -a + math.pi / 2, 0), parent='body', style='eye_pink'))
    add(P('core', (8, 8, 8), (-4, -6, -4), parent='body', style='puff_glow', anim='pulse'))
    for k in range(10):
        a = k * math.pi / 5
        ln = 26 + (k % 3) * 8
        n = f'thread{k}'
        add(P(n, (1, ln, 1), (-0.5, -ln, -0.5), (math.cos(a) * 10, -1, math.sin(a) * 10), rot=(0.1 * math.sin(a), 0, 0.1 * math.cos(a)), parent='body',
              style='lumen' if k % 2 else 'bloom_glow', anim='sway'))
    for sx in (-1, 1):
        n = 'hookArm' + S(sx)
        add(P(n, (2, 34, 2), (-1, -34, -1), (sx * 6, -1, 4), parent='body', style='myco_hide', anim='reachA' if sx < 0 else 'reachB'))
        add(P(n + 'Hook', (2, 6, 6), (-1, -40, -3), parent=n, style='bone'))
    return parts


# ============================================================================================== the Last Realm
def herald_of_ruin(P):
    """The Unmaker's sword arm made flesh: a giant of bone-white plate split open over black void, a crown of shards, eight
    realm stones set in its breastplate, a greatsword of white and black longer than it is tall."""
    parts = []
    add = parts.append
    legs2(P, add, 7, 30, (10, 15, 10), (10, 15, 10), 'unmade_w', 'unmade_b')
    add(P('pelvis', (22, 8, 14), (-11, 0, -7), (0, 30, 0), style='unmade_b'))
    add(P('body', (28, 26, 16), (-14, 0, -8), (0, 36, 0), style='unmade_w'))
    add(P('rift', (6, 20, 1), (-3, 3, 8), parent='body', style='void_plate'))
    add(P('riftGlow', (2, 18, 1), (-1, 4, 8.4), parent='body', style='accretion2'))
    for k, st in enumerate(['shard_g', 'shard_c', 'shard_v', 'shard_t', 'shard_i', 'shard_r', 'shard_y', 'shard_m']):
        add(P(f'stone{k}', (2, 2, 1), (-11 + (k % 4) * 2 + (12 if k >= 4 else 0) - (0 if k >= 4 else 0), 16 + (k % 2) * 3, 8.2), parent='body', style=st))
    add(P('head', (14, 14, 12), (-7, 0, -6), (0, 28, 1), parent='body', style='unmade_w', anim='head'))
    add(P('faceVoid', (10, 6, 1), (-5, 3, 6), parent='head', style='void_plate'))
    eyes(P, add, 'head', 5, 6.4, 'eye_violet', spread=5, w=2, h=1)
    for k in range(7):
        a = -1.2 + k * 0.4
        add(P(f'crown{k}', (2, 10 - abs(k - 3) * 1.5, 2), (-1, 0, -1), (math.sin(a) * 7, 13, math.cos(a) * 6 - 1), rot=(0.25 * math.cos(a), 0, -a * 0.4),
              parent='head', style='shard_i' if k == 3 else 'unmade_w2'))
    for sx in (-1, 1):
        add(P('pauldron' + S(sx), (16, 8, 16), (-8, 0, -8), (sx * 18, 58, 0), rot=(0, 0, -sx * 0.3), style='unmade_w'))
        add(P('pauldronB' + S(sx), (12, 4, 12), (-6, 7, -6), (sx * 18, 58, 0), rot=(0, 0, -sx * 0.4), style='unmade_b'))
        for k in range(3):
            add(P(f'pSpike{S(sx)}{k}', (2, 10 - k * 2, 2), (-1, 8, -1), (sx * 18, 58, -4 + k * 4), rot=(0, 0, -sx * (0.5 + k * 0.15)), style='unmade_b'))
    a = arms2(P, add, 19, 56, (10, 20, 10), (10, 18, 10), 'unmade_w', 'unmade_b', reach=(-0.8, -0.3))
    add(P('blade', (5, 70, 2), (-2.5, -100, -1), parent=a[0], style='unmade_w'))
    add(P('bladeEdge', (1, 70, 3), (-0.5, -100, -1.5), parent=a[0], style='void_plate'))
    add(P('bladeGlow', (1, 60, 1), (-0.5, -94, 1.2), parent=a[0], style='accretion2'))
    add(P('guard', (16, 3, 4), (-8, -32, -2), parent=a[0], style='gold_d'))
    return parts


def herald_of_silence(P):
    """A great eye wrapped in rings of broken worlds: a white sclera with a black hole for a pupil, lids of bone plate, three
    tilted rings of shards circling, and tendrils of void hanging beneath."""
    parts = []
    add = parts.append
    add(P('body', (24, 24, 24), (-12, -12, -12), (0, 30, 0), style='eye_white'))
    add(P('iris', (14, 14, 1), (-7, -7, 12), parent='body', style='accretion'))
    add(P('pupil', (8, 8, 1), (-4, -4, 12.4), parent='body', style='abyss'))
    add(P('lidTop', (26, 8, 26), (-13, 8, -13), parent='body', style='unmade_w'))
    add(P('lidBot', (26, 6, 26), (-13, -14, -13), parent='body', style='unmade_w'))
    for k in range(6):
        a = k * math.pi / 3
        add(P(f'lash{k}', (2, 8, 2), (-1, 0, -1), (math.cos(a) * 11, 14, math.sin(a) * 11), rot=(math.sin(a) * 0.6, 0, -math.cos(a) * 0.6), parent='body', style='unmade_b'))
    for r, (tilt, n, st) in enumerate([(0.4, 14, 'unmade_w2'), (-0.5, 12, 'void_plate'), (1.2, 10, 'shard_i')]):
        ring = f'ring{r}'
        add(P(ring, (1, 1, 1), (-0.5, -0.5, -0.5), (0, 0, 0), rot=(tilt, 0, 0.3 * r), parent='body', style='void', anim='spin' if r % 2 == 0 else 'spinR'))
        for k in range(n):
            a = k * 2 * math.pi / n
            add(P(f'{ring}s{k}', (3, 2, 3), (-1.5, -1, -1.5), (math.cos(a) * (20 + r * 4), 0, math.sin(a) * (20 + r * 4)), parent=ring, style=st))
    for k in range(7):
        a = k * 2 * math.pi / 7
        add(P(f'tendril{k}', (2, 20 + (k % 3) * 6, 2), (-1, -26 - (k % 3) * 6, -1), (math.cos(a) * 7, -10, math.sin(a) * 7), parent='body',
              style='void_plate', anim='sway'))
    return parts


MOBS = {lt_id: dict(parts=fn, seed=8000 + i, shadow=1.0) for i, (lt_id, fn) in enumerate([
    ('thornmaw', thornmaw), ('hollowbark', hollowbark), ('rot_matron', rot_matron),
    ('galeclaw', galeclaw), ('thunder_colossus', thunder_colossus), ('squall_seraph', squall_seraph),
    ('cinderjaw', cinderjaw), ('chainwarden', chainwarden), ('ashen_choir', ashen_choir),
    ('reef_crusher', reef_crusher), ('drowned_admiral', drowned_admiral), ('abyssal_siren', abyssal_siren),
    ('frostmaw', frostmaw), ('rime_knight', rime_knight), ('the_mourner', the_mourner),
    ('dune_tyrant', dune_tyrant), ('sand_pharaoh', sand_pharaoh), ('glass_djinn', glass_djinn),
    ('pendulum_butcher', pendulum_butcher), ('gearwyrm', gearwyrm), ('hourless_oracle', hourless_oracle),
    ('rot_behemoth', rot_behemoth), ('pale_gardener', pale_gardener), ('lumen_horror', lumen_horror),
    ('herald_of_ruin', herald_of_ruin), ('herald_of_silence', herald_of_silence)])}


def _height(parts):
    """The model's height in units: the lowest and highest corners of every part, following parents and rotations."""
    import numpy as np
    import render_models as rm
    fr = rm.world_frames(parts)
    lo, hi = 1e9, -1e9
    for p in parts:
        R, t = fr[p['name']]
        x0, y0, z0 = p['origin']
        w, h, d = p['size']
        for cx in (x0, x0 + w):
            for cy in (y0, y0 + h):
                for cz in (z0, z0 + d):
                    y = (t + R @ np.array([cx, cy, cz]))[1]
                    lo, hi = min(lo, y), max(hi, y)
    return lo, hi


def register(mobs, styles, glow_styles, part):
    styles.update(STYLES)
    glow_styles.update(GLOW)
    import mobspecs
    from lieutenants import BY_ID
    for key, m in MOBS.items():
        def build(f=m['parts'], key=key):
            raw = f(part)
            lo, hi = _height(raw)
            k = BY_ID[key]['size'][1] * 16 / max(1.0, hi - min(0.0, lo))
            k = max(0.6, min(3.0, k))
            out = mobspecs.scaled(raw, k)
            if lo < 0:                                    # flyers trail below their own feet: lift them so the lowest point is the ground
                out = mobspecs.shifted(out, -lo * k)
            return out
        mobs[key] = dict(parts=build, seed=m['seed'], shadow=BY_ID[key]['size'][0] * 0.5)
