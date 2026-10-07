package com.aurelia.entity;

import com.aurelia.registry.ModBlocks;
import com.aurelia.registry.ModEntities;
import com.aurelia.registry.ModItems;
import com.aurelia.world.Story;
import java.util.ArrayList;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.BossEvent;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * Mossback, Warden of the Grove (2500 HP).
 * Phase 1: heavy melee plus a telegraphed ground slam.
 * Phase 2 (66%): faster, bigger slam that also deals armour-piercing damage, and every slam calls Grove Ants.
 * Phase 3 (33%): chain slams (two in a row), widest radius, three ants per call.
 */
public class MossbackTitan extends AureliaBoss {
    private int slamTicks = 0;
    private int pendingSlams = 0;
    /** Gimmick: Root Hearts he plants around the arena. While any stands he heals and shrugs off most damage. */
    private final List<BlockPos> hearts = new ArrayList<>();
    private int heartTimer = 300;

    public MossbackTitan(EntityType<? extends MossbackTitan> type, Level level) {
        super(type, level, BossEvent.BossBarColor.GREEN);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return baseAttributes(2500.0, 26.0, 0.27);
    }

    @Override
    protected Item shardItem() {
        return ModItems.GROVE_SHARD.get();
    }

    @Override
    protected String phaseLine() {
        return Story.TITAN_PHASE;
    }

    @Override
    protected String finalPhaseLine() {
        return Story.TITAN_FINAL;
    }

    @Override
    protected String deathLine() {
        return Story.TITAN_DEATH;
    }

    @Override
    public String awakenLine() {
        return "The garden remembers.";
    }

    @Override
    protected int abilityInterval() {
        return phase >= 3 ? 70 : phase == 2 ? 90 : 130;
    }

    @Override
    protected void onPhaseTwo() {
        setSpeed(0.30);
    }

    @Override
    protected void onPhaseThree() {
        setSpeed(0.36);
    }

    private void setSpeed(double value) {
        var speed = this.getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed != null) {
            speed.setBaseValue(value);
        }
    }

    @Override
    protected void castAbility(LivingEntity target) {
        this.slamTicks = 30; // 1.5 second wind-up
        this.pendingSlams = phase >= 3 ? 1 : 0;
        this.getNavigation().stop();
        if (phase >= 2) {
            summonAnts(target, phase >= 3 ? 3 : 2);
        }
    }

    @Override
    protected void tickBoss(@Nullable LivingEntity target) {
        this.hearts.removeIf(pos -> !this.level().getBlockState(pos).is(ModBlocks.ROOT_HEART.get()));
        if (!this.hearts.isEmpty() && this.tickCount % 20 == 0) {
            this.heal(this.getMaxHealth() * 0.012f * this.hearts.size());
            if (this.level() instanceof ServerLevel serverLevel) {
                for (BlockPos pos : this.hearts) {
                    serverLevel.sendParticles(ParticleTypes.HAPPY_VILLAGER, pos.getX() + 0.5, pos.getY() + 1.0, pos.getZ() + 0.5, 6, 0.3, 0.4, 0.3, 0.0);
                }
            }
        }
        if (this.hearts.isEmpty() && target != null && --this.heartTimer <= 0) {
            this.heartTimer = phase >= 3 ? 400 : 560;
            plantHearts();
        }
        if (this.slamTicks > 0) {
            this.slamTicks--;
            this.getNavigation().stop();
            if (this.level() instanceof ServerLevel serverLevel) {
                serverLevel.sendParticles(ParticleTypes.ANGRY_VILLAGER, getX(), getY() + getBbHeight() + 0.5, getZ(),
                        3, 0.8, 0.2, 0.8, 0.0);
            }
            if (this.slamTicks == 0) {
                doSlam();
                if (this.pendingSlams > 0) {
                    this.pendingSlams--;
                    this.slamTicks = 20; // quicker second slam
                }
            }
        }
    }

    private void doSlam() {
        double radius = phase >= 3 ? 11.0 : phase == 2 ? 9.0 : 7.0;
        float damage = phase >= 3 ? 56.0f : phase == 2 ? 44.0f : 34.0f;
        float piercing = phase >= 3 ? 14.0f : phase == 2 ? 8.0f : 0.0f; // magic damage ignores armour
        for (LivingEntity victim : this.level().getEntitiesOfClass(LivingEntity.class,
                this.getBoundingBox().inflate(radius, 3.0, radius),
                e -> e != this && !(e instanceof AureliaBoss) && !(e instanceof GroveAnt))) {
            victim.hurt(this.damageSources().mobAttack(this), damage);
            if (piercing > 0.0f) {
                victim.hurt(this.damageSources().magic(), piercing);
            }
            Vec3 push = victim.position().subtract(this.position()).multiply(1.0, 0.0, 1.0).normalize().scale(1.4);
            victim.setDeltaMovement(victim.getDeltaMovement().add(push.x, 1.0, push.z));
            victim.hurtMarked = true;
        }
        this.playSound(SoundEvents.GENERIC_EXPLODE, 3.0f, 0.6f);
        if (this.level() instanceof ServerLevel serverLevel) {
            serverLevel.sendParticles(ParticleTypes.EXPLOSION_EMITTER, getX(), getY() + 0.5, getZ(), 1, 0, 0, 0, 0);
            serverLevel.sendParticles(ParticleTypes.POOF, getX(), getY() + 0.2, getZ(), 60, radius / 2.0, 0.1, radius / 2.0, 0.05);
        }
    }

    private void plantHearts() {
        BlockPos centre = this.arena != null ? this.arena : this.blockPosition();
        int count = phase >= 3 ? 4 : 3;
        for (int i = 0; i < count; i++) {
            double angle = this.random.nextDouble() * Math.PI * 2.0;
            double radius = 6.0 + this.random.nextDouble() * 4.0;
            BlockPos base = BlockPos.containing(centre.getX() + Math.cos(angle) * radius, centre.getY(), centre.getZ() + Math.sin(angle) * radius);
            for (int dy = 3; dy >= -3; dy--) {
                BlockPos pos = base.offset(0, dy, 0);
                if (this.level().getBlockState(pos).isAir() && !this.level().getBlockState(pos.below()).isAir()) {
                    this.level().setBlock(pos, ModBlocks.ROOT_HEART.get().defaultBlockState(), 3);
                    this.hearts.add(pos);
                    break;
                }
            }
        }
        if (!this.hearts.isEmpty()) {
            this.say("Mossback drives his roots into the earth. Break the Root Hearts, or he will not stop healing.");
            this.playSound(SoundEvents.ROOTS_BREAK, 3.0f, 0.5f);
        }
    }

    @Override
    protected float incomingMultiplier() {
        return this.hearts.isEmpty() ? 1.0f : 0.3f;
    }

    @Override
    public void die(DamageSource source) {
        for (BlockPos pos : this.hearts) {
            this.level().setBlock(pos, Blocks.AIR.defaultBlockState(), 3);
        }
        this.hearts.clear();
        super.die(source);
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putLongArray("Hearts", this.hearts.stream().mapToLong(BlockPos::asLong).toArray());
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        this.hearts.clear();
        for (long packed : tag.getLongArray("Hearts")) {
            this.hearts.add(BlockPos.of(packed));
        }
    }

    private void summonAnts(LivingEntity target, int count) {
        int existing = this.level().getEntitiesOfClass(GroveAnt.class, this.getBoundingBox().inflate(24.0)).size();
        for (int i = 0; i < count && existing + i < 8; i++) {
            GroveAnt ant = ModEntities.GROVE_ANT.get().create(this.level());
            if (ant == null) {
                continue;
            }
            ant.moveTo(getX() + (random.nextDouble() - 0.5) * 6.0, getY(), getZ() + (random.nextDouble() - 0.5) * 6.0,
                    random.nextFloat() * 360.0f, 0.0f);
            ant.setTarget(target);
            this.level().addFreshEntity(ant);
        }
    }
}
