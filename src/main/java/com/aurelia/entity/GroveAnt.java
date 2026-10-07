package com.aurelia.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.level.Level;

/** Horse-sized ant that roams the Gaudy Grove and is summoned by Mossback. */
public class GroveAnt extends AureliaMinion {

    public GroveAnt(EntityType<? extends GroveAnt> type, Level level) {
        super(type, level);
        this.xpReward = 10;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(30.0, 7.0, 0.34);
    }
}
