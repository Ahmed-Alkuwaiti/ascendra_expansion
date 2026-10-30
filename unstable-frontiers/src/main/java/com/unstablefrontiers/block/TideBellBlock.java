package com.unstablefrontiers.block;

import com.mojang.serialization.MapCodec;
import com.unstablefrontiers.drowned.DrownedTravel;
import com.unstablefrontiers.drowned.DeepcallerEncounter;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SimpleWaterloggedBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * A bell. A tide bell hangs in each station's shelter: ring it to mark the shelter as yours (the rift-tide returns you to
 * the last one you rang if you black out from lack of air) and to see the others you have rung; sneak and ring to travel
 * to the next. The abyssal bell (ABYSSAL) at the Sunless Vault calls the Deepcaller.
 */
public class TideBellBlock extends Block implements SimpleWaterloggedBlock {
    public static final MapCodec<TideBellBlock> CODEC = simpleCodec(p -> new TideBellBlock(p, false));
    public static final BooleanProperty WATERLOGGED = BlockStateProperties.WATERLOGGED;
    private static final VoxelShape SHAPE = Block.box(3, 2, 3, 13, 15, 13);
    private final boolean abyssal;

    public TideBellBlock(Properties p, boolean abyssal) {
        super(p);
        this.abyssal = abyssal;
        registerDefaultState(stateDefinition.any().setValue(WATERLOGGED, false));
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
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return SHAPE;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (level instanceof ServerLevel sl && player instanceof ServerPlayer sp) {
            if (abyssal) {
                DeepcallerEncounter.ring(sl, pos, sp);
            } else {
                DrownedTravel.ringBell(sl, pos, sp, sp.isShiftKeyDown());
            }
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }
}
