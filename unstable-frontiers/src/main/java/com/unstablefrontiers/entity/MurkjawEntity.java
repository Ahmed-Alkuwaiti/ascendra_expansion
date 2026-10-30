package com.unstablefrontiers.entity;

import com.unstablefrontiers.registry.ModSounds;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.RawAnimation;

/**
 * The Murkjaw: a long ambush eel that waits in caves, wrecks and kelp. It hunts swimmers. It holds off at eight or nine
 * blocks, then its jaw unhinges and its lure flares (one second) while a trail of bubbles marks the line it will take:
 * the line is fixed half way through. Then it lunges along it. Off the line and it misses: if it hits a wall it is stunned
 * for three seconds (double damage), otherwise it drifts open for a second and a half (half again as much). Up close it
 * bites. It never chases more than 32 blocks from its lair, and out of water it flounders.
 */
public class MurkjawEntity extends AnimatedMonster {
    public static final int IDLE = 0, TELL = 1, LUNGE = 2, RECOVER = 3, STUNNED = 4;
    private static final int TELL_TICKS = 20, LOCK_AT = 10, LUNGE_TICKS = 16, RECOVER_TICKS = 30, STUN_TICKS = 60;
    private static final RawAnimation A_SWIM = RawAnimation.begin().thenLoop("animation.murkjaw.swim");
    private static final RawAnimation A_TELL = RawAnimation.begin().thenPlayAndHold("animation.murkjaw.tell");
    private static final RawAnimation A_LUNGE = RawAnimation.begin().thenLoop("animation.murkjaw.lunge");
    private static final RawAnimation A_STUNNED = RawAnimation.begin().thenLoop("animation.murkjaw.stunned");
    private static final RawAnimation A_BITE = RawAnimation.begin().thenPlay("animation.murkjaw.bite");
    private static final RawAnimation A_DEATH = RawAnimation.begin().thenPlayAndHold("animation.murkjaw.death");

    @Nullable
    private BlockPos home;
    private Vec3 dir = Vec3.ZERO;
    private Vec3 lungeFrom = Vec3.ZERO;
    private int lungeCooldown = 40;
    private int biteCooldown;
    private boolean hitThisLunge;
    private double orbit = random.nextDouble() * Math.PI * 2;

    public MurkjawEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        xpReward = 10;
        setNoGravity(true);
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 30.0D)
                .add(Attributes.ATTACK_DAMAGE, 9.0D)
                .add(Attributes.ARMOR, 4.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.3D)
                .add(Attributes.FOLLOW_RANGE, 24.0D);
    }

    @Override
    protected void registerGoals() {
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false, p -> p.isInWater()));
    }

    @Override
    public boolean canDrownInFluidType(net.neoforged.neoforge.fluids.FluidType type) {
        return false;   // a sea creature (LivingEntity#canBreatheUnderwater is final in NeoForge)
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (home == null) {
            home = blockPosition();
        }
        lungeCooldown--;
        biteCooldown--;
        setNoGravity(isInWater());
        LivingEntity t = getTarget();
        if (t != null && (!t.isAlive() || t.distanceToSqr(this) > 28 * 28 || home.distSqr(t.blockPosition()) > 32 * 32)) {
            setTarget(null);
            t = null;
        }
        if (!isInWater()) {
            if (state() != IDLE) {
                setState(IDLE);
            }
            return;
        }
        switch (state()) {
            case TELL -> tell(t);
            case LUNGE -> lunge();
            case RECOVER -> {
                setDeltaMovement(getDeltaMovement().scale(0.8D));
                if (stateTicks >= RECOVER_TICKS) {
                    setState(IDLE);
                }
            }
            case STUNNED -> {
                setDeltaMovement(getDeltaMovement().scale(0.6D).add(0, -0.01D, 0));
                if (stateTicks % 8 == 0) {
                    particles(ParticleTypes.BUBBLE, position().add(0, 0.5D, 0), 3, 0.4D);
                }
                if (stateTicks >= STUN_TICKS) {
                    setState(IDLE);
                    lungeCooldown = 40;
                }
            }
            default -> stalk(t);
        }
    }

    private void stalk(@Nullable LivingEntity t) {
        if (t == null) {
            orbit += 0.02D;
            Vec3 c = Vec3.atCenterOf(home);
            swim(new Vec3(c.x + Math.cos(orbit) * 4, c.y + Math.sin(orbit * 2), c.z + Math.sin(orbit) * 4), 0.07D);
            return;
        }
        face(t.position());
        double d = distanceTo(t);
        if (d < 2.4D && biteCooldown <= 0) {
            doHurtTarget(t);
            triggerAnim("main", "bite");
            sound(ModSounds.MURKJAW_BITE.get(), 1.0F, 1.0F);
            biteCooldown = 25;
        }
        // hold off at eight or nine blocks, circling slowly
        orbit += 0.025D;
        Vec3 away = position().subtract(t.position());
        Vec3 flat = new Vec3(away.x, 0, away.z);
        flat = flat.lengthSqr() < 1.0E-4 ? new Vec3(1, 0, 0) : flat.normalize();
        Vec3 side = new Vec3(-flat.z, 0, flat.x);
        Vec3 want = t.position().add(flat.scale(8.5)).add(side.scale(Math.sin(orbit) * 3)).add(0, 0.5D, 0);
        swim(want, 0.16D);
        if (lungeCooldown <= 0 && d > 4 && d < 13 && hasLineOfSight(t)) {
            setState(TELL);
            sound(ModSounds.MURKJAW_TELL.get(), 1.2F, 1.0F);
        }
    }

    private void tell(@Nullable LivingEntity t) {
        setDeltaMovement(getDeltaMovement().scale(0.6D));
        if (t != null && stateTicks <= LOCK_AT) {
            dir = t.getEyePosition().subtract(position().add(0, getBbHeight() / 2, 0)).normalize();
            face(t.position());
        }
        if (stateTicks % 2 == 0) {
            Vec3 from = position().add(0, getBbHeight() / 2, 0);
            line(ParticleTypes.BUBBLE, from, from.add(dir.scale(14)), 0.8D);
            particles(ParticleTypes.GLOW, from.add(dir.scale(0.8D)), 2, 0.15D);
        }
        if (stateTicks >= TELL_TICKS) {
            lungeFrom = position();
            hitThisLunge = false;
            setState(LUNGE);
            sound(ModSounds.MURKJAW_LUNGE.get(), 1.4F, 1.0F);
        }
    }

    private void lunge() {
        setDeltaMovement(dir.scale(1.05D));
        if (!hitThisLunge) {
            for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(0.6D),
                    e -> e != this && e.isAlive() && !(e instanceof MurkjawEntity) && !(e instanceof DeepcallerEntity))) {
                e.hurt(damageSources().mobAttack(this), (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * 1.6F);
                hitThisLunge = true;
            }
        }
        if (horizontalCollision || verticalCollision && stateTicks > 2) {
            setState(STUNNED);
            setDeltaMovement(dir.scale(-0.2D));
            sound(ModSounds.MURKJAW_STUN.get(), 1.2F, 1.0F);
            lungeCooldown = 60;
            return;
        }
        if (stateTicks >= LUNGE_TICKS || position().distanceTo(lungeFrom) > 15) {
            setState(hitThisLunge ? IDLE : RECOVER);
            lungeCooldown = 50 + random.nextInt(30);
        }
    }

    private void face(Vec3 at) {
        Vec3 d = at.subtract(position());
        setYRot((float) Math.toDegrees(Math.atan2(-d.x, d.z)));
        yBodyRot = getYRot();
        yHeadRot = getYRot();
    }

    private void swim(Vec3 at, double speed) {
        if (!level().getFluidState(BlockPos.containing(at)).is(FluidTags.WATER)) {
            at = new Vec3(at.x, getY(), at.z);
        }
        Vec3 d = at.subtract(position());
        Vec3 want = d.lengthSqr() > 1 ? d.normalize().scale(speed) : d.scale(speed);
        setDeltaMovement(getDeltaMovement().scale(0.85D).add(want.scale(0.15D)));
        Vec3 v = getDeltaMovement();
        if (state() == IDLE && getTarget() == null && v.horizontalDistanceSqr() > 1.0E-4) {
            setYRot((float) Math.toDegrees(Math.atan2(-v.x, v.z)));
            yBodyRot = getYRot();
        }
    }

    @Override
    public void travel(Vec3 input) {
        if (isAlive() && isInWater()) {
            move(MoverType.SELF, getDeltaMovement());
            setDeltaMovement(getDeltaMovement().scale(state() == LUNGE ? 1.0D : 0.93D));
        } else {
            super.travel(input);
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (state() == STUNNED) {
            amount *= 2.0F;
        } else if (state() == RECOVER) {
            amount *= 1.5F;
        }
        return super.hurt(source, amount);
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        if (home != null) {
            tag.putLong("Home", home.asLong());
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("Home")) {
            home = BlockPos.of(tag.getLong("Home"));
        }
    }

    @Override
    public String debugInfo() {
        return super.debugInfo() + ", lunge cooldown " + lungeCooldown + ", in water " + isInWater();
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "main", 3, s -> {
            if (isDeadOrDying()) {
                return s.setAndContinue(A_DEATH);
            }
            return s.setAndContinue(switch (state()) {
                case TELL -> A_TELL;
                case LUNGE -> A_LUNGE;
                case STUNNED, RECOVER -> A_STUNNED;
                default -> A_SWIM;
            });
        }).triggerableAnim("bite", A_BITE));
    }

    @Override
    protected int deathTicks() {
        return 24;
    }

    @Nullable
    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.MURKJAW_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.MURKJAW_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.MURKJAW_DEATH.get();
    }
}
