package com.unstablefrontiers.ecology;

import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.encounter.CageBeacons;
import com.unstablefrontiers.encounter.EncounterManager;
import com.unstablefrontiers.registry.ModSounds;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

/**
 * Between landmarks, after dark: now and then a hunting flyer (roster night_overflight) crosses the sky near a player and
 * may stoop on them. At most one per player at a time, at most one every overflightIntervalTicks per player, never inside
 * a Cage Beacon's ground, and never when the roster cannot be resolved.
 */
public final class Overflight {
    private static final Map<UUID, Long> NEXT = new HashMap<>();
    private static final Map<UUID, UUID> FLYER = new HashMap<>();

    private Overflight() {}

    public static void tick(ServerLevel level, long time) {
        if (time % 100 != 0 || level.isDay()) {
            return;
        }
        Roster r = EncounterManager.usable("night_overflight");
        if (r == null) {
            return;
        }
        for (ServerPlayer p : level.players()) {
            if (p.isSpectator() || p.isCreative()) {
                continue;
            }
            UUID flyer = FLYER.get(p.getUUID());
            if (flyer != null && level.getEntity(flyer) != null) {
                continue;
            }
            long next = NEXT.computeIfAbsent(p.getUUID(), u -> time + level.random.nextInt(FrontierConfig.overflightInterval()));
            if (time < next || CageBeacons.covers(level, p.blockPosition())) {
                continue;
            }
            NEXT.put(p.getUUID(), time + FrontierConfig.overflightInterval());
            double a = level.random.nextDouble() * Math.PI * 2;
            int x = (int) (p.getX() + Math.cos(a) * 40);
            int z = (int) (p.getZ() + Math.sin(a) * 40);
            if (!level.hasChunkAt(new net.minecraft.core.BlockPos(x, 0, z))) {
                continue;
            }
            int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z) + 24;
            for (EntityType<?> type : Roster.pick(r.flyers().isEmpty() ? r.mobs() : r.flyers(), 1, level.random)) {
                Mob m = EncounterManager.spawn(level, type, new Vec3(x + 0.5D, y, z + 0.5D));
                if (m == null) {
                    continue;
                }
                Creatures.tagResident(m, 0L, "");
                m.setPersistenceRequired();
                level.addFreshEntity(m);
                m.setTarget(p);
                FLYER.put(p.getUUID(), m.getUUID());
                level.playSound(null, p.blockPosition(), ModSounds.ELITE_TELL.get(), SoundSource.HOSTILE, 0.6F, 1.5F);
                p.displayClientMessage(Component.translatable("message.unstable_frontiers.overflight").withStyle(ChatFormatting.DARK_GRAY), true);
            }
        }
    }

    public static void clearMemory() {
        NEXT.clear();
        FLYER.clear();
    }
}
