package com.aurelia.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
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
import net.minecraft.world.phys.Vec3;

/** Sunscar Citadel caster. Focuses sunlight through its mirror: a line of light, a second to step aside, then fire. */
public class Sunseer extends AureliaMinion {
    private int beamCooldown = 60;
    private int focusTicks = 0;
    private Vec3 focusAt = Vec3.ZERO;

    public Sunseer(EntityType<? extends Sunseer> type, Level level) {
        super(type, level);
        this.xpReward = 28;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(45.0, 5.0, 0.26);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(1, new FloatGoal(this));
        this.goalSelector.addGoal(2, new AvoidEntityGoal<>(this, Player.class, 7.0f, 1.0, 1.3));
        this.goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.8));
        this.goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 16.0f));
        this.goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        LivingEntity target = this.getTarget();
        if (this.focusTicks > 0) {
            this.focusTicks--;
            Vec3 from = this.position().add(0.0, 2.2, 0.0);
            if (this.level() instanceof ServerLevel level && this.focusTicks % 3 == 0) {
                Vec3 d = this.focusAt.subtract(from);
                double len = d.length();
                for (double t = 0.0; t < len; t += 1.0) {
                    Vec3 p = from.add(d.scale(t / len));
                    level.sendParticles(ParticleTypes.WAX_ON, p.x, p.y, p.z, 1, 0.0, 0.0, 0.0, 0.0);
                }
            }
            if (this.focusTicks == 0 && target != null && target.isAlive()
                    && target.position().distanceToSqr(this.focusAt.subtract(0.0, 1.0, 0.0)) < 4.0 && this.hasLineOfSight(target)) {
                target.hurt(this.damageSources().indirectMagic(this, this), 10.0f);
                target.setSecondsOnFire(4);
                this.playSound(SoundEvents.FIRECHARGE_USE, 1.5f, 1.4f);
            }
            return;
        }
        if (target != null && target.isAlive() && this.distanceToSqr(target) < 400.0 && this.hasLineOfSight(target) && --this.beamCooldown <= 0) {
            this.beamCooldown = 90;
            this.focusTicks = 22;
            this.focusAt = target.position().add(0.0, 1.0, 0.0);
            this.playSound(SoundEvents.BEACON_POWER_SELECT, 1.5f, 1.8f);
        }
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }
}
