package com.aurelia.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

/** Spore Cathedral caster. Drifts overhead and rains stinging spores onto whoever it follows. */
public class SporeDrifter extends FlyingGuard {

    public SporeDrifter(EntityType<? extends SporeDrifter> type, Level level) {
        super(type, level);
        this.xpReward = 25;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 30.0)
                .add(Attributes.ATTACK_DAMAGE, 4.0)
                .add(Attributes.MOVEMENT_SPEED, 0.2)
                .add(Attributes.FLYING_SPEED, 0.3)
                .add(Attributes.FOLLOW_RANGE, 32.0);
    }

    @Override
    protected double hoverHeight() {
        return 5.0;
    }

    @Override
    protected double hoverRadius() {
        return 4.0;
    }

    @Override
    protected int attackInterval() {
        return 90;
    }

    @Override
    protected void attack(LivingEntity target) {
        AreaEffectCloud cloud = new AreaEffectCloud(this.level(), target.getX(), target.getY(), target.getZ());
        cloud.setOwner(this);
        cloud.setRadius(2.5f);
        cloud.setDuration(100);
        cloud.setRadiusPerTick(-0.01f);
        cloud.setParticle(ParticleTypes.SPORE_BLOSSOM_AIR);
        cloud.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 1));
        cloud.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 80, 0));
        this.level().addFreshEntity(cloud);
        this.playSound(SoundEvents.SLIME_SQUISH, 1.0f, 0.5f);
    }
}
