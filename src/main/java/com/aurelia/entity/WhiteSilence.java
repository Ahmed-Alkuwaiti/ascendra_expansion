package com.aurelia.entity;

import com.aurelia.registry.ModEntities;
import com.aurelia.registry.ModItems;
import com.aurelia.world.Story;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.CampfireBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * The White Silence, Warden of the Pale Wastes (5000 HP). It hunts by sound.
 *  COLD: standing near it freezes you (leather armour keeps the cold out, the arena braziers thaw you).
 *  ICE LANCE: a line of frost marks the ground, then ice tears up along it.
 *  THE WHITE: every half minute it draws breath (three seconds' warning), goes invisible and blinds everyone for eight
 *  seconds. Anyone who moves without crouching, jumps, or strikes it standing up is HEARD: it appears behind them and
 *  strikes. A player who creeps up crouching and hits it SHATTERS its composure: the White ends and it staggers for five
 *  seconds (full damage, caps raised 2.5x). Its frozen heart and lantern still glow while it is invisible.
 * Phase 2 (66%): Pale Mirages, copies of itself that shatter into frost when struck.
 * Phase 3 (33%): the White comes more often and lasts longer, and the cold bites harder.
 */
public class WhiteSilence extends AureliaBoss {
    private int whiteTimer = 420;
    private int tellTicks = 0;
    private int whiteTicks = 0;
    private int staggerTicks = 0;
    private int strikeCooldown = 0;
    private final Set<UUID> struck = new HashSet<>();
    private final Map<UUID, Vec3> lastPos = new HashMap<>();
    private int lanceTicks = 0;
    private Vec3 lanceFrom = Vec3.ZERO;
    private Vec3 lanceDir = Vec3.ZERO;
    private int casts = 0;

    public WhiteSilence(EntityType<? extends WhiteSilence> type, Level level) {
        super(type, level, BossEvent.BossBarColor.WHITE);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return baseAttributes(5000.0, 30.0, 0.27);
    }

    @Override
    protected Item shardItem() {
        return ModItems.FROZEN_TEAR.get();
    }

    @Override
    protected String phaseLine() {
        return Story.SILENCE_PHASE;
    }

    @Override
    protected String finalPhaseLine() {
        return Story.SILENCE_FINAL;
    }

    @Override
    protected String deathLine() {
        return Story.SILENCE_DEATH;
    }

    @Override
    public String awakenLine() {
        return "...";
    }

    @Override
    protected int abilityInterval() {
        return phase >= 3 ? 60 : phase == 2 ? 75 : 95;
    }

    private boolean inWhite() {
        return this.whiteTicks > 0;
    }

    @Override
    protected void tickBoss(@Nullable LivingEntity target) {
        if (!(this.level() instanceof ServerLevel level)) {
            return;
        }
        if (this.strikeCooldown > 0) {
            this.strikeCooldown--;
        }
        if (this.tickCount % 10 == 0) {
            coldAura(level);
        }
        if (this.lanceTicks > 0) {
            tickLance(level);
        }
        if (this.staggerTicks > 0) {
            this.staggerTicks--;
            this.getNavigation().stop();
            level.sendParticles(ParticleTypes.CRIT, getX(), getY() + 4.0, getZ(), 6, 0.8, 1.5, 0.8, 0.1);
            return;
        }
        if (this.tellTicks > 0) {
            this.tellTicks--;
            this.getNavigation().stop();
            level.sendParticles(ParticleTypes.SNOWFLAKE, getX(), getY() + 5.0, getZ(), 30, 4.0, 2.0, 4.0, 0.05);
            if (this.tellTicks == 0) {
                beginWhite(level);
            }
            return;
        }
        if (inWhite()) {
            tickWhite(level);
            return;
        }
        if (target != null && --this.whiteTimer <= 0) {
            this.whiteTimer = phase >= 3 ? 340 : phase == 2 ? 420 : 500;
            this.tellTicks = 60;
            this.playSound(SoundEvents.WARDEN_SNIFF, 4.0f, 0.5f);
            for (ServerPlayer player : level.getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(48.0))) {
                Story.title(player, "THE WHITE", "Crouch, and be still", ChatFormatting.WHITE);
            }
        }
    }

    // ---- the cold

    private void coldAura(ServerLevel level) {
        double reach = phase >= 3 ? 9.0 : 7.0;
        int bite = phase >= 3 ? 40 : 34;          // vanilla thaws 2 a tick, so 34 every 10 ticks is a net gain of 14
        for (Player player : level.getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(48.0))) {
            if (player.isCreative() || player.isSpectator()) {
                continue;
            }
            if (nearFire(level, player.blockPosition())) {
                player.setTicksFrozen(Math.max(0, player.getTicksFrozen() - 40));
                continue;
            }
            if (player.distanceToSqr(this) < reach * reach && player.canFreeze()) {
                player.setTicksFrozen(Math.min(player.getTicksRequiredToFreeze() + 80, player.getTicksFrozen() + bite));
                level.sendParticles(ParticleTypes.SNOWFLAKE, player.getX(), player.getY() + 1.0, player.getZ(), 4, 0.4, 0.6, 0.4, 0.01);
            }
            if (player.isFullyFrozen() && this.tickCount % 20 == 0) {
                player.hurt(this.damageSources().freeze(), phase >= 3 ? 5.0f : 3.0f);
            }
        }
    }

    private static boolean nearFire(ServerLevel level, BlockPos at) {
        for (BlockPos p : BlockPos.betweenClosed(at.offset(-3, -1, -3), at.offset(3, 1, 3))) {
            BlockState s = level.getBlockState(p);
            if (s.is(BlockTags.CAMPFIRES) && s.getValue(CampfireBlock.LIT)) {
                return true;
            }
        }
        return false;
    }

    // ---- the White

    private void beginWhite(ServerLevel level) {
        this.whiteTicks = phase >= 3 ? 200 : 160;
        this.struck.clear();
        this.lastPos.clear();
        this.setInvisible(true);
        this.getNavigation().stop();
        this.playSound(SoundEvents.WARDEN_SONIC_CHARGE, 4.0f, 0.4f);
        for (Player player : level.getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(48.0))) {
            this.lastPos.put(player.getUUID(), player.position());
        }
    }

    private void tickWhite(ServerLevel level) {
        this.whiteTicks--;
        this.getNavigation().stop();
        level.sendParticles(ParticleTypes.SNOWFLAKE, getX(), getY() + 3.0, getZ(), 2, 0.6, 2.0, 0.6, 0.0);
        for (Player player : level.getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(48.0))) {
            if (player.isCreative() || player.isSpectator()) {
                continue;
            }
            if (this.tickCount % 20 == 0) {
                player.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 50, 0, false, false));
            }
            Vec3 now = player.position();
            Vec3 before = this.lastPos.getOrDefault(player.getUUID(), now);
            this.lastPos.put(player.getUUID(), now);
            double dx = now.x - before.x;
            double dz = now.z - before.z;
            boolean moved = dx * dx + dz * dz > 0.09 * 0.09 || now.y - before.y > 0.1;
            if (moved && !player.isCrouching()) {
                heard(level, player);
            }
        }
        if (this.whiteTicks == 0) {
            endWhite();
        }
    }

    private void heard(ServerLevel level, Player player) {
        if (this.struck.contains(player.getUUID()) || this.strikeCooldown > 0) {
            return;
        }
        this.struck.add(player.getUUID());
        this.strikeCooldown = 12;
        Vec3 look = player.getLookAngle().multiply(1.0, 0.0, 1.0);
        look = look.lengthSqr() < 0.01 ? new Vec3(0, 0, 1) : look.normalize();
        Vec3 behind = player.position().subtract(look.scale(2.5));
        if (!this.randomTeleport(behind.x, player.getY(), behind.z, true)) {
            this.randomTeleport(player.getX() + 2.0, player.getY(), player.getZ(), true);
        }
        player.hurt(this.damageSources().mobAttack(this), phase >= 3 ? 64.0f : phase == 2 ? 52.0f : 40.0f);
        if (player.canFreeze()) {
            player.setTicksFrozen(player.getTicksRequiredToFreeze() + 60);
        }
        player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 2));
        player.displayClientMessage(Component.literal("It heard you.").withStyle(ChatFormatting.WHITE), true);
        this.playSound(SoundEvents.GLASS_BREAK, 3.0f, 0.5f);
        level.sendParticles(ParticleTypes.SNOWFLAKE, player.getX(), player.getY() + 1.0, player.getZ(), 40, 0.6, 1.0, 0.6, 0.1);
    }

    private void endWhite() {
        this.whiteTicks = 0;
        this.setInvisible(false);
        this.playSound(SoundEvents.AMETHYST_BLOCK_CHIME, 3.0f, 0.4f);
    }

    /** A sneak attack during the White breaks its composure. */
    private void shatter(Player by) {
        endWhite();
        this.staggerTicks = 100;
        this.say("You struck it in perfect silence. The White Silence staggers, its mask cracking. Now!");
        this.playSound(SoundEvents.GLASS_BREAK, 4.0f, 0.3f);
        for (ServerPlayer player : this.level().getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(48.0))) {
            player.removeEffect(MobEffects.BLINDNESS);
            Story.title(player, "", "Its composure shatters", ChatFormatting.AQUA);
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (inWhite() && source.getEntity() instanceof Player player && !player.isCreative()) {
            if (player.isCrouching()) {
                shatter(player);
            } else if (this.level() instanceof ServerLevel level) {
                heard(level, player);
                return false;
            }
        }
        return super.hurt(source, amount);
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        if (inWhite() || this.tellTicks > 0 || this.staggerTicks > 0) {
            return false;
        }
        boolean hit = super.doHurtTarget(target);
        if (hit && target instanceof LivingEntity victim && victim.canFreeze()) {
            victim.setTicksFrozen(Math.min(victim.getTicksRequiredToFreeze() + 60, victim.getTicksFrozen() + 60));
        }
        return hit;
    }

    // ---- abilities

    @Override
    protected void castAbility(LivingEntity target) {
        if (inWhite() || this.tellTicks > 0 || this.staggerTicks > 0) {
            return;
        }
        this.casts++;
        if (phase >= 2 && this.casts % 3 == 0) {
            summonMirages(target);
        } else {
            beginLance(target);
        }
    }

    private void beginLance(LivingEntity target) {
        Vec3 d = target.position().subtract(this.position()).multiply(1.0, 0.0, 1.0);
        if (d.lengthSqr() < 0.01) {
            return;
        }
        this.lanceDir = d.normalize();
        this.lanceFrom = this.position();
        this.lanceTicks = 24;
        this.playSound(SoundEvents.POWDER_SNOW_BREAK, 3.0f, 0.5f);
    }

    private void tickLance(ServerLevel level) {
        this.lanceTicks--;
        double length = 20.0;
        if (this.lanceTicks % 4 == 0 && this.lanceTicks > 0) {
            for (double t = 1.0; t < length; t += 1.0) {
                Vec3 p = this.lanceFrom.add(this.lanceDir.scale(t));
                level.sendParticles(ParticleTypes.SNOWFLAKE, p.x, p.y + 0.2, p.z, 1, 0.1, 0.0, 0.1, 0.0);
            }
        }
        if (this.lanceTicks == 0) {
            float damage = phase >= 3 ? 40.0f : phase == 2 ? 32.0f : 26.0f;
            for (Player player : level.getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(length + 2.0))) {
                Vec3 rel = player.position().subtract(this.lanceFrom);
                double along = rel.x * this.lanceDir.x + rel.z * this.lanceDir.z;
                double off = Math.abs(rel.x * this.lanceDir.z - rel.z * this.lanceDir.x);
                if (along > 0.0 && along < length && off < 1.6 && Math.abs(rel.y) < 3.0) {
                    player.hurt(this.damageSources().mobAttack(this), damage);
                    player.push(0.0, 0.7, 0.0);
                    player.hurtMarked = true;
                    if (player.canFreeze()) {
                        player.setTicksFrozen(Math.min(player.getTicksRequiredToFreeze() + 60, player.getTicksFrozen() + 100));
                    }
                }
            }
            for (double t = 1.0; t < length; t += 0.7) {
                Vec3 p = this.lanceFrom.add(this.lanceDir.scale(t));
                level.sendParticles(ParticleTypes.ITEM_SNOWBALL, p.x, p.y + 0.5, p.z, 3, 0.2, 0.6, 0.2, 0.05);
            }
            this.playSound(SoundEvents.GLASS_BREAK, 3.0f, 0.7f);
        }
    }

    private void summonMirages(LivingEntity target) {
        int existing = this.level().getEntitiesOfClass(PaleMirage.class, this.getBoundingBox().inflate(40.0)).size();
        int count = phase >= 3 ? 3 : 2;
        for (int i = 0; i < count && existing + i < 4; i++) {
            PaleMirage mirage = ModEntities.PALE_MIRAGE.get().create(this.level());
            if (mirage == null) {
                continue;
            }
            double a = this.random.nextDouble() * Math.PI * 2.0;
            mirage.moveTo(getX() + Math.cos(a) * 5.0, getY(), getZ() + Math.sin(a) * 5.0, this.getYRot(), 0.0f);
            mirage.setTarget(target);
            this.level().addFreshEntity(mirage);
        }
        this.say("The White Silence comes apart into reflections. Only one of them is real.");
        this.playSound(SoundEvents.ILLUSIONER_MIRROR_MOVE, 3.0f, 0.6f);
    }

    @Override
    protected float incomingMultiplier() {
        return this.staggerTicks > 0 ? 1.0f : 0.6f;
    }

    @Override
    protected float capMultiplier() {
        return this.staggerTicks > 0 ? 2.5f : 1.0f;
    }

    @Override
    public void die(DamageSource source) {
        this.setInvisible(false);
        for (PaleMirage mirage : this.level().getEntitiesOfClass(PaleMirage.class, this.getBoundingBox().inflate(48.0))) {
            mirage.discard();
        }
        super.die(source);
    }
}
