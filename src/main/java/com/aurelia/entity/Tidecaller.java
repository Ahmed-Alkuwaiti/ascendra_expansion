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

/** Tidewrack Citadel caster. Keeps its distance, opens whirlpools under you, and mends the drowned garrison. */
public class Tidecaller extends AureliaMinion {
    private int vortexCooldown = 60;
    private int healCooldown = 120;

    public Tidecaller(EntityType<? extends Tidecaller> type, Level level) {
        super(type, level);
        this.xpReward = 28;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(50.0, 5.0, 0.26);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(1, new FloatGoal(this));
        this.goalSelector.addGoal(2, new AvoidEntityGoal<>(this, Player.class, 7.0f, 1.0, 1.3));
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
        if (target != null && target.isAlive() && this.distanceToSqr(target) < 256.0 && --this.vortexCooldown <= 0) {
            this.vortexCooldown = 120;
            AreaEffectCloud cloud = new AreaEffectCloud(this.level(), target.getX(), target.getY(), target.getZ());
            cloud.setOwner(this);
            cloud.setRadius(3.0f);
            cloud.setDuration(100);
            cloud.setRadiusPerTick(-0.01f);
            cloud.setParticle(ParticleTypes.BUBBLE_POP);
            cloud.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 2));
            cloud.addEffect(new MobEffectInstance(MobEffects.DIG_SLOWDOWN, 120, 1));
            this.level().addFreshEntity(cloud);
            this.playSound(SoundEvents.BUBBLE_COLUMN_WHIRLPOOL_AMBIENT, 1.5f, 0.8f);
        }
        if (--this.healCooldown <= 0) {
            this.healCooldown = 140;
            for (Monster ally : this.level().getEntitiesOfClass(Monster.class, this.getBoundingBox().inflate(9.0),
                    e -> e != this && e.isAlive() && e.getHealth() < e.getMaxHealth() && !(e instanceof AureliaBoss))) {
                ally.heal(10.0f);
                if (this.level() instanceof ServerLevel level) {
                    com.aurelia.Perf.particles(level, ParticleTypes.DRIPPING_WATER, ally.getX(), ally.getY() + 2.0, ally.getZ(), 10, 0.4, 0.4, 0.4, 0.0);
                }
            }
        }
    }

    @Override
    public boolean canBreatheUnderwater() {
        return true;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }
}
