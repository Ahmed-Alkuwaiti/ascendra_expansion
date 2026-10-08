package com.aurelia.entity;

import com.aurelia.registry.ModItems;
import com.aurelia.world.Story;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * Tempest Roc, Warden of Skyreach (3000 HP). A flying boss driven by a small state machine:
 * HOVER (circle the target, 8 blocks up) -> TELEGRAPH (hang still, glow) -> DIVE (fast charge, knocks you back).
 * Phase 2 (66%): lightning strikes around the target, faster and harder dives.
 * Phase 3 (33%): dives come in pairs, two lightning bolts at a time, shorter pauses.
 */
public class TempestRoc extends AureliaBoss {
    private enum Mode { HOVER, TELEGRAPH, DIVE, STUNNED }

    private Mode mode = Mode.HOVER;
    private int modeTicks = 60;
    private int chainDives = 0;
    private double angle = 0.0;
    private Vec3 diveTo = Vec3.ZERO;
    private int gustTimer = 260;
    private boolean toldStun = false;

    public TempestRoc(EntityType<? extends TempestRoc> type, Level level) {
        super(type, level, BossEvent.BossBarColor.BLUE);
        this.moveControl = new FlyingMoveControl(this, 20, true);
        this.setNoGravity(true);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return baseAttributes(3000.0, 16.0, 0.2).add(Attributes.FLYING_SPEED, 0.5);
    }

    @Override
    protected Item shardItem() {
        return ModItems.STORM_SHARD.get();
    }

    @Override
    protected String phaseLine() {
        return Story.ROC_PHASE;
    }

    @Override
    protected String finalPhaseLine() {
        return Story.ROC_FINAL;
    }

    @Override
    protected String deathLine() {
        return Story.ROC_DEATH;
    }

    @Override
    public String awakenLine() {
        return "The wind has been waiting.";
    }

    @Override
    public double spawnHeightOffset() {
        return 10.0;
    }

    @Override
    protected int abilityInterval() {
        return 1000000; // the Roc does not use the periodic ability timer
    }

    /** The Roc only flies: no ground goals, just targeting. */
    @Override
    protected void registerGoals() {
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    protected void tickBoss(@Nullable LivingEntity target) {
        if (target == null) {
            this.mode = Mode.HOVER;
            return;
        }
        if (this.shieldTicks > 0) {
            return;
        }
        switch (this.mode) {
            case HOVER -> {
                if (phase >= 2 && --this.gustTimer <= 0) {
                    this.gustTimer = 260;
                    gust();
                }
                this.angle += phase >= 3 ? 0.11 : phase == 2 ? 0.09 : 0.06;
                double x = target.getX() + Math.cos(this.angle) * 10.0;
                double z = target.getZ() + Math.sin(this.angle) * 10.0;
                double y = target.getY() + 8.0;
                this.getMoveControl().setWantedPosition(x, y, z, 1.0);
                this.getLookControl().setLookAt(target, 30.0f, 30.0f);
                int every = phase >= 3 ? 25 : 45;
                if (phase >= 2 && this.tickCount % every == 0) {
                    strike(target);
                    if (phase >= 3) {
                        strike(target);
                    }
                }
                if (--this.modeTicks <= 0) {
                    this.mode = Mode.TELEGRAPH;
                    this.modeTicks = phase >= 3 ? 18 : 25;
                    this.chainDives = phase >= 3 ? 1 : 0;
                    this.playSound(SoundEvents.PHANTOM_SWOOP, 3.0f, 0.6f);
                }
            }
            case TELEGRAPH -> {
                this.getLookControl().setLookAt(target, 60.0f, 60.0f);
                if (this.level() instanceof ServerLevel serverLevel) {
                    serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, getX(), getY() + 0.9, getZ(),
                            8, 1.4, 0.6, 1.4, 0.1);
                }
                if (--this.modeTicks <= 0) {
                    this.mode = Mode.DIVE;
                    this.modeTicks = 40;
                    this.diveTo = target.position().add(0.0, target.getBbHeight() * 0.5, 0.0);
                }
            }
            case DIVE -> {
                this.getMoveControl().setWantedPosition(diveTo.x, diveTo.y, diveTo.z,
                        phase >= 3 ? 3.4 : phase == 2 ? 3.0 : 2.4);
                if (this.getBoundingBox().inflate(0.6).intersects(target.getBoundingBox())) {
                    float damage = phase >= 3 ? 60.0f : phase == 2 ? 48.0f : 36.0f;
                    target.hurt(this.damageSources().mobAttack(this), damage);
                    if (phase >= 2) {
                        target.hurt(this.damageSources().magic(), phase >= 3 ? 12.0f : 7.0f); // ignores armour
                    }
                    Vec3 dir = target.position().subtract(this.position()).multiply(1.0, 0.0, 1.0).normalize();
                    target.push(dir.x * 1.8, 0.7, dir.z * 1.8);
                    target.hurtMarked = true;
                    this.playSound(SoundEvents.LIGHTNING_BOLT_THUNDER, 2.0f, 1.4f);
                    endDive();
                } else if (--this.modeTicks <= 0 || this.position().distanceToSqr(diveTo) < 4.0) {
                    // Gimmick: a dive that misses slams the Roc into the ground and leaves it stunned and exposed.
                    this.mode = Mode.STUNNED;
                    this.modeTicks = phase >= 3 ? 50 : 70;
                    this.chainDives = 0;
                    this.playSound(SoundEvents.ANVIL_LAND, 2.0f, 0.6f);
                    if (!this.toldStun) {
                        this.toldStun = true;
                        this.say("The Roc misses and slams into the ground, stunned. Strike now, before it rises!");
                    }
                }
            }
            case STUNNED -> {
                this.setDeltaMovement(Vec3.ZERO);
                if (this.level() instanceof ServerLevel serverLevel) {
                    serverLevel.sendParticles(ParticleTypes.CRIT, getX(), getY() + 1.5, getZ(), 6, 1.2, 0.4, 1.2, 0.1);
                }
                if (--this.modeTicks <= 0) {
                    this.mode = Mode.HOVER;
                    this.modeTicks = phase >= 3 ? 40 : phase == 2 ? 50 : 90;
                }
            }
        }
    }

    /** A blast of wind that shoves every nearby player away from the Roc. */
    private void gust() {
        for (Player player : this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(26.0))) {
            Vec3 dir = player.position().subtract(this.position()).multiply(1.0, 0.0, 1.0).normalize();
            player.push(dir.x * 1.6, 0.5, dir.z * 1.6);
            player.hurtMarked = true;
        }
        this.playSound(SoundEvents.ENDER_DRAGON_FLAP, 3.0f, 0.6f);
        if (this.level() instanceof ServerLevel serverLevel) {
            serverLevel.sendParticles(ParticleTypes.CLOUD, getX(), getY(), getZ(), 80, 4.0, 1.0, 4.0, 0.4);
        }
    }

    @Override
    protected float incomingMultiplier() {
        return this.mode == Mode.STUNNED ? 1.0f : 0.5f;
    }

    @Override
    protected float capMultiplier() {
        return this.mode == Mode.STUNNED ? 2.5f : 1.0f;
    }

    private void endDive() {
        if (phase >= 3 && this.chainDives > 0) {
            this.chainDives--;
            this.mode = Mode.TELEGRAPH;
            this.modeTicks = 12;
            return;
        }
        this.mode = Mode.HOVER;
        this.modeTicks = phase >= 3 ? 40 : phase == 2 ? 50 : 90;
    }

    private void strike(LivingEntity target) {
        if (!(this.level() instanceof ServerLevel serverLevel)) {
            return;
        }
        BlockPos pos = BlockPos.containing(target.getX() + (random.nextDouble() - 0.5) * 5.0, target.getY(),
                target.getZ() + (random.nextDouble() - 0.5) * 5.0);
        LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(serverLevel);
        if (bolt != null) {
            bolt.moveTo(Vec3.atBottomCenterOf(pos));
            serverLevel.addFreshEntity(bolt);
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        // The storm cannot hurt its own Warden.
        if (source.is(DamageTypeTags.IS_LIGHTNING) || source.is(DamageTypeTags.IS_FIRE)) {
            return false;
        }
        return super.hurt(source, amount);
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }
}
