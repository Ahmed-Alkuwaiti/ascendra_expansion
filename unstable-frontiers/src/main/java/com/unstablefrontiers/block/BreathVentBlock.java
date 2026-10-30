package com.unstablefrontiers.block;

import com.unstablefrontiers.config.FrontierConfig;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

/**
 * A breath vent: a crack in the sea floor streaming air. A diving rig held in its stream (up to 10 blocks above it) refills
 * quickly (see DrownedBreathing); the stream is drawn here, on the client only.
 */
public class BreathVentBlock extends Block {
    public static final int REACH = 10;

    public BreathVentBlock(Properties p) {
        super(p);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource r) {
        int n = Math.max(1, (int) Math.round(3 * FrontierConfig.particles()));
        for (int i = 0; i < n; i++) {
            level.addAlwaysVisibleParticle(ParticleTypes.BUBBLE_COLUMN_UP, pos.getX() + 0.3D + r.nextDouble() * 0.4D, pos.getY() + 1.05D,
                    pos.getZ() + 0.3D + r.nextDouble() * 0.4D, 0, 0.6D, 0);
        }
        if (r.nextInt(4) == 0) {
            level.addParticle(ParticleTypes.BUBBLE, pos.getX() + 0.5D, pos.getY() + 1 + r.nextDouble() * REACH, pos.getZ() + 0.5D, 0, 0.2D, 0);
        }
    }
}
