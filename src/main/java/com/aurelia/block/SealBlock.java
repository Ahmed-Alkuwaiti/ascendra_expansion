package com.aurelia.block;

import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.Set;
import java.util.function.Supplier;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;

/**
 * A citadel's inner door. It will not open while any of its guardians (one mob type) is alive within 48 blocks.
 * Touch it once they are all dead and the whole connected seal dissolves.
 */
public class SealBlock extends Block {
    private final Supplier<EntityType<?>> guardian;
    private final String guardianName;

    public SealBlock(Properties properties, Supplier<EntityType<?>> guardian, String guardianName) {
        super(properties);
        this.guardian = guardian;
        this.guardianName = guardianName;
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player,
                                 InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }
        ServerLevel serverLevel = (ServerLevel) level;
        EntityType<?> type = this.guardian.get();
        int alive = serverLevel.getEntitiesOfClass(Mob.class, new AABB(pos).inflate(48.0),
                e -> e.getType() == type && e.isAlive()).size();
        if (alive > 0) {
            player.displayClientMessage(Component.literal("The seal holds. " + alive + " " + this.guardianName
                    + (alive == 1 ? " still stands guard." : "s still stand guard.")), true);
            return InteractionResult.CONSUME;
        }
        dissolve(serverLevel, pos);
        player.displayClientMessage(Component.literal("With its guardians gone, the seal crumbles."), true);
        return InteractionResult.CONSUME;
    }

    private void dissolve(ServerLevel level, BlockPos start) {
        ArrayDeque<BlockPos> queue = new ArrayDeque<>();
        Set<BlockPos> seen = new HashSet<>();
        queue.add(start);
        seen.add(start);
        while (!queue.isEmpty() && seen.size() < 600) {
            BlockPos p = queue.poll();
            level.setBlock(p, Blocks.AIR.defaultBlockState(), 3);
            com.aurelia.Perf.particles(level, ParticleTypes.POOF, p.getX() + 0.5, p.getY() + 0.5, p.getZ() + 0.5, 4, 0.3, 0.3, 0.3, 0.02);
            for (Direction dir : Direction.values()) {
                BlockPos n = p.relative(dir);
                if (!seen.contains(n) && level.getBlockState(n).is(this)) {
                    seen.add(n);
                    queue.add(n);
                }
            }
        }
        level.playSound(null, start, SoundEvents.WITHER_BREAK_BLOCK, SoundSource.BLOCKS, 1.5f, 0.8f);
    }
}
