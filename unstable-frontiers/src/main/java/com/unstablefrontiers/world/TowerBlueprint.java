package com.unstablefrontiers.world;

import com.unstablefrontiers.UnstableFrontiers;
import javax.annotation.Nullable;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ChestBlock;
import net.minecraft.world.level.block.EndRodBlock;
import net.minecraft.world.level.block.LadderBlock;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The three-floor cage tower, as a pure function from local coordinates to a block. Local x and z run 0..24 across the
 * footprint, local y 0 is the base platform. Everything inside the footprint above the platform that is not part of the
 * tower is air, so terrain never fills a cage.
 *
 * <pre>
 *  y 45..61  crown: an open cage arena with the vault, a lit roof and four lit spires (the landmark)
 *  y 31..45  floor 2, the Aerie        (inset 4, flying predators)
 *  y 17..31  floor 1, the Hatchery     (inset 3, nest defenders)
 *  y  3..17  floor 0, the Swarm Pen    (inset 2, ground insects)
 *  y  0..2   base platform and plinth, stairs up from the south
 * </pre>
 * Each cage is narrower than the one below, so the tower steps in and every step is a walkable ledge. Ways in: the south
 * door, a ladder up the iron spine on the east face with a bridge to every floor, a ladder inside each floor up through a
 * hole in the ceiling, bent-bar gaps in every wall, or simply breaking the bars. Nothing is unbreakable.
 */
public final class TowerBlueprint {
    public static final int SIZE = 25;
    public static final int C = 12;
    public static final int FLOOR_H = 14;
    public static final int[] FLOOR_Y = {3, 17, 31};
    public static final int[] INSET = {2, 3, 4};
    public static final int CROWN_Y = 45;
    public static final int CROWN_INSET = 5;
    public static final int CROWN_ROOF = CROWN_Y + 8;
    public static final int TOP = 61;
    public static final int STAGES = 4;
    public static final String[] STAGE_NAMES = {"swarm_pen", "hatchery", "aerie", "crown"};

    /** Where each floor's inside ladder climbs to the floor above (x, z); index 2 leads to the crown. */
    private static final int[][] HOLE = {{C + 5, C + 5}, {C - 6, C - 5}, {C + 5, C - 5}};

    /** Spawn spots per stage, as offsets from the centre. Spots blocked at spawn time are skipped. */
    public static final int[][] FLOOR_SPAWNS = {{-5, 0}, {5, 0}, {0, -5}, {0, 5}, {-5, 5}, {5, -5}, {-4, -4}, {4, 4}};
    public static final int[][] CROWN_SPAWNS = {{-4, 0}, {4, 0}, {0, -4}, {0, 4}};

    private static final BlockState AIR = Blocks.AIR.defaultBlockState();
    private static final BlockState PLATFORM = Blocks.POLISHED_BLACKSTONE_BRICKS.defaultBlockState();
    private static final BlockState PLATFORM_CRACKED = Blocks.CRACKED_POLISHED_BLACKSTONE_BRICKS.defaultBlockState();
    private static final BlockState FLOOR = Blocks.DEEPSLATE_TILES.defaultBlockState();
    private static final BlockState FLOOR_CRACKED = Blocks.CRACKED_DEEPSLATE_TILES.defaultBlockState();
    private static final BlockState PILLAR = Blocks.POLISHED_BLACKSTONE.defaultBlockState();
    private static final BlockState BEAM = Blocks.CHISELED_POLISHED_BLACKSTONE.defaultBlockState();
    private static final BlockState BAND = Blocks.POLISHED_BASALT.defaultBlockState();
    private static final BlockState BARS = Blocks.IRON_BARS.defaultBlockState();
    private static final BlockState LIGHT = Blocks.SHROOMLIGHT.defaultBlockState();
    private static final BlockState PEDESTAL = Blocks.GILDED_BLACKSTONE.defaultBlockState();
    private static final BlockState CHAIN = Blocks.CHAIN.defaultBlockState();
    private static final BlockState ROD = Blocks.END_ROD.defaultBlockState().setValue(EndRodBlock.FACING, Direction.UP);
    private static final BlockState LADDER_W = Blocks.LADDER.defaultBlockState().setValue(LadderBlock.FACING, Direction.WEST);
    private static final BlockState STAIR_N = Blocks.POLISHED_BLACKSTONE_BRICK_STAIRS.defaultBlockState().setValue(StairBlock.FACING, Direction.NORTH);
    private static final BlockState CHEST = Blocks.CHEST.defaultBlockState().setValue(ChestBlock.FACING, Direction.SOUTH);
    private static final BlockState COBWEB = Blocks.COBWEB.defaultBlockState();
    private static final BlockState BONES = Blocks.BONE_BLOCK.defaultBlockState();
    private static final BlockState DIRT = Blocks.COARSE_DIRT.defaultBlockState();
    private static final BlockState EGG_SAC = Blocks.WHITE_WOOL.defaultBlockState();
    private static final BlockState NEST = Blocks.HAY_BLOCK.defaultBlockState();
    private static final BlockState MOSS = Blocks.MOSS_BLOCK.defaultBlockState();

    public static final BlockState FOUNDATION = Blocks.COBBLED_DEEPSLATE.defaultBlockState();

    private static final ResourceLocation[] LOOT = {
            UnstableFrontiers.id("chests/swarm_pen"), UnstableFrontiers.id("chests/hatchery"),
            UnstableFrontiers.id("chests/aerie"), UnstableFrontiers.id("chests/crown_vault")};

    private TowerBlueprint() {}

    /** Bottom y of a stage's fighting space (its floor slab), local. */
    public static int stageFloor(int stage) {
        return stage < 3 ? FLOOR_Y[stage] : CROWN_Y;
    }

    public static int stageInset(int stage) {
        return stage < 3 ? INSET[stage] : CROWN_INSET;
    }

    /** Which stage a local position stands in, or -1 (outside any cage, on a ladder, a ledge or the spine). */
    public static int stageAt(int lx, int ly, int lz) {
        for (int s = 0; s < STAGES; s++) {
            int lo = stageInset(s);
            int hi = SIZE - 1 - lo;
            int fy = stageFloor(s);
            int top = s < 3 ? fy + FLOOR_H - 1 : CROWN_ROOF;
            if (ly > fy && ly <= top && lx > lo && lx < hi && lz > lo && lz < hi) {
                return s;
            }
        }
        return -1;
    }

    /** The loot table of the chest at this local position, or null. */
    @Nullable
    public static ResourceLocation lootAt(int lx, int ly, int lz) {
        if (lx != C || lz != C) {
            return null;
        }
        for (int s = 0; s < 3; s++) {
            if (ly == FLOOR_Y[s] + 2) {
                return LOOT[s];
            }
        }
        return ly == CROWN_Y + 2 ? LOOT[3] : null;
    }

    /** The block at a local position, or null to leave the world as it is (outside the footprint). */
    @Nullable
    public static BlockState stateAt(int lx, int ly, int lz, int variant) {
        if (lx < 0 || lz < 0 || lx >= SIZE || lz >= SIZE || ly < 0 || ly > TOP) {
            return null;
        }
        int h = hash(lx, ly, lz, variant);

        // The iron spine on the east face with its ladder and a bridge to every stage.
        if (lx == SIZE - 1 && lz == C && ly >= 1 && ly <= CROWN_Y + 2) {
            return PILLAR;
        }
        if (lx == SIZE - 2 && lz == C && ly >= 1 && ly <= CROWN_Y + 1) {
            return LADDER_W;
        }
        for (int s = 0; s < STAGES; s++) {
            int hi = SIZE - 1 - stageInset(s);
            if (ly == stageFloor(s) && (lz == C - 1 || lz == C - 2) && lx > hi && lx <= SIZE - 2) {
                return FLOOR;
            }
        }

        // Base platform, plinth and the south stairs.
        if (ly == 0) {
            return h % 7 == 0 ? PLATFORM_CRACKED : PLATFORM;
        }
        if (lx >= C - 1 && lx <= C + 1 && ((lz == SIZE - 1 && ly == 1) || (lz == SIZE - 2 && ly == 2) || (lz == SIZE - 3 && ly == 3))) {
            return STAIR_N;
        }
        if (ly == 1 && lz == SIZE - 2 && lx >= C - 1 && lx <= C + 1) {
            return PLATFORM; // under the second stair
        }
        if (ly <= 2) {
            return lx >= 2 && lx <= 22 && lz >= 2 && lz <= 22 ? PLATFORM : AIR;
        }

        // Ledges: the top rim of each cage, outside the narrower cage above it.
        for (int s = 0; s < 3; s++) {
            int lo = INSET[s];
            int hi = SIZE - 1 - lo;
            if (ly == FLOOR_Y[s] + FLOOR_H && inSquare(lx, lz, lo, hi) && onRim(lx, lz, lo, hi)) {
                return BEAM;
            }
        }

        for (int s = 0; s < 3; s++) {
            int fy = FLOOR_Y[s];
            if (ly >= fy && ly < fy + FLOOR_H) {
                return chamber(s, lx, ly, lz, h);
            }
        }
        return crown(lx, ly, lz, h);
    }

    private static BlockState chamber(int s, int lx, int ly, int lz, int h) {
        int lo = INSET[s];
        int hi = SIZE - 1 - lo;
        int fy = FLOOR_Y[s];
        if (!inSquare(lx, lz, lo, hi)) {
            return AIR;
        }
        if (ly == fy) {
            return slab(s, lx, lz, h);
        }
        int dy = ly - fy;
        boolean cornerPillar = (lx <= lo + 1 || lx >= hi - 1) && (lz <= lo + 1 || lz >= hi - 1);
        if (cornerPillar) {
            return PILLAR;
        }
        if (onRim(lx, lz, lo, hi)) {
            if (dy == FLOOR_H - 1) {
                return BEAM;
            }
            if (s == 0 && lz == hi && lx >= C - 1 && lx <= C + 1 && dy <= 3) {
                return AIR; // the front door
            }
            if (lx == hi && (lz == C - 1 || lz == C - 2) && dy <= 3) {
                return AIR; // the door from the spine bridge
            }
            if (dy == 7) {
                return BAND;
            }
            return gap(s, lx, lz, lo, hi, dy) ? AIR : BARS;
        }
        // Inside ladder up to the floor above, on its own post.
        int[] hole = HOLE[s];
        if (lx == hole[0] && lz == hole[1]) {
            return LADDER_W;
        }
        if (lx == hole[0] + 1 && lz == hole[1]) {
            return PILLAR;
        }
        // The loot pen in the middle: a small cage you can see into from anywhere on the floor.
        if (Math.abs(lx - C) <= 2 && Math.abs(lz - C) <= 2 && dy <= 4) {
            if (lx == C && lz == C) {
                return dy == 1 ? PEDESTAL : dy == 2 ? CHEST : AIR;
            }
            boolean penRim = Math.abs(lx - C) == 2 || Math.abs(lz - C) == 2;
            if (penRim) {
                return lz == C + 2 && lx == C && dy <= 2 ? AIR : BARS;
            }
            return AIR;
        }
        return decor(s, lx, dy, lz, lo, hi, h);
    }

    private static BlockState slab(int s, int lx, int lz, int h) {
        if (s > 0) {
            int[] below = HOLE[s - 1];
            if (lx == below[0] && lz == below[1]) {
                return LADDER_W;
            }
        }
        int lo = INSET[s];
        int hi = SIZE - 1 - lo;
        if ((lx == lo + 3 || lx == hi - 3) && (lz == lo + 3 || lz == hi - 3)) {
            return LIGHT;
        }
        if (s == 0 && h % 9 == 0) {
            return DIRT;
        }
        if (s == 2 && h % 11 == 0) {
            return MOSS;
        }
        return h % 6 == 0 ? FLOOR_CRACKED : FLOOR;
    }

    private static BlockState decor(int s, int lx, int dy, int lz, int lo, int hi, int h) {
        boolean nearWall = lx <= lo + 2 || lx >= hi - 2 || lz <= lo + 2 || lz >= hi - 2;
        if (dy >= FLOOR_H - 3 && nearWall && h % 4 == 0) {
            return COBWEB;
        }
        if (dy != 1) {
            return AIR;
        }
        switch (s) {
            case 0:
                if (h % 31 == 0) return BONES;
                if (nearWall && h % 13 == 0) return COBWEB;
                break;
            case 1:
                if (h % 17 == 0) return EGG_SAC;
                if (h % 17 == 1) return COBWEB;
                break;
            default:
                if (nearWall && h % 7 == 0) return NEST;
                if (h % 37 == 0) return BONES;
                break;
        }
        return AIR;
    }

    private static BlockState crown(int lx, int ly, int lz, int h) {
        int lo = CROWN_INSET;
        int hi = SIZE - 1 - lo;
        int dy = ly - CROWN_Y;
        if (lx == C && lz == C && ly > CROWN_ROOF) {
            if (ly == CROWN_ROOF + 1) return LIGHT;
            if (ly < TOP - 1) return CHAIN;
            return ly == TOP - 1 ? LIGHT : ROD;
        }
        if (ly == CROWN_ROOF + 1 && (Math.abs(lx - C) + Math.abs(lz - C) == 1)) {
            return LIGHT;
        }
        if (!inSquare(lx, lz, lo, hi)) {
            return AIR;
        }
        if (dy == 0) {
            int[] below = HOLE[2];
            if (lx == below[0] && lz == below[1]) {
                return LADDER_W;
            }
            return h % 5 == 0 ? FLOOR_CRACKED : FLOOR;
        }
        boolean cornerPillar = (lx <= lo + 1 || lx >= hi - 1) && (lz <= lo + 1 || lz >= hi - 1);
        boolean outerCorner = (lx == lo || lx == hi) && (lz == lo || lz == hi);
        if (cornerPillar) {
            if (ly <= CROWN_ROOF + 4) return PILLAR;
            if (outerCorner && ly == CROWN_ROOF + 5) return LIGHT;
            if (outerCorner && ly == CROWN_ROOF + 6) return ROD;
            return AIR;
        }
        if (ly > CROWN_ROOF) {
            return AIR;
        }
        if (onRim(lx, lz, lo, hi)) {
            if (ly == CROWN_ROOF) return BEAM;
            if (lx == hi && (lz == C - 1 || lz == C - 2) && dy <= 3) return AIR;
            return gap(3, lx, lz, lo, hi, dy) ? AIR : BARS;
        }
        if (ly == CROWN_ROOF) {
            return lx == C || lz == C ? BEAM : AIR;
        }
        if (lx == C && lz == C) {
            return dy == 1 ? PEDESTAL : dy == 2 ? CHEST : AIR;
        }
        return AIR;
    }

    /** One bent-bar gap, two wide and three tall, per wall side; placed differently on every stage. */
    private static boolean gap(int s, int lx, int lz, int lo, int hi, int dy) {
        if (dy < 2 || dy > 4) {
            return false;
        }
        int span = Math.max(1, (hi - 4) - (lo + 3) - 1);
        for (int side = 0; side < 4; side++) {
            int a = lo + 3 + Math.floorMod(s * 7 + side * 5, span);
            boolean match = switch (side) {
                case 0 -> lz == lo && (lx == a || lx == a + 1);
                case 1 -> lz == hi && (lx == a || lx == a + 1);
                case 2 -> lx == lo && (lz == a || lz == a + 1);
                default -> lx == hi && (lz == a || lz == a + 1);
            };
            if (match) {
                return true;
            }
        }
        return false;
    }

    private static boolean inSquare(int lx, int lz, int lo, int hi) {
        return lx >= lo && lx <= hi && lz >= lo && lz <= hi;
    }

    private static boolean onRim(int lx, int lz, int lo, int hi) {
        return lx == lo || lx == hi || lz == lo || lz == hi;
    }

    private static int hash(int x, int y, int z, int variant) {
        int h = x * 73856093 ^ y * 19349663 ^ z * 83492791 ^ variant * 2654435;
        h ^= h >>> 13;
        h *= 0x5bd1e995;
        h ^= h >>> 15;
        return h & 0x7fffffff;
    }
}
