package com.aurelia.entity;

import com.aurelia.registry.ModEntities;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import javax.annotation.Nullable;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

/**
 * Each Warden's signature: a telegraphed move on its own timer, on top of its gimmick and its ordinary attacks. Every one is shown
 * before it lands (particles and a sound), so it can always be read and dodged.
 */
public final class BossSignatures {
    private BossSignatures() {}

    /** Per-boss state for the move in flight. */
    public static final class State {
        int cooldown = 360;
        int timer = -1;
        int length = 0;
        Vec3 centre = Vec3.ZERO;
        Vec3 dir = Vec3.ZERO;
        final List<Vec3> points = new ArrayList<>();
        final Map<UUID, Vec3> marks = new HashMap<>();
        final Set<UUID> hit = new HashSet<>();
    }

    public static void tick(AureliaBoss boss, @Nullable LivingEntity target) {
        if (!(boss.level() instanceof ServerLevel level)) {
            return;
        }
        State s = boss.signature;
        if (s.timer >= 0) {
            telegraph(boss, level, s);
            if (s.timer == 0) {
                resolve(boss, level, s);
            }
            s.timer--;
            return;
        }
        if (target == null || boss.shieldTicks > 0 || --s.cooldown > 0) {
            return;
        }
        s.cooldown = switch (boss.phase) {
            case 1 -> 600;
            case 2 -> 440;
            default -> 300;
        } + boss.getRandom().nextInt(120);
        s.points.clear();
        s.marks.clear();
        s.hit.clear();
        s.centre = boss.arena != null ? Vec3.atBottomCenterOf(boss.arena) : boss.position();
        start(boss, level, s, target);
    }

    private static List<Player> players(AureliaBoss boss, double r) {
        return boss.level().getEntitiesOfClass(Player.class, boss.getBoundingBox().inflate(r), p -> p.isAlive() && !p.isSpectator() && !p.isCreative());
    }

    private static void ring(ServerLevel level, ParticleOptions p, Vec3 c, double r, int n) {
        for (int k = 0; k < n; k++) {
            double a = k * Math.PI * 2 / n;
            level.sendParticles(p, c.x + Math.cos(a) * r, c.y + 0.15, c.z + Math.sin(a) * r, 1, 0.05, 0.05, 0.05, 0.0);
        }
    }

    private static void bolt(ServerLevel level, Vec3 at) {
        LightningBolt b = EntityType.LIGHTNING_BOLT.create(level);
        if (b != null) {
            b.moveTo(at.x, at.y, at.z);
            b.setVisualOnly(true);
            level.addFreshEntity(b);
        }
    }

    private static double flat(Vec3 a, Vec3 b) {
        double dx = a.x - b.x, dz = a.z - b.z;
        return Math.sqrt(dx * dx + dz * dz);
    }

    // ------------------------------------------------------------------------------------------------ start
    private static void start(AureliaBoss boss, ServerLevel level, State s, LivingEntity target) {
        if (boss instanceof MossbackTitan) {
            for (Player p : players(boss, 32)) {
                s.marks.put(p.getUUID(), p.position());
            }
            s.length = 34;
            boss.playSound(SoundEvents.ROOTED_DIRT_PLACE, 3.0f, 0.5f);
        } else if (boss instanceof TempestRoc) {
            s.centre = target.position();
            s.length = 70;
            boss.playSound(SoundEvents.TRIDENT_THUNDER, 3.0f, 1.4f);
        } else if (boss instanceof HollowKing) {
            for (Player p : players(boss, 24)) {
                s.marks.put(p.getUUID(), p.position());
            }
            s.length = 90;
            boss.playSound(SoundEvents.CHAIN_PLACE, 3.0f, 0.4f);
        } else if (boss instanceof Vorath) {
            double a = boss.getRandom().nextDouble() * Math.PI * 2;
            s.dir = new Vec3(Math.cos(a), 0, Math.sin(a));
            s.length = 56;                                                    // 20 ticks of warning, then the wave crosses
            boss.playSound(SoundEvents.ELDER_GUARDIAN_CURSE, 3.0f, 0.5f);
        } else if (boss instanceof WhiteSilence) {
            for (Player p : players(boss, 32)) {
                p.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 70, 0));
            }
            s.length = 50;
            boss.playSound(SoundEvents.POWDER_SNOW_STEP, 3.0f, 0.4f);
        } else if (boss instanceof Kharzul) {
            Vec3 d = target.position().subtract(boss.position());
            s.dir = new Vec3(d.x, 0, d.z).normalize();
            s.length = 26;
            boss.getNavigation().stop();
            boss.playSound(SoundEvents.WITHER_SHOOT, 2.5f, 0.4f);
        } else if (boss instanceof Vexor) {
            for (Player p : players(boss, 40)) {
                s.marks.put(p.getUUID(), p.position());
            }
            s.length = 80;
            boss.playSound(SoundEvents.BELL_RESONATE, 3.0f, 0.6f);
        } else if (boss instanceof BloomMother) {
            for (int k = 0; k < 7 + boss.phase * 2; k++) {
                double a = boss.getRandom().nextDouble() * Math.PI * 2, r = 3 + boss.getRandom().nextDouble() * 10;
                s.points.add(s.centre.add(Math.cos(a) * r, 0, Math.sin(a) * r));
            }
            for (Player p : players(boss, 24)) {
                s.points.add(p.position());                                   // one under everybody, too
            }
            s.length = 50;
            boss.playSound(SoundEvents.BIG_DRIPLEAF_TILT_DOWN, 3.0f, 0.5f);
        } else if (boss instanceof Unmaker) {
            s.length = 110;
            boss.playSound(SoundEvents.WARDEN_SONIC_CHARGE, 4.0f, 0.4f);
        } else {
            return;
        }
        s.timer = s.length;
    }

    // ------------------------------------------------------------------------------------------------ while it builds
    private static void telegraph(AureliaBoss boss, ServerLevel level, State s) {
        int t = s.length - s.timer;                                           // ticks since it began
        if (boss instanceof MossbackTitan) {
            if (t % 3 == 0) {
                for (Vec3 m : s.marks.values()) {
                    ring(level, ParticleTypes.COMPOSTER, m, 2.6, 18);
                    ring(level, ParticleTypes.SPORE_BLOSSOM_AIR, m, 1.4 * t / s.length, 8);
                }
            }
        } else if (boss instanceof TempestRoc) {
            double r = 8.0 * s.timer / s.length;                              // the ring of strikes closes on the marked spot
            ring(level, ParticleTypes.ELECTRIC_SPARK, s.centre, r, 24);
            if (t > 0 && t % 10 == 0) {
                for (int k = 0; k < 6; k++) {
                    double a = k * Math.PI / 3 + t * 0.1;
                    Vec3 at = s.centre.add(Math.cos(a) * r, 0, Math.sin(a) * r);
                    bolt(level, at);
                    for (Player p : players(boss, 48)) {
                        if (flat(p.position(), at) < 2.0) {
                            p.hurt(boss.damageSources().lightningBolt(), 7.0f);
                        }
                    }
                }
            }
        } else if (boss instanceof HollowKing) {
            if (t % 4 == 0) {
                for (Player p : players(boss, 40)) {
                    if (!s.marks.containsKey(p.getUUID())) {
                        continue;
                    }
                    Vec3 from = boss.position().add(0, boss.getBbHeight() * 0.6, 0), to = p.position().add(0, 1, 0);
                    for (int k = 1; k < 12; k++) {
                        Vec3 q = from.lerp(to, k / 12.0);
                        level.sendParticles(ParticleTypes.SOUL, q.x, q.y, q.z, 1, 0, 0, 0, 0);
                    }
                    if (flat(p.position(), boss.position()) > 10.0) {                // the chain drags anyone who strays
                        Vec3 in = boss.position().subtract(p.position()).normalize().scale(1.2);
                        p.push(in.x, 0.3, in.z);
                        p.hurtMarked = true;
                        p.addEffect(new MobEffectInstance(MobEffects.WITHER, 40, 1));
                        p.hurt(boss.damageSources().mobAttack(boss), 3.0f);
                    }
                }
            }
        } else if (boss instanceof Vorath) {
            Vec3 side = new Vec3(-s.dir.z, 0, s.dir.x);
            if (t < 20) {
                Vec3 line = s.centre.subtract(s.dir.scale(16));
                for (int k = -15; k <= 15; k += 2) {
                    Vec3 q = line.add(side.scale(k));
                    level.sendParticles(ParticleTypes.SPLASH, q.x, q.y + 0.4, q.z, 4, 0.2, 0.2, 0.2, 0.0);
                }
                return;
            }
            Vec3 front = s.centre.subtract(s.dir.scale(16)).add(s.dir.scale(t - 20));
            for (int k = -15; k <= 15; k += 2) {
                Vec3 q = front.add(side.scale(k));
                level.sendParticles(ParticleTypes.FALLING_WATER, q.x, q.y + 2.5, q.z, 6, 0.3, 1.2, 0.3, 0.0);
                level.sendParticles(ParticleTypes.BUBBLE_POP, q.x, q.y + 0.5, q.z, 2, 0.3, 0.3, 0.3, 0.0);
            }
            for (Player p : players(boss, 48)) {
                Vec3 rel = p.position().subtract(front);
                if (Math.abs(rel.dot(s.dir)) < 1.6 && Math.abs(rel.dot(side)) < 16 && s.hit.add(p.getUUID())) {
                    p.push(s.dir.x * 2.0, 0.6, s.dir.z * 2.0);
                    p.hurtMarked = true;
                    p.hurt(boss.damageSources().drown(), 6.0f);
                    p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 2));
                }
            }
        } else if (boss instanceof WhiteSilence) {
            if (t % 5 == 0) {
                for (Player p : players(boss, 40)) {
                    level.sendParticles(ParticleTypes.SNOWFLAKE, p.getX(), p.getY() + 1.2, p.getZ(), 30, 2.5, 1.2, 2.5, 0.02);
                }
            }
        } else if (boss instanceof Kharzul) {
            boss.setDeltaMovement(0, boss.getDeltaMovement().y, 0);
            if (t % 3 == 0) {
                for (double r = 2; r <= 10; r += 1.5) {
                    for (double a = -60; a <= 60; a += 12) {
                        Vec3 d = s.dir.yRot((float) Math.toRadians(a)).scale(r);
                        level.sendParticles(ParticleTypes.FLAME, boss.getX() + d.x, boss.getY() + 0.2, boss.getZ() + d.z, 1, 0, 0, 0, 0);
                    }
                }
            }
        } else if (boss instanceof Vexor) {
            if (t % 20 == 0) {
                boss.playSound(SoundEvents.NOTE_BLOCK_HAT.value(), 3.0f, 0.5f + t / 160.0f);
            }
            if (t % 4 == 0) {
                for (Vec3 m : s.marks.values()) {
                    level.sendParticles(ParticleTypes.REVERSE_PORTAL, m.x, m.y + 1, m.z, 10, 0.3, 0.8, 0.3, 0.02);
                }
            }
        } else if (boss instanceof BloomMother) {
            if (t % 3 == 0) {
                for (Vec3 q : s.points) {
                    ring(level, ParticleTypes.SPORE_BLOSSOM_AIR, q, 2.4, 10);
                    level.sendParticles(ParticleTypes.HAPPY_VILLAGER, q.x, q.y + 0.3, q.z, 1 + t / 10, 0.6, 0.2, 0.6, 0.0);
                }
            }
        } else if (boss instanceof Unmaker) {
            double r = Mth.lerp((double) t / s.length, 32.0, 7.0);             // the edge of the world closes in
            ring(level, ParticleTypes.SQUID_INK, s.centre, r, 64);
            ring(level, ParticleTypes.REVERSE_PORTAL, s.centre.add(0, 1.5, 0), r, 32);
            if (t % 10 == 0) {
                for (Player p : players(boss, 64)) {
                    if (flat(p.position(), s.centre) > r) {
                        p.hurt(boss.damageSources().magic(), 4.0f);
                        p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 60, 0));
                    }
                }
            }
        }
    }

    // ------------------------------------------------------------------------------------------------ when it lands
    private static void resolve(AureliaBoss boss, ServerLevel level, State s) {
        if (boss instanceof MossbackTitan) {
            boss.playSound(SoundEvents.ROOTED_DIRT_BREAK, 4.0f, 0.4f);
            for (Player p : players(boss, 40)) {
                Vec3 m = s.marks.get(p.getUUID());
                if (m != null && flat(p.position(), m) < 2.6) {
                    p.hurt(boss.damageSources().mobAttack(boss), 10.0f);
                    p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 70, 6));
                    p.addEffect(new MobEffectInstance(MobEffects.JUMP, 70, 128));
                    p.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 1));
                    level.sendParticles(ParticleTypes.SPORE_BLOSSOM_AIR, p.getX(), p.getY() + 0.5, p.getZ(), 60, 1.0, 1.0, 1.0, 0.05);
                }
            }
        } else if (boss instanceof TempestRoc) {
            bolt(level, s.centre);
            for (Player p : players(boss, 48)) {
                if (flat(p.position(), s.centre) < 3.0) {
                    p.hurt(boss.damageSources().lightningBolt(), 12.0f);
                    p.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 30, 1));
                }
            }
        } else if (boss instanceof HollowKing) {
            boss.playSound(SoundEvents.CHAIN_BREAK, 3.0f, 0.4f);
            for (Player p : players(boss, 40)) {
                if (s.marks.containsKey(p.getUUID())) {
                    Vec3 in = boss.position().subtract(p.position()).normalize().scale(1.6);
                    p.push(in.x, 0.5, in.z);
                    p.hurtMarked = true;
                    p.setSecondsOnFire(4);
                }
            }
        } else if (boss instanceof WhiteSilence) {
            List<Player> ps = players(boss, 40);
            if (!ps.isEmpty()) {
                Player p = ps.get(boss.getRandom().nextInt(ps.size()));
                Vec3 behind = p.position().subtract(p.getLookAngle().multiply(1, 0, 1).normalize().scale(3.0));
                level.sendParticles(ParticleTypes.SNOWFLAKE, boss.getX(), boss.getY() + 2, boss.getZ(), 80, 1.0, 2.0, 1.0, 0.05);
                boss.teleportTo(behind.x, p.getY(), behind.z);
                p.setTicksFrozen(p.getTicksRequiredToFreeze() + 160);
                p.hurt(boss.damageSources().freeze(), 8.0f);
                boss.playSound(SoundEvents.GLASS_BREAK, 3.0f, 0.4f);
                for (int k = 0; k < 2; k++) {                                   // and it is not alone in the white
                    PaleMirage m = ModEntities.PALE_MIRAGE.get().create(level);
                    if (m != null) {
                        double a = boss.getRandom().nextDouble() * Math.PI * 2;
                        m.moveTo(p.getX() + Math.cos(a) * 5, p.getY(), p.getZ() + Math.sin(a) * 5, 0, 0);
                        level.addFreshEntity(m);
                    }
                }
            }
        } else if (boss instanceof Kharzul) {
            boss.playSound(SoundEvents.PLAYER_ATTACK_SWEEP, 4.0f, 0.5f);
            for (double a = -60; a <= 60; a += 10) {
                Vec3 d = s.dir.yRot((float) Math.toRadians(a)).scale(5);
                level.sendParticles(ParticleTypes.SWEEP_ATTACK, boss.getX() + d.x, boss.getY() + 1, boss.getZ() + d.z, 1, 0, 0, 0, 0);
            }
            for (Player p : players(boss, 12)) {
                Vec3 rel = p.position().subtract(boss.position());
                Vec3 flatRel = new Vec3(rel.x, 0, rel.z);
                if (flatRel.length() < 10.5 && flatRel.normalize().dot(s.dir) > 0.5) {
                    p.hurt(boss.damageSources().mobAttack(boss), 14.0f);
                    p.addEffect(new MobEffectInstance(MobEffects.WITHER, 60, 1));
                    p.setSecondsOnFire(4);
                }
            }
        } else if (boss instanceof Vexor) {
            boss.playSound(SoundEvents.ENDERMAN_TELEPORT, 4.0f, 0.5f);
            for (Player p : players(boss, 64)) {
                Vec3 m = s.marks.get(p.getUUID());
                if (m != null && p instanceof ServerPlayer sp) {               // the last four seconds never happened
                    level.sendParticles(ParticleTypes.REVERSE_PORTAL, p.getX(), p.getY() + 1, p.getZ(), 40, 0.4, 0.8, 0.4, 0.1);
                    sp.teleportTo(m.x, m.y, m.z);
                    sp.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 2));
                }
            }
            boss.heal(boss.getMaxHealth() * 0.015f);
        } else if (boss instanceof BloomMother) {
            boss.playSound(SoundEvents.PUFFER_FISH_BLOW_UP, 4.0f, 0.5f);
            for (Vec3 q : s.points) {
                level.sendParticles(ParticleTypes.EXPLOSION, q.x, q.y + 0.5, q.z, 1, 0, 0, 0, 0);
                level.sendParticles(ParticleTypes.SPORE_BLOSSOM_AIR, q.x, q.y + 1, q.z, 40, 1.5, 1.0, 1.5, 0.05);
                for (Player p : players(boss, 32)) {
                    if (flat(p.position(), q) < 2.5) {
                        p.hurt(boss.damageSources().mobAttack(boss), 8.0f);
                        p.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 2));
                        p.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 25, 1));
                    }
                }
            }
        } else if (boss instanceof Unmaker) {
            boss.playSound(SoundEvents.WARDEN_SONIC_BOOM, 4.0f, 0.5f);
            for (Player p : players(boss, 64)) {
                if (flat(p.position(), s.centre) > 7.5) {
                    p.hurt(boss.damageSources().magic(), 12.0f);
                    p.addEffect(new MobEffectInstance(MobEffects.WITHER, 80, 1));
                }
            }
        }
    }
}
