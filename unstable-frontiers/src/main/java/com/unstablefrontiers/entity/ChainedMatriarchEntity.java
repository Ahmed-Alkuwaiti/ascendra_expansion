package com.unstablefrontiers.entity;

import com.unstablefrontiers.encounter.Elites;
import com.unstablefrontiers.registry.ModSounds;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraft.ChatFormatting;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.RawAnimation;

/**
 * The Chained Matriarch: the beast in the Great Cage, a brood queen the Cagewright shackled to the cage floor.
 *
 * <p>Before the fight she hangs in her chains and struggles (she cannot be hurt). The Cagewright's Key at the lock starts
 * it. While any pylon stands she stays chained: tethered close to the middle of the cage and hardened (a third of the
 * damage), but she has to open her brood sac to call her young, and the open sac takes extra damage. Break the pylons and
 * the chains snap: she takes full damage, and she can leap.
 *
 * <p>Every attack has a tell, and every tell has an answer:
 * <ul>
 * <li>Scythe Sweep: she rears with both scythes back and sparks trace the arc in front of her. The arc is locked when the
 * tell ends; get behind her or out of reach.</li>
 * <li>Acid Volley: the sac swells and her head draws back, then three globs fly at where you stand. Keep moving; the
 * puddles they leave linger.</li>
 * <li>Brood Call: the plates on her sac lift and it pulses for three seconds while young climb in. She stands still and
 * the sac takes 150% damage: this is the opening.</li>
 * <li>Leap (unchained only): she crouches and a ring marks where she will land. Leave the ring.</li>
 * </ul>
 * There is no enrage and no hidden phase: the only change in the fight is the one the players cause by breaking the chains.
 */
public class ChainedMatriarchEntity extends AnimatedMonster {
    public static final int IDLE = 0, SWEEP_TELL = 1, SWEEP = 2, SPIT_TELL = 3, SPIT = 4, BROOD = 5, LEAP_TELL = 6, LEAP = 7, ROAR = 8;
    private static final int SWEEP_TELL_TICKS = 22, SPIT_TELL_TICKS = 18, BROOD_TICKS = 60, LEAP_TELL_TICKS = 24, ROAR_TICKS = 40;
    private static final double TETHER = 9.0D;
    private static final double SWEEP_REACH = 7.0D;
    private static final double LEAP_RADIUS = 4.0D;

    private static final RawAnimation A_IDLE = RawAnimation.begin().thenLoop("animation.chained_matriarch.idle");
    private static final RawAnimation A_STRUGGLE = RawAnimation.begin().thenLoop("animation.chained_matriarch.struggle");
    private static final RawAnimation A_WALK = RawAnimation.begin().thenLoop("animation.chained_matriarch.walk");
    private static final RawAnimation A_SWEEP_TELL = RawAnimation.begin().thenPlayAndHold("animation.chained_matriarch.sweep_tell");
    private static final RawAnimation A_SWEEP = RawAnimation.begin().thenPlayAndHold("animation.chained_matriarch.sweep");
    private static final RawAnimation A_SPIT_TELL = RawAnimation.begin().thenPlayAndHold("animation.chained_matriarch.spit_tell");
    private static final RawAnimation A_SPIT = RawAnimation.begin().thenPlayAndHold("animation.chained_matriarch.spit");
    private static final RawAnimation A_BROOD = RawAnimation.begin().thenLoop("animation.chained_matriarch.brood");
    private static final RawAnimation A_LEAP_TELL = RawAnimation.begin().thenPlayAndHold("animation.chained_matriarch.leap_tell");
    private static final RawAnimation A_LEAP = RawAnimation.begin().thenPlayAndHold("animation.chained_matriarch.leap");
    private static final RawAnimation A_DEATH = RawAnimation.begin().thenPlayAndHold("animation.chained_matriarch.death");

    @Nullable
    private Vec3 anchor;
    private boolean chained = true;
    private boolean freed;
    private int attackCooldown = 40;
    private int broodCooldown = 300;
    private int leapCooldown = 200;
    private float lockedYaw;
    private Vec3 leapAt = Vec3.ZERO;

    public ChainedMatriarchEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        xpReward = 400;
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 900.0D)
                .add(Attributes.ATTACK_DAMAGE, 20.0D)
                .add(Attributes.ARMOR, 14.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 6.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.22D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D)
                .add(Attributes.FOLLOW_RANGE, 40.0D)
                .add(Attributes.STEP_HEIGHT, 2.0D);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, false, false, null));
    }

    // -------------------------------------------------------------------------------------------- the encounter
    /** Called by the Great Cage every few ticks: where her chains are fixed, and whether any pylon still holds them. */
    public void setChained(boolean chained, Vec3 anchor) {
        this.anchor = anchor;
        if (this.chained && !chained && !freed) {
            freed = true;
            setState(ROAR);
            sound(ModSounds.MATRIARCH_ROAR.get(), 4.0F, 0.8F);
            sound(ModSounds.SHACKLE.get(), 3.0F, 0.5F);
            particles(ParticleTypes.EXPLOSION, position().add(0, 2, 0), 6, 1.5D);
            tell("message.unstable_frontiers.matriarch_free", ChatFormatting.RED);
            getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(0.28D);
        }
        this.chained = chained && !freed;
    }

    public boolean isChained() {
        return chained;
    }

    private void tell(String key, ChatFormatting colour) {
        if (level() instanceof ServerLevel sl) {
            for (ServerPlayer p : sl.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(28.0D))) {
                p.displayClientMessage(Component.translatable(key).withStyle(colour), true);
            }
        }
    }

    // ------------------------------------------------------------------------------------------------- the AI
    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (attackCooldown > 0) {
            attackCooldown--;
        }
        if (broodCooldown > 0) {
            broodCooldown--;
        }
        if (leapCooldown > 0) {
            leapCooldown--;
        }
        LivingEntity target = getTarget();
        if (target != null && (!target.isAlive() || target instanceof Player p && (p.isCreative() || p.isSpectator()))) {
            setTarget(null);
            target = null;
        }
        switch (state()) {
            case ROAR -> {
                getNavigation().stop();
                if (stateTicks >= ROAR_TICKS) {
                    setState(IDLE);
                    attackCooldown = 20;
                }
            }
            case SWEEP_TELL -> sweepTell(target);
            case SWEEP -> sweep();
            case SPIT_TELL -> spitTell(target);
            case SPIT -> {
                if (stateTicks >= 10) {
                    setState(IDLE);
                }
            }
            case BROOD -> brood();
            case LEAP_TELL -> leapTell(target);
            case LEAP -> leap();
            default -> idle(target);
        }
        tether();
    }

    private void idle(@Nullable LivingEntity target) {
        if (target == null) {
            if (anchor != null && position().distanceToSqr(anchor) > 9) {
                getNavigation().moveTo(anchor.x, anchor.y, anchor.z, 0.8D);
            }
            return;
        }
        getLookControl().setLookAt(target, 20.0F, 20.0F);
        double d = distanceTo(target);
        if (d > 5.0D) {
            getNavigation().moveTo(target, 1.0D);
        } else {
            getNavigation().stop();
            face(target);
        }
        if (attackCooldown > 0) {
            return;
        }
        if (broodCooldown <= 0) {
            getNavigation().stop();
            setState(BROOD);
            sound(ModSounds.MATRIARCH_BROOD.get(), 3.0F, 1.0F);
            tell("message.unstable_frontiers.matriarch_brood", ChatFormatting.GREEN);
            return;
        }
        if (!chained && leapCooldown <= 0 && d > 7.0D && d < 22.0D && onGround()) {
            getNavigation().stop();
            setState(LEAP_TELL);
            sound(ModSounds.MATRIARCH_ROAR.get(), 2.5F, 1.3F);
            return;
        }
        if (d < SWEEP_REACH - 0.5D) {
            getNavigation().stop();
            setState(SWEEP_TELL);
            sound(ModSounds.MATRIARCH_SWEEP_TELL.get(), 2.5F, 1.0F);
        } else if (d < 26.0D && hasLineOfSight(target)) {
            getNavigation().stop();
            setState(SPIT_TELL);
            sound(ModSounds.MATRIARCH_SPIT.get(), 2.0F, 0.7F);
        }
    }

    private void sweepTell(@Nullable LivingEntity target) {
        getNavigation().stop();
        if (target != null) {
            face(target);
        }
        if (stateTicks % 3 == 0 && level() instanceof ServerLevel sl) {
            // sparks trace the arc the scythes will cover
            int n = Math.max(1, com.unstablefrontiers.config.FrontierConfig.particleCount(9));
            for (int i = 0; i < n; i++) {
                double a = Math.toRadians(getYRot() + 90 - 60 + 120.0D * i / Math.max(1, n - 1));
                sl.sendParticles(ParticleTypes.CRIT, getX() + Math.cos(a) * SWEEP_REACH * 0.85D, getY() + 0.3D,
                        getZ() + Math.sin(a) * SWEEP_REACH * 0.85D, 1, 0, 0, 0, 0);
            }
        }
        if (stateTicks >= SWEEP_TELL_TICKS) {
            lockedYaw = getYRot();
            setState(SWEEP);
        }
    }

    private void sweep() {
        getNavigation().stop();
        setYRot(lockedYaw);
        yBodyRot = lockedYaw;
        if (stateTicks == 5) {
            sound(ModSounds.MATRIARCH_SWEEP.get(), 3.0F, 1.0F);
            Vec3 fwd = Vec3.directionFromRotation(0, lockedYaw);
            for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(SWEEP_REACH, 2.0D, SWEEP_REACH),
                    e -> e != this && e.isAlive() && !(e instanceof Monster))) {
                Vec3 to = e.position().subtract(position());
                Vec3 flat = new Vec3(to.x, 0, to.z);
                if (flat.length() > SWEEP_REACH + e.getBbWidth() / 2 || flat.length() < 1.0E-3) {
                    continue;
                }
                if (flat.normalize().dot(fwd) < 0.5D) {   // a 120 degree arc in front
                    continue;
                }
                e.hurt(damageSources().mobAttack(this), (float) getAttributeValue(Attributes.ATTACK_DAMAGE));
                e.knockback(1.6D, -flat.x, -flat.z);
                e.hurtMarked = true;
            }
        }
        if (stateTicks >= 14) {
            setState(IDLE);
            attackCooldown = 30 + random.nextInt(20);
        }
    }

    private void spitTell(@Nullable LivingEntity target) {
        getNavigation().stop();
        if (target != null) {
            face(target);
        }
        if (stateTicks % 4 == 0) {
            particles(ParticleTypes.ITEM_SLIME, mouth(), 4, 0.3D);
        }
        if (stateTicks >= SPIT_TELL_TICKS) {
            if (target != null) {
                volley(target);
            }
            setState(SPIT);
            attackCooldown = 40 + random.nextInt(20);
        }
    }

    private void volley(LivingEntity target) {
        Vec3 from = mouth();
        sound(ModSounds.MATRIARCH_SPIT.get(), 2.5F, 1.2F);
        for (int i = -1; i <= 1; i++) {
            AcidGlobEntity glob = new AcidGlobEntity(level(), this);
            glob.setPos(from.x, from.y, from.z);
            Vec3 aim = target.position().add(0, target.getBbHeight() * 0.3D, 0);
            Vec3 side = new Vec3(-(aim.z - from.z), 0, aim.x - from.x).normalize().scale(i * 2.2D);
            Vec3 d = aim.add(side).subtract(from);
            // a lob that comes down on the spot: flight time from distance, then the rise that gravity (0.03) takes back
            double t = Math.max(6.0D, d.horizontalDistance() / 1.1D);
            glob.setDeltaMovement(d.x / t, d.y / t + 0.015D * t, d.z / t);
            level().addFreshEntity(glob);
        }
    }

    private void brood() {
        getNavigation().stop();
        if (stateTicks % 10 == 0) {
            particles(ParticleTypes.ITEM_SLIME, position().add(Vec3.directionFromRotation(0, getYRot()).scale(-2.5D)).add(0, 2.0D, 0), 6, 0.8D);
        }
        if (stateTicks == 30 && level() instanceof ServerLevel sl) {
            Elites.broodCall(sl, this, 2);
        }
        if (stateTicks >= BROOD_TICKS) {
            setState(IDLE);
            broodCooldown = 500 + random.nextInt(200);
            attackCooldown = 20;
        }
    }

    private void leapTell(@Nullable LivingEntity target) {
        getNavigation().stop();
        if (target != null && stateTicks < LEAP_TELL_TICKS - 10) {   // the spot is fixed well before she jumps
            face(target);
            leapAt = target.position();
        }
        if (stateTicks % 3 == 0) {
            ring(ParticleTypes.FLAME, leapAt, LEAP_RADIUS);
        }
        if (stateTicks >= LEAP_TELL_TICKS) {
            Vec3 d = leapAt.subtract(position());
            double flat = d.horizontalDistance();
            // a ballistic hop that lands near the marked spot: in the air, horizontal speed decays by 0.91 a tick, so the
            // distance covered is about ten times the starting speed
            double vy = 0.9D + Math.min(0.4D, flat * 0.02D);
            Vec3 v = new Vec3(d.x, 0, d.z).scale(1.0D / 9.5D);
            if (v.length() > 2.2D) {
                v = v.normalize().scale(2.2D);
            }
            setDeltaMovement(v.x, vy, v.z);
            hurtMarked = true;
            setState(LEAP);
            sound(ModSounds.MATRIARCH_ROAR.get(), 3.0F, 1.5F);
        }
    }

    private void leap() {
        if (stateTicks > 5 && onGround() || stateTicks > 60) {
            sound(ModSounds.MATRIARCH_SLAM.get(), 4.0F, 0.9F);
            particles(new BlockParticleOption(ParticleTypes.BLOCK, level().getBlockState(blockPosition().below())), position(), 30, 2.5D);
            particles(ParticleTypes.EXPLOSION, position(), 4, 2.0D);
            for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(LEAP_RADIUS, 1.5D, LEAP_RADIUS),
                    e -> e != this && e.isAlive() && !(e instanceof Monster) && e.distanceToSqr(this) < (LEAP_RADIUS + 1.5D) * (LEAP_RADIUS + 1.5D))) {
                e.hurt(damageSources().mobAttack(this), (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * 1.2F);
                e.knockback(2.0D, getX() - e.getX(), getZ() - e.getZ());
                e.setDeltaMovement(e.getDeltaMovement().add(0, 0.5D, 0));
                e.hurtMarked = true;
            }
            setState(IDLE);
            leapCooldown = 220 + random.nextInt(100);
            attackCooldown = 40;   // a breather after landing
        }
    }

    /** While chained she cannot leave the middle of the cage: past the chain's reach she is dragged back. */
    private void tether() {
        if (!chained || anchor == null || state() == ROAR) {
            return;
        }
        Vec3 off = position().subtract(anchor);
        Vec3 flat = new Vec3(off.x, 0, off.z);
        if (flat.length() > TETHER) {
            Vec3 pull = flat.normalize().scale(-0.25D);
            setDeltaMovement(getDeltaMovement().multiply(0.3D, 1, 0.3D).add(pull));
            getNavigation().stop();
            if (tickCount % 10 == 0) {
                sound(ModSounds.SHACKLE.get(), 1.0F, 0.6F);
            }
        }
    }

    private void face(LivingEntity target) {
        Vec3 d = target.position().subtract(position());
        float yaw = (float) Math.toDegrees(Math.atan2(-d.x, d.z));
        setYRot(yaw);
        yBodyRot = yaw;
        yHeadRot = yaw;
    }

    private Vec3 mouth() {
        return position().add(Vec3.directionFromRotation(0, getYRot()).scale(2.6D)).add(0, 3.6D, 0);
    }

    // ---------------------------------------------------------------------------------------------- damage
    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.is(DamageTypes.GENERIC_KILL) || source.is(DamageTypes.FELL_OUT_OF_WORLD)) {
            return super.hurt(source, amount);
        }
        if (isNoAi()) {
            return false;   // hanging in her chains before the fight
        }
        if (source.getEntity() instanceof ChainedMatriarchEntity || source.getDirectEntity() instanceof AcidGlobEntity) {
            return false;
        }
        if (state() == BROOD) {
            amount *= 1.5F;
            particles(ParticleTypes.CRIT, position().add(0, 2.4D, 0), 8, 1.0D);
        } else if (chained) {
            amount *= 0.35F;
            particles(ParticleTypes.ENCHANTED_HIT, position().add(0, 2.4D, 0), 6, 1.0D);
        }
        return super.hurt(source, amount);
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }

    @Override
    public boolean canBeLeashed() {
        return false;
    }

    @Override
    protected boolean canRide(net.minecraft.world.entity.Entity vehicle) {
        return false;
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("Freed", freed);
        if (anchor != null) {
            tag.putDouble("AnchorX", anchor.x);
            tag.putDouble("AnchorY", anchor.y);
            tag.putDouble("AnchorZ", anchor.z);
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        freed = tag.getBoolean("Freed");
        chained = !freed;
        if (tag.contains("AnchorX")) {
            anchor = new Vec3(tag.getDouble("AnchorX"), tag.getDouble("AnchorY"), tag.getDouble("AnchorZ"));
        }
        if (freed) {
            getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(0.28D);
        }
    }

    // ------------------------------------------------------------------------------------------- animation
    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "main", 5, s -> {
            if (isDeadOrDying()) {
                return s.setAndContinue(A_DEATH);
            }
            if (isNoAi()) {
                return s.setAndContinue(A_STRUGGLE);
            }
            return s.setAndContinue(switch (state()) {
                case SWEEP_TELL -> A_SWEEP_TELL;
                case SWEEP -> A_SWEEP;
                case SPIT_TELL -> A_SPIT_TELL;
                case SPIT -> A_SPIT;
                case BROOD -> A_BROOD;
                case LEAP_TELL -> A_LEAP_TELL;
                case LEAP -> A_LEAP;
                case ROAR -> A_STRUGGLE;
                default -> s.isMoving() ? A_WALK : A_IDLE;
            });
        }));
    }

    @Override
    protected int deathTicks() {
        return 50;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.MATRIARCH_AMBIENT.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 160;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.MATRIARCH_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.MATRIARCH_DEATH.get();
    }

    @Override
    protected float getSoundVolume() {
        return 3.0F;
    }

    /** All living Matriarchs near a point (for tests and commands). */
    public static List<ChainedMatriarchEntity> near(Level level, Vec3 at, double r) {
        return level.getEntitiesOfClass(ChainedMatriarchEntity.class, new net.minecraft.world.phys.AABB(at, at).inflate(r));
    }
}
