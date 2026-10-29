package com.unstablefrontiers.abyss;

import com.unstablefrontiers.UnstableFrontiers;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import com.unstablefrontiers.entity.StarBoltEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.level.biome.Biome;

/** The Astral Abyss: keys and the heights everything else in it agrees on. */
public final class AbyssDimension {
    public static final ResourceKey<Level> LEVEL = ResourceKey.create(Registries.DIMENSION, UnstableFrontiers.id("astral_abyss"));
    public static final ResourceLocation EFFECTS = UnstableFrontiers.id("astral_abyss");
    public static final ResourceKey<Biome> SHOALS = ResourceKey.create(Registries.BIOME, UnstableFrontiers.id("starlit_shoals"));
    public static final ResourceKey<Biome> REACH = ResourceKey.create(Registries.BIOME, UnstableFrontiers.id("shattered_reach"));
    public static final ResourceKey<Biome> HOLLOW = ResourceKey.create(Registries.BIOME, UnstableFrontiers.id("eclipse_hollow"));
    /** Below this a falling player is caught by the rift and set back on safe ground. */
    public static final int CATCH_Y = 24;
    /** Below this an item, or anything else that is not a player, is lost to the void unless rescued. */
    public static final int ITEM_RESCUE_Y = 16;

    private AbyssDimension() {}

    public static boolean is(Level level) {
        return level.dimension() == LEVEL;
    }

    /** Natural spawns stay off the landing and the Hollow Crown, and are capped at 8 of the Abyss's creatures within 48 blocks. */
    public static boolean crowded(Level level, Vec3 at) {
        if (near(at, AbyssTerrain.LANDING, 12) || near(at, AbyssTerrain.HOLLOW_CROWN, 8)) {
            return true;
        }
        return level.getEntitiesOfClass(Mob.class, new AABB(at, at).inflate(48), StarBoltEntity::isAbyssCreature).size() >= 8;
    }

    private static boolean near(Vec3 at, AbyssTerrain.Anchor a, int margin) {
        double dx = at.x - a.x(), dz = at.z - a.z();
        return dx * dx + dz * dz < (double) (a.radius() + margin) * (a.radius() + margin);
    }
}
