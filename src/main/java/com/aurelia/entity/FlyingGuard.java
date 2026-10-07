package com.aurelia.entity;

import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

/** Flying citadel guards: circle their target at a set height and attack on a timer. */
public abstract class FlyingGuard extends Monster {
    protected int cooldown = 60;
    protected double angle;

    protected FlyingGuard(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        this.moveControl = new FlyingMoveControl(this, 20, true);
        this.setNoGravity(true);
        this.angle = this.random.nextDouble() * 6.28;
    }

    protected abstract double hoverHeight();

    protected abstract double hoverRadius();

    protected abstract int attackInterval();

    protected abstract void attack(LivingEntity target);

    protected boolean hovering() {
        return true;
    }

    @Override
    protected void registerGoals() {
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        LivingEntity target = this.getTarget();
        if (target == null || !target.isAlive()) {
            return;
        }
        if (this.hovering()) {
            this.angle += 0.06;
            this.getMoveControl().setWantedPosition(
                    target.getX() + Math.cos(this.angle) * this.hoverRadius(),
                    target.getY() + this.hoverHeight(),
                    target.getZ() + Math.sin(this.angle) * this.hoverRadius(), 1.0);
            this.getLookControl().setLookAt(target, 30.0f, 30.0f);
        }
        if (--this.cooldown <= 0) {
            this.cooldown = this.attackInterval();
            this.attack(target);
        }
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }
}
