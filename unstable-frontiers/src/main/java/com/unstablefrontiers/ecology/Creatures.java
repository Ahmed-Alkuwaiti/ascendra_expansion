package com.unstablefrontiers.ecology;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.config.FrontierConfig;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.function.Supplier;
import javax.annotation.Nullable;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.event.EventHooks;

/**
 * Rosters, roles and spawning shared by the towers and the wild. Only creatures this mod spawns carry a role; nothing
 * here touches any other creature, and no creature's own AI is replaced.
 */
public final class Creatures {
    public static final String ROLE = "uf_role";
    public static final String ROLE_ENCOUNTER = "encounter";
    public static final String ROLE_AMBIENT = "ambient";
    public static final String TOWER = "uf_tower";
    public static final String SESSION = "uf_session";

    public static final TagKey<EntityType<?>> SWARM = TagKey.create(Registries.ENTITY_TYPE, UnstableFrontiers.id("swarm"));
    public static final TagKey<EntityType<?>> RAPTORS = TagKey.create(Registries.ENTITY_TYPE, UnstableFrontiers.id("raptors"));
    public static final TagKey<EntityType<?>> INSECTS = TagKey.create(Registries.ENTITY_TYPE, UnstableFrontiers.id("frontier_insects"));

    private static final Set<String> WARNED = new HashSet<>();

    /** One roster line: a creature and the most of it allowed in one wave or group (0 = no limit). */
    public record Entry(EntityType<?> type, int max) {}

    private Creatures() {}

    public static List<Entry> roster(Supplier<List<? extends String>> primary, Supplier<List<? extends String>> fallback) {
        List<? extends String> lines = UnstableFrontiers.antarchyLoaded() ? primary.get() : fallback.get();
        List<Entry> out = new ArrayList<>();
        for (String line : lines) {
            String id = line;
            int max = 0;
            int at = line.indexOf('@');
            if (at > 0) {
                id = line.substring(0, at);
                max = Integer.parseInt(line.substring(at + 1));
            }
            ResourceLocation rl = ResourceLocation.tryParse(id);
            // The entity registry answers unknown ids with its default (the pig), so check the key first.
            if (rl == null || !BuiltInRegistries.ENTITY_TYPE.containsKey(rl)) {
                if (WARNED.add(id)) {
                    UnstableFrontiers.LOGGER.warn("Roster entry '{}' is not a registered entity; skipping it", id);
                }
                continue;
            }
            out.add(new Entry(BuiltInRegistries.ENTITY_TYPE.get(rl), max));
        }
        return out;
    }

    /** Picks up to n creatures from a roster, honouring each entry's per-wave limit. */
    public static List<EntityType<?>> pick(List<Entry> roster, int n, RandomSource random) {
        List<EntityType<?>> out = new ArrayList<>();
        int[] used = new int[roster.size()];
        for (int i = 0; i < n; i++) {
            List<Integer> open = new ArrayList<>();
            for (int j = 0; j < roster.size(); j++) {
                if (roster.get(j).max() == 0 || used[j] < roster.get(j).max()) {
                    open.add(j);
                }
            }
            if (open.isEmpty()) {
                break;
            }
            int j = open.get(random.nextInt(open.size()));
            used[j]++;
            out.add(roster.get(j).type());
        }
        return out;
    }

    public static String role(Entity e) {
        return e.getPersistentData().getString(ROLE);
    }

    public static boolean isAmbient(Entity e) {
        return ROLE_AMBIENT.equals(role(e));
    }

    public static boolean isEncounter(Entity e) {
        return ROLE_ENCOUNTER.equals(role(e));
    }

    public static boolean isOurs(Entity e) {
        return !role(e).isEmpty();
    }

    /**
     * Creates a creature at a spot, or returns null if it would not fit there. The creature is not yet in the world; the
     * caller tags it and adds it.
     */
    @Nullable
    public static Mob create(ServerLevel level, EntityType<?> type, Vec3 at) {
        Entity e = type.create(level);
        if (!(e instanceof Mob mob)) {
            if (e != null) {
                e.discard();
            }
            return null;
        }
        mob.moveTo(at.x, at.y, at.z, level.random.nextFloat() * 360.0F, 0.0F);
        if (!level.noCollision(mob) || level.containsAnyLiquid(mob.getBoundingBox())) {
            mob.discard();
            return null;
        }
        EventHooks.finalizeMobSpawn(mob, level, level.getCurrentDifficultyAt(mob.blockPosition()), MobSpawnType.EVENT, null);
        return mob;
    }

    public static void tagAmbient(Mob mob) {
        mob.getPersistentData().putString(ROLE, ROLE_AMBIENT);
    }

    public static void tagEncounter(Mob mob, long tower, int session) {
        CompoundTag d = mob.getPersistentData();
        d.putString(ROLE, ROLE_ENCOUNTER);
        d.putLong(TOWER, tower);
        d.putInt(SESSION, session);
        mob.setPersistenceRequired();
    }

    public static boolean flies(Mob mob) {
        return mob.getType().is(RAPTORS) || mob.isNoGravity();
    }

    public static int particles(int base) {
        return FrontierConfig.particleCount(base);
    }
}
