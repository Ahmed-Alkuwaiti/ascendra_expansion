"""Realm wildlife: one passive creature for each realm, built with the same box-model conventions as the bosses
(units of 1/16 block, y up, front toward +z)."""
import math

from mobs_act2 import side_box, side_name

STYLES = {
    'shell_moss': dict(base=(74, 104, 44), var=10, patches=[((110, 150, 60), 14, (1, 3)), ((50, 70, 30), 12, (1, 2))], dots=((230, 210, 90), 6, (1, 1))),
    'skin_green': dict(base=(120, 140, 90), var=8, patches=[((96, 116, 70), 12, (1, 2))]),
    'ray_top': dict(base=(206, 226, 240), var=7, patches=[((170, 200, 230), 12, (1, 3)), ((240, 250, 255), 10, (1, 2))]),
    'ray_belly': dict(base=(240, 246, 250), var=5, patches=[]),
    'beetle': dict(base=(24, 20, 22), var=5, patches=[((44, 36, 36), 12, (1, 2))], cracks=(255, 130, 40)),
    'ember_glow': dict(base=(255, 140, 40), var=14, patches=[((255, 220, 120), 12, (1, 2))]),
    'jelly': dict(base=(90, 210, 200), var=12, patches=[((170, 250, 240), 12, (1, 2)), ((40, 150, 160), 10, (1, 2))]),
    'jelly_core': dict(base=(220, 255, 250), var=6, patches=[((140, 255, 230), 8, (1, 1))]),
    'hare': dict(base=(238, 242, 246), var=6, patches=[((214, 222, 232), 12, (1, 3))]),
    'hare_pink': dict(base=(220, 170, 180), var=6, patches=[]),
    'skink': dict(base=(196, 70, 40), var=10, patches=[((230, 120, 50), 14, (1, 2)), ((130, 40, 26), 12, (1, 2))]),
    'skink_belly': dict(base=(240, 190, 120), var=8, patches=[]),
    'cog_brass': dict(base=(196, 150, 70), var=10, patches=[((230, 190, 100), 12, (1, 2)), ((130, 96, 40), 10, (1, 2))]),
    'puff': dict(base=(200, 70, 190), var=10, patches=[((230, 120, 220), 12, (1, 3))], dots=((255, 220, 250), 14, (1, 2))),
    'puff_glow': dict(base=(255, 120, 235), var=12, patches=[((255, 220, 250), 10, (1, 1))]),
    'eye_dark': dict(base=(16, 14, 20), var=2, patches=[]),
}
GLOW = {'ember_glow', 'jelly', 'jelly_core', 'puff_glow'}


def mossling(P):
    """A small tortoise with a garden on its back: moss, a fern, a red mushroom and a flower."""
    parts = []
    add = parts.append
    add(P('body', (10, 4, 12), (-5, 0, -6), (0, 3, 0), style='skin_green'))
    add(P('shell', (12, 5, 14), (-6, 3, -7), parent='body', style='shell_moss'))
    add(P('shellTop', (9, 2, 10), (-4.5, 8, -5), parent='body', style='shell_moss'))
    add(P('fern', (1, 4, 3), (-3, 10, -2), parent='body', style='moss_l'))
    add(P('shroomStem', (1, 2, 1), (2, 10, 1), parent='body', style='root_c'))
    add(P('shroomCap', (3, 1, 3), (1, 12, 0), parent='body', style='cap'))
    add(P('flower', (1, 1, 1), (0, 10, -4), parent='body', style='glow_y'))
    add(P('head', (5, 4, 5), (-2.5, -1, 0), (0, 4, 6), parent='body', style='skin_green', anim='head', eyes=(20, 20, 20)))
    add(P('tail', (2, 2, 3), (-1, 0, -3), (0, 2, -6), parent='body', style='skin_green'))
    for i, (x, z) in enumerate([(-4, 4), (4, 4), (-4, -4), (4, -4)]):
        add(P(f'leg{i}', (3, 3, 3), (-1.5, -3, -1.5), (x, 0, z), parent='body', style='skin_green', anim='legA' if i in (0, 3) else 'legB'))
    return parts


def cloud_ray(P):
    """A pale sky manta: a broad flat body, wide flapping wings, cephalic fins and a long whip tail."""
    parts = []
    add = parts.append
    add(P('body', (10, 3, 14), (-5, -1.5, -7), (0, 10, 0), style='ray_top'))
    add(P('belly', (8, 1, 12), (-4, -2.5, -6), parent='body', style='ray_belly'))
    for sx in (-1, 1):
        nm = side_name(sx)
        add(P('wing' + nm, (14, 1, 12), (side_box(sx, 14), -0.5, -6), (sx * 5, 0, 0), parent='body', style='ray_top',
              anim='wingL' if sx < 0 else 'wingR'))
        add(P('tip' + nm, (6, 1, 6), (side_box(sx, 6), -0.5, -3), (sx * 14, 0, -2), parent='wing' + nm, style='ray_top'))
        add(P('fin' + nm, (2, 1, 4), (-1, -0.5, 0), (sx * 3, 0, 7), rot=(0, sx * 0.3, 0), parent='body', style='ray_belly'))
        add(P('eye' + nm, (1, 1, 1), (-0.5, 0, 0), (sx * 3.5, 1.2, 5), parent='body', style='glow_w'))
    add(P('tail', (1, 1, 14), (-0.5, -0.5, -14), (0, 0, -7), parent='body', style='ray_top', anim='sway'))
    add(P('tailTip', (1, 1, 8), (-0.5, -0.5, -8), (0, 0, -14), parent='tail', style='feather_w'))
    return parts


def ember_beetle(P):
    """A black beetle split by glowing cracks, a curved horn, wing-cases that glow underneath, six legs."""
    parts = []
    add = parts.append
    add(P('body', (8, 4, 10), (-4, 0, -5), (0, 2, 0), style='beetle'))
    add(P('elytraL', (4, 2, 10), (-4.2, 3.5, -5.2), rot=(0, 0, 0.12), parent='body', style='beetle'))
    add(P('elytraR', (4, 2, 10), (0.2, 3.5, -5.2), rot=(0, 0, -0.12), parent='body', style='beetle'))
    add(P('seam', (1, 1, 10), (-0.5, 5, -5), parent='body', style='ember_glow'))
    add(P('glowBelly', (6, 1, 8), (-3, -0.5, -4), parent='body', style='ember_glow', anim='pulse'))
    add(P('head', (5, 3, 3), (-2.5, 0, 0), (0, 1, 5), parent='body', style='beetle', anim='head', eyes=(255, 150, 40)))
    add(P('horn', (1, 4, 1), (-0.5, 2, 1), rot=(-0.4, 0, 0), parent='head', style='beetle'))
    add(P('hornTip', (1, 1, 1), (-0.5, 5.5, 2.5), parent='head', style='ember_glow'))
    for sx in (-1, 1):
        for k in range(3):
            add(P(f'leg{side_name(sx)}{k}', (5, 1, 1), (side_box(sx, 5), -0.5, -0.5), (sx * 4, 1, 3 - k * 3),
                  rot=(0, 0, -sx * 0.6), parent='body', style='beetle', anim='legA' if (k + (sx > 0)) % 2 else 'legB'))
    return parts


def lantern_jelly(P):
    """A drifting jellyfish: a glowing bell, a brighter core, frilled lips and long trailing tentacles."""
    parts = []
    add = parts.append
    add(P('bell', (10, 6, 10), (-5, 0, -5), (0, 10, 0), style='jelly', anim='pulse'))
    add(P('bellTop', (7, 2, 7), (-3.5, 6, -3.5), parent='bell', style='jelly'))
    add(P('core', (4, 4, 4), (-2, 1, -2), parent='bell', style='jelly_core'))
    add(P('lip', (12, 1, 12), (-6, -0.5, -6), parent='bell', style='jelly'))
    for i in range(8):
        a = i * math.pi / 4
        ln = 10 + (i % 3) * 3
        add(P(f'tentacle{i}', (1, ln, 1), (-0.5, -ln, -0.5), (4 * math.cos(a), 0, 4 * math.sin(a)), parent='bell', style='jelly', anim='flutter'))
    for i in range(4):
        a = i * math.pi / 2 + 0.4
        add(P(f'arm{i}', (2, 8, 2), (-1, -8, -1), (1.5 * math.cos(a), 0, 1.5 * math.sin(a)), parent='bell', style='jelly_core', anim='sway'))
    return parts


def frost_hare(P):
    """A snow-white hare: long ears with pink insides, a fluffy tail, strong back legs."""
    parts = []
    add = parts.append
    add(P('body', (6, 6, 9), (-3, 0, -4.5), (0, 3, 0), rot=(-0.15, 0, 0), style='hare'))
    add(P('head', (5, 5, 5), (-2.5, 0, 0), (0, 5, 4), parent='body', style='hare', anim='head', eyes=(30, 40, 70)))
    add(P('nose', (1, 1, 1), (-0.5, 1.5, 4.8), parent='head', style='hare_pink'))
    for sx in (-1, 1):
        nm = side_name(sx)
        add(P('ear' + nm, (2, 7, 1), (-1, 0, -0.5), (sx * 1.5, 5, 1), rot=(-0.2, 0, sx * 0.15), parent='head', style='hare'))
        add(P('earIn' + nm, (1, 5, 1), (-0.5, 1, 0.1), parent='ear' + nm, style='hare_pink'))
        add(P('front' + nm, (2, 4, 2), (-1, -4, -1), (sx * 2, 1, 3), parent='body', style='hare', anim='legA' if sx < 0 else 'legB'))
        add(P('back' + nm, (2, 4, 6), (-1, -3, -3), (sx * 2.5, 1, -2.5), parent='body', style='hare', anim='legB' if sx < 0 else 'legA'))
    add(P('tail', (3, 3, 3), (-1.5, 0, -2), (0, 3, -4.5), parent='body', style='hare'))
    return parts


def sand_skink(P):
    """A red desert lizard, long and low: a pale belly, splayed legs and a tail that swings as it runs."""
    parts = []
    add = parts.append
    add(P('body', (6, 3, 12), (-3, 0, -6), (0, 2, 0), style='skink'))
    add(P('belly', (5, 1, 11), (-2.5, -0.5, -5.5), parent='body', style='skink_belly'))
    add(P('head', (5, 3, 6), (-2.5, 0, 0), (0, 0.5, 6), parent='body', style='skink', anim='head', eyes=(20, 20, 20)))
    add(P('frill', (7, 3, 1), (-3.5, 1, 0), parent='head', style='sand_glow'))
    prev = 'body'
    z = -6
    for k in range(4):
        w = 4 - k
        nm = f'tail{k}'
        add(P(nm, (w, 2, 5), (-w / 2, 0, -5), (0, 0.5 if k == 0 else 0, z), parent=prev, style='skink', anim='undulate'))
        prev, z = nm, -5
    for sx in (-1, 1):
        for k, zz in enumerate((4, -3)):
            add(P(f'leg{side_name(sx)}{k}', (4, 1.5, 1.5), (side_box(sx, 4), -0.75, -0.75), (sx * 3, 1, zz), rot=(0, 0, -sx * 0.5),
                  parent='body', style='skink', anim='legA' if (k + (sx > 0)) % 2 else 'legB'))
    return parts


def cogling(P):
    """A brass clockwork beetle: a round shell with a turning cog, a clock-face front, four jointed legs, a ticking antenna."""
    parts = []
    add = parts.append
    add(P('body', (8, 5, 9), (-4, 0, -4.5), (0, 3, 0), style='cog_brass'))
    add(P('face', (6, 4, 1), (-3, 0.5, 4.4), parent='body', style='clockface', eyes=(170, 70, 255)))
    add(P('gear', (7, 1, 7), (-3.5, 0, -3.5), (0, 5, -0.5), parent='body', style='brass_d', anim='spin'))
    for k in range(6):
        a = k * math.pi / 3
        add(P(f'tooth{k}', (2, 1, 2), (-1, 0, -1), (4 * math.cos(a), 0, 4 * math.sin(a)), parent='gear', style='brass_d'))
    add(P('hub', (2, 2, 2), (-1, 0.5, -1), parent='gear', style='rift_glow'))
    add(P('antenna', (1, 4, 1), (-0.5, 0, -0.5), (0, 5, 3.5), rot=(0.4, 0, 0), parent='body', style='iron_dk', anim='sway'))
    add(P('bulb', (1, 1, 1), (-0.5, 4, -0.5), parent='antenna', style='gold_glow'))
    for sx in (-1, 1):
        for k, zz in enumerate((2.5, -2.5)):
            leg = f'leg{side_name(sx)}{k}'
            add(P(leg, (4, 1, 1), (side_box(sx, 4), -0.5, -0.5), (sx * 4, 1.5, zz), rot=(0, 0, -sx * 0.5), parent='body', style='iron_dk',
                  anim='legA' if (k + (sx > 0)) % 2 else 'legB'))
            add(P(leg + 'Foot', (1, 3, 1), (-0.5, -3, -0.5), (sx * 4, 0, 0), parent=leg, style='cog_brass'))
    return parts


def spore_puff(P):
    """A floating puffball: a round spotted cap, a ring of glowing pores, two sleepy eyes and dangling root-threads."""
    parts = []
    add = parts.append
    add(P('puff', (10, 9, 10), (-5, 0, -5), (0, 10, 0), style='puff', anim='pulse'))
    add(P('puffX', (12, 6, 8), (-6, 1.5, -4), parent='puff', style='puff'))
    add(P('puffZ', (8, 6, 12), (-4, 1.5, -6), parent='puff', style='puff'))
    add(P('crown', (6, 2, 6), (-3, 9, -3), parent='puff', style='puff'))
    for i in range(6):
        a = i * math.pi / 3
        add(P(f'pore{i}', (2, 1, 2), (-1, 9.5, -1), (3 * math.cos(a), 0, 3 * math.sin(a)), parent='puff', style='puff_glow'))
    for sx in (-1, 1):
        add(P('eye' + side_name(sx), (2, 1, 1), (-1, 0, 0), (sx * 2, 4, 5.1), parent='puff', style='eye_dark'))
    for i in range(5):
        a = i * 2 * math.pi / 5
        ln = 5 + (i % 2) * 3
        add(P(f'thread{i}', (1, ln, 1), (-0.5, -ln, -0.5), (3 * math.cos(a), 0, 3 * math.sin(a)), parent='puff', style='root_c', anim='flutter'))
    return parts


MOBS = {
    'mossling': dict(parts=mossling, seed=71, shadow=0.5),
    'cloud_ray': dict(parts=cloud_ray, seed=72, shadow=0.9, scale=1.7),
    'ember_beetle': dict(parts=ember_beetle, seed=73, shadow=0.4),
    'lantern_jelly': dict(parts=lantern_jelly, seed=74, shadow=0.0),
    'frost_hare': dict(parts=frost_hare, seed=75, shadow=0.3),
    'sand_skink': dict(parts=sand_skink, seed=76, shadow=0.4),
    'cogling': dict(parts=cogling, seed=77, shadow=0.4),
    'spore_puff': dict(parts=spore_puff, seed=78, shadow=0.3),
}


def register(mobs, styles, glow_styles, part):
    styles.update(STYLES)
    glow_styles.update(GLOW)
    for key, m in MOBS.items():
        k = m.get('scale', 1.0)
        mobs[key] = dict(parts=(lambda f=m['parts'], k=k: f(part) if k == 1.0 else __import__('mobspecs').scaled(f(part), k)),
                         seed=m['seed'], shadow=m['shadow'])
