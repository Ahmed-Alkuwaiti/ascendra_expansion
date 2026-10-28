package com.unstablefrontiers.encounter;

import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.ecology.Creatures;
import com.unstablefrontiers.ecology.Roster;
import com.unstablefrontiers.landmark.FrontierData;
import com.unstablefrontiers.landmark.LandmarkDef;
import com.unstablefrontiers.landmark.LandmarkDef.Kind;
import com.unstablefrontiers.landmark.LandmarkDef.Zone;
import com.unstablefrontiers.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;

/**
 * Elites: the guardian of a landmark and the beast of the Great Cage. An elite is the creature its roster names, with
 * its own health and attacks (nothing is inflated; Integrated Boogaloo's difficulty scaling applies as it does to any
 * spawn). What it gains is a name, a boss bar and abilities that are always announced before they land: a ring drawn on
 * the ground before a slam, a call before escorts arrive, a crouch before a pounce, a shriek before the dark. Every
 * ability can be avoided by reacting to its tell.
 *
 * <p>The finale's beast is shielded while any of the cage's pylons stands: it takes a sixth of the damage dealt to it.
 * Pylon cores break quickly when mined, and every pylon that falls brings flyers down from the dome.
 */
public final class Elites {
    private static final int TELL = 30;
    private static final float SHIELDED = 1.0F / 6.0F;

    private Elites() {}

    static void begin(ServerLevel level, LandmarkState s, LandmarkDef def, Zone z, ZoneState zs, Roster r, ServerPlayer target) {
        spawnElite(level, s, z, zs, r, target);
        List<EntityType<?>> escorts = Roster.pick(r.mobs(), r.escorts(), level.random);
        for (int i = 0; i < escorts.size(); i++) {
            BlockPos at = z.spawns().isEmpty() ? z.centre() : z.spawns().get((i + 1) % z.spawns().size());
            Mob m = EncounterManager.spawn(level, escorts.get(i), s.feet(at));
            if (m != null) {
                EncounterManager.enlist(level, s, z, zs, m, false, target);
            }
        }
        zs.abilityAt = level.getGameTime() + FrontierConfig.ABILITY_INTERVAL.get();
        zs.pylonsSeen = pylons(level, s, z).size();
    }

    private static void spawnElite(ServerLevel level, LandmarkState s, Zone z, ZoneState zs, Roster r, @Nullable ServerPlayer target) {
        EntityType<?> type = r.elite() != null ? Roster.type(r.elite().type()) : Roster.pick(r.mobs(), 1, level.random).get(0);
        BlockPos at = z.spawns().isEmpty() ? z.centre() : z.spawns().get(0);
        Mob elite = EncounterManager.spawn(level, type, s.feet(at));
        if (elite == null) {
            return;
        }
        if (r.elite() != null && !r.elite().title().isEmpty()) {
            elite.setCustomName(Component.literal(r.elite().title()).withStyle(ChatFormatting.DARK_RED));
        }
        EncounterManager.enlist(level, s, z, zs, elite, false, target);
        zs.elite = elite.getUUID();
        Feedback.burst(level, ParticleTypes.LARGE_SMOKE, elite.position().add(0, 1, 0), 20, 1.0D);
    }

    static void tick(ServerLevel level, LandmarkState s, LandmarkDef def, Zone z, ZoneState zs, Roster r, long t, List<ServerPlayer> engaged) {
        Mob elite = zs.elite == null ? null : level.getEntity(zs.elite) instanceof Mob m ? m : null;
        if (elite == null && !zs.eliteSlain) {
            // Lost without dying (pushed out of the world, removed by another mod): it returns to its post.
            spawnElite(level, s, z, zs, r, engaged.isEmpty() ? null : engaged.get(0));
            return;
        }
        if (elite == null) {
            return;
        }
        if (z.kind() == Kind.FINALE) {
            pylonTick(level, s, z, zs, r, elite, t, engaged);
        }
        if (zs.pendingAbility != null) {
            if (t >= zs.pendingAt) {
                perform(level, s, z, zs, r, elite, zs.pendingAbility);
                zs.pendingAbility = null;
            }
            return;
        }
        if (t < zs.abilityAt || r.elite() == null || r.elite().abilities().isEmpty()) {
            return;
        }
        ServerPlayer near = nearest(elite, engaged, 16);
        if (near == null) {
            return;
        }
        List<String> abilities = r.elite().abilities();
        String ability = abilities.get(level.random.nextInt(abilities.size()));
        tell(level, s, z, elite, ability, engaged);
        zs.pendingAbility = ability;
        zs.pendingAt = t + TELL;
        zs.abilityAt = t + FrontierConfig.ABILITY_INTERVAL.get() + level.random.nextInt(40);
    }

    private static void tell(ServerLevel level, LandmarkState s, Zone z, Mob elite, String ability, List<ServerPlayer> engaged) {
        Component name = elite.getDisplayName();
        Feedback.sound(level, elite.blockPosition(), ModSounds.ELITE_TELL.get(), 2.0F, ability.equals("screech") ? 1.4F : 0.8F);
        switch (ability) {
            case "slam" -> Feedback.ring(level, ParticleTypes.CRIT, elite.position(), 5.0D);
            case "rally" -> {
                for (BlockPos p : z.spawns()) {
                    Feedback.burst(level, ParticleTypes.SMOKE, s.feet(p).add(0, 0.5D, 0), 4, 0.3D);
                }
            }
            case "pounce" -> Feedback.burst(level, ParticleTypes.CLOUD, elite.position(), 8, 0.6D);
            case "screech" -> Feedback.burst(level, ParticleTypes.SCULK_SOUL, elite.position().add(0, elite.getBbHeight(), 0), 10, 0.8D);
            default -> {}
        }
        Feedback.bar(engaged, Component.translatable("elite.unstable_frontiers." + ability + ".tell", name).withStyle(ChatFormatting.YELLOW));
    }

    private static void perform(ServerLevel level, LandmarkState s, Zone z, ZoneState zs, Roster r, Mob elite, String ability) {
        switch (ability) {
            case "slam" -> {
                for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, elite.getBoundingBox().inflate(5.5D, 2.0D, 5.5D))) {
                    if (p.isSpectator() || p.isCreative() || p.distanceToSqr(elite) > 5.5D * 5.5D) {
                        continue;
                    }
                    p.hurt(level.damageSources().mobAttack(elite), 7.0F);
                    p.knockback(1.2D, elite.getX() - p.getX(), elite.getZ() - p.getZ());
                    p.hurtMarked = true;
                }
                Feedback.burst(level, ParticleTypes.EXPLOSION, elite.position(), 6, 2.0D);
                Feedback.sound(level, elite.blockPosition(), ModSounds.ELITE_SLAM.get(), 2.0F, 1.0F);
            }
            case "rally" -> {
                int alive = zs.mobs.size() - 1;
                int want = Math.min(2, r.escorts() - alive);
                List<EntityType<?>> types = Roster.pick(r.mobs(), Math.max(0, want), level.random);
                for (int i = 0; i < types.size() && !z.spawns().isEmpty(); i++) {
                    Mob m = EncounterManager.spawn(level, types.get(i), s.feet(z.spawns().get(level.random.nextInt(z.spawns().size()))));
                    if (m != null) {
                        EncounterManager.enlist(level, s, z, zs, m, false, elite.getTarget());
                    }
                }
            }
            case "pounce" -> {
                LivingEntity target = elite.getTarget();
                if (target != null && target.distanceToSqr(elite) < 20 * 20) {
                    Vec3 d = target.position().subtract(elite.position());
                    Vec3 flat = new Vec3(d.x, 0, d.z).normalize().scale(Math.min(1.6D, d.horizontalDistance() * 0.18D));
                    elite.setDeltaMovement(flat.x, 0.7D, flat.z);
                    elite.hurtMarked = true;
                }
            }
            case "screech" -> {
                for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, elite.getBoundingBox().inflate(14.0D))) {
                    if (!p.isSpectator() && !p.isCreative()) {
                        p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 0));
                        p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 80, 0));
                    }
                }
            }
            default -> {}
        }
    }

    // ---------------------------------------------------------------------------------------------------- pylons
    public static List<BlockPos> pylons(ServerLevel level, LandmarkState s, Zone z) {
        List<BlockPos> out = new ArrayList<>();
        for (BlockPos local : z.pylons()) {
            BlockPos p = s.world(local);
            if (!level.getBlockState(p).isAir()) {
                out.add(p);
            }
        }
        return out;
    }

    private static void pylonTick(ServerLevel level, LandmarkState s, Zone z, ZoneState zs, Roster r, Mob elite, long t,
                                  List<ServerPlayer> engaged) {
        List<BlockPos> standing = pylons(level, s, z);
        if (zs.pylonsSeen < 0) {
            zs.pylonsSeen = standing.size();
        }
        if (standing.size() < zs.pylonsSeen) {
            zs.pylonsSeen = standing.size();
            Feedback.sound(level, elite.blockPosition(), ModSounds.PYLON.get(), 3.0F, 1.0F);
            Feedback.title(engaged, Component.empty(), standing.isEmpty()
                    ? Component.translatable("message.unstable_frontiers.shield_down").withStyle(ChatFormatting.LIGHT_PURPLE)
                    : Component.translatable("message.unstable_frontiers.pylon_down", standing.size()).withStyle(ChatFormatting.LIGHT_PURPLE));
            List<EntityType<?>> flyers = Roster.pick(r.flyers(), Math.min(2, z.flyerSpawns().size()), level.random);
            for (int i = 0; i < flyers.size(); i++) {
                Mob m = EncounterManager.spawn(level, flyers.get(i), s.feet(z.flyerSpawns().get(i)));
                if (m != null) {
                    EncounterManager.enlist(level, s, z, zs, m, false, engaged.isEmpty() ? null : engaged.get(0));
                }
            }
        }
        if (t % 20 == 0 && !standing.isEmpty()) {
            // A visible tether from each standing pylon to the beast.
            Vec3 to = elite.position().add(0, elite.getBbHeight() * 0.6D, 0);
            for (BlockPos p : standing) {
                Vec3 from = p.getCenter();
                int steps = FrontierConfig.particleCount(12);
                for (int i = 0; i < steps; i++) {
                    Vec3 q = from.lerp(to, i / (double) Math.max(1, steps));
                    level.sendParticles(ParticleTypes.END_ROD, q.x, q.y, q.z, 1, 0, 0, 0, 0);
                }
            }
        }
    }

    /** Damage taken by the finale beast while its pylons stand. Returns the new amount. */
    public static float shield(ServerLevel level, Entity victim, float amount) {
        if (!Creatures.isEncounter(victim)) {
            return amount;
        }
        LandmarkState s = EncounterManager.data(level).get(Creatures.landmark(victim));
        LandmarkDef def = s == null ? null : FrontierData.landmark(s.id);
        if (def == null || Creatures.zone(victim) >= def.zones().size()) {
            return amount;
        }
        Zone z = def.zones().get(Creatures.zone(victim));
        ZoneState zs = s.zone(z);
        if (z.kind() != Kind.FINALE || !victim.getUUID().equals(zs.elite) || pylons(level, s, z).isEmpty()) {
            return amount;
        }
        Feedback.burst(level, ParticleTypes.ENCHANTED_HIT, victim.position().add(0, victim.getBbHeight() / 2, 0), 8, 0.6D);
        if (level.getGameTime() - zs.hintAt > 40) {
            zs.hintAt = level.getGameTime();
            Feedback.sound(level, victim.blockPosition(), ModSounds.SHIELD.get(), 1.5F, 1.0F);
            Feedback.bar(EncounterManager.players(level, s.world(z.box()), 16),
                    Component.translatable("message.unstable_frontiers.shielded").withStyle(ChatFormatting.LIGHT_PURPLE));
        }
        return amount * SHIELDED;
    }

    /** Whether a block is a standing pylon core of an active finale (mined quickly). */
    public static boolean isActivePylon(ServerLevel level, BlockPos pos) {
        for (LandmarkState s : EncounterManager.data(level).all()) {
            LandmarkDef def = FrontierData.landmark(s.id);
            if (def == null) {
                continue;
            }
            for (Zone z : def.zones()) {
                if (z.kind() == Kind.FINALE && s.zone(z).status == ZoneState.Status.ACTIVE) {
                    for (BlockPos local : z.pylons()) {
                        if (s.world(local).equals(pos)) {
                            return true;
                        }
                    }
                }
            }
        }
        return false;
    }

    @Nullable
    private static ServerPlayer nearest(Mob elite, List<ServerPlayer> players, double within) {
        ServerPlayer best = null;
        double bd = within * within;
        for (ServerPlayer p : players) {
            double d = p.distanceToSqr(elite);
            if (d < bd) {
                bd = d;
                best = p;
            }
        }
        return best;
    }

    static boolean isElite(ZoneState zs, UUID id) {
        return id.equals(zs.elite);
    }
}
