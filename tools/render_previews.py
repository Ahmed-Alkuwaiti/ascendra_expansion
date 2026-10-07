"""Preview sheets for act two: the Wardens, the guards, the citadels and the realm structures."""
from PIL import Image, ImageDraw, ImageFont

import montage
import render_models as rm
import render_structure as rs

OUT = '../previews'
S = '../src/main/resources/data/aurelia/structures/'
B = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
M = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 19)
MB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)


def header(img, title, sub, col):
    d = ImageDraw.Draw(img)
    d.text((24, 14), title, fill=col, font=B)
    d.text((24, 60), sub, fill=(225, 225, 232), font=M)


# ---- the three Wardens, front and back
BOSSES = [('vorath', 'VORATH, THE TIDE DEVOURER', 'Warden of the Drowned Expanse  |  4500 HP', (90, 230, 210), ((10, 30, 40), (20, 60, 70))),
          ('white_silence', 'THE WHITE SILENCE', 'Warden of the Pale Wastes  |  5000 HP', (220, 235, 255), ((40, 46, 58), (110, 120, 136))),
          ('kharzul', 'KHARZUL, THE GLASS REAPER', 'Warden of the Scarlet Sands  |  6000 HP', (255, 110, 90), ((50, 16, 14), (130, 60, 36)))]
tile = 620
sheet = Image.new('RGB', (tile * 2, len(BOSSES) * (tile + 100) + 10), (14, 14, 20))
for i, (key, title, sub, col, bg) in enumerate(BOSSES):
    parts, tex, glow = rm.build(key)
    y = i * (tile + 100)
    sc = None
    for k, (yaw, pitch) in enumerate([(-35, 16), (150, 18)]):
        im, s = rm.render(parts, tex, glow, yaw, pitch, size=tile, bg=bg, scale=sc)
        sc = s if sc is None else sc
        sheet.paste(im, (k * tile, y + 100))
    d = ImageDraw.Draw(sheet)
    d.text((24, y + 14), title, fill=col, font=B)
    d.text((24, y + 60), f'{sub}  |  {len(parts)} parts', fill=(225, 225, 232), font=M)
sheet.save(f'{OUT}/10_act_two_wardens.png')

# ---- the nine guards
GUARDS = [('coralclad_juggernaut', 'Coralclad Juggernaut', 'heavy, hauls you in with its anchor'),
          ('tidecaller', 'Tidecaller', 'whirlpools, mends the garrison'), ('razorclaw', 'Razorclaw', 'fast, pins you with a claw'),
          ('rimeguard', 'Rimeguard', 'heavy, freezes what it cuts'), ('hushwraith', 'Hushwraith', 'shrieks at anyone moving upright'),
          ('rimefang', 'Rimefang', 'fast, frost bite'), ('sandglass_sentinel', 'Sandglass Sentinel', 'heavy, throws projectiles back'),
          ('sunseer', 'Sunseer', 'focused sunbeam'), ('glasswing_scarab', 'Glasswing Scarab', 'burrows and bursts out beside you')]
t = 420
sheet = Image.new('RGB', (3 * t, 3 * (t + 64) + 96), (14, 14, 20))
header(sheet, 'THE OUTER CITADEL GUARDS', 'Tidewrack (top), Rimefast (middle), Sunscar (bottom). Heavy guards hold each citadel\'s seal.', (255, 210, 140))
bgs = [((12, 34, 44), (24, 66, 76)), ((44, 50, 62), (110, 120, 136)), ((52, 20, 16), (130, 66, 40))]
for i, (key, name, note) in enumerate(GUARDS):
    parts, tex, glow = rm.build(key)
    im, _ = rm.render(parts, tex, glow, -35, 14, size=t, bg=bgs[i // 3])
    x, y = (i % 3) * t, 96 + (i // 3) * (t + 64)
    sheet.paste(im, (x, y + 64))
    d = ImageDraw.Draw(sheet)
    d.text((x + 12, y + 6), name, fill=(240, 240, 245), font=MB)
    d.text((x + 12, y + 36), note, fill=(190, 190, 200), font=M)
sheet.save(f'{OUT}/11_act_two_guards.png')


# ---- citadels: exterior and a cut-away, side by side
def citadel(name, file, title, sub, col, ext, cut, bg):
    a = rs.render(S + file, '/tmp/_a.png', size=860, bg=bg, **ext)
    b = rs.render(S + file, '/tmp/_b.png', size=860, bg=bg, **cut)
    a.thumbnail((900, 900))
    b.thumbnail((900, 900))
    img = Image.new('RGB', (1840, 1060), (14, 14, 20))
    img.paste(a, (20, 120))
    img.paste(b, (940, 120))
    header(img, title, sub, col)
    d = ImageDraw.Draw(img)
    d.text((24, 92), 'white: heavy guard   pink: caster   orange: beast', fill=(200, 200, 210), font=M)
    img.save(f'{OUT}/{name}')


citadel('12_tidewrack_citadel.png', 'tidewrack_citadel.nbt', 'THE TIDEWRACK CITADEL',
        'Portal to the Drowned Expanse | ocean | RITE: ring five Tide Bells in rising order, in a dry vault under the reef',
        (90, 230, 210), dict(sea=22), dict(cut=30, hide=['water', 'kelp', 'seagrass']), ((16, 30, 44), (40, 70, 90)))
citadel('13_rimefast_citadel.png', 'rimefast_citadel.nbt', 'THE RIMEFAST CITADEL',
        'Portal to the Pale Wastes | snowy biomes | RITE: crouch, perfectly still, on four Hush Stones in the chapel',
        (220, 235, 255), dict(rot=2), dict(rot=2, cutx=40), ((40, 46, 58), (100, 110, 126)))
citadel('14_sunscar_citadel.png', 'sunscar_citadel.nbt', 'THE SUNSCAR CITADEL',
        'Portal to the Scarlet Sands | desert and badlands | RITE: turn the Sun Mirrors so the Sunwell\'s beam lights three lenses',
        (255, 120, 90), dict(), dict(cut=32), ((60, 30, 20), (140, 80, 50)))


# ---- the Sunscar mirror court, seen from above (the starting state; no solution shown)
import gen_act2_citadels as gc
cs_ = 44
img = Image.new('RGB', (19 * cs_ + 60, 19 * cs_ + 170), (14, 14, 20))
d = ImageDraw.Draw(img)
header(img, 'THE MIRROR COURT', 'Sunscar Citadel, from above. North is up. Touch a mirror to flip it; light each lens.', (255, 120, 90))
ox, oy = 30, 120
for i in range(-1, 18):
    for j in range(-1, 18):
        x, y = ox + (i + 1) * cs_, oy + (j + 1) * cs_
        wall = i in (-1, 17) or j in (-1, 17)
        col = (120, 60, 30) if wall else (196, 120, 70)
        if (i, j) in gc.SUN_OPENINGS:
            col = (60, 40, 30)
        d.rectangle([x, y, x + cs_ - 2, y + cs_ - 2], fill=col)
        if (i, j) in gc.SUN_PILLARS:
            d.rectangle([x + 6, y + 6, x + cs_ - 8, y + cs_ - 8], fill=(150, 70, 30), outline=(250, 236, 180), width=3)
        if (i, j) in gc.SUN_LENSES:
            d.ellipse([x + 6, y + 6, x + cs_ - 8, y + cs_ - 8], fill=(220, 50, 50), outline=(255, 210, 120), width=3)
        if (i, j) == gc.SUN_SOURCE:
            d.ellipse([x + 4, y + 4, x + cs_ - 6, y + cs_ - 6], fill=(255, 214, 90))
            d.polygon([(x + cs_ // 2, y - 6), (x + 10, y + 10), (x + cs_ - 12, y + 10)], fill=(255, 250, 200))
        if (i, j) == (8, -1):
            d.rectangle([x + 4, y + 4, x + cs_ - 6, y + cs_ - 6], fill=(255, 220, 120))
            d.text((x + 10, y + 8), 'P', fill=(40, 20, 10), font=MB)
for (i, j), slash in zip(gc.SUN_MIRRORS, gc.SUN_INIT):
    x, y = ox + (i + 1) * cs_, oy + (j + 1) * cs_
    d.rectangle([x, y, x + cs_ - 2, y + cs_ - 2], fill=(230, 180, 60))
    a, b = ((x + 6, y + cs_ - 8), (x + cs_ - 8, y + 6)) if slash else ((x + 6, y + 6), (x + cs_ - 8, y + cs_ - 8))
    d.line([a, b], fill=(255, 255, 255), width=6)
ly = oy + 19 * cs_ + 12
d.text((30, ly), 'yellow = Sunwell (fires north)  gold = mirror  red = lens  P = portal  framed = pillar',
       fill=(220, 220, 228), font=M)
img.save(f'{OUT}/16_sunscar_mirror_court.png')

montage.montage(['drowned_spire_0', 'drowned_wreck_0', 'drowned_bones_0', 'drowned_outpost_0', 'drowned_outpost_1', 'drowned_spire_2',
                 'pale_colossus_0', 'pale_colossus_1', 'pale_spire_2', 'pale_outpost_0', 'pale_outpost_1', 'pale_spire_0',
                 'scarlet_monolith_2', 'scarlet_bones_0', 'scarlet_outpost_0', 'scarlet_outpost_1', 'scarlet_monolith_0', 'drowned_wreck_1'],
                f'{OUT}/15_outer_realm_structures.png', cols=6, tile=360)
print('previews written')
