package com.aurelia.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.level.Level;

/** A reflection of the White Silence. It looks exactly like her, hits like her, and shatters into frost when struck. */
public class PaleMirage extends AureliaMinion {
    private int life = 600;

    public PaleMirage(EntityType<? extends PaleMirage> type, Level level) {
        super(type, level);
        this.xpReward = 0;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(20.0, 16.0, 0.29);
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (--this.life <= 0) {
            this.discard();
        }
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && target instanceof LivingEntity victim && victim.canFreeze()) {
            victim.setTicksFrozen(Math.min(victim.getTicksRequiredToFreeze() + 40, victim.getTicksFrozen() + 50));
        }
        return hit;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (this.level().isClientSide || this.isRemoved()) {
            return false;
        }
        if (source.getEntity() instanceof LivingEntity attacker) {
            attacker.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 2));
            if (attacker.canFreeze()) {
                attacker.setTicksFrozen(attacker.getTicksRequiredToFreeze() + 40);
            }
        }
        this.playSound(SoundEvents.GLASS_BREAK, 1.5f, 1.2f);
        if (this.level() instanceof ServerLevel level) {
            level.sendParticles(ParticleTypes.SNOWFLAKE, getX(), getY() + 3.0, getZ(), 60, 0.6, 2.0, 0.6, 0.08);
        }
        this.discard();
        return false;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return true;
    }
}
