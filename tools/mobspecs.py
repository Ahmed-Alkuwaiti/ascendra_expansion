"""Box-model specs for every custom mob and boss.

One spec drives three things: (1) the painted texture, (2) the preview renders, (3) generated Java (MobModels.java).
Coordinates: units of 1/16 block, y up from the ground, front toward +z. Sizes are integers.
anim tags: head, legA, legB, armA, armB, wingL, wingR, spin, none
"""
import math
import os
import random

from PIL import Image, ImageDraw

ASSETS = __import__('paths').RES + '/assets/aurelia'


def part(name, size, origin, pivot=(0, 0, 0), rot=(0, 0, 0), style='bark', anim='none', eyes=None, parent=None):
    """A box. With a parent, pivot is relative to the parent's pivot (in the parent's rotated frame)."""
    return dict(name=name, size=tuple(max(1, int(round(s))) for s in size), origin=tuple(origin), pivot=tuple(pivot),
                rot=tuple(rot), style=style, anim=anim, eyes=eyes, parent=parent)


def scaled(parts, k, prefix=''):
    out = []
    for p in parts:
        q = dict(p)
        q['name'] = prefix + p['name']
        q['parent'] = (prefix + p['parent']) if p.get('parent') else None
        q['size'] = tuple(max(1, int(round(s * k))) for s in p['size'])
        q['origin'] = tuple(o * k for o in p['origin'])
        q['pivot'] = tuple(v * k for v in p['pivot'])
        out.append(q)
    return out


def shifted(parts, dy):
    out = []
    for p in parts:
        q = dict(p)
        if not p.get('parent'):
            q['pivot'] = (p['pivot'][0], p['pivot'][1] + dy, p['pivot'][2])
        out.append(q)
    return out


# ------------------------------------------------------------------ texture styles
STYLES = {
    'bark': dict(base=(88, 62, 38), var=14, patches=[((70, 120, 44), 22, (2, 5)), ((52, 40, 26), 14, (1, 3))]),
    'moss': dict(base=(84, 128, 44), var=14, patches=[((120, 170, 60), 16, (1, 3)), ((60, 96, 34), 12, (2, 4))]),
    'cap': dict(base=(200, 48, 46), var=10, patches=[], dots=((238, 228, 208), 16, (1, 3))),
    'stem': dict(base=(214, 204, 184), var=8, patches=[((190, 178, 156), 14, (1, 3))]),
    'glowg': dict(base=(150, 255, 90), var=10, patches=[((230, 255, 170), 6, (1, 2))]),
    'fur_moss': dict(base=(84, 92, 60), var=12, patches=[((90, 140, 50), 20, (2, 4)), ((70, 52, 36), 14, (1, 3))]),
    'quartz': dict(base=(236, 230, 224), var=8, patches=[((205, 200, 196), 18, (1, 3))]),
    'armor_q': dict(base=(226, 228, 232), var=8, patches=[((190, 198, 210), 20, (2, 4)), ((100, 200, 235), 8, (1, 2))]),
    'trim_blue': dict(base=(58, 110, 190), var=10, patches=[((100, 160, 230), 10, (1, 2))]),
    'gold': dict(base=(226, 180, 64), var=12, patches=[((250, 220, 120), 8, (1, 2))]),
    'wood': dict(base=(120, 86, 50), var=8, patches=[((90, 62, 34), 10, (1, 2))]),
    'cyan_core': dict(base=(90, 225, 255), var=10, patches=[((225, 255, 255), 8, (1, 2))]),
    'plate': dict(base=(222, 224, 220), var=6, patches=[((196, 110, 60), 12, (1, 2)), ((170, 176, 186), 12, (1, 3))]),
    'navy': dict(base=(28, 40, 86), var=8, patches=[((60, 80, 140), 22, (1, 3)), ((90, 200, 255), 6, (1, 1))]),
    'feather_w': dict(base=(240, 244, 250), var=6, patches=[((200, 214, 235), 20, (1, 3))]),
    'ash_armor': dict(base=(42, 38, 44), var=7, patches=[((66, 60, 68), 22, (2, 4))], cracks=(255, 120, 30)),
    'ash_fur': dict(base=(48, 42, 46), var=7, patches=[((70, 62, 68), 18, (2, 4))], cracks=(255, 110, 28)),
    'flame': dict(base=(255, 140, 40), var=18, patches=[((255, 224, 96), 14, (1, 2))]),
    'cape': dict(base=(140, 24, 30), var=10, patches=[((100, 14, 20), 16, (1, 3))]),
    'soul_robe': dict(base=(30, 36, 46), var=6, patches=[((52, 74, 90), 18, (2, 4))]),
    'hood': dict(base=(20, 24, 32), var=5, patches=[((40, 56, 70), 10, (1, 3))]),
    'soul_light': dict(base=(90, 230, 255), var=12, patches=[((225, 255, 255), 8, (1, 2))]),
    'blade': dict(base=(62, 58, 66), var=6, patches=[], cracks=(255, 120, 30)),
    'king_armor': dict(base=(38, 34, 42), var=7, patches=[((64, 58, 68), 24, (2, 5))], cracks=(255, 110, 28)),
    'rune_cyan': dict(base=(70, 220, 255), var=10, patches=[((220, 255, 255), 8, (1, 2))]),
    'bark_d': dict(base=(58, 42, 26), var=10, patches=[((80, 110, 44), 14, (1, 3)), ((40, 30, 20), 12, (1, 3))]),
    'moss_l': dict(base=(128, 178, 70), var=14, patches=[((170, 215, 100), 14, (1, 3)), ((88, 132, 50), 12, (1, 3))]),
    'cap_brown': dict(base=(150, 100, 60), var=10, patches=[], dots=((232, 214, 190), 14, (1, 3))),
    'cap_orange': dict(base=(214, 132, 62), var=10, patches=[], dots=((246, 226, 196), 14, (1, 3))),
    'bone': dict(base=(224, 216, 198), var=7, patches=[((196, 186, 166), 14, (1, 3))]),
    'rune_orange': dict(base=(255, 156, 52), var=12, patches=[((255, 226, 120), 10, (1, 2))]),
    'navy_d': dict(base=(18, 26, 62), var=7, patches=[((40, 56, 110), 18, (1, 3)), ((90, 200, 255), 5, (1, 1))]),
    'bark_rot': dict(base=(40, 30, 22), var=8, patches=[((24, 18, 14), 22, (1, 4)), ((62, 48, 32), 10, (1, 3))]),
    'moss_dk': dict(base=(42, 72, 34), var=10, patches=[((26, 48, 24), 20, (1, 3)), ((70, 104, 44), 8, (1, 2))]),
    'void': dict(base=(9, 8, 11), var=3, patches=[]),
    'glow_y': dict(base=(206, 255, 84), var=12, patches=[((250, 255, 190), 8, (1, 2))]),
    'glow_w': dict(base=(226, 248, 255), var=8, patches=[((120, 220, 255), 8, (1, 1))]),
    'thorn': dict(base=(28, 21, 16), var=6, patches=[((48, 36, 26), 14, (1, 3))]),
    'bone_d': dict(base=(176, 164, 140), var=8, patches=[((140, 128, 106), 16, (1, 3))]),
    'storm': dict(base=(15, 19, 38), var=6, patches=[((30, 40, 80), 16, (1, 3)), ((8, 10, 20), 14, (1, 3))]),
    'storm_l': dict(base=(34, 44, 84), var=8, patches=[((56, 72, 124), 16, (1, 3))]),
    'steel': dict(base=(64, 70, 86), var=8, patches=[((98, 106, 126), 12, (1, 2)), ((40, 44, 56), 12, (1, 2))]),
    'plate_dk': dict(base=(112, 88, 46), var=9, patches=[((160, 130, 70), 10, (1, 2)), ((70, 54, 28), 12, (1, 2))]),
    'horn': dict(base=(30, 25, 28), var=6, patches=[((54, 46, 50), 14, (1, 3))]),
    'cape_d': dict(base=(74, 12, 18), var=8, patches=[((40, 6, 10), 22, (1, 4)), ((110, 24, 28), 6, (1, 2))]),
    'fur': dict(base=(26, 22, 24), var=10, patches=[((52, 44, 46), 26, (1, 2))]),
    'cap_pale': dict(base=(150, 160, 120), var=10, patches=[], dots=((60, 80, 40), 14, (1, 2))),
    'plate_g': dict(base=(206, 174, 92), var=10, patches=[((246, 220, 140), 10, (1, 2)), ((150, 120, 60), 10, (1, 2))]),
}


def unfolded(size):
    w, h, d = size
    return (2 * d + 2 * w, d + h)


def pack(parts):
    rects = sorted(range(len(parts)), key=lambda i: -unfolded(parts[i]['size'])[1])
    for sheet in (64, 128, 256, 512):
        x = y = row_h = 0
        ok = True
        pos = {}
        for i in rects:
            w, h = unfolded(parts[i]['size'])
            if x + w > sheet:
                x, y, row_h = 0, y + row_h, 0
            if y + h > sheet or w > sheet:
                ok = False
                break
            pos[i] = (x, y)
            x += w
            row_h = max(row_h, h)
        if ok:
            return sheet, pos
    raise ValueError('model does not fit in a 512 sheet')


GLOW_STYLES = {'glowg', 'glow_y', 'glow_w', 'rune_cyan', 'rune_orange', 'soul_light', 'flame'}


def paint(parts, seed):
    sheet, pos = pack(parts)
    img = Image.new('RGBA', (sheet, sheet), (0, 0, 0, 0))
    glow = Image.new('RGBA', (sheet, sheet), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    px = img.load()
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for i, p in enumerate(parts):
        u, v = pos[i]
        p['uv'] = (u, v)
        w, h, dd = p['size']
        rw, rh = unfolded(p['size'])
        st = STYLES[p['style']]
        for x in range(rw):
            for y in range(rh):
                n = rnd.randint(-st['var'], st['var'])
                px[u + x, v + y] = tuple(max(0, min(255, c + n)) for c in st['base']) + (255,)
        for (col, count, (lo, hi)) in st.get('patches', []):
            for _ in range(max(1, int(count * (rw * rh) / 400))):
                x, y = rnd.randint(0, max(0, rw - 1)), rnd.randint(0, max(0, rh - 1))
                d.rectangle([u + x, v + y, min(u + rw - 1, u + x + rnd.randint(lo, hi)),
                             min(v + rh - 1, v + y + rnd.randint(lo, hi))], fill=col + (255,))
        if 'dots' in st:
            col, count, (lo, hi) = st['dots']
            for _ in range(max(2, int(count * (rw * rh) / 400))):
                x, y = rnd.randint(0, max(0, rw - 2)), rnd.randint(0, max(0, rh - 2))
                d.rectangle([u + x, v + y, min(u + rw - 1, u + x + rnd.randint(lo, hi)),
                             min(v + rh - 1, v + y + rnd.randint(lo, hi))], fill=col + (255,))
        if 'cracks' in st:
            for _ in range(max(2, int(8 * (rw * rh) / 600))):
                x, y = rnd.randint(0, max(0, rw - 1)), rnd.randint(0, max(0, rh - 1))
                for _ in range(rnd.randint(2, 5)):
                    nx = min(rw - 1, max(0, x + rnd.randint(-2, 2)))
                    ny = min(rh - 1, max(0, y + rnd.randint(-2, 2)))
                    d.line([u + x, v + y, u + nx, v + ny], fill=st['cracks'] + (255,))
                    gd.line([u + x, v + y, u + nx, v + ny], fill=st['cracks'] + (255,))
                    x, y = nx, ny
        for (fx0, fy0, fw, fh) in [(dd, 0, w, dd), (dd + w, 0, w, dd), (0, dd, dd, h), (dd, dd, w, h), (dd + w, dd, dd, h), (2 * dd + w, dd, w, h)]:
            for ex in range(fw):
                for ey in range(fh):
                    if (ex in (0, fw - 1) or ey in (0, fh - 1)) and fw > 2 and fh > 2:
                        c = px[u + fx0 + ex, v + fy0 + ey]
                        px[u + fx0 + ex, v + fy0 + ey] = (int(c[0] * 0.78), int(c[1] * 0.78), int(c[2] * 0.78), 255)
        if p['style'] in GLOW_STYLES:
            glow.paste(img.crop((u, v, u + rw, v + rh)), (u, v))
        if p['eyes']:   # eyes on the front face
            fx, fy = u + dd, v + dd
            ex = max(1, w // 4)
            ey = fy + int(h * 0.4)
            size = 2 if w >= 8 else 1
            if w >= 14:
                size = 3
            for ox in (fx + max(1, int(w * 0.22)), fx + w - max(1, int(w * 0.22)) - size):
                d.rectangle([ox, ey, ox + size - 1, ey + size - 1], fill=p['eyes'] + (255,))
                gd.rectangle([ox, ey, ox + size - 1, ey + size - 1], fill=p['eyes'] + (255,))
    img.info['glow'] = glow
    return img, sheet


# ------------------------------------------------------------------ guards
def bramble():
    return [
        part('legR', (6, 14, 6), (-3, -14, -3), (-5, 14, 0), anim='legA'),
        part('legL', (6, 14, 6), (-3, -14, -3), (5, 14, 0), anim='legB'),
        part('torso', (18, 16, 11), (-9, 0, -5.5), (0, 14, 0), style='moss'),
        part('hump', (14, 4, 7), (-7, 0, -3.5), (0, 30, -1), style='moss'),
        part('shoulderR', (8, 5, 8), (-4, 0, -4), (-13, 28, 0), style='moss'),
        part('shoulderL', (8, 5, 8), (-4, 0, -4), (13, 28, 0), style='moss'),
        part('armR', (7, 22, 7), (-3.5, -20, -3.5), (-13, 28, 0), anim='armA'),
        part('armL', (7, 22, 7), (-3.5, -20, -3.5), (13, 28, 0), anim='armB'),
        part('head', (11, 10, 10), (-5.5, 0, -5), (0, 30, 1), eyes=(150, 255, 90), anim='head'),
        part('headAntlerR', (2, 9, 2), (2.5, 10, -1), (0, 30, 1), anim='head', style='wood'),
        part('headAntlerL', (2, 9, 2), (-4.5, 10, -1), (0, 30, 1), anim='head', style='wood'),
        part('headTineR', (1, 4, 1), (4.5, 15, -0.5), (0, 30, 1), anim='head', style='wood'),
        part('headTineL', (1, 4, 1), (-5.5, 15, -0.5), (0, 30, 1), anim='head', style='wood'),
        part('mush1Stem', (2, 4, 2), (-6, 30, -4), style='stem'),
        part('mush1Cap', (7, 3, 7), (-8.5, 34, -6.5), style='cap'),
        part('mush2Stem', (2, 5, 2), (3, 30, 0), style='stem'),
        part('mush2Cap', (7, 3, 7), (0.5, 35, -2.5), style='cap'),
    ]


def sporecap():
    return [
        part('legR', (3, 5, 3), (-1.5, -5, -1.5), (-2.5, 5, 0), style='stem', anim='legA'),
        part('legL', (3, 5, 3), (-1.5, -5, -1.5), (2.5, 5, 0), style='stem', anim='legB'),
        part('body', (8, 8, 6), (-4, 0, -3), (0, 5, 0), style='stem'),
        part('armR', (2, 7, 2), (-1, -6, -1), (-5, 12, 0), rot=(-0.6, 0, 0), style='stem', anim='armA'),
        part('armL', (2, 7, 2), (-1, -6, -1), (5, 12, 0), rot=(-0.6, 0, 0), style='stem', anim='armB'),
        part('podR', (3, 3, 3), (-1.5, -8, 0), (-5, 12, 0), rot=(-0.6, 0, 0), style='glowg', anim='armA'),
        part('podL', (3, 3, 3), (-1.5, -8, 0), (5, 12, 0), rot=(-0.6, 0, 0), style='glowg', anim='armB'),
        part('head', (9, 7, 9), (-4.5, 0, -4.5), (0, 13, 0), style='stem', eyes=(150, 255, 90), anim='head'),
        part('headCap', (16, 5, 16), (-8, 0, -8), (0, 20, 0), style='cap', anim='head'),
        part('headCap2', (11, 3, 11), (-5.5, 0, -5.5), (0, 25, 0), style='cap', anim='head'),
    ]


def rootstalker():
    return [
        part('body', (8, 8, 18), (-4, 0, -9), (0, 9, 0), style='fur_moss'),
        part('chest', (9, 9, 7), (-4.5, 0, 1), (0, 9, 0), style='fur_moss'),
        part('mossBack', (6, 2, 8), (-3, 8, -7), (0, 9, 0), style='moss'),
        part('head', (8, 8, 8), (-4, -4, 0), (0, 16, 12), style='fur_moss', eyes=(150, 255, 90), anim='head'),
        part('headSnout', (4, 4, 5), (-2, -3, 8), (0, 16, 12), style='fur_moss', anim='head'),
        part('headAntlerR', (1, 8, 1), (1.5, 4, 2), (0, 16, 12), style='wood', anim='head'),
        part('headAntlerL', (1, 8, 1), (-2.5, 4, 2), (0, 16, 12), style='wood', anim='head'),
        part('headTineR', (1, 4, 1), (2.5, 9, 2), (0, 16, 12), style='wood', anim='head'),
        part('headTineL', (1, 4, 1), (-3.5, 9, 2), (0, 16, 12), style='wood', anim='head'),
        part('legFR', (3, 9, 3), (-1.5, -9, -1.5), (-3, 9, 6), style='fur_moss', anim='legA'),
        part('legFL', (3, 9, 3), (-1.5, -9, -1.5), (3, 9, 6), style='fur_moss', anim='legB'),
        part('legBR', (3, 9, 3), (-1.5, -9, -1.5), (-3, 9, -6), style='fur_moss', anim='legB'),
        part('legBL', (3, 9, 3), (-1.5, -9, -1.5), (3, 9, -6), style='fur_moss', anim='legA'),
        part('tail', (2, 2, 9), (-1, -1, -9), (0, 16, -9), rot=(0.5, 0, 0), style='fur_moss'),
    ]


def knight(style, cracks_style, helm_eyes, spear=True):
    base = [
        part('legR', (5, 12, 5), (-2.5, -12, -2.5), (-3, 12, 0), style=style, anim='legA'),
        part('legL', (5, 12, 5), (-2.5, -12, -2.5), (3, 12, 0), style=style, anim='legB'),
        part('body', (12, 13, 7), (-6, 0, -3.5), (0, 12, 0), style=style),
        part('head', (8, 8, 8), (-4, 0, -4), (0, 25, 0), style=style, eyes=helm_eyes, anim='head'),
        part('pauldronR', (6, 3, 6), (-3, 0, -3), (-9, 24, 0), style=style),
        part('pauldronL', (6, 3, 6), (-3, 0, -3), (9, 24, 0), style=style),
        part('armR', (4, 12, 4), (-2, -10, -2), (-8, 24, 0), rot=(-0.4, 0, 0), style=style, anim='armA'),
        part('armL', (4, 12, 4), (-2, -10, -2), (8, 24, 0), style=style, anim='armB'),
    ]
    return base


def calcite():
    parts = knight('armor_q', 'armor_q', (90, 220, 255))
    parts += [
        part('belt', (12, 2, 8), (-6, 0, -4), (0, 12, 0), style='gold'),
        part('tabard', (8, 8, 1), (-4, -8, 3.5), (0, 12, 0), style='trim_blue'),
        part('headCrest', (2, 4, 8), (-1, 8, -4), (0, 25, 0), style='gold', anim='head'),
        part('spearShaft', (2, 36, 2), (-1, -14, 2.5), (-8, 24, 0), rot=(-0.4, 0, 0), style='wood', anim='armA'),
        part('spearTip', (3, 5, 1), (-1.5, 22, 3), (-8, 24, 0), rot=(-0.4, 0, 0), style='plate', anim='armA'),
        part('shield', (2, 13, 10), (-1, -6, -5), (10, 24, 0), style='plate', anim='armB'),
    ]
    return parts


def ashbound():
    parts = knight('ash_armor', 'ash_armor', (255, 150, 40))
    parts += [
        part('headHornR', (2, 7, 2), (3, 6, -1), (0, 25, 0), style='ash_armor', anim='head'),
        part('headHornL', (2, 7, 2), (-5, 6, -1), (0, 25, 0), style='ash_armor', anim='head'),
        part('spikeR', (2, 4, 2), (-1, 3, -1), (-9, 24, 0), style='ash_armor'),
        part('spikeL', (2, 4, 2), (-1, 3, -1), (9, 24, 0), style='ash_armor'),
        part('cape', (12, 22, 2), (-6, -20, -5), (0, 26, 0), rot=(0.12, 0, 0), style='cape'),
        part('swordBlade', (3, 34, 1), (-1.5, -22, 2.5), (-8, 24, 0), rot=(-0.4, 0, 0), style='blade', anim='armA'),
        part('swordGuard', (9, 2, 2), (-4.5, -12, 2), (-8, 24, 0), rot=(-0.4, 0, 0), style='gold', anim='armA'),
    ]
    return parts


def wisp():
    parts = [part('core', (6, 6, 6), (-3, -3, -3), (0, 22, 0), style='cyan_core')]
    for i, (o, s) in enumerate([((7, -4, -1), (3, 8, 2)), ((-10, -4, -1), (3, 8, 2)),
                                ((-1, -4, 7), (2, 8, 3)), ((-1, -4, -10), (2, 8, 3))]):
        parts.append(part(f'plate{i}', s, o, (0, 22, 0), style='plate', anim='spin'))
    return parts


def talon():
    return [
        part('body', (6, 6, 12), (-3, -3, -6), (0, 14, 0), style='navy'),
        part('belly', (5, 2, 10), (-2.5, -3, -5), (0, 13, 0), style='feather_w'),
        part('chest', (7, 7, 5), (-3.5, -3.5, 2), (0, 14, 0), style='feather_w'),
        part('head', (5, 5, 5), (-2.5, -2.5, 0), (0, 16, 8), style='feather_w', eyes=(90, 220, 255), anim='head'),
        part('headBeak', (3, 2, 4), (-1.5, -2, 5), (0, 16, 8), style='gold', anim='head'),
        part('wingLa', (12, 1, 8), (0, -0.5, -4), (3, 16, 0), style='navy', anim='wingL'),
        part('wingLb', (12, 1, 7), (12, -0.5, -3.5), (3, 16, 0), style='navy', anim='wingL'),
        part('wingRa', (12, 1, 8), (-12, -0.5, -4), (-3, 16, 0), style='navy', anim='wingR'),
        part('wingRb', (12, 1, 7), (-24, -0.5, -3.5), (-3, 16, 0), style='navy', anim='wingR'),
        part('tail', (5, 1, 8), (-2.5, -0.5, -14), (0, 14, 0), style='navy'),
        part('clawR', (2, 5, 2), (-1, -5, -1), (-2, 11, 1), style='gold'),
        part('clawL', (2, 5, 2), (-1, -5, -1), (2, 11, 1), style='gold'),
    ]


def soul_jailer():
    parts = [
        part('robe1', (14, 6, 10), (-7, 0, -5), (0, 6, 0), style='soul_robe'),
        part('robe2', (12, 8, 8), (-6, 0, -4), (0, 12, 0), style='soul_robe'),
        part('robe3', (14, 4, 8), (-7, 0, -4), (0, 20, 0), style='soul_robe'),
        part('head', (8, 8, 8), (-4, 0, -4), (0, 24, 0), style='hood', anim='head'),
        part('headFace', (6, 6, 1), (-3, 1, 4), (0, 24, 0), style='hood', eyes=(90, 230, 255), anim='head'),
        part('headTip', (4, 4, 4), (-2, 8, -3), (0, 24, 0), style='hood', anim='head'),
        part('armR', (3, 11, 3), (-1.5, -10, -1.5), (-8, 23, 0), rot=(-1.0, 0, 0), style='soul_robe', anim='armA'),
        part('armL', (3, 11, 3), (-1.5, -10, -1.5), (8, 23, 0), rot=(-1.0, 0, 0), style='soul_robe', anim='armB'),
        part('lantern', (5, 6, 5), (-2.5, -3, 6), (-8, 16, 0), style='soul_light'),
        part('chain', (1, 5, 1), (-0.5, 3, 8), (-8, 16, 0), style='plate'),
    ]
    for i, (x, z) in enumerate([(-3, -2), (3, -2), (-3, 3), (3, 3)]):
        parts.append(part(f'wisp{i}', (3, 6, 3), (x - 1.5, 0, z - 1.5), (0, 0, 0), style='soul_light'))
    return shifted(parts, 4)


def cinder_hound():
    parts = [
        part('body', (10, 10, 18), (-5, 0, -9), (0, 10, 0), style='ash_fur'),
        part('chest', (11, 11, 8), (-5.5, 0, 1), (0, 10, 0), style='ash_fur'),
        part('head', (9, 9, 9), (-4.5, -4.5, 0), (0, 17, 12), style='ash_fur', eyes=(255, 150, 40), anim='head'),
        part('headSnout', (5, 4, 5), (-2.5, -4, 9), (0, 17, 12), style='ash_fur', anim='head'),
        part('headTuskR', (1, 3, 1), (1.5, -6, 8), (0, 17, 12), style='quartz', anim='head'),
        part('headTuskL', (1, 3, 1), (-2.5, -6, 8), (0, 17, 12), style='quartz', anim='head'),
        part('legFR', (4, 10, 4), (-2, -10, -2), (-3.5, 10, 6), style='ash_fur', anim='legA'),
        part('legFL', (4, 10, 4), (-2, -10, -2), (3.5, 10, 6), style='ash_fur', anim='legB'),
        part('legBR', (4, 10, 4), (-2, -10, -2), (-3.5, 10, -6), style='ash_fur', anim='legB'),
        part('legBL', (4, 10, 4), (-2, -10, -2), (3.5, 10, -6), style='ash_fur', anim='legA'),
        part('tail', (2, 2, 8), (-1, -1, -8), (0, 17, -9), rot=(0.4, 0, 0), style='ash_fur'),
        part('tailFlame', (3, 3, 3), (-1.5, -1.5, -11), (0, 17, -9), rot=(0.4, 0, 0), style='flame'),
    ]
    for i, z in enumerate([-6, -2, 2, 6]):
        parts.append(part(f'mane{i}', (2, 5, 2), (-1, 0, z - 1), (0, 20, 0), style='ash_armor'))
    return parts


# ------------------------------------------------------------------ bosses
def mossback():
    parts = [
        part('legR', (12, 28, 12), (-6, -28, -6), (-12, 28, 0), anim='legA'),
        part('legL', (12, 28, 12), (-6, -28, -6), (12, 28, 0), anim='legB'),
        part('torso', (40, 34, 24), (-20, 0, -12), (0, 28, 0), style='moss'),
        part('hump', (34, 10, 20), (-17, 0, -10), (0, 62, 0), style='moss'),
        part('shoulderR', (20, 8, 20), (-10, 0, -10), (-27, 58, 0), style='moss'),
        part('shoulderL', (20, 8, 20), (-10, 0, -10), (27, 58, 0), style='moss'),
        part('armR', (14, 40, 14), (-7, -36, -7), (-27, 58, 0), rot=(-0.25, 0, 0), anim='armA'),
        part('armL', (14, 40, 14), (-7, -36, -7), (27, 58, 0), rot=(-0.25, 0, 0), anim='armB'),
        part('fistR', (18, 12, 18), (-9, -48, -9), (-27, 58, 0), rot=(-0.25, 0, 0), style='moss', anim='armA'),
        part('fistL', (18, 12, 18), (-9, -48, -9), (27, 58, 0), rot=(-0.25, 0, 0), style='moss', anim='armB'),
        part('head', (22, 18, 20), (-11, 0, -8), (0, 60, 12), eyes=(150, 255, 90), anim='head'),
        part('headBrow', (24, 5, 6), (-12, 14, 8), (0, 60, 12), style='moss', anim='head'),
        part('headTuskR', (3, 10, 3), (6, -8, 10), (0, 60, 12), style='stem', anim='head'),
        part('headTuskL', (3, 10, 3), (-9, -8, 10), (0, 60, 12), style='stem', anim='head'),
        part('headAntlerR', (3, 20, 3), (8, 18, -2), (0, 60, 12), style='wood', anim='head'),
        part('headAntlerL', (3, 20, 3), (-11, 18, -2), (0, 60, 12), style='wood', anim='head'),
        part('headTineR', (2, 9, 2), (11, 30, -1.5), (0, 60, 12), style='wood', anim='head'),
        part('headTineL', (2, 9, 2), (-13, 30, -1.5), (0, 60, 12), style='wood', anim='head'),
    ]
    for i, (x, z, h) in enumerate([(-12, -4, 8), (6, -2, 10), (-2, 6, 6), (14, 4, 7), (-14, 6, 7)]):
        parts.append(part(f'mush{i}Stem', (3, h, 3), (x - 1.5, 72, z - 1.5), style='stem'))
        parts.append(part(f'mush{i}Cap', (12, 4, 12), (x - 6, 72 + h, z - 6), style='cap'))
    return parts


def roc():
    base = talon()
    parts = scaled(base, 3.0)
    extra = [
        part('crest1', (2, 8, 2), (-1, 4, -1), (0, 16, 8), style='navy', anim='head'),
        part('crest2', (2, 6, 2), (-4, 3, -1), (0, 16, 8), style='navy', anim='head'),
        part('crest3', (2, 6, 2), (2, 3, -1), (0, 16, 8), style='navy', anim='head'),
        part('chestRune', (4, 4, 1), (-2, -3, 5.5), (0, 14, 0), style='rune_cyan'),
        part('tailB', (3, 1, 6), (-1.5, -0.5, -20), (0, 14, 0), style='navy'),
    ]
    parts += scaled(extra, 3.0)
    return parts


def hollow_king():
    k = scaled(ashbound(), 2.65)
    for p in k:
        if p['style'] == 'ash_armor':
            p['style'] = 'king_armor'
    extra = [
        part('chestCore', (4, 5, 1), (-2, 3, 3.6), (0, 12, 0), style='rune_cyan'),
        part('shoulderCapeL', (6, 2, 8), (-3, 3, -4), (9, 24, 0), style='cape'),
        part('shoulderCapeR', (6, 2, 8), (-3, 3, -4), (-9, 24, 0), style='cape'),
    ]
    k += scaled(extra, 2.65)
    # floating crown: six cyan spikes in a ring above the head
    for i in range(6):
        a = i * math.pi / 3
        x, z = 13 * math.cos(a), 13 * math.sin(a)
        k.append(part(f'crown{i}', (3, 14, 3), (x - 1.5, 24, z - 1.5), (0, 25 * 2.65, 0), style='rune_cyan', anim='spin'))
    return k


MOBS = {
    'bramble_sentinel': dict(parts=bramble, seed=1, shadow=0.9),
    'sporecap': dict(parts=sporecap, seed=2, shadow=0.5),
    'rootstalker': dict(parts=rootstalker, seed=3, shadow=0.6),
    'calcite_sentinel': dict(parts=calcite, seed=4, shadow=0.6),
    'storm_wisp': dict(parts=wisp, seed=5, shadow=0.3),
    'gale_talon': dict(parts=talon, seed=6, shadow=0.4),
    'ashbound_knight': dict(parts=ashbound, seed=7, shadow=0.6),
    'soul_jailer': dict(parts=soul_jailer, seed=8, shadow=0.4),
    'cinder_hound': dict(parts=cinder_hound, seed=9, shadow=0.7),
    'mossback_titan': dict(parts=mossback, seed=10, shadow=1.8),
    'tempest_roc': dict(parts=roc, seed=11, shadow=1.8),
    'hollow_king': dict(parts=hollow_king, seed=12, shadow=1.4),
}


import bosses_v3 as bosses_v2  # noqa: E402  (detailed bosses; they take the part constructor so there is no circular import)
MOBS['mossback_titan']['parts'] = lambda: bosses_v2.mossback(part)
MOBS['tempest_roc']['parts'] = lambda: bosses_v2.roc(part)
MOBS['hollow_king']['parts'] = lambda: bosses_v2.king(part)


def build_all():
    built = {}
    os.makedirs(f'{ASSETS}/textures/entity', exist_ok=True)
    for key, m in MOBS.items():
        parts = m['parts']()
        img, sheet = paint(parts, m['seed'])
        img.info.pop('glow').save(f'{ASSETS}/textures/entity/{key}_glow.png')
        img.save(f'{ASSETS}/textures/entity/{key}.png')
        built[key] = dict(parts=parts, sheet=sheet, shadow=m['shadow'])
    return built


if __name__ == '__main__':
    b = build_all()
    for k, v in b.items():
        print(f"{k}: {len(v['parts'])} parts, texture {v['sheet']}x{v['sheet']}")

import mobs_act2  # noqa: E402  (act two: three Wardens and nine guards)
mobs_act2.register(MOBS, STYLES, GLOW_STYLES, part)

import mobs_act3  # noqa: E402  (act three: Vexor, the Bloom Mother and six guards)
mobs_act3.register(MOBS, STYLES, GLOW_STYLES, part)
