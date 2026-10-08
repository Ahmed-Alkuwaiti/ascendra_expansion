package com.aurelia.block;

import com.aurelia.entity.Vexor;
import com.aurelia.registry.ModBlocks;
import com.aurelia.world.Realm;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;

/**
 * A clock dial. Right-click to wind it forward one hour.
 *  In the Paradox Keep: the three dials are geared together. Winding one also winds the next one along the row
 *  (the last winds the first). Set all three to the hour on the Master Clock and the portal wakes.
 *  In the Clockwork Rift: the arena's dials turn freely; during THE HOUR STRIKES, Vexor needs all three on his hour.
 */
public class ClockDialBlock extends Block {
    public static final IntegerProperty HOUR = IntegerProperty.create("hour", 0, 11);
    public static final BooleanProperty FILLED = PuzzleNodeBlock.FILLED;
    private static final int RANGE = 16;

    public ClockDialBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(HOUR, 0).setValue(FILLED, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(HOUR, FILLED);
    }

    public static String hourName(int hour) {
        return (hour == 0 ? 12 : hour) + " o'clock";
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }
        ServerLevel serverLevel = (ServerLevel) level;
        if (state.getValue(FILLED)) {
            player.displayClientMessage(Component.literal("The dial is locked at " + hourName(state.getValue(HOUR)) + ". Time agrees with itself here."), true);
            return InteractionResult.CONSUME;
        }
        if (Realm.of(level) == Realm.CLOCKWORK) {
            BlockState next = wind(serverLevel, pos, state);
            player.displayClientMessage(Component.literal("The dial reads " + hourName(next.getValue(HOUR)) + ".").withStyle(ChatFormatting.GOLD), true);
            for (Vexor vexor : serverLevel.getEntitiesOfClass(Vexor.class, new AABB(pos).inflate(64.0))) {
                vexor.onDialSet();
            }
            return InteractionResult.CONSUME;
        }
        List<BlockPos> dials = group(serverLevel, pos);
        int i = dials.indexOf(pos);
        wind(serverLevel, pos, state);
        if (dials.size() > 1) {
            BlockPos linked = dials.get((i + 1) % dials.size());
            wind(serverLevel, linked, serverLevel.getBlockState(linked));
        }
        Integer target = masterHour(serverLevel, pos);
        StringBuilder read = new StringBuilder("The dials read");
        boolean all = target != null;
        for (BlockPos d : dials) {
            int h = serverLevel.getBlockState(d).getValue(HOUR);
            read.append(' ').append(h == 0 ? 12 : h);
            all &= target != null && h == target;
        }
        player.displayClientMessage(Component.literal(read + (target != null ? ". The Master Clock reads " + (target == 0 ? 12 : target) + "." : "."))
                .withStyle(ChatFormatting.GOLD), true);
        if (all) {
            for (BlockPos d : dials) {
                serverLevel.setBlock(d, serverLevel.getBlockState(d).setValue(FILLED, true), 3);
                com.aurelia.Perf.particles(serverLevel, ParticleTypes.END_ROD, d.getX() + 0.5, d.getY() + 1.2, d.getZ() + 0.5, 20, 0.3, 0.4, 0.3, 0.05);
            }
            serverLevel.playSound(null, pos, SoundEvents.BELL_BLOCK, SoundSource.BLOCKS, 2.0f, 0.5f);
            PuzzleLogic.check(serverLevel, pos, this, FILLED);
        }
        return InteractionResult.CONSUME;
    }

    /** Winds a dial forward one hour, with a tick. */
    public static BlockState wind(ServerLevel level, BlockPos pos, BlockState state) {
        BlockState next = state.setValue(HOUR, (state.getValue(HOUR) + 1) % 12);
        level.setBlock(pos, next, 3);
        level.playSound(null, pos, SoundEvents.UI_BUTTON_CLICK.value(), SoundSource.BLOCKS, 0.8f, 1.6f);
        com.aurelia.Perf.particles(level, ParticleTypes.ELECTRIC_SPARK, pos.getX() + 0.5, pos.getY() + 1.1, pos.getZ() + 0.5, 4, 0.2, 0.1, 0.2, 0.02);
        return next;
    }

    /** The dials near a position, in a stable order: along whichever horizontal axis they spread out on. */
    public static List<BlockPos> group(ServerLevel level, BlockPos near) {
        List<BlockPos> found = new ArrayList<>();
        for (BlockPos p : BlockPos.betweenClosed(near.offset(-RANGE, -6, -RANGE), near.offset(RANGE, 6, RANGE))) {
            if (level.getBlockState(p).getBlock() instanceof ClockDialBlock) {
                found.add(p.immutable());
            }
        }
        int minX = found.stream().mapToInt(BlockPos::getX).min().orElse(0), maxX = found.stream().mapToInt(BlockPos::getX).max().orElse(0);
        int minZ = found.stream().mapToInt(BlockPos::getZ).min().orElse(0), maxZ = found.stream().mapToInt(BlockPos::getZ).max().orElse(0);
        boolean alongX = maxX - minX >= maxZ - minZ;
        found.sort(alongX ? Comparator.comparingInt(BlockPos::getX).thenComparingInt(BlockPos::getZ)
                : Comparator.comparingInt(BlockPos::getZ).thenComparingInt(BlockPos::getX));
        return found;
    }

    /** The hour on the nearest Master Clock, or null if there is none. */
    public static Integer masterHour(ServerLevel level, BlockPos near) {
        for (BlockPos p : BlockPos.betweenClosed(near.offset(-RANGE, -6, -RANGE), near.offset(RANGE, 6, RANGE))) {
            BlockState s = level.getBlockState(p);
            if (s.is(ModBlocks.MASTER_CLOCK.get())) {
                return s.getValue(HOUR);
            }
        }
        return null;
    }
}
