package com.unstablefrontiers.entity;

import com.unstablefrontiers.ecology.Creatures;
import com.unstablefrontiers.registry.ModEntities;
import com.unstablefrontiers.registry.ModSounds;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.tags.EntityTypeTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.PlayState;
import software.bernie.geckolib.animation.RawAnimation;

/**
 * The Shrikewing: the frontier's sky hunter.
 *
 * <p>It circles high over its home ground and sometimes perches on the highest point near it. It hunts players and, now
 * and then, insects (Gnashbacks and Antarchy's arthropods), which is how the sky and the ground come to fight. Its attack
 * is a dive: it circles its prey, then hangs in the air with its wings flared and screeches while a ring marks the place
 * it has chosen (the tell; the ring stops following you half way through), and dives at that place. Step out of the ring. A missed dive leaves it climbing slowly and
 * open to attack (+50% damage); crashing into the ground grounds it, flapping helplessly, for three seconds (double
 * damage).
 */
public class ShrikewingEntity extends AnimatedMonster {
    public static final int FLY = 0, TELL = 1, DIVE = 2, RECOVER = 3, PERCH = 4, GROUNDED = 5;
    private static final TagKey<EntityType<?>> BOSSES = TagKey.create(Registries.ENTITY_TYPE, ResourceLocation.fromNamespaceAndPath("c", "bosses"));

    private static final RawAnimation A_FLY = RawAnimation.begin().thenLoop("animation.shrikewing.fly");
    private static final RawAnimation A_GLIDE = RawAnimation.begin().thenLoop("animation.shrikewing.glide");
    private static final RawAnimation A_TELL = RawAnimation.begin().thenPlayAndHold("animation.shrikewing.dive_tell");
    private static final RawAnimation A_DIVE = RawAnimation.begin().thenLoop("animation.shrikewing.dive");
    private static final RawAnimation A_RECOVER = RawAnimation.begin().thenLoop("animation.shrikewing.recover");
    private static final RawAnimation A_PERCH = RawAnimation.begin().thenLoop("animation.shrikewing.perch");
    private static final RawAnimation A_DEATH = RawAnimation.begin().thenPlayAndHold("animation.shrikewing.death");
    private static final RawAnimation A_RAKE = RawAnimation.begin().thenPlay("animation.shrikewing.rake");

    @Nullable
    private BlockPos home;
    private double orbit = random.nextDouble() * Math.PI * 2;
    private int circleTicks = 80;
    private int perchCooldown = 600 + random.nextInt(600);
    @Nullable
    private Vec3 perchAt;
    private Vec3 diveAt = Vec3.ZERO;

    public ShrikewingEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        xpReward = 20;
        setNoGravity(true);
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 70.0D)
                .add(Attributes.ATTACK_DAMAGE, 14.0D)
                .add(Attributes.ARMOR, 4.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.3D)
                .add(Attributes.FLYING_SPEED, 0.6D)
                .add(Attributes.FOLLOW_RANGE, 40.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.4D);
    }

    @Override
    protected void registerGoals() {
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false, null));
        // the rivalry: now and then it picks an insect as prey (checked rarely, so it stays a bounded event)
        targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, LivingEntity.class, 400, true, false, ShrikewingEntity::isPrey));
    }

    public static boolean isPrey(LivingEntity e) {
        if (e instanceof ShrikewingEntity || e instanceof ChainedMatriarchEntity || e.getType().is(BOSSES)) {
            return false;
        }
        return (e instanceof GnashbackEntity || e.getType().is(Creatures.INSECTS) || e.getType().is(EntityTypeTags.ARTHROPOD))
                && e.getMaxHealth() <= 400;
    }

    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason, @Nullable SpawnGroupData data) {
        home = blockPosition();
        return super.finalizeSpawn(level, difficulty, reason, data);
    }

    // ---------------------------------------------------------------------------------------------------- flight
    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (home == null) {
            home = blockPosition();
        }
        if (perchCooldown > 0) {
            perchCooldown--;
        }
        LivingEntity target = getTarget();
        if (target != null && (!target.isAlive() || target.distanceToSqr(this) > 48 * 48)) {
            setTarget(null);
            target = null;
        }
        switch (state()) {
            case PERCH -> perch(target);
            case GROUNDED -> {
                setNoGravity(false);
                if (stateTicks > 60) {
                    takeOff();
                }
            }
            case TELL -> tell(target);
            case DIVE -> dive();
            case RECOVER -> {
                flyTowards(position().add(0, 6, 0), 0.22D);
                if (stateTicks > 40) {
                    setState(FLY);
                    circleTicks = 80 + random.nextInt(60);
                }
            }
            default -> fly(target);
        }
        if (state() != PERCH && state() != GROUNDED) {
            Vec3 v = getDeltaMovement();
            if (v.horizontalDistanceSqr() > 1.0E-4) {
                setYRot((float) Math.toDegrees(Math.atan2(-v.x, v.z)));
                yBodyRot = getYRot();
                yHeadRot = getYRot();
            }
        }
    }

    private void fly(@Nullable LivingEntity target) {
        setNoGravity(true);
        if (target != null) {
            // circle the prey, then commit to a dive
            orbit += 0.06D;
            Vec3 c = target.position();
            Vec3 at = new Vec3(c.x + Math.cos(orbit) * 10, c.y + 9, c.z + Math.sin(orbit) * 10);
            flyTowards(at, 0.5D);
            if (--circleTicks <= 0 && hasLineOfSight(target)) {
                setState(TELL);
                sound(ModSounds.SHRIKEWING_SCREECH.get(), 3.0F, 1.0F);
            }
            return;
        }
        // patrol: a slow orbit high over home; now and then, perch on the highest point nearby
        orbit += 0.02D;
        int ground = level().getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, home.getX(), home.getZ());
        Vec3 at = new Vec3(home.getX() + Math.cos(orbit) * 16, Math.max(ground, home.getY()) + 18, home.getZ() + Math.sin(orbit) * 16);
        if (perchCooldown <= 0) {
            perchAt = findPerch();
            perchCooldown = 900 + random.nextInt(900);
            if (perchAt != null) {
                setState(PERCH);
                return;
            }
        }
        flyTowards(at, 0.32D);
        if (horizontalCollision) {
            setDeltaMovement(getDeltaMovement().add(0, 0.3D, 0));
        }
    }

    @Nullable
    private Vec3 findPerch() {
        BlockPos best = null;
        for (int i = 0; i < 10; i++) {
            int x = home.getX() + random.nextInt(25) - 12;
            int z = home.getZ() + random.nextInt(25) - 12;
            int y = level().getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
            if (best == null || y > best.getY()) {
                best = new BlockPos(x, y, z);
            }
        }
        return best == null ? null : Vec3.atBottomCenterOf(best);
    }

    private void perch(@Nullable LivingEntity target) {
        if (target != null || stateTicks > 500 + random.nextInt(200)) {
            takeOff();
            return;
        }
        if (perchAt != null && !onGround()) {
            setNoGravity(true);
            flyTowards(perchAt.add(0, 0.2D, 0), 0.3D);
            if (position().distanceToSqr(perchAt) < 2.5D || stateTicks > 200) {
                setNoGravity(false);
                perchAt = null;
            }
        } else {
            setNoGravity(false);
            setDeltaMovement(getDeltaMovement().multiply(0.5D, 1, 0.5D));
        }
    }

    private void takeOff() {
        setNoGravity(true);
        setDeltaMovement(getDeltaMovement().add(0, 0.6D, 0));
        setState(FLY);
        sound(ModSounds.SHRIKEWING_FLAP.get(), 1.5F, 0.9F);
    }

    private void tell(@Nullable LivingEntity target) {
        setNoGravity(true);
        setDeltaMovement(getDeltaMovement().scale(0.6D));
        if (target != null && stateTicks <= 10) {
            // it picks its spot early in the tell; after that the ring stays put, and stepping out of it is the dodge
            getLookControl().setLookAt(target, 30, 30);
            Vec3 d = target.position().subtract(position());
            setYRot((float) Math.toDegrees(Math.atan2(-d.x, d.z)));
            yBodyRot = getYRot();
            diveAt = target.position();
        }
        if (stateTicks % 2 == 0) {
            ring(ParticleTypes.ANGRY_VILLAGER, diveAt, 1.6D);
        }
        if (stateTicks >= 22) {
            setState(DIVE);
            sound(ModSounds.SHRIKEWING_FLAP.get(), 2.0F, 0.6F);
        }
    }

    private void dive() {
        setNoGravity(true);
        Vec3 d = diveAt.add(0, 0.6D, 0).subtract(position());
        if (d.lengthSqr() > 1.0E-4) {
            setDeltaMovement(d.normalize().scale(1.3D));
        }
        for (LivingEntity hit : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(0.6D),
                e -> e != this && e.isAlive() && !(e instanceof ShrikewingEntity))) {
            hit.hurt(damageSources().mobAttack(this), (float) getAttributeValue(Attributes.ATTACK_DAMAGE));
            hit.knockback(1.0D, -d.x, -d.z);
            hit.hurtMarked = true;
            triggerAnim("attack", "rake");
            setState(RECOVER);
            return;
        }
        if (onGround() || horizontalCollision || verticalCollision) {
            setDeltaMovement(Vec3.ZERO);
            setState(GROUNDED);
            sound(ModSounds.SHRIKEWING_HURT.get(), 1.5F, 0.6F);
            particles(ParticleTypes.CLOUD, position(), 12, 0.8D);
            return;
        }
        if (d.lengthSqr() < 2.0D || stateTicks > 40) {
            setState(RECOVER);
        }
    }

    private void flyTowards(Vec3 at, double speed) {
        Vec3 d = at.subtract(position());
        Vec3 want = d.lengthSqr() > 1 ? d.normalize().scale(speed) : d.scale(speed);
        setDeltaMovement(getDeltaMovement().scale(0.88D).add(want.scale(0.12D)));
    }

    @Override
    public void travel(Vec3 input) {
        if (isNoGravity()) {
            move(net.minecraft.world.entity.MoverType.SELF, getDeltaMovement());
            setDeltaMovement(getDeltaMovement().scale(0.98D));
        } else {
            super.travel(input);
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (state() == GROUNDED) {
            amount *= 2.0F;
        } else if (state() == RECOVER) {
            amount *= 1.5F;
        }
        if (state() == PERCH && !level().isClientSide) {
            takeOff();
        }
        return super.hurt(source, amount);
    }

    /** Knocked out of the sky (the Shrike Impaler does this): it lands hard and is grounded. */
    public void ground() {
        setNoGravity(false);
        setDeltaMovement(new Vec3(0, -1.2D, 0));
        hurtMarked = true;
        setState(GROUNDED);
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
        controllers.add(new AnimationController<>(this, "main", 5, s -> {
            if (isDeadOrDying()) {
                return s.setAndContinue(A_DEATH);
            }
            return s.setAndContinue(switch (state()) {
                case TELL -> A_TELL;
                case DIVE -> A_DIVE;
                case RECOVER, GROUNDED -> A_RECOVER;
                case PERCH -> onGround() ? A_PERCH : A_GLIDE;
                default -> getDeltaMovement().y < -0.05D ? A_GLIDE : A_FLY;
            });
        }));
        controllers.add(new AnimationController<>(this, "attack", 2, s -> PlayState.STOP).triggerableAnim("rake", A_RAKE));
    }

    @Override
    protected int deathTicks() {
        return 26;
    }

    @Nullable
    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.SHRIKEWING_AMBIENT.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 200;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.SHRIKEWING_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.SHRIKEWING_DEATH.get();
    }

    @Override
    protected float getSoundVolume() {
        return 2.0F;
    }

    public static EntityType<ShrikewingEntity> type() {
        return ModEntities.SHRIKEWING.get();
    }
}
