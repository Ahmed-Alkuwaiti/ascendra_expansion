package com.unstablefrontiers.entity;

import com.unstablefrontiers.config.FrontierConfig;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * Shared base of the frontier's own creatures: a GeckoLib animatable whose animation follows one synced "state" (what the
 * creature is doing: idle, telling an attack, attacking, stunned), so every client shows the same tell at the same time.
 * Death animations get time to play before the body is removed.
 */
public abstract class AnimatedMonster extends Monster implements GeoEntity {
    private static final EntityDataAccessor<Integer> STATE = SynchedEntityData.defineId(AnimatedMonster.class, EntityDataSerializers.INT);
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    /** Ticks the current state has lasted (server side). */
    protected int stateTicks;

    protected AnimatedMonster(EntityType<? extends Monster> type, Level level) {
        super(type, level);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(STATE, 0);
    }

    public int state() {
        return entityData.get(STATE);
    }

    protected void setState(int state) {
        if (state() != state) {
            com.unstablefrontiers.debug.CreatureTrial.log(this, state(), state);
            entityData.set(STATE, state);
            stateTicks = 0;
        }
    }

    /** For screenshots and tests: holds a creature (with its AI off) in one of its states, so its pose can be seen. */
    public void debugPose(int state) {
        setState(state);
    }

    @Override
    public void tick() {
        super.tick();
        if (!level().isClientSide) {
            stateTicks++;
        }
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }

    /** How long the death animation needs, in ticks, before the body disappears. */
    protected int deathTicks() {
        return 30;
    }

    @Override
    protected void tickDeath() {
        deathTime++;
        if (deathTime >= deathTicks() && !level().isClientSide && !isRemoved()) {
            level().broadcastEntityEvent(this, (byte) 60);
            remove(RemovalReason.KILLED);
        }
    }

    protected void sound(SoundEvent sound, float volume, float pitch) {
        level().playSound(null, getX(), getY(), getZ(), sound, getSoundSource(), volume, pitch);
    }

    protected void particles(ParticleOptions p, Vec3 at, int base, double spread) {
        if (level() instanceof ServerLevel sl) {
            int n = FrontierConfig.particleCount(base);
            if (n > 0) {
                sl.sendParticles(p, at.x, at.y, at.z, n, spread, spread * 0.5D, spread, 0.02D);
            }
        }
    }

    /** A ring of particles on the ground: where an attack is about to land. */
    protected void ring(ParticleOptions p, Vec3 centre, double radius) {
        if (level() instanceof ServerLevel sl) {
            int n = FrontierConfig.particleCount(32);
            for (int i = 0; i < n; i++) {
                double a = i * Math.PI * 2 / Math.max(1, n);
                sl.sendParticles(p, centre.x + Math.cos(a) * radius, centre.y + 0.1D, centre.z + Math.sin(a) * radius, 1, 0, 0, 0, 0);
            }
        }
    }
}
