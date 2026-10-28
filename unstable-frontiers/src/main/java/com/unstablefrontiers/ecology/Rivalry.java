package com.unstablefrontiers.ecology;

import com.unstablefrontiers.config.FrontierConfig;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import javax.annotation.Nullable;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;

/**
 * The one deliberate rivalry of this milestone: flying predators (entity tag unstable_frontiers:raptors) hunt ground
 * insects (unstable_frontiers:swarm). It only ever involves wild creatures this mod spawned, never the player's pets,
 * Antarchy's bosses or anything else, and it never replaces a creature's AI: a predator with no target is simply handed
 * the nearest prey, and the prey's own retaliation does the rest.
 *
 * <p>Bounded everywhere: updates run every aiUpdateIntervalTicks; each looks in boxes of rivalrySearchRadius around
 * players only; each player has at most rivalryFightsPerPlayer fights; a fight ends after pursuitTicks or when the two
 * drift apart, and the predator then rests for rivalryCooldownTicks. Creatures in unloaded chunks do not tick, so no
 * fight runs off-screen.
 */
public final class Rivalry {
    private record Fight(UUID prey, long start) {}

    private static final Map<UUID, Fight> FIGHTS = new HashMap<>();
    private static final Map<UUID, Long> RESTING = new HashMap<>();

    private Rivalry() {}

    public static void tick(ServerLevel level, long time) {
        if (time % FrontierConfig.aiInterval() != 0) {
            return;
        }
        int radius = FrontierConfig.rivalryRadius();
        maintain(level, time, radius);
        int perPlayer = FrontierConfig.fightsPerPlayer();
        for (ServerPlayer p : level.players()) {
            if (p.isSpectator() || perPlayer <= 0) {
                continue;
            }
            int active = fightsNear(level, p, radius * 2.0D);
            if (active >= perPlayer) {
                continue;
            }
            List<Mob> hunters = level.getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(radius * 2.0D, radius, radius * 2.0D),
                    m -> m.isAlive() && Creatures.isAmbient(m) && m.getType().is(Creatures.RAPTORS) && m.getTarget() == null
                            && !FIGHTS.containsKey(m.getUUID()) && RESTING.getOrDefault(m.getUUID(), 0L) <= time);
            for (Mob hunter : hunters) {
                if (active >= perPlayer) {
                    break;
                }
                Mob prey = nearestPrey(level, hunter, radius);
                if (prey == null) {
                    continue;
                }
                hunter.setTarget(prey);
                if (prey.getTarget() == null) {
                    prey.setTarget(hunter);
                }
                FIGHTS.put(hunter.getUUID(), new Fight(prey.getUUID(), time));
                active++;
            }
        }
    }

    private static void maintain(ServerLevel level, long time, int radius) {
        double apart = radius * 1.5D;
        Iterator<Map.Entry<UUID, Fight>> it = FIGHTS.entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<UUID, Fight> f = it.next();
            Entity a = level.getEntity(f.getKey());
            Entity b = level.getEntity(f.getValue().prey());
            boolean over = !(a instanceof Mob hunter) || !hunter.isAlive() || !(b instanceof LivingEntity prey) || !prey.isAlive()
                    || time - f.getValue().start() > FrontierConfig.PURSUIT_TICKS.get() || a.distanceToSqr(b) > apart * apart;
            if (!over) {
                continue;
            }
            if (a instanceof Mob hunter && hunter.getTarget() == b) {
                hunter.setTarget(null);
            }
            if (b instanceof Mob preyMob && preyMob.getTarget() == a) {
                preyMob.setTarget(null);
            }
            RESTING.put(f.getKey(), time + FrontierConfig.RIVALRY_COOLDOWN.get());
            it.remove();
        }
        RESTING.values().removeIf(until -> until <= time);
    }

    private static int fightsNear(ServerLevel level, ServerPlayer p, double radius) {
        int n = 0;
        for (UUID hunter : FIGHTS.keySet()) {
            Entity e = level.getEntity(hunter);
            if (e != null && e.distanceToSqr(p) <= radius * radius) {
                n++;
            }
        }
        return n;
    }

    @Nullable
    private static Mob nearestPrey(ServerLevel level, Mob hunter, int radius) {
        Mob best = null;
        double bestD = Double.MAX_VALUE;
        for (Mob m : level.getEntitiesOfClass(Mob.class, hunter.getBoundingBox().inflate(radius),
                m -> m.isAlive() && Creatures.isAmbient(m) && m.getType().is(Creatures.SWARM))) {
            double d = m.distanceToSqr(hunter);
            if (d < bestD) {
                bestD = d;
                best = m;
            }
        }
        return best;
    }

    public static int fightCount() {
        return FIGHTS.size();
    }

    public static void clearMemory() {
        FIGHTS.clear();
        RESTING.clear();
    }
}
