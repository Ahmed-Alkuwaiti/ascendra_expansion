package com.unstablefrontiers.block;

import com.mojang.serialization.MapCodec;
import com.unstablefrontiers.drowned.DrownedTravel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SimpleWaterloggedBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * The tide gate: a sheet of moving water in a stone ring. The Sunken Gate's carries a properly equipped diver to the
 * Drowned Expanse (and tells anyone else what they still need); the Tidewatch Station's carries them home. Waterlogged by
 * default, so a gate under water leaves no air pocket.
 */
public class TideGateBlock extends Block implements SimpleWaterloggedBlock {
    public static final MapCodec<TideGateBlock> CODEC = simpleCodec(TideGateBlock::new);
    public static final BooleanProperty WATERLOGGED = BlockStateProperties.WATERLOGGED;

    public TideGateBlock(Properties p) {
        super(p);
        registerDefaultState(stateDefinition.any().setValue(WATERLOGGED, true));
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
        b.add(WATERLOGGED);
    }

    @Override
    protected FluidState getFluidState(BlockState s) {
        return s.getValue(WATERLOGGED) ? Fluids.WATER.getSource(false) : super.getFluidState(s);
    }

    @Override
    protected BlockState updateShape(BlockState s, Direction d, BlockState o, LevelAccessor level, BlockPos pos, BlockPos op) {
        if (s.getValue(WATERLOGGED)) {
            level.scheduleTick(pos, Fluids.WATER, Fluids.WATER.getTickDelay(level));
        }
        return super.updateShape(s, d, o, level, pos, op);
    }

    @Override
    protected VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return Shapes.empty();
    }

    @Override
    protected void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        if (!level.isClientSide && entity instanceof ServerPlayer p) {
            DrownedTravel.throughGate(p, pos);
        }
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource r) {
        if (r.nextInt(2) == 0) {
            level.addParticle(state.getValue(WATERLOGGED) ? ParticleTypes.BUBBLE : ParticleTypes.SPLASH, pos.getX() + r.nextDouble(),
                    pos.getY() + r.nextDouble(), pos.getZ() + r.nextDouble(), 0, 0.05D, 0);
        }
        if (r.nextInt(6) == 0) {
            level.addParticle(ParticleTypes.GLOW, pos.getX() + r.nextDouble(), pos.getY() + r.nextDouble(), pos.getZ() + r.nextDouble(), 0, 0.01D, 0);
        }
    }
}
