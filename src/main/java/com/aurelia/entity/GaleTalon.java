package com.aurelia.entity;

import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** Stormwatch Citadel diver. Circles overhead, then folds its wings and strikes with heavy knockback. */
public class GaleTalon extends FlyingGuard {
    private int diveTicks = 0;
    private Vec3 diveTo = Vec3.ZERO;

    public GaleTalon(EntityType<? extends GaleTalon> type, Level level) {
        super(type, level);
        this.xpReward = 20;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 30.0)
                .add(Attributes.ATTACK_DAMAGE, 10.0)
                .add(Attributes.MOVEMENT_SPEED, 0.3)
                .add(Attributes.FLYING_SPEED, 0.6)
                .add(Attributes.FOLLOW_RANGE, 36.0);
    }

    @Override
    protected double hoverHeight() {
        return 7.0;
    }

    @Override
    protected double hoverRadius() {
        return 9.0;
    }

    @Override
    protected int attackInterval() {
        return 70;
    }

    @Override
    protected boolean hovering() {
        return this.diveTicks <= 0;
    }

    @Override
    protected void attack(LivingEntity target) {
        this.diveTicks = 26;
        this.diveTo = target.position().add(0.0, target.getBbHeight() * 0.5, 0.0);
        this.playSound(SoundEvents.PHANTOM_SWOOP, 1.5f, 1.3f);
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.diveTicks > 0) {
            this.diveTicks--;
            this.getMoveControl().setWantedPosition(this.diveTo.x, this.diveTo.y, this.diveTo.z, 2.4);
            LivingEntity target = this.getTarget();
            if (target != null && this.getBoundingBox().inflate(0.5).intersects(target.getBoundingBox())) {
                target.hurt(this.damageSources().mobAttack(this), 10.0f);
                Vec3 dir = target.position().subtract(this.position()).multiply(1.0, 0.0, 1.0).normalize();
                target.push(dir.x * 1.4, 0.5, dir.z * 1.4);
                target.hurtMarked = true;
                this.diveTicks = 0;
            }
        }
    }
}
