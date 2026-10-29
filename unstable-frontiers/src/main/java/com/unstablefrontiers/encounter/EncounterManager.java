package com.unstablefrontiers.encounter;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.ecology.Creatures;
import com.unstablefrontiers.ecology.Roster;
import com.unstablefrontiers.landmark.FrontierData;
import com.unstablefrontiers.landmark.LandmarkDef;
import com.unstablefrontiers.landmark.LandmarkDef.Kind;
import com.unstablefrontiers.landmark.LandmarkDef.Zone;
import com.unstablefrontiers.registry.ModSounds;
import com.unstablefrontiers.world.LandmarkLocator;
import com.unstablefrontiers.world.LandmarkPiece;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.BossEvent;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * Runs every landmark fight. All state lives in {@link LandmarkData}; this class only acts on landmarks with a player
 * within {@link #AWAKE} blocks, and every search it makes is a box around one landmark. Per kind:
 * <ul>
 * <li>WAVES: waves come while waves remain, each when the last is mostly down and the cooldown has passed.</li>
 * <li>BROOD: like waves, but every wave hatches from the egg clutches still whole; smash them and the waves stop.</li>
 * <li>AMBUSH: one burst from hiding (and from the zone's release points) the moment you cross the trigger.</li>
 * <li>CELL / ROOST: the prisoners or roosting flyers are already there, dormant and visible; they wake when you step into
 * the zone or strike one.</li>
 * <li>GUARDIAN: an elite with escorts, a boss bar and telegraphed abilities. Opens the landmark's gate when it falls.</li>
 * <li>FINALE: started by the Cagewright's Key at the lock; the beast is shielded while its pylons stand.</li>
 * <li>TERRITORY: no fight; residents live here (see {@link com.unstablefrontiers.ecology.Rivalry}).</li>
 * </ul>
 * A fight nobody is near for disengageTicks resets: its creatures are removed and it can be tried again. Rosters that
 * cannot be resolved stop the fight from starting and say why, in chat and in the log; nothing is substituted.
 */
public final class EncounterManager {
    public static final int AWAKE = 48;
    private static final Map<String, ServerBossEvent> BARS = new HashMap<>();

    private EncounterManager() {}

    public static LandmarkData data(ServerLevel level) {
        return LandmarkData.get(level);
    }

    // ------------------------------------------------------------------------------------------------------- the tick
    public static void tick(ServerLevel level) {
        long t = level.getGameTime();
        LandmarkData data = data(level);
        if (t % 40 == 0) {
            discover(level, data);
        }
        if (t % 10 != 0) {
            return;
        }
        for (LandmarkState s : data.all()) {
            LandmarkDef def = FrontierData.landmark(s.id);
            if (def == null || !level.isLoaded(s.centre(def))) {
                continue;
            }
            BoundingBox bounds = s.bounds(def);
            List<ServerPlayer> near = players(level, bounds, AWAKE);
            boolean anyActive = false;
            for (Zone z : def.zones()) {
                anyActive |= s.zone(z).status == ZoneState.Status.ACTIVE;
            }
            if (near.isEmpty() && !anyActive) {
                continue;
            }
            if (!near.isEmpty()) {
                welcome(level, s, def, players(level, bounds, 6));
                wake(level, s, def, t);
            }
            for (Zone z : def.zones()) {
                tickZone(level, data, s, def, z, s.zone(z), t);
            }
        }
    }

    /** Registers the landmarks around each player from the structure references of loaded chunks. */
    private static void discover(ServerLevel level, LandmarkData data) {
        for (ServerPlayer p : level.players()) {
            if (p.isSpectator()) {
                continue;
            }
            for (LandmarkPiece piece : LandmarkLocator.near(level, p.blockPosition(), 2)) {
                if (data.get(piece.origin().asLong()) == null && FrontierData.landmark(piece.templateId()) != null) {
                    data.add(new LandmarkState(piece.templateId(), piece.origin(), piece.rotation()));
                }
            }
        }
    }

    /** First steps into a landmark: its name, once per player. */
    private static void welcome(ServerLevel level, LandmarkState s, LandmarkDef def, List<ServerPlayer> inside) {
        List<ServerPlayer> fresh = new ArrayList<>();
        for (ServerPlayer p : inside) {
            if (s.visitors.add(p.getUUID())) {
                fresh.add(p);
            }
        }
        if (fresh.isEmpty() || def.kind().equals("wayside")) {
            return;
        }
        data(level).setDirty();
        Feedback.title(fresh, Component.literal(def.title()).withStyle(ChatFormatting.DARK_RED),
                Component.translatable("landmark.unstable_frontiers." + def.kind() + ".subtitle").withStyle(ChatFormatting.GRAY));
        Feedback.sound(level, fresh.get(0).blockPosition(), ModSounds.DISCOVER.get(), 1.0F, 1.0F);
    }

    /** A player is near: place dormant prisoners and roosting flyers, and move residents in. */
    private static void wake(ServerLevel level, LandmarkState s, LandmarkDef def, long t) {
        for (Zone z : def.zones()) {
            ZoneState zs = s.zone(z);
            if ((z.kind() == Kind.CELL || z.kind() == Kind.ROOST) && zs.status == ZoneState.Status.IDLE && !zs.dormantPlaced) {
                Roster r = usable(z.roster());
                if (r != null) {
                    zs.session++;
                    zs.dormantPlaced = true;      // before spawning: the join check admits dormant creatures only once placed
                    spawnGroup(level, s, z, zs, r, true);
                    data(level).setDirty();
                }
            }
            if (z.kind() == Kind.FINALE && zs.status == ZoneState.Status.IDLE && !zs.dormantPlaced && requirementsMet(s, def, z)) {
                // the beast is visible in its cage before the fight, struggling in its chains
                Roster r = usable(z.roster());
                if (r != null && r.elite() != null) {
                    zs.session++;
                    zs.dormantPlaced = true;
                    Elites.spawnElite(level, s, z, zs, r, null, true);
                    data(level).setDirty();
                }
            }
        }
        if (!def.residents().isEmpty()) {
            pruneResidents(level, s);
            if (s.residents.isEmpty() && (s.residentsAt == Long.MIN_VALUE || t - s.residentsAt >= FrontierConfig.RESIDENT_RESPAWN.get())
                    && !CageBeacons.covers(level, s.centre(def))) {
                spawnResidents(level, s, def);
                s.residentsAt = t;
                data(level).setDirty();
            }
        }
    }

    private static void tickZone(ServerLevel level, LandmarkData data, LandmarkState s, LandmarkDef def, Zone z, ZoneState zs, long t) {
        if (z.kind() == Kind.TERRITORY || zs.status == ZoneState.Status.CLEARED) {
            return;
        }
        BoundingBox box = s.world(z.box());
        if (zs.status == ZoneState.Status.IDLE) {
            List<ServerPlayer> inTrigger = players(level, s.world(z.trigger()), 0);
            if (inTrigger.isEmpty()) {
                return;
            }
            if (!requirementsMet(s, def, z)) {
                hint(zs, t, inTrigger, Component.translatable("message.unstable_frontiers.sealed", z.name(), progress(s, def, z))
                        .withStyle(ChatFormatting.GOLD));
                return;
            }
            if (z.kind() == Kind.FINALE) {
                hint(zs, t, inTrigger, Component.translatable("message.unstable_frontiers.finale_locked").withStyle(ChatFormatting.GOLD));
                return;
            }
            start(level, s, def, z, zs, inTrigger, t);
            return;
        }
        // ACTIVE
        prune(level, zs);
        for (ServerPlayer p : players(level, box, 4)) {
            if (zs.participants.add(p.getUUID())) {
                data.setDirty();
            }
        }
        List<ServerPlayer> engaged = players(level, box, 24);
        if (!engaged.isEmpty()) {
            zs.lastEngaged = t;
        } else if (t - zs.lastEngaged > FrontierConfig.DISENGAGE_TICKS.get()) {
            reset(level, s, def, z, zs);
            return;
        }
        leash(level, s, z, zs, box);
        Roster r = FrontierData.roster(z.roster());
        if (r == null) {
            return;
        }
        switch (z.kind()) {
            case WAVES, AMBUSH, BROOD -> waves(level, s, def, z, zs, r, t, engaged);
            case GUARDIAN, FINALE -> Elites.tick(level, s, def, z, zs, r, t, engaged);
            default -> {}
        }
        if (cleared(level, s, z, zs)) {
            clear(level, s, def, z, zs);
        } else {
            updateBar(level, s, def, z, zs, box);
        }
        data.setDirty();
    }

    // -------------------------------------------------------------------------------------------------- starting
    private static void start(ServerLevel level, LandmarkState s, LandmarkDef def, Zone z, ZoneState zs, List<ServerPlayer> players, long t) {
        start(level, s, def, z, zs, players, t, false);
    }

    /** forced: from an operator command; skips the server-wide fight limit. */
    private static void start(ServerLevel level, LandmarkState s, LandmarkDef def, Zone z, ZoneState zs, List<ServerPlayer> players, long t,
                              boolean forced) {
        Roster r = FrontierData.roster(z.roster());
        List<ResourceLocation> missing = r == null ? List.of() : r.missing();
        if (r == null || !missing.isEmpty()) {
            Component why = r == null
                    ? Component.translatable("message.unstable_frontiers.roster_missing", z.roster())
                    : Component.translatable("message.unstable_frontiers.roster_unusable", z.roster(), missing.toString());
            hint(zs, t, players, why.copy().withStyle(ChatFormatting.RED));
            return;
        }
        if (!forced && activeCount(level, s) >= FrontierConfig.activeEncounters()) {
            hint(zs, t, players, Component.translatable("message.unstable_frontiers.busy").withStyle(ChatFormatting.GRAY));
            return;
        }
        boolean wasDormant = zs.dormantPlaced;
        zs.status = ZoneState.Status.ACTIVE;
        if (!wasDormant) {
            zs.session++;
        }
        zs.lastEngaged = t;
        zs.eliteSlain = false;
        zs.telegraphed = false;
        for (ServerPlayer p : players) {
            zs.participants.add(p.getUUID());
        }
        BlockPos at = s.world(z.centre());
        switch (z.kind()) {
            case WAVES -> {
                zs.wavesLeft = z.waves() > 0 ? z.waves() : FrontierConfig.wavesPerFloor();
                zs.nextWaveAt = t + 40;
            }
            case BROOD -> {
                zs.broodStart = brood(level, s, z).size();
                zs.wavesLeft = 1 + Math.min(4, zs.broodStart / 3);
                zs.nextWaveAt = t + 40;
            }
            case AMBUSH -> {
                zs.wavesLeft = Math.max(1, z.waves());
                zs.nextWaveAt = t;
            }
            case CELL, ROOST -> {
                int woken = wakeDormant(level, zs, players.get(0));
                if (woken == 0) {
                    spawnGroup(level, s, z, zs, r, false);
                }
            }
            case GUARDIAN, FINALE -> Elites.begin(level, s, def, z, zs, r, players.get(0));
            default -> {}
        }
        Feedback.title(players(level, s.world(z.box()), 16), Component.literal(z.name()).withStyle(ChatFormatting.RED),
                Component.translatable("zone.unstable_frontiers." + z.kind().name().toLowerCase() + ".start").withStyle(ChatFormatting.GRAY));
        Feedback.sound(level, at, z.kind() == Kind.GUARDIAN || z.kind() == Kind.FINALE ? ModSounds.ELITE_TELL.get() : ModSounds.WAKE.get(),
                2.0F, 1.0F);
        data(level).setDirty();
    }

    /** A dormant creature was struck or the finale lock was opened: start its zone if it may start. */
    public static void provoke(ServerLevel level, Entity e, @Nullable ServerPlayer by) {
        LandmarkState s = data(level).get(Creatures.landmark(e));
        LandmarkDef def = s == null ? null : FrontierData.landmark(s.id);
        if (def == null || Creatures.zone(e) >= def.zones().size()) {
            return;
        }
        Zone z = def.zones().get(Creatures.zone(e));
        ZoneState zs = s.zone(z);
        if (zs.status != ZoneState.Status.IDLE || z.kind() == Kind.FINALE) {
            return;   // the finale only starts at its lock
        }
        List<ServerPlayer> who = new ArrayList<>(players(level, s.world(z.box()), 12));
        if (by != null && !who.contains(by)) {
            who.add(by);
        }
        if (!who.isEmpty() && requirementsMet(s, def, z)) {
            start(level, s, def, z, zs, who, level.getGameTime());
        } else if (e instanceof Mob m) {
            Creatures.setDormant(m, false);
        }
    }

    /** The Cagewright's Key used on a block: returns true (and starts the finale) if it is a Great Cage lock. */
    public static boolean useKey(ServerLevel level, ServerPlayer player, BlockPos clicked) {
        for (LandmarkState s : data(level).all()) {
            LandmarkDef def = FrontierData.landmark(s.id);
            if (def == null) {
                continue;
            }
            for (Zone z : def.zones()) {
                if (z.kind() != Kind.FINALE || z.lock() == null || s.world(z.lock()).distSqr(clicked) > 4) {
                    continue;
                }
                ZoneState zs = s.zone(z);
                if (zs.status != ZoneState.Status.IDLE) {
                    player.displayClientMessage(Component.translatable("message.unstable_frontiers.lock_open"), true);
                    return true;
                }
                if (usable(z.roster()) == null) {
                    player.displayClientMessage(Component.translatable("message.unstable_frontiers.roster_unusable", z.roster(),
                            String.valueOf(rosterMissing(z.roster()))).withStyle(ChatFormatting.RED), false);
                    return true;
                }
                if (z.lockGate() != null) {
                    openGate(level, s, def, z.lockGate());
                }
                start(level, s, def, z, zs, List.of(player), level.getGameTime());
                return zs.status == ZoneState.Status.ACTIVE;
            }
        }
        return false;
    }

    // ---------------------------------------------------------------------------------------------------- waves
    private static void waves(ServerLevel level, LandmarkState s, LandmarkDef def, Zone z, ZoneState zs, Roster r, long t,
                              List<ServerPlayer> engaged) {
        if (zs.wavesLeft <= 0) {
            return;
        }
        int size = waveSize(zs, engaged.size());
        int alive = zs.mobs.size();
        if (alive > Math.max(0, size / 3) || t < zs.nextWaveAt - 30) {
            return;
        }
        List<BlockPos> clutches = z.kind() == Kind.BROOD ? brood(level, s, z) : List.of();
        if (z.kind() == Kind.BROOD && zs.wavesLeft < 1 + Math.min(4, zs.broodStart / 3) && clutches.isEmpty()) {
            zs.wavesLeft = 0;
            Feedback.bar(engaged, Component.translatable("message.unstable_frontiers.brood_broken").withStyle(ChatFormatting.GREEN));
            return;
        }
        if (!zs.telegraphed) {
            zs.telegraphed = true;
            List<Vec3> spots = spots(s, z, clutches);
            for (Vec3 p : spots) {
                Feedback.burst(level, z.kind() == Kind.BROOD ? ParticleTypes.ITEM_SLIME : ParticleTypes.SMOKE, p.add(0, 0.5D, 0), 6, 0.4D);
            }
            Feedback.sound(level, s.world(z.centre()), z.kind() == Kind.BROOD ? ModSounds.BROOD.get() : ModSounds.WAVE.get(), 1.5F, 1.0F);
            if (z.kind() == Kind.BROOD) {
                Feedback.bar(engaged, Component.translatable("message.unstable_frontiers.brood_left", clutches.size())
                        .withStyle(ChatFormatting.YELLOW));
            }
            return;
        }
        if (t < zs.nextWaveAt) {
            return;
        }
        int n = z.kind() == Kind.BROOD ? Math.min(size, 1 + clutches.size() / 2) : size;
        List<Vec3> spots = spots(s, z, clutches);
        List<EntityType<?>> types = Roster.pick(r.mobs(), n, level.random);
        int i = 0;
        for (EntityType<?> type : types) {
            Mob m = spawn(level, type, spots.get(i++ % spots.size()));
            if (m != null) {
                enlist(level, s, z, zs, m, false, engaged.isEmpty() ? null : engaged.get(0));
            }
        }
        if (z.kind() == Kind.AMBUSH && !r.flyers().isEmpty() && !z.flyerSpawns().isEmpty()) {
            for (EntityType<?> type : Roster.pick(r.flyers(), Math.min(2, z.flyerSpawns().size()), level.random)) {
                Mob m = spawn(level, type, s.feet(z.flyerSpawns().get(level.random.nextInt(z.flyerSpawns().size()))));
                if (m != null) {
                    enlist(level, s, z, zs, m, false, engaged.isEmpty() ? null : engaged.get(0));
                }
            }
        }
        zs.wavesLeft--;
        zs.nextWaveAt = t + FrontierConfig.waveCooldown();
        zs.telegraphed = false;
    }

    private static int waveSize(ZoneState zs, int players) {
        int budget = Math.min(FrontierConfig.encounterPerPlayer() * Math.max(1, players), FrontierConfig.encounterPerLandmark());
        return Math.max(1, Math.min(FrontierConfig.mobsPerWave(), budget));
    }

    /** Spawn points for a wave: around intact clutches for a brood, the zone's spawns plus release points otherwise. */
    private static List<Vec3> spots(LandmarkState s, Zone z, List<BlockPos> clutches) {
        List<Vec3> out = new ArrayList<>();
        if (!clutches.isEmpty()) {
            for (BlockPos c : clutches) {
                out.add(new Vec3(c.getX() + 0.5D, c.getY(), c.getZ() + 0.5D));
            }
            return out;
        }
        for (BlockPos p : z.spawns()) {
            out.add(s.feet(p));
        }
        if (z.kind() == Kind.AMBUSH) {
            for (BlockPos p : z.brood()) {
                out.add(s.feet(p.below()));
            }
        }
        if (out.isEmpty()) {
            out.add(s.feet(z.centre()));
        }
        return out;
    }

    /** Intact egg clutches of a brood zone, in world positions. */
    public static List<BlockPos> brood(ServerLevel level, LandmarkState s, Zone z) {
        List<BlockPos> out = new ArrayList<>();
        Block egg = z.broodBlock() != null ? BuiltInRegistries.BLOCK.get(ResourceLocation.parse(z.broodBlock())) : Blocks.TURTLE_EGG;
        if (!z.brood().isEmpty() && z.kind() != Kind.AMBUSH) {
            for (BlockPos p : z.brood()) {
                BlockPos w = s.world(p);
                if (level.getBlockState(w).is(egg)) {
                    out.add(w);
                }
            }
            return out;
        }
        BoundingBox b = s.world(z.box());
        for (BlockPos p : BlockPos.betweenClosed(b.minX(), b.minY(), b.minZ(), b.maxX(), b.maxY(), b.maxZ())) {
            if (level.getBlockState(p).is(egg)) {
                out.add(p.immutable());
            }
        }
        return out;
    }

    // ---------------------------------------------------------------------------------------------- spawning
    /** Places a zone's group: one creature per spawn point (flyers at the flyer points), up to the roster's count. */
    private static void spawnGroup(ServerLevel level, LandmarkState s, Zone z, ZoneState zs, Roster r, boolean dormant) {
        int n = Math.max(1, Math.min(z.spawns().size(), FrontierConfig.mobsPerWave()));
        if (z.waves() > 0 && z.kind() == Kind.CELL) {
            n = Math.min(n, r.mobs().size() + 1);
        }
        List<EntityType<?>> types = Roster.pick(r.mobs(), n, level.random);
        for (int i = 0; i < types.size(); i++) {
            Mob m = spawn(level, types.get(i), s.feet(z.spawns().get(i % z.spawns().size())));
            if (m != null) {
                enlist(level, s, z, zs, m, dormant, null);
            }
        }
        if (!z.flyerSpawns().isEmpty() && !r.flyers().isEmpty()) {
            List<EntityType<?>> flyers = Roster.pick(r.flyers(), z.flyerSpawns().size(), level.random);
            for (int i = 0; i < flyers.size(); i++) {
                Mob m = spawn(level, flyers.get(i), s.feet(z.flyerSpawns().get(i)));
                if (m != null) {
                    enlist(level, s, z, zs, m, dormant, null);
                }
            }
        }
    }

    public static void enlist(ServerLevel level, LandmarkState s, Zone z, ZoneState zs, Mob m, boolean dormant, @Nullable LivingEntity target) {
        Creatures.tagEncounter(m, s.key(), z.index(), zs.session);
        if (dormant) {
            Creatures.setDormant(m, true);
        }
        level.addFreshEntity(m);
        zs.mobs.add(m.getUUID());
        if (!dormant && target != null) {
            m.setTarget(target);
        }
    }

    /** Creates a creature at a spot, nudging it to free space nearby if the spot is blocked. Not yet added to the world. */
    @Nullable
    public static Mob spawn(ServerLevel level, EntityType<?> type, Vec3 at) {
        for (int i = 0; i < 6; i++) {
            Vec3 p = i == 0 ? at : at.add(level.random.nextInt(5) - 2, level.random.nextInt(2), level.random.nextInt(5) - 2);
            Mob m = Creatures.create(level, type, p, i == 5);
            if (m != null) {
                return m;
            }
        }
        return null;
    }

    private static int wakeDormant(ServerLevel level, ZoneState zs, ServerPlayer target) {
        int n = 0;
        for (UUID id : zs.mobs) {
            if (level.getEntity(id) instanceof Mob m && Creatures.isDormant(m)) {
                Creatures.setDormant(m, false);
                m.setTarget(target);
                Feedback.burst(level, ParticleTypes.ANGRY_VILLAGER, m.position().add(0, m.getBbHeight(), 0), 3, 0.3D);
                n++;
            }
        }
        return n;
    }

    private static void spawnResidents(ServerLevel level, LandmarkState s, LandmarkDef def) {
        int cap = FrontierConfig.residentsPerLandmark();
        int placed = 0;
        for (LandmarkDef.Resident res : def.residents()) {
            Roster r = usable(res.roster());
            if (r == null || res.spots().isEmpty()) {
                continue;
            }
            String side = res.roster().equals(def.rivalryHunters()) ? "hunter" : res.roster().equals(def.rivalryPrey()) ? "prey" : "";
            List<Roster.Entry> list = res.flying() && !r.flyers().isEmpty() ? r.flyers() : r.mobs();
            for (EntityType<?> type : Roster.pick(list, Math.min(res.count(), cap - placed), level.random)) {
                Mob m = spawn(level, type, s.feet(res.spots().get(level.random.nextInt(res.spots().size()))));
                if (m == null) {
                    continue;
                }
                Creatures.tagResident(m, s.key(), side);
                level.addFreshEntity(m);
                s.residents.add(m.getUUID());
                placed++;
            }
        }
    }

    private static void pruneResidents(ServerLevel level, LandmarkState s) {
        s.residents.removeIf(id -> {
            Entity e = level.getEntity(id);
            return e == null || !e.isAlive();
        });
    }

    private static void prune(ServerLevel level, ZoneState zs) {
        zs.mobs.removeIf(id -> {
            Entity e = level.getEntity(id);
            return e == null || !e.isAlive();
        });
    }

    /** Creatures that stray too far are brought back to the fight; flyers get twice the room. */
    private static void leash(ServerLevel level, LandmarkState s, Zone z, ZoneState zs, BoundingBox box) {
        double r = FrontierConfig.LEASH_RADIUS.get();
        Vec3 c = box.getCenter().getCenter();
        for (UUID id : zs.mobs) {
            if (!(level.getEntity(id) instanceof Mob m)) {
                continue;
            }
            double limit = Creatures.flies(m) ? r * 2 : r;
            if (m.position().distanceToSqr(c) > limit * limit && !z.spawns().isEmpty()) {
                Vec3 back = s.feet(z.spawns().get(level.random.nextInt(z.spawns().size())));
                m.teleportTo(back.x, back.y, back.z);
                m.getNavigation().stop();
            }
        }
    }

    // ------------------------------------------------------------------------------------------- finishing
    private static boolean cleared(ServerLevel level, LandmarkState s, Zone z, ZoneState zs) {
        return switch (z.kind()) {
            case WAVES, AMBUSH, BROOD -> zs.wavesLeft <= 0 && zs.mobs.isEmpty();
            case CELL, ROOST -> zs.mobs.isEmpty();
            case GUARDIAN, FINALE -> zs.eliteSlain;
            default -> false;
        };
    }

    private static void clear(ServerLevel level, LandmarkState s, LandmarkDef def, Zone z, ZoneState zs) {
        zs.status = ZoneState.Status.CLEARED;
        zs.elite = null;
        // Escorts left when an elite falls go wild: they stay, but no longer belong to the fight.
        for (UUID id : zs.mobs) {
            if (level.getEntity(id) instanceof Mob m) {
                Creatures.tagResident(m, s.key(), "");
            }
        }
        zs.mobs.clear();
        removeBar(s, z);
        BlockPos at = s.world(z.centre());
        List<ServerPlayer> here = players(level, s.world(z.box()), 24);
        if (z.gate() != null) {
            openGate(level, s, def, z.gate());
        }
        if (z.reward() != null) {
            reward(level, s, def, z, zs);
        }
        boolean all = true;
        for (Zone o : def.zones()) {
            all &= o.kind() == Kind.TERRITORY || s.zone(o).status == ZoneState.Status.CLEARED;
        }
        if (z.last() || all) {
            Feedback.title(here, Component.translatable("message.unstable_frontiers.conquered", def.title()).withStyle(ChatFormatting.GOLD),
                    Component.translatable("landmark.unstable_frontiers." + def.kind() + ".conquered").withStyle(ChatFormatting.GRAY));
            Feedback.sound(level, at, ModSounds.CONQUER.get(), 2.0F, 1.0F);
            for (ServerPlayer p : here) {
                Progress.conquered(p, def.kind());
            }
        } else {
            Feedback.bar(here, Component.translatable("message.unstable_frontiers.zone_cleared", z.name()).withStyle(ChatFormatting.GREEN));
            Feedback.sound(level, at, ModSounds.WAKE.get(), 1.0F, 1.6F);
        }
        data(level).setDirty();
    }

    private static void reset(ServerLevel level, LandmarkState s, LandmarkDef def, Zone z, ZoneState zs) {
        for (UUID id : zs.mobs) {
            Entity e = level.getEntity(id);
            if (e != null) {
                e.discard();
            }
        }
        zs.mobs.clear();
        zs.status = ZoneState.Status.IDLE;
        zs.dormantPlaced = false;
        zs.elite = null;
        zs.wavesLeft = 0;
        zs.participants.clear();
        zs.session++;
        removeBar(s, z);
        data(level).setDirty();
        UnstableFrontiers.LOGGER.debug("Landmark {} zone {} reset (nobody near)", s.id, z.id());
    }

    /** Removes a named gate from the world: the blocks crumble with particles and a grinding sound. */
    public static void openGate(ServerLevel level, LandmarkState s, LandmarkDef def, String gate) {
        List<BlockPos> blocks = def.gates().get(gate);
        if (blocks == null || !s.openGates.add(gate)) {
            return;
        }
        for (BlockPos local : blocks) {
            BlockPos p = s.world(local);
            BlockState was = level.getBlockState(p);
            if (!was.isAir()) {
                level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, was), p.getX() + 0.5D, p.getY() + 0.5D, p.getZ() + 0.5D,
                        Math.max(1, FrontierConfig.particleCount(8)), 0.3D, 0.3D, 0.3D, 0.05D);
                level.setBlock(p, Blocks.AIR.defaultBlockState(), 3);
            }
        }
        if (!blocks.isEmpty()) {
            Feedback.sound(level, s.world(blocks.get(0)), ModSounds.GATE.get(), 2.0F, 1.0F);
        }
        data(level).setDirty();
    }

    /** Gives each participant the zone's reward items (a comma-separated list), once per player per landmark. */
    private static void reward(ServerLevel level, LandmarkState s, LandmarkDef def, Zone z, ZoneState zs) {
        List<Item> items = new ArrayList<>();
        for (String name : z.reward().split(",")) {
            name = name.trim();
            ResourceLocation id = name.contains(":") ? ResourceLocation.parse(name) : UnstableFrontiers.id(name);
            if (!BuiltInRegistries.ITEM.containsKey(id)) {
                UnstableFrontiers.LOGGER.error("Landmark {} zone {} names reward {}, which is not an item", s.id, z.id(), id);
                return;
            }
            items.add(BuiltInRegistries.ITEM.get(id));
        }
        for (UUID u : zs.participants) {
            if (!(level.getPlayerByUUID(u) instanceof ServerPlayer p) || p.distanceToSqr(s.world(z.centre()).getCenter()) > 96 * 96) {
                continue;
            }
            if (!s.rewarded.add(u)) {
                continue;
            }
            for (Item item : items) {
                ItemStack stack = new ItemStack(item);
                if (!p.getInventory().add(stack)) {
                    p.drop(stack, false);
                }
                p.displayClientMessage(Component.translatable("message.unstable_frontiers.reward", new ItemStack(item).getHoverName())
                        .withStyle(ChatFormatting.GOLD), false);
            }
        }
    }

    // --------------------------------------------------------------------------------------------- the boss bar
    private static String barKey(LandmarkState s, Zone z) {
        return s.key() + "/" + z.index();
    }

    private static void updateBar(ServerLevel level, LandmarkState s, LandmarkDef def, Zone z, ZoneState zs, BoundingBox box) {
        if (zs.elite == null || !(level.getEntity(zs.elite) instanceof LivingEntity elite)) {
            return;
        }
        Roster r = FrontierData.roster(z.roster());
        ServerBossEvent bar = BARS.computeIfAbsent(barKey(s, z), k -> new ServerBossEvent(elite.getDisplayName(),
                color(r == null || r.elite() == null ? "red" : r.elite().bar()), BossEvent.BossBarOverlay.NOTCHED_10));
        Component name = elite.getDisplayName();
        if (z.kind() == Kind.FINALE) {
            int pylons = Elites.pylons(level, s, z).size();
            name = name.copy().append(Component.translatable("bar.unstable_frontiers.pylons", pylons).withStyle(ChatFormatting.LIGHT_PURPLE));
        }
        bar.setName(name);
        bar.setProgress(Math.max(0, Math.min(1, elite.getHealth() / elite.getMaxHealth())));
        List<ServerPlayer> near = players(level, box, 32);
        for (ServerPlayer p : new ArrayList<>(bar.getPlayers())) {
            if (!near.contains(p)) {
                bar.removePlayer(p);
            }
        }
        for (ServerPlayer p : near) {
            bar.addPlayer(p);
        }
    }

    private static BossEvent.BossBarColor color(String name) {
        try {
            return BossEvent.BossBarColor.valueOf(name.toUpperCase());
        } catch (IllegalArgumentException e) {
            return BossEvent.BossBarColor.RED;
        }
    }

    private static void removeBar(LandmarkState s, Zone z) {
        ServerBossEvent bar = BARS.remove(barKey(s, z));
        if (bar != null) {
            bar.removeAllPlayers();
        }
    }

    // ------------------------------------------------------------------------------------------------ events
    /** Whether a tagged creature that is loading still belongs to a live fight (otherwise it is turned away). */
    public static boolean belongs(ServerLevel level, Entity e) {
        LandmarkState s = data(level).get(Creatures.landmark(e));
        LandmarkDef def = s == null ? null : FrontierData.landmark(s.id);
        if (def == null || Creatures.zone(e) >= def.zones().size()) {
            return false;
        }
        ZoneState zs = s.zone(def.zones().get(Creatures.zone(e)));
        if (zs.session != Creatures.session(e)) {
            return false;
        }
        return zs.status == ZoneState.Status.ACTIVE || (zs.status == ZoneState.Status.IDLE && zs.dormantPlaced && Creatures.isDormant(e));
    }

    public static void onDeath(ServerLevel level, Entity e) {
        LandmarkState s = data(level).get(Creatures.landmark(e));
        LandmarkDef def = s == null ? null : FrontierData.landmark(s.id);
        if (def == null) {
            return;
        }
        if (Creatures.isResident(e)) {
            s.residents.remove(e.getUUID());
            return;
        }
        if (Creatures.zone(e) >= def.zones().size()) {
            return;
        }
        ZoneState zs = s.zone(def.zones().get(Creatures.zone(e)));
        zs.mobs.remove(e.getUUID());
        if (e.getUUID().equals(zs.elite)) {
            zs.eliteSlain = true;
        }
        data(level).setDirty();
    }

    public static boolean anyActive(ServerLevel level) {
        return activeCount(level, null) > 0;
    }

    /** Landmarks with a fight running, other than `except` (several parts of one landmark count once). */
    private static int activeCount(ServerLevel level, @Nullable LandmarkState except) {
        int n = 0;
        for (LandmarkState s : data(level).all()) {
            if (s == except) {
                continue;
            }
            for (ZoneState z : s.zones) {
                if (z.status == ZoneState.Status.ACTIVE) {
                    n++;
                    break;
                }
            }
        }
        return n;
    }

    public static void clearMemory() {
        for (ServerBossEvent bar : BARS.values()) {
            bar.removeAllPlayers();
        }
        BARS.clear();
    }

    // --------------------------------------------------------------------------------------------------- helpers
    public static boolean requirementsMet(LandmarkState s, LandmarkDef def, Zone z) {
        for (String req : z.requires()) {
            Zone o = def.zone(req);
            if (o != null && s.zone(o).status != ZoneState.Status.CLEARED) {
                return false;
            }
        }
        return true;
    }

    private static String progress(LandmarkState s, LandmarkDef def, Zone z) {
        int done = 0;
        for (String req : z.requires()) {
            Zone o = def.zone(req);
            if (o == null || s.zone(o).status == ZoneState.Status.CLEARED) {
                done++;
            }
        }
        return done + "/" + z.requires().size();
    }

    private static void hint(ZoneState zs, long t, List<ServerPlayer> to, Component line) {
        if (t - zs.hintAt < 60) {
            return;
        }
        zs.hintAt = t;
        Feedback.bar(to, line);
    }

    @Nullable
    public static Roster usable(String name) {
        Roster r = FrontierData.roster(name);
        return r != null && r.missing().isEmpty() ? r : null;
    }

    private static List<ResourceLocation> rosterMissing(String name) {
        Roster r = FrontierData.roster(name);
        return r == null ? List.of() : r.missing();
    }

    public static List<ServerPlayer> players(ServerLevel level, BoundingBox box, int inflate) {
        AABB area = AABB.of(box).inflate(inflate);
        List<ServerPlayer> out = new ArrayList<>();
        for (ServerPlayer p : level.players()) {
            if (!p.isSpectator() && p.isAlive() && area.contains(p.position())) {
                out.add(p);
            }
        }
        return out;
    }

    /** The landmark and zone at a position, for commands. */
    @Nullable
    public static LandmarkState at(ServerLevel level, BlockPos pos, int slack) {
        for (LandmarkState s : data(level).all()) {
            LandmarkDef def = FrontierData.landmark(s.id);
            if (def != null && s.bounds(def).inflatedBy(slack).isInside(pos)) {
                return s;
            }
        }
        for (LandmarkPiece piece : LandmarkLocator.near(level, pos, 1)) {
            if (piece.getBoundingBox().inflatedBy(slack).isInside(pos) && FrontierData.landmark(piece.templateId()) != null) {
                LandmarkState s = new LandmarkState(piece.templateId(), piece.origin(), piece.rotation());
                data(level).add(s);
                return s;
            }
        }
        return null;
    }

    /** For commands: forces a zone to start, clear or reset. */
    public static String force(ServerLevel level, LandmarkState s, String zoneId, String action, ServerPlayer by) {
        LandmarkDef def = FrontierData.landmark(s.id);
        Zone z = def == null ? null : def.zone(zoneId);
        if (z == null) {
            return "no zone '" + zoneId + "'";
        }
        ZoneState zs = s.zone(z);
        switch (action) {
            case "start" -> {
                if (zs.status == ZoneState.Status.ACTIVE) {
                    return "already active";
                }
                zs.status = ZoneState.Status.IDLE;
                if (z.kind() == Kind.FINALE && z.lockGate() != null) {
                    openGate(level, s, def, z.lockGate());
                }
                start(level, s, def, z, zs, List.of(by), level.getGameTime(), true);
            }
            case "clear" -> {
                for (UUID id : zs.mobs) {
                    Entity e = level.getEntity(id);
                    if (e != null) {
                        e.discard();
                    }
                }
                zs.mobs.clear();
                zs.participants.add(by.getUUID());
                clear(level, s, def, z, zs);
            }
            case "reset" -> {
                reset(level, s, def, z, zs);
                if (z.gate() != null) {
                    s.openGates.remove(z.gate());
                }
            }
            default -> {
                return "unknown action";
            }
        }
        return z.id() + " is now " + zs.status;
    }

    /** One line per zone, for /frontier landmark info. */
    public static List<String> describe(ServerLevel level, LandmarkState s) {
        List<String> out = new ArrayList<>();
        LandmarkDef def = FrontierData.landmark(s.id);
        if (def == null) {
            out.add(s.id + ": no definition loaded");
            return out;
        }
        out.add(def.title() + " (" + s.id + ") origin " + s.origin.toShortString() + " rotation " + s.rotation + " centre "
                + s.centre(def).toShortString());
        for (Zone z : def.zones()) {
            ZoneState zs = s.zone(z);
            Roster r = FrontierData.roster(z.roster());
            String roster = r == null ? "MISSING" : r.missing().isEmpty() ? "ok" : "missing " + r.missing();
            out.add("  " + z.id() + " [" + z.kind() + "] " + zs.status + " session " + zs.session + " mobs " + zs.mobs.size() + " waves left "
                    + zs.wavesLeft + " roster " + z.roster() + " (" + roster + ")" + (requirementsMet(s, def, z) ? "" : " sealed"));
        }
        out.add("  residents " + s.residents.size() + ", gates open " + s.openGates + ", rewarded " + s.rewarded.size());
        return out;
    }
}
