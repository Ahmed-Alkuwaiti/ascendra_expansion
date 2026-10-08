package com.aurelia.entity;

import com.aurelia.block.SporeValveBlock;
import com.aurelia.registry.ModEntities;
import com.aurelia.registry.ModItems;
import com.aurelia.world.ArenaBuilder;
import com.aurelia.world.Story;
import java.util.ArrayList;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * The Bloom Mother, Warden of the Mycelial Deep (6500 HP). Rooted to the arena; she never moves. Her petals close over
 * her heart, so she takes 30% damage.
 *  ROOT LASH: roots churn under up to three players, then burst up through the floor and throw them.
 *  SPORE MORTAR: she spits spore pods that burst into clouds of poison where they land.
 *  DEVOUR: anyone close in front of her when the petals snap shut is chewed.
 *  THE INHALE: every half minute she draws breath for six seconds, dragging everyone toward her maw. Wrench open the arena's
 *  spore valves while she does: with two or more open at the end, she CHOKES and her petals are blown wide for seven
 *  seconds (full damage, caps 2.5x). Fewer, and she EXHALES: poison, nausea and 20% of everyone's health, and she heals.
 *  Between inhales her roots creep over the valves and seal them again.
 * Phase 2 (66%): Root Grubs crawl out of the floor. Phase 3 (33%): Spore Drifters, and she inhales more often.
 */
public class BloomMother extends AureliaBoss {
    private int inhaleTimer = 500;
    private int inhaleTicks = 0;
    private int openTicks = 0;
    private int sealTimer = 200;
    private int devourTicks = 0;
    private int casts = 0;
    private final List<Vec3> lashAt = new ArrayList<>();
    private final List<Integer> lashTicks = new ArrayList<>();

    public BloomMother(EntityType<? extends BloomMother> type, Level level) {
        super(type, level, BossEvent.BossBarColor.PINK);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return baseAttributes(6500.0, 28.0, 0.0);
    }

    @Override
    protected Item shardItem() {
        return ModItems.BLOOM_HEART.get();
    }

    @Override
    protected String phaseLine() {
        return Story.BLOOM_PHASE;
    }

    @Override
    protected String finalPhaseLine() {
        return Story.BLOOM_FINAL;
    }

    @Override
    protected String deathLine() {
        return Story.BLOOM_DEATH;
    }

    @Override
    public String awakenLine() {
        return "Something under the floor turns toward you.";
    }

    @Override
    public Vec3 spawnPosition(BlockPos altar) {
        return new Vec3(altar.getX() + 0.5, altar.getY(), altar.getZ() - 5.5);
    }

    @Override
    protected int abilityInterval() {
        return phase >= 3 ? 55 : phase == 2 ? 70 : 90;
    }

    /** She is rooted: no walking, only targeting. */
    @Override
    protected void registerGoals() {
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    public void knockback(double strength, double x, double z) {
    }

    private List<BlockPos> valves() {
        List<BlockPos> out = new ArrayList<>();
        if (this.arena != null) {
            for (int[] v : ArenaBuilder.VALVES) {
                BlockPos p = this.arena.offset(v[0], 0, v[1]);
                if (this.level().getBlockState(p).getBlock() instanceof SporeValveBlock) {
                    out.add(p);
                }
            }
        }
        return out;
    }

    @Override
    protected void tickBoss(@Nullable LivingEntity target) {
        if (!(this.level() instanceof ServerLevel level)) {
            return;
        }
        this.setDeltaMovement(0.0, this.getDeltaMovement().y, 0.0);
        if (target != null) {
            double dx = target.getX() - getX();
            double dz = target.getZ() - getZ();
            float yaw = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0f;
            this.setYRot(Mth.rotLerp(0.06f, this.getYRot(), yaw));
            this.yBodyRot = this.getYRot();
        }
        tickLashes(level);
        if (this.devourTicks > 0 && --this.devourTicks == 0) {
            devour(level);
        }
        if (this.openTicks > 0) {
            this.openTicks--;
            com.aurelia.Perf.particles(level, ParticleTypes.SPORE_BLOSSOM_AIR, getX(), getY() + 5.0, getZ(), 6, 2.0, 1.0, 2.0, 0.02);
            com.aurelia.Perf.particles(level, ParticleTypes.CRIT, getX(), getY() + 5.0, getZ(), 4, 1.5, 1.5, 1.5, 0.1);
            return;
        }
        if (this.inhaleTicks > 0) {
            tickInhale(level);
            return;
        }
        if (--this.sealTimer <= 0) {
            this.sealTimer = phase >= 3 ? 140 : 200;
            for (BlockPos v : valves()) {
                BlockState s = level.getBlockState(v);
                if (s.getValue(SporeValveBlock.OPEN)) {
                    SporeValveBlock.setOpen(level, v, s, false);
                    com.aurelia.Perf.particles(level, ParticleTypes.SPORE_BLOSSOM_AIR, v.getX() + 0.5, v.getY() + 1.0, v.getZ() + 0.5, 30, 0.5, 0.5, 0.5, 0.02);
                    break;
                }
            }
        }
        if (target != null && --this.inhaleTimer <= 0) {
            this.inhaleTimer = phase >= 3 ? 360 : 500;
            this.inhaleTicks = 120;
            this.playSound(SoundEvents.WARDEN_SONIC_CHARGE, 4.0f, 0.5f);
            for (ServerPlayer player : level.getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(48.0))) {
                Story.title(player, "SHE INHALES", "Open the spore valves before she breathes out", ChatFormatting.LIGHT_PURPLE);
            }
        }
    }

    // ---- the inhale

    private void tickInhale(ServerLevel level) {
        this.inhaleTicks--;
        Vec3 maw = this.position().add(0.0, 4.0, 0.0);
        for (Player player : level.getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(24.0))) {
            if (player.isCreative() || player.isSpectator()) {
                continue;
            }
            Vec3 pull = maw.subtract(player.position()).multiply(1.0, 0.0, 1.0);
            if (pull.lengthSqr() > 4.0) {
                pull = pull.normalize().scale(0.055);
                player.push(pull.x, 0.0, pull.z);
                player.hurtMarked = true;
            }
            if (this.inhaleTicks % 4 == 0) {
                com.aurelia.Perf.particles(level, ParticleTypes.SPORE_BLOSSOM_AIR, player.getX(), player.getY() + 1.0, player.getZ(), 2, 0.3, 0.3, 0.3, 0.0);
            }
        }
        if (this.inhaleTicks % 10 == 0) {
            this.playSound(SoundEvents.ELYTRA_FLYING, 2.0f, 0.4f);
        }
        if (this.inhaleTicks > 0) {
            return;
        }
        long open = valves().stream().filter(v -> level.getBlockState(v).getValue(SporeValveBlock.OPEN)).count();
        if (open >= 2) {
            this.openTicks = 140;
            this.say("The valves roar, and she chokes on her own spores. Her petals are torn open: strike the heart!");
            this.playSound(SoundEvents.RAVAGER_STUNNED, 4.0f, 0.4f);
            for (ServerPlayer player : level.getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(48.0))) {
                Story.title(player, "", "She chokes", ChatFormatting.LIGHT_PURPLE);
            }
            for (BlockPos v : valves()) {
                BlockState s = level.getBlockState(v);
                if (s.getValue(SporeValveBlock.OPEN)) {
                    SporeValveBlock.setOpen(level, v, s, false);
                }
            }
        } else {
            exhale(level);
        }
    }

    private void exhale(ServerLevel level) {
        this.say("She breathes out. The whole cavern turns violet.");
        this.playSound(SoundEvents.WARDEN_SONIC_BOOM, 4.0f, 0.5f);
        for (Player player : level.getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(20.0))) {
            player.addEffect(new MobEffectInstance(MobEffects.POISON, 160, 1));
            player.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 120, 0));
            player.hurt(this.damageSources().magic(), player.getMaxHealth() * 0.2f);
        }
        com.aurelia.Perf.particles(level, ParticleTypes.SPORE_BLOSSOM_AIR, getX(), getY() + 3.0, getZ(), 400, 10.0, 3.0, 10.0, 0.1);
        this.heal(this.getMaxHealth() * 0.03f);
    }

    // ---- attacks

    @Override
    protected void castAbility(LivingEntity target) {
        if (this.inhaleTicks > 0 || this.openTicks > 0) {
            return;
        }
        this.casts++;
        if (phase >= 2 && this.casts % 3 == 0) {
            summon(target);
        }
        switch (this.casts % 3) {
            case 0 -> rootLash();
            case 1 -> sporeMortar();
            default -> {
                this.devourTicks = 18;
                this.playSound(SoundEvents.RAVAGER_ROAR, 3.0f, 0.6f);
            }
        }
    }

    private void rootLash() {
        List<Player> players = this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(28.0), p -> !p.isCreative() && !p.isSpectator());
        for (int i = 0; i < players.size() && i < 3; i++) {
            this.lashAt.add(players.get(i).position());
            this.lashTicks.add(26);
        }
        this.playSound(SoundEvents.ROOTS_BREAK, 3.0f, 0.4f);
    }

    private void tickLashes(ServerLevel level) {
        float damage = phase >= 3 ? 36.0f : phase == 2 ? 30.0f : 24.0f;
        for (int i = this.lashAt.size() - 1; i >= 0; i--) {
            Vec3 at = this.lashAt.get(i);
            int t = this.lashTicks.get(i) - 1;
            if (t % 3 == 0) {
                com.aurelia.Perf.particles(level, ParticleTypes.SPORE_BLOSSOM_AIR, at.x, at.y + 0.1, at.z, 6, 1.0, 0.0, 1.0, 0.0);
                com.aurelia.Perf.particles(level, ParticleTypes.CRIMSON_SPORE, at.x, at.y + 0.2, at.z, 6, 1.0, 0.0, 1.0, 0.0);
            }
            if (t <= 0) {
                for (Player player : level.getEntitiesOfClass(Player.class, new net.minecraft.world.phys.AABB(at, at).inflate(1.8, 2.0, 1.8))) {
                    player.hurt(this.damageSources().mobAttack(this), damage);
                    player.push(0.0, 1.0, 0.0);
                    player.hurtMarked = true;
                    player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 2));
                }
                com.aurelia.Perf.particles(level, ParticleTypes.EXPLOSION, at.x, at.y + 0.5, at.z, 2, 0.5, 0.2, 0.5, 0.0);
                level.playSound(null, BlockPos.containing(at), SoundEvents.ROOTS_BREAK, SoundSource.HOSTILE, 2.0f, 0.5f);
                this.lashAt.remove(i);
                this.lashTicks.remove(i);
            } else {
                this.lashTicks.set(i, t);
            }
        }
    }

    private void sporeMortar() {
        for (Player player : this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(28.0), p -> !p.isCreative() && !p.isSpectator())) {
            AreaEffectCloud cloud = new AreaEffectCloud(this.level(), player.getX() + (random.nextDouble() - 0.5) * 2.0, player.getY(),
                    player.getZ() + (random.nextDouble() - 0.5) * 2.0);
            cloud.setOwner(this);
            cloud.setRadius(3.0f);
            cloud.setDuration(120);
            cloud.setWaitTime(15);
            cloud.setRadiusPerTick(-0.01f);
            cloud.setParticle(ParticleTypes.SPORE_BLOSSOM_AIR);
            cloud.addEffect(new MobEffectInstance(MobEffects.POISON, 100, phase >= 3 ? 2 : 1));
            cloud.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 80, 0));
            this.level().addFreshEntity(cloud);
        }
        this.playSound(SoundEvents.SLIME_SQUISH, 3.0f, 0.4f);
    }

    private void devour(ServerLevel level) {
        Vec3 look = Vec3.directionFromRotation(0.0f, this.getYRot());
        Vec3 front = this.position().add(look.scale(3.0));
        for (Player player : level.getEntitiesOfClass(Player.class, new net.minecraft.world.phys.AABB(front, front).inflate(4.0, 4.0, 4.0))) {
            player.hurt(this.damageSources().mobAttack(this), phase >= 3 ? 56.0f : 44.0f);
            player.addEffect(new MobEffectInstance(MobEffects.WITHER, 80, 1));
        }
        this.playSound(SoundEvents.EVOKER_FANGS_ATTACK, 4.0f, 0.4f);
        com.aurelia.Perf.particles(level, ParticleTypes.SPORE_BLOSSOM_AIR, front.x, front.y + 2.0, front.z, 60, 2.0, 1.0, 2.0, 0.05);
    }

    private void summon(LivingEntity target) {
        int grubs = this.level().getEntitiesOfClass(RootGrub.class, this.getBoundingBox().inflate(32.0)).size();
        for (int i = 0; i < 2 && grubs + i < 6; i++) {
            RootGrub grub = ModEntities.ROOT_GRUB.get().create(this.level());
            if (grub != null) {
                double a = random.nextDouble() * Math.PI * 2.0;
                grub.moveTo(getX() + Math.cos(a) * 6.0, getY(), getZ() + Math.sin(a) * 6.0, random.nextFloat() * 360.0f, 0.0f);
                grub.setTarget(target);
                this.level().addFreshEntity(grub);
            }
        }
        if (phase >= 3) {
            int drifters = this.level().getEntitiesOfClass(SporeDrifter.class, this.getBoundingBox().inflate(32.0)).size();
            for (int i = 0; i < 2 && drifters + i < 4; i++) {
                SporeDrifter drifter = ModEntities.SPORE_DRIFTER.get().create(this.level());
                if (drifter != null) {
                    drifter.moveTo(getX() + (random.nextDouble() - 0.5) * 8.0, getY() + 6.0, getZ() + (random.nextDouble() - 0.5) * 8.0, 0.0f, 0.0f);
                    drifter.setTarget(target);
                    this.level().addFreshEntity(drifter);
                }
            }
        }
    }

    @Override
    protected float incomingMultiplier() {
        return this.openTicks > 0 ? 1.0f : 0.3f;
    }

    @Override
    protected float capMultiplier() {
        return this.openTicks > 0 ? 2.5f : 1.0f;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        return super.hurt(source, amount);
    }
}
