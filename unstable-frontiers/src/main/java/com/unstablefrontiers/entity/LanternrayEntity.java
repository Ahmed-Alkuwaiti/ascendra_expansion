package com.unstablefrontiers.entity;

import com.unstablefrontiers.drowned.DrownedDimension;
import com.unstablefrontiers.drowned.DrownedPlaces;
import com.unstablefrontiers.drowned.DrownedTerrain;
import com.unstablefrontiers.registry.ModSounds;
import java.util.UUID;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * The Lanternray: a broad, gentle ray with lights along its wings, gliding in loose pairs over the reefs and kelp. It never
 * attacks; struck, it flashes and flees. Fed glow berries in the Drowned Expanse it leads the feeder for up to 40 seconds
 * toward the nearest place they have not charted, waiting when they fall behind and leaving a trail of light.
 */
public class LanternrayEntity extends PathfinderMob implements GeoEntity {
    private static final EntityDataAccessor<Boolean> LEADING = SynchedEntityData.defineId(LanternrayEntity.class, EntityDataSerializers.BOOLEAN);
    private static final RawAnimation A_SWIM = RawAnimation.begin().thenLoop("animation.lanternray.swim");
    private static final RawAnimation A_FLASH = RawAnimation.begin().thenPlay("animation.lanternray.flash").thenLoop("animation.lanternray.swim");
    private static final RawAnimation A_DEATH = RawAnimation.begin().thenPlayAndHold("animation.lanternray.death");
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    @Nullable
    private BlockPos home;
    private double orbit = random.nextDouble() * Math.PI * 2;
    private int fleeTicks;
    private int leadTicks;
    @Nullable
    private UUID leader;
    @Nullable
    private Vec3 leadTo;
    /** The feeder as fed (the UUID alone cannot find a player that is not in the level's list, such as a fake player). */
    private java.lang.ref.WeakReference<Player> leaderRef = new java.lang.ref.WeakReference<>(null);

    public LanternrayEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        setNoGravity(true);
        xpReward = 1;
    }

    public static AttributeSupplier.Builder attributes() {
        return PathfinderMob.createMobAttributes().add(Attributes.MAX_HEALTH, 16.0D).add(Attributes.MOVEMENT_SPEED, 0.4D);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(LEADING, false);
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
        setNoGravity(isInWater());
        if (!isInWater()) {
            return;
        }
        Vec3 want;
        double speed;
        if (leadTicks > 0 && leadTo != null && leader != null && leaderOf() instanceof Player p && p.isAlive() && p.level() == level()) {
            leadTicks--;
            double behind = p.distanceTo(this);
            Vec3 toward = leadTo.subtract(position());
            want = behind > 12 ? p.position().add(0, 1, 0) : position().add(toward.normalize().scale(6));
            speed = behind > 12 ? 0.18D : 0.32D;
            if (tickCount % 4 == 0 && level() instanceof ServerLevel sl) {
                sl.sendParticles(ParticleTypes.GLOW, getX(), getY() + 0.3D, getZ(), 2, 0.4, 0.1, 0.4, 0.0);
            }
            if (toward.length() < 20 || leadTicks == 0) {
                stopLeading();
            }
        } else {
            if (leadTicks > 0) {
                stopLeading();
            }
            orbit += fleeTicks > 0 ? 0.0D : 0.012D;
            Vec3 c = Vec3.atCenterOf(home);
            want = fleeTicks > 0 ? position().add(getDeltaMovement().normalize().scale(4)).add(0, 0.5, 0)
                    : new Vec3(c.x + Math.cos(orbit) * 9, c.y + 3 + Math.sin(orbit * 1.7) * 2, c.z + Math.sin(orbit) * 9);
            speed = fleeTicks > 0 ? 0.4D : 0.1D;
            if (fleeTicks > 0) {
                fleeTicks--;
            }
        }
        // keep inside the water
        if (!level().getFluidState(BlockPos.containing(want)).is(FluidTags.WATER)) {
            want = new Vec3(want.x, getY() - 1, want.z);
        }
        Vec3 d = want.subtract(position());
        Vec3 v = d.lengthSqr() > 1 ? d.normalize().scale(speed) : d.scale(speed);
        setDeltaMovement(getDeltaMovement().scale(0.88D).add(v.scale(0.12D)));
        Vec3 m = getDeltaMovement();
        if (m.horizontalDistanceSqr() > 1.0E-4) {
            setYRot((float) Math.toDegrees(Math.atan2(-m.x, m.z)));
            yBodyRot = getYRot();
        }
    }

    @Nullable
    private Player leaderOf() {
        Player p = leaderRef.get();
        return p != null && !p.isRemoved() ? p : level().getPlayerByUUID(leader);
    }

    private void stopLeading() {
        leadTicks = 0;
        leader = null;
        leadTo = null;
        entityData.set(LEADING, false);
    }

    @Override
    public void travel(Vec3 input) {
        if (isAlive() && isInWater()) {
            move(MoverType.SELF, getDeltaMovement());
            setDeltaMovement(getDeltaMovement().scale(0.95D));
        } else {
            super.travel(input);
        }
    }

    @Override
    protected InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!stack.is(Items.GLOW_BERRIES)) {
            return super.mobInteract(player, hand);
        }
        if (level() instanceof ServerLevel sl && player instanceof ServerPlayer sp) {
            if (!player.getAbilities().instabuild) {
                stack.shrink(1);
            }
            DrownedTerrain.Anchor target = null;
            double best = Double.MAX_VALUE;
            if (DrownedDimension.is(sl)) {
                for (DrownedTerrain.Anchor a : DrownedTerrain.ANCHORS) {
                    double dd = Math.hypot(a.x() - getX(), a.z() - getZ());
                    if (!DrownedPlaces.charted(sp, a) && dd < best) {
                        best = dd;
                        target = a;
                    }
                }
            }
            sl.sendParticles(ParticleTypes.HEART, getX(), getY() + 0.6D, getZ(), 3, 0.4, 0.2, 0.4, 0.0);
            if (target == null) {
                player.displayClientMessage(Component.translatable("message.unstable_frontiers.ray_content"), true);
            } else {
                leader = player.getUUID();
                leaderRef = new java.lang.ref.WeakReference<>(player);
                leadTo = new Vec3(target.x() + 0.5D, target.floor() + 6, target.z() + 0.5D);
                leadTicks = 800;
                entityData.set(LEADING, true);
                triggerAnim("main", "flash");
                player.displayClientMessage(Component.translatable("message.unstable_frontiers.ray_leads"), true);
            }
            playSound(ModSounds.RAY_CHIME.get(), 1.0F, 1.2F);
        }
        return InteractionResult.sidedSuccess(level().isClientSide);
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean r = super.hurt(source, amount);
        if (r && !level().isClientSide) {
            fleeTicks = 60;
            stopLeading();
            triggerAnim("main", "flash");
            if (level() instanceof ServerLevel sl) {
                sl.sendParticles(ParticleTypes.GLOW, getX(), getY() + 0.3D, getZ(), 12, 0.8, 0.2, 0.8, 0.05);
            }
        }
        return r;
    }

    public boolean leading() {
        return entityData.get(LEADING);
    }

    @Override
    public boolean removeWhenFarAway(double d) {
        return leadTicks <= 0 && d > 96 * 96;
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
        controllers.add(new AnimationController<>(this, "main", 5, s -> s.setAndContinue(isDeadOrDying() ? A_DEATH : A_SWIM))
                .triggerableAnim("flash", A_FLASH));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }

    @Override
    protected void tickDeath() {
        if (++deathTime >= 20 && !level().isClientSide && !isRemoved()) {
            level().broadcastEntityEvent(this, (byte) 60);
            remove(RemovalReason.KILLED);
        }
    }

    @Nullable
    @Override
    protected SoundEvent getAmbientSound() {
        return isInWater() ? ModSounds.RAY_AMBIENT.get() : null;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.RAY_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.RAY_DEATH.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 240;
    }
}
