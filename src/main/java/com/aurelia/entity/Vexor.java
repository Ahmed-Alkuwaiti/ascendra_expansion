package com.aurelia.entity;

import com.aurelia.block.ClockDialBlock;
import com.aurelia.registry.ModBlocks;
import com.aurelia.registry.ModEntities;
import com.aurelia.registry.ModItems;
import com.aurelia.world.ArenaBuilder;
import com.aurelia.world.Story;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * Vexor, the Hour Eater, Warden of the Clockwork Rift (6000 HP). A clockwork eye in a cage of turning rings, hovering
 * over a clock face. The rings turn most blows aside: he takes 40% damage.
 *  TWELVE STRIKES: the numerals of the clock face light one after another round the dial, and each one bursts a second
 *  later. Keep stepping round them.
 *  THE PENDULUM: a line marks the face from rim to rim; then a pendulum sweeps it.
 *  TIME STOP: everyone is slowed almost to a halt and bolts of rift light lance three of them.
 *  THE HOUR STRIKES: he channels for ten seconds, sets the Master Clock to a new hour and scrambles the three dials round
 *  the face. Wind all three to his hour before the channel ends and his gears SEIZE: he crashes onto the face for seven
 *  seconds (full damage, caps raised 2.5x). Fail and he EATS THE HOUR: everyone is thrown back to where they stood five
 *  seconds earlier and loses 30% of their health, and he mends 5% of his.
 * Phase 2 (66%): Secondhands, and the strikes run both rings of numerals. Phase 3 (33%): the hour strikes more often.
 */
public class Vexor extends AureliaBoss {
    private int hourTimer = 520;
    private int channelTicks = 0;
    private int targetHour = 0;
    private int jamTicks = 0;
    private int casts = 0;
    private double angle = 0.0;
    private int pendulumTicks = 0;
    private double pendulumAngle = 0.0;
    private final List<Vec3> strikeAt = new ArrayList<>();
    private final List<Integer> strikeTicks = new ArrayList<>();
    private final Map<UUID, ArrayDeque<Vec3>> history = new HashMap<>();

    public Vexor(EntityType<? extends Vexor> type, Level level) {
        super(type, level, BossEvent.BossBarColor.PURPLE);
        this.moveControl = new FlyingMoveControl(this, 20, true);
        this.setNoGravity(true);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return baseAttributes(6000.0, 26.0, 0.2).add(Attributes.FLYING_SPEED, 0.45);
    }

    @Override
    protected Item shardItem() {
        return ModItems.HOUR_CORE.get();
    }

    @Override
    protected String phaseLine() {
        return Story.VEXOR_PHASE;
    }

    @Override
    protected String finalPhaseLine() {
        return Story.VEXOR_FINAL;
    }

    @Override
    protected String deathLine() {
        return Story.VEXOR_DEATH;
    }

    @Override
    public String awakenLine() {
        return "It is later than you think.";
    }

    @Override
    public double spawnHeightOffset() {
        return 9.0;
    }

    @Override
    protected int abilityInterval() {
        return phase >= 3 ? 60 : phase == 2 ? 75 : 95;
    }

    @Override
    protected void registerGoals() {
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
    }

    private Vec3 centre() {
        return this.arena != null ? Vec3.atBottomCenterOf(this.arena) : this.position();
    }

    @Override
    protected void tickBoss(@Nullable LivingEntity target) {
        if (!(this.level() instanceof ServerLevel level)) {
            return;
        }
        Vec3 c = centre();
        recordHistory(level);
        tickStrikes(level);
        tickPendulum(level, c);
        if (this.jamTicks > 0) {
            this.jamTicks--;
            this.getMoveControl().setWantedPosition(c.x, c.y + 0.5, c.z - 5.0, 1.0);
            level.sendParticles(ParticleTypes.CRIT, getX(), getY() + 2.5, getZ(), 8, 2.0, 1.5, 2.0, 0.1);
            level.sendParticles(ParticleTypes.SMOKE, getX(), getY() + 3.0, getZ(), 4, 1.5, 1.0, 1.5, 0.02);
            if (this.jamTicks == 0) {
                this.playSound(SoundEvents.PISTON_EXTEND, 4.0f, 0.4f);
            }
            return;
        }
        this.angle += 0.015;
        double bob = Math.sin(this.tickCount * 0.04) * 1.2;
        this.getMoveControl().setWantedPosition(c.x + Math.cos(this.angle) * 6.0, c.y + 9.0 + bob, c.z + Math.sin(this.angle) * 6.0, 1.0);
        if (target != null) {
            this.getLookControl().setLookAt(target, 20.0f, 20.0f);
        }
        if (this.channelTicks > 0) {
            this.channelTicks--;
            if (this.tickCount % 20 == 0) {
                this.playSound(SoundEvents.BELL_BLOCK, 4.0f, 0.5f + (200 - this.channelTicks) * 0.004f);
                int secs = this.channelTicks / 20;
                for (ServerPlayer player : level.getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(48.0))) {
                    player.displayClientMessage(Component.literal("Set the three clocks to " + ClockDialBlock.hourName(this.targetHour)
                            + "  (" + secs + ")").withStyle(ChatFormatting.GOLD), true);
                }
            }
            BlockPos master = masterPos();
            if (master != null) {
                level.sendParticles(ParticleTypes.REVERSE_PORTAL, master.getX() + 0.5, master.getY() + 1.0, master.getZ() + 0.5, 6, 0.3, 0.5, 0.3, 0.05);
            }
            if (this.channelTicks == 0) {
                eatTheHour(level);
            }
            return;
        }
        if (target != null && --this.hourTimer <= 0) {
            this.hourTimer = phase >= 3 ? 440 : 520;
            beginHour(level);
        }
    }

    // ---- the hour strikes

    @Nullable
    private BlockPos masterPos() {
        return this.arena == null ? null : this.arena.offset(ArenaBuilder.MASTER[0], ArenaBuilder.MASTER[1], ArenaBuilder.MASTER[2]);
    }

    private List<BlockPos> dialPositions() {
        List<BlockPos> out = new ArrayList<>();
        if (this.arena != null) {
            for (int[] d : ArenaBuilder.DIALS) {
                BlockPos p = this.arena.offset(d[0], 0, d[1]);
                if (this.level().getBlockState(p).getBlock() instanceof ClockDialBlock) {
                    out.add(p);
                }
            }
        }
        return out;
    }

    private void beginHour(ServerLevel level) {
        List<BlockPos> dials = dialPositions();
        BlockPos master = masterPos();
        if (dials.isEmpty() || master == null || !level.getBlockState(master).is(ModBlocks.MASTER_CLOCK.get())) {
            return;
        }
        this.targetHour = this.random.nextInt(12);
        level.setBlock(master, level.getBlockState(master).setValue(ClockDialBlock.HOUR, this.targetHour), 3);
        for (BlockPos d : dials) {
            int h = (this.targetHour + 1 + this.random.nextInt(11)) % 12;
            level.setBlock(d, level.getBlockState(d).setValue(ClockDialBlock.HOUR, h).setValue(ClockDialBlock.FILLED, false), 3);
        }
        this.channelTicks = 200;
        this.playSound(SoundEvents.WARDEN_ROAR, 4.0f, 1.6f);
        for (ServerPlayer player : level.getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(48.0))) {
            Story.title(player, "THE HOUR STRIKES", "Wind the three clocks to " + ClockDialBlock.hourName(this.targetHour), ChatFormatting.GOLD);
        }
    }

    /** Called by an arena dial whenever someone winds it. */
    public void onDialSet() {
        if (this.channelTicks <= 0) {
            return;
        }
        List<BlockPos> dials = dialPositions();
        for (BlockPos d : dials) {
            if (this.level().getBlockState(d).getValue(ClockDialBlock.HOUR) != this.targetHour) {
                return;
            }
        }
        this.channelTicks = 0;
        this.jamTicks = 140;
        this.say("Every clock agrees. Vexor's gears seize and he falls, grinding, onto the face. Strike the eye!");
        this.playSound(SoundEvents.ANVIL_LAND, 4.0f, 0.4f);
        for (ServerPlayer player : this.level().getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(48.0))) {
            Story.title(player, "", "His gears seize", ChatFormatting.GOLD);
        }
    }

    private void eatTheHour(ServerLevel level) {
        this.say("Vexor eats the hour. Five seconds of your life go back into the machine.");
        this.playSound(SoundEvents.ENDERMAN_TELEPORT, 4.0f, 0.3f);
        for (ServerPlayer player : level.getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(48.0))) {
            if (player.isCreative() || player.isSpectator()) {
                continue;
            }
            ArrayDeque<Vec3> past = this.history.get(player.getUUID());
            if (past != null && !past.isEmpty()) {
                Vec3 then = past.peekFirst();
                level.sendParticles(ParticleTypes.REVERSE_PORTAL, player.getX(), player.getY() + 1.0, player.getZ(), 60, 0.4, 1.0, 0.4, 0.2);
                player.teleportTo(then.x, then.y, then.z);
                player.fallDistance = 0;
            }
            player.hurt(this.damageSources().magic(), player.getMaxHealth() * 0.3f);
            player.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 60, 0));
        }
        this.heal(this.getMaxHealth() * 0.05f);
    }

    private void recordHistory(ServerLevel level) {
        if (this.tickCount % 20 != 0) {
            return;
        }
        for (ServerPlayer player : level.getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(64.0))) {
            ArrayDeque<Vec3> q = this.history.computeIfAbsent(player.getUUID(), k -> new ArrayDeque<>());
            q.addLast(player.position());
            while (q.size() > 5) {
                q.pollFirst();
            }
        }
    }

    // ---- attacks

    @Override
    protected void castAbility(LivingEntity target) {
        if (this.channelTicks > 0 || this.jamTicks > 0) {
            return;
        }
        this.casts++;
        if (phase >= 2 && this.casts % 3 == 0) {
            summonSecondhands(target);
        }
        switch (this.casts % 3) {
            case 0 -> twelveStrikes();
            case 1 -> beginPendulum();
            default -> timeStop();
        }
    }

    private void twelveStrikes() {
        Vec3 c = centre();
        double start = this.random.nextDouble() * Math.PI * 2.0;
        int dir = this.random.nextBoolean() ? 1 : -1;
        for (int k = 0; k < 12; k++) {
            double a = start + dir * k * Math.PI / 6.0;
            double r = phase >= 2 && k % 2 == 1 ? 10.5 : 7.0;
            this.strikeAt.add(new Vec3(c.x + Math.cos(a) * r, c.y, c.z + Math.sin(a) * r));
            this.strikeTicks.add(24 + k * 5);
        }
        this.playSound(SoundEvents.BELL_BLOCK, 3.0f, 1.2f);
    }

    private void tickStrikes(ServerLevel level) {
        float damage = phase >= 3 ? 38.0f : phase == 2 ? 30.0f : 24.0f;
        for (int i = this.strikeAt.size() - 1; i >= 0; i--) {
            Vec3 at = this.strikeAt.get(i);
            int t = this.strikeTicks.get(i) - 1;
            if (t <= 22 && t % 3 == 0) {
                for (int k = 0; k < 10; k++) {
                    double a = k * Math.PI / 5.0;
                    level.sendParticles(ParticleTypes.END_ROD, at.x + Math.cos(a) * 2.2, at.y + 0.2, at.z + Math.sin(a) * 2.2, 1, 0, 0, 0, 0);
                }
            }
            if (t <= 0) {
                for (Player player : level.getEntitiesOfClass(Player.class, new net.minecraft.world.phys.AABB(at, at).inflate(2.2, 3.0, 2.2))) {
                    player.hurt(this.damageSources().magic(), damage);
                    player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 1));
                }
                level.sendParticles(ParticleTypes.REVERSE_PORTAL, at.x, at.y + 1.0, at.z, 50, 0.5, 2.0, 0.5, 0.2);
                level.sendParticles(ParticleTypes.ELECTRIC_SPARK, at.x, at.y + 0.5, at.z, 20, 1.0, 0.5, 1.0, 0.2);
                level.playSound(null, BlockPos.containing(at), SoundEvents.BELL_BLOCK, SoundSource.HOSTILE, 1.5f, 1.8f);
                this.strikeAt.remove(i);
                this.strikeTicks.remove(i);
            } else {
                this.strikeTicks.set(i, t);
            }
        }
    }

    private void beginPendulum() {
        this.pendulumTicks = 32;
        this.pendulumAngle = this.random.nextDouble() * Math.PI;
        this.playSound(SoundEvents.CHAIN_PLACE, 4.0f, 0.4f);
    }

    private void tickPendulum(ServerLevel level, Vec3 c) {
        if (this.pendulumTicks <= 0) {
            return;
        }
        this.pendulumTicks--;
        double dx = Math.cos(this.pendulumAngle);
        double dz = Math.sin(this.pendulumAngle);
        if (this.pendulumTicks % 4 == 0 && this.pendulumTicks > 0) {
            for (double t = -13.0; t <= 13.0; t += 1.0) {
                level.sendParticles(ParticleTypes.SMALL_FLAME, c.x + dx * t, c.y + 0.2, c.z + dz * t, 1, 0.05, 0.0, 0.05, 0.0);
            }
        }
        if (this.pendulumTicks == 0) {
            float damage = phase >= 3 ? 52.0f : phase == 2 ? 42.0f : 34.0f;
            for (Player player : level.getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(40.0))) {
                double rx = player.getX() - c.x;
                double rz = player.getZ() - c.z;
                double off = rx * dz - rz * dx;
                if (Math.abs(off) < 2.0 && Math.abs(rx * dx + rz * dz) < 14.0 && Math.abs(player.getY() - c.y) < 4.0) {
                    player.hurt(this.damageSources().mobAttack(this), damage);
                    double s = Math.signum(off == 0 ? 1 : off);
                    player.push(dz * s * 1.6, 0.5, -dx * s * 1.6);
                    player.hurtMarked = true;
                }
            }
            for (double t = -13.0; t <= 13.0; t += 0.5) {
                level.sendParticles(ParticleTypes.SWEEP_ATTACK, c.x + dx * t, c.y + 1.0, c.z + dz * t, 1, 0, 0, 0, 0);
            }
            this.playSound(SoundEvents.PLAYER_ATTACK_SWEEP, 4.0f, 0.4f);
        }
    }

    private void timeStop() {
        List<Player> players = this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(32.0), p -> !p.isCreative() && !p.isSpectator());
        for (Player player : players) {
            player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 50, 4));
            player.addEffect(new MobEffectInstance(MobEffects.DIG_SLOWDOWN, 60, 2));
        }
        if (this.level() instanceof ServerLevel level) {
            Vec3 eye = this.position().add(0.0, 4.0, 0.0);
            for (int k = 0; k < 3 && !players.isEmpty(); k++) {
                Player victim = players.get(this.random.nextInt(players.size()));
                Vec3 to = victim.position().add(0.0, 1.0, 0.0);
                Vec3 d = to.subtract(eye);
                for (double t = 0.0; t < 1.0; t += 0.04) {
                    Vec3 p = eye.add(d.scale(t));
                    level.sendParticles(ParticleTypes.REVERSE_PORTAL, p.x, p.y, p.z, 1, 0, 0, 0, 0);
                }
                victim.hurt(this.damageSources().indirectMagic(this, this), phase >= 3 ? 18.0f : 14.0f);
            }
        }
        this.say("Time stops. The eye does not.");
        this.playSound(SoundEvents.BEACON_DEACTIVATE, 4.0f, 0.5f);
    }

    private void summonSecondhands(LivingEntity target) {
        int existing = this.level().getEntitiesOfClass(Secondhand.class, this.getBoundingBox().inflate(40.0)).size();
        for (int i = 0; i < 2 && existing + i < 5; i++) {
            Secondhand hand = ModEntities.SECONDHAND.get().create(this.level());
            if (hand == null) {
                continue;
            }
            hand.moveTo(getX() + (random.nextDouble() - 0.5) * 8.0, getY(), getZ() + (random.nextDouble() - 0.5) * 8.0, 0.0f, 0.0f);
            hand.setTarget(target);
            this.level().addFreshEntity(hand);
        }
    }

    @Override
    protected float incomingMultiplier() {
        return this.jamTicks > 0 ? 1.0f : 0.4f;
    }

    @Override
    protected float capMultiplier() {
        return this.jamTicks > 0 ? 2.5f : 1.0f;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.is(DamageTypeTags.IS_FALL) || source.is(DamageTypeTags.IS_LIGHTNING)) {
            return false;
        }
        return super.hurt(source, amount);
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }
}
