package com.aurelia.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

/**
 * Rootbound Citadel support caster. Keeps its distance, lobs poison spore clouds, and heals nearby guards.
 * Always drops a Spore Heart, which is what the Rootbound portal puzzle needs.
 */
public class Sporecap extends AureliaMinion {
    private int sporeCooldown = 60;
    private int healCooldown = 100;

    public Sporecap(EntityType<? extends Sporecap> type, Level level) {
        super(type, level);
        this.xpReward = 25;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(34.0, 4.0, 0.27);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(1, new FloatGoal(this));
        this.goalSelector.addGoal(2, new AvoidEntityGoal<>(this, Player.class, 7.0f, 1.0, 1.35));
        this.goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.8));
        this.goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 14.0f));
        this.goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        LivingEntity target = this.getTarget();
        if (target != null && target.isAlive() && this.distanceToSqr(target) < 256.0 && --this.sporeCooldown <= 0) {
            this.sporeCooldown = 90;
            this.throwSpores(target);
        }
        if (--this.healCooldown <= 0) {
            this.healCooldown = 120;
            this.healAllies();
        }
    }

    private void throwSpores(LivingEntity target) {
        AreaEffectCloud cloud = new AreaEffectCloud(this.level(), target.getX(), target.getY(), target.getZ());
        cloud.setOwner(this);
        cloud.setRadius(2.5f);
        cloud.setDuration(100);
        cloud.setRadiusPerTick(-0.01f);
        cloud.setParticle(ParticleTypes.SPORE_BLOSSOM_AIR);
        cloud.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 1));
        cloud.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 1));
        this.level().addFreshEntity(cloud);
        this.playSound(SoundEvents.SLIME_SQUISH, 1.0f, 0.7f);
    }

    private void healAllies() {
        for (Monster ally : this.level().getEntitiesOfClass(Monster.class, this.getBoundingBox().inflate(8.0),
                e -> e != this && e.isAlive() && e.getHealth() < e.getMaxHealth() && !(e instanceof AureliaBoss))) {
            ally.heal(8.0f);
            if (this.level() instanceof ServerLevel serverLevel) {
                serverLevel.sendParticles(ParticleTypes.HAPPY_VILLAGER, ally.getX(), ally.getY() + 1.0, ally.getZ(),
                        8, 0.4, 0.6, 0.4, 0.0);
            }
        }
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }
}
