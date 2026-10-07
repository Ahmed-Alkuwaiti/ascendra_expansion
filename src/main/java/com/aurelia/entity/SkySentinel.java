package com.aurelia.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.level.Level;

/** A quartz-and-cloud guardian that patrols Skyreach and fills the spawner rooms of its citadel. */
public class SkySentinel extends AureliaMinion {

    public SkySentinel(EntityType<? extends SkySentinel> type, Level level) {
        super(type, level);
        this.xpReward = 14;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return minionAttributes(50.0, 9.0, 0.30);
    }
}
