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
 *  BRINE (Tidewrack): an undertow grate. Drags at your legs and squeezes the air from your lungs.
 *  FROST (Rimefast): a frost rune. Freezes you where you stand.
 *  SUNFLARE (Sunscar): a mirrored plate. Blinding light and a burn.
 */
public class TrapBlock extends Block {
    public enum Kind { SPORE, GALE, EMBER, BRINE, FROST, SUNFLARE }

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
                case BRINE -> {
                    player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 3));
                    player.addEffect(new MobEffectInstance(MobEffects.DIG_SLOWDOWN, 120, 1));
                    player.setAirSupply(Math.max(-10, player.getAirSupply() - 30));
                    player.setDeltaMovement(player.getDeltaMovement().multiply(0.3, 1.0, 0.3).add(0.0, -0.3, 0.0));
                    player.hurtMarked = true;
                    serverLevel.sendParticles(ParticleTypes.BUBBLE_COLUMN_UP, x, y - 0.6, z, 20, 0.4, 0.3, 0.4, 0.05);
                    if (player.tickCount % 20 == 0) {
                        serverLevel.playSound(null, pos, SoundEvents.BUBBLE_COLUMN_WHIRLPOOL_INSIDE, SoundSource.BLOCKS, 1.0f, 0.8f);
                    }
                }
                case FROST -> {
                    if (player.canFreeze()) {
                        player.setTicksFrozen(Math.min(player.getTicksRequiredToFreeze() + 60, player.getTicksFrozen() + 16));
                    }
                    player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 2));
                    serverLevel.sendParticles(ParticleTypes.SNOWFLAKE, x, y, z, 24, 0.4, 0.5, 0.4, 0.03);
                    if (player.tickCount % 20 == 0) {
                        serverLevel.playSound(null, pos, SoundEvents.POWDER_SNOW_STEP, SoundSource.BLOCKS, 1.0f, 0.6f);
                    }
                }
                case SUNFLARE -> {
                    player.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 50, 0));
                    player.setSecondsOnFire(3);
                    if (player.tickCount % 10 == 0) {
                        player.hurt(player.damageSources().hotFloor(), 2.0f);
                    }
                    serverLevel.sendParticles(ParticleTypes.END_ROD, x, y, z, 16, 0.3, 0.6, 0.3, 0.05);
                    if (player.tickCount % 20 == 0) {
                        serverLevel.playSound(null, pos, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.BLOCKS, 1.5f, 1.8f);
                    }
                }
            }
        }
        super.stepOn(level, pos, state, entity);
    }
}
