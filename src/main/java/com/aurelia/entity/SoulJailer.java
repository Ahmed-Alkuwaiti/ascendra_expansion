package com.aurelia.entity;

import com.aurelia.registry.ModEntities;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
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
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

/**
 * Ashen Citadel support caster. Chains nearby players (heavy slowness and weakness) and calls a Shade.
 * Drops Soul Sigils for the Ashen portal puzzle.
 */
public class SoulJailer extends AureliaMinion {
    private int jailCooldown = 80;

    public SoulJailer(EntityType<? extends SoulJailer> type, Level level) {
        super(type, level);
        this.xpReward = 30;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(60.0, 6.0, 0.26);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(1, new FloatGoal(this));
        this.goalSelector.addGoal(2, new AvoidEntityGoal<>(this, Player.class, 6.0f, 1.0, 1.3));
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
        if (target != null && target.isAlive() && this.distanceToSqr(target) < 196.0 && --this.jailCooldown <= 0) {
            this.jailCooldown = 140;
            this.castJail(target);
        }
    }

    private void castJail(LivingEntity target) {
        for (Player player : this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(12.0))) {
            player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 2));
            player.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 100, 0));
            if (this.level() instanceof ServerLevel serverLevel) {
                serverLevel.sendParticles(ParticleTypes.SOUL, player.getX(), player.getY() + 1.0, player.getZ(),
                        24, 0.5, 0.9, 0.5, 0.04);
            }
        }
        int shades = this.level().getEntitiesOfClass(HollowShade.class, this.getBoundingBox().inflate(20.0)).size();
        if (shades < 4) {
            HollowShade shade = ModEntities.HOLLOW_SHADE.get().create(this.level());
            if (shade != null) {
                shade.moveTo(this.getX() + (this.random.nextDouble() - 0.5) * 3.0, this.getY(),
                        this.getZ() + (this.random.nextDouble() - 0.5) * 3.0, this.random.nextFloat() * 360.0f, 0.0f);
                shade.setTarget(target);
                this.level().addFreshEntity(shade);
            }
        }
        this.playSound(SoundEvents.SOUL_ESCAPE, 1.5f, 0.7f);
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }
}
