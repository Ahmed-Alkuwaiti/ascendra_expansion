package com.aurelia.entity;

import com.aurelia.world.Story;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * Common behaviour for the three Wardens:
 *  - server boss bar
 *  - hard cap on damage per hit (5% of max health) so overpowered modded weapons can't one-shot them
 *  - a phase change at 50% health with a short invulnerable "roar"
 *  - a periodic special ability
 *  - a shard drop plus a story line on death
 */
public abstract class AureliaBoss extends Monster {
    private final ServerBossEvent bossEvent;
    protected int phase = 1;
    protected int shieldTicks = 0;
    protected int abilityCooldown = 100;
    @Nullable
    protected BlockPos arena;
    /** The signature move in flight (see BossSignatures). */
    public final BossSignatures.State signature = new BossSignatures.State();

    // ---- Damage limits (tune these for your strongest weapons) ----
    /** Max fraction of max health a single hit can remove. */
    protected static final float HIT_CAP = 0.02f;
    /** Max fraction of max health that can be removed per second, however many hits land. */
    protected static final float SECOND_CAP = 0.04f;
    private float windowDamage = 0.0f;
    private int windowTicks = 0;

    protected AureliaBoss(EntityType<? extends AureliaBoss> type, Level level, BossEvent.BossBarColor color) {
        super(type, level);
        this.bossEvent = new ServerBossEvent(this.getDisplayName(), color, BossEvent.BossBarOverlay.NOTCHED_10);
        this.bossEvent.setDarkenScreen(true);
        this.bossEvent.setCreateWorldFog(true);
        this.xpReward = 500;
        this.setPersistenceRequired();
    }

    protected static AttributeSupplier.Builder baseAttributes(double health, double damage, double speed) {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, health)
                .add(Attributes.ATTACK_DAMAGE, damage)
                .add(Attributes.MOVEMENT_SPEED, speed)
                .add(Attributes.FOLLOW_RANGE, 64.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
                .add(Attributes.ARMOR, 10.0);
    }

    // ---- Hooks for subclasses ----

    protected abstract Item shardItem();

    protected abstract String phaseLine();

    protected abstract String finalPhaseLine();

    protected abstract String deathLine();

    public abstract String awakenLine();

    protected abstract int abilityInterval();

    /** Fired on the periodic ability timer while a target exists. */
    protected void castAbility(LivingEntity target) {}

    /** Fired every server tick (target may be null). */
    protected void tickBoss(@Nullable LivingEntity target) {}

    protected void onPhaseTwo() {}

    protected void onPhaseThree() {}

    /** A roar at each phase change: darkness, and a shockwave that throws nearby players back. */
    protected void dreadPulse() {
        this.playSound(SoundEvents.WARDEN_ROAR, 4.0f, 0.7f);
        for (net.minecraft.world.entity.player.Player player : this.level().getEntitiesOfClass(
                net.minecraft.world.entity.player.Player.class, this.getBoundingBox().inflate(32.0))) {
            player.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.DARKNESS, 100, 0));
            net.minecraft.world.phys.Vec3 away = player.position().subtract(this.position()).multiply(1.0, 0.0, 1.0).normalize();
            player.push(away.x * 1.3, 0.45, away.z * 1.3);
            player.hurtMarked = true;
        }
    }

    /** Scales incoming damage before the caps. Used by gimmicks (a shielded or exposed boss). */
    protected float incomingMultiplier() {
        return 1.0f;
    }

    /** Scales the per-hit and per-second damage caps. Above 1 while a boss is stunned or staggered. */
    protected float capMultiplier() {
        return 1.0f;
    }

    /** How far above the altar the boss should appear. */
    public double spawnHeightOffset() {
        return 0.0;
    }

    /** Where the boss appears when woken at the given altar. Bosses that live in water or air override this. */
    public net.minecraft.world.phys.Vec3 spawnPosition(BlockPos altar) {
        return new net.minecraft.world.phys.Vec3(altar.getX() + 0.5, altar.getY() + 1 + spawnHeightOffset(), altar.getZ() - 4.5);
    }

    public void setArena(BlockPos pos) {
        this.arena = pos;
    }

    // ---- Behaviour ----

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(1, new FloatGoal(this));
        this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.0, true));
        this.goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.8));
        this.goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 16.0f));
        this.goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        this.bossEvent.setProgress(this.getHealth() / this.getMaxHealth());
        if (this.getTarget() != null && this.tickCount % (phase >= 3 ? 20 : 40) == 0) {
            this.playSound(SoundEvents.WARDEN_HEARTBEAT, 3.0f, phase >= 3 ? 1.1f : 0.8f);
        }

        if (this.shieldTicks > 0) {
            this.shieldTicks--;
            if (this.level() instanceof ServerLevel serverLevel) {
                com.aurelia.Perf.particles(serverLevel, ParticleTypes.END_ROD, getX(), getY() + getBbHeight() / 2.0, getZ(),
                        4, getBbWidth() / 2.0, getBbHeight() / 3.0, getBbWidth() / 2.0, 0.02);
            }
        }

        if (++this.windowTicks >= 20) {
            this.windowTicks = 0;
            this.windowDamage = 0.0f;
        }

        if (this.phase == 1 && this.getHealth() <= this.getMaxHealth() * 0.66f) {
            this.phase = 2;
            this.shieldTicks = 60;
            this.onPhaseTwo();
            this.dreadPulse();
            this.say(phaseLine());
            this.playSound(SoundEvents.WITHER_SPAWN, 2.0f, 0.7f);
        } else if (this.phase == 2 && this.getHealth() <= this.getMaxHealth() * 0.33f) {
            this.phase = 3;
            this.shieldTicks = 80;
            this.onPhaseThree();
            this.dreadPulse();
            this.say(finalPhaseLine());
            this.playSound(SoundEvents.WITHER_SPAWN, 2.0f, 0.5f);
        }

        LivingEntity target = this.getTarget();
        if (target != null && !target.isAlive()) {
            target = null;
        }
        if (target != null && this.shieldTicks <= 0 && --this.abilityCooldown <= 0) {
            this.abilityCooldown = abilityInterval();
            this.castAbility(target);
        }
        this.tickBoss(target);
        BossSignatures.tick(this, target);
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean bypass = source.is(DamageTypeTags.BYPASSES_INVULNERABILITY);
        if (!bypass) {
            if (this.shieldTicks > 0) {
                return false;
            }
            amount *= incomingMultiplier();
            float cap = capMultiplier();
            amount = Math.min(amount, this.getMaxHealth() * HIT_CAP * cap);
            float room = this.getMaxHealth() * SECOND_CAP * cap - this.windowDamage;
            if (room <= 0.0f) {
                // This second's damage budget is spent: the blow glances off.
                this.playSound(SoundEvents.SHIELD_BLOCK, 1.0f, 0.8f);
                return false;
            }
            amount = Math.min(amount, room);
        }
        boolean hit = super.hurt(source, amount);
        if (hit && !bypass) {
            this.windowDamage += amount;
        }
        return hit;
    }

    @Override
    protected void dropCustomDeathLoot(DamageSource source, int looting, boolean recentlyHit) {
        super.dropCustomDeathLoot(source, looting, recentlyHit);
        net.minecraft.world.phys.Vec3 at = lootPosition();
        net.minecraft.world.entity.item.ItemEntity drop = new net.minecraft.world.entity.item.ItemEntity(this.level(), at.x, at.y, at.z,
                new ItemStack(shardItem()));
        drop.setDefaultPickUpDelay();
        drop.setGlowingTag(true);
        this.level().addFreshEntity(drop);
        Item relic = com.aurelia.registry.ModItems.relicOf(this);
        if (relic != null) {                     // each Warden also leaves a relic for the Convergence Gate
            net.minecraft.world.entity.item.ItemEntity r = new net.minecraft.world.entity.item.ItemEntity(this.level(), at.x, at.y + 0.5, at.z,
                    new ItemStack(relic));
            r.setDefaultPickUpDelay();
            r.setGlowingTag(true);
            this.level().addFreshEntity(r);
        }
    }

    /** Where the Warden's relic lands. Vorath dies at sea, so he leaves his on the arena stone instead. */
    protected net.minecraft.world.phys.Vec3 lootPosition() {
        return this.position().add(0.0, 0.5, 0.0);
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        if (!this.level().isClientSide) {
            this.say(deathLine());
        }
    }

    /** Sends a story line to every player near the boss. */
    protected void say(String text) {
        for (Player player : this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(80.0))) {
            Story.narrate(player, text);
        }
    }

    // ---- Boss bar plumbing ----

    @Override
    public void startSeenByPlayer(ServerPlayer player) {
        super.startSeenByPlayer(player);
        this.bossEvent.addPlayer(player);
    }

    @Override
    public void stopSeenByPlayer(ServerPlayer player) {
        super.stopSeenByPlayer(player);
        this.bossEvent.removePlayer(player);
    }

    @Override
    public void setCustomName(@Nullable Component name) {
        super.setCustomName(name);
        this.bossEvent.setName(this.getDisplayName());
    }

    @Override
    public void remove(Entity.RemovalReason reason) {
        super.remove(reason);
        this.bossEvent.removeAllPlayers();
    }

    @Override
    protected boolean shouldDespawnInPeaceful() {
        return false;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("Phase", this.phase);
        if (this.arena != null) {
            tag.putLong("Arena", this.arena.asLong());
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        this.phase = Math.max(1, tag.getInt("Phase"));
        if (tag.contains("Arena")) {
            this.arena = BlockPos.of(tag.getLong("Arena"));
        }
        if (this.hasCustomName()) {
            this.bossEvent.setName(this.getDisplayName());
        }
    }
}
