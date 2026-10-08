package com.aurelia.entity;

import com.aurelia.registry.ModItems;
import com.aurelia.world.Story;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Drowned;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * Vorath, the Tide Devourer, Warden of the Drowned Expanse (4500 HP). A leviathan that circles the arena under the water.
 *  Submerged he takes only 30% damage. Ringing one of the arena's Tide Bells drags him up against the edge of the ring,
 *  EXPOSED for seven seconds: full damage, damage caps raised 2.5x. A bell then needs thirty seconds to recover.
 *  DEVOUR: a ring of bubbles marks where you stand, then he bursts out of the sea and lunges across the ring through it.
 *  UNDERTOW: the sea drags everyone on the ring toward the water.
 * Phase 2 (66%): TIDAL SURGE (a wave that throws you back) and CALL OF THE DEEP (drowned climb onto the ring).
 * Phase 3 (33%): devours come in pairs, faster, and the undertow is stronger.
 */
public class Vorath extends AureliaBoss {
    private enum Mode { CIRCLE, TELL, LUNGE, RETURN, RISE, EXPOSED }

    private static final double CIRCLE_RADIUS = 18.0;
    private Mode mode = Mode.CIRCLE;
    private int modeTicks = 0;
    private double angle = 0.0;
    private Vec3 lungeTo = Vec3.ZERO;
    private Vec3 approach = Vec3.ZERO;
    private BlockPos bell = BlockPos.ZERO;
    private int devourTimer = 160;
    private int undertowTimer = 220;
    private int undertowTicks = 0;
    private int surgeTimer = 300;
    private int callTimer = 360;
    private int chain = 0;
    private boolean toldBells = false;

    public Vorath(EntityType<? extends Vorath> type, Level level) {
        super(type, level, BossEvent.BossBarColor.BLUE);
        this.setNoGravity(true);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return baseAttributes(4500.0, 20.0, 0.3);
    }

    @Override
    protected Item shardItem() {
        return ModItems.LEVIATHAN_PEARL.get();
    }

    @Override
    protected String phaseLine() {
        return Story.VORATH_PHASE;
    }

    @Override
    protected String finalPhaseLine() {
        return Story.VORATH_FINAL;
    }

    @Override
    protected String deathLine() {
        return Story.VORATH_DEATH;
    }

    @Override
    public String awakenLine() {
        return "The sea opens its mouth.";
    }

    @Override
    protected int abilityInterval() {
        return 1000000; // Vorath runs on his own timers
    }

    @Override
    public Vec3 spawnPosition(BlockPos altar) {
        return new Vec3(altar.getX() + 0.5, altar.getY() - 6, altar.getZ() - CIRCLE_RADIUS + 0.5);
    }

    @Override
    protected Vec3 lootPosition() {
        return this.arena != null ? Vec3.atCenterOf(this.arena).add(0.0, 1.0, 2.0) : super.lootPosition();
    }

    @Override
    protected void registerGoals() {
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
    }

    // ---- he swims like he flies: steered every tick, no gravity, no water drag beyond his own

    @Override
    public void travel(Vec3 input) {
        if (this.isControlledByLocalInstance()) {
            this.move(MoverType.SELF, this.getDeltaMovement());
            this.setDeltaMovement(this.getDeltaMovement().scale(0.88));
        } else {
            super.travel(input);
        }
    }

    @Override
    public boolean canBreatheUnderwater() {
        return true;
    }

    @Override
    public boolean isPushedByFluid() {
        return false;
    }

    private void steer(Vec3 dest, double speed) {
        Vec3 d = dest.subtract(this.position());
        double len = d.length();
        if (len < 0.05) {
            this.setDeltaMovement(this.getDeltaMovement().scale(0.5));
            return;
        }
        Vec3 want = d.scale(Math.min(speed, len) / len);
        this.setDeltaMovement(this.getDeltaMovement().lerp(want, 0.3));
        double horiz = Math.sqrt(d.x * d.x + d.z * d.z);
        if (horiz > 0.2) {
            float yaw = (float) (Mth.atan2(d.z, d.x) * Mth.RAD_TO_DEG) - 90.0f;
            this.setYRot(Mth.rotLerp(0.25f, this.getYRot(), yaw));
            this.yBodyRot = this.getYRot();
            this.yHeadRot = this.getYRot();
        }
        this.setXRot(Mth.clamp((float) (-Mth.atan2(d.y, Math.max(horiz, 0.01)) * Mth.RAD_TO_DEG) * 0.5f, -35.0f, 35.0f));
    }

    private Vec3 centre() {
        return this.arena != null ? Vec3.atBottomCenterOf(this.arena) : this.position();
    }

    // ---- the fight

    @Override
    protected void tickBoss(@Nullable LivingEntity target) {
        Vec3 c = centre();
        if (this.level() instanceof ServerLevel level && this.isInWater() && this.tickCount % 4 == 0) {
            level.sendParticles(ParticleTypes.BUBBLE, getX(), getY() + 1.0, getZ(), 6, 2.0, 0.8, 2.0, 0.05);
        }
        if (this.undertowTicks > 0) {
            this.undertowTicks--;
            pullTowardSea(c, phase >= 3 ? 0.09 : 0.06);
        }
        switch (this.mode) {
            case CIRCLE -> {
                this.angle += phase >= 3 ? 0.035 : 0.025;
                double bob = Math.sin(this.tickCount * 0.05) * 1.2;
                steer(new Vec3(c.x + Math.cos(this.angle) * CIRCLE_RADIUS, c.y - 6.0 + bob, c.z + Math.sin(this.angle) * CIRCLE_RADIUS), 0.45);
                if (target == null) {
                    return;
                }
                if (!this.toldBells && this.tickCount > 100) {
                    this.toldBells = true;
                    this.say("He will not come within reach on his own. The Tide Bells on the ring's edge: ring one and the sea will hand him to you.");
                }
                if (--this.devourTimer <= 0) {
                    beginDevour(target, phase >= 3 ? 1 : 0);
                } else if (--this.undertowTimer <= 0) {
                    this.undertowTimer = phase >= 3 ? 220 : 300;
                    this.undertowTicks = 50;
                    this.say("The undertow drags at your legs.");
                    this.playSound(SoundEvents.BUBBLE_COLUMN_WHIRLPOOL_AMBIENT, 4.0f, 0.5f);
                } else if (phase >= 2 && --this.surgeTimer <= 0) {
                    this.surgeTimer = phase >= 3 ? 240 : 320;
                    tidalSurge(c);
                } else if (phase >= 2 && --this.callTimer <= 0) {
                    this.callTimer = 420;
                    callTheDeep(c, target);
                }
            }
            case TELL -> {
                steer(this.approach.add(0.0, -3.0, 0.0), 0.6);
                if (this.level() instanceof ServerLevel level) {
                    for (int i = 0; i < 12; i++) {
                        double a = i * Math.PI / 6 + this.tickCount * 0.1;
                        level.sendParticles(ParticleTypes.BUBBLE_POP, lungeTo.x + Math.cos(a) * 3.0, lungeTo.y + 0.2, lungeTo.z + Math.sin(a) * 3.0, 1, 0.0, 0.2, 0.0, 0.02);
                    }
                    level.sendParticles(ParticleTypes.SPLASH, lungeTo.x, lungeTo.y + 0.2, lungeTo.z, 6, 1.5, 0.1, 1.5, 0.1);
                }
                if (--this.modeTicks <= 0) {
                    this.mode = Mode.LUNGE;
                    this.modeTicks = 34;
                    this.playSound(SoundEvents.ELDER_GUARDIAN_CURSE, 3.0f, 0.5f);
                }
            }
            case LUNGE -> {
                // breach next to the ring first, then hurl himself across the stone
                boolean breached = this.position().distanceToSqr(this.approach) < 9.0 || this.getY() > c.y - 0.5;
                steer(breached ? this.lungeTo : this.approach, breached ? 1.2 : 0.9);
                if (this.position().distanceToSqr(this.lungeTo) < 4.0 || --this.modeTicks <= 0) {
                    devourImpact();
                    if (this.chain > 0) {
                        this.chain--;
                        this.mode = Mode.RETURN;
                        this.modeTicks = 18;
                    } else {
                        this.mode = Mode.RETURN;
                        this.modeTicks = 40;
                    }
                }
            }
            case RETURN -> {
                Vec3 out = horizontalFrom(c, this.position(), 17.0);
                steer(new Vec3(out.x, c.y + 0.5, out.z), 0.8);
                if (--this.modeTicks <= 0 || horizontalDist(c, this.position()) > 15.5) {
                    if (this.chain > 0 && target != null) {
                        beginDevour(target, this.chain);
                        this.modeTicks = 22;
                    } else {
                        this.mode = Mode.CIRCLE;
                        this.angle = Math.atan2(this.getZ() - c.z, this.getX() - c.x);
                        this.devourTimer = phase >= 3 ? 110 : phase == 2 ? 140 : 170;
                    }
                }
            }
            case RISE -> {
                Vec3 spot = exposedSpot(c);
                steer(spot, 0.7);
                if (this.position().distanceToSqr(spot) < 2.0 || --this.modeTicks <= 0) {
                    this.mode = Mode.EXPOSED;
                    this.modeTicks = phase >= 3 ? 110 : 140;
                    this.playSound(SoundEvents.ELDER_GUARDIAN_HURT, 4.0f, 0.5f);
                }
            }
            case EXPOSED -> {
                steer(exposedSpot(c), 0.2);
                if (this.level() instanceof ServerLevel level) {
                    level.sendParticles(ParticleTypes.CRIT, getX(), getY() + 2.5, getZ(), 6, 2.0, 0.6, 2.0, 0.1);
                }
                if (this.modeTicks % 30 == 0) {
                    thrash();
                }
                if (--this.modeTicks <= 0) {
                    this.mode = Mode.CIRCLE;
                    this.angle = Math.atan2(this.getZ() - c.z, this.getX() - c.x);
                    this.devourTimer = 80;
                    this.playSound(SoundEvents.GENERIC_SPLASH, 3.0f, 0.5f);
                }
            }
        }
    }

    /** Called by an arena Tide Bell. Returns true if the bell drags him up. */
    public boolean onBellRung(BlockPos bellPos) {
        if (this.arena == null || this.mode == Mode.EXPOSED || this.mode == Mode.RISE || !this.isAlive()) {
            return false;
        }
        this.bell = bellPos;
        this.mode = Mode.RISE;
        this.modeTicks = 60;
        this.chain = 0;
        this.say("The bell's voice drags Vorath up against the stone. Strike now!");
        for (ServerPlayer player : this.level().getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(48.0))) {
            Story.title(player, "", "Vorath surfaces", ChatFormatting.DARK_AQUA);
        }
        return true;
    }

    private Vec3 exposedSpot(Vec3 c) {
        Vec3 out = horizontalFrom(c, Vec3.atBottomCenterOf(this.bell), 15.0);
        return new Vec3(out.x, c.y - 2.0, out.z);
    }

    private static Vec3 horizontalFrom(Vec3 c, Vec3 toward, double radius) {
        Vec3 d = new Vec3(toward.x - c.x, 0.0, toward.z - c.z);
        if (d.lengthSqr() < 1.0e-4) {
            d = new Vec3(0.0, 0.0, -1.0);
        }
        d = d.normalize().scale(radius);
        return new Vec3(c.x + d.x, c.y, c.z + d.z);
    }

    private static double horizontalDist(Vec3 a, Vec3 b) {
        double dx = a.x - b.x;
        double dz = a.z - b.z;
        return Math.sqrt(dx * dx + dz * dz);
    }

    private void beginDevour(LivingEntity target, int chainLeft) {
        Vec3 c = centre();
        this.mode = Mode.TELL;
        this.modeTicks = phase >= 3 ? 26 : 40;
        this.chain = chainLeft;
        this.lungeTo = target.position();
        this.approach = horizontalFrom(c, this.lungeTo, 15.0).add(0.0, 0.5, 0.0);
        this.playSound(SoundEvents.BUBBLE_COLUMN_UPWARDS_AMBIENT, 4.0f, 0.5f);
        if (target instanceof Player player) {
            player.displayClientMessage(net.minecraft.network.chat.Component.literal("The water under you starts to churn. MOVE.")
                    .withStyle(ChatFormatting.DARK_AQUA), true);
        }
    }

    private void devourImpact() {
        float damage = phase >= 3 ? 64.0f : phase == 2 ? 52.0f : 40.0f;
        for (LivingEntity victim : this.level().getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(2.0, 1.5, 2.0),
                e -> e != this && !(e instanceof AureliaBoss) && !(e instanceof Drowned))) {
            victim.hurt(this.damageSources().mobAttack(this), damage);
            victim.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 60, 0));
            victim.push(0.0, 0.9, 0.0);
            victim.hurtMarked = true;
        }
        this.playSound(SoundEvents.RAVAGER_ATTACK, 4.0f, 0.4f);
        this.playSound(SoundEvents.GENERIC_SPLASH, 4.0f, 0.6f);
        if (this.level() instanceof ServerLevel level) {
            level.sendParticles(ParticleTypes.SPLASH, getX(), getY() + 1.0, getZ(), 120, 3.0, 1.0, 3.0, 0.3);
        }
    }

    /** Pushes everyone near the arena outward, toward the water. */
    private void pullTowardSea(Vec3 c, double strength) {
        for (Player player : this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(40.0))) {
            if (player.isCreative() || player.isSpectator() || horizontalDist(c, player.position()) > 22.0) {
                continue;
            }
            Vec3 out = new Vec3(player.getX() - c.x, 0.0, player.getZ() - c.z);
            if (out.lengthSqr() < 0.01) {
                continue;
            }
            out = out.normalize().scale(strength);
            player.push(out.x, 0.0, out.z);
            player.hurtMarked = true;
            if (this.level() instanceof ServerLevel level && this.tickCount % 5 == 0) {
                level.sendParticles(ParticleTypes.BUBBLE_POP, player.getX(), player.getY() + 0.2, player.getZ(), 4, 0.4, 0.1, 0.4, 0.02);
            }
        }
    }

    private void tidalSurge(Vec3 c) {
        this.say("Vorath heaves, and the sea comes over the ring.");
        this.playSound(SoundEvents.GENERIC_SPLASH, 5.0f, 0.4f);
        for (Player player : this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(40.0))) {
            if (horizontalDist(c, player.position()) > 20.0) {
                continue;
            }
            Vec3 away = player.position().subtract(this.position()).multiply(1.0, 0.0, 1.0);
            away = away.lengthSqr() < 0.01 ? new Vec3(1, 0, 0) : away.normalize();
            player.push(away.x * 1.4, 0.55, away.z * 1.4);
            player.hurtMarked = true;
            player.hurt(this.damageSources().magic(), phase >= 3 ? 16.0f : 12.0f);
            player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 1));
        }
        if (this.level() instanceof ServerLevel level) {
            for (int i = 0; i < 36; i++) {
                double a = i * Math.PI / 18;
                level.sendParticles(ParticleTypes.SPLASH, c.x + Math.cos(a) * 11, c.y + 0.5, c.z + Math.sin(a) * 11, 10, 0.5, 0.5, 0.5, 0.3);
            }
        }
    }

    private void callTheDeep(Vec3 c, LivingEntity target) {
        int existing = this.level().getEntitiesOfClass(Drowned.class, this.getBoundingBox().inflate(40.0)).size();
        int count = phase >= 3 ? 3 : 2;
        for (int i = 0; i < count && existing + i < 6; i++) {
            Drowned drowned = EntityType.DROWNED.create(this.level());
            if (drowned == null) {
                continue;
            }
            double a = this.random.nextDouble() * Math.PI * 2.0;
            drowned.moveTo(c.x + Math.cos(a) * 10.0, c.y, c.z + Math.sin(a) * 10.0, this.random.nextFloat() * 360.0f, 0.0f);
            drowned.setTarget(target);
            drowned.setPersistenceRequired();
            this.level().addFreshEntity(drowned);
        }
        this.say("Drowned sailors haul themselves out of the sea and onto the ring.");
    }

    private void thrash() {
        for (LivingEntity victim : this.level().getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(2.5),
                e -> e != this && !(e instanceof AureliaBoss))) {
            Vec3 away = victim.position().subtract(this.position()).multiply(1.0, 0.0, 1.0);
            away = away.lengthSqr() < 0.01 ? new Vec3(1, 0, 0) : away.normalize();
            victim.push(away.x * 0.7, 0.35, away.z * 0.7);
            victim.hurtMarked = true;
            victim.hurt(this.damageSources().mobAttack(this), 8.0f);
        }
        this.playSound(SoundEvents.ELDER_GUARDIAN_FLOP, 3.0f, 0.5f);
    }

    @Override
    protected float incomingMultiplier() {
        if (this.mode == Mode.EXPOSED) {
            return 1.0f;
        }
        return this.isInWater() ? 0.3f : 0.6f;
    }

    @Override
    protected float capMultiplier() {
        return this.mode == Mode.EXPOSED ? 2.5f : 1.0f;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.is(DamageTypeTags.IS_DROWNING)) {
            return false;
        }
        return super.hurt(source, amount);
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }
}
