package com.aurelia.block;

import com.aurelia.world.Realm;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.BlockHitResult;

/**
 * A spore valve. Right-click to wrench it open.
 *  In the Spore Cathedral: an open valve is forced shut again by the roots after twelve seconds. Have all three open at
 *  once and they lock open for good (LOCKED) and the portal wakes. They are far apart: you have to run.
 *  In the Mycelial Deep: valves stay open until the Bloom Mother's roots seal them. During her INHALE, two or more open
 *  valves choke her.
 */
public class SporeValveBlock extends Block {
    public static final BooleanProperty OPEN = BooleanProperty.create("open");
    public static final BooleanProperty LOCKED = BooleanProperty.create("locked");
    public static final int OPEN_TICKS = 240;
    private static final int RANGE = 40;

    public SporeValveBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(OPEN, false).setValue(LOCKED, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(OPEN, LOCKED);
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }
        ServerLevel serverLevel = (ServerLevel) level;
        if (state.getValue(LOCKED)) {
            player.displayClientMessage(Component.literal("The valve is rusted open. Spores pour out of it."), true);
            return InteractionResult.CONSUME;
        }
        if (state.getValue(OPEN)) {
            player.displayClientMessage(Component.literal("The valve is already open, hissing."), true);
            return InteractionResult.CONSUME;
        }
        setOpen(serverLevel, pos, state, true);
        if (Realm.of(level) == Realm.MYCELIAL) {
            player.displayClientMessage(Component.literal("You wrench the valve open. Spores roar out of it.").withStyle(ChatFormatting.LIGHT_PURPLE), true);
            return InteractionResult.CONSUME;
        }
        serverLevel.scheduleTick(pos, this, OPEN_TICKS);
        List<BlockPos> valves = group(serverLevel, pos);
        long open = valves.stream().filter(v -> serverLevel.getBlockState(v).getValue(OPEN)).count();
        if (open >= valves.size() && !valves.isEmpty()) {
            for (BlockPos v : valves) {
                serverLevel.setBlock(v, serverLevel.getBlockState(v).setValue(OPEN, true).setValue(LOCKED, true), 3);
            }
            serverLevel.playSound(null, pos, SoundEvents.BEACON_ACTIVATE, SoundSource.BLOCKS, 2.0f, 0.6f);
            PuzzleLogic.check(serverLevel, pos, this, LOCKED);
        } else {
            player.displayClientMessage(Component.literal("The valve shrieks open. " + open + " of " + valves.size()
                    + " open. The roots are already closing it: run.").withStyle(ChatFormatting.LIGHT_PURPLE), true);
        }
        return InteractionResult.CONSUME;
    }

    @Override
    public void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (state.getValue(OPEN) && !state.getValue(LOCKED) && Realm.of(level) != Realm.MYCELIAL) {
            setOpen(level, pos, state, false);
        }
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (state.getValue(OPEN)) {
            for (int i = 0; i < 3; i++) {
                level.addParticle(ParticleTypes.SPORE_BLOSSOM_AIR, pos.getX() + 0.5, pos.getY() + 1.1, pos.getZ() + 0.5,
                        (random.nextDouble() - 0.5) * 0.1, 0.25, (random.nextDouble() - 0.5) * 0.1);
            }
        }
    }

    public static void setOpen(ServerLevel level, BlockPos pos, BlockState state, boolean open) {
        level.setBlock(pos, state.setValue(OPEN, open), 3);
        level.playSound(null, pos, open ? SoundEvents.PISTON_EXTEND : SoundEvents.PISTON_CONTRACT, SoundSource.BLOCKS, 1.5f, open ? 0.6f : 0.8f);
        level.sendParticles(open ? ParticleTypes.SPORE_BLOSSOM_AIR : ParticleTypes.SMOKE, pos.getX() + 0.5, pos.getY() + 1.2, pos.getZ() + 0.5,
                open ? 60 : 10, 0.3, 1.5, 0.3, 0.05);
    }

    public static List<BlockPos> group(ServerLevel level, BlockPos near) {
        List<BlockPos> found = new ArrayList<>();
        for (BlockPos p : BlockPos.betweenClosed(near.offset(-RANGE, -16, -RANGE), near.offset(RANGE, 16, RANGE))) {
            if (level.getBlockState(p).getBlock() instanceof SporeValveBlock) {
                found.add(p.immutable());
            }
        }
        return found;
    }
}
