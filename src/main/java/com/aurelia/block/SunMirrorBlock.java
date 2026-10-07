package com.aurelia.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.BlockHitResult;

/**
 * A Sun Mirror. SLASH true is "/" (seen from above, north up: it runs from south-west to north-east), false is "\".
 * Right-click flips it, then every Sunwell nearby fires again so you can see where the light goes.
 */
public class SunMirrorBlock extends Block {
    public static final BooleanProperty SLASH = BooleanProperty.create("slash");

    public SunMirrorBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(SLASH, true));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(SLASH);
    }

    /** The direction a beam leaves a mirror, given the direction it was travelling. */
    public static Direction reflect(Direction travel, boolean slash) {
        if (slash) {
            return switch (travel) {
                case EAST -> Direction.NORTH;
                case NORTH -> Direction.EAST;
                case WEST -> Direction.SOUTH;
                case SOUTH -> Direction.WEST;
                default -> travel;
            };
        }
        return switch (travel) {
            case EAST -> Direction.SOUTH;
            case SOUTH -> Direction.EAST;
            case WEST -> Direction.NORTH;
            case NORTH -> Direction.WEST;
            default -> travel;
        };
    }

    /** A quarter turn (or any mirroring) swaps "/" and "\", so citadels placed at any rotation keep their layout. */
    @Override
    public BlockState rotate(BlockState state, Rotation rotation) {
        return rotation == Rotation.CLOCKWISE_90 || rotation == Rotation.COUNTERCLOCKWISE_90
                ? state.setValue(SLASH, !state.getValue(SLASH)) : state;
    }

    @Override
    public BlockState mirror(BlockState state, Mirror mirror) {
        return mirror == Mirror.NONE ? state : state.setValue(SLASH, !state.getValue(SLASH));
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player,
                                 InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }
        level.setBlock(pos, state.setValue(SLASH, !state.getValue(SLASH)), 3);
        level.playSound(null, pos, SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.BLOCKS, 1.0f, 1.3f);
        SunBeam.fireNear((ServerLevel) level, pos, player);
        return InteractionResult.CONSUME;
    }
}
