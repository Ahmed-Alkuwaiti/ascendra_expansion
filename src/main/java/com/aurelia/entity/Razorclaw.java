package com.aurelia.entity;

import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

/** Tidewrack Citadel beast. A reef crab that scuttles in fast and pins you with its claw. */
public class Razorclaw extends BeastGuard {

    public Razorclaw(EntityType<? extends Razorclaw> type, Level level) {
        super(type, level);
        this.xpReward = 22;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 44.0)
                .add(Attributes.ATTACK_DAMAGE, 9.0)
                .add(Attributes.ARMOR, 6.0)
                .add(Attributes.MOVEMENT_SPEED, 0.34)
                .add(Attributes.FOLLOW_RANGE, 32.0);
    }

    @Override
    protected void onBite(LivingEntity victim) {
        victim.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 3));
    }

    @Override
    public boolean canBreatheUnderwater() {
        return true;
    }
}
