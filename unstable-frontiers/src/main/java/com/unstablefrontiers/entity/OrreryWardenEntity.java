package com.unstablefrontiers.entity;

import com.unstablefrontiers.abyss.AbyssDimension;
import com.unstablefrontiers.registry.ModSounds;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.RawAnimation;

/**
 * The Orrery Warden keeps its distance and fires its lens. The tell: its rings stop and swing into line and the lens
 * flares for a second while a thin line of light marks its aim (the aim is fixed for the last third). Then the beam
 * burns for a second and a half, turning slowly after you: get behind a wall or keep moving across it. Afterwards its
 * rings stall and it sinks for two and a half seconds, taking double damage. Close in and it pulses its rings outward
 * (a short tell as the rings contract).
 */
public class OrreryWardenEntity extends AnimatedMonster {
    public static final int IDLE = 0, BEAM_TELL = 1, BEAM = 2, STALLED = 3, PULSE_TELL = 4, PULSE = 5;
    private static final int BEAM_TELL_TICKS = 20, BEAM_TICKS = 30, STALL_TICKS = 50, PULSE_TELL_TICKS = 12;
    private static final double BEAM_RANGE = 24.0D;
    private static final DustParticleOptions AIM = new DustParticleOptions(new Vector3f(0.5F, 0.95F, 1.0F), 0.8F);

    private static final RawAnimation A_IDLE = RawAnimation.begin().thenLoop("animation.orrery_warden.idle");
    private static final RawAnimation A_BEAM_TELL = RawAnimation.begin().thenPlayAndHold("animation.orrery_warden.beam_tell");
    private static final RawAnimation A_BEAM = RawAnimation.begin().thenLoop("animation.orrery_warden.beam");
    private static final RawAnimation A_STALLED = RawAnimation.begin().thenLoop("animation.orrery_warden.stalled");
    private static final RawAnimation A_PULSE_TELL = RawAnimation.begin().thenPlayAndHold("animation.orrery_warden.pulse_tell");
    private static final RawAnimation A_PULSE = RawAnimation.begin().thenPlay("animation.orrery_warden.pulse").thenLoop("animation.orrery_warden.idle");
    private static final RawAnimation A_DEATH = RawAnimation.begin().thenPlayAndHold("animation.orrery_warden.death");

    @Nullable
    private BlockPos home;
    private int beamCooldown = 50;
    private int pulseCooldown = 40;
    private Vec3 beamDir = new Vec3(0, 0, 1);

    public OrreryWardenEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        xpReward = 20;
        setNoGravity(true);
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 60.0D)
                .add(Attributes.ATTACK_DAMAGE, 10.0D)
                .add(Attributes.ARMOR, 8.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.2D)
                .add(Attributes.FLYING_SPEED, 0.3D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.8D)
                .add(Attributes.FOLLOW_RANGE, 32.0D);
    }

    @Override
    protected void registerGoals() {
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false, null));
    }

    public Vec3 lens() {
        return position().add(0, 1.25D, 0).add(Vec3.directionFromRotation(0, getYRot()).scale(0.6D));
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (home == null) {
            home = blockPosition();
        }
        beamCooldown--;
        pulseCooldown--;
        LivingEntity t = getTarget();
        if (t != null && (!t.isAlive() || t.distanceToSqr(this) > 40 * 40 || home.distSqr(t.blockPosition()) > 48 * 48)) {
            setTarget(null);   // it does not chase far from what it guards
            t = null;
        }
        switch (state()) {
            case BEAM_TELL -> beamTell(t);
            case BEAM -> beam(t);
            case STALLED -> {
                setDeltaMovement(getDeltaMovement().multiply(0.8D, 0.8D, 0.8D).add(0, -0.01D, 0));
                if (stateTicks >= STALL_TICKS) {
                    setState(IDLE);
                    sound(ModSounds.WARDEN_RECOVER.get(), 1.2F, 1.0F);
                }
            }
            case PULSE_TELL -> {
                setDeltaMovement(getDeltaMovement().scale(0.6D));
                if (stateTicks >= PULSE_TELL_TICKS) {
                    pulse();
                    setState(PULSE);
                }
            }
            case PULSE -> {
                if (stateTicks > 10) {
                    setState(IDLE);
                }
            }
            default -> idle(t);
        }
    }

    private void idle(@Nullable LivingEntity t) {
        if (t == null) {
            Vec3 c = Vec3.atCenterOf(home).add(Math.sin(tickCount / 40.0D) * 3, 1 + Math.sin(tickCount / 25.0D), Math.cos(tickCount / 40.0D) * 3);
            drift(c, 0.06D);
            return;
        }
        face(t);
        double d = distanceTo(t);
        Vec3 away = position().subtract(t.position());
        Vec3 flat = new Vec3(away.x, 0, away.z);
        flat = flat.lengthSqr() < 1.0E-4 ? new Vec3(1, 0, 0) : flat.normalize();
        Vec3 want = t.position().add(flat.scale(11)).add(0, 3.5D, 0);
        drift(want, d < 7 ? 0.14D : 0.09D);
        if (d < 4.5D && pulseCooldown <= 0) {
            setState(PULSE_TELL);
            sound(ModSounds.WARDEN_TELL.get(), 1.0F, 1.6F);
            pulseCooldown = 70;
        } else if (beamCooldown <= 0 && d < BEAM_RANGE && hasLineOfSight(t)) {
            setState(BEAM_TELL);
            sound(ModSounds.WARDEN_TELL.get(), 1.5F, 0.8F);
            beamDir = t.getEyePosition().subtract(lens()).normalize();
        }
    }

    private void beamTell(@Nullable LivingEntity t) {
        setDeltaMovement(getDeltaMovement().scale(0.5D));
        if (t != null && stateTicks < BEAM_TELL_TICKS * 2 / 3) {
            beamDir = t.getEyePosition().add(0, -0.4D, 0).subtract(lens()).normalize();
            face(t);
        }
        if (stateTicks % 2 == 0) {
            line(AIM, lens(), end(), 0.9D);
        }
        if (stateTicks >= BEAM_TELL_TICKS) {
            setState(BEAM);
            sound(ModSounds.WARDEN_BEAM.get(), 2.0F, 1.0F);
        }
    }

    private void beam(@Nullable LivingEntity t) {
        setDeltaMovement(Vec3.ZERO);
        if (t != null) {
            // it turns after you, but slowly: about 2 degrees a tick
            Vec3 want = t.getEyePosition().add(0, -0.4D, 0).subtract(lens()).normalize();
            beamDir = turn(beamDir, want, Math.toRadians(2.0D));
            setYRot((float) Math.toDegrees(Math.atan2(-beamDir.x, beamDir.z)));
            yBodyRot = getYRot();
        }
        Vec3 from = lens(), to = end();
        if (stateTicks % 2 == 0) {
            line(ParticleTypes.END_ROD, from, to, 0.7D);
        }
        if (stateTicks % 5 == 0) {
            AABB box = new AABB(from, to).inflate(0.8D);
            for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, box, e -> e != this && e.isAlive()
                    && !StarBoltEntity.isAbyssCreature(e))) {
                if (distanceToLine(e.position().add(0, e.getBbHeight() / 2, 0), from, to) < 0.9D + e.getBbWidth() / 2) {
                    e.hurt(damageSources().indirectMagic(this, this), (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * 0.6F);
                }
            }
        }
        if (stateTicks >= BEAM_TICKS) {
            setState(STALLED);
            beamCooldown = 70 + random.nextInt(40);
            sound(ModSounds.WARDEN_STALL.get(), 1.4F, 1.0F);
        }
    }

    /** Where the beam stops: the first block it meets, or its full range. Walls and pillars are cover. */
    private Vec3 end() {
        Vec3 from = lens();
        Vec3 to = from.add(beamDir.scale(BEAM_RANGE));
        BlockHitResult hit = level().clip(new ClipContext(from, to, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this));
        return hit.getType() == HitResult.Type.BLOCK ? hit.getLocation() : to;
    }

    private void pulse() {
        sound(ModSounds.WARDEN_PULSE.get(), 1.5F, 1.0F);
        ring(ParticleTypes.END_ROD, position().add(0, 0.5D, 0), 4.0D);
        boolean abyss = AbyssDimension.is(level());
        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(4.5D), e -> e != this && e.isAlive()
                && !StarBoltEntity.isAbyssCreature(e) && e.distanceToSqr(this) < 4.5D * 4.5D)) {
            e.hurt(damageSources().mobAttack(this), (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * 0.7F);
            e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 1));
            // a nudge, not a launch; in the abyss barely that, so nobody is pushed off an island
            e.knockback(abyss ? 0.15D : 0.5D, getX() - e.getX(), getZ() - e.getZ());
            e.hurtMarked = true;
        }
    }

    static double distanceToLine(Vec3 p, Vec3 a, Vec3 b) {
        Vec3 ab = b.subtract(a);
        double t = Math.max(0, Math.min(1, p.subtract(a).dot(ab) / Math.max(1.0E-6, ab.lengthSqr())));
        return p.distanceTo(a.add(ab.scale(t)));
    }

    static Vec3 turn(Vec3 from, Vec3 to, double maxAngle) {
        double dot = Math.max(-1, Math.min(1, from.dot(to)));
        double angle = Math.acos(dot);
        if (angle <= maxAngle) {
            return to;
        }
        return from.lerp(to, maxAngle / angle).normalize();
    }

    private void face(LivingEntity t) {
        Vec3 d = t.position().subtract(position());
        setYRot((float) Math.toDegrees(Math.atan2(-d.x, d.z)));
        yBodyRot = getYRot();
        yHeadRot = getYRot();
    }

    private void drift(Vec3 at, double speed) {
        Vec3 d = at.subtract(position());
        Vec3 want = d.lengthSqr() > 1 ? d.normalize().scale(speed) : d.scale(speed);
        setDeltaMovement(getDeltaMovement().scale(0.9D).add(want.scale(0.1D)));
    }

    @Override
    public void travel(Vec3 input) {
        if (isAlive()) {
            move(MoverType.SELF, getDeltaMovement());
            setDeltaMovement(getDeltaMovement().scale(0.96D));
        } else {
            super.travel(input);
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (state() == STALLED) {
            amount *= 2.0F;
            particles(ParticleTypes.CRIT, position().add(0, 1.2D, 0), 8, 0.6D);
        }
        return super.hurt(source, amount);
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
    public String debugInfo() {
        return super.debugInfo() + ", beam cooldown " + beamCooldown;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "main", 4, s -> {
            if (isDeadOrDying()) {
                return s.setAndContinue(A_DEATH);
            }
            return s.setAndContinue(switch (state()) {
                case BEAM_TELL -> A_BEAM_TELL;
                case BEAM -> A_BEAM;
                case STALLED -> A_STALLED;
                case PULSE_TELL -> A_PULSE_TELL;
                case PULSE -> A_PULSE;
                default -> A_IDLE;
            });
        }));
    }

    @Override
    protected int deathTicks() {
        return 30;
    }

    @Nullable
    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.WARDEN_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.WARDEN_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.WARDEN_DEATH.get();
    }
}
