package com.aurelia;

import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;

/**
 * The mod's particles all pass through here, thinned by the config's particle density: bursts send fewer particles, rings and trails
 * drop a share of their points. Fewer particles to send and draw keeps a busy fight or a crowded dungeon smooth. Telegraphs that warn
 * of an attack (the Wardens' signature moves, trap warnings) do not come through here and always show in full.
 */
public final class Perf {
    private Perf() {}

    private static int scale(ServerLevel level, int count) {
        double d = AureliaConfig.PARTICLE_DENSITY.get();
        if (d >= 1.0) {
            return count;
        }
        if (d <= 0.0) {
            return -1;
        }
        if (count <= 1) {
            return level.random.nextDouble() < d ? count : -1;            // single points of a ring or a trail: keep a share of them
        }
        return Math.max(1, (int) Math.round(count * d));
    }

    public static int particles(ServerLevel level, ParticleOptions type, double x, double y, double z, int count, double dx, double dy, double dz,
                                double speed) {
        int n = scale(level, count);
        return n < 0 ? 0 : level.sendParticles(type, x, y, z, n, dx, dy, dz, speed);
    }

    public static boolean particles(ServerLevel level, ServerPlayer player, ParticleOptions type, boolean force, double x, double y, double z,
                                    int count, double dx, double dy, double dz, double speed) {
        int n = scale(level, count);
        return n >= 0 && level.sendParticles(player, type, force, x, y, z, n, dx, dy, dz, speed);
    }
}
