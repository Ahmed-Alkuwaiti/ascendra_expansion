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
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** Paradox Keep caster. Circles overhead and flings clock-hand blades; each hit steals a second (slowness). */
public class Secondhand extends FlyingGuard {

    public Secondhand(EntityType<? extends Secondhand> type, Level level) {
        super(type, level);
        this.xpReward = 25;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 32.0)
                .add(Attributes.ATTACK_DAMAGE, 6.0)
                .add(Attributes.MOVEMENT_SPEED, 0.25)
                .add(Attributes.FLYING_SPEED, 0.45)
                .add(Attributes.FOLLOW_RANGE, 32.0);
    }

    @Override
    protected double hoverHeight() {
        return 4.0;
    }

    @Override
    protected double hoverRadius() {
        return 7.0;
    }

    @Override
    protected int attackInterval() {
        return 60;
    }

    @Override
    protected void attack(LivingEntity target) {
        if (!this.hasLineOfSight(target) || !(this.level() instanceof ServerLevel level)) {
            return;
        }
        Vec3 from = this.position().add(0.0, 1.2, 0.0);
        Vec3 d = target.getEyePosition().subtract(from);
        for (double t = 0.0; t < 1.0; t += 0.05) {
            Vec3 p = from.add(d.scale(t));
            com.aurelia.Perf.particles(level, ParticleTypes.ELECTRIC_SPARK, p.x, p.y, p.z, 1, 0, 0, 0, 0);
        }
        target.hurt(this.damageSources().indirectMagic(this, this), 8.0f);
        target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 2));
        this.playSound(SoundEvents.TRIDENT_THROW, 1.5f, 1.6f);
    }
}
