package com.aurelia.block;

import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.BlockHitResult;

/** The Master Clock. It cannot be wound; it shows the hour every dial near it must agree with. */
public class MasterClockBlock extends Block {

    public MasterClockBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(ClockDialBlock.HOUR, 0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(ClockDialBlock.HOUR);
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (!level.isClientSide) {
            player.displayClientMessage(Component.literal("The Master Clock reads " + ClockDialBlock.hourName(state.getValue(ClockDialBlock.HOUR))
                    + ". Its hands will not move."), true);
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }
}
