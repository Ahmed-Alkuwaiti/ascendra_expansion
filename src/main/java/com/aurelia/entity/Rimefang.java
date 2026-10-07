package com.aurelia.entity;

import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

/** Rimefast Citadel beast. A gaunt white wolf; its bite fills you with frost. */
public class Rimefang extends BeastGuard {

    public Rimefang(EntityType<? extends Rimefang> type, Level level) {
        super(type, level);
        this.xpReward = 22;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 46.0)
                .add(Attributes.ATTACK_DAMAGE, 9.0)
                .add(Attributes.MOVEMENT_SPEED, 0.37)
                .add(Attributes.FOLLOW_RANGE, 32.0);
    }

    @Override
    protected void onBite(LivingEntity victim) {
        if (victim.canFreeze()) {
            victim.setTicksFrozen(Math.min(victim.getTicksRequiredToFreeze() + 40, victim.getTicksFrozen() + 80));
        }
        victim.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 1));
    }
}
