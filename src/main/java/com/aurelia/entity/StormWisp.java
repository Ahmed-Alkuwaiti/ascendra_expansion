package com.aurelia.entity;

import com.aurelia.block.PuzzleNodeBlock;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * Stormwatch Citadel caster. Floats above its target and calls down telegraphed lightning.
 * The lightning charges any Storm Pylon within 4 blocks of the strike, which is how the Stormwatch portal puzzle
 * is solved: lure a wisp and stand next to a pylon.
 */
public class StormWisp extends FlyingGuard {
    private int shockTicks = 0;
    private BlockPos shockPos = BlockPos.ZERO;

    public StormWisp(EntityType<? extends StormWisp> type, Level level) {
        super(type, level);
        this.xpReward = 25;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 30.0)
                .add(Attributes.ATTACK_DAMAGE, 6.0)
                .add(Attributes.MOVEMENT_SPEED, 0.25)
                .add(Attributes.FLYING_SPEED, 0.4)
                .add(Attributes.FOLLOW_RANGE, 32.0);
    }

    @Override
    protected double hoverHeight() {
        return 3.5;
    }

    @Override
    protected double hoverRadius() {
        return 8.0;
    }

    @Override
    protected int attackInterval() {
        return 80;
    }

    @Override
    protected void attack(LivingEntity target) {
        this.shockTicks = 24;
        this.shockPos = target.blockPosition();
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.shockTicks > 0) {
            this.shockTicks--;
            if (this.level() instanceof ServerLevel serverLevel) {
                serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, shockPos.getX() + 0.5, shockPos.getY() + 0.3,
                        shockPos.getZ() + 0.5, 6, 1.2, 0.1, 1.2, 0.05);
            }
            if (this.shockTicks == 0) {
                this.strike();
            }
        }
    }

    private void strike() {
        if (!(this.level() instanceof ServerLevel serverLevel)) {
            return;
        }
        LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(serverLevel);
        if (bolt != null) {
            bolt.moveTo(Vec3.atBottomCenterOf(this.shockPos));
            bolt.setVisualOnly(true);
            serverLevel.addFreshEntity(bolt);
        }
        for (LivingEntity victim : serverLevel.getEntitiesOfClass(LivingEntity.class,
                new net.minecraft.world.phys.AABB(this.shockPos).inflate(2.5),
                e -> !(e instanceof FlyingGuard) && !(e instanceof AureliaBoss))) {
            victim.hurt(this.damageSources().mobAttack(this), 8.0f);
        }
        PuzzleNodeBlock.chargeNearby(serverLevel, this.shockPos, 4);
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.is(DamageTypeTags.IS_LIGHTNING)) {
            return false;
        }
        return super.hurt(source, amount);
    }
}
