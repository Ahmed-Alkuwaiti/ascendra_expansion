package com.unstablefrontiers.landmark;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.GsonHelper;
import net.minecraft.world.level.levelgen.structure.BoundingBox;

/**
 * A landmark's encounters and points of interest, in template-local coordinates. Written by the structure generator next
 * to each template (data/unstable_frontiers/landmark/&lt;name&gt;.json) and read on every data reload.
 */
public record LandmarkDef(ResourceLocation id, ResourceLocation template, BlockPos size, String kind, String title, int ground, List<Zone> zones, Map<String, BlockPos> points,
                          Map<String, List<BlockPos>> gates, List<Resident> residents, @Nullable String rivalryHunters,
                          @Nullable String rivalryPrey) {

    public enum Kind {
        /** Waves on a floor: comes in waves until all are spent and the floor is empty. */
        WAVES,
        /** One burst from hiding the moment you cross the trigger. */
        AMBUSH,
        /** A hanging cell: its prisoner waits, dormant and visible, until you step aboard. */
        CELL,
        /** Waves that hatch from egg clutches; every clutch you smash is one fewer reinforcement. */
        BROOD,
        /** Roosting predators, dormant on their perches until you set foot in the nest or strike one. */
        ROOST,
        /** An elite with escorts and a boss bar. */
        GUARDIAN,
        /** The Great Cage: started by the key at the lock; the beast is shielded while its pylons stand. */
        FINALE,
        /** Not a fight: residents that live here and quarrel among themselves. */
        TERRITORY
    }

    public record Zone(int index, String id, String name, Kind kind, BoundingBox box, BoundingBox trigger, List<BlockPos> spawns,
                       List<BlockPos> flyerSpawns, String roster, int waves, @Nullable String reward, @Nullable String gate,
                       boolean last, List<String> requires, List<BlockPos> brood, List<BlockPos> pylons, @Nullable BlockPos lock,
                       @Nullable String lockGate, @Nullable String broodBlock) {
        public BlockPos centre() {
            return new BlockPos((box.minX() + box.maxX()) / 2, box.minY(), (box.minZ() + box.maxZ()) / 2);
        }
    }

    public record Resident(String roster, List<BlockPos> spots, int count, boolean flying) {}

    @Nullable
    public Zone zone(String zid) {
        for (Zone z : zones) {
            if (z.id().equals(zid)) {
                return z;
            }
        }
        return null;
    }

    @Nullable
    public Zone finalZone() {
        for (Zone z : zones) {
            if (z.last()) {
                return z;
            }
        }
        return null;
    }

    public boolean isFightZone(Zone z) {
        return z.kind() != Kind.TERRITORY;
    }

    static LandmarkDef parse(ResourceLocation id, JsonObject o) {
        List<Zone> zones = new ArrayList<>();
        JsonArray za = GsonHelper.getAsJsonArray(o, "zones", new JsonArray());
        for (int i = 0; i < za.size(); i++) {
            JsonObject z = za.get(i).getAsJsonObject();
            BoundingBox box = box(z.getAsJsonArray("box"));
            zones.add(new Zone(i, GsonHelper.getAsString(z, "id"), GsonHelper.getAsString(z, "name", ""),
                    Kind.valueOf(GsonHelper.getAsString(z, "kind", "waves").toUpperCase()), box,
                    z.has("trigger") ? box(z.getAsJsonArray("trigger")) : box, posList(z, "spawns"),
                    posList(z, z.has("flyer_spawns") ? "flyer_spawns" : "flyers_at"), GsonHelper.getAsString(z, "roster", ""),
                    GsonHelper.getAsInt(z, "waves", -1), z.has("reward") ? GsonHelper.getAsString(z, "reward") : null,
                    z.has("gate") ? GsonHelper.getAsString(z, "gate") : null, GsonHelper.getAsBoolean(z, "final", false),
                    strings(z, "requires"), posList(z, z.has("brood_eggs") ? "brood_eggs" : "release_from"), posList(z, "pylons"),
                    z.has("lock") ? pos(z.getAsJsonArray("lock")) : null, z.has("lock_gate") ? GsonHelper.getAsString(z, "lock_gate") : null,
                    z.has("brood") && z.get("brood").isJsonPrimitive() ? GsonHelper.getAsString(z, "brood") : null));
        }
        Map<String, BlockPos> points = new HashMap<>();
        JsonObject po = GsonHelper.getAsJsonObject(o, "points", new JsonObject());
        for (Map.Entry<String, JsonElement> e : po.entrySet()) {
            points.put(e.getKey(), pos(e.getValue().getAsJsonArray()));
        }
        Map<String, List<BlockPos>> gates = new HashMap<>();
        JsonObject go = GsonHelper.getAsJsonObject(o, "gates", new JsonObject());
        for (Map.Entry<String, JsonElement> e : go.entrySet()) {
            List<BlockPos> list = new ArrayList<>();
            for (JsonElement p : e.getValue().getAsJsonArray()) {
                list.add(pos(p.getAsJsonArray()));
            }
            gates.put(e.getKey(), list);
        }
        List<Resident> residents = new ArrayList<>();
        for (JsonElement r : GsonHelper.getAsJsonArray(o, "residents", new JsonArray())) {
            JsonObject ro = r.getAsJsonObject();
            residents.add(new Resident(GsonHelper.getAsString(ro, "roster"), posList(ro, "spots"), GsonHelper.getAsInt(ro, "count", 2),
                    GsonHelper.getAsBoolean(ro, "flying", false)));
        }
        String hunters = null, prey = null;
        if (o.has("rivalry")) {
            JsonObject rv = o.getAsJsonObject("rivalry");
            hunters = GsonHelper.getAsString(rv, "hunters", null);
            prey = GsonHelper.getAsString(rv, "prey", null);
        }
        ResourceLocation template = ResourceLocation.parse(GsonHelper.getAsString(o, "template", id.toString()));
        JsonArray sz = GsonHelper.getAsJsonArray(o, "size", new JsonArray());
        BlockPos size = sz.size() == 3 ? pos(sz) : new BlockPos(16, 16, 16);
        return new LandmarkDef(id, template, size, GsonHelper.getAsString(o, "kind", "landmark"), GsonHelper.getAsString(o, "title", id.getPath()),
                GsonHelper.getAsInt(o, "ground", 0), zones, points, gates, residents, hunters, prey);
    }

    private static BoundingBox box(JsonArray a) {
        return BoundingBox.fromCorners(new BlockPos(a.get(0).getAsInt(), a.get(1).getAsInt(), a.get(2).getAsInt()),
                new BlockPos(a.get(3).getAsInt(), a.get(4).getAsInt(), a.get(5).getAsInt()));
    }

    private static BlockPos pos(JsonArray a) {
        return new BlockPos(a.get(0).getAsInt(), a.get(1).getAsInt(), a.get(2).getAsInt());
    }

    private static List<BlockPos> posList(JsonObject o, String key) {
        List<BlockPos> out = new ArrayList<>();
        if (o.has(key)) {
            for (JsonElement e : o.getAsJsonArray(key)) {
                out.add(pos(e.getAsJsonArray()));
            }
        }
        return out;
    }

    private static List<String> strings(JsonObject o, String key) {
        List<String> out = new ArrayList<>();
        if (o.has(key)) {
            for (JsonElement e : o.getAsJsonArray(key)) {
                out.add(e.getAsString());
            }
        }
        return out;
    }
}
