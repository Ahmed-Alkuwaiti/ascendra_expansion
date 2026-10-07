"""Sprites for the Arsenals of the Tenfold Seal: each realm's weapon (64 x 64), tools, materials and armor icons (32 x 32) and
ore (16 x 16), drawn with pixelart.py. Weapons and tools run from the grip at the bottom left to the business end at the top
right, the way Minecraft holds them."""
import math

from pixelart import Sprite, Mat, M, GEMS

U = (0.7071, -0.7071)          # along the weapon, toward the tip
V = (0.7071, 0.7071)           # across it, toward the bottom right


class Frame:
    """Coordinates along (a) and across (b) a weapon whose axis passes through c."""
    def __init__(self, s, c, u=U):
        self.s, self.c, self.u = s, c, u
        self.v = (-u[1], u[0]) if u != U else V

    def p(self, a, b=0.0):
        return (self.c[0] + self.u[0] * a + self.v[0] * b, self.c[1] + self.u[1] * a + self.v[1] * b)

    def poly(self, pts, mat):
        self.s.poly([self.p(a, b) for a, b in pts], mat)

    def box(self, a0, a1, b0, b1, mat):
        self.poly([(a0, b0), (a1, b0), (a1, b1), (a0, b1)], mat)

    def line(self, a0, b0, a1, b1, w, mat, w1=None):
        self.s.line(self.p(a0, b0), self.p(a1, b1), w, mat, w1)

    def path(self, pts, w, mat, w_end=None):
        self.s.path([self.p(a, b) for a, b in pts], w, mat, w_end)

    def gem(self, a, b, r, mat):
        x, y = self.p(a, b)
        self.s.gem(x, y, r, mat)

    def ellipse(self, a, b, r, mat):
        x, y = self.p(a, b)
        self.s.ellipse(x, y, r, r, mat)


def arc(cx, cy, r, a0, a1, n=10):
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in [a0 + (a1 - a0) * i / n for i in range(n + 1)]]


# ================================================================================================ weapons, 64 x 64
def rootbreaker():
    """A living warhammer: a knotted root haft wound with vines, a head of mossy heartwood bound in gold, a green core blazing."""
    s = Sprite(64, 11)
    f = Frame(s, (6, 58))
    f.line(0, 0, 48, 0, 5, 'bark')
    for a in (6, 26):
        f.box(a - 1.5, a + 1.5, -3.5, 3.5, 'gold')
    f.gem(0, 0, 4.5, 'gold')
    f.path([(4, -1), (10, 2), (16, -2), (22, 2), (28, -2), (34, 2), (40, -1)], 2, 'vine')
    for a, b in [(12, 3), (24, -4), (36, 3)]:
        f.poly([(a, b), (a + 3, b + 2), (a + 4, b - 1)], 'leaf')
    h = Frame(s, f.p(50, 0))
    h.box(-9, 9, -19, 19, 'wood_d')
    h.box(-7.5, 7.5, -20, 20, 'bark')
    for b in (-15, 15):
        h.box(-9.5, 9.5, b - 2.2, b + 2.2, 'gold')
    h.box(2, 7.5, -13, 13, 'moss')
    for b in (-21.5, 21.5):
        h.box(-5, 5, b - 1.5, b + 1.5, 'wood_d')
        h.poly([(-2, b * 1.12), (0, b * 1.22), (2, b * 1.12)], 'leaf')
    h.box(-5, 5, -5, 5, 'gold')
    h.gem(0, 0, 3.6, 'verdant')
    for b in (-9, 9):
        h.gem(0, b, 1.6, 'verdant')
    h.path([(7.5, -18), (6, -12), (8, -6), (6, 0), (8, 6), (6, 12), (7.5, 18)], 1.6, 'vine')
    return s


def stormpiercer():
    """A lance of storm-glass: a long white-and-blue haft, swept fins at the socket, a long crystal head with lightning in it."""
    s = Sprite(64, 12)
    f = Frame(s, (5, 59))
    f.line(0, 0, 48, 0, 3.5, 'aether')
    f.gem(0, 0, 3.5, 'gold')
    for a in (10, 22, 34):
        f.box(a - 1.2, a + 1.2, -3, 3, 'gold')
    f.path([(4, 0), (8, 2.5), (12, -2.5), (16, 2.5), (20, -2.5), (24, 2.5), (28, -2.5), (32, 2.5), (36, -2), (40, 1.5)], 1.2, 'storm')
    h = Frame(s, f.p(48, 0))
    for sg in (-1, 1):                                            # swept fins
        h.poly([(-2, 0), (5, sg * 2), (-1, sg * 9), (-6, sg * 10), (-3, sg * 3)], 'white')
        h.poly([(-1, sg * 3), (3, sg * 3), (-2, sg * 7.5)], 'sky')
    h.box(-3, 3, -3.5, 3.5, 'gold')
    h.poly([(2, -4.5), (14, -3.5), (24, 0), (14, 3.5), (2, 4.5)], 'sky_m')
    h.poly([(3, -2), (14, -1.5), (21, 0), (14, 1.5), (3, 2)], 'sky')
    h.poly([(5, 0), (8, -1), (10, 0.8), (13, -0.6), (16, 0.6)], 'white')
    h.gem(0, 0, 2.2, 'gem_c')
    return s


def soulcleaver():
    """A slab of black soulsteel with a burning blue edge: a demon's cleaver, gold-bound, embers caught in the metal."""
    s = Sprite(64, 13)
    f = Frame(s, (6, 58))
    f.line(-1, 0, 14, 0, 4, 'leather')
    f.gem(-1, 0, 3.6, 'gold')
    f.box(13, 17, -9, 9, 'black')
    f.box(14, 16, -10, 10, 'gold')
    f.gem(15, 0, 2.4, 'gem_o')
    b = Frame(s, f.p(17, 0))
    b.poly([(0, -6), (40, -8), (46, -4), (44, 4), (38, 11), (0, 10)], 'soulsteel')          # the slab
    b.poly([(1, 7.5), (38, 8.5), (43, 4), (45, 4.5), (39, 11.5), (1, 11)], 'soul')         # the burning edge
    b.poly([(2, -6), (40, -8), (42, -6.5), (2, -4)], 'dark')                                # the spine
    for a in (6, 18, 30):
        b.box(a, a + 3, -6, -3, 'gold')
    for (a, c) in [(10, 0), (22, 3), (34, -1)]:
        b.path([(a, c - 3), (a + 2, c), (a + 1, c + 3), (a + 4, c + 5)], 1.2, 'ember')
    b.ellipse(44, -1, 2.5, 'soul')
    return s


def tidebinder():
    """A trident of pearl and tidesteel, gold-banded, with coral-bone tines and a glowing tide-stone where they meet."""
    s = Sprite(64, 14)
    f = Frame(s, (5, 59))
    f.line(0, 0, 42, 0, 3.6, 'pearl')
    f.gem(0, 0, 3.4, 'gold')
    for a in (8, 20, 32):
        f.box(a - 1.5, a + 1.5, -3, 3, 'gold')
    f.path([(4, 2), (10, -2), (16, 2), (22, -2), (28, 2), (34, -2)], 1.0, 'teal')
    h = Frame(s, f.p(42, 0))
    h.box(-2, 3, -11, 11, 'tidesteel')
    h.box(-3, -1, -12, 12, 'gold')
    h.poly([(3, -2.5), (20, -1.2), (24, 0), (20, 1.2), (3, 2.5)], 'tidesteel')               # the centre tine
    for sg in (-1, 1):
        h.path([(2, sg * 10), (8, sg * 11), (13, sg * 10), (17, sg * 8)], 2.6, 'tidesteel', 1.2)
        h.poly([(15, sg * 9.5), (19, sg * 8.5), (17, sg * 6.5)], 'pearl')
        h.path([(0, sg * 11), (-3, sg * 15), (-1, sg * 18)], 1.5, 'coral', 1.0)
    h.poly([(18, -1), (24, 0), (18, 1)], 'pearl')
    h.gem(1, 0, 3, 'teal_g')
    return s


def silent_requiem():
    """A reaper's scythe of rime-steel, a crescent edged in violet void-light, a silver bell hanging silent from the haft."""
    s = Sprite(64, 15)
    s.line((10, 60), (40, 6), 3.6, 'night')
    for (x, y) in [(12, 56), (24, 35), (34, 17)]:
        s.line((x - 1.2, y + 2), (x + 1.2, y - 2), 5, 'gold')
    s.gem(10, 60, 3.2, 'gold')
    outer = arc(34, 27, 24, -80, 62, 16)
    inner = arc(30, 29, 19, -62, 52, 16)
    s.poly(outer + inner[::-1], 'ice')
    s.poly(arc(34, 27, 24, -60, 62, 14) + arc(33.4, 27.3, 21.6, -58, 58, 14)[::-1], 'void_p')
    s.poly(arc(31.5, 28.5, 20, -60, 50, 12) + arc(30.4, 29, 19, -58, 50, 12)[::-1], 'frost')
    s.poly([(36, 1), (45, 1), (46, 10), (37, 11)], 'night')
    s.gem(41, 6, 2.6, 'void_p')
    s.line((21, 44), (23, 47), 1, 'string')
    s.poly([(20, 47), (26, 47), (27.5, 52), (18.5, 52)], 'gold')
    s.ellipse(23, 53, 1.2, 1.2, 'gold')
    for (x, y) in [(50, 18), (55, 30), (46, 40)]:
        s.gem(x, y, 1.2, 'ice_g')
    return s


def venomfangs():
    """Twin daggers like a serpent's fangs: curved scarlet blades with venom-glass edges, amber poison sacs in the guards."""
    s = Sprite(64, 16)
    for (ox, oy, k) in [(0, 0, 1.0), (18, 6, 0.82)]:
        gx, gy = 8 + ox, 56 + oy * 0.2

        def P(x, y):
            return (gx + x * k, gy - y * k)
        s.line(P(0, 0), P(8, 8), 4 * k, 'black')
        s.gem(*P(0, 0), 3 * k, 'gold')
        for t in (2.5, 5.5):
            s.line(P(t - 0.6, t - 0.6), P(t + 0.6, t + 0.6), 5.5 * k, 'gold')
        s.line(P(5, 12), P(13, 4), 3.5 * k, 'gold')
        s.ellipse(*P(9, 8), 3 * k, 3 * k, 'amber')
        outer = [P(10, 12), P(16, 22), P(19, 32), P(18, 42), P(14, 50)]
        inner = [P(13, 8), P(21, 18), P(25, 28), P(25, 38), P(14, 50)]
        s.poly(outer + inner[::-1], 'scarlet')
        s.poly([P(13, 9), P(21, 19), P(25, 29), P(25, 38), P(22, 39), P(22, 30), P(19, 20), P(12, 11)], 'glass_r')
        s.path([P(14, 14), P(18, 24), P(20, 34)], 1.0 * k, 'scarlet_g')
    return s


def hourshatter():
    """A clockwork repeating crossbow: brass-and-black stock, bladed limbs, a turning gear at its heart, a bolt of violet time."""
    s = Sprite(64, 17)
    f = Frame(s, (7, 57))
    f.line(-2, 0, 40, 0, 6, 'black')
    f.line(0, 0, 38, 0, 3, 'brass')
    f.box(-4, 2, -4, 4, 'brass')
    f.poly([(6, 3), (10, 9), (13, 9), (11, 3)], 'black')                                   # the grip
    h = Frame(s, f.p(36, 0))
    for sg in (-1, 1):                                                                       # bladed limbs
        h.path([(0, sg * 2), (2, sg * 9), (-1, sg * 16), (-6, sg * 21)], 3.4, 'black', 2.0)
        h.path([(1, sg * 3), (3, sg * 9), (0, sg * 15)], 1.4, 'brass')
        h.poly([(-6, sg * 21), (-3, sg * 26), (-9, sg * 23)], 'chronite')
    h.line(-6, -21, -14, 0, 0.8, 'string')
    h.line(-6, 21, -14, 0, 0.8, 'string')
    f.line(18, 0, 50, 0, 1.6, 'chrono_g')                                                   # the loaded bolt
    h2 = Frame(s, f.p(50, 0))
    h2.poly([(0, -2.5), (5, 0), (0, 2.5)], 'chrono_g')
    gx, gy = f.p(20, 0)
    for k in range(8):                                                                       # the gear
        a = k * math.pi / 4
        s.gem(gx + 7.5 * math.cos(a), gy + 7.5 * math.sin(a), 1.8, 'brass')
    s.ellipse(gx, gy, 7, 7, 'brass')
    s.ellipse(gx, gy, 4.5, 4.5, 'black')
    s.gem(gx, gy, 3, 'chrono_g')
    return s


def sporethorn():
    """A staff of pale stalk grown thorny, its head a cradle of curling tendrils round a blazing spore-orb, small caps sprouting."""
    s = Sprite(64, 18)
    f = Frame(s, (6, 58))
    f.path([(0, 0), (12, 1.5), (24, -1.5), (36, 1.5), (44, 0)], 3.6, 'stalk', 3.0)
    f.gem(0, 0, 3, 'myc')
    for a, sg in [(8, 1), (16, -1), (26, 1), (34, -1)]:
        f.poly([(a, sg * 1.5), (a + 2, sg * 5), (a + 3, sg * 1.5)], 'stalk')
    for a in (12, 30):
        f.box(a - 1.2, a + 1.2, -3, 3, 'myc')
    h = Frame(s, f.p(50, 0))
    for sg in (-1, 1):
        h.path([(-7, sg * 1.5), (-4, sg * 8), (3, sg * 10), (9, sg * 7), (10, sg * 2)], 2.4, 'stalk', 1.2)
    h.ellipse(1, 0, 7, 'myc_g')
    h.ellipse(1, 0, 3.5, 'star')
    for (a, b) in [(-10, 6), (-14, -5)]:
        h.line(a, b, a + 2, b + 2 * (1 if b > 0 else -1), 1, 'stalk')
        h.ellipse(a + 2, b + 3 * (1 if b > 0 else -1), 2.2, 'myc')
    for (x, y) in [(56, 4), (59, 14), (46, 3)]:
        s.ellipse(x, y, 1, 1, 'myc_g')
    return s


def worldsunder():
    """The Genesis greatsword: a broad white blade edged in black, the eight realm stones set down its heart, a crown of a
    guard in gold, and the shards of the unmade worlds hanging round it."""
    s = Sprite(64, 19)
    f = Frame(s, (5, 59))
    f.line(-1, 0, 12, 0, 4.2, 'black')
    for a in (3, 7):
        f.box(a - 0.8, a + 0.8, -2.8, 2.8, 'gold')
    f.gem(-2, 0, 3.6, 'gold')
    f.gem(-2, 0, 1.6, 'star')
    g = Frame(s, f.p(14, 0))
    g.poly([(-3, -4), (2, -14), (5, -13), (3, -4), (3, 4), (5, 13), (2, 14), (-3, 4)], 'gold')    # the crown guard
    g.poly([(-1, -3), (1, -9), (2, -3)], 'black')
    g.poly([(-1, 3), (1, 9), (2, 3)], 'black')
    g.gem(0, 0, 3.4, 'abyss')
    g.gem(0, 0, 1.6, 'star')
    b = Frame(s, f.p(17, 0))
    b.poly([(0, -8), (36, -6.5), (47, 0), (36, 6.5), (0, 8)], 'black')
    b.poly([(0, -6.4), (35, -5), (43, 0), (35, 5), (0, 6.4)], 'genesis')
    b.poly([(0, -1.4), (36, -0.8), (40, 0), (36, 0.8), (0, 1.4)], 'gold')
    for i, gm in enumerate(GEMS):
        b.gem(3 + i * 4.3, 0, 2.0, gm)
    for (x, y, m) in [(52, 26, 'genesis'), (57, 20, 'black'), (34, 6, 'genesis'), (40, 4, 'black'), (60, 12, 'star'), (27, 10, 'star')]:
        s.gem(x, y, 2.2 if m != 'star' else 1.2, m)
    return s


WEAPONS = {'grove': ('rootbreaker', rootbreaker), 'skyreach': ('stormpiercer', stormpiercer), 'hollow': ('soulcleaver', soulcleaver),
           'drowned': ('tidebinder', tidebinder), 'pale': ('silent_requiem', silent_requiem), 'scarlet': ('venomfangs', venomfangs),
           'clockwork': ('hourshatter', hourshatter), 'mycelial': ('sporethorn', sporethorn), 'genesis': ('worldsunder', worldsunder)}


# ================================================================================================ tools, 32 x 32
TOOL = {   # haft, head, trim, glow, flourish
    'grove': ('bark', 'verdant_m', 'gold', 'verdant', 'vine'),
    'skyreach': ('aether', 'sky_m', 'gold', 'sky', 'storm'),
    'hollow': ('black', 'soulsteel', 'gold', 'soul', 'ember'),
    'drowned': ('pearl', 'tidesteel', 'gold', 'teal_g', 'coral'),
    'pale': ('night', 'ice', 'gold', 'void_p', 'frost'),
    'scarlet': ('black', 'scarlet', 'gold', 'amber', 'glass_r'),
    'clockwork': ('black', 'chronite', 'brass', 'chrono_g', 'brass'),
    'mycelial': ('stalk', 'myc', 'myc_ingot', 'myc_g', 'myc_g'),
    'genesis': ('black', 'genesis', 'gold', 'star', 'gold'),
}


def _haft(s, realm, length):
    hm, head, trim, glow, fl = TOOL[realm]
    f = Frame(s, (3.5, 28.5))
    f.line(0, 0, length, 0, 2.6, hm)
    f.gem(0, 0, 2.0, trim)
    f.box(7, 8.6, -1.9, 1.9, trim)
    if fl in ('vine', 'coral', 'storm', 'ember'):
        f.path([(2, 1), (6, -1), (10, 1), (14, -1)], 0.9, fl)
    return f


def pickaxe(realm):
    s = Sprite(32, 21)
    hm, head, trim, glow, fl = TOOL[realm]
    f = _haft(s, realm, 25)
    h = Frame(s, f.p(23, 0))
    for sg in (-1, 1):
        h.path([(0, 0), (-0.6, sg * 6), (-3, sg * 11)], 3.8, head, 1.2)
    h.path([(1.2, -6), (0.9, 0), (1.2, 6)], 1.0, fl if fl not in ('vine',) else 'leaf')
    h.box(-2.2, 2.2, -2.2, 2.2, trim)
    h.gem(0, 0, 1.4, glow)
    if realm == 'genesis':
        for sg in (-1, 1):
            h.gem(-3, sg * 11, 1.2, 'gem_c' if sg < 0 else 'gem_m')
    return s


def axe(realm):
    s = Sprite(32, 22)
    hm, head, trim, glow, fl = TOOL[realm]
    f = _haft(s, realm, 25)
    h = Frame(s, f.p(20, 0))
    h.poly([(-5, -1.5), (4, -1.5), (7, -7), (5, -12), (-7, -12), (-7, -6)], head)
    h.poly([(-7, -10.5), (5.5, -10.5), (5, -12.5), (-7, -12.5)], glow if realm != 'grove' else 'leaf')
    h.poly([(-2, 1.3), (2, 1.3), (0, 5)], trim)
    h.box(-2, 2, -2.2, 2.2, trim)
    h.gem(0, -6, 1.5, glow)
    return s


def shovel(realm):
    s = Sprite(32, 23)
    hm, head, trim, glow, fl = TOOL[realm]
    f = _haft(s, realm, 20)
    h = Frame(s, f.p(21, 0))
    h.poly([(-2, -4.5), (5, -5.2), (9, -3.4), (10.5, 0), (9, 3.4), (5, 5.2), (-2, 4.5)], head)
    h.poly([(1, -2.6), (7, -2.4), (8, 0), (7, 2.4), (1, 2.6)], glow if realm in ('genesis', 'pale', 'hollow') else head)
    h.box(-3.4, -0.8, -3.2, 3.2, trim)
    h.gem(3.2, 0, 1.4, glow)
    return s


# ================================================================================================ materials, 32 x 32
def ingot(body, inlay, extra=None):
    """A bar seen from above and in front: a bright top, a darker front face and a darkest end."""
    s = Sprite(32, 31)
    base = M[body].tones[2]
    front, end = Mat(tuple(int(c * 0.78) for c in base)), Mat(tuple(int(c * 0.62) for c in base))
    s.poly([(4, 15), (19, 8), (29, 12), (14, 20)], body)
    s.poly([(4, 15), (14, 20), (14, 26), (3, 21)], end)
    s.poly([(14, 20), (29, 12), (29, 18), (14, 26)], front)
    s.line((9, 15), (20, 10.5), 1.2, inlay)
    s.line((17, 21.5), (26, 16.5), 1.0, inlay)
    if extra:
        extra(s)
    return s


def crystal(mats, pts=((16, 28, 4.5, 23), (10, 28, 3, 14), (22, 28, 3.2, 16))):
    s = Sprite(32, 32)
    for i, (x, y, w, h) in enumerate(pts[::-1]):
        m = mats[i % len(mats)]
        s.poly([(x - w, y), (x - w, y - h * 0.7), (x, y - h), (x + w, y - h * 0.7), (x + w, y)], m)
        s.poly([(x - w * 0.3, y - 1), (x - w * 0.3, y - h * 0.65), (x, y - h * 0.85), (x + w * 0.2, y - h * 0.6), (x + w * 0.2, y - 1)], m)
    return s


def lump(body, speck, seed):
    s = Sprite(32, seed)
    s.poly([(6, 20), (9, 10), (17, 6), (25, 9), (27, 18), (22, 26), (12, 26)], body)
    s.poly([(10, 18), (12, 11), (18, 9), (23, 12), (23, 18), (18, 22)], body)
    for (x, y, r) in [(13, 13, 2.2), (20, 17, 1.8), (16, 21, 1.4), (22, 11, 1.2)]:
        s.gem(x, y, r, speck)
    return s


def living_root_fiber():
    s = Sprite(32, 33)
    for k, (dx, m) in enumerate([(-3, 'bark'), (0, 'wood'), (3, 'bark'), (1.5, 'vine')]):
        s.path([(6 + dx, 27), (10 + dx, 20), (15 + dx, 14), (20 + dx * 0.5, 9), (26 + dx * 0.4, 5)], 2.2 if m != 'vine' else 1.2, m)
    s.line((10, 14), (16, 22), 4, 'gold')
    for (x, y) in [(24, 4), (27, 9)]:
        s.poly([(x, y), (x + 3, y - 1), (x + 2, y + 2)], 'leaf')
    s.ellipse(12, 23, 1.2, 1.2, 'verdant')
    return s


def caged_soul_ember():
    s = Sprite(32, 34)
    s.rect(9, 7, 23, 9, 'black')
    s.rect(14, 3, 18, 7, 'black')
    s.ellipse(16, 18, 6, 7, 'soul')
    s.ellipse(16, 19, 3, 4, 'white')
    for x in (9, 13, 19, 23):
        s.rect(x - 0.8, 9, x + 0.8, 27, 'black')
    s.rect(8, 26, 24, 29, 'black')
    s.rect(9, 9, 23, 10.5, 'gold')
    s.rect(9, 25, 23, 26.5, 'gold')
    return s


def frozen_black_flame_core():
    s = Sprite(32, 35)
    s.poly([(16, 3), (28, 9), (28, 23), (16, 29), (4, 23), (4, 9)], 'ice')
    s.poly([(16, 7), (24, 11), (24, 21), (16, 25), (8, 21), (8, 11)], 'abyss')
    s.poly([(16, 9), (20, 16), (18, 22), (14, 22), (12, 16)], 'void_p')
    s.poly([(16, 13), (18, 18), (16, 21), (14, 18)], 'night')
    for (x, y) in [(4, 9), (28, 9), (16, 3)]:
        s.gem(x, y, 1.6, 'ice_g')
    return s


def amber_venom_vial():
    s = Sprite(32, 36)
    s.ellipse(16, 20, 8.5, 8.5, 'frost')
    s.rect(13, 6, 19, 13, 'frost')
    s.ellipse(16, 21.5, 6.5, 6, 'amber')
    s.rect(12.5, 3, 19.5, 7, 'wood')
    s.rect(11, 9, 21, 10.5, 'gold')
    s.gem(16, 21, 2, 'scarlet_g')
    s.ellipse(13, 17, 1.2, 1.2, 'white')
    return s


def temporal_core():
    s = Sprite(32, 37)
    for k in range(10):
        a = k * math.pi / 5
        s.gem(16 + 11 * math.cos(a), 16 + 11 * math.sin(a), 2.6, 'brass')
    s.ellipse(16, 16, 11, 11, 'brass')
    s.ellipse(16, 16, 8, 8, 'black')
    s.gem(16, 16, 5.5, 'chrono_g')
    s.gem(16, 16, 2.2, 'star')
    s.line((16, 16), (16, 9), 1, 'gold')
    return s


def pearl():
    s = Sprite(32, 38)
    s.ellipse(16, 17, 10, 10, 'pearl')
    s.ellipse(13, 14, 3, 3, 'white')
    s.ellipse(19, 20, 2.5, 2.5, 'teal')
    return s


def spore_cluster():
    s = Sprite(32, 39)
    for (x, y, r, m) in [(11, 20, 6, 'myc'), (21, 21, 5.5, 'myc'), (16, 12, 6.5, 'myc_g'), (9, 11, 3.5, 'myc_g'), (23, 12, 3.2, 'myc')]:
        s.ellipse(x, y, r, r, m)
    for (x, y) in [(15, 10), (20, 19), (10, 18)]:
        s.ellipse(x, y, 1.2, 1.2, 'star')
    return s


def fractured_genesis():
    s = Sprite(32, 40)
    s.poly([(16, 4), (27, 9), (16, 14), (5, 9)], 'genesis')
    s.poly([(5, 9), (16, 14), (16, 28), (5, 22)], 'abyss')
    s.poly([(16, 14), (27, 9), (27, 22), (16, 28)], 'black')
    s.path([(9, 14), (11, 18), (9, 21)], 1, 'star')
    s.path([(22, 13), (20, 17), (23, 21), (21, 24)], 1, 'star')
    s.path([(12, 8), (16, 9), (19, 7)], 1, 'gold')
    for (x, y, m) in [(4, 4, 'genesis'), (28, 3, 'black'), (29, 27, 'genesis'), (3, 28, 'star')]:
        s.gem(x, y, 1.8, m)
    return s


def sky_crystal():
    return crystal(['sky', 'sky_m', 'sky'], ((16, 29, 4.5, 26), (9, 28, 3, 15), (23, 28, 3, 13)))


def rime_crystal():
    return crystal(['ice_g', 'ice', 'frost'], ((15, 29, 4, 24), (9, 29, 3.2, 17), (22, 29, 3.4, 20)))


def scarlet_shard():
    return crystal(['scarlet_g', 'scarlet'], ((17, 29, 5, 25), (10, 29, 3, 12)))


def _bar(gem):
    def f(s):
        s.gem(17, 12.5, 2.0, gem)
    return f


MATERIALS = {   # id -> sprite
    'verdantite_ingot': lambda: ingot('verdant_m', 'verdant', _bar('verdant')),
    'living_root_fiber': living_root_fiber,
    'stormglass_shard': sky_crystal,                          # shown as the Sky Crystal Shard
    'aetherium_ingot': lambda: ingot('aether', 'sky', _bar('gem_c')),
    'soulsteel_ingot': lambda: ingot('soulsteel', 'soul', _bar('ember')),
    'caged_soul_ember': caged_soul_ember,
    'tidestone_shard': pearl,                                 # shown as the Abyssal Pearl
    'tidesteel_ingot': lambda: ingot('tidesteel', 'teal_g', _bar('pearl')),
    'rime_crystal': rime_crystal,
    'frozen_black_flame_core': frozen_black_flame_core,
    'sunglass_shard': scarlet_shard,                          # shown as the Scarlet Shard
    'amber_venom_vial': amber_venom_vial,
    'chronite_ingot': lambda: ingot('brass', 'chrono_g', _bar('chrono_g')),
    'temporal_core': temporal_core,
    'bloomspore': spore_cluster,                              # shown as the Spore Cluster
    'mycelial_ingot': lambda: ingot('myc_ingot', 'myc_g', _bar('myc_g')),
    'genesis_ingot': lambda: ingot('genesis', 'gold', lambda s: [s.gem(15.5 + i * 1.5, 22.8 - i * 0.8, 0.9, g) for i, g in enumerate(GEMS)]),
    'fractured_genesis': fractured_genesis,
    'verdant_shard': lambda: lump('moss', 'verdant', 41),      # raw verdantite
    'emberheart': lambda: lump('soulsteel', 'soul', 42),       # raw soulsteel
    'chronite_shard': lambda: lump('dark', 'chrono_g', 43),    # raw chronite
}


# ================================================================================================ ores, 16 x 16
ORE = {   # block id -> host stone, mineral materials
    'verdant_ore': ('stone', ['verdant', 'verdant_m']), 'stormglass_ore': ('stone', ['sky', 'white']),
    'emberheart_ore': ('deepslate', ['soul', 'ember']), 'tidestone_ore': ('deepslate', ['teal_g', 'pearl']),
    'rime_ore': ('frost', ['void_p', 'ice_g']), 'sunglass_ore': ('rust', ['scarlet_g', 'black']),
    'chronite_ore': ('deepslate', ['chrono_g', 'brass']), 'bloomspore_ore': ('stone', ['myc_g', 'myc']),
}


def ore(block):
    host, mins = ORE[block]
    s = Sprite(16, sum(map(ord, block)))
    s.rect(-1, -1, 17, 17, host if host != 'frost' else 'ice')
    s.rect(-1, -1, 17, 17, host if host != 'frost' else 'ice')
    spots = [(4, 4, 2.2), (11, 3, 1.6), (12, 10, 2.4), (4, 11, 1.8), (8, 8, 1.3)]
    for i, (x, y, r) in enumerate(spots):
        s.gem(x, y, r, mins[i % len(mins)])
    return s


# ================================================================================================ armor icons, 32 x 32
ICON = {   # base, trim, glow, flourish
    'grove': ('bark', 'moss', 'verdant', 'leaves'), 'skyreach': ('white', 'sky_m', 'sky', 'crystal'),
    'hollow': ('black', 'gold', 'ember', 'crown'), 'drowned': ('teal', 'pearl', 'teal_g', 'antler'),
    'pale': ('ice', 'gold', 'void_p', 'hood'), 'scarlet': ('scarlet', 'gold', 'amber', 'wings'),
    'clockwork': ('black', 'brass', 'chrono_g', 'gear'), 'mycelial': ('stalk', 'myc', 'myc_g', 'cap'),
    'genesis': ('genesis', 'gold', 'star', 'genesis'),
}


def helmet(realm):
    base, trim, glow, fl = ICON[realm]
    s = Sprite(32, 51)
    if fl == 'antler':
        for sg in (-1, 1):
            s.path([(16 + sg * 6, 12), (16 + sg * 10, 6), (16 + sg * 12, 1)], 2, 'pearl', 1)
            s.path([(16 + sg * 9, 7), (16 + sg * 14, 6)], 1.4, 'coral')
    if fl in ('crown', 'genesis'):
        for x in (8, 12, 16, 20, 24):
            s.poly([(x - 2, 10), (x, 3 if x == 16 else 5), (x + 2, 10)], trim)
    if fl == 'crystal':
        for sg in (-1, 1):
            s.poly([(16 + sg * 7, 12), (16 + sg * 14, 2), (16 + sg * 10, 13)], glow)
    if fl == 'hood':
        s.poly([(5, 28), (6, 10), (16, 3), (26, 10), (27, 28)], 'frost')
    if fl == 'wings':
        for sg in (-1, 1):
            s.poly([(16 + sg * 8, 14), (16 + sg * 15, 5), (16 + sg * 13, 18)], 'glass_r')
    if fl == 'cap':
        s.ellipse(16, 10, 13, 7, 'myc')
    s.poly([(7, 26), (7, 13), (11, 8), (21, 8), (25, 13), (25, 26), (20, 26), (19, 20), (13, 20), (12, 26)], base)
    s.rect(7, 13, 25, 15.5, trim)
    s.rect(9, 16, 23, 21, 'abyss')                                    # the face recess, two slanted eyes scowling in it
    s.poly([(10, 17), (15, 18.5), (15, 20), (10, 18.5)], glow)
    s.poly([(22, 17), (17, 18.5), (17, 20), (22, 18.5)], glow)
    s.rect(11, 21, 12.2, 24, 'bone')
    s.rect(19.8, 21, 21, 24, 'bone')
    s.gem(16, 11, 2, glow if fl != 'genesis' else 'gem_r')
    if fl == 'leaves':
        for (x, y) in [(8, 9), (22, 7), (25, 11)]:
            s.poly([(x, y), (x + 4, y - 2), (x + 3, y + 2)], 'leaf')
    if fl == 'gear':
        s.ellipse(16, 6, 4, 4, trim)
        s.gem(16, 6, 1.6, glow)
    if fl == 'cap':
        s.ellipse(16, 9, 12, 5, 'myc')
        for x in (9, 16, 23):
            s.ellipse(x, 8, 1.2, 1.2, glow)
    return s


def chestplate(realm):
    base, trim, glow, fl = ICON[realm]
    s = Sprite(32, 52)
    s.poly([(3, 7), (11, 4), (16, 7), (21, 4), (29, 7), (29, 15), (25, 15), (25, 28), (7, 28), (7, 15), (3, 15)], base)
    for sg in (-1, 1):                                                 # pauldrons, each with a horn sweeping up and out
        x = 16 + sg * 11
        s.poly([(x - 5, 11), (x - 5, 6), (x, 3), (x + 5, 6), (x + 5, 11)], trim)
        s.poly([(x + sg * 1, 6), (x + sg * 5, -0.5), (x + sg * 7, 0.5), (x + sg * 4.5, 7)], 'black')
    s.rect(9, 21, 23, 23, trim)
    s.poly([(9, 24), (16, 27), (23, 24), (23, 25.5), (16, 28.5), (9, 25.5)], trim)
    s.gem(16, 14, 3.2, glow)
    if fl == 'genesis':
        for i, gm in enumerate(GEMS):
            a = i * math.pi / 4
            s.gem(16 + 5.6 * math.cos(a), 14 + 5.6 * math.sin(a), 1.1, gm)
    if fl in ('crown', 'genesis', 'crystal'):
        for sg in (-1, 1):
            s.poly([(16 + sg * 9, 4), (16 + sg * 13, -1), (16 + sg * 12, 5)], glow if fl == 'crystal' else trim)
    if fl == 'leaves':
        for (x, y) in [(4, 4), (26, 3)]:
            s.poly([(x, y), (x + 4, y - 2), (x + 3, y + 2)], 'leaf')
    if fl == 'gear':
        s.ellipse(16, 14, 4.2, 4.2, trim)
        s.gem(16, 14, 2.4, glow)
    return s


def leggings(realm):
    base, trim, glow, fl = ICON[realm]
    s = Sprite(32, 53)
    s.poly([(7, 4), (25, 4), (26, 28), (19, 28), (16, 13), (13, 28), (6, 28)], base)
    s.rect(6.5, 4, 25.5, 7.5, trim)
    s.gem(16, 6, 1.8, glow)
    for x in (10, 22):
        s.rect(x - 2.5, 16, x + 2.5, 19, trim)
    if fl in ('crown', 'scarlet', 'pale', 'genesis', 'hood', 'wings'):
        s.poly([(13, 8), (19, 8), (18, 18), (14, 18)], 'cloth_r' if fl in ('crown', 'wings') else glow if fl == 'genesis' else 'frost')
    return s


def boots(realm):
    base, trim, glow, fl = ICON[realm]
    s = Sprite(32, 54)
    for x0 in (3, 17):
        s.poly([(x0 + 1, 10), (x0 + 9, 10), (x0 + 9, 22), (x0 + 13, 24), (x0 + 13, 28), (x0, 28), (x0, 22)], base)
        s.rect(x0, 10, x0 + 10, 13, trim)
        s.rect(x0, 25.5, x0 + 13, 28, trim)
        s.gem(x0 + 5, 17, 1.6, glow)
        if fl in ('crystal', 'wings'):
            s.poly([(x0 + 1, 12), (x0 - 2, 6), (x0 + 4, 11)], glow if fl == 'crystal' else 'glass_r')
    return s


ICONS = {'helmet': helmet, 'chestplate': chestplate, 'leggings': leggings, 'boots': boots}
