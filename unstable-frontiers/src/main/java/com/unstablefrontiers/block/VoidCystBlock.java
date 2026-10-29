package com.unstablefrontiers.block;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * A swollen pod of rift growth. In the observatory's coolant vaults these are what Lumen Mites hatch from: every cyst
 * still whole is one more reinforcement (the brood fights count them), so smashing them ends the hatching sooner.
 */
public class VoidCystBlock extends Block {
    public static final MapCodec<VoidCystBlock> CODEC = simpleCodec(VoidCystBlock::new);
    private static final VoxelShape SHAPE = Block.box(2, 0, 2, 14, 13, 14);

    public VoidCystBlock(Properties p) {
        super(p);
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return SHAPE;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource r) {
        if (r.nextInt(4) == 0) {
            level.addParticle(ParticleTypes.GLOW, pos.getX() + 0.2D + r.nextDouble() * 0.6D, pos.getY() + 0.9D,
                    pos.getZ() + 0.2D + r.nextDouble() * 0.6D, 0, 0.01D, 0);
        }
    }
}
