package com.aurelia.entity;

import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;

/** Rootbound Citadel heavy guard. Slow, hard to knock back, and thorny: melee attackers get hurt too. */
public class BrambleSentinel extends AureliaMinion {

    public BrambleSentinel(EntityType<? extends BrambleSentinel> type, Level level) {
        super(type, level);
        this.xpReward = 30;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(90.0, 12.0, 0.24)
                .add(Attributes.ARMOR, 6.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.6);
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hit = super.hurt(source, amount);
        if (hit && !this.level().isClientSide && source.getDirectEntity() instanceof LivingEntity attacker
                && attacker != this) {
            attacker.hurt(this.damageSources().thorns(this), 3.0f);
        }
        return hit;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }
}
