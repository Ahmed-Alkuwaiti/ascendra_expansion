"""The lieutenants' lairs (lieutenants.py): one colossal structure per lieutenant, placed by LairBuilder.java a hundred and fifty
blocks out from each realm's landing pad. Every lair is 81 x 81 and built on one of five plans:

  arena   a colosseum: tiered walls round a sanded fighting floor, eight spiked towers, a hooded colossus over the far rim
  temple  a cathedral on a raised plinth: a towering facade with a rose window, a pillared nave, an apse with a dome
  spire   a tower sixty blocks tall, a spiral ramp round it and a battlement platform on top, held by flying buttresses
  pit     a plaza round a pit sixteen deep, its walls bristling with spikes, a ramp spiralling down, bridges across it
  maw     a hill with a giant horned skull for a face; walk in through the teeth to a courtyard open to the sky

and on one of four grounds: solid (sunk into the terrain), floating (a rock island hanging under it), cavern (a floor slab;
LairBuilder carves the cavern) or stilts (the Drowned Expanse: piers down into the sea). At the heart of each is the Lair Seal
(crouch and touch it to call the lieutenant out), with a beacon beside it whose beam marks the lair from afar.

Writes data/aurelia/structures/lair_<id>.nbt, the loot tables and world/LairLayout.java (each lair's size, floor height, seal
and beacon), and returns each lair's entrance for the route check (check_lairs.py).
"""
import math
import random

import paths
from gen_act3_citadels import AIR, Grid, chest, lantern, chain, statue
from lieutenants import LIEUTENANTS, of_realm

M = 'minecraft:'
W = L = 81
C = 40
GROUND = {'grove': 'solid', 'skyreach': 'float', 'hollow': 'cavern', 'drowned': 'stilts', 'pale': 'solid', 'scarlet': 'solid',
          'clockwork': 'float', 'mycelial': 'cavern', 'last': 'float'}
PAL = {
    'grove': dict(stone='mossy_stone_bricks', stone2='deepslate_bricks', brick='mossy_cobblestone', trim='dark_oak_planks', pillar='dark_oak_log',
                  floor='moss_block', floor2='mossy_stone_bricks', glow='shroomlight', glass='lime', spike='dark_oak_log', tip='pointed_dripstone',
                  soil_top='grass_block', soil='dirt', under='stone', fluid=None, fire='campfire', bars='dark_oak_fence', roof='deepslate_tiles'),
    'skyreach': dict(stone='calcite', stone2='polished_deepslate', brick='quartz_bricks', trim='smooth_quartz', pillar='quartz_pillar',
                     floor='polished_diorite', floor2='calcite', glow='sea_lantern', glass='light_blue', spike='polished_deepslate', tip='lightning_rod',
                     soil_top='grass_block', soil='dirt', under='andesite', fluid=None, fire='soul_campfire', bars='iron_bars', roof='polished_deepslate'),
    'hollow': dict(stone='polished_blackstone_bricks', stone2='blackstone', brick='cracked_polished_blackstone_bricks', trim='gilded_blackstone',
                   pillar='basalt', floor='polished_blackstone', floor2='magma_block', glow='shroomlight', glass='orange', spike='blackstone',
                   tip='pointed_dripstone', soil_top='blackstone', soil='blackstone', under='basalt', fluid='lava', fire='soul_campfire',
                   bars='iron_bars', roof='blackstone'),
    'drowned': dict(stone='dark_prismarine', stone2='prismarine_bricks', brick='prismarine', trim='prismarine_bricks', pillar='dark_prismarine',
                    floor='prismarine_bricks', floor2='dark_prismarine', glow='sea_lantern', glass='cyan', spike='dark_prismarine', tip='pointed_dripstone',
                    soil_top='sand', soil='sandstone', under='prismarine', fluid='water', fire='soul_campfire', bars='iron_bars', roof='dark_prismarine'),
    'pale': dict(stone='packed_ice', stone2='deepslate_tiles', brick='blue_ice', trim='polished_deepslate', pillar='packed_ice', floor='snow_block',
                 floor2='packed_ice', glow='sea_lantern', glass='white', spike='packed_ice', tip='pointed_dripstone', soil_top='snow_block',
                 soil='packed_ice', under='stone', fluid=None, fire='soul_campfire', bars='iron_bars', roof='deepslate_tiles'),
    'scarlet': dict(stone='cut_red_sandstone', stone2='smooth_red_sandstone', brick='chiseled_red_sandstone', trim='gold_block', pillar='cut_red_sandstone',
                    floor='red_terracotta', floor2='orange_terracotta', glow='shroomlight', glass='red', spike='red_terracotta', tip='pointed_dripstone',
                    soil_top='red_sand', soil='red_sandstone', under='red_sandstone', fluid='lava', fire='campfire', bars='iron_bars', roof='red_terracotta'),
    'clockwork': dict(stone='polished_blackstone_bricks', stone2='deepslate_tiles', brick='waxed_oxidized_cut_copper', trim='gold_block',
                      pillar='polished_basalt', floor='polished_blackstone', floor2='waxed_cut_copper', glow='ochre_froglight', glass='yellow',
                      spike='polished_blackstone', tip='lightning_rod', soil_top='tuff', soil='tuff', under='deepslate', fluid=None, fire='soul_campfire',
                      bars='iron_bars', roof='waxed_oxidized_cut_copper'),
    'mycelial': dict(stone='mushroom_stem', stone2='polished_deepslate', brick='brown_mushroom_block', trim='bone_block', pillar='mushroom_stem',
                     floor='mycelium', floor2='sculk', glow='shroomlight', glass='magenta', spike='bone_block', tip='pointed_dripstone', soil_top='mycelium',
                     soil='dirt', under='stone', fluid=None, fire='soul_campfire', bars='iron_bars', roof='red_mushroom_block'),
    'last': dict(stone='calcite', stone2='polished_blackstone_bricks', brick='polished_blackstone', trim='gold_block', pillar='quartz_pillar',
                 floor='calcite', floor2='polished_blackstone', glow='pearlescent_froglight', glass='purple', spike='polished_blackstone', tip='end_rod',
                 soil_top='calcite', soil='smooth_basalt', under='blackstone', fluid=None, fire='soul_campfire', bars='iron_bars', roof='polished_blackstone'),
}
FLOOR = {'solid': 14, 'float': 30, 'cavern': 3, 'stilts': 26}        # template y of the walking floor, by ground


def B(name):
    return name if ':' in name else M + name


class Lair:
    def __init__(self, lt, H):
        self.lt = lt
        self.realm = lt['realm']
        self.p = PAL[self.realm]
        self.ground = GROUND[self.realm]
        self.F = FLOOR[self.ground]
        self.g = Grid(W, H, L)
        self.rnd = random.Random(sum(map(ord, lt['id'])))
        self.seal = self.beacon = None
        self.entrance = (C, self.F, L - 2)

    # -------------------------------------------------------------------------------------------- materials
    def b(self, key):
        return B(self.p[key])

    def wall(self, x, y, z):
        r = self.rnd.random()
        return self.b('stone') if r < 0.62 else (self.b('stone2') if r < 0.84 else self.b('brick'))

    def floor(self, x, y, z):
        return self.b('floor') if (x // 3 + z // 3) % 2 else self.b('floor2')

    def set(self, x, y, z, name, props=None):
        self.g.set(x, y, z, B(name), props)

    # -------------------------------------------------------------------------------------------- the ground
    def foundation(self, r=39, pit=None):
        """Under the floor: sunk ground, a floating island, a cavern slab or piers into the sea. pit=(radius, depth) keeps a pit open."""
        F = self.F
        for x in range(W):
            for z in range(L):
                d = math.hypot(x - C, z - C)
                if d > r:
                    continue
                if self.ground == 'solid':
                    depth = F if d < r - 6 else int(4 + (r - d) * 1.6)
                    for y in range(max(0, F - depth), F):
                        self.set(x, y, z, self.b('soil_top') if y == F - 1 else (self.b('soil') if y > F - 4 else self.b('under')))
                elif self.ground == 'float':
                    hang = int((1 - (d / r) ** 1.4) * (F - 2) * (0.75 + 0.25 * math.sin(x * 0.7) * math.cos(z * 0.6))) + 3
                    for y in range(max(0, F - hang), F):
                        k = F - y
                        self.set(x, y, z, self.b('soil_top') if k == 1 else (self.b('soil') if k < 4 else (
                            self.b('under') if self.rnd.random() > 0.04 else B('deepslate_coal_ore'))))
                elif self.ground == 'cavern':
                    for y in range(0, F):
                        self.set(x, y, z, self.b('stone2') if y < F - 1 else self.b('floor'))
                else:                                                # stilts: a deck on piers into the sea
                    self.set(x, F - 1, z, self.b('floor2'))
                    self.set(x, F - 2, z, self.b('stone'))
                    if (x - C) % 6 == 0 and (z - C) % 6 == 0:
                        for y in range(0, F - 2):
                            self.set(x, y, z, self.b('pillar') if (y + x) % 7 else B('sea_lantern'))
        if pit:
            pr, pd = pit
            for x in range(W):
                for z in range(L):
                    d = math.hypot(x - C, z - C)
                    if d <= pr + 4:
                        for y in range(max(0, F - pd - 4), F):
                            self.set(x, y, z, self.wall(x, y, z) if d > pr else AIR)
                        if d <= pr:
                            for y in range(F - pd - 4, F - pd):
                                self.set(x, y, z, self.b('stone2'))
                            self.set(x, F - pd - 1, z, self.floor(x, F - pd - 1, z))

    def clear(self, cx, cz, r, y0, y1):
        for x in range(int(cx - r), int(cx + r) + 1):
            for z in range(int(cz - r), int(cz + r) + 1):
                if math.hypot(x - cx, z - cz) <= r:
                    for y in range(y0, y1):
                        if 0 <= x < W and 0 <= z < L:
                            self.g.set(x, y, z, AIR)

    # -------------------------------------------------------------------------------------------- pieces
    def spike(self, x, y, z, h, block=None, tip=True):
        """A tapering spike: 3 x 3, then 2 x 2, then a single column, finished with the realm's point."""
        blk = block or self.b('spike')
        for k in range(h):
            t = k / max(1, h)
            w = 1 if t < 0.35 else (0 if t < 0.7 else -1)
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    if w == 1 or (w == 0 and dx >= 0 and dz >= 0) or (w == -1 and dx == 0 and dz == 0):
                        self.set(x + dx, y + k, z + dz, blk)
        if tip:
            t = self.p['tip']
            if t == 'pointed_dripstone':
                self.set(x, y + h, z, t, {'vertical_direction': 'up', 'thickness': 'frustum', 'waterlogged': 'false'})
                self.set(x, y + h + 1, z, t, {'vertical_direction': 'up', 'thickness': 'tip', 'waterlogged': 'false'})
            elif t in ('lightning_rod', 'end_rod'):
                self.set(x, y + h, z, t, {'facing': 'up'} if t == 'end_rod' else {'facing': 'up', 'powered': 'false', 'waterlogged': 'false'})

    def brazier(self, x, y, z, h=3):
        for k in range(h):
            self.set(x, y + k, z, self.b('trim') if k == h - 1 else self.b('stone2'))
        self.set(x, y + h, z, self.p['fire'], {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'})

    def tower(self, x, z, r, y0, h, roof=True, windows=True):
        """A round tower with a battlement, arrow slits glowing, and a steep spiked roof."""
        for yy in range(y0, y0 + h):
            for dx in range(-r - 1, r + 2):
                for dz in range(-r - 1, r + 2):
                    d = math.hypot(dx, dz)
                    if d <= r:
                        edge = d > r - 1.2
                        if edge and windows and yy % 7 == 4 and (dx == 0 or dz == 0) and yy > y0 + 4:
                            self.set(x + dx, yy, z + dz, self.p['glass'] + '_stained_glass')
                        else:
                            self.set(x + dx, yy, z + dz, (self.b('pillar') if (dx == 0 or dz == 0) and edge and yy % 9 == 0 else self.wall(x, yy, z)) if edge else self.b('stone2'))
        top = y0 + h
        for dx in range(-r - 1, r + 2):                                # machicolation ring and merlons
            for dz in range(-r - 1, r + 2):
                d = math.hypot(dx, dz)
                if d <= r + 1:
                    self.set(x + dx, top, z + dz, self.b('trim'))
                    if d > r and (dx + dz) % 2 == 0:
                        self.set(x + dx, top + 1, z + dz, self.b('stone'))
        if roof:
            rh = r * 3
            for k in range(rh):
                rr = (r + 0.5) * (1 - k / rh)
                for dx in range(-r - 1, r + 2):
                    for dz in range(-r - 1, r + 2):
                        if math.hypot(dx, dz) <= rr:
                            self.set(x + dx, top + 2 + k, z + dz, self.b('roof'))
            self.spike(x, top + 2 + rh, z, 5, tip=True)
            for sx, sz in ((1, 0), (-1, 0), (0, 1), (0, -1)):            # four horns out of the roof
                for k in range(5):
                    self.set(x + sx * (r + 1 + k // 2), top + 3 + k, z + sz * (r + 1 + k // 2), self.b('spike'))
        else:
            self.brazier(x, top + 1, z, 2)

    def seal_and_beacon(self, x, y, z, bx, by, bz):
        """The Lair Seal on a dais ringed with braziers; the beacon on a one-tier pyramid, its beam tinted the realm's colour."""
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                self.set(x + dx, y - 1, z + dz, self.b('trim') if max(abs(dx), abs(dz)) == 3 else self.b('stone2'))
        for dx, dz in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
            self.brazier(x + dx, y, z + dz, 2)
        slot = [l['id'] for l in of_realm(self.realm)].index(self.lt['id'])
        self.set(x, y, z, 'aurelia:lair_seal', {'slot': str(slot)})
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                self.set(bx + dx, by - 1, bz + dz, 'iron_block')
        self.set(bx, by, bz, 'beacon')
        self.set(bx, by + 1, bz, self.p['glass'] + '_stained_glass')
        for yy in range(by + 2, min(self.g.H, by + 90)):               # nothing over the beam
            self.g.set(bx, yy, bz, AIR)
        self.seal = (x, y, z)
        self.beacon = (bx, by, bz)

    def loot(self, spots):
        for x, y, z, facing in spots:
            chest(self.g, x, y, z, f'aurelia:chests/lair_{self.realm}', facing)

    def skull_post(self, x, y, z, h=3):
        for k in range(h):
            self.set(x, y + k, z, self.p['bars'] if self.p['bars'] != 'iron_bars' else 'polished_blackstone_wall' if self.realm in ('hollow', 'clockwork', 'last') else 'cobblestone_wall')
        self.set(x, y + h, z, 'skeleton_skull', {'rotation': str(self.rnd.randint(0, 15))})

    # ============================================================================================ the five plans
    def arena(self):
        F = self.F
        self.foundation(39)
        self.clear(C, C, 38, F, F + 40)
        for x in range(W):                                              # the fighting floor, sand-strewn, stained
            for z in range(L):
                d = math.hypot(x - C, z - C)
                if d <= 22:
                    self.set(x, F - 1, z, self.floor(x, F - 1, z) if self.rnd.random() > 0.08 else B('coarse_dirt' if self.realm != 'drowned' else 'sand'))
                elif d <= 36:                                          # seating tiers climbing to the outer wall
                    top = F + int((d - 22) * 1.3)
                    for y in range(F - 1, top + 1):
                        self.set(x, y, z, self.wall(x, y, z) if y < top else (self.b('trim') if int(d) % 3 == 0 else self.b('stone')))
                elif d <= 38:
                    for y in range(F - 1, F + 24):
                        self.set(x, y, z, self.wall(x, y, z))
                    ang = math.atan2(z - C, x - C)
                    if int(ang * 20) % 2 == 0:
                        self.set(x, F + 24, z, self.b('stone'))
                        if int(ang * 10) % 4 == 0:
                            self.set(x, F + 25, z, self.p['bars'] if 'fence' in self.p['bars'] else 'iron_bars')
        for x in range(C - 4, C + 5):                                   # the gate tunnel through the south stands
            for z in range(C + 21, L):
                for y in range(F, F + 10):
                    self.g.set(x, y, z, AIR)
                self.set(x, F - 1, z, self.floor(x, F - 1, z))
            for y in range(F + 10, F + 13):
                for z in range(C + 21, C + 40):
                    self.set(x, y, z, self.b('stone2'))
        for x in range(C - 4, C + 5, 2):                                # a raised portcullis
            for y in range(F + 7, F + 10):
                self.set(x, y, C + 37, 'iron_bars')
        for k in range(8):                                              # eight spiked towers round the rim
            a = math.pi / 2 + (k + 0.5) * math.pi / 4
            tx, tz = int(C + math.cos(a) * 36), int(C + math.sin(a) * 36)
            self.tower(tx, tz, 4, F - 1, 34)
        statue(self.g, C, F + 12, C - 31, 's', 30, self.b('stone2'), self.b('trim'), B('black_concrete'), self.b('glow'), held='orb', rnd=self.rnd)
        for k in range(10):                                             # braziers round the floor's edge, spikes between
            a = k * math.pi / 5 + 0.2
            x, z = int(C + math.cos(a) * 20), int(C + math.sin(a) * 20)
            if abs(x - C) <= 5 and z > C:
                continue
            self.brazier(x, F, z, 2)
            self.spike(int(C + math.cos(a + 0.3) * 19), F, int(C + math.sin(a + 0.3) * 19), 6)
        for x in range(C - 7, C + 8):                                   # chains of the fallen hung from the gate stands
            if x % 3 == 0:
                chain(self.g, x, F + 6, F + 9, C + 22)
        self.seal_and_beacon(C, F, C, C, F, C + 6)
        self.loot([(C - 6, F, C - 18, 'south'), (C + 6, F, C - 18, 'south')])
        for z in range(C + 40, L):
            for x in range(C - 4, C + 5):
                self.set(x, F - 1, z, self.floor(x, F - 1, z))

    def temple(self):
        F = self.F
        self.foundation(39)
        P = F + 6                                                        # the plinth's top
        self.clear(C, C, 38, F, F + 70)
        for x in range(C - 20, C + 21):
            for z in range(C - 38, C + 30):
                for y in range(F - 1, P):
                    self.set(x, y, z, self.wall(x, y, z) if y < P - 1 else self.floor(x, y, z))
        for z in range(C + 30, C + 39):                                 # the grand stair
            top = P - 1 - (z - C - 30) * 6 // 9
            for x in range(C - 9, C + 10):
                for y in range(F - 1, top + 1):
                    self.set(x, y, z, self.b('trim') if y == top else self.wall(x, y, z))
        for x in (C - 11, C + 11):
            for z in range(C + 30, C + 39, 4):
                self.brazier(x, F, z, 4)
        H = P + 32
        for z in range(C - 26, C + 27):                                 # nave walls and buttresses
            for x in (C - 16, C - 15, C + 15, C + 16):
                for y in range(P, H):
                    win = (z % 8 in (3, 4)) and P + 8 <= y <= P + 22
                    self.set(x, y, z, self.p['glass'] + '_stained_glass' if win else self.wall(x, y, z))
            if z % 8 == 0:
                for sx in (-1, 1):
                    for k in range(6):
                        for y in range(P, H - k * 4):
                            self.set(C + sx * (17 + k), y, z, self.b('stone2'))
                    self.spike(C + sx * 22, P + 6, z, 7)
        for k in range(0, 13):                                          # the roof: a steep gable
            for z in range(C - 27, C + 28):
                for x in range(C - 17 + k, C + 18 - k):
                    if x in (C - 17 + k, C + 17 - k):
                        self.set(x, H + k, z, self.b('roof'))
        for z in range(C - 26, C + 26, 6):                              # columns down the nave
            for x in (C - 9, C + 9):
                for y in range(P, H):
                    self.set(x, y, z, self.b('pillar'))
                    if y in (P, H - 1):
                        for dx in (-1, 0, 1):
                            for dz in (-1, 0, 1):
                                self.set(x + dx, y, z + dz, self.b('trim'))
                lantern(self.g, x, H - 4, z + 1, soul=self.p['fire'] == 'soul_campfire', hanging=False)
        for x in range(C - 14, C + 15):                                 # a carpet of the realm's floor down the nave
            pass
        for z in range(C - 26, C + 27):
            for x in range(C - 2, C + 3):
                self.set(x, P - 1, z, self.b('trim') if x in (C - 2, C + 2) else self.b('floor2'))
        for z in range(C + 26, C + 29):                                 # the facade, with its doorway and rose window
            for x in range(C - 20, C + 21):
                for y in range(P, H + 14):
                    if abs(x - C) <= 4 and y < P + 15 - max(0, abs(x - C) - 2) * 2:
                        self.g.set(x, y, z, AIR)
                    elif math.hypot(x - C, y - (P + 24)) <= 7 and z == C + 27:
                        self.set(x, y, z, self.p['glass'] + '_stained_glass' if math.hypot(x - C, y - (P + 24)) < 6.2 else self.b('trim'))
                    elif y < H + 14 - abs(x - C) // 2:
                        self.set(x, y, z, self.wall(x, y, z))
        for sx in (-1, 1):                                              # bell towers either side of the facade
            self.tower(C + sx * 17, C + 27, 5, P, 44)
        for z in range(C - 40, C - 26):                                 # the apse: a half-round chancel under a dome
            for x in range(C - 16, C + 17):
                d = math.hypot(x - C, z - (C - 26))
                if d > 16:
                    continue
                for y in range(P, H + 8):
                    if d > 14.5:
                        self.set(x, y, z, self.wall(x, y, z))
                self.set(x, P - 1, z, self.floor(x, P - 1, z))
        for k in range(16):
            rr = 16 * math.cos(k / 16 * math.pi / 2)
            for x in range(C - 17, C + 18):
                for z in range(C - 43, C - 25):
                    d = math.hypot(x - C, z - (C - 26))
                    if rr - 1.3 <= d <= rr and z <= C - 26:
                        self.set(x, H + 8 + k, z, self.b('roof'))
        top = H + 8 + 16
        for x in range(C - 2, C + 3):
            for z in range(C - 28, C - 23):
                for y in range(H + 8, top):
                    if math.hypot(x - C, z - (C - 26)) <= 2.2:
                        self.g.set(x, y, z, AIR)
        statue(self.g, C, P, C - 39, 's', 28, self.b('stone2'), self.b('trim'), B('black_concrete'), self.b('glow'), held='hourglass', rnd=self.rnd)
        self.seal_and_beacon(C, P, C - 22, C, P, C - 26)
        self.loot([(C - 13, P, C - 20, 'east'), (C + 13, P, C - 20, 'west')])
        self.entrance = (C, F, L - 2)

    def spire(self):
        F = self.F
        self.foundation(34)
        T = F + 50                                                      # the battlement platform's floor
        self.clear(C, C, 38, F, min(self.g.H, T + 30))
        for x in range(W):
            for z in range(L):
                if math.hypot(x - C, z - C) <= 33:
                    self.set(x, F - 1, z, self.floor(x, F - 1, z))
        for y in range(F, T):                                           # the tower: a solid core, fluted
            for x in range(C - 12, C + 13):
                for z in range(C - 12, C + 13):
                    d = math.hypot(x - C, z - C)
                    if d <= 10.5 or (d <= 12 and int(math.atan2(z - C, x - C) * 6) % 2 == 0):
                        self.set(x, y, z, self.wall(x, y, z) if d > 9 else self.b('stone2'))
        for x in range(W):                                              # the platform, battlemented
            for z in range(L):
                d = math.hypot(x - C, z - C)
                if d <= 19:
                    for y in range(T - 3, T):
                        self.set(x, y, z, self.floor(x, y, z) if y == T - 1 else self.b('stone2'))
                    if d > 18:
                        self.set(x, T, z, self.b('stone'))
                        if (x + z) % 2 == 0:
                            self.set(x, T + 1, z, self.b('stone'))
        for k in range(4):                                              # four spiked turrets on the rim
            a = k * math.pi / 2 + math.pi / 4
            self.tower(int(C + math.cos(a) * 17), int(C + math.sin(a) * 17), 3, T, 10)
        for k in range(6):                                              # flying buttresses down to pylons
            a = k * math.pi / 3
            px, pz = C + math.cos(a) * 30, C + math.sin(a) * 30
            for y in range(F, F + 20):
                for dx in range(-1, 2):
                    for dz in range(-1, 2):
                        self.set(int(px) + dx, y, int(pz) + dz, self.b('stone2'))
            self.spike(int(px), F + 20, int(pz), 8)
            for s in range(40):
                t = s / 39
                x = C + math.cos(a) * (12 + 18 * t)
                z = C + math.sin(a) * (12 + 18 * t)
                y = T - 8 - (T - 8 - (F + 20)) * t ** 1.4
                self.set(int(x), int(y), int(z), self.b('stone'))
                self.set(int(x), int(y) - 1, int(z), self.b('stone2'))
        n = 520                                                          # the spiral ramp, laid last: it cuts its own way up through the platform
        for i in range(n):
            t = i / n
            ang = math.pi / 2 + t * math.pi * 2 * 1.65
            y = F + int(t * (T - F))
            for rr in (13, 14, 15, 16):
                x, z = int(round(C + math.cos(ang) * rr)), int(round(C + math.sin(ang) * rr))
                self.set(x, y - 1, z, self.b('trim') if rr == 16 else self.b('floor2'))
                for k in range(0, 4):
                    self.g.set(x, y + k, z, AIR)
            x, z = int(round(C + math.cos(ang) * 17)), int(round(C + math.sin(ang) * 17))
            self.set(x, y, z, self.b('stone'))
            if i % 26 == 0:
                self.spike(int(round(C + math.cos(ang) * 19)), y - 2, int(round(C + math.sin(ang) * 19)), 5)
        self.seal_and_beacon(C, T, C, C, T, C + 7)
        self.loot([(C - 10, T, C - 10, 'south'), (C + 10, T, C - 10, 'south')])
        self.entrance = (C, F, L - 8)

    def pit(self):
        F = self.F
        D = 16
        if self.ground in ('solid', 'cavern', 'stilts'):
            self.F = F = max(F, D + 6)
        self.foundation(39, pit=(20, D))
        self.clear(C, C, 38, F, F + 30)
        for x in range(W):
            for z in range(L):
                d = math.hypot(x - C, z - C)
                if 21 < d <= 38:
                    self.set(x, F - 1, z, self.floor(x, F - 1, z))
        n = 420                                                          # the ramp spiralling down the pit wall
        for i in range(n):
            t = i / n
            ang = math.pi / 2 + t * math.pi * 2 * 1.2
            y = F - 1 - int(t * D)
            for rr in (17, 18, 19, 20):
                x, z = int(round(C + math.cos(ang) * rr)), int(round(C + math.sin(ang) * rr))
                for yy in range(F - D - 1, y):
                    self.set(x, yy, z, self.b('stone2'))
                self.set(x, y, z, self.b('trim') if rr == 17 else self.b('floor2'))
                for k in range(1, 5):
                    self.g.set(x, y + k, z, AIR)
        for k in range(28):                                             # spikes thrust out of the pit wall
            a = k * math.pi * 2 / 28
            y = F - 4 - (k % 4) * 3
            for s in range(5):
                x, z = int(round(C + math.cos(a) * (21 - s))), int(round(C + math.sin(a) * (21 - s)))
                if math.hypot(x - C, z - C) < 16.5:
                    self.set(x, y, z, self.b('spike') if s < 4 else self.p['tip'] if self.p['tip'] != 'pointed_dripstone' else self.b('spike'))
        for k in range(16):                                             # the rim: jagged teeth round the pit
            a = k * math.pi / 8
            if abs(math.cos(a)) < 0.3 and math.sin(a) > 0:
                continue
            self.spike(int(C + math.cos(a) * 24), F, int(C + math.sin(a) * 24), 6 + (k % 3) * 3)
        for k in range(6):                                              # six colossal arches over the pit
            a = k * math.pi / 3 + 0.3
            for s in range(60):
                t = s / 59
                rr = 26 - t * 26
                y = F + int(math.sin(t * math.pi) * 18)
                x, z = int(C + math.cos(a) * rr), int(C + math.sin(a) * rr)
                if t > 0.5:
                    break
                for dy in (0, 1):
                    self.set(x, y + dy, z, self.b('stone2'))
            self.spike(int(C + math.cos(a) * 13), F + 17, int(C + math.sin(a) * 13), 4)
        for x in range(C - 22, C + 23):                                 # a narrow bridge east to west, broken in the middle
            if abs(x - C) > 3:
                self.set(x, F - 1, C, self.b('trim'))
                if x % 4 == 0:
                    self.skull_post(x, F, C - 1 if x % 8 else C + 1, 2)
        if self.p['fluid']:
            for k in range(6):
                a = k * math.pi / 3 + 0.5
                x, z = int(C + math.cos(a) * 13), int(C + math.sin(a) * 13)
                for dx in range(-1, 2):
                    for dz in range(-1, 2):
                        self.set(x + dx, F - D - 1, z + dz, self.p['fluid'])
                        self.set(x + dx, F - D - 2, z + dz, self.b('stone2'))
        for k in range(8):
            a = k * math.pi / 4
            self.brazier(int(C + math.cos(a) * 30), F, int(C + math.sin(a) * 30), 3)
            self.tower(int(C + math.cos(a + 0.4) * 35), int(C + math.sin(a + 0.4) * 35), 3, F - 1, 18) if k % 2 == 0 else None
        Fb = F - D
        self.seal_and_beacon(C, Fb, C, C, Fb, C + 6)
        self.loot([(C - 7, Fb, C - 12, 'south'), (C + 7, Fb, C - 12, 'south')])
        self.entrance = (C, F, L - 3)

    def maw(self):
        F = self.F
        self.foundation(39)
        self.clear(C, C, 38, F, F + 56)
        # the hill: a great mound over the north half
        for x in range(W):
            for z in range(L):
                dx, dz = (x - C) / 38, (z - (C - 6)) / 32
                r2 = dx * dx + dz * dz
                if r2 > 1:
                    continue
                h = int(34 * math.sqrt(1 - r2) * (0.8 + 0.2 * math.sin(x * 0.4) * math.cos(z * 0.3)))
                for y in range(F - 1, F + h):
                    self.set(x, y, z, self.b('stone2') if self.rnd.random() < 0.7 else self.b('under'))
        CZ = C - 8                                                      # the courtyard, open to the sky
        for x in range(W):
            for z in range(L):
                if math.hypot(x - C, z - CZ) <= 16:
                    for y in range(F, F + 60):
                        self.g.set(x, y, z, AIR)
                    self.set(x, F - 1, z, self.floor(x, F - 1, z))
                    if math.hypot(x - C, z - CZ) > 15:
                        for y in range(F, F + 14):
                            self.set(x, y, z, self.b('stone2'))
        for x in range(C - 4, C + 5):                                   # the throat: from the mouth to the courtyard
            for z in range(CZ + 14, C + 26):
                for y in range(F, F + 9):
                    self.g.set(x, y, z, AIR)
                self.set(x, F - 1, z, self.floor(x, F - 1, z))
        # the skull, built out of the hill's south face
        SZ = C + 22
        for x in range(C - 21, C + 22):
            for y in range(F, F + 44):
                for z in range(SZ - 8, SZ + 4):
                    u, v = (x - C) / 21, (y - (F + 23)) / 21
                    dome = u * u + v * v <= 1 and y >= F + 12
                    jaw = abs(x - C) <= 14 and F <= y < F + 13 and z >= SZ - 3
                    if dome or jaw:
                        self.set(x, y, z, B('bone_block') if self.realm not in ('hollow', 'clockwork', 'last') or (x + y) % 5 else self.b('stone2'))
        for sx in (-1, 1):                                              # sockets with burning eyes
            ex = C + sx * 9
            for x in range(ex - 5, ex + 6):
                for y in range(F + 21, F + 32):
                    if math.hypot(x - ex, (y - (F + 26)) * 1.2) <= 4.6:
                        for z in range(SZ - 1, SZ + 4):
                            self.set(x, y, z, B('black_concrete') if z < SZ + 3 else AIR)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    self.set(ex + dx, F + 26 + dy, SZ + 2, self.b('glow') if abs(dx) + abs(dy) < 2 else B('black_concrete'))
            for k in range(30):                                         # horns curling out and up
                t = k / 29
                hx = C + sx * (19 + t * 14)
                hy = F + 32 + math.sin(t * math.pi * 0.9) * 28
                hz = SZ - 3 - t * 8
                rr = 4.2 * (1 - t) + 0.7
                for x in range(int(hx - rr), int(hx + rr) + 1):
                    for y in range(int(hy - rr), int(hy + rr) + 1):
                        for z in range(int(hz - rr), int(hz + rr) + 1):
                            if math.dist((x, y, z), (hx, hy, hz)) <= rr:
                                self.set(x, y, z, self.b('spike') if t < 0.8 else self.b('trim'))
        for x in range(C - 3, C + 4):                                   # the nose
            for y in range(F + 15, F + 21):
                if abs(x - C) <= (y - F - 15) * 0.6 + 0.5:
                    for z in range(SZ + 1, SZ + 4):
                        self.set(x, y, z, B('black_concrete') if z < SZ + 3 else AIR)
        for x in range(C - 6, C + 7):                                   # the mouth: the way in, between teeth
            for y in range(F, F + 12):
                for z in range(SZ - 8, SZ + 4):
                    self.g.set(x, y, z, AIR)
        for x in range(C - 6, C + 7, 2):                                # fangs down from the upper jaw, tusks up from the lower
            for k in range(4 if x % 4 == 0 else 3):
                self.set(x, F + 11 - k, SZ + 2, B('bone_block'))
            if abs(x - C) >= 4:
                self.set(x, F, SZ + 2, B('bone_block'))
                self.set(x, F + 1, SZ + 2, B('bone_block'))
        for z in range(SZ + 4, L):                                      # the approach, lined with skull posts and braziers
            for x in range(C - 4, C + 5):
                self.set(x, F - 1, z, self.floor(x, F - 1, z))
            if z % 4 == 0:
                self.skull_post(C - 6, F, z, 3)
                self.skull_post(C + 6, F, z, 3)
            if z % 8 == 2:
                self.brazier(C - 8, F, z, 3)
                self.brazier(C + 8, F, z, 3)
        for k in range(10):                                             # spike field either side
            for sx in (-1, 1):
                self.spike(C + sx * (13 + (k % 3) * 6), F, SZ + 6 + (k // 3) * 4, 5 + (k % 4) * 2)
        self.seal_and_beacon(C, F, CZ, C, F, CZ + 6)
        self.loot([(C - 11, F, CZ - 6, 'east'), (C + 11, F, CZ - 6, 'west')])
        self.entrance = (C, F, L - 2)

    def build(self):
        getattr(self, self.lt['lair'])()
        if self.ground == 'cavern':                                     # the cavern ceiling comes from LairBuilder's carve: no roofing here
            pass
        return self


HEIGHT = {'arena': 90, 'temple': 100, 'spire': 110, 'pit': 80, 'maw': 100}


def loot_tables():
    import json
    import os
    from kit_data import ARSENAL, GENESIS
    D = paths.RES + '/data/aurelia/loot_tables/chests'
    os.makedirs(D, exist_ok=True)
    for realm in ['grove', 'skyreach', 'hollow', 'drowned', 'pale', 'scarlet', 'clockwork', 'mycelial', 'last']:
        a = ARSENAL.get(realm, GENESIS)
        metal, special = f'aurelia:{a["metal"]}', f'aurelia:{a["special"]}'
        entries = [
            {'type': 'minecraft:item', 'name': metal, 'weight': 10, 'functions': [{'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': 2, 'max': 6}}]},
            {'type': 'minecraft:item', 'name': special, 'weight': 3},
            {'type': 'minecraft:item', 'name': 'minecraft:diamond', 'weight': 4, 'functions': [{'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': 1, 'max': 3}}]},
            {'type': 'minecraft:item', 'name': 'minecraft:gold_ingot', 'weight': 8, 'functions': [{'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': 3, 'max': 9}}]},
            {'type': 'minecraft:item', 'name': 'minecraft:book', 'weight': 4, 'functions': [{'function': 'minecraft:enchant_with_levels', 'levels': {'type': 'minecraft:uniform', 'min': 20, 'max': 39}, 'treasure': True}]},
            {'type': 'minecraft:item', 'name': 'minecraft:golden_apple', 'weight': 3},
            {'type': 'minecraft:item', 'name': 'minecraft:experience_bottle', 'weight': 5, 'functions': [{'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': 2, 'max': 6}}]},
        ]
        if realm == 'last':
            entries = [e for e in entries if e['name'] != special]
        json.dump({'type': 'minecraft:chest', 'pools': [{'rolls': {'type': 'minecraft:uniform', 'min': 4, 'max': 7}, 'bonus_rolls': 0, 'entries': entries}]},
                  open(f'{D}/lair_{realm}.json', 'w'), indent=2)


def layout_java(rows):
    lines = '\n'.join(f'            case "{i}" -> new int[] {{{", ".join(str(v) for v in r)}}};' for i, r in rows)
    return f'''package com.aurelia.world;

/**
 * GENERATED by gen_lairs.py. Each lair template's size, floor height, Lair Seal and beacon, as
 * {{width, height, length, floor, sealX, sealY, sealZ, beaconX, beaconY, beaconZ}} in template space.
 */
public final class LairLayout {{
    private LairLayout() {{}}

    public static int[] get(String id) {{
        return switch (id) {{
{lines}
            default -> null;
        }};
    }}
}}
'''


def main(only=None):
    rows, entrances = [], {}
    for lt in LIEUTENANTS:
        if only and lt['id'] not in only:
            continue
        lair = Lair(lt, HEIGHT[lt['lair']]).build()
        # above the floor LairBuilder clears the whole lair's volume before placing it, so the template needn't carry that air;
        # below the floor (a pit, a throat) it must
        lair.g.b = {k: v for k, v in lair.g.b.items() if not (v[0] == AIR and k[1] >= lair.F)}
        lair.g.save(f'lair_{lt["id"]}')
        s, b = lair.seal, lair.beacon
        rows.append((lt['id'], [W, lair.g.H, L, lair.F, s[0], s[1], s[2], b[0], b[1], b[2]]))
        entrances[lt['id']] = (lair.entrance, s)
    if not only:
        open(paths.JAVA + '/world/LairLayout.java', 'w').write(layout_java(rows))
        loot_tables()
    return entrances


if __name__ == '__main__':
    import sys
    main(sys.argv[1:] or None)
