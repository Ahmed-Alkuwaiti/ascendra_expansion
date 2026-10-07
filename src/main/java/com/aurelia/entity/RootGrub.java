package com.aurelia.entity;

import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

/** Spore Cathedral beast. A bloated grub; its split-root mouth poisons. */
public class RootGrub extends BeastGuard {

    public RootGrub(EntityType<? extends RootGrub> type, Level level) {
        super(type, level);
        this.xpReward = 20;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 42.0)
                .add(Attributes.ATTACK_DAMAGE, 8.0)
                .add(Attributes.ARMOR, 4.0)
                .add(Attributes.MOVEMENT_SPEED, 0.33)
                .add(Attributes.FOLLOW_RANGE, 32.0);
    }

    @Override
    protected void onBite(LivingEntity victim) {
        victim.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 1));
    }
}
