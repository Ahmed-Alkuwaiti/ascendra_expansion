package com.unstablefrontiers.debug;

import com.mojang.logging.LogUtils;
import com.unstablefrontiers.ecology.Creatures;
import com.unstablefrontiers.encounter.Elites;
import com.unstablefrontiers.encounter.EncounterManager;
import com.unstablefrontiers.encounter.LandmarkState;
import com.unstablefrontiers.encounter.ZoneState;
import com.unstablefrontiers.entity.AcidGlobEntity;
import com.unstablefrontiers.entity.AnimatedMonster;
import com.unstablefrontiers.entity.ChainedMatriarchEntity;
import com.unstablefrontiers.entity.GnashbackEntity;
import com.unstablefrontiers.entity.ShrikewingEntity;
import com.unstablefrontiers.landmark.FrontierData;
import com.unstablefrontiers.landmark.LandmarkDef;
import com.unstablefrontiers.registry.ModEntities;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.function.IntPredicate;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import org.slf4j.Logger;

/**
 * Continuous-integration only (/frontier debug trial &lt;gnashback|shrikewing|matriarch&gt;): plays each creature's fight
 * against a stand-in target (a motionless iron golem) and checks the mechanics the player relies on: the tell comes before
 * the attack, dodging it works and leaves the creature open, the openings take the damage they promise, and the boss's
 * chains, brood call, acid and leap work in the Great Cage. Each step logs "TRIAL PASS" or "TRIAL FAIL"; the CI script
 * greps them. While a trial runs, the smoke test waits for it.
 */
public final class CreatureTrial {
    private static final Logger LOGGER = LogUtils.getLogger();
    /** Logs every creature state change while a CI run is active. */
    public static final boolean VERBOSE = System.getenv("UF_SMOKE") != null;
    static final Deque<Step> STEPS = new ArrayDeque<>();
    @Nullable
    private static Step current;
    private static int elapsed;
    /** Runs every tick while a trial is active (keeps a landmark fight engaged with nobody standing in it). */
    @Nullable
    static Runnable keepAlive;
    /** What the creature under trial is doing, logged when a step times out. */
    @Nullable
    static java.util.function.Supplier<String> status;

    private record Step(String name, int timeout, IntPredicate body) {}

    /** Registered on the game bus for its tick; the trials themselves are static. */
    public CreatureTrial() {}

    public static boolean running() {
        return current != null || !STEPS.isEmpty();
    }

    public static void log(AnimatedMonster m, int from, int to) {
        if (VERBOSE) {
            LOGGER.info("TRIAL state {} {} -> {} (hp {}/{})", m.getType().toShortString(), from, to, String.format("%.1f", m.getHealth()),
                    String.format("%.1f", m.getMaxHealth()));
        }
    }

    static void step(String name, int timeout, IntPredicate body) {
        STEPS.add(new Step(name, timeout, body));
    }

    static void pass(String what, Object... args) {
        LOGGER.info("TRIAL PASS " + what, args);
    }

    static void fail(String what, Object... args) {
        LOGGER.info("TRIAL FAIL " + what, args);
    }

    @SubscribeEvent
    public void onTick(ServerTickEvent.Post event) {
        if (keepAlive != null && running()) {
            keepAlive.run();
        }
        if (current == null) {
            current = STEPS.poll();
            elapsed = 0;
            if (current == null) {
                return;
            }
        }
        boolean done;
        try {
            done = current.body().test(elapsed);
        } catch (Exception e) {
            fail("{}: {}", current.name(), e.toString());
            LOGGER.error("TRIAL step {} threw", current.name(), e);
            done = true;
        }
        if (!done && ++elapsed > current.timeout()) {
            fail("{}: timed out after {} ticks ({})", current.name(), current.timeout(), status == null ? "-" : status.get());
            done = true;
        }
        if (done) {
            current = null;
        }
    }

    // ---------------------------------------------------------------------------------------------------- arenas
    /** A stone floor high above the terrain with clear air above, and an obsidian wall across its far (+z) end. */
    static void arena(ServerLevel level, BlockPos c) {
        for (int x = -16; x <= 16; x++) {
            for (int z = -16; z <= 24; z++) {
                for (int y = -1; y <= 14; y++) {
                    level.setBlock(c.offset(x, y, z), y == -1 ? Blocks.STONE.defaultBlockState() : Blocks.AIR.defaultBlockState(), 2);
                }
            }
        }
        for (int x = -16; x <= 16; x++) {
            for (int y = 0; y < 4; y++) {
                level.setBlock(c.offset(x, y, 20), Blocks.OBSIDIAN.defaultBlockState(), 2);
            }
        }
    }

    static IronGolem dummy(ServerLevel level, Vec3 at) {
        IronGolem g = EntityType.IRON_GOLEM.create(level);
        g.moveTo(at.x, at.y, at.z, 180, 0);
        g.setNoAi(true);
        g.setPersistenceRequired();
        // a stand-in that cannot die, so a long trial never loses its target (damage still shows as lost health)
        g.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(100000.0D);
        g.setHealth(100000.0F);
        level.addFreshEntity(g);
        return g;
    }

    static <T extends Mob> T spawn(ServerLevel level, EntityType<T> type, Vec3 at) {
        Mob m = Creatures.create(level, type, at, true);
        level.addFreshEntity(m);
        @SuppressWarnings("unchecked") T t = (T) m;
        return t;
    }

    static String describe(AnimatedMonster m) {
        var t = m.getTarget();
        return String.format("state %d, target %s at %.1f, alive %s, on ground %s, no AI %s, pos %s, %s", m.state(),
                t == null ? "none" : t.getType().toShortString(), t == null ? -1.0D : m.distanceTo(t), m.isAlive(), m.onGround(),
                m.isNoAi(), m.blockPosition().toShortString(), m.debugInfo());
    }

    /** Damage dealt by a fixed armour-bypassing hit, after the creature's own rules. */
    static float probe(Mob m, float amount) {
        float before = m.getHealth();
        m.invulnerableTime = 0;
        m.hurt(m.level().damageSources().magic(), amount);
        m.invulnerableTime = 0;
        return before - m.getHealth();
    }

    // ------------------------------------------------------------------------------------------------- Gnashback
    public static void gnashback(ServerLevel level, BlockPos c) {
        GnashbackEntity[] g = new GnashbackEntity[1];
        IronGolem[] dummy = new IronGolem[1];
        float[] idleHit = new float[1];
        float[] dummyHp = new float[1];
        step("gnashback setup", 5, t -> {
            arena(level, c);
            g[0] = spawn(level, ModEntities.GNASHBACK.get(), Vec3.atBottomCenterOf(c));
            dummy[0] = dummy(level, Vec3.atBottomCenterOf(c.offset(0, 0, 11)));
            g[0].setTarget(dummy[0]);
            status = () -> describe(g[0]);
            LOGGER.info("TRIAL gnashback hp {} armor {} attack {}", g[0].getMaxHealth(), g[0].getArmorValue(),
                    g[0].getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_DAMAGE));
            return true;
        });
        step("gnashback idle damage", 5, t -> {
            idleHit[0] = probe(g[0], 10);
            g[0].setTarget(dummy[0]);
            return true;
        });
        step("gnashback tells its charge", 300, t -> {
            g[0].setTarget(dummy[0]);
            if (g[0].distanceTo(dummy[0]) < 8 && g[0].state() == GnashbackEntity.IDLE) {
                g[0].teleportTo(c.getX() + 0.5D, c.getY(), c.getZ() + 0.5D);   // back off to charging range, as a player would
            }
            if (g[0].state() == GnashbackEntity.TELL) {
                pass("gnashback tells its charge (scrape) before charging");
                return true;
            }
            return false;
        });
        step("gnashback sidestep", 120, t -> {   // the rest of the tell, then the whole charge
            if (t == 18) {
                dummy[0].teleportTo(c.getX() + 7.5D, c.getY(), c.getZ() + 11.5D);   // step aside late in the tell
            }
            if (g[0].state() == GnashbackEntity.STUNNED) {
                pass("a dodged charge into a wall stuns the gnashback");
                return true;
            }
            if (t > 18 && g[0].state() == GnashbackEntity.IDLE) {
                fail("dodged gnashback charge ended without a stun");
                return true;
            }
            return false;
        });
        step("gnashback stunned damage", 5, t -> {
            float stunned = probe(g[0], 10);
            if (stunned > idleHit[0] * 1.7F) {
                pass("stunned gnashback takes {} from a hit that deals {} normally", stunned, idleHit[0]);
            } else {
                fail("stunned gnashback took {} vs {} normally", stunned, idleHit[0]);
            }
            return true;
        });
        step("gnashback recovers", 200, t -> g[0].state() == GnashbackEntity.IDLE);
        step("gnashback charge hits", 400, t -> {
            if (t == 0) {
                dummy[0].teleportTo(c.getX() + 0.5D, c.getY(), c.getZ() + 10.5D);
                dummyHp[0] = dummy[0].getHealth();
            }
            g[0].setTarget(dummy[0]);
            if (dummy[0].getHealth() < dummyHp[0] - 5) {
                pass("an undodged gnashback charge hits for {}", dummyHp[0] - dummy[0].getHealth());
                return true;
            }
            if (g[0].distanceTo(dummy[0]) < 8 && g[0].state() == GnashbackEntity.IDLE) {
                g[0].teleportTo(c.getX() + 0.5D, c.getY(), c.getZ() + 0.5D);
                dummyHp[0] = dummy[0].getHealth();   // bites do not count: only the charge
            }
            return false;
        });
        step("gnashback cleanup", 2, t -> {
            g[0].discard();
            dummy[0].discard();
            return true;
        });
    }

    // ------------------------------------------------------------------------------------------------ Shrikewing
    public static void shrikewing(ServerLevel level, BlockPos c) {
        ShrikewingEntity[] s = new ShrikewingEntity[1];
        IronGolem[] dummy = new IronGolem[1];
        float[] hp = new float[1];
        step("shrikewing setup", 5, t -> {
            arena(level, c);
            s[0] = spawn(level, ModEntities.SHRIKEWING.get(), Vec3.atBottomCenterOf(c.offset(0, 10, 0)));
            dummy[0] = dummy(level, Vec3.atBottomCenterOf(c.offset(0, 0, 6)));
            s[0].setTarget(dummy[0]);
            status = () -> describe(s[0]);
            LOGGER.info("TRIAL shrikewing hp {} armor {}", s[0].getMaxHealth(), s[0].getArmorValue());
            return true;
        });
        step("shrikewing flies", 60, t -> {
            if (t == 59) {
                if (s[0].getY() > c.getY() + 3) {
                    pass("shrikewing stays aloft (y {} over floor {})", (int) s[0].getY(), c.getY());
                } else {
                    fail("shrikewing fell to y {}", (int) s[0].getY());
                }
                return true;
            }
            s[0].setTarget(dummy[0]);
            return false;
        });
        step("shrikewing tells its dive", 600, t -> {
            s[0].setTarget(dummy[0]);
            if (s[0].state() == ShrikewingEntity.TELL) {
                pass("shrikewing screeches and marks the spot before diving");
                return true;
            }
            return false;
        });
        step("shrikewing dodged dive", 120, t -> {
            if (t == 12) {
                dummy[0].teleportTo(dummy[0].getX() + 8, dummy[0].getY(), dummy[0].getZ());   // leave the ring after it locks
            }
            if (s[0].state() == ShrikewingEntity.GROUNDED || s[0].state() == ShrikewingEntity.RECOVER) {
                pass(s[0].state() == ShrikewingEntity.GROUNDED ? "a dodged dive grounds the shrikewing"
                        : "a dodged dive leaves the shrikewing climbing (open)");
                return true;
            }
            return false;
        });
        step("shrikewing dive hits", 900, t -> {
            if (t == 0) {
                hp[0] = dummy[0].getHealth();
            }
            s[0].setTarget(dummy[0]);
            if (dummy[0].getHealth() < hp[0] - 3) {
                pass("an undodged dive hits for {}", hp[0] - dummy[0].getHealth());
                return true;
            }
            return false;
        });
        step("shrikewing cleanup", 2, t -> {
            s[0].discard();
            dummy[0].discard();
            return true;
        });
    }

    // ---------------------------------------------------------------------------------------- the Chained Matriarch
    public static void matriarch(ServerLevel level, BlockPos at) {
        LandmarkState[] s = new LandmarkState[1];
        LandmarkDef[] def = new LandmarkDef[1];
        ChainedMatriarchEntity[] m = new ChainedMatriarchEntity[1];
        IronGolem[] dummy = new IronGolem[1];
        boolean[] seen = new boolean[16];
        step("matriarch dormant", 10, t -> {
            s[0] = EncounterManager.at(level, at, 8);
            def[0] = s[0] == null ? null : FrontierData.landmark(s[0].id);
            if (def[0] == null) {
                fail("no Great Cage at {}", at);
                STEPS.clear();
                return true;
            }
            ZoneState zs0 = s[0].zone(def[0].zone("finale"));
            keepAlive = () -> zs0.lastEngaged = level.getGameTime();
            EncounterManager.force(level, s[0], "finale", "reset", null);
            EncounterManager.wake(level, s[0], def[0], level.getGameTime());
            ZoneState zs = s[0].zone(def[0].zone("finale"));
            if (zs.elite != null && level.getEntity(zs.elite) instanceof ChainedMatriarchEntity cm && cm.isNoAi()) {
                m[0] = cm;
                pass("the Matriarch waits in the cage before the fight (dormant, hp {})", cm.getMaxHealth());
                float d = probe(cm, 50);
                if (d == 0) {
                    pass("the dormant Matriarch cannot be hurt");
                } else {
                    fail("the dormant Matriarch took {}", d);
                }
            } else {
                fail("no dormant Matriarch placed (elite {})", zs.elite);
            }
            return true;
        });
        step("matriarch fight starts", 10, t -> {
            net.minecraft.server.level.ServerPlayer by = net.neoforged.neoforge.common.util.FakePlayerFactory.getMinecraft(level);
            by.moveTo(Vec3.atBottomCenterOf(s[0].world(def[0].zone("finale").centre())));
            EncounterManager.force(level, s[0], "finale", "start", by);
            ZoneState zs = s[0].zone(def[0].zone("finale"));
            if (zs.status == ZoneState.Status.ACTIVE && m[0] != null && m[0].isAlive() && !m[0].isNoAi() && m[0].isChained()) {
                pass("the key wakes the same Matriarch, chained");
            } else {
                fail("fight start: status {} matriarch {}", zs.status, m[0]);
                m[0] = level.getEntity(zs.elite) instanceof ChainedMatriarchEntity cm ? cm : null;
            }
            if (m[0] == null) {
                STEPS.clear();
                return true;
            }
            Vec3 front = m[0].position().add(Vec3.directionFromRotation(0, m[0].getYRot()).scale(4.0D));
            dummy[0] = dummy(level, front);
            m[0].setTarget(dummy[0]);
            status = () -> describe(m[0]);
            return true;
        });
        step("matriarch chained damage", 3, t -> {
            float d = probe(m[0], 20);
            if (d > 4 && d < 10) {
                pass("chained, she takes {} of 20", d);
            } else {
                fail("chained, she took {} of 20 (expected about 7)", d);
            }
            return true;
        });
        step("matriarch sweeps at close range", 400, t -> {
            m[0].setTarget(dummy[0]);
            seen[m[0].state()] = true;
            if (seen[ChainedMatriarchEntity.SWEEP_TELL] && seen[ChainedMatriarchEntity.SWEEP]) {
                pass("scythe sweep: tell then strike");
                return true;
            }
            return false;
        });
        step("matriarch spits at range", 600, t -> {
            if (t == 0) {
                Vec3 far = m[0].position().add(Vec3.directionFromRotation(0, m[0].getYRot()).scale(8.0D));
                dummy[0].teleportTo(far.x, far.y + 1, far.z);
            }
            m[0].setTarget(dummy[0]);
            AABB area = m[0].getBoundingBox().inflate(30);
            if (!level.getEntitiesOfClass(AcidGlobEntity.class, area).isEmpty() || !level.getEntitiesOfClass(AreaEffectCloud.class, area).isEmpty()) {
                pass("acid volley thrown (spit tell seen: {})", seen[ChainedMatriarchEntity.SPIT_TELL] || m[0].state() >= 3);
                return true;
            }
            return false;
        });
        step("matriarch brood call", 900, t -> {
            m[0].setTarget(dummy[0]);
            if (m[0].state() == ChainedMatriarchEntity.BROOD) {
                float d = probe(m[0], 20);
                if (d > 25) {
                    pass("brood call: the open sac takes {} of 20 even while chained", d);
                } else {
                    fail("brood call: the sac took only {} of 20", d);
                }
                return true;
            }
            return false;
        });
        step("matriarch escorts arrive", 80, t -> {
            ZoneState zs = s[0].zone(def[0].zone("finale"));
            if (t == 79) {
                LOGGER.info("TRIAL finale holds {} creatures after the brood call", zs.mobs.size());
                if (zs.mobs.size() > 1) {
                    pass("brood call brought escorts ({} in the fight)", zs.mobs.size());
                } else {
                    fail("brood call brought nobody");
                }
                return true;
            }
            return false;
        });
        step("matriarch chains snap", 100, t -> {
            if (t == 0) {
                for (BlockPos p : Elites.pylons(level, s[0], def[0].zone("finale"))) {
                    level.setBlock(p, Blocks.AIR.defaultBlockState(), 3);
                }
            }
            if (!m[0].isChained() && (m[0].state() == ChainedMatriarchEntity.ROAR || t > 50)) {
                pass("breaking the pylons frees her (roar)");
                return true;
            }
            return false;
        });
        step("matriarch free damage", 60, t -> {
            if (m[0].state() == ChainedMatriarchEntity.BROOD) {
                return false;
            }
            float d = probe(m[0], 20);
            if (d > 15 && d < 25) {
                pass("free, she takes {} of 20", d);
            } else {
                fail("free, she took {} of 20", d);
            }
            return true;
        });
        step("matriarch leaps", 900, t -> {
            if (t == 0) {
                Vec3 far = m[0].position().add(Vec3.directionFromRotation(0, m[0].getYRot()).scale(12.0D));
                dummy[0].teleportTo(far.x, far.y + 1, far.z);
            }
            m[0].setTarget(dummy[0]);
            seen[m[0].state()] = true;
            if (seen[ChainedMatriarchEntity.LEAP_TELL] && seen[ChainedMatriarchEntity.LEAP] && m[0].state() == ChainedMatriarchEntity.IDLE) {
                pass("leap: crouch and landing ring, then the jump (landed {} blocks from the dummy)",
                        String.format("%.1f", m[0].position().distanceTo(dummy[0].position())));
                return true;
            }
            return false;
        });
        step("matriarch dies and the cage opens", 200, t -> {
            if (t == 0) {
                m[0].kill();
            }
            ZoneState zs = s[0].zone(def[0].zone("finale"));
            if (zs.status == ZoneState.Status.CLEARED) {
                pass("killing her clears the Great Cage (gates open {})", s[0].openGates);
                return true;
            }
            return false;
        });
        step("matriarch cleanup", 2, t -> {
            if (dummy[0] != null) {
                dummy[0].discard();
            }
            keepAlive = null;
            return true;
        });
    }
}
