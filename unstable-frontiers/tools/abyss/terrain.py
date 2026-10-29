"""The Astral Abyss terrain, exactly as AbyssChunkGenerator.java computes it (same hashing, same noise, same numbers),
so previews of this module are previews of the real dimension. Change both together.

The abyss is designed, not seeded: every world has the same islands, so the landing, the destinations and the
stepping-stone routes between them are always where the guide says.
"""
import math

M64 = (1 << 64) - 1


def mix(h):
    h &= M64
    h ^= h >> 31
    h = (h * 0xBF58476D1CE4E5B9) & M64
    h ^= h >> 27
    h = (h * 0x94D049BB133111EB) & M64
    h ^= h >> 31
    return h


def rnd(ix, iz, seed):
    """0..1 for an integer lattice point."""
    h = mix(((ix & M64) * 0x9E3779B97F4A7C15) ^ ((iz & M64) * 0xC2B2AE3D27D4EB4F) ^ ((seed & M64) * 0x165667B19E3779F9))
    return (h >> 11) * (1.0 / (1 << 53))


def noise(x, z, seed):
    ix, iz = math.floor(x), math.floor(z)
    fx, fz = x - ix, z - iz
    ux, uz = fx * fx * (3 - 2 * fx), fz * fz * (3 - 2 * fz)
    a, b = rnd(ix, iz, seed), rnd(ix + 1, iz, seed)
    c, d = rnd(ix, iz + 1, seed), rnd(ix + 1, iz + 1, seed)
    return a + (b - a) * ux + (c - a) * uz + (a - b - c + d) * ux * uz


def fbm(x, z, seed, octaves):
    s, amp, norm, f = 0.0, 1.0, 0.0, 1.0
    for i in range(octaves):
        s += amp * noise(x * f, z * f, seed + i * 7919)
        norm += amp
        amp *= 0.5
        f *= 2.03
    return s / norm


# Island layers: (scale, threshold, base top y, top variation, max thickness, seed)
LAYERS = [
    (50.0, 0.615, 98, 16, 34, 11),     # the main shoals
    (88.0, 0.655, 150, 22, 24, 23),    # high islands
    (22.0, 0.70, 62, 26, 7, 37),       # low debris
]

# Fixed places: name -> (x, z, radius, top y). The generator gives each a guaranteed island and keeps its sky clear.
ANCHORS = {
    'landing': (0, 0, 20, 100),
    'starwell': (232, -148, 24, 112),
    'archive': (-236, -72, 30, 122),
    'tether_spire': (64, 268, 20, 92),
    'hollow_crown': (24, 560, 46, 112),
}
# Stepping-stone routes between them, for travellers without flight.
ROUTES = [('landing', 'starwell'), ('landing', 'archive'), ('landing', 'tether_spire'), ('tether_spire', 'hollow_crown')]
STONE_SPACING = 5.0
STONE_RADIUS = 1.6
MIN_Y, HEIGHT = 0, 256


def anchor_profile(x, z):
    """(top, bottom) of an anchor island at this column, or None. Bottom tapers like a hanging rock."""
    for name, (cx, cz, r, top) in ANCHORS.items():
        d = math.hypot(x - cx, z - cz)
        rr = r * (0.88 + 0.24 * noise(math.atan2(z - cz, x - cx) * 2.0 + 10, 0.5, 71))
        if d <= rr:
            k = 1 - (d / rr) ** 2
            t = top + (1 if d < rr - 3 else 0) - (0 if d < rr - 1.5 else 1)
            depth = 6 + (r * 0.9) * k ** 1.3 * (0.75 + 0.5 * noise(x / 9.0, z / 9.0, 73))
            return t, t - int(depth)
    return None


def clear_sky(x, z):
    """Anchors keep the air around them free of other islands (the arena most of all)."""
    for name, (cx, cz, r, top) in ANCHORS.items():
        margin = 34 if name == 'hollow_crown' else 8
        if math.hypot(x - cx, z - cz) <= r + margin:
            return name
    return None


def layer_columns(x, z):
    out = []
    if clear_sky(x, z):
        return out
    for scale, t, base, var, thick, seed in LAYERS:
        m = fbm(x / scale, z / scale, seed, 4)
        if m <= t:
            continue
        k = (m - t) / (1 - t)
        top = base + int((fbm(x / 150.0, z / 150.0, seed + 5, 2) - 0.5) * 2 * var + k * 7)
        depth = 2 + thick * (k ** 0.6) * (0.65 + 0.35 * noise(x / 7.0, z / 7.0, seed + 9))
        out.append((top, top - int(depth)))
    return out


def route_stones():
    """Every stepping stone: (x, z, y). Deterministic; the generator places each where it falls."""
    stones = []
    for a, b in ROUTES:
        ax, az, ar, ay = ANCHORS[a]
        bx, bz, br, by = ANCHORS[b]
        dist = math.hypot(bx - ax, bz - az)
        ux, uz = (bx - ax) / dist, (bz - az) / dist
        start, end = ar - 2, dist - br + 2
        n = int((end - start) / STONE_SPACING)
        for i in range(n + 1):
            s = start + i * STONE_SPACING
            f = s / dist
            wob = (noise(s / 23.0, 0.5, 91) - 0.5) * 10
            x = ax + ux * s - uz * wob
            z = az + uz * s + ux * wob
            y = math.floor(ay + (by - ay) * f + math.sin(s / 31.0) * 3 + 0.5)
            stones.append((x, z, y))
    return stones


STONES = route_stones()


def stone_at(x, z):
    """(top) of a stepping stone covering this column, or None."""
    best = None
    for sx, sz, sy in STONES:
        if abs(sx - x) <= 2 and abs(sz - z) <= 2 and math.hypot(sx - x - 0.5, sz - z - 0.5) <= STONE_RADIUS + 0.3:
            best = sy if best is None else max(best, sy)
    return best


def column(x, z):
    """All solid spans (top, bottom) at a column, highest first."""
    spans = []
    a = anchor_profile(x, z)
    if a:
        spans.append(a)
    spans += layer_columns(x, z)
    s = stone_at(x, z)
    if s is not None:
        spans.append((s, s - 1))
    return sorted(spans, reverse=True)


def surface(x, z):
    sp = column(x, z)
    return sp[0][0] if sp else None
