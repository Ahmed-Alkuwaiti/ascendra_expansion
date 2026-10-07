package com.aurelia.block;

import com.aurelia.registry.ModBlocks;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The Sunscar Citadel's light puzzle. A Sunwell throws a beam along its facing, one block at a time, at its own height.
 * A Sun Mirror turns it 90 degrees ("/" or "\", flipped by right-clicking it). A Sunglass Lens lets it through and is
 * charged by it. Anything with a collision shape stops it. Lenses stay charged; when every lens is lit the portal wakes.
 */
public final class SunBeam {
    private static final int MAX_STEPS = 96;
    private static final int SEARCH = 24;

    private SunBeam() {}

    /** Fires every Sunwell near the given position. */
    public static void fireNear(ServerLevel level, BlockPos near, Player player) {
        boolean any = false;
        for (BlockPos p : BlockPos.betweenClosed(near.offset(-SEARCH, -6, -SEARCH), near.offset(SEARCH, 6, SEARCH))) {
            BlockState s = level.getBlockState(p);
            if (s.is(ModBlocks.SUNWELL.get())) {
                any = true;
                fire(level, p.immutable(), s, player);
            }
        }
        if (!any && player != null) {
            player.displayClientMessage(Component.literal("The mirror turns, but there is no Sunwell near enough to light it."), true);
        }
    }

    public static void fire(ServerLevel level, BlockPos well, BlockState wellState, Player player) {
        if (!level.isDay()) {
            if (player != null) {
                player.displayClientMessage(Component.literal("The Sunwell is cold. It only gathers light while the sun is up."), true);
            }
            return;
        }
        Direction dir = wellState.getValue(SunwellBlock.FACING);
        BlockPos pos = well;
        List<BlockPos> path = new ArrayList<>();
        BlockPos lastLens = null;
        for (int i = 0; i < MAX_STEPS; i++) {
            pos = pos.relative(dir);
            if (!level.hasChunkAt(pos)) {
                break;
            }
            BlockState s = level.getBlockState(pos);
            path.add(pos);
            if (s.getBlock() instanceof SunMirrorBlock) {
                dir = SunMirrorBlock.reflect(dir, s.getValue(SunMirrorBlock.SLASH));
                continue;
            }
            if (s.getBlock() instanceof PuzzleNodeBlock node && node.kind() == PuzzleNodeBlock.Kind.LENS) {
                if (!s.getValue(PuzzleNodeBlock.FILLED)) {
                    PuzzleNodeBlock.fill(level, pos, s);
                }
                lastLens = pos;
                continue;
            }
            if (!s.getCollisionShape(level, pos).isEmpty()) {
                path.remove(path.size() - 1);
                break;
            }
        }
        for (BlockPos p : path) {
            level.sendParticles(ParticleTypes.END_ROD, p.getX() + 0.5, p.getY() + 0.5, p.getZ() + 0.5, 3, 0.15, 0.15, 0.15, 0.0);
            level.sendParticles(ParticleTypes.WAX_ON, p.getX() + 0.5, p.getY() + 0.5, p.getZ() + 0.5, 1, 0.1, 0.1, 0.1, 0.0);
        }
        level.playSound(null, well, SoundEvents.BEACON_POWER_SELECT, SoundSource.BLOCKS, 1.5f, 1.4f);
        if (player != null && lastLens == null) {
            int lenses = 0;
            int lit = 0;
            for (BlockPos p : BlockPos.betweenClosed(well.offset(-SEARCH, -6, -SEARCH), well.offset(SEARCH, 6, SEARCH))) {
                BlockState s = level.getBlockState(p);
                if (s.getBlock() instanceof PuzzleNodeBlock node && node.kind() == PuzzleNodeBlock.Kind.LENS) {
                    lenses++;
                    if (s.getValue(PuzzleNodeBlock.FILLED)) {
                        lit++;
                    }
                }
            }
            player.displayClientMessage(Component.literal("The beam strikes stone. Lenses lit: " + lit + " of " + lenses + "."), true);
        }
    }
}
