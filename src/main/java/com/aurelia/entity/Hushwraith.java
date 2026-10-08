package com.aurelia.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

/**
 * Rimefast Citadel caster. Blind, and it listens. It cannot notice a crouching player more than four blocks away.
 * Anyone it hears moving upright nearby sets off its shriek: darkness for everyone close, and the garrison is roused
 * (speed and strength for every guard around it).
 */
public class Hushwraith extends AureliaMinion {
    private int shriekCooldown = 40;

    public Hushwraith(EntityType<? extends Hushwraith> type, Level level) {
        super(type, level);
        this.xpReward = 28;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(40.0, 7.0, 0.27);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(1, new FloatGoal(this));
        this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.0, false));
        this.goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.6));
        this.goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 10.0f));
        this.goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, false, false,
                p -> !p.isCrouching() || p.distanceToSqr(this) < 16.0));
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (--this.shriekCooldown > 0) {
            return;
        }
        this.shriekCooldown = 10;
        for (Player player : this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(14.0))) {
            if (player.isCreative() || player.isSpectator() || player.isCrouching()) {
                continue;
            }
            if (player.isSprinting() || player.getDeltaMovement().horizontalDistanceSqr() > 0.004 || this.distanceToSqr(player) < 36.0) {
                shriek(player);
                return;
            }
        }
    }

    private void shriek(LivingEntity heard) {
        this.shriekCooldown = 160;
        this.setTarget(heard);
        this.playSound(SoundEvents.GHAST_HURT, 2.0f, 0.4f);
        for (Player player : this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(16.0))) {
            player.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 100, 0));
        }
        for (Monster ally : this.level().getEntitiesOfClass(Monster.class, this.getBoundingBox().inflate(16.0),
                e -> e.isAlive() && !(e instanceof AureliaBoss))) {
            ally.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 120, 1));
            ally.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 120, 0));
            if (ally != this && ally.getTarget() == null) {
                ally.setTarget(heard);
            }
        }
        if (this.level() instanceof ServerLevel level) {
            com.aurelia.Perf.particles(level, ParticleTypes.SONIC_BOOM, getX(), getY() + 2.0, getZ(), 1, 0, 0, 0, 0);
            com.aurelia.Perf.particles(level, ParticleTypes.SNOWFLAKE, getX(), getY() + 2.0, getZ(), 40, 3.0, 1.0, 3.0, 0.1);
        }
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }
}
