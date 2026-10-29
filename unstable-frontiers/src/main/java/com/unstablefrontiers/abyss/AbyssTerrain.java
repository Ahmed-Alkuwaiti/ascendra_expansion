package com.unstablefrontiers.abyss;

import java.util.ArrayList;
import java.util.List;

/**
 * The Astral Abyss's shape: floating islands in three layers, five fixed places with guaranteed islands, and stepping-stone
 * routes between them. Pure maths with no game state, so it is the same in every world and identical to
 * tools/abyss/terrain.py, whose previews therefore show the real dimension. Change both together.
 */
public final class AbyssTerrain {
    /** A fixed place in the abyss. */
    public record Anchor(String name, int x, int z, int radius, int top) {}

    public record Stone(double x, double z, int y) {}

    // scale, threshold, base top y, top variation, max thickness, seed
    private static final double[][] LAYERS = {
            {50.0, 0.615, 98, 16, 34, 11},
            {88.0, 0.655, 150, 22, 24, 23},
            {22.0, 0.70, 62, 26, 7, 37},
    };
    public static final Anchor LANDING = new Anchor("landing", 0, 0, 20, 100);
    public static final Anchor STARWELL = new Anchor("starwell", 232, -148, 24, 112);
    public static final Anchor ARCHIVE = new Anchor("archive", -236, -72, 30, 122);
    public static final Anchor TETHER_SPIRE = new Anchor("tether_spire", 64, 268, 20, 92);
    public static final Anchor HOLLOW_CROWN = new Anchor("hollow_crown", 24, 560, 46, 112);
    public static final Anchor[] ANCHORS = {LANDING, STARWELL, ARCHIVE, TETHER_SPIRE, HOLLOW_CROWN};
    private static final Anchor[][] ROUTES = {{LANDING, STARWELL}, {LANDING, ARCHIVE}, {LANDING, TETHER_SPIRE}, {TETHER_SPIRE, HOLLOW_CROWN}};
    private static final double STONE_SPACING = 5.0;
    private static final double STONE_RADIUS = 1.6;
    public static final List<Stone> STONES = routeStones();

    private AbyssTerrain() {}

    static long mix(long h) {
        h ^= h >>> 31;
        h *= 0xBF58476D1CE4E5B9L;
        h ^= h >>> 27;
        h *= 0x94D049BB133111EBL;
        h ^= h >>> 31;
        return h;
    }

    static double rnd(long ix, long iz, long seed) {
        long h = mix((ix * 0x9E3779B97F4A7C15L) ^ (iz * 0xC2B2AE3D27D4EB4FL) ^ (seed * 0x165667B19E3779F9L));
        return (h >>> 11) * 0x1.0p-53;
    }

    public static double noise(double x, double z, long seed) {
        long ix = (long) Math.floor(x), iz = (long) Math.floor(z);
        double fx = x - ix, fz = z - iz;
        double ux = fx * fx * (3 - 2 * fx), uz = fz * fz * (3 - 2 * fz);
        double a = rnd(ix, iz, seed), b = rnd(ix + 1, iz, seed), c = rnd(ix, iz + 1, seed), d = rnd(ix + 1, iz + 1, seed);
        return a + (b - a) * ux + (c - a) * uz + (a - b - c + d) * ux * uz;
    }

    public static double fbm(double x, double z, long seed, int octaves) {
        double s = 0, amp = 1, norm = 0, f = 1;
        for (int i = 0; i < octaves; i++) {
            s += amp * noise(x * f, z * f, seed + i * 7919L);
            norm += amp;
            amp *= 0.5;
            f *= 2.03;
        }
        return s / norm;
    }

    /** {top, bottom} of an anchor island at this column, or null. */
    static int[] anchorProfile(int x, int z) {
        for (Anchor a : ANCHORS) {
            double d = Math.hypot(x - a.x, z - a.z);
            double rr = a.radius * (0.88 + 0.24 * noise(Math.atan2(z - a.z, x - a.x) * 2.0 + 10, 0.5, 71));
            if (d <= rr) {
                double k = 1 - Math.pow(d / rr, 2);
                int t = a.top + (d < rr - 3 ? 1 : 0) - (d < rr - 1.5 ? 0 : 1);
                double depth = 6 + (a.radius * 0.9) * Math.pow(k, 1.3) * (0.75 + 0.5 * noise(x / 9.0, z / 9.0, 73));
                return new int[] {t, t - (int) depth};
            }
        }
        return null;
    }

    /** The anchor whose clear sky covers this column, or null. */
    public static Anchor clearSky(int x, int z) {
        for (Anchor a : ANCHORS) {
            int margin = a == HOLLOW_CROWN ? 34 : 8;
            if (Math.hypot(x - a.x, z - a.z) <= a.radius + margin) {
                return a;
            }
        }
        return null;
    }

    static void layerColumns(int x, int z, List<int[]> out) {
        if (clearSky(x, z) != null) {
            return;
        }
        for (double[] l : LAYERS) {
            double scale = l[0], t = l[1], base = l[2], var = l[3], thick = l[4];
            long seed = (long) l[5];
            double m = fbm(x / scale, z / scale, seed, 4);
            if (m <= t) {
                continue;
            }
            double k = (m - t) / (1 - t);
            int top = (int) (base + (int) ((fbm(x / 150.0, z / 150.0, seed + 5, 2) - 0.5) * 2 * var + k * 7));
            double depth = 2 + thick * Math.pow(k, 0.6) * (0.65 + 0.35 * noise(x / 7.0, z / 7.0, seed + 9));
            out.add(new int[] {top, top - (int) depth});
        }
    }

    static List<Stone> routeStones() {
        List<Stone> stones = new ArrayList<>();
        for (Anchor[] r : ROUTES) {
            Anchor a = r[0], b = r[1];
            double dist = Math.hypot(b.x - a.x, b.z - a.z);
            double ux = (b.x - a.x) / dist, uz = (b.z - a.z) / dist;
            double start = a.radius - 2, end = dist - b.radius + 2;
            int n = (int) ((end - start) / STONE_SPACING);
            for (int i = 0; i <= n; i++) {
                double s = start + i * STONE_SPACING;
                double f = s / dist;
                double wob = (noise(s / 23.0, 0.5, 91) - 0.5) * 10;
                double x = a.x + ux * s - uz * wob;
                double z = a.z + uz * s + ux * wob;
                int y = (int) Math.floor(a.top + (b.top - a.top) * f + Math.sin(s / 31.0) * 3 + 0.5);
                stones.add(new Stone(x, z, y));
            }
        }
        return stones;
    }

    /** Top of a stepping stone covering this column, or Integer.MIN_VALUE. */
    static int stoneAt(int x, int z, List<Stone> near) {
        int best = Integer.MIN_VALUE;
        for (Stone s : near) {
            if (Math.abs(s.x - x) <= 2 && Math.abs(s.z - z) <= 2 && Math.hypot(s.x - x - 0.5, s.z - z - 0.5) <= STONE_RADIUS + 0.3) {
                best = Math.max(best, s.y);
            }
        }
        return best;
    }

    /** Stones that can touch the 16x16 chunk at (cx, cz). */
    public static List<Stone> stonesNear(int chunkX, int chunkZ) {
        int x0 = chunkX << 4, z0 = chunkZ << 4;
        List<Stone> out = new ArrayList<>();
        for (Stone s : STONES) {
            if (s.x >= x0 - 3 && s.x <= x0 + 19 && s.z >= z0 - 3 && s.z <= z0 + 19) {
                out.add(s);
            }
        }
        return out;
    }

    /** All solid spans {top, bottom} of a column, highest first. */
    public static List<int[]> column(int x, int z, List<Stone> near) {
        List<int[]> spans = new ArrayList<>(4);
        int[] a = anchorProfile(x, z);
        if (a != null) {
            spans.add(a);
        }
        layerColumns(x, z, spans);
        int s = stoneAt(x, z, near);
        if (s != Integer.MIN_VALUE) {
            spans.add(new int[] {s, s - 1});
        }
        spans.sort((p, q) -> q[0] != p[0] ? Integer.compare(q[0], p[0]) : Integer.compare(q[1], p[1]));
        return spans;
    }

    public static List<int[]> column(int x, int z) {
        return column(x, z, STONES);
    }

    public static void main(String[] args) {
        // parity check with tools/abyss/terrain.py: print a grid of columns
        StringBuilder sb = new StringBuilder();
        for (int x = -300; x <= 300; x += 37) {
            for (int z = -200; z <= 620; z += 41) {
                sb.append(x).append(',').append(z);
                for (int[] sp : column(x, z)) {
                    sb.append(' ').append(sp[0]).append(':').append(sp[1]);
                }
                sb.append('\n');
            }
        }
        sb.append("stones ").append(STONES.size()).append(' ').append(STONES.get(17)).append('\n');
        System.out.print(sb);
    }
}
