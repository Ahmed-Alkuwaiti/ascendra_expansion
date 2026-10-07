"""The Arsenals of the Tenfold Seal as one sheet, laid out like the design reference: per realm, its armor (rendered on a stand),
weapon, three tools, ore (as a block) and two materials. Usage: python3 arsenal_sheet.py out.jpg"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import arsenal_art as art
import gen_armor as ga
from kit_data import ARSENAL, GENESIS, REALMS
from pixelart import upscale

F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REALM_TITLE = {'grove': 'GAUDY GROVE', 'skyreach': 'SKYREACH', 'hollow': 'THE HOLLOW', 'drowned': 'DROWNED EXPANSE', 'pale': 'PALE WASTES',
               'scarlet': 'SCARLET SANDS', 'clockwork': 'CLOCKWORK RIFT', 'mycelial': 'MYCELIAL DEEP', 'genesis': 'UNMAKER ENDGAME'}
ACCENT = {'grove': (90, 200, 70), 'skyreach': (90, 170, 240), 'hollow': (220, 60, 50), 'drowned': (40, 190, 180), 'pale': (150, 160, 230),
          'scarlet': (230, 50, 70), 'clockwork': (190, 150, 70), 'mycelial': (190, 70, 210), 'genesis': (240, 220, 160)}
BGS = {'grove': (14, 26, 16), 'skyreach': (16, 26, 46), 'hollow': (30, 12, 14), 'drowned': (8, 28, 32), 'pale': (24, 26, 44),
       'scarlet': (36, 12, 14), 'clockwork': (26, 20, 14), 'mycelial': (28, 12, 32), 'genesis': (20, 20, 30)}


def pixel_text(text, size, colour, shadow=(0, 0, 0), k=3):
    """Text drawn without antialiasing at a small size, then blown up: a pixel font."""
    f = ImageFont.truetype(F, size)
    w = int(f.getlength(text)) + 4
    im = Image.new('RGBA', (w, size + 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    d.text((2, 2), text, font=f, fill=shadow + (255,))
    d.text((1, 1), text, font=f, fill=colour + (255,))
    return upscale(im.crop(im.getbbox()), k)


def iso_block(tex, a=64):
    """A 16 x 16 block texture on an isometric cube: lit top, mid left, dark right."""
    T = np.asarray(tex.convert('RGBA'), dtype=np.float32)
    W, H = 2 * a, 2 * a
    out = np.zeros((H, W, 4), np.float32)
    top, right, bottom, left = np.array([a, 0.]), np.array([2 * a, a / 2]), np.array([a, a]), np.array([0, a / 2])
    down = np.array([0, a])
    faces = [(top, right - top, left - top, 1.0), (left, bottom - left, down, 0.78), (bottom, right - bottom, down, 0.6)]
    ys, xs = np.mgrid[0:H, 0:W]
    P = np.stack([xs + 0.5, ys + 0.5], -1)
    for o, e1, e2, shade in faces:
        M = np.linalg.inv(np.array([e1, e2]).T)
        uv = (P - o) @ M.T
        m = (uv[..., 0] >= 0) & (uv[..., 0] < 1) & (uv[..., 1] >= 0) & (uv[..., 1] < 1)
        iu = np.clip((uv[..., 0] * 16).astype(int), 0, 15)
        iv = np.clip((uv[..., 1] * 16).astype(int), 0, 15)
        c = T[iv, iu]
        out[m, :3] = c[m, :3] * shade
        out[m, 3] = 255
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


def cell(w, h, bg, accent):
    im = Image.new('RGBA', (w, h), bg + (255,))
    d = ImageDraw.Draw(im)
    for y in range(h):                                              # a soft vignette
        t = abs(y - h / 2) / (h / 2)
        d.line([(0, y), (w, y)], fill=tuple(int(c * (1 - 0.35 * t)) for c in bg) + (255,))
    return im


def fit(img, w, h):
    img = img.crop(img.getbbox()) if img.getbbox() else img
    k = min(w / img.width, h / img.height)
    return img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.NEAREST)


def caption(text, w):
    t = pixel_text(text.upper(), 9, (236, 232, 220), k=2)
    if t.width > w - 8:
        t = t.resize((w - 8, int(t.height * (w - 8) / t.width)), Image.NEAREST)
    return t


def main(out):
    COLS = [('', 190), ('ARMOR', 250), ('WEAPON', 270), ('TOOLS', 330), ('ORE', 190), ('MATERIALS', 300)]
    RH = 250
    W = sum(c[1] for c in COLS) + 2 * 12
    H = 150 + 52 + RH * 10 + 12
    sheet = Image.new('RGBA', (W, H), (16, 14, 20, 255))
    d = ImageDraw.Draw(sheet)
    title = pixel_text('ARSENALS OF THE TENFOLD SEAL', 20, (250, 210, 110), (90, 50, 10), k=3)
    sheet.alpha_composite(title, ((W - title.width) // 2, 40))
    x = 12
    for name, w in COLS:
        d.rectangle([x, 150, x + w - 4, 196], fill=(36, 34, 46, 255), outline=(70, 66, 90, 255))
        if name:
            t = pixel_text(name, 12, (220, 214, 240), k=2)
            sheet.alpha_composite(t, (x + (w - t.width) // 2, 160))
        x += w
    rows = [(r, ARSENAL[r]) for r in REALMS] + [('genesis', GENESIS)]
    for i, (realm, a) in enumerate(rows):
        y0 = 202 + i * RH + (RH if realm == 'genesis' else 0) * 0
        rh = RH if realm != 'genesis' else RH + RH - 6
        if realm == 'genesis':
            y0 = 202 + 8 * RH
        acc, bg = ACCENT[realm], BGS[realm]
        x = 12
        armor_name = (a['armor_name'] + ' armor').upper()
        cells = []
        # label
        c = cell(COLS[0][1] - 4, rh - 6, bg, acc)
        words = REALM_TITLE[realm].split(' ')
        lines = [' '.join(words[:len(words) // 2 or 1]), ' '.join(words[len(words) // 2 or 1:])] if len(words) > 1 else [words[0]]
        ty = (c.height - 40 * len(lines)) // 2
        for ln in lines:
            if not ln:
                continue
            t = pixel_text(ln, 13, acc, k=3)
            t = fit(t, c.width - 16, 40) if t.width > c.width - 16 else t
            c.alpha_composite(t, ((c.width - t.width) // 2, ty))
            ty += 44
        cells.append(c)
        # armor
        c = cell(COLS[1][1] - 4, rh - 6, bg, acc)
        front = ga.render_preview(realm, size=420, bg=None, views=((-24, 6),))[0]
        im = front.convert('RGBA')
        px = np.array(im)
        px[..., 3] = np.where(px[..., :3].sum(-1) > 0, 255, 0)
        im = fit(Image.fromarray(px), c.width - 20, c.height - 44)
        c.alpha_composite(im, ((c.width - im.width) // 2, 8))
        cap = caption(armor_name, c.width)
        c.alpha_composite(cap, ((c.width - cap.width) // 2, c.height - cap.height - 8))
        cells.append(c)
        # weapon
        c = cell(COLS[2][1] - 4, rh - 6, bg, acc)
        wpn = upscale(art.WEAPONS[realm][1]().render(), 3)
        wpn = fit(wpn, c.width - 30, c.height - 44)
        c.alpha_composite(wpn, ((c.width - wpn.width) // 2, 6))
        cap = caption(a['weapon_name'], c.width)
        c.alpha_composite(cap, ((c.width - cap.width) // 2, c.height - cap.height - 8))
        cells.append(c)
        # tools
        c = cell(COLS[3][1] - 4, rh - 6, bg, acc)
        for k, fn in enumerate((art.pickaxe, art.axe, art.shovel)):
            t = upscale(fn(realm).render(), 3)
            c.alpha_composite(t, (6 + k * 106, (c.height - t.height) // 2 - 10))
        cap = caption(a['tool_name'] + ' tools', c.width)
        c.alpha_composite(cap, ((c.width - cap.width) // 2, c.height - cap.height - 8))
        cells.append(c)
        # ore
        c = cell(COLS[4][1] - 4, rh - 6, bg, acc)
        if realm == 'genesis':
            blk = upscale(art.MATERIALS['fractured_genesis']().render(), 4)
            name = 'Fractured Genesis (boss drop)'
        else:
            blk = iso_block(art.ore(a['ore']).render(outline=False, halo=False), 62)
            name = a['ore_name'].replace(' Ore', '')
        c.alpha_composite(blk, ((c.width - blk.width) // 2, max(6, (c.height - 44 - blk.height) // 2)))
        cap = caption(name, c.width)
        c.alpha_composite(cap, ((c.width - cap.width) // 2, c.height - cap.height - 8))
        cells.append(c)
        # materials
        c = cell(COLS[5][1] - 4, rh - 6, bg, acc)
        mats = [(a['metal'], a['metal_name']), (a['special'], a['special_name'])] if realm != 'genesis' else \
            [('genesis_ingot', 'Genesis Ingot'), ('hand_of_genesis', 'Hand of Genesis')]
        if realm in ('skyreach', 'drowned', 'mycelial'):
            mats = [(a['special'], a['special_name']), (a['metal'], a['metal_name'])]
        for k, (mid, mname) in enumerate(mats):
            if mid == 'hand_of_genesis':
                import relics
                m = relics.render_relic(relics.hand_of_genesis(), size=260, k=8)
                m = fit(m, 120, 120)
            else:
                m = upscale(art.MATERIALS[mid]().render(), 4)
            sub_w = c.width // 2
            c.alpha_composite(m, (k * sub_w + (sub_w - m.width) // 2, max(4, (c.height - 60 - m.height) // 2)))
            cap = caption(mname, sub_w)
            c.alpha_composite(cap, (k * sub_w + (sub_w - cap.width) // 2, c.height - cap.height - 10))
        cells.append(c)
        x = 12
        for (nm, w), cc in zip(COLS, cells):
            sheet.alpha_composite(cc, (x, y0))
            d.rectangle([x, y0, x + w - 5, y0 + rh - 7], outline=acc + (255,), width=2)
            x += w
    sheet.convert('RGB').save(out, quality=92)
    print('wrote', out, sheet.size)


if __name__ == '__main__':
    main(sys.argv[1])
