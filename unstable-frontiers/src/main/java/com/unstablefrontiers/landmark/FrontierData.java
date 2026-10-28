package com.unstablefrontiers.landmark;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.ecology.Roster;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.annotation.Nullable;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimpleJsonResourceReloadListener;
import net.minecraft.util.profiling.ProfilerFiller;
import net.neoforged.fml.ModList;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.AddReloadListenerEvent;

/**
 * The data the frontier is built from, reloaded with /reload: landmark definitions (data/&lt;ns&gt;/landmark, written by
 * the structure generator) and rosters (data/&lt;ns&gt;/roster). After each load every roster a landmark names is checked;
 * problems are logged as errors with the fix, and kept for {@link #problems()} so players and operators are told in game
 * too. A landmark whose roster is missing or unusable does not start its fights: it never falls back to other creatures.
 */
public final class FrontierData {
    private static final Gson GSON = new Gson();
    private static Map<ResourceLocation, LandmarkDef> landmarks = Map.of();
    private static Map<ResourceLocation, Roster> rosters = Map.of();
    private static List<String> problems = List.of();

    public FrontierData() {}

    @SubscribeEvent
    public void onReload(AddReloadListenerEvent event) {
        event.addListener(new Listener("landmark", true));
        event.addListener(new Listener("roster", false));
    }

    private static final class Listener extends SimpleJsonResourceReloadListener {
        private final boolean isLandmarks;

        Listener(String dir, boolean isLandmarks) {
            super(GSON, dir);
            this.isLandmarks = isLandmarks;
        }

        @Override
        protected void apply(Map<ResourceLocation, JsonElement> files, ResourceManager manager, ProfilerFiller profiler) {
            if (isLandmarks) {
                Map<ResourceLocation, LandmarkDef> out = new HashMap<>();
                files.forEach((id, json) -> {
                    try {
                        out.put(id, LandmarkDef.parse(id, json.getAsJsonObject()));
                    } catch (Exception e) {
                        UnstableFrontiers.LOGGER.error("Landmark {} is malformed and was skipped: {}", id, e.toString());
                    }
                });
                landmarks = out;
            } else {
                Map<ResourceLocation, Roster> out = new HashMap<>();
                files.forEach((id, json) -> {
                    try {
                        out.put(id, Roster.parse(id, json.getAsJsonObject()));
                    } catch (Exception e) {
                        UnstableFrontiers.LOGGER.error("Roster {} is malformed and was skipped: {}", id, e.toString());
                    }
                });
                rosters = out;
                // Rosters load after landmarks (listeners run in the order added), so both are current here.
                validate();
            }
        }
    }

    private static void validate() {
        List<String> found = new ArrayList<>();
        for (LandmarkDef def : landmarks.values()) {
            for (LandmarkDef.Zone z : def.zones()) {
                found.addAll(check(def, z.roster()));
            }
            for (LandmarkDef.Resident r : def.residents()) {
                found.addAll(check(def, r.roster()));
            }
        }
        problems = List.copyOf(found.stream().distinct().toList());
        for (String p : problems) {
            UnstableFrontiers.LOGGER.error("Unstable Frontiers: {}", p);
        }
        UnstableFrontiers.LOGGER.info("Unstable Frontiers data: {} landmarks, {} rosters, {} problems", landmarks.size(), rosters.size(),
                problems.size());
    }

    private static List<String> check(LandmarkDef def, String name) {
        if (name == null || name.isEmpty()) {
            return List.of();
        }
        Roster r = roster(name);
        if (r == null) {
            return List.of("landmark " + def.id() + " names roster '" + name + "', but data/unstable_frontiers/roster/" + name
                    + ".json does not exist. Restore the mod's data or remove the datapack that overrides it.");
        }
        List<String> out = new ArrayList<>();
        for (ResourceLocation m : r.missing()) {
            out.add("roster '" + name + "' needs " + m + ", which is not registered. " + hint(m.getNamespace()));
        }
        return out;
    }

    private static String hint(String namespace) {
        if (namespace.equals("antarchy")) {
            return ModList.get().isLoaded("antarchy")
                    ? "Antarchy " + ModList.get().getModContainerById("antarchy").map(c -> c.getModInfo().getVersion().toString()).orElse("?")
                            + " is installed but lacks it; this addon targets Antarchy 2.2.9+1.21.1 as shipped in Integrated Boogaloo 1.0.8."
                    : "Install Antarchy 2.2.9+1.21.1 (it ships with Integrated Boogaloo 1.0.8).";
        }
        return "Install the mod '" + namespace + "' or edit the roster in a datapack.";
    }

    @Nullable
    public static LandmarkDef landmark(ResourceLocation id) {
        return landmarks.get(id);
    }

    public static Map<ResourceLocation, LandmarkDef> landmarks() {
        return landmarks;
    }

    /** A roster by short name (unstable_frontiers namespace) or full id. */
    @Nullable
    public static Roster roster(String name) {
        ResourceLocation id = name.contains(":") ? ResourceLocation.parse(name) : UnstableFrontiers.id(name);
        return rosters.get(id);
    }

    public static Map<ResourceLocation, Roster> rosters() {
        return rosters;
    }

    public static List<String> problems() {
        return problems;
    }
}
