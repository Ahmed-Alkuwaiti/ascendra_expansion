package com.aurelia.world;

import com.aurelia.block.TideBellBlock;
import com.aurelia.registry.ModBlocks;
import com.aurelia.AureliaMod;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The extra pieces each act two arena needs on top of the standard landing pad (built by RealmTravel).
 * c is the standing level at the altar; the pad's surface is at c.y - 1 and the return Waygate is at c + (0, 0, 9).
 */
public final class ArenaBuilder {
    private ArenaBuilder() {}

    public static void decorate(ServerLevel level, Realm realm, BlockPos c) {
        switch (realm) {
            case DROWNED -> drowned(level, c);
            case PALE -> pale(level, c);
            case SCARLET -> raiseScarletPillars(level, c);
            case CLOCKWORK -> clockwork(level, c);
            case MYCELIAL -> mycelial(level, c);
            case LAST -> last(level, c);
            default -> { }
        }
    }

    /** Positions of the three Tide Bells, relative to the altar. */
    public static final int[][] BELLS = {{11, 0}, {-11, 0}, {0, -11}};

    /** The Clockwork Rift: the three arena dials, and the Master Clock on a column at the north rim (x, y, z from the altar). */
    public static final int[][] DIALS = {{9, 3}, {-9, 3}, {0, -9}};
    public static final int[] MASTER = {0, 4, -12};
    /** The Mycelial Deep: the three spore valves. */
    public static final int[][] VALVES = {{10, 2}, {-10, 2}, {0, -11}};

    /** A clock face: gold numerals and hands set into the pad, a rim of iron, three dials and the Master Clock. */
    private static void clockwork(ServerLevel level, BlockPos c) {
        BlockState gold = Blocks.GOLD_BLOCK.defaultBlockState();
        BlockState rim = Blocks.POLISHED_BLACKSTONE_BRICKS.defaultBlockState();
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        for (int dx = -14; dx <= 14; dx++) {
            for (int dz = -14; dz <= 14; dz++) {
                double d = Math.sqrt(dx * dx + dz * dz);
                if (d > 12.0 && d <= 14.0) {
                    for (int dy = -6; dy <= -1; dy++) {
                        level.setBlock(p.set(c.getX() + dx, c.getY() + dy, c.getZ() + dz), rim, 2);
                    }
                } else if (d > 10.5 && d <= 11.5) {
                    level.setBlock(p.set(c.getX() + dx, c.getY() - 1, c.getZ() + dz), Blocks.POLISHED_BLACKSTONE.defaultBlockState(), 2);
                }
            }
        }
        for (int k = 0; k < 12; k++) {
            double a = k * Math.PI / 6.0;
            level.setBlock(c.offset((int) Math.round(Math.cos(a) * 11), -1, (int) Math.round(Math.sin(a) * 11)), gold, 2);
            level.setBlock(c.offset((int) Math.round(Math.cos(a) * 13), 0, (int) Math.round(Math.sin(a) * 13)),
                    Blocks.CANDLE.defaultBlockState().setValue(net.minecraft.world.level.block.CandleBlock.LIT, true), 2);
        }
        for (int r = 2; r <= 9; r++) {
            level.setBlock(c.offset(r, -1, 0), gold, 2);
        }
        for (int r = 2; r <= 6; r++) {
            level.setBlock(c.offset(0, -1, -r), gold, 2);
        }
        for (int[] d : DIALS) {
            level.setBlock(c.offset(d[0], -1, d[1]), Blocks.CHISELED_POLISHED_BLACKSTONE.defaultBlockState(), 2);
            level.setBlock(c.offset(d[0], 0, d[1]), ModBlocks.CLOCK_DIAL.get().defaultBlockState(), 3);
        }
        for (int dy = 0; dy < MASTER[1]; dy++) {
            level.setBlock(c.offset(MASTER[0], dy, MASTER[2]), dy == MASTER[1] - 1 ? Blocks.GOLD_BLOCK.defaultBlockState() : rim, 2);
        }
        level.setBlock(c.offset(MASTER[0], MASTER[1], MASTER[2]), ModBlocks.MASTER_CLOCK.get().defaultBlockState(), 3);
    }

    /** The Mycelial Deep: veins of light in the floor, three spore valves, and fungus round the rim. */
    private static void mycelial(ServerLevel level, BlockPos c) {
        for (int k = 0; k < 10; k++) {
            double a = k * Math.PI / 5.0;
            for (int r = 3; r <= 11; r++) {
                if (r % 2 == 1) {
                    level.setBlock(c.offset((int) Math.round(Math.cos(a) * r), -1, (int) Math.round(Math.sin(a) * r)),
                            Blocks.PEARLESCENT_FROGLIGHT.defaultBlockState(), 2);
                }
            }
        }
        for (int[] v : VALVES) {
            level.setBlock(c.offset(v[0], -1, v[1]), Blocks.BONE_BLOCK.defaultBlockState(), 2);
            level.setBlock(c.offset(v[0], 0, v[1]), ModBlocks.SPORE_VALVE.get().defaultBlockState(), 3);
        }
        for (int k = 0; k < 8; k++) {
            double a = k * Math.PI / 4.0 + 0.4;
            BlockPos base = c.offset((int) Math.round(Math.cos(a) * 12), 0, (int) Math.round(Math.sin(a) * 12));
            level.setBlock(base, Blocks.MUSHROOM_STEM.defaultBlockState(), 2);
            level.setBlock(base.above(), Blocks.MUSHROOM_STEM.defaultBlockState(), 2);
            level.setBlock(base.above(2), Blocks.PURPLE_WOOL.defaultBlockState(), 2);
        }
    }

    /** Opens a ring of deep water around the pad (whatever the terrain was) so Vorath can circle, and hangs the bells. */
    private static void drowned(ServerLevel level, BlockPos c) {
        BlockState water = Blocks.WATER.defaultBlockState();
        BlockState air = Blocks.AIR.defaultBlockState();
        BlockState floor = Blocks.DARK_PRISMARINE.defaultBlockState();
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        for (int dx = -26; dx <= 26; dx++) {
            for (int dz = -26; dz <= 26; dz++) {
                int d2 = dx * dx + dz * dz;
                if (d2 <= 12 * 12 || d2 > 26 * 26) {
                    continue;
                }
                for (int dy = -14; dy <= 22; dy++) {
                    p.set(c.getX() + dx, c.getY() + dy, c.getZ() + dz);
                    if (dy == -14) {
                        if (level.getBlockState(p).isAir() || !level.getFluidState(p).isEmpty()) {
                            level.setBlock(p, floor, 2);
                        }
                    } else if (dy <= -2) {
                        level.setBlock(p, water, 2);
                    } else {
                        level.setBlock(p, air, 2);
                    }
                }
            }
        }
        // a skirt of stone under the pad so the water ring has a wall to lap against
        for (int dx = -12; dx <= 12; dx++) {
            for (int dz = -12; dz <= 12; dz++) {
                if (dx * dx + dz * dz > 12 * 12) {
                    continue;
                }
                for (int dy = -13; dy <= -7; dy++) {
                    p.set(c.getX() + dx, c.getY() + dy, c.getZ() + dz);
                    level.setBlock(p, Blocks.DARK_PRISMARINE.defaultBlockState(), 2);
                }
            }
        }
        for (int[] b : BELLS) {
            level.setBlock(c.offset(b[0], -1, b[1]), Blocks.PRISMARINE_BRICKS.defaultBlockState(), 2);
            level.setBlock(c.offset(b[0], 0, b[1]), ModBlocks.TIDE_BELL.get().defaultBlockState().setValue(TideBellBlock.NOTE, 0), 3);
        }
    }

    /** Four braziers: standing near one thaws the White Silence's cold out of you. */
    private static void pale(ServerLevel level, BlockPos c) {
        int[][] fires = {{9, 0}, {-9, 0}, {0, -9}, {-6, 7}};
        for (int[] f : fires) {
            level.setBlock(c.offset(f[0], 0, f[1]), Blocks.CAMPFIRE.defaultBlockState(), 3);
            level.setBlock(c.offset(f[0], -1, f[1]), Blocks.STONE_BRICKS.defaultBlockState(), 2);
        }
    }

    /** Kharzul's cover: four 3x3 pillars of red sandstone, rebuilt every time he wakes. */
    public static void raiseScarletPillars(ServerLevel level, BlockPos c) {
        int[][] pillars = {{7, 0}, {-7, 0}, {0, -8}, {4, 6}};
        java.util.List<net.minecraft.world.entity.player.Player> near = level.getEntitiesOfClass(
                net.minecraft.world.entity.player.Player.class, new net.minecraft.world.phys.AABB(c).inflate(16.0));
        for (int[] pl : pillars) {
            for (int dx = -1; dx <= 1; dx++) {
                for (int dz = -1; dz <= 1; dz++) {
                    for (int dy = 0; dy < 6; dy++) {
                        BlockState s = (dy == 5) ? Blocks.CHISELED_RED_SANDSTONE.defaultBlockState()
                                : (dx == 0 && dz == 0 ? Blocks.RED_SANDSTONE.defaultBlockState() : Blocks.CUT_RED_SANDSTONE.defaultBlockState());
                        BlockPos at = c.offset(pl[0] + dx, dy, pl[1] + dz);
                        // never rebuild stone inside somebody standing there
                        if (near.stream().noneMatch(pp -> pp.getBoundingBox().intersects(new net.minecraft.world.phys.AABB(at)))) {
                            level.setBlock(at, s, 2);
                        }
                    }
                }
            }
        }
    }

    // ---- the Last Realm

    /** The Realm Nodes stand this far from the altar, in realm order at 45 degree steps; the islands twice as far and more. */
    public static final int NODE_RADIUS = 22;
    public static final int ISLAND_DISTANCE = 66;

    public static BlockPos nodePos(BlockPos c, Realm realm) {
        double a = Math.toRadians(realm.ordinal() * 45.0);
        return c.offset((int) Math.round(Math.cos(a) * NODE_RADIUS), 1, (int) Math.round(Math.sin(a) * NODE_RADIUS));
    }

    /** Where the altar stands inside last_dread (x and z), and the standing level inside it (y); see tools/gen_last_dread.py. */
    private static final int DREAD_CENTRE = 104;
    private static final int DREAD_FLOOR = 90;

    /**
     * The dread first (the Abyssal Root and its Eye below, the Eight Talons, the Shattered Crown and its Heart overhead, the eight
     * Watchers, the bridges' vertebrae, the drifting wreckage), placed once; then the arena ring, its nodes and bridges round the pad,
     * and an island for every realm at the end of each bridge. The fight only ever resets the ring.
     */
    private static void last(ServerLevel level, BlockPos c) {
        place(level, "last_dread", c.offset(-DREAD_CENTRE, -DREAD_FLOOR, -DREAD_CENTRE));
        restoreLast(level, c);
        for (Realm realm : Realm.values()) {
            if (realm == Realm.LAST) {
                continue;
            }
            double a = Math.toRadians(realm.ordinal() * 45.0);
            BlockPos origin = c.offset((int) Math.round(Math.cos(a) * ISLAND_DISTANCE) - 17, -40, (int) Math.round(Math.sin(a) * ISLAND_DISTANCE) - 17);
            place(level, "last_island_" + realm.id, origin);
        }
    }

    /** Puts the arena back as it was (the Unmaker eats pieces of it). The template never touches the pad itself. */
    public static void restoreLast(ServerLevel level, BlockPos c) {
        place(level, "last_core", c.offset(-56, -40, -56));
    }

    private static void place(ServerLevel level, String name, BlockPos origin) {
        StructureTemplate template = level.getStructureManager().getOrCreate(new ResourceLocation(AureliaMod.MODID, name));
        template.placeInWorld(level, origin, origin, new StructurePlaceSettings(), level.random, 2);
    }
}
