package com.unstablefrontiers.block;

import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.registry.AbyssRegistry;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * The vent's column: up to {@link #HEIGHT} blocks of open air above it. A player's own movement is decided by their client,
 * so the lift is applied there for players (smooth) and on the server for everything else; the server also clears fall
 * distance so nobody takes damage stepping off at the top.
 */
public class UpdraftVentBlockEntity extends BlockEntity {
    public static final int HEIGHT = 24;
    private int height = -1;

    public UpdraftVentBlockEntity(BlockPos pos, BlockState state) {
        super(AbyssRegistry.UPDRAFT_VENT_BE.get(), pos, state);
    }

    public static void tick(Level level, BlockPos pos, BlockState state, UpdraftVentBlockEntity vent) {
        if (vent.height < 0 || level.getGameTime() % 40 == 0) {
            int h = 1;
            while (h < HEIGHT && level.getBlockState(pos.above(h)).getCollisionShape(level, pos.above(h)).isEmpty()) {
                h++;
            }
            vent.height = h - 1;
        }
        if (vent.height <= 0) {
            return;
        }
        AABB column = new AABB(pos.getX() + 0.05D, pos.getY() + 1, pos.getZ() + 0.05D, pos.getX() + 0.95D, pos.getY() + 1 + vent.height,
                pos.getZ() + 0.95D);
        for (Entity e : level.getEntitiesOfClass(Entity.class, column, x -> !x.isSpectator())) {
            boolean player = e instanceof Player;
            if (level.isClientSide != player) {
                if (player && !level.isClientSide) {
                    e.fallDistance = 0;
                }
                continue;
            }
            Vec3 v = e.getDeltaMovement();
            double up = e.isShiftKeyDown() ? Math.max(v.y - 0.04D, -0.18D) : Math.min(v.y + 0.12D, 0.62D);
            e.setDeltaMovement(v.x * 0.9D, up, v.z * 0.9D);
            e.fallDistance = 0;
            if (!player) {
                e.hurtMarked = true;
            }
        }
        if (level.isClientSide && level.random.nextInt(Math.max(1, (int) (3 / Math.max(0.2D, FrontierConfig.particles())))) == 0) {
            double y = pos.getY() + 1 + level.random.nextDouble() * vent.height;
            level.addParticle(ParticleTypes.END_ROD, pos.getX() + 0.2D + level.random.nextDouble() * 0.6D, y,
                    pos.getZ() + 0.2D + level.random.nextDouble() * 0.6D, 0, 0.12D, 0);
        }
    }
}
