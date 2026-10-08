package com.aurelia.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** Paradox Keep heavy guard. Its clock-weight flail hurls you back, and the bell on its head tolls, dragging time to a crawl. */
public class HourWarden extends AureliaMinion {
    private int tollCooldown = 100;

    public HourWarden(EntityType<? extends HourWarden> type, Level level) {
        super(type, level);
        this.xpReward = 38;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(140.0, 15.0, 0.23)
                .add(Attributes.ARMOR, 12.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.8)
                .add(Attributes.ATTACK_KNOCKBACK, 2.0);
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        LivingEntity target = this.getTarget();
        if (target != null && this.distanceToSqr(target) < 100.0 && --this.tollCooldown <= 0) {
            this.tollCooldown = 140;
            for (Player player : this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(8.0))) {
                player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 2));
                player.addEffect(new MobEffectInstance(MobEffects.DIG_SLOWDOWN, 80, 1));
            }
            this.playSound(SoundEvents.BELL_BLOCK, 2.0f, 0.4f);
            if (this.level() instanceof ServerLevel level) {
                com.aurelia.Perf.particles(level, ParticleTypes.REVERSE_PORTAL, getX(), getY() + 3.0, getZ(), 50, 3.0, 1.0, 3.0, 0.1);
            }
        }
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && target instanceof LivingEntity victim) {
            Vec3 away = victim.position().subtract(this.position()).multiply(1.0, 0.0, 1.0).normalize();
            victim.push(away.x * 1.2, 0.45, away.z * 1.2);
            victim.hurtMarked = true;
        }
        return hit;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }
}
