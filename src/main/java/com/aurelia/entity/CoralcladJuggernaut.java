package com.aurelia.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** Tidewrack Citadel heavy guard. Hurls its chained anchor at anyone who keeps their distance and hauls them in. */
public class CoralcladJuggernaut extends AureliaMinion {
    private int hookCooldown = 80;

    public CoralcladJuggernaut(EntityType<? extends CoralcladJuggernaut> type, Level level) {
        super(type, level);
        this.xpReward = 35;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(120.0, 14.0, 0.23)
                .add(Attributes.ARMOR, 10.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.7);
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        LivingEntity target = this.getTarget();
        if (target == null || !target.isAlive() || --this.hookCooldown > 0) {
            return;
        }
        double d = this.distanceToSqr(target);
        if (d > 16.0 && d < 196.0 && this.hasLineOfSight(target)) {
            this.hookCooldown = 110;
            Vec3 pull = this.position().subtract(target.position()).normalize().scale(1.3);
            target.push(pull.x, 0.4, pull.z);
            target.hurtMarked = true;
            target.hurt(this.damageSources().mobAttack(this), 4.0f);
            target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 1));
            this.playSound(SoundEvents.CHAIN_BREAK, 2.0f, 0.5f);
            if (this.level() instanceof ServerLevel level) {
                Vec3 step = target.position().subtract(this.position()).scale(1.0 / 12.0);
                for (int i = 0; i < 12; i++) {
                    level.sendParticles(ParticleTypes.CRIT, getX() + step.x * i, getY() + 1.6 + step.y * i, getZ() + step.z * i, 1, 0, 0, 0, 0);
                }
            }
        } else {
            this.hookCooldown = 20;
        }
    }

    @Override
    public boolean canBreatheUnderwater() {
        return true;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }
}
