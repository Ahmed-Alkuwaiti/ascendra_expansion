package com.unstablefrontiers.encounter;

import com.unstablefrontiers.config.FrontierConfig;
import java.util.Collection;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.phys.Vec3;

/** Titles, action-bar lines, sounds and particles: how the landmarks talk to the player. */
public final class Feedback {
    private Feedback() {}

    public static void title(Collection<ServerPlayer> players, Component title, Component subtitle) {
        for (ServerPlayer p : players) {
            p.connection.send(new ClientboundSetTitlesAnimationPacket(10, 50, 20));
            p.connection.send(new ClientboundSetSubtitleTextPacket(subtitle));
            p.connection.send(new ClientboundSetTitleTextPacket(title));
        }
    }

    public static void bar(Collection<ServerPlayer> players, Component line) {
        for (ServerPlayer p : players) {
            p.displayClientMessage(line, true);
        }
    }

    public static void chat(Collection<ServerPlayer> players, Component line) {
        for (ServerPlayer p : players) {
            p.displayClientMessage(line, false);
        }
    }

    public static void sound(ServerLevel level, BlockPos at, SoundEvent sound, float volume, float pitch) {
        level.playSound(null, at, sound, SoundSource.HOSTILE, volume, pitch);
    }

    public static void burst(ServerLevel level, ParticleOptions particle, Vec3 at, int base, double spread) {
        int n = FrontierConfig.particleCount(base);
        if (n > 0) {
            level.sendParticles(particle, at.x, at.y, at.z, n, spread, spread * 0.6D, spread, 0.02D);
        }
    }

    /** A flat ring on the ground: the warning drawn before an elite's slam lands. */
    public static void ring(ServerLevel level, ParticleOptions particle, Vec3 centre, double radius) {
        int n = FrontierConfig.particleCount(28);
        for (int i = 0; i < n; i++) {
            double a = i * Math.PI * 2 / n;
            level.sendParticles(particle, centre.x + Math.cos(a) * radius, centre.y + 0.15D, centre.z + Math.sin(a) * radius, 1, 0, 0, 0, 0);
        }
    }
}
