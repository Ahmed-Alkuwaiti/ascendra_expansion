"""Act two citadels as vanilla structure templates (DataVersion 3465 = 1.20.1).

Tidewrack - a drowned sea-fortress on a reef. Rite: ring five Tide Bells as the tide rises (shortest pedestal first).
Rimefast  - a hushed abbey in the snow.        Rite: crouch, perfectly still, on four Hush Stones.
Sunscar   - a sun temple in the red desert.    Rite: turn the Sun Mirrors so the Sunwell's beam lights three lenses.
"""
import itertools
import math
import random

import gen_citadels2 as base
from gen_citadels2 import AIR, Grid, chest_nbt, disc, lectern, sphere

base.PASSABLE.update({'minecraft:water', 'minecraft:seagrass', 'minecraft:tall_seagrass', 'minecraft:kelp', 'minecraft:kelp_plant',
                      'minecraft:sea_pickle', 'minecraft:tube_coral', 'minecraft:brain_coral', 'minecraft:bubble_coral', 'minecraft:fire_coral',
                      'minecraft:horn_coral', 'minecraft:tube_coral_fan', 'minecraft:snow', 'minecraft:candle', 'minecraft:white_candle',
                      'minecraft:light_blue_candle', 'minecraft:red_candle', 'minecraft:sculk_vein', 'minecraft:dead_bush', 'minecraft:campfire',
                      'minecraft:wall_torch', 'minecraft:torch', 'minecraft:light_blue_carpet', 'minecraft:white_carpet', 'minecraft:red_carpet',
                      'minecraft:orange_carpet', 'minecraft:spruce_trapdoor', 'minecraft:iron_bars', 'aurelia:tide_bell'})
# guards must never stand on water, even though swimmers can move through it
_solid = Grid.solid
Grid.solid = lambda self, x, y, z: _solid(self, x, y, z) and (self.get(x, y, z) or ('',))[0] != 'minecraft:water'

WL = 22                     # Tidewrack: the last water layer in template space (placed at y 40, so world y 62, under sea level 63)
WATER = 'minecraft:water'


def stairs(facing, half='bottom'):
    return {'facing': facing, 'half': half, 'shape': 'straight', 'waterlogged': 'false'}


def slab(kind='bottom'):
    return {'type': kind, 'waterlogged': 'false'}


def chest(g, x, y, z, table, facing='north'):
    g.set(x, y, z, 'minecraft:chest', {'facing': facing, 'type': 'single', 'waterlogged': 'false'}, chest_nbt(table))


def lantern(g, x, y, z, soul=False, hanging=False):
    g.set(x, y, z, 'minecraft:soul_lantern' if soul else 'minecraft:lantern', {'hanging': str(hanging).lower(), 'waterlogged': 'false'})


def ring(g, cx, cz, r0, r1, y0, y1, pick):
    for x in range(int(cx - r1) - 1, int(cx + r1) + 2):
        for z in range(int(cz - r1) - 1, int(cz + r1) + 2):
            d = math.hypot(x - cx, z - cz)
            if r0 <= d <= r1:
                for y in range(y0, y1 + 1):
                    g.set(x, y, z, pick(x, y, z, d))


# ================================================================================================ TIDEWRACK
def tidewrack():
    W = L = 65
    H = 72
    C = 32
    rnd = random.Random(404)
    g = Grid(W, H, L)
    PB, DP, PR, SL = 'minecraft:prismarine_bricks', 'minecraft:dark_prismarine', 'minecraft:prismarine', 'minecraft:sea_lantern'
    CORALS = ['tube', 'brain', 'bubble', 'fire', 'horn']

    def rock(x, y, z, d=0):
        roll = rnd.random()
        return 'minecraft:stone' if roll < 0.45 else 'minecraft:gravel' if roll < 0.55 else 'minecraft:andesite' if roll < 0.75 else PR

    # ---- the reef mound: rough rock rising toward the island, sand and coral on top, lagoon water above
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if d > 31.5:
                continue
            top = int(13 - d * 0.22 + rnd.uniform(-1.0, 1.0))
            for y in range(0, top + 1):
                g.set(x, y, z, rock(x, y, z) if y < top else ('minecraft:sand' if rnd.random() < 0.8 else 'minecraft:gravel'))
            if d < 27.5:                                      # the lagoon inside the sea wall
                for y in range(top + 1, WL + 1):
                    g.set(x, y, z, WATER, {'level': '0'})
                if rnd.random() < 0.10:
                    c = rnd.choice(CORALS)
                    g.set(x, top, z, f'minecraft:{c}_coral_block')
                    g.set(x, top + 1, z, f'minecraft:{c}_coral', {'waterlogged': 'true'})
                elif rnd.random() < 0.10:
                    for k in range(rnd.randint(3, WL - top - 1)):
                        g.set(x, top + 1 + k, z, 'minecraft:kelp_plant')
                elif rnd.random() < 0.18:
                    g.set(x, top + 1, z, 'minecraft:seagrass')
                elif rnd.random() < 0.03:
                    g.set(x, top + 1, z, 'minecraft:sea_pickle', {'pickles': str(rnd.randint(1, 4)), 'waterlogged': 'true'})
            for y in range(WL + 1, H):                        # clear the air above the reef
                if d < 30.5:
                    g.set(x, y, z, AIR)

    # ---- the sea wall: a broken ring from the reef to well above the water, with a wall-walk and battlements
    def wall_block(x, y, z, d):
        r = rnd.random()
        return DP if r < 0.25 else (PR if r < 0.45 else PB)
    breaches = [math.radians(a) for a in (65, 200, 300)]
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if 27.5 <= d <= 30.0:
                ang = math.atan2(z - C, x - C)
                broken = any(abs((ang - b + math.pi) % (2 * math.pi) - math.pi) < 0.11 for b in breaches)
                top = WL + 6 - (rnd.randint(4, 9) if broken else 0)
                for y in range(4, top + 1):
                    g.set(x, y, z, wall_block(x, y, z, d))
                if not broken and int((ang + math.pi) * 30) % 2 == 0 and d > 29.0:
                    g.set(x, WL + 7, z, PB)
                if broken:
                    for y in range(top + 1, WL + 1):
                        g.set(x, y, z, WATER, {'level': '0'})
    # sea gate on the south side (+z), at the waterline, with a portcullis of iron bars half raised
    for x in range(C - 3, C + 4):
        for z in range(C + 26, C + 32):
            for y in range(WL - 3, WL + 5):
                if math.hypot(x - C, z - C) >= 27.0:
                    g.set(x, y, z, WATER if y <= WL else AIR, {'level': '0'} if y <= WL else None)
    for x in range(C - 4, C + 5):
        g.set(x, WL + 5, C + 29, DP)
        g.set(x, WL + 6, C + 29, PB)
    for x in (C - 4, C + 4):
        for y in range(WL - 3, WL + 6):
            g.set(x, y, C + 29, DP)
    for x in range(C - 3, C + 4):
        g.set(x, WL + 4, C + 29, 'minecraft:iron_bars')
    for x in (C - 4, C + 4):
        g.set(x, WL + 7, C + 29, SL)
    # four round towers on the diagonals, hollow, ladders inside, a lantern room on top
    for (sx, sz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        tx, tz = C + round(sx * 20.5), C + round(sz * 20.5)
        for x in range(tx - 4, tx + 5):
            for z in range(tz - 4, tz + 5):
                d = math.hypot(x - tx, z - tz)
                if d <= 4.3:
                    for y in range(3, WL + 16):
                        g.set(x, y, z, (DP if rnd.random() < 0.3 else PB) if d > 3.0 else (AIR if y > WL else WATER))
                    g.set(x, WL + 1, z, DP if d <= 3.0 else PB)
                    g.set(x, WL + 6, z, 'minecraft:spruce_planks' if d <= 3.0 else PB)
                    g.set(x, WL + 16, z, DP)
                if 3.7 < d <= 4.5 and (x + z) % 2 == 0:
                    g.set(x, WL + 17, z, PB)
        for y in range(WL + 2, WL + 16):
            g.set(tx, y, tz - 3 if sz > 0 else tz + 3, 'minecraft:ladder', {'facing': 'south' if sz > 0 else 'north', 'waterlogged': 'false'})
        g.set(tx, WL + 16, tz - 3 if sz > 0 else tz + 3, AIR)
        for (dx, dz) in ((3, 0), (-3, 0), (0, 3), (0, -3)):
            g.set(tx + dx, WL + 9, tz + dz, 'minecraft:light_blue_stained_glass')
        g.set(tx, WL + 17, tz, SL)
        lantern(g, tx, WL + 15, tz, hanging=True)
        # doors from the wall-walk on either side into each tower
        dx, dz = (C - tx), (C - tz)
        n = math.hypot(dx, dz)
        for sgn in (1, -1):
            for k in range(2, 6):
                for y in (WL + 7, WL + 8):
                    for (ax, az) in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)):
                        cx, cz = round(tx - sgn * dz / n * k) + ax, round(tz + sgn * dx / n * k) + az
                        if math.hypot(cx - tx, cz - tz) > 2.5:
                            g.set(cx, y, cz, AIR)
        chest(g, tx + 1, WL + 2, tz, 'aurelia:chests/tidewrack_cache', 'west')
    # rope ladders from the lagoon up to the wall-walk
    for a in (20, 110, 160, 250, 340):
        ang = math.radians(a)
        x, z = round(C + 27.0 * math.cos(ang)), round(C + 27.0 * math.sin(ang))
        face = ('east' if math.cos(ang) < 0 else 'west') if abs(math.cos(ang)) > abs(math.sin(ang)) else ('south' if math.sin(ang) < 0 else 'north')
        for y in range(WL - 2, WL + 7):
            if g.get(x, y, z) and g.get(x, y, z)[0] in (WATER, AIR):
                g.set(x, y, z, 'minecraft:ladder', {'facing': face, 'waterlogged': 'true' if y <= WL else 'false'})

    # ---- the central island and the keep
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C) + rnd.uniform(-0.6, 0.6)
            if d <= 12.5:
                for y in range(0, WL + 2):
                    g.set(x, y, z, rock(x, y, z))
                top = 'minecraft:sand' if d > 10.5 else ('minecraft:grass_block' if rnd.random() < 0.6 else 'minecraft:moss_block')
                g.set(x, WL + 1, z, top, {'snowy': 'false'} if top == 'minecraft:grass_block' else None)
    K0, K1, KF = C - 8, C + 8, WL + 2                     # keep footprint, ground floor
    for x in range(K0, K1 + 1):
        for z in range(K0, K1 + 1):
            edge = x in (K0, K1) or z in (K0, K1)
            for y in range(KF, KF + 15):
                g.set(x, y, z, (DP if (y - KF) % 5 == 0 else PB) if edge else AIR)
            g.set(x, KF - 1, z, DP if (x + z) % 2 else PR)
            g.set(x, KF + 15, z, DP)
            if edge and (x + z) % 2 == 0:
                g.set(x, KF + 16, z, PB)
    for (bx, bz) in [(K0, K0), (K1, K0), (K0, K1), (K1, K1)]:   # corner buttresses
        for y in range(KF - 1, KF + 18):
            g.set(bx, y, bz, DP)
        g.set(bx, KF + 18, bz, SL)
    for x in range(C - 1, C + 2):                              # keep door (south) and arrow-slit windows
        for y in range(KF, KF + 4):
            g.set(x, y, K1, AIR)
    for k in (-5, 5):
        for y in (KF + 7, KF + 8, KF + 11):
            g.set(C + k, y, K0, 'minecraft:light_blue_stained_glass')
            g.set(C + k, y, K1, 'minecraft:light_blue_stained_glass')
            g.set(K0, y, C + k, 'minecraft:light_blue_stained_glass')
            g.set(K1, y, C + k, 'minecraft:light_blue_stained_glass')
    # the lighthouse rising from the keep roof
    for y in range(KF + 15, KF + 38):
        for x in range(C - 4, C + 5):
            for z in range(C - 4, C + 5):
                d = math.hypot(x - C, z - C)
                if d <= 3.6:
                    g.set(x, y, z, (PB if (y // 4) % 2 else DP) if d > 2.4 else AIR)
    for y in range(KF, KF + 15):
        g.set(C, y, C + 3, DP)
    for y in range(KF, KF + 39):
        g.set(C, y, C + 2, 'minecraft:ladder', {'facing': 'north', 'waterlogged': 'false'})
    for x in range(C - 4, C + 5):
        for z in range(C - 4, C + 5):
            d = math.hypot(x - C, z - C)
            if d <= 4.6:
                g.set(x, KF + 38, z, DP)
            if 3.8 < d <= 4.6:
                g.set(x, KF + 39, z, 'minecraft:prismarine_wall')
    g.set(C, KF + 38, C + 2, 'minecraft:ladder', {'facing': 'north', 'waterlogged': 'false'})
    for (dx, dz) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        for y in range(KF + 39, KF + 43):
            g.set(C + dx, y, C + dz, PB)
    sphere(g, C, KF + 41, C, 1.2, SL)
    for x in range(C - 3, C + 4):
        for z in range(C - 3, C + 4):
            if math.hypot(x - C, z - C) <= 3.2:
                g.set(x, KF + 43, z, DP)
    g.set(C, KF + 44, C, 'minecraft:lightning_rod', {'facing': 'up', 'powered': 'false', 'waterlogged': 'false'})
    chest(g, C + 1, KF + 39, C - 1, 'aurelia:chests/tidewrack_cache', 'south')

    # keep ground floor: a pillared hall, drowned banners, the stair down sealed with coral
    for (px, pz) in [(C - 5, C - 5), (C + 5, C - 5), (C - 5, C + 5), (C + 5, C + 5)]:
        for y in range(KF, KF + 15):
            g.set(px, y, pz, DP if y % 3 else SL)
    for x in range(K0 + 1, K1):
        for z in range(K0 + 1, K1):
            if (x - C) ** 2 + (z - C) ** 2 > 9 and rnd.random() < 0.06:
                g.set(x, KF, z, 'minecraft:light_blue_carpet')
    lectern(g, C + 5, KF, C + 2, 'west', 'The Tidewrack Citadel',
            ["Vorath kept the sea so calm that the Sovereign sailed her whole court across it. Then the crown broke, and the sea "
             "remembered it was hungry. This citadel is all that was left above the water.",
             "The way down is sealed with living coral. It will not open while the Coralclad Juggernauts still walk the wall.",
             "Below, five Tide Bells hang in the vault. Ring them as the tide rises: the lowest bell first, the highest last. "
             "Ring one out of turn and every bell falls silent, and the sea comes in to punish you."])
    # ---- the Bell Vault: a dry dome under the reef, five bells on stepped pedestals, the portal in a glass alcove
    SX, SZ = C - 4, C - 1                                     # the stair shaft, in the hall's west side
    VF = 6                                                    # vault floor (template y), deep under the lagoon
    VC = (C, C - 1)
    for x in range(C - 12, C + 13):
        for z in range(C - 13, C + 12):
            for y in range(VF - 2, VF + 13):
                dx, dz, dy = x - VC[0], z - VC[1], y - VF
                inside = (dx * dx + dz * dz) / 81.0 + max(0, dy) ** 2 / 100.0
                if inside <= 1.0 and dy >= 1:
                    g.set(x, y, z, AIR)
                elif inside <= 1.55 and dy >= -1:
                    g.set(x, y, z, DP if rnd.random() < 0.7 else PB)
            if (x - VC[0]) ** 2 + (z - VC[1]) ** 2 <= 81:
                ring_d = math.hypot(x - VC[0], z - VC[1])
                g.set(x, VF, z, SL if int(ring_d) in (3, 7) and (x + z) % 3 == 0 else (PR if int(ring_d) % 2 else DP))
    # the shaft: walled where it runs through rock, open where it hangs from the vault ceiling
    for y in range(VF + 1, KF):
        for x in range(SX - 2, SX + 3):
            for z in range(SZ - 2, SZ + 3):
                in_vault = g.get(x, y, z) is not None and g.get(x, y, z)[0] == AIR and y <= VF + 11
                wall = abs(x - SX) == 2 or abs(z - SZ) == 2
                if not in_vault:
                    g.set(x, y, z, DP if wall else AIR)
    RINGC = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    for y in range(KF - 1, VF, -1):                           # a spiral of steps around a sea-lantern core
        ox, oz = RINGC[(KF - 1 - y) % 8]
        g.set(SX + ox, y, SZ + oz, DP)
        g.set(SX, y, SZ, SL if y % 4 == 0 else DP)
    for x in range(SX - 1, SX + 2):
        for z in range(SZ - 1, SZ + 2):
            if (x, z) not in ((SX, SZ), (SX + 1, SZ)):
                g.set(x, KF - 1, z, AIR)
    for y in range(KF, KF + 4):                               # the Coral Seal: a cage of living coral over the shaft
        for x in range(SX - 2, SX + 3):
            for z in range(SZ - 2, SZ + 3):
                if abs(x - SX) == 2 or abs(z - SZ) == 2:
                    g.set(x, y, z, 'aurelia:coral_seal')
    for x in range(SX - 2, SX + 3):
        for z in range(SZ - 2, SZ + 3):
            g.set(x, KF + 4, z, 'aurelia:coral_seal')
    # five bells on pedestals 0 to 4 blocks tall; spatial order is shuffled so the heights (and their voices) are the clue
    notes = [2, 0, 4, 1, 3]
    for i, note in enumerate(notes):
        a = math.radians(20 + 35 * i)
        bx, bz = round(VC[0] + 6.0 * math.cos(a)), round(VC[1] + 6.0 * math.sin(a))
        for k in range(note):
            g.set(bx, VF + 1 + k, bz, PB if k < note - 1 else 'minecraft:chiseled_stone_bricks')
        g.set(bx, VF + 1 + note, bz, 'aurelia:tide_bell', {'note': str(note), 'rung': 'false'})
        g.set(bx, VF + 8, bz, SL)
    for x in (C - 1, C, C + 1):                               # portal alcove on the north wall of the vault
        for y in range(VF + 1, VF + 5):
            g.set(x, y, VC[1] - 9, 'minecraft:light_blue_stained_glass')
    for y in range(VF + 1, VF + 6):
        g.set(C - 2, y, VC[1] - 8, DP)
        g.set(C + 2, y, VC[1] - 8, DP)
    g.box(C - 2, VF + 5, VC[1] - 8, C + 2, VF + 5, VC[1] - 8, SL)
    g.set(C, VF + 1, VC[1] - 8, 'aurelia:waygate', {'realm': 'drowned', 'active': 'false'})
    chest(g, C - 6, VF + 1, VC[1] + 4, 'aurelia:chests/tidewrack_cache', 'east')
    chest(g, C + 6, VF + 1, VC[1] + 4, 'aurelia:chests/tidewrack_cache', 'west')
    lectern(g, C + 3, VF + 1, VC[1] + 6, 'north', 'The Bell Vault',
            ["The tide rises from the lowest stone to the highest. So must the bells: first the bell that stands on the floor, "
             "then the one a step higher, up to the highest. Listen as you go; each voice is higher than the last."])
    for (lx, lz) in [(C - 5, VC[1] - 5), (C + 5, VC[1] - 5), (C, VC[1] + 7)]:
        lantern(g, lx, VF + 9, lz, hanging=True)

    # ---- causeways: from the sea gate and two breaches to the island, a stone deck above the water with brine grates
    def causeway(x0, z0, x1, z1):
        n = int(math.hypot(x1 - x0, z1 - z0))
        for i in range(n + 1):
            t = i / max(n, 1)
            x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
            for w in (-1, 0, 1):
                nx, nz = -(z1 - z0) / max(n, 1), (x1 - x0) / max(n, 1)
                g.set(x + nx * w, WL + 1, z + nz * w, 'aurelia:brine_grate' if (i % 7 == 3 and w == 0) else (PB if rnd.random() < 0.7 else PR))
            if i % 5 == 0:
                for yy in range(4, WL + 1):
                    g.set(x, yy, z, DP)
            if i % 4 == 0:
                for w in (-2, 2):
                    g.set(x + nx * w, WL + 2, z + nz * w, 'minecraft:prismarine_wall')
                    if i % 8 == 0:
                        lantern(g, round(x + nx * w), WL + 3, round(z + nz * w))
    causeway(C, C + 27, C, K1 + 1)
    for deg in (300, 200):                                    # two more causeways run in from breaches in the wall
        ang = math.radians(deg)
        causeway(C + 27.5 * math.cos(ang), C + 27.5 * math.sin(ang), C + 12.5 * math.cos(ang), C + 12.5 * math.sin(ang))

    # ---- the wreck of the Sovereign's flagship, broken against the inside of the wall (north-west)
    WX, WZ = C - 15, C - 14
    for i in range(-9, 10):
        for j in range(-3, 4):
            for k in range(0, 6):
                x, z = WX + i, WZ + j + int(i * 0.25)
                y = WL - 2 + k + int(i * 0.18)
                hull = abs(j) == 3 - (k == 0) or k == 0 or abs(i) == 9
                if hull and rnd.random() < 0.85:
                    g.set(x, y, z, 'minecraft:dark_oak_planks' if rnd.random() < 0.7 else 'minecraft:stripped_dark_oak_log')
                elif not hull:
                    g.set(x, y, z, WATER if y <= WL else AIR, {'level': '0'} if y <= WL else None)
    for y in range(WL + 2, WL + 16):                          # the broken mast, leaning
        g.set(WX + (y - WL) // 4, y, WZ, 'minecraft:dark_oak_log', {'axis': 'y'})
    for x in range(WX - 3, WX + 5):
        g.set(x, WL + 12, WZ, 'minecraft:dark_oak_fence')
    for x in range(WX - 2, WX + 4):
        for y in range(WL + 6, WL + 11):
            if rnd.random() < 0.6:
                g.set(x + (y - WL) // 4, y, WZ + 1, 'minecraft:white_wool')
    g.set(WX + 2, WL, WZ, 'minecraft:chest', {'facing': 'north', 'type': 'single', 'waterlogged': 'true'}, chest_nbt('aurelia:chests/tidewrack_cache'))

    # ---- life on the walls: sea lanterns, hanging kelp-like vines of glow lichen, prismarine spires on the battlements
    for a in range(0, 360, 30):
        ang = math.radians(a + 15)
        x, z = round(C + 28.7 * math.cos(ang)), round(C + 28.7 * math.sin(ang))
        if g.get(x, WL + 6, z) and g.get(x, WL + 6, z)[0] != AIR:
            g.set(x, WL + 7, z, SL)

    # ---- garrison
    for (x, z) in [(C - 3, C + 23), (C + 3, C + 23), (C - 4, K1 + 2), (C + 4, K1 + 2)]:
        g.ground_guard('aurelia:coralclad_juggernaut', x, z, WL + 2, 3)
    for (x, z) in [(C - 6, C + 6), (C + 6, C + 6), (C + 18, C - 21), (C - 21, C + 18)]:
        g.ground_guard('aurelia:tidecaller', x, z, WL + 2, 3)
    for (x, z) in [(C, C + 20), (C + 1, C + 14), (C - 9, C - 9), (C + 9, C - 9), (C - 10, C + 3)]:
        g.ground_guard('aurelia:razorclaw', x, z, WL + 2, 1)
    g.save('tidewrack_citadel')
    return g


# ================================================================================================ RIMEFAST
def rimefast():
    W = L = 65
    H = 58
    C = 32
    G = 12
    rnd = random.Random(505)
    g = Grid(W, H, L)
    SB, CSB, MSB = 'minecraft:stone_bricks', 'minecraft:cracked_stone_bricks', 'minecraft:mossy_stone_bricks'
    DT, PD, CAL, PI = 'minecraft:deepslate_tiles', 'minecraft:polished_deepslate', 'minecraft:calcite', 'minecraft:packed_ice'
    SP, SPL = 'minecraft:spruce_planks', 'minecraft:spruce_log'
    SNOW1 = {'layers': '1'}

    def stone():
        r = rnd.random()
        return CSB if r < 0.15 else (MSB if r < 0.22 else SB)

    # ---- snowfield: snow over stone, the whole compound cleared above ground
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if d > 31.8 and max(abs(x - C), abs(z - C)) > 29:
                continue
            for y in range(0, G):
                g.set(x, y, z, 'minecraft:stone' if y < G - 3 else 'minecraft:dirt')
            g.set(x, G, z, 'minecraft:snow_block')
            for y in range(G + 1, H):
                g.set(x, y, z, AIR)
            if rnd.random() < 0.25:
                g.set(x, G + 1, z, 'minecraft:snow', SNOW1)

    # ---- the curtain wall, four round towers with spruce cone roofs, the south gatehouse
    E = 27
    for x in range(C - E, C + E + 1):
        for z in range(C - E, C + E + 1):
            if max(abs(x - C), abs(z - C)) in (E, E - 1):
                for y in range(G + 1, G + 9):
                    g.set(x, y, z, stone())
                g.set(x, G + 9, z, PI if max(abs(x - C), abs(z - C)) == E else SB)
                if max(abs(x - C), abs(z - C)) == E and (x + z) % 2 == 0:
                    g.set(x, G + 10, z, SB)
                    g.set(x, G + 11, z, 'minecraft:snow', SNOW1)

    def cone(cx, cz, r, y0, height):
        for k in range(height):
            rr = r * (1 - k / height) + 0.3
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                for z in range(int(cz - r) - 1, int(cz + r) + 2):
                    if math.hypot(x - cx, z - cz) <= rr:
                        g.set(x, y0 + k, z, 'minecraft:spruce_planks' if math.hypot(x - cx, z - cz) < rr - 1 else DT)
    for (sx, sz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        tx, tz = C + sx * E, C + sz * E
        for x in range(tx - 4, tx + 5):
            for z in range(tz - 4, tz + 5):
                d = math.hypot(x - tx, z - tz)
                if d <= 4.2:
                    for y in range(G + 1, G + 15):
                        g.set(x, y, z, stone() if d > 3.0 else AIR)
                    g.set(x, G + 7, z, SP if d <= 3.0 else stone())
        cone(tx, tz, 5.0, G + 15, 11)
        g.set(tx, G + 26, tz, 'minecraft:lightning_rod', {'facing': 'up', 'powered': 'false', 'waterlogged': 'false'})
        for (dx, dz) in ((4, 0), (-4, 0), (0, 4), (0, -4)):
            g.set(tx + dx, G + 11, tz + dz, 'minecraft:light_blue_stained_glass')
        lantern(g, tx, G + 6, tz, soul=True, hanging=True)
    for x in range(C - 3, C + 4):                                # gate
        for y in range(G + 1, G + 7):
            for z in (C + E - 1, C + E):
                g.set(x, y, z, AIR)
    for gx in (C - 5, C + 5):
        for x in range(gx - 2, gx + 3):
            for z in range(C + E - 2, C + E + 3):
                for y in range(G + 1, G + 13):
                    g.set(x, y, z, stone())
        cone(gx, C + E, 3.2, G + 13, 7)
        g.set(gx, G + 9, C + E + 2, 'minecraft:soul_lantern', {'hanging': 'false', 'waterlogged': 'false'})
    for x in range(C - 4, C + 5):
        g.set(x, G + 7, C + E, 'minecraft:chiseled_stone_bricks')
        g.set(x, G + 7, C + E - 1, 'minecraft:chiseled_stone_bricks')
    for x in range(C - 2, C + 3):
        g.set(x, G + 6, C + E - 1, 'minecraft:iron_bars')

    # ---- the path from the gate to the nave, lined with soul braziers, frost runes set into it
    NZ1 = C + 6                                                  # nave south wall
    for z in range(NZ1 + 1, C + E):
        for x in range(C - 2, C + 3):
            g.set(x, G, z, 'aurelia:frost_rune' if (z % 6 == 0 and x == C) else (CAL if abs(x - C) < 2 else 'minecraft:polished_andesite'))
            g.set(x, G + 1, z, AIR)
        if z % 5 == 0:
            for bx in (C - 4, C + 4):
                g.set(bx, G + 1, z, SB)
                g.set(bx, G + 2, z, 'minecraft:stone_brick_wall')
                g.set(bx, G + 3, z, 'minecraft:soul_campfire', {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'})

    # ---- the nave: tall walls, buttresses, lancet windows, a steep tiled roof, an apse to the north
    NX0, NX1, NZ0 = C - 10, C + 10, C - 22
    for x in range(NX0, NX1 + 1):
        for z in range(NZ0, NZ1 + 1):
            edge = x in (NX0, NX1) or z in (NZ0, NZ1)
            for y in range(G + 1, G + 15):
                g.set(x, y, z, stone() if edge else AIR)
            g.set(x, G, z, CAL if abs(x - C) <= 1 else (PD if (x + z) % 2 else DT))
    for z in range(NZ0, NZ1 + 1, 4):                              # buttresses
        for x in (NX0 - 1, NX0 - 2, NX1 + 1, NX1 + 2):
            top = G + 11 - (abs(x - C) - 11) * 3
            for y in range(G + 1, top):
                g.set(x, y, z, SB)
            g.set(x, top, z, 'minecraft:stone_brick_slab', slab())
    for z in range(NZ0 + 2, NZ1 - 1, 4):                          # lancet windows
        for x in (NX0, NX1):
            for y in range(G + 4, G + 12):
                g.set(x, y, z, 'minecraft:white_stained_glass' if y < G + 10 else 'minecraft:light_blue_stained_glass')
                g.set(x, y, z + 1, 'minecraft:white_stained_glass' if y < G + 10 else 'minecraft:light_blue_stained_glass')
    for k in range(12):                                          # the roof
        y = G + 15 + k
        for z in range(NZ0 - 1, NZ1 + 2):
            for x in (NX0 - 1 + k, NX1 + 1 - k):
                g.set(x, y, z, 'minecraft:deepslate_tile_stairs', stairs('east' if x < C else 'west'))
            if k < 11:
                for x in range(NX0 + k, NX1 - k + 1):
                    if z in (NZ0 - 1, NZ1 + 1):
                        g.set(x, y, z, stone())
    for z in range(NZ0 - 1, NZ1 + 2):
        g.set(C, G + 27, z, DT)
    for x in range(NX0 + 1, NX1):                                # vaulted ceiling under the roof
        for z in range(NZ0 + 1, NZ1):
            g.set(x, G + 15, z, SP if (z % 4) else SPL)
    # apse: a half-round chapel off the north end, with the portal
    for x in range(C - 8, C + 9):
        for z in range(NZ0 - 9, NZ0 + 1):
            d = math.hypot(x - C, z - NZ0)
            if d <= 8.2:
                for y in range(G + 1, G + 13):
                    g.set(x, y, z, stone() if d > 7.0 else AIR)
                g.set(x, G, z, CAL if d < 3 else PD)
                g.set(x, G + 13, z, DT)
            if d <= 7.0:
                for y in range(G + 13, G + 13 + int(math.sqrt(max(0, 49 - d * d)) * 0.5)):
                    g.set(x, y, z, DT)
    for x in range(C - 6, C + 7):
        for y in range(G + 1, G + 12):
            g.set(x, y, NZ0, AIR)
    for (wx, wz) in [(C - 7, NZ0 - 3), (C + 7, NZ0 - 3), (C - 4, NZ0 - 7), (C + 4, NZ0 - 7)]:
        for y in range(G + 4, G + 10):
            g.set(wx, y, wz, 'minecraft:light_blue_stained_glass')
    WGZ = NZ0 - 6
    for y in range(G + 1, G + 6):
        g.set(C - 2, y, WGZ, 'minecraft:quartz_pillar', {'axis': 'y'})
        g.set(C + 2, y, WGZ, 'minecraft:quartz_pillar', {'axis': 'y'})
    for x in (C - 1, C, C + 1):
        for y in range(G + 1, G + 5):
            g.set(x, y, WGZ - 1, 'minecraft:white_stained_glass')
    g.box(C - 2, G + 6, WGZ, C + 2, G + 6, WGZ, 'minecraft:chiseled_quartz_block')
    g.set(C, G + 1, WGZ, 'aurelia:waygate', {'realm': 'pale', 'active': 'false'})
    for (cx, cz) in [(C - 3, WGZ + 2), (C + 3, WGZ + 2)]:
        g.set(cx, G + 1, cz, 'minecraft:white_candle', {'candles': '4', 'lit': 'true', 'waterlogged': 'false'})
    lectern(g, C + 4, G + 1, NZ0 - 2, 'west', 'The Rimefast Citadel',
            ["The White Silence was asked to keep one thing: the sound of the Sovereign weeping, so the realms would not hear it. "
             "It took that sound, and then it took all the others, to be sure.",
             "The chapel doors are sealed with rime. They will not open while a Rimeguard still keeps the yard.",
             "Four Hush Stones wait in the aisles. Crouch on each one and be perfectly still until it has listened to your silence. "
             "Any step, any blow, and it begins again. The Hushwraiths will scream if they hear you move."])
    # pillars, pews, sculk, and the four Hush Stones in the side aisles
    for z in range(NZ0 + 3, NZ1 - 1, 4):
        for x in (C - 5, C + 5):
            for y in range(G + 1, G + 15):
                g.set(x, y, z, PI if y % 5 else CAL)
    for z in range(NZ0 + 5, NZ1 - 2, 2):
        for x in list(range(C - 4, C - 1)) + list(range(C + 2, C + 5)):
            g.set(x, G + 1, z, 'minecraft:spruce_stairs', stairs('south'))
    stones = [(C - 8, NZ0 + 5), (C + 8, NZ0 + 5), (C - 8, NZ1 - 5), (C + 8, NZ1 - 5)]
    for (hx, hz) in stones:
        for x in range(hx - 2, hx + 3):
            for z in range(hz - 2, hz + 3):
                if (x, z) != (hx, hz) and NX0 < x < NX1 and rnd.random() < 0.7:
                    g.set(x, G, z, 'minecraft:sculk')
                    if rnd.random() < 0.3:
                        g.set(x, G + 1, z, 'minecraft:sculk_vein', {'down': 'true', 'up': 'false', 'north': 'false', 'south': 'false',
                                                                     'east': 'false', 'west': 'false', 'waterlogged': 'false'})
        g.set(hx, G, hz, 'aurelia:hush_stone', {'filled': 'false'})
        g.set(hx, G + 1, hz, AIR)
        for (cx, cz) in [(hx - 1, hz - 1), (hx + 1, hz + 1)]:
            if NX0 < cx < NX1:
                g.set(cx, G + 1, cz, 'minecraft:light_blue_candle', {'candles': '3', 'lit': 'true', 'waterlogged': 'false'})
    for z in range(NZ0 + 2, NZ1, 6):
        lantern(g, C, G + 14, z, soul=True, hanging=True)
        for y in range(G + 13, G + 15):
            g.set(C, y + 1, z, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'}) if y + 1 < G + 15 else None
    # the doors: a pointed arch, sealed with rime
    for x in range(C - 2, C + 3):
        for y in range(G + 1, G + 7 - (abs(x - C) == 2)):
            g.set(x, y, NZ1, 'aurelia:rime_seal')
    for y in range(G + 1, G + 9):
        g.set(C - 3, y, NZ1 + 1, 'minecraft:chiseled_stone_bricks')
        g.set(C + 3, y, NZ1 + 1, 'minecraft:chiseled_stone_bricks')
    g.box(C - 3, G + 9, NZ1 + 1, C + 3, G + 9, NZ1 + 1, 'minecraft:chiseled_stone_bricks')
    g.set(C, G + 11, NZ1 + 1, 'minecraft:light_blue_stained_glass')

    # ---- the belltower, west of the doors: a belfry with an empty frame where the bell was taken
    BX, BZ = C - 17, C + 3
    for x in range(BX - 3, BX + 4):
        for z in range(BZ - 3, BZ + 4):
            edge = abs(x - BX) == 3 or abs(z - BZ) == 3
            for y in range(G + 1, G + 34):
                g.set(x, y, z, stone() if edge else AIR)
            for fl in (G + 10, G + 20):
                if not edge:
                    g.set(x, fl, z, SP)
    for y in range(G + 26, G + 31):                              # belfry arches
        for (dx, dz) in [(0, 3), (0, -3), (3, 0), (-3, 0), (1, 3), (-1, 3), (1, -3), (-1, -3), (3, 1), (3, -1), (-3, 1), (-3, -1)]:
            g.set(BX + dx, y, BZ + dz, AIR)
    for x in range(BX - 2, BX + 3):
        for z in range(BZ - 2, BZ + 3):
            g.set(x, G + 25, z, SP)
    g.box(BX - 2, G + 31, BZ, BX + 2, G + 31, BZ, SPL, {'axis': 'x'})
    for y in range(G + 28, G + 31):
        g.set(BX, y, BZ, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})
    for k in range(7):
        r = 3.5 - k * 0.5
        for x in range(BX - 4, BX + 5):
            for z in range(BZ - 4, BZ + 5):
                if max(abs(x - BX), abs(z - BZ)) <= r + 0.5:
                    g.set(x, G + 34 + k, z, DT)
    for y in range(G + 1, G + 25):
        g.set(BX + 2, y, BZ + 2, 'minecraft:ladder', {'facing': 'north', 'waterlogged': 'false'})
        if y in (G + 10, G + 20):
            g.set(BX + 2, y, BZ + 2, 'minecraft:ladder', {'facing': 'north', 'waterlogged': 'false'})
    g.set(BX + 2, G + 25, BZ + 2, AIR)
    for y in range(G + 1, G + 4):
        g.set(BX + 3, y, BZ, AIR)
    chest(g, BX - 1, G + 26, BZ - 1, 'aurelia:chests/rimefast_cache', 'south')

    # ---- the cloister to the east: an arcade round a frozen fountain, and a refectory
    QX0, QX1, QZ0, QZ1 = C + 13, C + 24, C - 20, C + 2
    for x in range(QX0, QX1 + 1):
        for z in range(QZ0, QZ1 + 1):
            edge = x in (QX0, QX1) or z in (QZ0, QZ1)
            if edge:
                g.set(x, G, z, CAL)
                if (x + z) % 3 == 0:
                    for y in range(G + 1, G + 5):
                        g.set(x, y, z, 'minecraft:stone_brick_wall' if y < G + 4 else SB)
                g.set(x, G + 5, z, 'minecraft:stone_brick_slab', slab())
    fx, fz = (QX0 + QX1) // 2, (QZ0 + QZ1) // 2
    for x in range(fx - 3, fx + 4):
        for z in range(fz - 3, fz + 4):
            d = math.hypot(x - fx, z - fz)
            if d <= 3.2:
                g.set(x, G, z, PI if d > 2.2 else 'minecraft:ice')
                if d > 2.2:
                    g.set(x, G + 1, z, 'minecraft:stone_brick_wall')
    for y in range(G + 1, G + 5):
        g.set(fx, y, fz, PI if y < G + 4 else 'minecraft:blue_ice')
    RX0, RX1, RZ0, RZ1 = C + 12, C + 24, C + 8, C + 22
    for x in range(RX0, RX1 + 1):
        for z in range(RZ0, RZ1 + 1):
            edge = x in (RX0, RX1) or z in (RZ0, RZ1)
            for y in range(G + 1, G + 7):
                g.set(x, y, z, (SPL if (x in (RX0, RX1) and z in (RZ0, RZ1)) else (SP if y > G + 1 else stone())) if edge else AIR)
            g.set(x, G, z, SP)
    for k in range(8):
        for x in range(RX0 - 1, RX1 + 2):
            for z in (RZ0 - 1 + k, RZ1 + 1 - k):
                if RZ0 - 1 + k <= RZ1 + 1 - k:
                    g.set(x, G + 7 + k, z, 'minecraft:spruce_stairs', stairs('south' if z == RZ0 - 1 + k else 'north'))
    for y in range(G + 1, G + 4):
        g.set(RX0, y, RZ0 + 7, AIR)
    for z in range(RZ0 + 2, RZ1 - 1):
        g.set(C + 18, G + 1, z, 'minecraft:spruce_slab', slab('top'))
    chest(g, RX1 - 1, G + 1, RZ1 - 1, 'aurelia:chests/rimefast_cache', 'west')
    g.set(RX0 + 1, G + 1, RZ1 - 1, 'minecraft:campfire', {'facing': 'east', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'})

    # ---- the graveyard, south-west: rows of stones, and two kneeling statues of ice facing the chapel
    for row in range(4):
        for col in range(5):
            x, z = C - 24 + col * 3, C + 11 + row * 3
            if rnd.random() < 0.85:
                g.set(x, G + 1, z, 'minecraft:cobbled_deepslate_wall' if rnd.random() < 0.7 else 'minecraft:stone_brick_wall')
                if rnd.random() < 0.4:
                    g.set(x, G + 2, z, 'minecraft:snow', SNOW1)
    for (kx, kz) in [(C - 20, C + 24), (C - 14, C + 24)]:
        g.box(kx - 1, G + 1, kz, kx + 1, G + 1, kz + 1, PI)
        g.box(kx - 1, G + 2, kz, kx + 1, G + 4, kz, PI)
        g.set(kx, G + 5, kz, 'minecraft:snow_block')
        g.set(kx, G + 4, kz - 1, PI)
    # snowy spruces inside the walls
    for (tx, tz) in [(C - 22, C - 20), (C - 18, C - 8), (C + 22, C - 23), (C - 23, C + 4), (C + 8, C + 20), (C - 6, C + 22)]:
        for y in range(G + 1, G + 8):
            g.set(tx, y, tz, SPL, {'axis': 'y'})
        for k, r in enumerate([3, 3, 2, 2, 1, 1, 0]):
            for x in range(tx - r, tx + r + 1):
                for z in range(tz - r, tz + r + 1):
                    if abs(x - tx) + abs(z - tz) <= r + 1 and g.free(x, G + 4 + k, z):
                        g.set(x, G + 4 + k, z, 'minecraft:spruce_leaves', {'persistent': 'true', 'distance': '7', 'waterlogged': 'false'})
        g.set(tx, G + 11, tz, 'minecraft:snow', SNOW1)

    # ---- garrison
    for (x, z) in [(C - 3, NZ1 + 3), (C + 3, NZ1 + 3), (C - 4, C + 21), (C + 4, C + 21)]:
        g.ground_guard('aurelia:rimeguard', x, z, G + 1, 3)
    for (x, z) in [(C - 2, NZ0 + 9), (C + 2, NZ1 - 9), (fx - 4, fz + 6), (fx + 3, fz - 7), (C - 18, C + 16)]:
        g.ground_guard('aurelia:hushwraith', x, z, G + 1, 3)
    for (x, z) in [(C - 20, C + 13), (C - 12, C + 19), (C + 18, C - 12), (C + 10, C - 24)]:
        g.ground_guard('aurelia:rimefang', x, z, G + 1, 2)
    g.save('rimefast_citadel')
    return g


if __name__ == '__main__':
    tidewrack()
    rimefast()
