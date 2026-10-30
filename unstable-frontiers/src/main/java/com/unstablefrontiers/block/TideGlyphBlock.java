package com.unstablefrontiers.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

/**
 * A carved route marker. The old surveyors set them along the ways between their stations. To the naked eye it is
 * weathered stone; through Abyssal Goggles it glows (the client draws the glow only for a wearer).
 */
public class TideGlyphBlock extends Block {
    public TideGlyphBlock(Properties p) {
        super(p);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource r) {
        if (com.unstablefrontiers.client.DrownedClientHooks.seesGlyphs()) {
            for (int i = 0; i < 2; i++) {
                level.addAlwaysVisibleParticle(ParticleTypes.GLOW, pos.getX() + r.nextDouble(), pos.getY() + 1.0D + r.nextDouble() * 0.6D,
                        pos.getZ() + r.nextDouble(), 0, 0.03D, 0);
            }
            if (r.nextInt(3) == 0) {
                level.addAlwaysVisibleParticle(ParticleTypes.END_ROD, pos.getX() + 0.5D, pos.getY() + 1.4D, pos.getZ() + 0.5D, 0, 0.12D, 0);
            }
        }
    }
}
