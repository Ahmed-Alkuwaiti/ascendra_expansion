package com.aurelia.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** Spore Cathedral heavy guard. Its fungus shield turns frontal blows; when it falls it bursts into a spore cloud. */
public class HuskGuard extends AureliaMinion {

    public HuskGuard(EntityType<? extends HuskGuard> type, Level level) {
        super(type, level);
        this.xpReward = 38;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(140.0, 14.0, 0.24)
                .add(Attributes.ARMOR, 10.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.7);
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.getDirectEntity() != null) {
            Vec3 look = this.getViewVector(1.0f);
            Vec3 toAttacker = source.getDirectEntity().position().subtract(this.position()).normalize();
            if (look.dot(toAttacker) > 0.5) {
                amount *= 0.4f;
            }
        }
        return super.hurt(source, amount);
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        if (!this.level().isClientSide) {
            AreaEffectCloud cloud = new AreaEffectCloud(this.level(), getX(), getY(), getZ());
            cloud.setRadius(3.5f);
            cloud.setDuration(120);
            cloud.setRadiusPerTick(-0.02f);
            cloud.setParticle(ParticleTypes.SPORE_BLOSSOM_AIR);
            cloud.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 1));
            this.level().addFreshEntity(cloud);
        }
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }
}
