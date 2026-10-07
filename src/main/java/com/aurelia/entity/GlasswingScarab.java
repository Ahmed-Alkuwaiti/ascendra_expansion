package com.aurelia.entity;

import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;

/** Sunscar Citadel beast. Burrows into the sand and bursts out beside you; its bite leaves glass in the wound. */
public class GlasswingScarab extends BeastGuard {
    private int burrowCooldown = 100;

    public GlasswingScarab(EntityType<? extends GlasswingScarab> type, Level level) {
        super(type, level);
        this.xpReward = 22;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 40.0)
                .add(Attributes.ATTACK_DAMAGE, 9.0)
                .add(Attributes.ARMOR, 8.0)
                .add(Attributes.MOVEMENT_SPEED, 0.34)
                .add(Attributes.FOLLOW_RANGE, 32.0);
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        LivingEntity target = this.getTarget();
        if (target == null || !target.isAlive() || --this.burrowCooldown > 0) {
            return;
        }
        this.burrowCooldown = 140;
        if (this.distanceToSqr(target) > 36.0 && this.onGround() && this.level() instanceof ServerLevel level) {
            BlockParticleOption sand = new BlockParticleOption(ParticleTypes.BLOCK, Blocks.RED_SAND.defaultBlockState());
            level.sendParticles(sand, getX(), getY() + 0.3, getZ(), 40, 0.6, 0.2, 0.6, 0.1);
            if (this.randomTeleport(target.getX() + (this.random.nextDouble() - 0.5) * 3.0, target.getY(),
                    target.getZ() + (this.random.nextDouble() - 0.5) * 3.0, false)) {
                level.sendParticles(sand, getX(), getY() + 0.3, getZ(), 40, 0.6, 0.2, 0.6, 0.1);
                this.playSound(SoundEvents.SAND_BREAK, 1.5f, 0.6f);
            }
        }
    }

    @Override
    protected void onBite(LivingEntity victim) {
        victim.addEffect(new MobEffectInstance(MobEffects.WITHER, 60, 0));
    }
}
