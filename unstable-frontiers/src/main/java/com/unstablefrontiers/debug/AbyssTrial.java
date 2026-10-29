package com.unstablefrontiers.debug;

import static com.unstablefrontiers.debug.CreatureTrial.describe;
import static com.unstablefrontiers.debug.CreatureTrial.dummy;
import static com.unstablefrontiers.debug.CreatureTrial.fail;
import static com.unstablefrontiers.debug.CreatureTrial.pass;
import static com.unstablefrontiers.debug.CreatureTrial.probe;
import static com.unstablefrontiers.debug.CreatureTrial.spawn;
import static com.unstablefrontiers.debug.CreatureTrial.step;

import com.mojang.logging.LogUtils;
import com.unstablefrontiers.abyss.AbyssDimension;
import com.unstablefrontiers.abyss.AbyssPlaces;
import com.unstablefrontiers.abyss.AbyssTerrain;
import com.unstablefrontiers.abyss.AbyssTravel;
import com.unstablefrontiers.abyss.EclipseEncounter;
import com.unstablefrontiers.block.AbyssGateBlock;
import com.unstablefrontiers.block.RiftEngineBlock;
import com.unstablefrontiers.encounter.EncounterManager;
import com.unstablefrontiers.encounter.LandmarkState;
import com.unstablefrontiers.entity.EclipseLeviathanEntity;
import com.unstablefrontiers.entity.LumenMiteEntity;
import com.unstablefrontiers.entity.OrreryWardenEntity;
import com.unstablefrontiers.entity.StarBoltEntity;
import com.unstablefrontiers.landmark.FrontierData;
import com.unstablefrontiers.landmark.LandmarkDef;
import com.unstablefrontiers.registry.AbyssRegistry;
import com.unstablefrontiers.registry.ModEntities;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import org.slf4j.Logger;

/**
 * Continuous-integration only: the Rift Observatory's engine and gates, the Astral Abyss's places and void safety, the
 * Orrery Warden, the Lumen Mite and the Eclipse Leviathan, each step logged as "TRIAL PASS" or "TRIAL FAIL" (see
 * {@link CreatureTrial}, whose step runner these share).
 */
public final class AbyssTrial {
    private static final Logger LOGGER = LogUtils.getLogger();

    private AbyssTrial() {}

    private static boolean standable(ServerLevel level, BlockPos feet) {
        return level.getBlockState(feet).getCollisionShape(level, feet).isEmpty()
                && level.getBlockState(feet.above()).getCollisionShape(level, feet.above()).isEmpty()
                && !level.getBlockState(feet.below()).getCollisionShape(level, feet.below()).isEmpty();
    }

    // ------------------------------------------------------------------------------------------ the observatory
    /** At a built Rift Observatory: the dome is sealed until the Hall and the Vaults fall; the engine takes its parts and opens the gate. */
    public static void observatory(ServerLevel level, BlockPos at) {
        LandmarkState[] s = new LandmarkState[1];
        LandmarkDef[] def = new LandmarkDef[1];
        step("observatory found", 5, t -> {
            s[0] = EncounterManager.at(level, at, 16);
            def[0] = s[0] == null ? null : FrontierData.landmark(s[0].id);
            if (def[0] == null || !s[0].id.getPath().equals("rift_observatory")) {
                fail("no Rift Observatory at {}", at);
                CreatureTrial.STEPS.clear();
                return true;
            }
            if (!EncounterManager.requirementsMet(s[0], def[0], def[0].zone("dome"))) {
                pass("the Lens Dome is sealed until the Orrery Hall and the Coolant Vaults are cleared");
            } else {
                fail("the Lens Dome is open from the start");
            }
            return true;
        });
        step("observatory hall and vaults", 40, t -> {
            ServerPlayer by = FakePlayerFactory.getMinecraft(level);
            by.moveTo(Vec3.atBottomCenterOf(s[0].world(def[0].zone("hall").centre())));
            EncounterManager.force(level, s[0], "hall", "clear", by);
            EncounterManager.force(level, s[0], "vaults", "clear", by);
            if (EncounterManager.requirementsMet(s[0], def[0], def[0].zone("dome"))) {
                pass("clearing the Hall and the Vaults unseals the Lens Dome");
            } else {
                fail("the Lens Dome stays sealed after the Hall and the Vaults");
            }
            return true;
        });
        step("observatory engine", 20, t -> {
            BlockPos engine = s[0].world(def[0].points().get("engine"));
            ServerPlayer by = FakePlayerFactory.getMinecraft(level);
            by.moveTo(Vec3.atBottomCenterOf(engine.south(2)));
            BlockState st = level.getBlockState(engine);
            if (!st.is(AbyssRegistry.RIFT_ENGINE.get())) {
                fail("no rift engine at the engine point {} ({})", engine.toShortString(), st);
                return true;
            }
            BlockPos gate = s[0].world(def[0].points().get("gate")).north();
            boolean closedBefore = level.getBlockState(gate).is(AbyssRegistry.ABYSS_GATE.get()) && !level.getBlockState(gate).getValue(AbyssGateBlock.OPEN);
            Item[] parts = {AbyssRegistry.STAR_CHART.get(), AbyssRegistry.COOLANT_HEART.get(), AbyssRegistry.FOCUSING_LENS.get()};
            int taken = 0;
            for (Item part : parts) {
                ItemStack stack = new ItemStack(part);
                BlockHitResult hit = new BlockHitResult(Vec3.atCenterOf(engine), Direction.UP, engine, false);
                level.getBlockState(engine).useItemOn(stack, level, by, InteractionHand.MAIN_HAND, hit);
                taken += stack.isEmpty() ? 1 : 0;
            }
            BlockState after = level.getBlockState(engine);
            boolean open = level.getBlockState(gate).is(AbyssRegistry.ABYSS_GATE.get()) && level.getBlockState(gate).getValue(AbyssGateBlock.OPEN);
            if (taken == 3 && after.getValue(RiftEngineBlock.ACTIVE)) {
                pass("the engine takes its three parts in any order and wakes");
            } else {
                fail("engine took {} parts, active {}", taken, after.getValue(RiftEngineBlock.ACTIVE));
            }
            if (closedBefore && open) {
                pass("the waking engine opens the rift gate (closed before, open after)");
            } else {
                fail("rift gate at {}: closed before {}, open after {}", gate.toShortString(), closedBefore, open);
            }
            boolean lift = s[0].openGates.contains("lift") && def[0].gates().get("lift").stream().allMatch(p -> level.getBlockState(s[0].world(p)).isAir());
            if (lift) {
                pass("the waking engine unseals the lift up the Lens Tower");
            } else {
                fail("the lift is still sealed (open gates {})", s[0].openGates);
            }
            ItemStack extra = new ItemStack(AbyssRegistry.FOCUSING_LENS.get());
            level.getBlockState(engine).useItemOn(extra, level, by, InteractionHand.MAIN_HAND, new BlockHitResult(Vec3.atCenterOf(engine), Direction.UP, engine, false));
            if (!extra.isEmpty()) {
                pass("a woken engine takes no more parts");
            } else {
                fail("a woken engine swallowed another part");
            }
            return true;
        });
    }

    // ------------------------------------------------------------------------------------------- the abyss itself
    /** In the Astral Abyss: every place builds onto its island, arrivals stand on solid ground, the void catches falls and items. */
    public static void places(ServerLevel level) {
        step("abyss places", 60, t -> {
            if (!AbyssDimension.is(level)) {
                fail("not in the Astral Abyss");
                return true;
            }
            for (AbyssTerrain.Anchor a : AbyssTerrain.ANCHORS) {
                AbyssPlaces.build(level, a);
                LandmarkState s = EncounterManager.at(level, BlockPos.containing(AbyssPlaces.standing(a)), 64);
                Vec3 spot = AbyssPlaces.safeSpot(level, a);
                boolean ok = s != null && standable(level, BlockPos.containing(spot));
                if (ok) {
                    pass("{} built on its island; safe ground at {}", a.name(), BlockPos.containing(spot).toShortString());
                } else {
                    fail("{}: landmark {}, safe spot {} standable {}", a.name(), s == null ? "missing" : s.id, spot,
                            standable(level, BlockPos.containing(spot)));
                }
            }
            BlockPos arrival = BlockPos.containing(AbyssTravel.arrival());
            if (standable(level, arrival)) {
                pass("arrivals stand on the landing ({})", arrival.toShortString());
            } else {
                fail("the arrival point {} is not safe ground", arrival.toShortString());
            }
            LandmarkState landing = EncounterManager.at(level, arrival, 32);
            LandmarkDef ld = landing == null ? null : FrontierData.landmark(landing.id);
            BlockPos gate = ld == null ? null : landing.world(ld.points().get("gate")).above();
            if (gate != null && level.getBlockState(gate).is(AbyssRegistry.ABYSS_GATE.get()) && level.getBlockState(gate).getValue(AbyssGateBlock.OPEN)) {
                pass("the landing's return gate stands open");
            } else {
                fail("the landing's return gate is missing or closed ({})", gate == null ? "-" : level.getBlockState(gate));
            }
            Vec3 crown = EclipseEncounter.center();
            if (standable(level, BlockPos.containing(crown))) {
                pass("the Hollow Crown's floor is solid at the arena's middle");
            } else {
                fail("the Hollow Crown's middle {} is not solid ground", BlockPos.containing(crown).toShortString());
            }
            if (AbyssDimension.crowded(level, AbyssTravel.arrival())) {
                pass("nothing spawns naturally on the landing");
            } else {
                fail("natural spawns are allowed on the landing");
            }
            return true;
        });
        step("abyss void catch", 10, t -> {
            ServerPlayer p = FakePlayerFactory.getMinecraft(level);
            p.setHealth(p.getMaxHealth());
            p.moveTo(140, 8, -60);
            AbyssTravel.catchFall(p);
            BlockPos feet = p.blockPosition();
            float lost = p.getMaxHealth() - p.getHealth();
            if (standable(level, feet) && lost > 0 && p.getHealth() >= 1) {
                pass("a fall into the void is caught: back on safe ground at {} for {} of {} health", feet.toShortString(), lost, p.getMaxHealth());
            } else {
                fail("void catch put the player at {} (standable {}), health {}", feet.toShortString(), standable(level, feet), p.getHealth());
            }
            p.setHealth(1.0F);
            p.moveTo(140, 8, -60);
            AbyssTravel.catchFall(p);
            if (p.getHealth() >= 1.0F && p.isAlive()) {
                pass("the catch never takes the last of a player's health");
            } else {
                fail("the catch killed a player on 1 health");
            }
            return true;
        });
        ItemEntity[] item = new ItemEntity[1];
        step("abyss item rescue", 60, t -> {
            if (t == 0) {
                item[0] = new ItemEntity(level, 300, 12, 300, new ItemStack(Items.DIAMOND));
                level.addFreshEntity(item[0]);
                return false;
            }
            if (item[0].getY() > AbyssDimension.CATCH_Y + 8) {
                pass("an item dropped into the void drifts to a station ({})", item[0].blockPosition().toShortString());
                item[0].discard();
                return true;
            }
            if (t == 59) {
                fail("the dropped item fell away (y {})", (int) item[0].getY());
                item[0].discard();
            }
            return false;
        });
    }

    // --------------------------------------------------------------------------------------------- the creatures
    public static void warden(ServerLevel level, BlockPos c) {
        OrreryWardenEntity[] w = new OrreryWardenEntity[1];
        IronGolem[] dummy = new IronGolem[1];
        float[] idle = new float[1];
        float[] hp = new float[1];
        step("warden setup", 5, t -> {
            CreatureTrial.arena(level, c);
            w[0] = spawn(level, ModEntities.ORRERY_WARDEN.get(), Vec3.atBottomCenterOf(c.offset(0, 2, 0)));
            dummy[0] = dummy(level, Vec3.atBottomCenterOf(c.offset(0, 0, 10)));
            w[0].setTarget(dummy[0]);
            CreatureTrial.status = () -> describe(w[0]);
            LOGGER.info("TRIAL orrery_warden hp {} armor {}", w[0].getMaxHealth(), w[0].getArmorValue());
            idle[0] = probe(w[0], 10);
            return true;
        });
        step("warden tells its beam", 400, t -> {
            w[0].setTarget(dummy[0]);
            if (w[0].state() == OrreryWardenEntity.BEAM_TELL) {
                hp[0] = dummy[0].getHealth();
                pass("orrery warden aligns its rings (tell) before the beam");
                return true;
            }
            return false;
        });
        step("warden beam hits in the open", 120, t -> {
            w[0].setTarget(dummy[0]);
            if (dummy[0].getHealth() < hp[0] - 1) {
                pass("the beam hits a target in the open for {}", hp[0] - dummy[0].getHealth());
                return true;
            }
            return false;
        });
        step("warden stalls", 120, t -> {
            if (w[0].state() == OrreryWardenEntity.STALLED) {
                float d = probe(w[0], 10);
                if (d > idle[0] * 1.7F) {
                    pass("after the beam it stalls and takes {} from a hit that deals {} normally", d, idle[0]);
                } else {
                    fail("stalled warden took {} vs {} normally", d, idle[0]);
                }
                return true;
            }
            return false;
        });
        boolean[] walled = new boolean[1];
        step("warden beam blocked by cover", 900, t -> {
            w[0].setTarget(dummy[0]);
            if (!walled[0] && w[0].state() == OrreryWardenEntity.BEAM_TELL) {
                // the stand-in ducks into cover while the rings align: an obsidian shell around it
                BlockPos d = dummy[0].blockPosition();
                for (BlockPos p : BlockPos.betweenClosed(d.offset(-2, 0, -2), d.offset(2, 4, 2))) {
                    if (Math.abs(p.getX() - d.getX()) == 2 || Math.abs(p.getZ() - d.getZ()) == 2 || p.getY() == d.getY() + 4) {
                        level.setBlock(p, Blocks.OBSIDIAN.defaultBlockState(), 2);
                    }
                }
                hp[0] = dummy[0].getHealth();
                walled[0] = true;
            }
            if (walled[0] && w[0].state() == OrreryWardenEntity.STALLED) {
                float lost = hp[0] - dummy[0].getHealth();
                if (lost < 1) {
                    pass("cover taken during the tell stops the beam");
                } else {
                    fail("the beam went through cover for {}", lost);
                }
                return true;
            }
            return false;
        });
        step("warden cleanup", 2, t -> {
            w[0].discard();
            dummy[0].discard();
            return true;
        });
    }

    public static void mite(ServerLevel level, BlockPos c) {
        LumenMiteEntity[] m = new LumenMiteEntity[1];
        IronGolem[] dummy = new IronGolem[1];
        boolean[] told = new boolean[1];
        step("mite setup", 5, t -> {
            CreatureTrial.arena(level, c);
            m[0] = spawn(level, ModEntities.LUMEN_MITE.get(), Vec3.atBottomCenterOf(c.offset(0, 4, 0)));
            dummy[0] = dummy(level, Vec3.atBottomCenterOf(c.offset(0, 0, 9)));
            m[0].setTarget(dummy[0]);
            CreatureTrial.status = () -> describe(m[0]);
            LOGGER.info("TRIAL lumen_mite hp {}", m[0].getMaxHealth());
            return true;
        });
        step("mite flies", 60, t -> {
            m[0].setTarget(dummy[0]);
            if (t == 59) {
                if (m[0].getY() > c.getY() + 1.5D) {
                    pass("lumen mite stays aloft (y {} over floor {})", (int) m[0].getY(), c.getY());
                } else {
                    fail("lumen mite fell to y {}", (int) m[0].getY());
                }
                return true;
            }
            return false;
        });
        step("mite tells and spits", 600, t -> {
            m[0].setTarget(dummy[0]);
            told[0] |= m[0].state() == LumenMiteEntity.TELL;
            List<StarBoltEntity> bolts = level.getEntitiesOfClass(StarBoltEntity.class, new AABB(c).inflate(30));
            if (!bolts.isEmpty()) {
                if (told[0]) {
                    pass("lumen mite swells (tell) before it spits a star bolt");
                } else {
                    fail("a star bolt came with no tell");
                }
                return true;
            }
            return false;
        });
        step("star bolts expire", 100, t -> {
            List<StarBoltEntity> bolts = level.getEntitiesOfClass(StarBoltEntity.class, new AABB(c).inflate(60));
            if (bolts.isEmpty()) {
                pass("star bolts are gone within {} ticks", t);
                return true;
            }
            if (t == 99) {
                fail("{} star bolts still alive after 100 ticks", bolts.size());
            }
            return false;
        });
        step("mite cleanup", 2, t -> {
            m[0].discard();
            dummy[0].discard();
            return true;
        });
    }

    // ---------------------------------------------------------------------------------------- the Eclipse Leviathan
    /** At the Hollow Crown: the altar calls it, the intro shields it, its attacks are told, phases, mites, the eclipse,
     *  abandonment resets it, the charged altar calls it again, its state survives saving, and the victory pays out. */
    public static void leviathan(ServerLevel level) {
        EclipseLeviathanEntity[] lev = new EclipseLeviathanEntity[1];
        IronGolem[] dummy = new IronGolem[1];
        BlockPos[] altar = new BlockPos[1];
        ServerPlayer[] by = new ServerPlayer[1];
        boolean[] seen = new boolean[16];
        float[] normal = new float[1];
        step("leviathan summon", 40, t -> {
            AbyssPlaces.build(level, AbyssTerrain.HOLLOW_CROWN);
            Vec3 c = EclipseEncounter.center();
            LandmarkState s = EncounterManager.at(level, BlockPos.containing(c), 64);
            LandmarkDef def = s == null ? null : FrontierData.landmark(s.id);
            altar[0] = def == null ? null : s.world(def.points().get("altar"));
            if (altar[0] == null || !level.getBlockState(altar[0]).is(AbyssRegistry.ECLIPSE_ALTAR.get())) {
                fail("no Eclipse Altar at the Hollow Crown ({})", altar[0]);
                CreatureTrial.STEPS.clear();
                return true;
            }
            EclipseEncounter.forceReset(level);
            EclipseEncounter.trialHold = true;
            by[0] = FakePlayerFactory.getMinecraft(level);
            by[0].moveTo(c.x, c.y, c.z + 6);
            dummy[0] = dummy(level, c.add(8, 0, 4));
            EclipseLeviathanEntity.TRIAL_TARGETS.clear();
            EclipseLeviathanEntity.TRIAL_TARGETS.add(dummy[0]);
            boolean used = EclipseEncounter.summon(level, altar[0], by[0]);
            EclipseEncounter e = EclipseEncounter.get(level);
            lev[0] = e.boss() != null && level.getEntity(e.boss()) instanceof EclipseLeviathanEntity l ? l : null;
            if (lev[0] != null && used) {
                e.addParticipant(by[0].getUUID());
                pass("the altar takes the sigil and the Leviathan rises (hp {}, armor {})", lev[0].getMaxHealth(), lev[0].getArmorValue());
                CreatureTrial.status = () -> describe(lev[0]);
            } else {
                fail("summon: sigil used {}, boss {}", used, lev[0]);
                CreatureTrial.STEPS.clear();
                EclipseEncounter.trialHold = false;
            }
            return true;
        });
        step("leviathan intro shield", 5, t -> {
            float d = probe(lev[0], 50);
            if (d == 0) {
                pass("the rising Leviathan cannot be hurt");
            } else {
                fail("the rising Leviathan took {}", d);
            }
            if (EclipseEncounter.summon(level, altar[0], by[0])) {
                fail("a second Leviathan was called while one is awake");
            } else {
                pass("only one Leviathan at a time");
            }
            return true;
        });
        step("leviathan phase one attacks", 1800, t -> {
            seen[lev[0].state()] = true;
            if (lev[0].state() == EclipseLeviathanEntity.CIRCLE && normal[0] == 0) {
                normal[0] = probe(lev[0], 10);
            }
            if (seen[EclipseLeviathanEntity.BEAM_TELL] && seen[EclipseLeviathanEntity.BEAM] && seen[EclipseLeviathanEntity.PASS_TELL]
                    && seen[EclipseLeviathanEntity.PASS] && seen[EclipseLeviathanEntity.WELL_TELL] && seen[EclipseLeviathanEntity.WELL]) {
                pass("phase one: beam, low pass and gravity well, each with its tell (stand-in lost {})",
                        String.format("%.0f", dummy[0].getMaxHealth() - dummy[0].getHealth()));
                return true;
            }
            return false;
        });
        step("leviathan stays in its arena", 1, t -> {
            Vec3 c = lev[0].center();
            double d = Math.hypot(lev[0].getX() - c.x, lev[0].getZ() - c.z);
            if (d < EclipseEncounter.ARENA_RADIUS) {
                pass("the Leviathan keeps to its arena ({} blocks from the middle)", String.format("%.1f", d));
            } else {
                fail("the Leviathan strayed {} blocks from the middle", d);
            }
            return true;
        });
        step("leviathan phase two", 400, t -> {
            if (t == 0) {
                lev[0].invulnerableTime = 0;
                lev[0].setHealth(lev[0].getMaxHealth() * 0.7F);
                probe(lev[0], lev[0].getMaxHealth() * 0.06F);
            }
            if (lev[0].phase() == 2) {
                pass("phase two at two thirds of its health, with a roar (state {})", lev[0].state());
                return true;
            }
            return false;
        });
        step("leviathan calls mites", 2400, t -> {
            List<LumenMiteEntity> mites = level.getEntitiesOfClass(LumenMiteEntity.class, new AABB(BlockPos.containing(lev[0].center())).inflate(60));
            if (mites.size() > EclipseLeviathanEntity.MAX_MITES) {
                fail("{} mites alive, over the cap of {}", mites.size(), EclipseLeviathanEntity.MAX_MITES);
                return true;
            }
            if (!mites.isEmpty() && lev[0].state() == EclipseLeviathanEntity.CIRCLE) {
                pass("phase two calls Lumen Mites ({} alive, never more than {})", mites.size(), EclipseLeviathanEntity.MAX_MITES);
                return true;
            }
            return false;
        });
        step("leviathan phase three and the eclipse", 3000, t -> {
            if (t == 0) {
                lev[0].invulnerableTime = 0;
                lev[0].setHealth(lev[0].getMaxHealth() * 0.36F);
                probe(lev[0], lev[0].getMaxHealth() * 0.05F);
            }
            if (lev[0].state() == EclipseLeviathanEntity.EXPOSED) {
                float d = probe(lev[0], 10);
                if (lev[0].phase() == 3 && d > normal[0] * 1.7F) {
                    pass("phase three: the eclipse dive leaves it exposed, taking {} from a hit that deals {} normally", d, normal[0]);
                } else {
                    fail("exposed: phase {}, took {} vs {} normally", lev[0].phase(), d, normal[0]);
                }
                return true;
            }
            return false;
        });
        step("leviathan save and load", 5, t -> {
            CompoundTag tag = new CompoundTag();
            lev[0].saveWithoutId(tag);
            EclipseLeviathanEntity copy = ModEntities.ECLIPSE_LEVIATHAN.get().create(level);
            copy.load(tag);
            if (copy.phase() == lev[0].phase() && copy.center().distanceTo(lev[0].center()) < 0.01D && copy.mites().size() == lev[0].mites().size()) {
                pass("its phase, arena and mites survive a save and load");
            } else {
                fail("after load: phase {} vs {}, center {} vs {}", copy.phase(), lev[0].phase(), copy.center(), lev[0].center());
            }
            EclipseLeviathanEntity orphan = ModEntities.ECLIPSE_LEVIATHAN.get().create(level);
            orphan.moveTo(lev[0].center().add(0, 30, 0));
            if (!level.addFreshEntity(orphan)) {
                pass("a Leviathan with no fight to belong to is turned away");
            } else {
                fail("an orphan Leviathan joined the world");
                orphan.discard();
            }
            return true;
        });
        step("leviathan abandoned", EclipseEncounter.ABANDON_TICKS + 200, t -> {
            if (t == 0) {
                EclipseEncounter.trialHold = false;
            }
            EclipseEncounter e = EclipseEncounter.get(level);
            if (!e.active()) {
                int mites = level.getEntitiesOfClass(LumenMiteEntity.class, new AABB(BlockPos.containing(lev[0].center())).inflate(60),
                        m -> m.getPersistentData().getBoolean(EclipseEncounter.ADD_TAG)).size();
                if (!lev[0].isAlive() || lev[0].isRemoved()) {
                    pass("with nobody in the arena for {} s the fight resets: boss gone, {} of its mites left, altar charged {}", t / 20, mites, e.charged());
                } else {
                    fail("fight reset but the boss is still here");
                }
                return true;
            }
            return false;
        });
        step("leviathan recalled for free", 20, t -> {
            EclipseEncounter.trialHold = true;
            boolean used = EclipseEncounter.summon(level, altar[0], by[0]);
            EclipseEncounter e = EclipseEncounter.get(level);
            lev[0] = e.boss() != null && level.getEntity(e.boss()) instanceof EclipseLeviathanEntity l ? l : null;
            if (lev[0] != null && !used) {
                e.addParticipant(by[0].getUUID());
                pass("the charged altar calls it again without a sigil, at full health ({})", lev[0].getHealth());
            } else {
                fail("recall: sigil used {}, boss {}", used, lev[0]);
                CreatureTrial.STEPS.clear();
                EclipseEncounter.trialHold = false;
            }
            return true;
        });
        step("leviathan victory", 200, t -> {
            if (t == 0) {
                lev[0].kill();
            }
            EclipseEncounter e = EclipseEncounter.get(level);
            List<String> owed = e.owed(by[0].getUUID());
            if (!e.active() && e.kills() >= 1 && !owed.isEmpty()) {
                if (owed.stream().anyMatch(s -> s.contains("corona")) && owed.stream().anyMatch(s -> s.contains("eclipse_scale"))) {
                    pass("victory: rewards owed to a fighter who is away ({}), kept for when they log in", owed);
                } else {
                    fail("victory rewards incomplete: {}", owed);
                }
                return true;
            }
            return false;
        });
        step("leviathan cleanup", 2, t -> {
            EclipseEncounter.trialHold = false;
            EclipseLeviathanEntity.TRIAL_TARGETS.clear();
            if (dummy[0] != null) {
                dummy[0].discard();
            }
            return true;
        });
    }
}
