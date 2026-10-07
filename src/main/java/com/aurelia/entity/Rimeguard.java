package com.aurelia.entity;

import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;

/** Rimefast Citadel heavy guard. Its glaive freezes what it cuts, and striking its frozen armour chills you too. */
public class Rimeguard extends AureliaMinion {

    public Rimeguard(EntityType<? extends Rimeguard> type, Level level) {
        super(type, level);
        this.xpReward = 35;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(120.0, 13.0, 0.25)
                .add(Attributes.ARMOR, 10.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.6);
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && target instanceof LivingEntity victim) {
            if (victim.canFreeze()) {
                victim.setTicksFrozen(Math.min(victim.getTicksRequiredToFreeze() + 40, victim.getTicksFrozen() + 90));
            }
            victim.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 1));
        }
        return hit;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hit = super.hurt(source, amount);
        if (hit && !this.level().isClientSide && source.getDirectEntity() instanceof LivingEntity attacker && attacker != this
                && attacker.canFreeze()) {
            attacker.setTicksFrozen(Math.min(attacker.getTicksRequiredToFreeze() + 20, attacker.getTicksFrozen() + 30));
        }
        return hit;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }
}
