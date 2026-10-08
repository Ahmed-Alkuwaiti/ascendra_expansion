"""Makes every citadel daunting: each one, untouched, becomes the keep of a colossal fortress built round it.

The citadel itself (its rite, its puzzles, its guards, its Waygate) is kept exactly as its generator made it, in tools/_cores/.
Round it this lays out, on the citadel's own ground level:
  - a curtain wall twenty-six blocks high with a wall walk, spiked merlons and buttresses, and arrow slits that glow
  - eight great towers (four at the corners, three along the sides) with steep spiked roofs and horns
  - a gatehouse on the south side, where the citadel's own entrance faces: twin towers, a portcullis, a carved visage
  - a causeway from the gate to the keep, lined with braziers and skull posts, two hooded colossi flanking it outside
  - spike fields before the gate and a palisade of spikes round the walls' feet
  - per realm: a lava moat (the Ashen Citadel), piers into the sea (Tidewrack), a ring of broken obelisks (the Convergence Gate)

Writes the fortified templates over data/aurelia/structures/<name>.nbt, widens each structure's reach, and records how far
the keep moved (tools/_cores/offsets.json) for the route checks.
"""
import json
import math
import os
import random

import nbtlib
from nbtlib import Compound, Double, Int, List, String

import gen_citadels2
import paths
from gen_act3_citadels import AIR, Grid, chain, statue
from gen_lairs import PAL, B

CORES = os.path.join(os.path.dirname(__file__), '_cores')
# where each keep's own way in is (template z), so the causeway can run right up to it; others default to near the south edge
ENTRY = {'tidewrack_citadel': 58, 'rimefast_citadel': 59, 'sunscar_citadel': 62, 'paradox_keep': 95, 'spore_cathedral': 90, 'convergence_gate': 76}
STRUCT = paths.RES + '/data/aurelia/structures'
WORLDGEN = paths.RES + '/data/aurelia/worldgen/structure'
# name: (realm palette, ground level in template space, margin added on every side, mode)
CITADELS = {
    'rootbound_citadel': ('grove', 11, 30, 'land'),
    'stormwatch_citadel': ('skyreach', 8, 30, 'land'),
    'ashen_citadel': ('hollow', 66, 30, 'moat'),
    'tidewrack_citadel': ('drowned', 23, 30, 'sea'),
    'rimefast_citadel': ('pale', 12, 30, 'land'),
    'sunscar_citadel': ('scarlet', 8, 30, 'land'),
    'paradox_keep': ('clockwork', 9, 28, 'land'),
    'spore_cathedral': ('mycelial', 6, 28, 'land'),
    'convergence_gate': ('last', 6, 26, 'ruin'),
}


def load_core(name):
    """A template with full fidelity (block states, block entities, entities) as a Grid."""
    t = nbtlib.load(os.path.join(CORES, name + '.nbt'))
    W, H, L = [int(v) for v in t['size']]
    g = Grid(W, H, L)
    pal = []
    for p in t['palette']:
        props = tuple(sorted((str(k), str(v)) for k, v in p.get('Properties', {}).items()))
        pal.append((str(p['Name']), props))
    for b in t['blocks']:
        x, y, z = (int(v) for v in b['pos'])
        name, props = pal[int(b['state'])]
        g.b[(x, y, z)] = (name, props, b['nbt'] if 'nbt' in b else None)
    g.entities = list(t['entities'])
    return g


class Fortress:
    def __init__(self, name):
        self.name = name
        self.realm, self.G, self.M, self.mode = CITADELS[name]
        self.core = load_core(name)
        self.p = PAL[self.realm]
        self.rnd = random.Random(sum(map(ord, name)) * 7)
        cw, ch, cl = self.core.W, self.core.H, self.core.L
        self.W, self.L = cw + 2 * self.M, cl + 2 * self.M
        self.H = max(ch, self.G + 74)
        self.f = Grid(self.W, self.H, self.L)                          # the new work, enriched on its own
        self.cx, self.cz = self.W // 2, self.L // 2

    # -------------------------------------------------------------------------------------------- materials
    def b(self, key):
        return B(self.p[key])

    def wall(self):
        r = self.rnd.random()
        return self.b('stone') if r < 0.6 else (self.b('stone2') if r < 0.85 else self.b('brick'))

    def set(self, x, y, z, name, props=None):
        self.f.set(x, y, z, B(name), props)

    def in_core(self, x, z, pad=0):
        return self.M - pad <= x < self.M + self.core.W + pad and self.M - pad <= z < self.M + self.core.L + pad

    # -------------------------------------------------------------------------------------------- pieces
    def footing(self, x, z, depth):
        """Stone under a wall or tower down into the ground (or the sea floor), so nothing floats."""
        for y in range(max(0, self.G - depth), self.G):
            self.set(x, y, z, self.b('stone2') if self.mode != 'sea' else self.b('pillar'))

    def spike(self, x, y, z, h, tip=True):
        blk = self.b('spike')
        for k in range(h):
            t = k / max(1, h)
            w = 1 if t < 0.35 else (0 if t < 0.7 else -1)
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    if w == 1 or (w == 0 and dx >= 0 and dz >= 0) or (w == -1 and dx == 0 and dz == 0):
                        self.set(x + dx, y + k, z + dz, blk)
        t = self.p['tip']
        if tip and t == 'pointed_dripstone':
            self.set(x, y + h, z, t, {'vertical_direction': 'up', 'thickness': 'frustum', 'waterlogged': 'false'})
            self.set(x, y + h + 1, z, t, {'vertical_direction': 'up', 'thickness': 'tip', 'waterlogged': 'false'})
        elif tip and t == 'lightning_rod':
            self.set(x, y + h, z, t, {'facing': 'up', 'powered': 'false', 'waterlogged': 'false'})
        elif tip and t == 'end_rod':
            self.set(x, y + h, z, t, {'facing': 'up'})

    def brazier(self, x, y, z, h=3):
        for k in range(h):
            self.set(x, y + k, z, self.b('trim') if k == h - 1 else self.b('stone2'))
        self.set(x, y + h, z, self.p['fire'], {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'})

    def skull_post(self, x, y, z, h=3):
        post = self.p['bars'] if 'fence' in self.p['bars'] else ('polished_blackstone_wall' if self.realm in ('hollow', 'clockwork', 'last')
                                                                 else 'cobblestone_wall')
        for k in range(h):
            self.set(x, y + k, z, post)
        self.set(x, y + h, z, 'skeleton_skull', {'rotation': str(self.rnd.randint(0, 15))})

    def tower(self, x, z, r, h):
        """A hollow round tower: thick wall, floors every ten blocks, glowing slits, battlement, steep roof, horns and a spike."""
        G = self.G
        for dx in range(-r - 1, r + 2):
            for dz in range(-r - 1, r + 2):
                d = math.hypot(dx, dz)
                if d > r:
                    continue
                self.footing(x + dx, z + dz, 14 if self.mode != 'sea' else G)
                for y in range(G, G + h):
                    edge = d > r - 2.2
                    if edge:
                        slit = y % 8 == 5 and (abs(dx) <= 0 or abs(dz) <= 0) and y > G + 4 and d > r - 1
                        self.set(x + dx, y, z + dz, self.p['glass'] + '_stained_glass' if slit else self.wall())
                    elif (y - G) % 10 == 0:
                        self.set(x + dx, y, z + dz, self.b('trim'))
        top = G + h
        for dx in range(-r - 2, r + 3):
            for dz in range(-r - 2, r + 3):
                d = math.hypot(dx, dz)
                if d <= r + 2:
                    self.set(x + dx, top, z + dz, self.b('trim'))
                    self.set(x + dx, top - 1, z + dz, self.b('stone2'))
                    if d > r + 1 and (dx + dz) % 2 == 0:
                        self.set(x + dx, top + 1, z + dz, self.b('stone'))
                        self.set(x + dx, top + 2, z + dz, self.b('stone'))
        rh = int(r * 2.6)
        for k in range(rh):
            rr = (r + 1) * (1 - k / rh) ** 0.9
            for dx in range(-r - 2, r + 3):
                for dz in range(-r - 2, r + 3):
                    d = math.hypot(dx, dz)
                    if rr - 1.5 <= d <= rr:
                        self.set(x + dx, top + 1 + k, z + dz, self.b('roof'))
        self.spike(x, top + rh, z, 6)
        for sx, sz in ((1, 0), (-1, 0), (0, 1), (0, -1)):              # horns sweeping out of the roof
            for k in range(7):
                self.set(x + sx * (r + 1 + k // 2), top + 3 + k, z + sz * (r + 1 + k // 2), self.b('spike'))
        for sx, sz in ((1, 1), (-1, 1), (1, -1), (-1, -1)):             # chains hung with cages from the battlement
            if self.rnd.random() < 0.5:
                cx, cz = x + sx * (r + 2), z + sz * (r + 2)
                chain(self.f, cx, top - 9, top - 1, cz)
                for dx in (0, 1):
                    for dz in (0, 1):
                        for y in range(top - 12, top - 9):
                            self.set(cx + dx - 1 + (1 if dx else 0) * 0, y, cz + dz - 1, 'iron_bars')

    def curtain(self, x0, z0, x1, z1, gate=None):
        """A straight run of wall from (x0, z0) to (x1, z1): five thick, twenty-six high, with a walk, merlons, spikes and buttresses."""
        G, Hh = self.G, 26
        n = max(abs(x1 - x0), abs(z1 - z0))
        ux, uz = (x1 - x0) / n, (z1 - z0) / n
        nx, nz = uz, -ux                                                 # outward normal (the walls run clockwise)
        for i in range(n + 1):
            x, z = round(x0 + ux * i), round(z0 + uz * i)
            gap = gate is not None and abs(i - gate) <= 5
            for t in range(-2, 3):
                xx, zz = round(x + nx * t), round(z + nz * t)
                self.footing(xx, zz, 12 if self.mode != 'sea' else G)
                for y in range(G, G + Hh):
                    if gap and y < G + 15 and abs(i - gate) <= 4:
                        continue
                    slit = t == 2 and y % 8 == 4 and i % 6 == 3
                    self.set(xx, y, zz, self.p['glass'] + '_stained_glass' if slit else self.wall())
            self.set(round(x + nx * 2.4), G + Hh, round(z + nz * 2.4), self.b('stone'))         # merlons and a walk
            if i % 2 == 0:
                self.set(round(x + nx * 2.4), G + Hh + 1, round(z + nz * 2.4), self.b('stone'))
                if i % 6 == 0:
                    self.set(round(x + nx * 2.4), G + Hh + 2, round(z + nz * 2.4), self.b('spike'))
            for t in range(-2, 2):
                self.set(round(x + nx * t), G + Hh - 1, round(z + nz * t), self.b('trim'))
            if i % 10 == 5 and not gap:                                 # buttresses with spikes out of them
                for k in range(1, 5):
                    for y in range(G, G + Hh - k * 5):
                        self.set(round(x + nx * (2 + k)), y, round(z + nz * (2 + k)), self.b('stone2'))
                self.spike(round(x + nx * 7), G, round(z + nz * 7), 4)
            if i % 4 == 0 and not gap and self.mode != 'sea':           # a palisade of spikes along the foot
                self.spike(round(x + nx * 9), G, round(z + nz * 9), 3 + (i % 3), tip=False)

    def gatehouse(self, x, z):
        """Twin towers, a portcullis, and over the arch a visage with burning eyes and fangs."""
        G = self.G
        for sx in (-1, 1):
            self.tower(x + sx * 9, z, 7, 44)
        for dx in range(-6, 7):                                        # the arch's crown and the visage above it
            for y in range(G + 14, G + 30):
                for dz in range(-3, 4):
                    self.set(x + dx, y, z + dz, self.wall())
        for sx in (-1, 1):
            for dx in range(-2, 3):
                for dy in range(-1, 2):
                    self.set(x + sx * 3 + dx, G + 22 + dy, z + 3, B('black_concrete') if abs(dx) == 2 or abs(dy) == 1 else self.b('glow'))
        for dx in range(-3, 4):
            self.set(x + dx, G + 17, z + 3, B('black_concrete'))
            if dx % 2 == 0:
                self.set(x + dx, G + 16, z + 3, B('bone_block'))
                self.set(x + dx, G + 15, z + 3, B('bone_block'))
        for dx in range(-4, 5, 2):                                     # the raised portcullis
            for y in range(G + 11, G + 14):
                self.set(x + dx, y, z + 2, 'iron_bars')
        for sx in (-1, 1):                                             # horns off the gatehouse
            for k in range(12):
                t = k / 11
                hx, hy = x + sx * (6 + t * 8), G + 28 + math.sin(t * math.pi * 0.8) * 9
                for dz in (-1, 0, 1):
                    self.set(round(hx), round(hy), z + dz, self.b('spike') if t < 0.8 else self.b('trim'))

    # -------------------------------------------------------------------------------------------- the whole
    def build(self):
        W, L, G, M = self.W, self.L, self.G, self.M
        cx, cz = self.cx, self.cz
        e = 12                                                           # the walls' centre line, in from the edge
        if self.mode == 'ruin':
            return self.ruin()
        # the bailey's ground, levelled and paved round the keep
        for x in range(e - 2, W - e + 2):
            for z in range(e - 2, L - e + 2):
                if self.in_core(x, z):
                    continue
                if self.mode == 'sea':
                    if (x - cx) % 6 == 0 and (z - cz) % 6 == 0:
                        for y in range(0, G - 1):
                            self.set(x, y, z, self.b('pillar'))
                    self.set(x, G - 1, z, self.b('floor') if (x // 3 + z // 3) % 2 else self.b('floor2'))
                    continue
                self.set(x, G - 1, z, self.b('soil_top') if self.rnd.random() < 0.7 else self.b('floor2'))
                for y in range(G - 4, G - 1):
                    self.set(x, y, z, self.b('soil'))
                for y in range(G, G + 7):
                    self.f.set(x, y, z, AIR)
        gate = cx - e
        self.curtain(e, L - 1 - e, e, e)                                  # west wall, south to north
        self.curtain(e, e, W - 1 - e, e)                                  # north
        self.curtain(W - 1 - e, e, W - 1 - e, L - 1 - e)                  # east
        self.curtain(W - 1 - e, L - 1 - e, e, L - 1 - e, gate=W - 1 - e - cx)   # south, with the gate in the middle
        for x, z in ((e, e), (W - 1 - e, e), (e, L - 1 - e), (W - 1 - e, L - 1 - e)):
            self.tower(x, z, 9, 56)
        for x, z in ((cx, e), (e, cz), (W - 1 - e, cz)):
            self.tower(x, z, 6, 46)
        self.gatehouse(cx, L - 1 - e)
        for z in range(self.M + self.core.L, L - e + 4):               # the causeway to the keep
            for x in range(cx - 4, cx + 5):
                self.set(x, G - 1, z, self.b('trim') if abs(x - cx) == 4 else self.b('floor'))
                for y in range(G, G + 12):
                    if not (L - e - 3 <= z <= L - e + 3) or y < G + 12:
                        self.f.set(x, y, z, AIR)
            if z % 5 == 0:
                self.skull_post(cx - 6, G, z, 3)
                self.skull_post(cx + 6, G, z, 3)
        self.causeway_into_keep()
        for z in range(L - e + 4, L):                                  # and on out past the gate
            for x in range(cx - 4, cx + 5):
                self.set(x, G - 1, z, self.b('floor'))
        for k, z in enumerate(range(self.M + self.core.L + 3, L - e - 4, 7)):
            self.brazier(cx - 8, G, z, 4)
            self.brazier(cx + 8, G, z, 4)
        if self.mode != 'sea':                                          # a field of spikes inside the walls, either side of the causeway
            for k in range(40):
                x = self.rnd.randint(e + 8, W - e - 9)
                z = self.rnd.randint(e + 8, L - e - 9)
                if self.in_core(x, z, pad=6) or abs(x - cx) < 12 or (z > L - e - 20 and abs(abs(x - cx) - (self.core.W // 2 + 12)) < 8):
                    continue
                self.spike(x, G, z, self.rnd.randint(4, 9))
        for sx in (-1, 1):                                             # hooded colossi in the bailey's south corners, watching the gate
            statue(self.f, cx + sx * (self.core.W // 2 + 12), G, L - e - 12, 's', 34, self.b('stone2'), self.b('trim'), B('black_concrete'), self.b('glow'),
                   held='orb' if sx < 0 else 'hourglass', rnd=self.rnd)
        if self.mode == 'moat':                                         # a moat of lava round the outside
            for x in range(W):
                for z in range(L):
                    d = min(x, z, W - 1 - x, L - 1 - z)
                    if d <= 1:
                        self.set(x, G - 1, z, 'lava')
                        self.set(x, G - 2, z, self.b('stone2'))
            for z in range(L - e + 3, L):
                for x in range(cx - 4, cx + 5):
                    self.set(x, G - 1, z, self.b('trim') if abs(x - cx) == 4 else self.b('floor'))
        return self

    def causeway_into_keep(self):
        """Carry the causeway on into the keep's bounding box, over whatever ground the citadel leaves to the world, up to its door."""
        G, M, cx = self.G, self.M, self.cx
        door_z = M + ENTRY.get(self.name, self.core.L - 6)
        for z in range(door_z, M + self.core.L):
            for x in range(cx - 4, cx + 5):
                if (x - M, G - 1, z - M) not in self.core.b:
                    self.set(x, G - 1, z, self.b('trim') if abs(x - cx) == 4 else self.b('floor'))
                    if self.mode == 'sea' and (x - cx) % 4 == 0 and z % 4 == 0:
                        for y in range(0, G - 1):
                            self.set(x, y, z, self.b('pillar'))

    def ruin(self):
        """The Convergence Gate: no walls, but a ring of broken obelisks bound in chains, spikes between, and two colossi."""
        W, L, G = self.W, self.L, self.G
        cx, cz = self.cx, self.cz
        for k in range(12):
            a = k * math.pi / 6 + 0.13
            x, z = int(cx + math.cos(a) * (W / 2 - 9)), int(cz + math.sin(a) * (L / 2 - 9))
            if z > cz + 20 and abs(x - cx) < 14:
                continue
            h = 22 + (k * 7) % 18
            broken = k % 3 == 1
            for y in range(G - 6, G + h):
                tw = 2 if y < G + h * 0.7 else 1
                for dx in range(-tw, tw + 1):
                    for dz in range(-tw, tw + 1):
                        if broken and y > G + h * 0.6 and (dx + dz + y) % 3 == 0:
                            continue
                        self.set(x + dx, y, z + dz, B('polished_blackstone_bricks') if (y // 4) % 2 else B('calcite'))
            self.set(x, G + h, z, B('pearlescent_froglight'), {'axis': 'y'})
            for k2 in range(3):                                          # chains slung between the stones
                chain(self.f, x + 3, G + h - 10 - k2 * 4, G + h - 8 - k2 * 4, z)
            for s in range(3):
                self.spike(int(cx + math.cos(a + 0.26) * (W / 2 - 12 + s * 3)), G, int(cz + math.sin(a + 0.26) * (L / 2 - 12 + s * 3)), 4 + s * 2)
        for z in range(self.M + self.core.L - 8, L):                    # a road of black and gold up to the gate
            for x in range(cx - 4, cx + 5):
                if (x - self.M, G - 1, z - self.M) not in self.core.b:
                    self.set(x, G - 1, z, B('gold_block') if abs(x - cx) == 4 else B('polished_blackstone_bricks'))
        for sx in (-1, 1):
            statue(self.f, cx + sx * 18, G, L - 12, 's', 36, B('polished_blackstone_bricks'), B('gold_block'), B('black_concrete'),
                   B('pearlescent_froglight'), held='orb' if sx < 0 else 'hourglass', rnd=self.rnd)
        return self

    def save(self):
        import enrich
        enrich.enrich(self.f, self.name, light=True)                   # dress only the new work, lightly
        out = Grid(self.W, self.H, self.L)
        out.b = dict(self.f.b)
        M = self.M
        for (x, y, z), v in self.core.b.items():                        # the keep, exactly as it was
            out.b[(x + M, y, z + M)] = v
        for e in self.core.entities:
            ent = Compound(e)
            pos = [float(v) for v in e['pos']]
            ent['pos'] = List[Double]([Double(pos[0] + M), Double(pos[1]), Double(pos[2] + M)])
            bp = [int(v) for v in e['blockPos']]
            ent['blockPos'] = List[Int]([Int(bp[0] + M), Int(bp[1]), Int(bp[2] + M)])
            out.entities.append(ent)
        was = gen_citadels2.ENRICH
        gen_citadels2.ENRICH = False
        try:
            out.save(self.name)
        finally:
            gen_citadels2.ENRICH = was
        j = json.load(open(f'{WORLDGEN}/{self.name}.json'))
        j['max_distance_from_center'] = 128
        json.dump(j, open(f'{WORLDGEN}/{self.name}.json', 'w'), indent=2)
        return M


def main(names=None):
    offs_p = os.path.join(CORES, 'offsets.json')
    offs = json.load(open(offs_p)) if os.path.exists(offs_p) else {}
    for name in names or CITADELS:
        offs[name] = Fortress(name).build().save()
    json.dump(offs, open(offs_p, 'w'), indent=1)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:] or None)
