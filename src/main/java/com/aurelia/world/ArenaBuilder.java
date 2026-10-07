package com.aurelia.world;

import com.aurelia.block.TideBellBlock;
import com.aurelia.registry.ModBlocks;
import net.minecraft.core.BlockPos;
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
            default -> { }
        }
    }

    /** Positions of the three Tide Bells, relative to the altar. */
    public static final int[][] BELLS = {{11, 0}, {-11, 0}, {0, -11}};

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
        for (int[] pl : pillars) {
            for (int dx = -1; dx <= 1; dx++) {
                for (int dz = -1; dz <= 1; dz++) {
                    for (int dy = 0; dy < 6; dy++) {
                        BlockState s = (dy == 5) ? Blocks.CHISELED_RED_SANDSTONE.defaultBlockState()
                                : (dx == 0 && dz == 0 ? Blocks.RED_SANDSTONE.defaultBlockState() : Blocks.CUT_RED_SANDSTONE.defaultBlockState());
                        level.setBlock(c.offset(pl[0] + dx, dy, pl[1] + dz), s, 2);
                    }
                }
            }
        }
    }
}
