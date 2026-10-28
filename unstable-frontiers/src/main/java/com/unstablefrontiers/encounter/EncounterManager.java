package com.unstablefrontiers.encounter;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.ecology.Creatures;
import com.unstablefrontiers.ecology.Rosters;
import com.unstablefrontiers.world.TowerBlueprint;
import com.unstablefrontiers.world.TowerLocator;
import com.unstablefrontiers.world.TowerRef;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import javax.annotation.Nullable;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;

/**
 * Runs the tower fights, server side only.
 *
 * <p>A stage (one of the three cage floors, or the crown) wakes when a player steps inside it and it is not yet cleared.
 * Only one stage per tower fights at a time, however many players arrive, and the server-wide number of fighting towers
 * is capped. A stage sends a fixed number of waves; each wave is limited by the per-player and per-tower caps, and the
 * next one waits for both the cooldown and for the floor to thin out. The stage is cleared when every wave has come and
 * every creature in it is dead. Clearing all four stages completes the tower and rewards the players who fought there,
 * once each, recorded in {@link TowerState#rewarded}.
 *
 * <p>If nobody is near for {@code disengageTicks}, the unfinished stage resets: its creatures are removed (loaded ones at
 * once, unloaded ones when their chunk loads, by session number) and floors already cleared stay cleared. Nothing spawns
 * while no player is near, so a fight never runs on with nobody watching.
 */
public final class EncounterManager {
    private static final int SCAN_INTERVAL = 20;
    private static final int STAGE_INTERVAL = 10;
    private static final int MISSING_TIMEOUT = 600;
    private static final double NEAR_VERTICAL = 48.0D;

    /** When each tracked creature was last found loaded; memory only, rebuilt after a restart. */
    private static final Map<UUID, Long> LAST_SEEN = new HashMap<>();
    /** Towers started from a command: they may spawn with no player near (for testing), and still reset when idle. */
    private static final Set<Long> FORCED = new HashSet<>();
    private static final Set<String> EMPTY_WARNED = new HashSet<>();
    private static final Map<Long, Integer> FAILS = new HashMap<>();

    private EncounterManager() {}

    public static void tick(ServerLevel level) {
        long time = level.getGameTime();
        TowerData data = TowerData.get(level);
        for (ServerPlayer p : level.players()) {
            if (p.isSpectator() || (time + p.getId()) % SCAN_INTERVAL != 0) {
                continue;
            }
            TowerRef ref = TowerLocator.at(level, p.blockPosition(), false);
            if (ref != null) {
                playerAtTower(level, data, ref, p, time);
            }
        }
        if (time % STAGE_INTERVAL == 0) {
            for (TowerState s : data.active()) {
                tickStage(level, data, s, time);
            }
        }
    }

    private static void playerAtTower(ServerLevel level, TowerData data, TowerRef ref, ServerPlayer p, long time) {
        TowerState s = data.getOrCreate(ref);
        if (s.completed) {
            return;
        }
        if (s.activeStage >= 0) {
            if (s.participants.add(p.getUUID())) {
                data.setDirty();
            }
            return;
        }
        int stage = TowerBlueprint.stageAt(ref.localX(p.getX()), ref.localY(p.getY()), ref.localZ(p.getZ()));
        if (stage < 0 || s.isCleared(stage) || p.isCreative()) {
            return;
        }
        if (data.active().size() >= FrontierConfig.activeTowers()) {
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.tower_busy"), true);
            return;
        }
        s.participants.add(p.getUUID());
        start(level, data, s, stage, time, false);
    }

    /** Wakes a stage. Used by players stepping in and by the debug command (forced). */
    public static void start(ServerLevel level, TowerData data, TowerState s, int stage, long time, boolean forced) {
        removeCreatures(level, s);
        s.activeStage = stage;
        s.session++;
        s.wave = 0;
        s.nextWaveTime = time + 40;
        s.lastPresence = time;
        if (forced) {
            FORCED.add(s.ref.id());
        } else {
            FORCED.remove(s.ref.id());
        }
        data.setDirty();
        Vec3 c = s.ref.stageCentre(stage);
        level.playSound(null, c.x, c.y, c.z, stage == 3 ? SoundEvents.RAVAGER_ROAR : SoundEvents.CHAIN_BREAK, SoundSource.HOSTILE, 3.0F, 0.6F);
        level.sendParticles(ParticleTypes.LARGE_SMOKE, c.x, c.y + 1, c.z, Creatures.particles(30), 4.0D, 1.0D, 4.0D, 0.02D);
        announce(level, c, Component.translatable("message.unstable_frontiers.stage_wakes", stageName(stage)));
        UnstableFrontiers.LOGGER.debug("Tower {} stage {} woke (session {})", s.ref.id(), stage, s.session);
    }

    private static void tickStage(ServerLevel level, TowerData data, TowerState s, long time) {
        int stage = s.activeStage;
        Vec3 c = s.ref.stageCentre(stage);
        double leash = FrontierConfig.LEASH_RADIUS.get();
        List<ServerPlayer> near = playersNear(level, c, leash + 8);
        if (!near.isEmpty()) {
            s.lastPresence = time;
            for (ServerPlayer p : near) {
                if (s.participants.add(p.getUUID())) {
                    data.setDirty();
                }
            }
        }
        if (time - s.lastPresence > FrontierConfig.DISENGAGE_TICKS.get()) {
            UnstableFrontiers.LOGGER.debug("Tower {} stage {} reset: nobody near", s.ref.id(), stage);
            abandon(level, data, s);
            return;
        }

        List<ServerPlayer> targets = new ArrayList<>();
        for (ServerPlayer p : near) {
            if (!p.isCreative()) {
                targets.add(p);
            }
        }
        Iterator<UUID> it = s.alive.iterator();
        while (it.hasNext()) {
            UUID u = it.next();
            Entity e = level.getEntity(u);
            if (e == null) {
                // Unloaded, or removed by something else. Give up on it after a while if players are here to see.
                long seen = LAST_SEEN.computeIfAbsent(u, k -> time);
                if (!near.isEmpty() && time - seen > MISSING_TIMEOUT) {
                    it.remove();
                    LAST_SEEN.remove(u);
                    data.setDirty();
                }
                continue;
            }
            LAST_SEEN.put(u, time);
            if (!e.isAlive()) {
                it.remove();
                LAST_SEEN.remove(u);
                data.setDirty();
                continue;
            }
            if (e instanceof Mob m) {
                leash(m, c, leash, targets);
            }
        }

        boolean mayspawn = !near.isEmpty() || FORCED.contains(s.ref.id());
        int waves = stage == 3 ? 1 : FrontierConfig.wavesPerFloor();
        int thin = Math.max(1, FrontierConfig.mobsPerWave() / 2);
        if (s.wave < waves && mayspawn && time >= s.nextWaveTime && s.alive.size() <= thin) {
            boolean done = spawnWave(level, data, s, Math.max(1, near.size()), targets);
            int fails = done ? 0 : FAILS.merge(s.ref.id(), 1, Integer::sum);
            if (done || fails >= 5) {
                // A wave that cannot be placed five times running (floor blocked up) is skipped rather than stalling the stage.
                FAILS.remove(s.ref.id());
                s.wave++;
                s.nextWaveTime = time + FrontierConfig.waveCooldown();
            } else {
                s.nextWaveTime = time + 100;
            }
            data.setDirty();
        }
        if (s.wave >= waves && s.alive.isEmpty()) {
            clearStage(level, data, s, near);
        }
    }

    /** A short pursuit: past the leash the creature drops its target and walks home; far past it, it is put back. */
    private static void leash(Mob m, Vec3 c, double leash, List<ServerPlayer> targets) {
        double dx = m.getX() - c.x;
        double dz = m.getZ() - c.z;
        double d2 = dx * dx + dz * dz;
        double dy = Math.abs(m.getY() - c.y);
        if (d2 > leash * leash || dy > 40) {
            m.setTarget(null);
            if (d2 > leash * leash * 2.25D || dy > 60) {
                m.teleportTo(c.x, c.y, c.z);
            } else {
                m.getNavigation().moveTo(c.x, c.y, c.z, 1.0D);
            }
        } else if (m.getTarget() == null && !targets.isEmpty()) {
            m.setTarget(nearest(targets, m));
        }
    }

    /** Spawns one wave; false if nothing could be placed (no room under the caps, or every spot blocked). */
    private static boolean spawnWave(ServerLevel level, TowerData data, TowerState s, int players, List<ServerPlayer> targets) {
        int stage = s.activeStage;
        int cap = Math.min(FrontierConfig.encounterPerTower(), FrontierConfig.encounterPerPlayer() * players);
        int room = cap - s.alive.size();
        if (room <= 0) {
            return false;
        }
        List<EntityType<?>> types;
        if (stage == 3) {
            types = new ArrayList<>(Creatures.pick(Rosters.stage(3), room, level.random));
            types.addAll(Creatures.pick(Rosters.crownEscorts(), Math.max(0, room - types.size()), level.random));
        } else {
            int n = Math.min(room, FrontierConfig.mobsPerWave() + players - 1);
            types = Creatures.pick(Rosters.stage(stage), n, level.random);
        }
        if (types.isEmpty()) {
            if (EMPTY_WARNED.add("stage" + stage)) {
                UnstableFrontiers.LOGGER.warn("Tower stage {} has no usable creatures in its roster; it will clear without a fight", TowerBlueprint.STAGE_NAMES[stage]);
            }
            return true;
        }
        int[][] spots = stage == 3 ? TowerBlueprint.CROWN_SPAWNS : TowerBlueprint.FLOOR_SPAWNS;
        List<int[]> order = new ArrayList<>(List.of(spots));
        Collections.shuffle(order, new java.util.Random(level.random.nextLong()));
        int fy = s.ref.baseY() + TowerBlueprint.stageFloor(stage) + 1;
        int next = 0;
        int placed = 0;
        for (EntityType<?> type : types) {
            Mob mob = null;
            for (int tries = 0; tries < order.size() && mob == null; tries++) {
                int[] o = order.get(next++ % order.size());
                double x = s.ref.originX() + TowerBlueprint.C + o[0] + 0.5D;
                double z = s.ref.originZ() + TowerBlueprint.C + o[1] + 0.5D;
                mob = Creatures.create(level, type, new Vec3(x, fy, z));
                if (mob != null && Creatures.flies(mob)) {
                    mob.moveTo(x, fy + 3, z);
                }
            }
            if (mob == null) {
                continue;
            }
            Creatures.tagEncounter(mob, s.ref.id(), s.session);
            if (!targets.isEmpty()) {
                mob.setTarget(nearest(targets, mob));
            }
            s.alive.add(mob.getUUID());
            if (!level.addFreshEntity(mob)) {
                s.alive.remove(mob.getUUID());
                continue;
            }
            placed++;
            level.sendParticles(ParticleTypes.LARGE_SMOKE, mob.getX(), mob.getY() + 1, mob.getZ(), Creatures.particles(8), 0.5D, 0.5D, 0.5D, 0.02D);
        }
        data.setDirty();
        return placed > 0;
    }

    private static void clearStage(ServerLevel level, TowerData data, TowerState s, List<ServerPlayer> near) {
        int stage = s.activeStage;
        s.cleared |= 1 << stage;
        s.activeStage = -1;
        s.wave = 0;
        FORCED.remove(s.ref.id());
        data.setDirty();
        Vec3 c = s.ref.stageCentre(stage);
        level.playSound(null, c.x, c.y, c.z, SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.PLAYERS, 1.0F, 1.0F);
        announce(level, c, Component.translatable("message.unstable_frontiers.stage_cleared", stageName(stage)));
        UnstableFrontiers.LOGGER.debug("Tower {} stage {} cleared", s.ref.id(), stage);
        if (s.allCleared() && !s.completed) {
            s.completed = true;
            Rewards.completeTower(level, s);
            UnstableFrontiers.LOGGER.info("Cage tower at {} {} completed", s.ref.originX() + TowerBlueprint.C, s.ref.originZ() + TowerBlueprint.C);
        }
    }

    /** Ends the unfinished stage without clearing it. Cleared stages, completion and rewards are untouched. */
    public static void abandon(ServerLevel level, TowerData data, TowerState s) {
        removeCreatures(level, s);
        s.activeStage = -1;
        s.wave = 0;
        s.session++;
        FORCED.remove(s.ref.id());
        data.setDirty();
    }

    /** Debug: forget every cleared floor and completion, keep the record of who was rewarded. */
    public static void reset(ServerLevel level, TowerData data, TowerState s) {
        abandon(level, data, s);
        s.cleared = 0;
        s.completed = false;
        s.participants.clear();
        data.setDirty();
    }

    private static void removeCreatures(ServerLevel level, TowerState s) {
        for (UUID u : s.alive) {
            Entity e = level.getEntity(u);
            if (e != null) {
                e.discard();
            }
            LAST_SEEN.remove(u);
        }
        s.alive.clear();
    }

    /** Called when a tracked creature dies. */
    public static void onDeath(ServerLevel level, Entity e) {
        TowerData data = TowerData.get(level);
        TowerState s = data.get(e.getPersistentData().getLong(Creatures.TOWER));
        if (s != null && s.alive.remove(e.getUUID())) {
            LAST_SEEN.remove(e.getUUID());
            data.setDirty();
        }
    }

    /** Whether a tower creature loading back into the world still belongs to a running fight. */
    public static boolean belongs(ServerLevel level, Entity e) {
        TowerState s = TowerData.get(level).get(e.getPersistentData().getLong(Creatures.TOWER));
        return s != null && s.activeStage >= 0 && s.session == e.getPersistentData().getInt(Creatures.SESSION) && s.alive.contains(e.getUUID());
    }

    public static void clearMemory() {
        LAST_SEEN.clear();
        FORCED.clear();
        FAILS.clear();
    }

    /** Whether any stage is fighting, so a forced test fight keeps running with no player in the dimension. */
    public static boolean anyActive(ServerLevel level) {
        return !FORCED.isEmpty() || !TowerData.get(level).active().isEmpty();
    }

    public static int trackedCount(TowerData data) {
        int n = 0;
        for (TowerState s : data.all()) {
            n += s.alive.size();
        }
        return n;
    }

    public static Component stageName(int stage) {
        return Component.translatable("stage.unstable_frontiers." + TowerBlueprint.STAGE_NAMES[stage]);
    }

    static List<ServerPlayer> playersNear(ServerLevel level, Vec3 c, double radius) {
        List<ServerPlayer> out = new ArrayList<>();
        for (ServerPlayer p : level.players()) {
            if (p.isSpectator() || !p.isAlive()) {
                continue;
            }
            double dx = p.getX() - c.x;
            double dz = p.getZ() - c.z;
            if (dx * dx + dz * dz <= radius * radius && Math.abs(p.getY() - c.y) <= NEAR_VERTICAL) {
                out.add(p);
            }
        }
        return out;
    }

    private static void announce(ServerLevel level, Vec3 c, Component message) {
        for (ServerPlayer p : playersNear(level, c, 64)) {
            p.displayClientMessage(message, true);
        }
    }

    @Nullable
    private static ServerPlayer nearest(List<ServerPlayer> players, Entity e) {
        ServerPlayer best = null;
        double bestD = Double.MAX_VALUE;
        for (ServerPlayer p : players) {
            double d = p.distanceToSqr(e);
            if (d < bestD) {
                bestD = d;
                best = p;
            }
        }
        return best;
    }
}
