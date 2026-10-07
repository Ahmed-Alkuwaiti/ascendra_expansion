package com.aurelia.entity;

import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

/** Paradox Keep beast. A clockwork spider; its gears catch in your clothes and steal your speed. */
public class Gearskitter extends BeastGuard {

    public Gearskitter(EntityType<? extends Gearskitter> type, Level level) {
        super(type, level);
        this.xpReward = 22;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 38.0)
                .add(Attributes.ATTACK_DAMAGE, 9.0)
                .add(Attributes.ARMOR, 8.0)
                .add(Attributes.MOVEMENT_SPEED, 0.38)
                .add(Attributes.FOLLOW_RANGE, 32.0);
    }

    @Override
    protected void onBite(LivingEntity victim) {
        victim.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 2));
        victim.addEffect(new MobEffectInstance(MobEffects.DIG_SLOWDOWN, 60, 1));
    }
}
