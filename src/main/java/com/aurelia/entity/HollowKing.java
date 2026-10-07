package com.aurelia.entity;

import com.aurelia.registry.ModEntities;
import com.aurelia.registry.ModItems;
import com.aurelia.world.Realm;
import com.aurelia.world.Story;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

/**
 * The Hollow King (the Sovereign, hollowed out) (4000 HP). Cycles three abilities:
 *  Void Step (teleports behind you and strikes), Dark Pulse (darkness + wither + armour-piercing damage),
 *  Shade Call (summons Shades).
 * Phase 2 (66%): faster casting, and every cast also crumbles columns out of the arena floor.
 * Phase 3 (33%): casts two abilities back to back, more Shades, and the floor falls away faster.
 */
public class HollowKing extends AureliaBoss {
    private int casts = 0;
    /** Gimmick: Annihilation. He channels for five seconds; deal 6% of his health in that window to break his guard. */
    private int channelTimer = 500;
    private int channelTicks = 0;
    private float channelDamage = 0.0f;
    private int staggerTicks = 0;

    public HollowKing(EntityType<? extends HollowKing> type, Level level) {
        super(type, level, BossEvent.BossBarColor.PURPLE);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return baseAttributes(4000.0, 28.0, 0.3);
    }

    @Override
    protected Item shardItem() {
        return ModItems.VOID_SHARD.get();
    }

    @Override
    protected String phaseLine() {
        return Story.KING_PHASE;
    }

    @Override
    protected String finalPhaseLine() {
        return Story.KING_FINAL;
    }

    @Override
    protected String deathLine() {
        return Story.KING_DEATH;
    }

    @Override
    public String awakenLine() {
        return "Something very old looks up.";
    }

    @Override
    protected int abilityInterval() {
        return phase >= 3 ? 55 : phase == 2 ? 70 : 100;
    }

    @Override
    protected void tickBoss(@Nullable LivingEntity target) {
        if (this.staggerTicks > 0) {
            this.staggerTicks--;
            this.getNavigation().stop();
            if (this.level() instanceof ServerLevel serverLevel) {
                serverLevel.sendParticles(ParticleTypes.CRIT, getX(), getY() + 3.0, getZ(), 6, 0.8, 1.5, 0.8, 0.1);
            }
            return;
        }
        if (this.channelTicks > 0) {
            this.channelTicks--;
            this.getNavigation().stop();
            if (this.level() instanceof ServerLevel serverLevel) {
                serverLevel.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, getX(), getY() + 3.0, getZ(), 14, 2.5, 2.5, 2.5, 0.02);
            }
            if (this.channelDamage >= this.getMaxHealth() * 0.06f) {
                this.channelTicks = 0;
                this.staggerTicks = 100;
                this.say("His guard breaks. The Hollow King staggers, wide open.");
                this.playSound(SoundEvents.ANVIL_LAND, 2.0f, 0.5f);
            } else if (this.channelTicks == 0) {
                annihilate();
            }
            return;
        }
        if (target != null && --this.channelTimer <= 0) {
            this.channelTimer = phase >= 3 ? 420 : 560;
            this.channelTicks = 100;
            this.channelDamage = 0.0f;
            this.say("The Hollow King raises his sword. ANNIHILATION is coming. Break his guard!");
            this.playSound(SoundEvents.WARDEN_ROAR, 3.0f, 0.6f);
            for (ServerPlayer player : this.level().getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(40.0))) {
                Story.title(player, "ANNIHILATION", "Break his guard before the dark falls", ChatFormatting.DARK_PURPLE);
            }
        }
    }

    private void annihilate() {
        for (Player player : this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(28.0))) {
            player.hurt(this.damageSources().magic(), player.getMaxHealth() * 0.6f);
            player.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 100, 0));
            player.push(0.0, 0.8, 0.0);
            player.hurtMarked = true;
        }
        this.say("The dark falls.");
        this.playSound(SoundEvents.GENERIC_EXPLODE, 4.0f, 0.4f);
        if (this.level() instanceof ServerLevel serverLevel) {
            serverLevel.sendParticles(ParticleTypes.EXPLOSION_EMITTER, getX(), getY() + 2.0, getZ(), 6, 6.0, 2.0, 6.0, 0.0);
        }
    }

    @Override
    protected float capMultiplier() {
        return this.staggerTicks > 0 ? 2.0f : 1.0f;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        float before = this.getHealth();
        boolean hit = super.hurt(source, amount);
        if (hit && this.channelTicks > 0) {
            this.channelDamage += Math.max(0.0f, before - this.getHealth());
        }
        return hit;
    }

    @Override
    protected void castAbility(LivingEntity target) {
        if (this.channelTicks > 0 || this.staggerTicks > 0) {
            return;
        }
        runCast(target, this.casts++ % 3);
        if (phase >= 3) {
            runCast(target, this.casts++ % 3);
        }
        if (phase >= 2) {
            collapse(phase >= 3 ? 8 : 5);
        }
    }

    private void runCast(LivingEntity target, int which) {
        switch (which) {
            case 0 -> voidStep(target);
            case 1 -> darkPulse();
            default -> summonShades(target);
        }
    }

    private void voidStep(LivingEntity target) {
        Vec3 look = target.getLookAngle().multiply(1.0, 0.0, 1.0).normalize();
        Vec3 behind = target.position().subtract(look.scale(3.0));
        if (!this.randomTeleport(behind.x, target.getY(), behind.z, true)) {
            this.randomTeleport(target.getX() + 3.0, target.getY(), target.getZ(), true);
        }
        this.playSound(SoundEvents.ENDERMAN_TELEPORT, 2.0f, 0.6f);
        // The ambush: a heavy strike if he lands close enough.
        if (this.distanceToSqr(target) < 25.0) {
            target.hurt(this.damageSources().mobAttack(this), phase >= 3 ? 56.0f : phase == 2 ? 44.0f : 32.0f);
        }
    }

    private void darkPulse() {
        float pierce = phase >= 3 ? 20.0f : phase == 2 ? 16.0f : 14.0f;
        for (Player player : this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(16.0))) {
            player.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 160, 0));
            player.addEffect(new MobEffectInstance(MobEffects.WITHER, 100, 2));
            player.hurt(this.damageSources().magic(), pierce);
        }
        this.playSound(SoundEvents.WARDEN_SONIC_BOOM, 2.0f, 0.5f);
        if (this.level() instanceof ServerLevel serverLevel) {
            serverLevel.sendParticles(ParticleTypes.SOUL, getX(), getY() + 2.0, getZ(), 80, 5.0, 1.5, 5.0, 0.05);
        }
    }

    private void summonShades(LivingEntity target) {
        int existing = this.level().getEntitiesOfClass(HollowShade.class, this.getBoundingBox().inflate(24.0)).size();
        int count = phase >= 3 ? 4 : phase == 2 ? 3 : 2;
        for (int i = 0; i < count && existing + i < 8; i++) {
            HollowShade shade = ModEntities.HOLLOW_SHADE.get().create(this.level());
            if (shade == null) {
                continue;
            }
            shade.moveTo(getX() + (random.nextDouble() - 0.5) * 6.0, getY(), getZ() + (random.nextDouble() - 0.5) * 6.0,
                    random.nextFloat() * 360.0f, 0.0f);
            shade.setTarget(target);
            this.level().addFreshEntity(shade);
        }
    }

    /** Tears random columns out of the arena floor. Leaves the altar and the return Waygate alone. */
    private void collapse(int columns) {
        if (this.arena == null || !(this.level() instanceof ServerLevel serverLevel)) {
            return;
        }
        for (int i = 0; i < columns; i++) {
            int dx = random.nextInt(25) - 12;
            int dz = random.nextInt(25) - 12;
            if (dx * dx + dz * dz > 144) {
                continue;
            }
            if (Math.abs(dx) <= 1 && Math.abs(dz) <= 1) {
                continue; // keep the altar's footing
            }
            if (dz >= 7) {
                continue; // keep the Waygate's footing
            }
            BlockPos top = this.arena.offset(dx, -1, dz);
            if (!serverLevel.getBlockState(top).is(Realm.HOLLOW.pad)) {
                continue;
            }
            for (int dy = 0; dy <= 5; dy++) {
                serverLevel.setBlock(top.below(dy), Blocks.AIR.defaultBlockState(), 3);
            }
            serverLevel.sendParticles(ParticleTypes.LARGE_SMOKE, top.getX() + 0.5, top.getY() + 1.0, top.getZ() + 0.5,
                    12, 0.4, 0.2, 0.4, 0.02);
        }
        this.playSound(SoundEvents.GENERIC_EXPLODE, 1.5f, 0.5f);
    }
}
