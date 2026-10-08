package com.aurelia.entity;

import com.aurelia.registry.ModEntities;
import com.aurelia.registry.ModItems;
import com.aurelia.world.ArenaBuilder;
import com.aurelia.world.Story;
import java.util.ArrayList;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
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
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

/**
 * Kharzul, the Glass Reaper, Warden of the Scarlet Sands (6000 HP). His glass body turns half of every blow aside
 * and throws arrows and other projectiles straight back at whoever fired them.
 *  REAPING ARC: a red ring marks a band around him; after a breath, his scythe sweeps it. Hug him or get clear.
 *  THE LAST GRAIN: he raises his hourglass for five seconds, then its light burns everyone it can see for 60% of their
 *  health. Keep stone between you and him: the light shatters the block that stops it, so cover runs out. Afterwards his
 *  glass is OVERHEATED for six seconds: full damage, caps raised 2.5x. The arena's four pillars are rebuilt each fight.
 * Phase 2 (66%): GLASS RAIN (marked circles where shards fall) and Glasswing Scarabs.
 * Phase 3 (33%): a second, wider arc follows each sweep, and the last grain falls sooner.
 */
public class Kharzul extends AureliaBoss {
    private static final DustParticleOptions RED = new DustParticleOptions(new Vector3f(1.0f, 0.12f, 0.08f), 1.6f);
    private int grainTimer = 640;
    private int channelTicks = 0;
    private int overheatTicks = 0;
    private int reapTicks = 0;
    private int reapBand = 0;
    private int casts = 0;
    private boolean warnedReflect = false;
    private final List<Vec3> rainAt = new ArrayList<>();
    private final List<Integer> rainTicks = new ArrayList<>();

    public Kharzul(EntityType<? extends Kharzul> type, Level level) {
        super(type, level, BossEvent.BossBarColor.RED);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return baseAttributes(6000.0, 24.0, 0.3);
    }

    @Override
    protected Item shardItem() {
        return ModItems.REAPERS_HOURGLASS.get();
    }

    @Override
    protected String phaseLine() {
        return Story.KHARZUL_PHASE;
    }

    @Override
    protected String finalPhaseLine() {
        return Story.KHARZUL_FINAL;
    }

    @Override
    protected String deathLine() {
        return Story.KHARZUL_DEATH;
    }

    @Override
    public String awakenLine() {
        return "Your time is already his.";
    }

    @Override
    protected int abilityInterval() {
        return phase >= 3 ? 65 : phase == 2 ? 80 : 100;
    }

    @Override
    public void setArena(BlockPos pos) {
        super.setArena(pos);
        if (this.level() instanceof ServerLevel level) {
            ArenaBuilder.raiseScarletPillars(level, pos);
        }
    }

    @Override
    protected void tickBoss(@Nullable LivingEntity target) {
        if (!(this.level() instanceof ServerLevel level)) {
            return;
        }
        tickRain(level);
        if (this.overheatTicks > 0) {
            this.overheatTicks--;
            this.getNavigation().stop();
            com.aurelia.Perf.particles(level, ParticleTypes.LAVA, getX(), getY() + 3.5, getZ(), 2, 0.8, 1.2, 0.8, 0.0);
            com.aurelia.Perf.particles(level, ParticleTypes.CRIT, getX(), getY() + 3.5, getZ(), 5, 0.8, 1.5, 0.8, 0.1);
            return;
        }
        if (this.channelTicks > 0) {
            this.channelTicks--;
            this.getNavigation().stop();
            com.aurelia.Perf.particles(level, new BlockParticleOption(ParticleTypes.FALLING_DUST, Blocks.RED_SAND.defaultBlockState()),
                    getX(), getY() + 6.0, getZ(), 12, 1.0, 0.4, 1.0, 0.0);
            com.aurelia.Perf.particles(level, ParticleTypes.END_ROD, getX(), getY() + 4.2, getZ(), 4, 0.3, 0.3, 0.3, 0.05);
            if (this.channelTicks % 20 == 0) {
                this.playSound(SoundEvents.BEACON_AMBIENT, 4.0f, 0.5f + (100 - this.channelTicks) * 0.01f);
            }
            if (this.channelTicks == 0) {
                lastGrain(level);
            }
            return;
        }
        if (this.reapTicks > 0) {
            tickReap(level);
        }
        if (target != null && --this.grainTimer <= 0) {
            this.grainTimer = phase >= 3 ? 520 : phase == 2 ? 600 : 700;
            this.channelTicks = 100;
            this.reapTicks = 0;
            this.say("Kharzul turns his hourglass. When the last grain falls, his light will find anything it can see.");
            for (ServerPlayer player : level.getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(48.0))) {
                Story.title(player, "THE LAST GRAIN", "Hide from his light", ChatFormatting.RED);
            }
            this.playSound(SoundEvents.WARDEN_ROAR, 3.0f, 1.3f);
        }
    }

    // ---- the reaping arc

    @Override
    protected void castAbility(LivingEntity target) {
        if (this.channelTicks > 0 || this.overheatTicks > 0 || this.reapTicks > 0) {
            return;
        }
        this.casts++;
        if (phase >= 2 && this.casts % 2 == 0) {
            glassRain();
        }
        if (phase >= 2 && this.casts % 3 == 0) {
            summonScarabs(target);
        }
        this.reapTicks = 30;
        this.reapBand = 0;
        this.playSound(SoundEvents.TRIDENT_RETURN, 3.0f, 0.5f);
    }

    private void tickReap(ServerLevel level) {
        double inner = this.reapBand == 0 ? 2.5 : 7.5;
        double outer = this.reapBand == 0 ? 7.5 : 12.0;
        if (this.reapTicks % 3 == 0) {
            double mid = (inner + outer) / 2.0;
            for (int i = 0; i < 40; i++) {
                double a = i * Math.PI / 20.0;
                com.aurelia.Perf.particles(level, RED, getX() + Math.cos(a) * mid, getY() + 0.3, getZ() + Math.sin(a) * mid, 1, 0.3, 0.0, 0.3, 0.0);
                com.aurelia.Perf.particles(level, RED, getX() + Math.cos(a) * inner, getY() + 0.3, getZ() + Math.sin(a) * inner, 1, 0.0, 0.0, 0.0, 0.0);
                com.aurelia.Perf.particles(level, RED, getX() + Math.cos(a) * outer, getY() + 0.3, getZ() + Math.sin(a) * outer, 1, 0.0, 0.0, 0.0, 0.0);
            }
        }
        if (--this.reapTicks > 0) {
            return;
        }
        float damage = phase >= 3 ? 66.0f : phase == 2 ? 54.0f : 44.0f;
        for (LivingEntity victim : level.getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(outer + 1.0, 3.0, outer + 1.0),
                e -> e != this && !(e instanceof AureliaBoss) && !(e instanceof GlasswingScarab))) {
            double dx = victim.getX() - getX();
            double dz = victim.getZ() - getZ();
            double d = Math.sqrt(dx * dx + dz * dz);
            if (d >= inner && d <= outer) {
                victim.hurt(this.damageSources().mobAttack(this), damage);
                victim.addEffect(new MobEffectInstance(MobEffects.WITHER, 60, 1));
            }
        }
        this.playSound(SoundEvents.PLAYER_ATTACK_SWEEP, 4.0f, 0.5f);
        com.aurelia.Perf.particles(level, ParticleTypes.SWEEP_ATTACK, getX(), getY() + 1.0, getZ(), 12, outer / 2.0, 0.2, outer / 2.0, 0.0);
        if (phase >= 3 && this.reapBand == 0) {
            this.reapBand = 1;
            this.reapTicks = 14;
        }
    }

    // ---- the last grain

    private void lastGrain(ServerLevel level) {
        Vec3 from = this.position().add(0.0, 4.2, 0.0);
        int burned = 0;
        for (Player player : level.getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(48.0))) {
            if (player.isCreative() || player.isSpectator()) {
                continue;
            }
            BlockHitResult toEyes = clip(level, from, player.getEyePosition());
            BlockHitResult toChest = clip(level, from, player.position().add(0.0, 0.9, 0.0));
            boolean seen = toEyes.getType() == HitResult.Type.MISS || toChest.getType() == HitResult.Type.MISS;
            if (seen) {
                burned++;
                beam(level, from, player.getEyePosition());
                player.hurt(this.damageSources().magic(), player.getMaxHealth() * 0.6f);
                player.setSecondsOnFire(5);
                player.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 40, 0));
            } else {
                beam(level, from, toEyes.getLocation());
                shatterCover(level, toEyes.getBlockPos());
                if (toChest.getType() == HitResult.Type.BLOCK) {
                    shatterCover(level, toChest.getBlockPos());
                }
                player.displayClientMessage(Component.literal("The light melts the stone in front of you.").withStyle(ChatFormatting.GOLD), true);
            }
        }
        this.playSound(SoundEvents.BEACON_DEACTIVATE, 5.0f, 0.6f);
        this.playSound(SoundEvents.GENERIC_EXPLODE, 2.0f, 1.4f);
        this.overheatTicks = 120;
        this.say(burned > 0 ? "The light passes. Kharzul's glass glows white-hot and brittle. Break it!"
                : "Nothing for the light to take. Kharzul's glass glows white-hot and brittle. Break it!");
    }

    private BlockHitResult clip(ServerLevel level, Vec3 from, Vec3 to) {
        return level.clip(new ClipContext(from, to, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this));
    }

    private static void beam(ServerLevel level, Vec3 from, Vec3 to) {
        Vec3 d = to.subtract(from);
        double len = d.length();
        for (double t = 0.0; t < len; t += 0.5) {
            Vec3 p = from.add(d.scale(t / len));
            com.aurelia.Perf.particles(level, ParticleTypes.END_ROD, p.x, p.y, p.z, 1, 0.02, 0.02, 0.02, 0.0);
        }
    }

    /** The block that stopped the light melts away (never anything unbreakable, like the altar or the waygate). */
    private static void shatterCover(ServerLevel level, BlockPos pos) {
        BlockState s = level.getBlockState(pos);
        if (s.isAir() || s.getDestroySpeed(level, pos) < 0.0f || s.hasBlockEntity()) {
            return;
        }
        level.destroyBlock(pos, false);
        com.aurelia.Perf.particles(level, ParticleTypes.LAVA, pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 6, 0.3, 0.3, 0.3, 0.0);
    }

    // ---- phase two and three

    private void glassRain() {
        for (Player player : this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(32.0))) {
            if (player.isCreative() || player.isSpectator()) {
                continue;
            }
            this.rainAt.add(player.position());
            this.rainTicks.add(26);
        }
        this.playSound(SoundEvents.AMETHYST_CLUSTER_BREAK, 3.0f, 0.5f);
    }

    private void tickRain(ServerLevel level) {
        for (int i = this.rainAt.size() - 1; i >= 0; i--) {
            Vec3 at = this.rainAt.get(i);
            int t = this.rainTicks.get(i) - 1;
            if (t % 4 == 0) {
                for (int k = 0; k < 16; k++) {
                    double a = k * Math.PI / 8.0;
                    com.aurelia.Perf.particles(level, RED, at.x + Math.cos(a) * 2.5, at.y + 0.2, at.z + Math.sin(a) * 2.5, 1, 0.0, 0.0, 0.0, 0.0);
                }
            }
            if (t <= 0) {
                for (LivingEntity victim : level.getEntitiesOfClass(LivingEntity.class, new net.minecraft.world.phys.AABB(at, at).inflate(2.5, 3.0, 2.5),
                        e -> e != this && !(e instanceof AureliaBoss) && !(e instanceof GlasswingScarab))) {
                    victim.hurt(this.damageSources().magic(), phase >= 3 ? 26.0f : 20.0f);
                    victim.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 1));
                }
                com.aurelia.Perf.particles(level, ParticleTypes.CRIT, at.x, at.y + 3.0, at.z, 40, 1.5, 2.0, 1.5, 0.2);
                level.playSound(null, BlockPos.containing(at), SoundEvents.GLASS_BREAK, net.minecraft.sounds.SoundSource.HOSTILE, 2.0f, 0.8f);
                this.rainAt.remove(i);
                this.rainTicks.remove(i);
            } else {
                this.rainTicks.set(i, t);
            }
        }
    }

    private void summonScarabs(LivingEntity target) {
        int existing = this.level().getEntitiesOfClass(GlasswingScarab.class, this.getBoundingBox().inflate(32.0)).size();
        for (int i = 0; i < 2 && existing + i < 6; i++) {
            GlasswingScarab scarab = ModEntities.GLASSWING_SCARAB.get().create(this.level());
            if (scarab == null) {
                continue;
            }
            scarab.moveTo(getX() + (random.nextDouble() - 0.5) * 6.0, getY(), getZ() + (random.nextDouble() - 0.5) * 6.0,
                    random.nextFloat() * 360.0f, 0.0f);
            scarab.setTarget(target);
            this.level().addFreshEntity(scarab);
        }
    }

    // ---- glass

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.getDirectEntity() instanceof Projectile && source.getEntity() instanceof LivingEntity shooter && shooter != this) {
            shooter.hurt(this.damageSources().thorns(this), 6.0f);
            this.playSound(SoundEvents.GLASS_BREAK, 1.0f, 1.6f);
            if (!this.warnedReflect && shooter instanceof Player player) {
                this.warnedReflect = true;
                player.displayClientMessage(Component.literal("It shatters against his glass and the shards fly back at you.")
                        .withStyle(ChatFormatting.RED), false);
            }
            return false;
        }
        return super.hurt(source, amount);
    }

    @Override
    protected float incomingMultiplier() {
        return this.overheatTicks > 0 ? 1.0f : 0.5f;
    }

    @Override
    protected float capMultiplier() {
        return this.overheatTicks > 0 ? 2.5f : 1.0f;
    }
}
