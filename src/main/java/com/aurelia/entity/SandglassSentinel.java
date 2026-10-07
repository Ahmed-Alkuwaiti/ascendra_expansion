package com.aurelia.entity;

import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;

/**
 * Sunscar Citadel heavy guard. Its glass core throws projectiles back at whoever fired them (a warning about Kharzul),
 * and a heavy blow knocks a blinding cloud of sand out of it.
 */
public class SandglassSentinel extends AureliaMinion {
    private int sandCooldown = 0;

    public SandglassSentinel(EntityType<? extends SandglassSentinel> type, Level level) {
        super(type, level);
        this.xpReward = 35;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(130.0, 15.0, 0.23)
                .add(Attributes.ARMOR, 12.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.8);
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.sandCooldown > 0) {
            this.sandCooldown--;
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.getDirectEntity() instanceof Projectile && source.getEntity() instanceof LivingEntity shooter && shooter != this) {
            shooter.hurt(this.damageSources().thorns(this), 4.0f);
            this.playSound(SoundEvents.GLASS_BREAK, 1.0f, 1.6f);
            return false;
        }
        boolean hit = super.hurt(source, amount);
        if (hit && amount >= 8.0f && this.sandCooldown <= 0 && this.level() instanceof ServerLevel level) {
            this.sandCooldown = 80;
            for (Player player : level.getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(4.0))) {
                player.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 50, 0));
            }
            level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, Blocks.RED_SAND.defaultBlockState()),
                    getX(), getY() + 1.5, getZ(), 80, 1.5, 1.0, 1.5, 0.2);
            this.playSound(SoundEvents.SAND_BREAK, 2.0f, 0.6f);
        }
        return hit;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }
}
