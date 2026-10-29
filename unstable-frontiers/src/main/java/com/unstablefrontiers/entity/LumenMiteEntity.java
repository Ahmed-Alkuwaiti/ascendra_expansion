package com.unstablefrontiers.entity;

import com.unstablefrontiers.registry.ModSounds;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.sounds.SoundEvent;
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
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.PlayState;
import software.bernie.geckolib.animation.RawAnimation;

/**
 * The Lumen Mite. It hangs a few blocks off its prey and circles; every few seconds its lantern swells and brightens
 * (three quarters of a second, with a rising hum) and it spits a slow star bolt at where you are. Side-step the bolt.
 * Fragile: two good hits kill one. Swarms are kept small by the places that hatch them.
 */
public class LumenMiteEntity extends AnimatedMonster {
    public static final int FLY = 0, TELL = 1, SPIT = 2;
    private static final int TELL_TICKS = 15;

    private static final RawAnimation A_FLY = RawAnimation.begin().thenLoop("animation.lumen_mite.fly");
    private static final RawAnimation A_TELL = RawAnimation.begin().thenPlayAndHold("animation.lumen_mite.spit_tell");
    private static final RawAnimation A_SPIT = RawAnimation.begin().thenPlay("animation.lumen_mite.spit").thenLoop("animation.lumen_mite.fly");
    private static final RawAnimation A_DEATH = RawAnimation.begin().thenPlayAndHold("animation.lumen_mite.death");

    @Nullable
    private BlockPos home;
    private int spitCooldown = 40 + random.nextInt(40);
    private int biteCooldown;
    private double orbit = random.nextDouble() * Math.PI * 2;
    private Vec3 aim = Vec3.ZERO;

    public LumenMiteEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        xpReward = 5;
        setNoGravity(true);
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 10.0D)
                .add(Attributes.ATTACK_DAMAGE, 4.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.3D)
                .add(Attributes.FLYING_SPEED, 0.5D)
                .add(Attributes.FOLLOW_RANGE, 24.0D);
    }

    @Override
    protected void registerGoals() {
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false, null));
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (home == null) {
            home = blockPosition();
        }
        spitCooldown--;
        biteCooldown--;
        LivingEntity t = getTarget();
        if (t != null && (!t.isAlive() || t.distanceToSqr(this) > 32 * 32)) {
            setTarget(null);
            t = null;
        }
        switch (state()) {
            case TELL -> {
                setDeltaMovement(getDeltaMovement().scale(0.7D));
                if (t != null) {
                    face(t);
                    aim = t.getEyePosition().add(0, -0.4D, 0);
                }
                if (stateTicks % 3 == 0) {
                    particles(ParticleTypes.GLOW, position().add(0, 0.4D, 0), 3, 0.2D);
                }
                if (stateTicks >= TELL_TICKS) {
                    spit();
                    setState(SPIT);
                }
            }
            case SPIT -> {
                if (stateTicks > 8) {
                    setState(FLY);
                }
            }
            default -> fly(t);
        }
        Vec3 v = getDeltaMovement();
        if (state() == FLY && v.horizontalDistanceSqr() > 1.0E-4) {
            setYRot((float) Math.toDegrees(Math.atan2(-v.x, v.z)));
            yBodyRot = getYRot();
        }
    }

    private void fly(@Nullable LivingEntity t) {
        if (t == null) {
            orbit += 0.03D;
            Vec3 c = Vec3.atCenterOf(home);
            flyTowards(new Vec3(c.x + Math.cos(orbit) * 6, c.y + 2 + Math.sin(orbit * 2), c.z + Math.sin(orbit) * 6), 0.18D);
            return;
        }
        orbit += 0.05D;
        double r = 6.5D;
        Vec3 c = t.position();
        flyTowards(new Vec3(c.x + Math.cos(orbit) * r, c.y + 2.5D + Math.sin(orbit * 3) * 0.8D, c.z + Math.sin(orbit) * r), 0.32D);
        if (distanceToSqr(t) < 2.2D && biteCooldown <= 0) {
            doHurtTarget(t);
            biteCooldown = 20;
        }
        if (spitCooldown <= 0 && hasLineOfSight(t)) {
            setState(TELL);
            sound(ModSounds.MITE_TELL.get(), 0.8F, 1.0F + random.nextFloat() * 0.2F);
            spitCooldown = 60 + random.nextInt(40);
        }
    }

    private void spit() {
        StarBoltEntity bolt = new StarBoltEntity(level(), this, (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * 1.5F);
        Vec3 from = position().add(0, 0.4D, 0).add(getLookAngle().scale(0.6D));
        bolt.setPos(from.x, from.y, from.z);
        Vec3 d = aim.subtract(from);
        bolt.shoot(d.x, d.y, d.z, 0.55F, 0.0F);
        level().addFreshEntity(bolt);
        triggerAnim("main", "spit");
        sound(ModSounds.MITE_SPIT.get(), 0.9F, 1.1F);
    }

    private void face(LivingEntity t) {
        Vec3 d = t.position().subtract(position());
        setYRot((float) Math.toDegrees(Math.atan2(-d.x, d.z)));
        yBodyRot = getYRot();
        yHeadRot = getYRot();
    }

    private void flyTowards(Vec3 at, double speed) {
        Vec3 d = at.subtract(position());
        Vec3 want = d.lengthSqr() > 1 ? d.normalize().scale(speed) : d.scale(speed);
        setDeltaMovement(getDeltaMovement().scale(0.85D).add(want.scale(0.15D)));
    }

    @Override
    public void travel(Vec3 input) {
        if (isAlive()) {
            move(MoverType.SELF, getDeltaMovement());
            setDeltaMovement(getDeltaMovement().scale(0.95D));
        } else {
            super.travel(input);
        }
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        setNoGravity(false);
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
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "main", 3, s -> {
            if (isDeadOrDying()) {
                return s.setAndContinue(A_DEATH);
            }
            if (state() == TELL) {
                return s.setAndContinue(A_TELL);
            }
            if (state() == SPIT) {
                return PlayState.CONTINUE;
            }
            return s.setAndContinue(A_FLY);
        }).triggerableAnim("spit", A_SPIT));
    }

    @Override
    protected int deathTicks() {
        return 16;
    }

    @Nullable
    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.MITE_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.MITE_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.MITE_DEATH.get();
    }
}
