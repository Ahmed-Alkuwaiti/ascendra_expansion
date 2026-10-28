package com.unstablefrontiers.ecology;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.config.FrontierConfig;
import javax.annotation.Nullable;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.event.EventHooks;

/**
 * Roles and spawning shared by landmark fights and residents. Only creatures this mod spawns carry a role; nothing
 * here touches any other creature, and no creature's own AI is replaced.
 */
public final class Creatures {
    public static final String ROLE = "uf_role";
    public static final String ROLE_ENCOUNTER = "encounter";
    public static final String ROLE_RESIDENT = "resident";
    public static final String ROLE_BOUND = "bound";
    public static final String LANDMARK = "uf_landmark";
    public static final String ZONE = "uf_zone";
    public static final String SESSION = "uf_session";
    public static final String DORMANT = "uf_dormant";
    public static final String SIDE = "uf_side";

    public static final TagKey<EntityType<?>> SWARM = TagKey.create(Registries.ENTITY_TYPE, UnstableFrontiers.id("swarm"));
    public static final TagKey<EntityType<?>> RAPTORS = TagKey.create(Registries.ENTITY_TYPE, UnstableFrontiers.id("raptors"));
    public static final TagKey<EntityType<?>> INSECTS = TagKey.create(Registries.ENTITY_TYPE, UnstableFrontiers.id("frontier_insects"));

    private Creatures() {}

    public static String role(Entity e) {
        return e.getPersistentData().getString(ROLE);
    }

    public static boolean isResident(Entity e) {
        return ROLE_RESIDENT.equals(role(e));
    }

    public static boolean isEncounter(Entity e) {
        return ROLE_ENCOUNTER.equals(role(e));
    }

    public static boolean isOurs(Entity e) {
        return !role(e).isEmpty();
    }

    /**
     * Creates a creature at a spot, or returns null if it would not fit there (unless forced). The creature is not yet in the world; the
     * caller tags it and adds it.
     */
    @Nullable
    public static Mob create(ServerLevel level, EntityType<?> type, Vec3 at, boolean force) {
        Entity e = type.create(level);
        if (!(e instanceof Mob mob)) {
            if (e != null) {
                e.discard();
            }
            return null;
        }
        mob.moveTo(at.x, at.y, at.z, level.random.nextFloat() * 360.0F, 0.0F);
        if (!force && (!level.noCollision(mob) || level.containsAnyLiquid(mob.getBoundingBox()))) {
            mob.discard();
            return null;
        }
        EventHooks.finalizeMobSpawn(mob, level, level.getCurrentDifficultyAt(mob.blockPosition()), MobSpawnType.EVENT, null);
        return mob;
    }

    /** A creature that lives at a landmark: side is "hunter", "prey" or empty (no rivalry). */
    public static void tagResident(Mob mob, long landmark, String side) {
        CompoundTag d = mob.getPersistentData();
        d.putString(ROLE, ROLE_RESIDENT);
        d.putLong(LANDMARK, landmark);
        d.putString(SIDE, side);
        mob.setPersistenceRequired();
    }

    public static void tagEncounter(Mob mob, long landmark, int zone, int session) {
        CompoundTag d = mob.getPersistentData();
        d.putString(ROLE, ROLE_ENCOUNTER);
        d.putLong(LANDMARK, landmark);
        d.putInt(ZONE, zone);
        d.putInt(SESSION, session);
        mob.setPersistenceRequired();
    }

    public static long landmark(Entity e) {
        return e.getPersistentData().getLong(LANDMARK);
    }

    public static int zone(Entity e) {
        return e.getPersistentData().getInt(ZONE);
    }

    public static int session(Entity e) {
        return e.getPersistentData().getInt(SESSION);
    }

    public static String side(Entity e) {
        return e.getPersistentData().getString(SIDE);
    }

    /** Dormant: placed visibly (a caged prisoner, a roosting flyer) but without AI until its fight starts or it is struck. */
    public static void setDormant(Mob mob, boolean dormant) {
        mob.setNoAi(dormant);
        if (dormant) {
            mob.getPersistentData().putBoolean(DORMANT, true);
        } else {
            mob.getPersistentData().remove(DORMANT);
        }
    }

    public static boolean isDormant(Entity e) {
        return e.getPersistentData().getBoolean(DORMANT);
    }

    public static boolean flies(Mob mob) {
        return mob.getType().is(RAPTORS) || mob.isNoGravity() || mob instanceof net.minecraft.world.entity.FlyingMob;
    }

    public static int particles(int base) {
        return FrontierConfig.particleCount(base);
    }
}
