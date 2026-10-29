package com.unstablefrontiers.abyss;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.encounter.EncounterManager;
import com.unstablefrontiers.encounter.LandmarkData;
import com.unstablefrontiers.encounter.LandmarkState;
import com.unstablefrontiers.landmark.FrontierData;
import com.unstablefrontiers.landmark.LandmarkDef;
import com.unstablefrontiers.world.LandmarkPiece;
import java.util.HashSet;
import java.util.Optional;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.Vec3;

/**
 * The abyss's five places are built the first time a player comes within {@link #BUILD_RANGE} blocks (the landing as you
 * arrive), each from its template onto the island the generator keeps for it, and registered as a landmark so its fights
 * run like the frontier's. Which are built is saved with the world.
 */
public final class AbyssPlaces extends SavedData {
    private static final String NAME = "unstable_frontiers_abyss_places";
    public static final int BUILD_RANGE = 96;
    private final Set<String> built = new HashSet<>();

    public static AbyssPlaces get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(new SavedData.Factory<>(AbyssPlaces::new, AbyssPlaces::load), NAME);
    }

    private static AbyssPlaces load(CompoundTag tag, HolderLookup.Provider registries) {
        AbyssPlaces p = new AbyssPlaces();
        for (Tag t : tag.getList("Built", Tag.TAG_STRING)) {
            p.built.add(t.getAsString());
        }
        return p;
    }

    @Override
    public CompoundTag save(CompoundTag tag, HolderLookup.Provider registries) {
        ListTag l = new ListTag();
        for (String s : built) {
            l.add(StringTag.valueOf(s));
        }
        tag.put("Built", l);
        return tag;
    }

    public boolean isBuilt(AbyssTerrain.Anchor a) {
        return built.contains(a.name());
    }

    public static ResourceLocation template(AbyssTerrain.Anchor a) {
        return UnstableFrontiers.id("abyss_" + a.name());
    }

    /** Feet position where a player stands at an anchor's centre. */
    public static Vec3 standing(AbyssTerrain.Anchor a) {
        return new Vec3(a.x() + 0.5D, a.top() + 2, a.z() + 0.5D);
    }

    /** Builds what is near players (every second). */
    public static void tick(ServerLevel level) {
        if (level.getGameTime() % 20 != 0) {
            return;
        }
        AbyssPlaces places = get(level);
        for (ServerPlayer p : level.players()) {
            for (AbyssTerrain.Anchor a : AbyssTerrain.ANCHORS) {
                if (!places.isBuilt(a) && Math.hypot(p.getX() - a.x(), p.getZ() - a.z()) < BUILD_RANGE) {
                    build(level, a);
                }
            }
        }
    }

    /** Places an anchor's template (once). Loads the few chunks it covers. */
    public static void build(ServerLevel level, AbyssTerrain.Anchor a) {
        AbyssPlaces places = get(level);
        if (places.isBuilt(a)) {
            return;
        }
        ResourceLocation id = template(a);
        Optional<StructureTemplate> t = level.getStructureManager().get(id);
        LandmarkDef def = FrontierData.landmark(id);
        if (t.isEmpty() || def == null) {
            UnstableFrontiers.LOGGER.error("Astral Abyss: template or definition {} missing; {} cannot be built", id, a.name());
            places.built.add(a.name());   // do not retry every second
            places.setDirty();
            return;
        }
        BlockPos size = new BlockPos(t.get().getSize());
        BlockPos origin = new BlockPos(a.x() - size.getX() / 2, a.top() + 2 - def.ground(), a.z() - size.getZ() / 2);
        for (int cx = origin.getX() >> 4; cx <= (origin.getX() + size.getX()) >> 4; cx++) {
            for (int cz = origin.getZ() >> 4; cz <= (origin.getZ() + size.getZ()) >> 4; cz++) {
                level.getChunk(cx, cz);
            }
        }
        t.get().placeInWorld(level, origin, origin, LandmarkPiece.settings(Rotation.NONE), level.random, 2);
        LandmarkData data = EncounterManager.data(level);
        if (data.get(origin.asLong()) == null) {
            data.add(new LandmarkState(id, origin, Rotation.NONE));
        }
        places.built.add(a.name());
        places.setDirty();
        UnstableFrontiers.LOGGER.info("Astral Abyss: built {} at {}", a.name(), origin.toShortString());
    }
}
