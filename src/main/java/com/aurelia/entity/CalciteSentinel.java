package com.aurelia.entity;

import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** Stormwatch Citadel heavy guard. Its shield turns aside most frontal blows, so flank it. */
public class CalciteSentinel extends AureliaMinion {

    public CalciteSentinel(EntityType<? extends CalciteSentinel> type, Level level) {
        super(type, level);
        this.xpReward = 30;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(100.0, 12.0, 0.25)
                .add(Attributes.ARMOR, 8.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.5)
                .add(Attributes.ATTACK_KNOCKBACK, 1.5);
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.getDirectEntity() != null) {
            Vec3 look = this.getViewVector(1.0f);
            Vec3 toAttacker = source.getDirectEntity().position().subtract(this.position()).normalize();
            if (look.dot(toAttacker) > 0.5) {
                amount *= 0.4f; // shield up
            }
        }
        return super.hurt(source, amount);
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }
}
