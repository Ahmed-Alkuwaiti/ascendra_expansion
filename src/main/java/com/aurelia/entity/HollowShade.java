package com.aurelia.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.level.Level;

/** A shadow that crawls out of the ash of the Hollow and is summoned by the Hollow King. */
public class HollowShade extends AureliaMinion {

    public HollowShade(EntityType<? extends HollowShade> type, Level level) {
        super(type, level);
        this.xpReward = 12;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(34.0, 8.0, 0.31);
    }
}
