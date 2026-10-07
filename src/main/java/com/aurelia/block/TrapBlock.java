package com.aurelia.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Citadel floor mechanisms that trigger when a player steps on them.
 *  SPORE (Rootbound): a puff of poison and slowness.
 *  GALE  (Stormwatch): a launch pad. Throws you about 20 blocks up with slow falling, so you can reach the bridges.
 *  EMBER (Ashen): a burst of flame.
 */
public class TrapBlock extends Block {
    public enum Kind { SPORE, GALE, EMBER }

    private final Kind kind;

    public TrapBlock(Properties properties, Kind kind) {
        super(properties);
        this.kind = kind;
    }

    @Override
    public void stepOn(Level level, BlockPos pos, BlockState state, Entity entity) {
        if (!level.isClientSide && entity instanceof Player player && level instanceof ServerLevel serverLevel) {
            double x = pos.getX() + 0.5, y = pos.getY() + 1.1, z = pos.getZ() + 0.5;
            switch (this.kind) {
                case SPORE -> {
                    player.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 1));
                    player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 1));
                    serverLevel.sendParticles(ParticleTypes.SPORE_BLOSSOM_AIR, x, y, z, 30, 0.6, 0.6, 0.6, 0.02);
                    if (player.tickCount % 20 == 0) {
                        serverLevel.playSound(null, pos, SoundEvents.SLIME_SQUISH, SoundSource.BLOCKS, 1.0f, 0.6f);
                    }
                }
                case GALE -> {
                    player.setDeltaMovement(player.getDeltaMovement().x, 1.9, player.getDeltaMovement().z);
                    player.hurtMarked = true;
                    player.fallDistance = 0;
                    player.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 160, 0));
                    serverLevel.sendParticles(ParticleTypes.CLOUD, x, y, z, 30, 0.4, 0.2, 0.4, 0.15);
                    serverLevel.playSound(null, pos, SoundEvents.ENDER_DRAGON_FLAP, SoundSource.BLOCKS, 1.0f, 1.4f);
                }
                case EMBER -> {
                    player.setSecondsOnFire(5);
                    player.hurt(player.damageSources().hotFloor(), 3.0f);
                    serverLevel.sendParticles(ParticleTypes.FLAME, x, y, z, 30, 0.4, 0.5, 0.4, 0.05);
                    if (player.tickCount % 20 == 0) {
                        serverLevel.playSound(null, pos, SoundEvents.FIRECHARGE_USE, SoundSource.BLOCKS, 1.0f, 0.8f);
                    }
                }
            }
        }
        super.stepOn(level, pos, state, entity);
    }
}
