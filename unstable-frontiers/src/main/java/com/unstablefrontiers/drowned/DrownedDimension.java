package com.unstablefrontiers.drowned;

import com.unstablefrontiers.UnstableFrontiers;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.animal.AbstractFish;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.level.biome.Biome;

/** The Drowned Expanse: its keys. Heights are in {@link DrownedTerrain}. */
public final class DrownedDimension {
    public static final ResourceKey<Level> LEVEL = ResourceKey.create(Registries.DIMENSION, UnstableFrontiers.id("drowned_expanse"));
    public static final ResourceLocation EFFECTS = UnstableFrontiers.id("drowned_expanse");
    public static final ResourceKey<Biome> SHALLOWS = ResourceKey.create(Registries.BIOME, UnstableFrontiers.id("glassreef_shallows"));
    public static final ResourceKey<Biome> KELPWOOD = ResourceKey.create(Registries.BIOME, UnstableFrontiers.id("kelpwood"));
    public static final ResourceKey<Biome> REACH = ResourceKey.create(Registries.BIOME, UnstableFrontiers.id("sunken_reach"));
    public static final ResourceKey<Biome> TRENCH = ResourceKey.create(Registries.BIOME, UnstableFrontiers.id("blackwater_trench"));

    private DrownedDimension() {}

    public static boolean is(Level level) {
        return level.dimension() == LEVEL;
    }

    /**
     * Natural spawning is turned away here: nothing hostile inside a place (its shelters stay safe), and no more than ten
     * non-fish creatures within 40 blocks of any spot, so the reefs never fill up.
     */
    public static boolean crowded(Level level, Entity e) {
        if (e instanceof Enemy) {
            for (DrownedTerrain.Anchor a : DrownedTerrain.ANCHORS) {
                double dx = e.getX() - a.x(), dz = e.getZ() - a.z();
                if (dx * dx + dz * dz < (a.radius() + 6.0D) * (a.radius() + 6.0D)) {
                    return true;
                }
            }
        }
        return level.getEntitiesOfClass(Mob.class, new AABB(e.blockPosition()).inflate(40), m -> !(m instanceof AbstractFish)).size() >= 10;
    }
}
