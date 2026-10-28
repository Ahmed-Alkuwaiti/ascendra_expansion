package com.unstablefrontiers.world;

import com.unstablefrontiers.UnstableFrontiers;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.biome.Biome;

public final class FrontierDimension {
    public static final ResourceKey<Level> LEVEL = ResourceKey.create(Registries.DIMENSION, UnstableFrontiers.id("frontier"));
    /** The quiet region: wild spawns are rare here unless a tower is close. */
    public static final ResourceKey<Biome> HUSHED_BARRENS = ResourceKey.create(Registries.BIOME, UnstableFrontiers.id("hushed_barrens"));

    private FrontierDimension() {}

    public static boolean is(Level level) {
        return level.dimension() == LEVEL;
    }
}
