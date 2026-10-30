package com.unstablefrontiers.drowned;

import com.unstablefrontiers.abyss.AbyssTerrain;
import java.util.ArrayList;
import java.util.List;

/**
 * The Drowned Expanse's sea floor: a flooded world from y 0 to the surface at {@link #SURFACE}. Bright reef shallows around
 * the arrival station sink outward through kelp forests to the dim Sunken Reach, and a trench (the Blackwater) cuts across
 * the south to depths of 270 blocks. Five fixed places sit on levelled pads; glyph posts mark the routes between them;
 * breath vents dot the floor everywhere. Pure maths with no game state: the same in every world, and previewable offline
 * (run {@link #main} for a map).
 */
public final class DrownedTerrain {
    /** The top water layer; air above it. */
    public static final int SURFACE = 299;
    public static final int MIN_Y = 0;
    public static final int HEIGHT = 320;
    /** Below this the deep begins: a basic rig drains three times as fast. */
    public static final int DEEP_LINE = 100;
    public static final int SHALLOWS = 0, KELPWOOD = 1, REACH = 2, TRENCH = 3;

    public record Anchor(String name, int x, int z, int radius, int floor) {}

    public static final Anchor TIDEWATCH = new Anchor("tidewatch", 0, 0, 22, 262);
    public static final Anchor DEEPWORK = new Anchor("deepwork", -330, 150, 26, 196);
    public static final Anchor CHOIR = new Anchor("choir", 300, -250, 30, 158);
    public static final Anchor WRECK = new Anchor("wreck", -150, -560, 30, 112);
    public static final Anchor VAULT = new Anchor("vault", 90, -800, 40, 30);
    public static final Anchor[] ANCHORS = {TIDEWATCH, DEEPWORK, CHOIR, WRECK, VAULT};
    private static final Anchor[][] ROUTES = {{TIDEWATCH, DEEPWORK}, {TIDEWATCH, CHOIR}, {DEEPWORK, WRECK}, {CHOIR, WRECK}, {WRECK, VAULT}};
    private static final double[][] TRENCH_LINE = {{-560, -400}, {-160, -610}, {90, -800}, {520, -840}};
    private static final double TRENCH_HALF = 60;
    public static final int POST_SPACING = 24;
    public static final List<int[]> POSTS = posts();

    private DrownedTerrain() {}

    static double noise(double x, double z, long seed) {
        return AbyssTerrain.noise(x, z, seed);
    }

    static double fbm(double x, double z, long seed, int octaves) {
        return AbyssTerrain.fbm(x, z, seed, octaves);
    }

    /** A 3D value noise, for the caves. */
    static double noise3(double x, double y, double z, long seed) {
        long iy = (long) Math.floor(y);
        double fy = y - iy;
        double uy = fy * fy * (3 - 2 * fy);
        double a = noise(x + iy * 17.31, z - iy * 9.77, seed), b = noise(x + (iy + 1) * 17.31, z - (iy + 1) * 9.77, seed);
        return a + (b - a) * uy;
    }

    public static double hash(int x, int y, int z, long salt) {
        return AbyssTerrain.noise(x * 1.618 + y * 7.1, z * 1.414 - y * 3.3, salt) * 0.5 + rnd(x, y, z, salt) * 0.5;
    }

    static double rnd(int x, int y, int z, long salt) {
        long h = (x * 0x9E3779B97F4A7C15L) ^ (z * 0xC2B2AE3D27D4EB4FL) ^ (y * 0x27D4EB2F165667C5L) ^ (salt * 0x165667B19E3779F9L);
        h ^= h >>> 31;
        h *= 0xBF58476D1CE4E5B9L;
        h ^= h >>> 27;
        h *= 0x94D049BB133111EBL;
        h ^= h >>> 31;
        return (h >>> 11) * 0x1.0p-53;
    }

    static double smooth(double e0, double e1, double v) {
        double t = Math.max(0, Math.min(1, (v - e0) / (e1 - e0)));
        return t * t * (3 - 2 * t);
    }

    /** Distance from (x, z) to the trench's centre line. */
    public static double trenchDistance(double x, double z) {
        double best = Double.MAX_VALUE;
        for (int i = 0; i < TRENCH_LINE.length - 1; i++) {
            double ax = TRENCH_LINE[i][0], az = TRENCH_LINE[i][1], bx = TRENCH_LINE[i + 1][0], bz = TRENCH_LINE[i + 1][1];
            double dx = bx - ax, dz = bz - az;
            double t = Math.max(0, Math.min(1, ((x - ax) * dx + (z - az) * dz) / (dx * dx + dz * dz)));
            best = Math.min(best, Math.hypot(x - (ax + dx * t), z - (az + dz * t)));
        }
        return best + (noise(x / 40.0, z / 40.0, 811) - 0.5) * 22;
    }

    /** The floor's top block y at a column (before caves). */
    public static int floor(int x, int z) {
        double d = Math.hypot(x, z);
        double base = 266 - 124 * Math.pow(Math.max(0, Math.min(1, (d - 110) / 430)), 1.15);
        double relief = (fbm(x / 110.0, z / 110.0, 301, 3) - 0.5) * 30 + (fbm(x / 26.0, z / 26.0, 303, 2) - 0.5) * 8;
        relief *= 0.45 + 0.55 * smooth(150, 320, d);
        double f = base + relief;
        // seamounts in the Reach: tall rock stacks rising out of the dim
        double stack = fbm(x / 46.0, z / 46.0, 307, 2);
        if (d > 330 && stack > 0.74) {
            f += Math.min(70, (stack - 0.74) * 520);
        }
        // the Blackwater trench
        double td = trenchDistance(x, z);
        if (td < TRENCH_HALF * 1.6) {
            double bottom = 24 + noise(x / 30.0, z / 30.0, 309) * 12;
            double wall = 1 - smooth(TRENCH_HALF * 0.45, TRENCH_HALF * 1.25, td);
            // terraced walls: ledges every 18 blocks
            double terr = Math.floor((f - bottom) * (1 - wall) / 18.0) * 18.0;
            f = Math.min(f, bottom + terr + (f - bottom) * (1 - wall) * 0.08);
        }
        // levelled pads under the places, blended into the floor around them
        for (Anchor a : ANCHORS) {
            double ad = Math.hypot(x - a.x, z - a.z);
            if (ad < a.radius + 30) {
                double k = 1 - smooth(a.radius, a.radius + 30, ad);
                f = f + (a.floor - f) * k;
            }
        }
        return (int) Math.max(MIN_Y + 6, Math.min(SURFACE - 10, Math.round(f)));
    }

    /** A cave tunnel (water-filled) at this block? Only in the floor's upper layers, never under the places. */
    public static boolean cave(int x, int y, int z, int floor) {
        if (y > floor - 3 || y < floor - 28 || y < 8) {
            return false;
        }
        for (Anchor a : ANCHORS) {
            if (Math.hypot(x - a.x, z - a.z) < a.radius + 12) {
                return false;
            }
        }
        double v = Math.abs(noise3(x / 34.0, y / 14.0, z / 34.0, 313) - 0.5);
        double w = Math.abs(noise3(x / 21.0, y / 11.0, z / 21.0, 317) - 0.5);
        return v < 0.035 && w < 0.2 && Math.hypot(x, z) > 140;
    }

    public static int region(int x, int z, int floor) {
        if (trenchDistance(x, z) < TRENCH_HALF * 1.1 || floor < 70) {
            return TRENCH;
        }
        if (floor >= 236) {
            return SHALLOWS;
        }
        if (floor >= 188) {
            return KELPWOOD;
        }
        return REACH;
    }

    /** A breath vent's floor column in this 40x40 cell, or null: one per cell, never on a place's pad. */
    public static int[] ventIn(int cx, int cz) {
        int x = cx * 40 + 6 + (int) (rnd(cx, 0, cz, 401) * 28);
        int z = cz * 40 + 6 + (int) (rnd(cx, 1, cz, 401) * 28);
        for (Anchor a : ANCHORS) {
            if (Math.hypot(x - a.x, z - a.z) < a.radius + 4) {
                return null;
            }
        }
        return new int[] {x, z};
    }

    public static boolean isVent(int x, int z) {
        int[] v = ventIn(Math.floorDiv(x, 40), Math.floorDiv(z, 40));
        return v != null && v[0] == x && v[1] == z;
    }

    private static List<int[]> posts() {
        List<int[]> out = new ArrayList<>();
        for (Anchor[] r : ROUTES) {
            double dx = r[1].x - r[0].x, dz = r[1].z - r[0].z;
            double len = Math.hypot(dx, dz);
            int n = (int) (len / POST_SPACING);
            for (int i = 1; i < n; i++) {
                double t = i / (double) n;
                double px = r[0].x + dx * t, pz = r[0].z + dz * t;
                // keep posts off the pads themselves
                boolean onPad = false;
                for (Anchor a : ANCHORS) {
                    onPad |= Math.hypot(px - a.x, pz - a.z) < a.radius + 6;
                }
                if (!onPad) {
                    out.add(new int[] {(int) Math.round(px), (int) Math.round(pz)});
                }
            }
        }
        return out;
    }

    public static List<int[]> postsNear(int chunkX, int chunkZ) {
        List<int[]> out = new ArrayList<>();
        for (int[] p : POSTS) {
            if (p[0] >> 4 == chunkX && p[1] >> 4 == chunkZ) {
                out.add(p);
            }
        }
        return out;
    }

    public static Anchor nearest(double x, double z) {
        Anchor best = TIDEWATCH;
        double bd = Double.MAX_VALUE;
        for (Anchor a : ANCHORS) {
            double d = Math.hypot(x - a.x, z - a.z);
            if (d < bd) {
                bd = d;
                best = a;
            }
        }
        return best;
    }

    /** Offline map: java DrownedTerrain out.png [size] (needs only the JDK). */
    public static void main(String[] args) throws Exception {
        int size = args.length > 1 ? Integer.parseInt(args[1]) : 1000;
        int x0 = -650, z0 = -950, span = 1300;
        java.awt.image.BufferedImage img = new java.awt.image.BufferedImage(size, size, java.awt.image.BufferedImage.TYPE_INT_RGB);
        for (int py = 0; py < size; py++) {
            for (int px = 0; px < size; px++) {
                int x = x0 + px * span / size, z = z0 + py * span / size;
                int f = floor(x, z);
                int reg = region(x, z, f);
                double l = f / 300.0;
                int[] c = switch (reg) {
                    case SHALLOWS -> new int[] {70, 190, 200};
                    case KELPWOOD -> new int[] {40, 130, 90};
                    case REACH -> new int[] {40, 70, 130};
                    default -> new int[] {30, 25, 60};
                };
                int r = (int) (c[0] * (0.35 + 0.8 * l)), g = (int) (c[1] * (0.35 + 0.8 * l)), b = (int) (c[2] * (0.35 + 0.8 * l));
                if (isVent(x, z)) {
                    r = g = b = 255;
                }
                img.setRGB(px, py, (Math.min(255, r) << 16) | (Math.min(255, g) << 8) | Math.min(255, b));
            }
        }
        java.awt.Graphics2D gr = img.createGraphics();
        gr.setColor(java.awt.Color.YELLOW);
        for (int[] p : POSTS) {
            int px = (p[0] - x0) * size / span, py = (p[1] - z0) * size / span;
            gr.fillRect(px - 1, py - 1, 3, 3);
        }
        gr.setColor(java.awt.Color.WHITE);
        for (Anchor a : ANCHORS) {
            int px = (a.x - x0) * size / span, py = (a.z - z0) * size / span, rr = a.radius * size / span;
            gr.drawOval(px - rr, py - rr, rr * 2, rr * 2);
            gr.drawString(a.name + " " + a.floor, px + rr + 2, py);
        }
        javax.imageio.ImageIO.write(img, "png", new java.io.File(args[0]));
        // a section along x = 0 from the station south across the trench
        java.awt.image.BufferedImage sec = new java.awt.image.BufferedImage(size, 320, java.awt.image.BufferedImage.TYPE_INT_RGB);
        for (int px = 0; px < size; px++) {
            int z = 100 - px * 1000 / size, x = 40;
            int f = floor(x, z);
            for (int y = 0; y < 320; y++) {
                int col = y > SURFACE ? 0xA0C8E8 : y > f ? (y > 236 ? 0x2C7FA8 : y > 150 ? 0x1C5277 : y > DEEP_LINE ? 0x123352 : 0x0A1A2E)
                        : cave(x, y, z, f) ? 0x0E2A40 : 0x555048;
                sec.setRGB(px, 319 - y, col);
            }
        }
        javax.imageio.ImageIO.write(sec, "png", new java.io.File(args[0].replace(".png", "_section.png")));
    }
}
