package com.unstablefrontiers.ecology;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import java.util.ArrayList;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.GsonHelper;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntityType;

/**
 * Who lives in or guards one part of a landmark: data/&lt;ns&gt;/roster/&lt;name&gt;.json. Entries name entity ids with a
 * weight and an optional per-wave limit; an optional elite (with a title, a boss-bar colour and abilities) leads guardian
 * and finale fights; flyers are used at a zone's flyer spawn points. Ids are checked against the entity registry; an id
 * that is not registered makes the roster unusable and is reported (see {@link #missing()}), never replaced.
 */
public record Roster(ResourceLocation id, List<Entry> mobs, List<Entry> flyers, @Nullable Elite elite, int escorts) {
    public record Entry(ResourceLocation type, int weight, int max) {}

    /** {@code health} multiplies the elite's maximum health (1 = unchanged). */
    public record Elite(ResourceLocation type, String title, String bar, List<String> abilities, double health) {}

    public static Roster parse(ResourceLocation id, JsonObject o) {
        Elite elite = null;
        if (o.has("elite")) {
            JsonObject e = GsonHelper.getAsJsonObject(o, "elite");
            List<String> ab = new ArrayList<>();
            for (JsonElement a : GsonHelper.getAsJsonArray(e, "abilities", new com.google.gson.JsonArray())) {
                ab.add(a.getAsString());
            }
            elite = new Elite(ResourceLocation.parse(GsonHelper.getAsString(e, "id")), GsonHelper.getAsString(e, "title", ""),
                    GsonHelper.getAsString(e, "bar", "red"), ab, GsonHelper.getAsDouble(e, "health", 1.0D));
        }
        return new Roster(id, entries(o, "mobs"), entries(o, "flyers"), elite, GsonHelper.getAsInt(o, "escorts", 0));
    }

    private static List<Entry> entries(JsonObject o, String key) {
        List<Entry> out = new ArrayList<>();
        for (JsonElement el : GsonHelper.getAsJsonArray(o, key, new com.google.gson.JsonArray())) {
            JsonObject e = el.getAsJsonObject();
            out.add(new Entry(ResourceLocation.parse(GsonHelper.getAsString(e, "id")), GsonHelper.getAsInt(e, "weight", 1),
                    GsonHelper.getAsInt(e, "max", 0)));
        }
        return out;
    }

    /** Every id in this roster that is not a registered entity type. Empty means the roster is usable. */
    public List<ResourceLocation> missing() {
        List<ResourceLocation> out = new ArrayList<>();
        for (Entry e : mobs) {
            check(e.type(), out);
        }
        for (Entry e : flyers) {
            check(e.type(), out);
        }
        if (elite != null) {
            check(elite.type(), out);
        }
        return out;
    }

    private static void check(ResourceLocation type, List<ResourceLocation> out) {
        // The entity registry answers unknown ids with its default (the pig), so test the key.
        if (!BuiltInRegistries.ENTITY_TYPE.containsKey(type) && !out.contains(type)) {
            out.add(type);
        }
    }

    public static EntityType<?> type(ResourceLocation id) {
        return BuiltInRegistries.ENTITY_TYPE.get(id);
    }

    /** Picks up to n creatures from a list by weight, honouring each entry's per-wave limit. */
    public static List<EntityType<?>> pick(List<Entry> list, int n, RandomSource random) {
        List<EntityType<?>> out = new ArrayList<>();
        int[] used = new int[list.size()];
        for (int i = 0; i < n; i++) {
            int total = 0;
            for (int j = 0; j < list.size(); j++) {
                if (open(list, used, j)) {
                    total += Math.max(1, list.get(j).weight());
                }
            }
            if (total == 0) {
                break;
            }
            int r = random.nextInt(total);
            for (int j = 0; j < list.size(); j++) {
                if (!open(list, used, j)) {
                    continue;
                }
                r -= Math.max(1, list.get(j).weight());
                if (r < 0) {
                    used[j]++;
                    out.add(type(list.get(j).type()));
                    break;
                }
            }
        }
        return out;
    }

    private static boolean open(List<Entry> list, int[] used, int j) {
        return list.get(j).max() == 0 || used[j] < list.get(j).max();
    }
}
