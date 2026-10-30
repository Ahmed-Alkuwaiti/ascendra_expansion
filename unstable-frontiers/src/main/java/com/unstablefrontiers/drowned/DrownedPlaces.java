package com.unstablefrontiers.drowned;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.encounter.EncounterManager;
import com.unstablefrontiers.encounter.LandmarkData;
import com.unstablefrontiers.encounter.LandmarkState;
import com.unstablefrontiers.encounter.ZoneState;
import com.unstablefrontiers.landmark.FrontierData;
import com.unstablefrontiers.landmark.LandmarkDef;
import com.unstablefrontiers.registry.ModAttachments;
import com.unstablefrontiers.world.LandmarkPiece;
import java.util.HashSet;
import java.util.Optional;
import java.util.Set;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.Vec3;

/**
 * The Drowned Expanse's five places: built from their templates onto their pads the first time a player comes within
 * {@link #BUILD_RANGE} blocks (the Tidewatch Station when you arrive), registered as landmarks so their fights run like the
 * frontier's. Also the player's chart of the Expanse: which places they know of. A place is charted by being told of it
 * (the Tidewatch briefing charts the first two), by winning the fight that points onward, or by finding it.
 */
public final class DrownedPlaces extends SavedData {
    private static final String NAME = "unstable_frontiers_drowned_places";
    public static final int BUILD_RANGE = 96;
    private static final String CHARTED = "drowned_charted";
    private final Set<String> built = new HashSet<>();

    public static DrownedPlaces get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(new SavedData.Factory<>(DrownedPlaces::new, DrownedPlaces::load), NAME);
    }

    private static DrownedPlaces load(CompoundTag tag, HolderLookup.Provider registries) {
        DrownedPlaces p = new DrownedPlaces();
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

    public boolean isBuilt(DrownedTerrain.Anchor a) {
        return built.contains(a.name());
    }

    public static ResourceLocation template(DrownedTerrain.Anchor a) {
        return UnstableFrontiers.id("drowned_" + a.name());
    }

    /** What winning each place's fight charts next. */
    private static DrownedTerrain.Anchor[] onward(DrownedTerrain.Anchor a) {
        if (a == DrownedTerrain.DEEPWORK || a == DrownedTerrain.CHOIR) {
            return new DrownedTerrain.Anchor[] {DrownedTerrain.WRECK};
        }
        if (a == DrownedTerrain.WRECK) {
            return new DrownedTerrain.Anchor[] {DrownedTerrain.VAULT};
        }
        return new DrownedTerrain.Anchor[0];
    }

    // ------------------------------------------------------------------------------------------------- charting
    public static boolean charted(ServerPlayer p, DrownedTerrain.Anchor a) {
        return ModAttachments.of(p).getCompound(CHARTED).getBoolean(a.name());
    }

    public static void chart(ServerPlayer p, DrownedTerrain.Anchor a, boolean announce) {
        CompoundTag all = ModAttachments.of(p);
        CompoundTag c = all.getCompound(CHARTED);
        if (c.getBoolean(a.name())) {
            return;
        }
        c.putBoolean(a.name(), true);
        all.put(CHARTED, c);
        if (announce) {
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.charted",
                    Component.translatable("place.unstable_frontiers." + a.name())).withStyle(ChatFormatting.AQUA), false);
        }
    }

    // ---------------------------------------------------------------------------------------------------- tick
    /** Every second: build what is near, chart what is found, chart onward for the winners of each place's fight. */
    public static void tick(ServerLevel level) {
        if (level.getGameTime() % 20 != 0) {
            return;
        }
        DrownedPlaces places = get(level);
        for (ServerPlayer p : level.players()) {
            for (DrownedTerrain.Anchor a : DrownedTerrain.ANCHORS) {
                double d = Math.hypot(p.getX() - a.x(), p.getZ() - a.z());
                if (!places.isBuilt(a) && d < BUILD_RANGE) {
                    build(level, a);
                }
                if (d < a.radius() + 24) {
                    chart(p, a, true);
                }
            }
        }
        if (level.getGameTime() % 100 != 0) {
            return;
        }
        for (DrownedTerrain.Anchor a : DrownedTerrain.ANCHORS) {
            LandmarkState s = state(level, a);
            LandmarkDef def = s == null ? null : FrontierData.landmark(s.id);
            LandmarkDef.Zone z = def == null ? null : def.finalZone();
            if (z == null) {
                continue;
            }
            ZoneState zs = s.zone(z);
            if (zs.status != ZoneState.Status.CLEARED) {
                continue;
            }
            for (java.util.UUID u : zs.participants) {
                if (level.getServer().getPlayerList().getPlayer(u) instanceof ServerPlayer p) {
                    for (DrownedTerrain.Anchor next : onward(a)) {
                        chart(p, next, true);
                    }
                }
            }
        }
    }

    @Nullable
    public static LandmarkState state(ServerLevel level, DrownedTerrain.Anchor a) {
        return EncounterManager.at(level, new BlockPos(a.x(), a.floor() + 2, a.z()), a.radius() + 16);
    }

    /** A named point of a built place's template, in the world (for example the arrival spot or the bell). */
    @Nullable
    public static BlockPos point(ServerLevel level, DrownedTerrain.Anchor a, String name) {
        build(level, a);
        LandmarkState s = state(level, a);
        LandmarkDef def = s == null ? null : FrontierData.landmark(s.id);
        BlockPos local = def == null ? null : def.points().get(name);
        return local == null ? null : s.world(local);
    }

    /** Where arrivals stand: inside the Tidewatch Station's air dome. */
    public static Vec3 arrival(ServerLevel level) {
        BlockPos p = point(level, DrownedTerrain.TIDEWATCH, "arrival");
        return p != null ? Vec3.atBottomCenterOf(p) : new Vec3(0.5D, DrownedTerrain.TIDEWATCH.floor() + 2, 0.5D);
    }

    /** Places an anchor's template (once). Loads the few chunks it covers. */
    public static void build(ServerLevel level, DrownedTerrain.Anchor a) {
        DrownedPlaces places = get(level);
        if (places.isBuilt(a)) {
            return;
        }
        ResourceLocation id = template(a);
        Optional<StructureTemplate> t = level.getStructureManager().get(id);
        LandmarkDef def = FrontierData.landmark(id);
        if (t.isEmpty() || def == null) {
            UnstableFrontiers.LOGGER.error("Drowned Expanse: template or definition {} missing; {} cannot be built", id, a.name());
            places.built.add(a.name());
            places.setDirty();
            return;
        }
        BlockPos size = new BlockPos(t.get().getSize());
        // the template's ground row is the pad's top block (the floor)
        BlockPos origin = new BlockPos(a.x() - size.getX() / 2, a.floor() - def.ground(), a.z() - size.getZ() / 2);
        for (int cx = origin.getX() >> 4; cx <= (origin.getX() + size.getX()) >> 4; cx++) {
            for (int cz = origin.getZ() >> 4; cz <= (origin.getZ() + size.getZ()) >> 4; cz++) {
                level.getChunk(cx, cz);
            }
        }
        // the template says exactly which blocks are waterlogged: with liquids kept, a gate or a bell inside a shelter
        // would be waterlogged by the sea that stood there before, and pour water into the air dome
        t.get().placeInWorld(level, origin, origin, LandmarkPiece.settings(Rotation.NONE).setKeepLiquids(false), level.random, 2);
        LandmarkData data = EncounterManager.data(level);
        if (data.get(origin.asLong()) == null) {
            data.add(new LandmarkState(id, origin, Rotation.NONE));
        }
        places.built.add(a.name());
        places.setDirty();
        UnstableFrontiers.LOGGER.info("Drowned Expanse: built {} at {}", a.name(), origin.toShortString());
    }
}
