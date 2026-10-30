package com.unstablefrontiers.client;

import net.minecraft.client.renderer.DimensionSpecialEffects;
import net.minecraft.world.phys.Vec3;

/** Above the Drowned Expanse: an ordinary daylight sky with clouds high over the water. Under it the fog does the work. */
public class DrownedSkyEffects extends DimensionSpecialEffects {
    public DrownedSkyEffects() {
        super(340.0F, true, SkyType.NORMAL, false, false);
    }

    @Override
    public Vec3 getBrightnessDependentFogColor(Vec3 fogColor, float brightness) {
        return fogColor.multiply(brightness * 0.94F + 0.06F, brightness * 0.94F + 0.06F, brightness * 0.91F + 0.09F);
    }

    @Override
    public boolean isFoggyAt(int x, int y) {
        return false;
    }
}
