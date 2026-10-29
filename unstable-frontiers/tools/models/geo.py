"""A small builder for Bedrock entity geometry (the .geo.json format GeckoLib loads and Blockbench opens and edits).

Units are pixels (16 per block). The model faces -Z ("north"): heads go at negative z. Cubes use box UV; the texture
atlas is packed automatically and painted by tex.py from each cube's material, so geometry and texture always agree.
"""
import json
import math


class Cube:
    def __init__(self, origin, size, material, inflate=0.0, mirror=False):
        self.origin = [float(v) for v in origin]
        self.size = [float(v) for v in size]
        self.material = material
        self.inflate = inflate
        self.mirror = mirror
        self.uv = None          # set by pack()

    def box(self):
        w, h, d = (max(1, math.ceil(s)) for s in self.size)
        return w, h, d

    def footprint(self):
        w, h, d = self.box()
        return 2 * (w + d), d + h


class Bone:
    def __init__(self, name, pivot, parent=None, rotation=(0, 0, 0)):
        self.name = name
        self.pivot = [float(v) for v in pivot]
        self.parent = parent
        self.rotation = [float(v) for v in rotation]
        self.cubes = []
        self.locators = {}

    def cube(self, origin, size, material, **kw):
        c = Cube(origin, size, material, **kw)
        self.cubes.append(c)
        return c


class Model:
    def __init__(self, name, tex_w=256, tex_h=256):
        self.name = name
        self.tex_w, self.tex_h = tex_w, tex_h
        self.bones = []

    def bone(self, name, pivot, parent=None, rotation=(0, 0, 0)):
        b = Bone(name, pivot, parent.name if isinstance(parent, Bone) else parent, rotation)
        self.bones.append(b)
        return b

    def get(self, name):
        return next(b for b in self.bones if b.name == name)

    def pack(self):
        """Shelf-packs every cube's box-UV footprint into the atlas (tallest first)."""
        cubes = [c for b in self.bones for c in b.cubes]
        order = sorted(cubes, key=lambda c: (-c.footprint()[1], -c.footprint()[0]))
        x = y = shelf = 0
        for c in order:
            fw, fh = c.footprint()
            if x + fw > self.tex_w:
                x, y, shelf = 0, y + shelf, 0
            if y + fh > self.tex_h:
                raise ValueError(f'{self.name}: texture atlas {self.tex_w}x{self.tex_h} too small')
            c.uv = [x, y]
            x += fw
            shelf = max(shelf, fh)
        return y + shelf

    def to_json(self, visible=(4, 3, 0)):
        self.pack()
        bones = []
        for b in self.bones:
            j = {'name': b.name, 'pivot': b.pivot}
            if b.parent:
                j['parent'] = b.parent
            if any(b.rotation):
                j['rotation'] = b.rotation
            if b.cubes:
                cs = []
                for c in b.cubes:
                    cj = {'origin': c.origin, 'size': c.size, 'uv': c.uv}
                    if c.inflate:
                        cj['inflate'] = c.inflate
                    if c.mirror:
                        cj['mirror'] = True
                    cs.append(cj)
                j['cubes'] = cs
            if b.locators:
                j['locators'] = b.locators
            bones.append(j)
        return {'format_version': '1.12.0', 'minecraft:geometry': [{
            'description': {'identifier': f'geometry.{self.name}', 'texture_width': self.tex_w, 'texture_height': self.tex_h,
                            'visible_bounds_width': visible[0], 'visible_bounds_height': visible[1],
                            'visible_bounds_offset': [0, visible[1] / 2, 0]},
            'bones': bones}]}

    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.to_json(), f, indent=1)


def mirror_x(origin, size):
    """The origin of a cube mirrored across x = 0."""
    return [-origin[0] - size[0], origin[1], origin[2]]
