package com.unstablefrontiers.debug;

import static com.unstablefrontiers.debug.CreatureTrial.describe;
import static com.unstablefrontiers.debug.CreatureTrial.dummy;
import static com.unstablefrontiers.debug.CreatureTrial.fail;
import static com.unstablefrontiers.debug.CreatureTrial.pass;
import static com.unstablefrontiers.debug.CreatureTrial.probe;
import static com.unstablefrontiers.debug.CreatureTrial.spawn;
import static com.unstablefrontiers.debug.CreatureTrial.step;

import com.mojang.logging.LogUtils;
import com.unstablefrontiers.drowned.DeepcallerEncounter;
import com.unstablefrontiers.drowned.DivingGearItem;
import com.unstablefrontiers.drowned.DrownedBreathing;
import com.unstablefrontiers.drowned.DrownedDimension;
import com.unstablefrontiers.drowned.DrownedPlaces;
import com.unstablefrontiers.drowned.DrownedTerrain;
import com.unstablefrontiers.drowned.DrownedTravel;
import com.unstablefrontiers.encounter.EncounterManager;
import com.unstablefrontiers.encounter.LandmarkState;
import com.unstablefrontiers.entity.DeepcallerEntity;
import com.unstablefrontiers.entity.LanternrayEntity;
import com.unstablefrontiers.entity.MurkjawEntity;
import com.unstablefrontiers.landmark.FrontierData;
import com.unstablefrontiers.landmark.LandmarkDef;
import com.unstablefrontiers.registry.DrownedRegistry;
import com.unstablefrontiers.registry.ModEntities;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.Drowned;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import org.slf4j.Logger;

/**
 * Continuous-integration only: the Drowned Expanse. The tide gate's gear check, the dimension's terrain and places, the
 * rig's breathing rules and the black-out rescue, the Murkjaw, the Lanternray, and the Deepcaller's fight; each step logged
 * as "TRIAL PASS" or "TRIAL FAIL" (see {@link CreatureTrial}, whose step runner these share).
 *
 * <p>A fake player cannot change dimension or tick its own breathing, so the rig is checked through the rules it follows
 * (drain, vents, rescue) rather than a real swim, and a real crossing is left to the client run.
 */
public final class DrownedTrial {
    private static final Logger LOGGER = LogUtils.getLogger();

    private DrownedTrial() {}

    /** A glass tank of still water with an obsidian wall across its far (+z) end. */
    static void tank(ServerLevel level, BlockPos c) {
        for (int x = -13; x <= 13; x++) {
            for (int z = -13; z <= 25; z++) {
                for (int y = -1; y <= 15; y++) {
                    boolean edge = x == -13 || x == 13 || z == -13 || z == 25 || y == -1;
                    level.setBlock(c.offset(x, y, z), edge ? Blocks.GLASS.defaultBlockState()
                            : y == 15 ? Blocks.AIR.defaultBlockState() : Blocks.WATER.defaultBlockState(), 2);
                }
            }
        }
        for (int x = -12; x <= 12; x++) {
            for (int y = 0; y < 15; y++) {
                level.setBlock(c.offset(x, y, 20), Blocks.OBSIDIAN.defaultBlockState(), 2);
            }
        }
    }

    private static boolean dry(ServerLevel level, BlockPos feet) {
        return level.getBlockState(feet).getCollisionShape(level, feet).isEmpty() && level.getFluidState(feet).isEmpty()
                && level.getBlockState(feet.above()).getCollisionShape(level, feet.above()).isEmpty() && level.getFluidState(feet.above()).isEmpty()
                && !level.getBlockState(feet.below()).getCollisionShape(level, feet.below()).isEmpty();
    }

    // ------------------------------------------------------------------------------------------------ the tide gate
    /** In the frontier: the gate turns back a diver without goggles and a way to breathe, and names what is missing. */
    public static void gate(ServerLevel level, BlockPos at) {
        step("tide gate gear check", 5, t -> {
            ServerPlayer p = FakePlayerFactory.getMinecraft(level);
            for (EquipmentSlot s : EquipmentSlot.values()) {
                p.setItemSlot(s, ItemStack.EMPTY);
            }
            p.moveTo(Vec3.atBottomCenterOf(at));
            boolean refusedBare = DrownedTravel.missingGear(p) != null;
            DrownedTravel.throughGate(p, at);
            boolean stayed = !DrownedDimension.is(p.level()) && p.blockPosition().distManhattan(at) < 3;
            p.setItemSlot(EquipmentSlot.HEAD, new ItemStack(DrownedRegistry.GOGGLES.get()));
            boolean refusedGoggles = DrownedTravel.missingGear(p) != null;
            p.setItemSlot(EquipmentSlot.CHEST, new ItemStack(DrownedRegistry.RIG.get()));
            boolean admitted = DrownedTravel.missingGear(p) == null;
            p.setItemSlot(EquipmentSlot.CHEST, ItemStack.EMPTY);
            p.setItemSlot(EquipmentSlot.FEET, ItemStack.EMPTY);
            if (refusedBare && stayed && refusedGoggles) {
                pass("the tide gate turns back a diver without goggles and a rig, and they stay where they stood");
            } else {
                fail("gate: refused bare {}, stayed {}, refused with goggles only {}", refusedBare, stayed, refusedGoggles);
            }
            if (admitted) {
                pass("goggles and a diving rig are enough to pass the tide gate");
            } else {
                fail("goggles and a rig were refused: {}", DrownedTravel.missingGear(p));
            }
            p.setItemSlot(EquipmentSlot.HEAD, ItemStack.EMPTY);
            return true;
        });
    }

    // ------------------------------------------------------------------------------------------------- the sea itself
    /** In the Drowned Expanse: the water column, every place built on its pad, the dry arrival dome, and the shelter rules. */
    public static void places(ServerLevel level) {
        step("drowned terrain", 20, t -> {
            if (!DrownedDimension.is(level)) {
                fail("not in the Drowned Expanse");
                CreatureTrial.STEPS.clear();
                return true;
            }
            int good = 0, total = 0;
            for (int[] xz : new int[][] {{60, 40}, {-200, 90}, {220, -150}, {-60, -420}, {300, -820}}) {
                total++;
                int floor = DrownedTerrain.floor(xz[0], xz[1]);
                level.getChunk(xz[0] >> 4, xz[1] >> 4);
                BlockPos top = new BlockPos(xz[0], DrownedTerrain.SURFACE, xz[1]);
                boolean water = level.getFluidState(top).is(FluidTags.WATER) && level.getBlockState(top.above()).isAir();
                BlockPos ground = new BlockPos(xz[0], floor, xz[1]);
                boolean solid = !level.getBlockState(ground).getCollisionShape(level, ground).isEmpty()
                        || !level.getBlockState(ground.below()).getCollisionShape(level, ground.below()).isEmpty();
                if (water && solid) {
                    good++;
                } else {
                    LOGGER.info("TRIAL column {} {}: surface {} {}, floor {} {}", xz[0], xz[1], level.getBlockState(top), level.getBlockState(top.above()),
                            floor, level.getBlockState(ground));
                }
            }
            if (good == total) {
                pass("the sea is water up to y {} with air above and a solid floor under every sampled column", DrownedTerrain.SURFACE);
            } else {
                fail("{} of {} sampled columns are wrong", total - good, total);
            }
            return true;
        });
        step("drowned places", 60, t -> {
            int built = 0;
            for (DrownedTerrain.Anchor a : DrownedTerrain.ANCHORS) {
                DrownedPlaces.build(level, a);
                LandmarkState s = DrownedPlaces.state(level, a);
                if (s != null) {
                    built++;
                    pass("{} built over its pad ({})", a.name(), s.origin.toShortString());
                } else {
                    fail("{} was not built", a.name());
                }
            }
            BlockPos arrival = BlockPos.containing(DrownedPlaces.arrival(level));
            if (dry(level, arrival)) {
                pass("arrivals stand on a dry floor inside the Tidewatch dome ({})", arrival.toShortString());
            } else {
                fail("the arrival {} is not a dry floor ({} / {})", arrival.toShortString(), level.getBlockState(arrival), level.getBlockState(arrival.below()));
            }
            BlockPos gate = DrownedPlaces.point(level, DrownedTerrain.TIDEWATCH, "gate");
            if (gate != null && level.getBlockState(gate).is(DrownedRegistry.TIDE_GATE.get())) {
                pass("the Tidewatch Station has its return tide gate");
            } else {
                fail("no return tide gate at Tidewatch ({})", gate == null ? "-" : level.getBlockState(gate));
            }
            int bells = 0;
            for (DrownedTerrain.Anchor a : DrownedTerrain.ANCHORS) {
                BlockPos bell = DrownedPlaces.point(level, a, "bell");
                if (bell != null && (level.getBlockState(bell).is(DrownedRegistry.TIDE_BELL.get()) || level.getBlockState(bell).is(DrownedRegistry.ABYSSAL_BELL.get()))) {
                    bells++;
                }
            }
            if (bells == DrownedTerrain.ANCHORS.length) {
                pass("every place has its bell ({} of {})", bells, DrownedTerrain.ANCHORS.length);
            } else {
                fail("only {} of {} places have a bell", bells, DrownedTerrain.ANCHORS.length);
            }
            Vec3 c = DeepcallerEncounter.center(level);
            if (level.getFluidState(BlockPos.containing(c)).is(FluidTags.WATER)) {
                pass("the Abyssal Vault's dome is flooded at the arena's middle");
            } else {
                fail("the vault's middle {} is {}", BlockPos.containing(c).toShortString(), level.getBlockState(BlockPos.containing(c)));
            }
            Drowned d = EntityType.DROWNED.create(level);
            d.moveTo(Vec3.atCenterOf(arrival));
            if (DrownedDimension.crowded(level, d)) {
                pass("nothing hostile spawns naturally inside a place");
            } else {
                fail("hostile spawns are allowed at the arrival");
            }
            d.discard();
            for (DrownedTerrain.Anchor a : DrownedTerrain.ANCHORS) {
                LandmarkState s = DrownedPlaces.state(level, a);
                LandmarkDef def = s == null ? null : FrontierData.landmark(s.id);
                if (a != DrownedTerrain.TIDEWATCH && a != DrownedTerrain.VAULT && (def == null || def.finalZone() == null)) {
                    fail("{} has no fight", a.name());
                }
            }
            LOGGER.info("TRIAL drowned places built {}", built);
            return true;
        });
    }

    // ---------------------------------------------------------------------------------------------------- breathing
    /** The rig's rules: its tank, the deep line, the vents, natural breathing taking over, and the once-a-minute rescue. */
    public static void breathing(ServerLevel level) {
        step("rig rules", 10, t -> {
            ServerPlayer p = FakePlayerFactory.getMinecraft(level);
            ItemStack rig = new ItemStack(DrownedRegistry.RIG.get());
            ItemStack deep = new ItemStack(DrownedRegistry.DEEP_RIG.get());
            int full = DivingGearItem.air(rig);
            DivingGearItem.setAir(rig, 9999);
            int clamped = DivingGearItem.air(rig);
            DivingGearItem.setAir(rig, 40);
            if (full == 180 && clamped == 180 && DivingGearItem.air(rig) == 40 && DivingGearItem.air(deep) == 420) {
                pass("a diving rig holds 180 s of air and a deep rig 420 s, and the tank cannot overfill");
            } else {
                fail("rig air: new {}, overfilled {}, set 40 -> {}, deep {}", full, clamped, DivingGearItem.air(rig), DivingGearItem.air(deep));
            }
            p.moveTo(40.5, 200, 40.5);
            int shallow = DrownedBreathing.drain(p, rig);
            p.moveTo(40.5, DrownedTerrain.DEEP_LINE - 20, 40.5);
            int below = DrownedBreathing.drain(p, rig);
            int belowDeep = DrownedBreathing.drain(p, deep);
            if (shallow == 1 && below == 3 && belowDeep == 1) {
                pass("below the deep line a diving rig drains three times as fast; a deep rig does not");
            } else {
                fail("drain: shallow {}, deep line {}, deep rig {}", shallow, below, belowDeep);
            }
            BlockPos base = new BlockPos(40, 200, 40);
            for (int y = -4; y <= 2; y++) {
                level.setBlock(base.offset(0, y, 0), y == -4 ? DrownedRegistry.BREATH_VENT.get().defaultBlockState() : Blocks.WATER.defaultBlockState(), 2);
            }
            p.moveTo(40.5, 200, 40.5);
            boolean over = DrownedBreathing.atVent(p);
            level.setBlock(base.offset(0, -2, 0), Blocks.STONE.defaultBlockState(), 2);
            boolean blocked = DrownedBreathing.atVent(p);
            if (over && !blocked) {
                pass("a breath vent refills a rig through open water above it, not through rock");
            } else {
                fail("vent: over {}, through rock {}", over, blocked);
            }
            p.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 200));
            boolean natural = DrownedBreathing.breathesUnderwater(p);
            p.removeEffect(MobEffects.WATER_BREATHING);
            if (natural && !DrownedBreathing.breathesUnderwater(p)) {
                pass("water breathing from elsewhere in the pack takes over from the rig (the tank is not used)");
            } else {
                fail("natural breathing: with the effect {}, without {}", natural, DrownedBreathing.breathesUnderwater(p));
            }
            BlockPos shelter = BlockPos.containing(DrownedPlaces.arrival(level));
            DrownedTravel.setShelter(p, shelter);
            p.getPersistentData().remove("uf_drowned_rescued");
            p.moveTo(200.5, 150, 200.5);
            boolean first = DrownedTravel.rescue(p);
            boolean home = p.blockPosition().distManhattan(shelter) < 3;
            p.moveTo(200.5, 150, 200.5);
            boolean second = DrownedTravel.rescue(p);
            if (first && home && !second) {
                pass("a diver who blacks out wakes at their last shelter, at most once a minute");
            } else {
                fail("rescue: first {}, at shelter {} ({}), second {}", first, home, p.blockPosition().toShortString(), second);
            }
            return true;
        });
    }

    // ---------------------------------------------------------------------------------------------------- the Murkjaw
    public static void murkjaw(ServerLevel level, BlockPos c) {
        MurkjawEntity[] m = new MurkjawEntity[1];
        IronGolem[] dummy = new IronGolem[1];
        int[] toldAt = {-1};
        float[] normal = new float[1];
        step("murkjaw setup", 5, t -> {
            tank(level, c);
            m[0] = spawn(level, ModEntities.MURKJAW.get(), Vec3.atCenterOf(c.offset(0, 6, 3)));
            dummy[0] = dummy(level, Vec3.atBottomCenterOf(c.offset(0, 5, 13)));
            dummy[0].setNoGravity(true);
            m[0].setTarget(dummy[0]);
            normal[0] = probe(m[0], 4);
            m[0].setHealth(m[0].getMaxHealth());
            CreatureTrial.status = () -> describe(m[0]);
            return true;
        });
        step("murkjaw swims", 60, t -> {
            m[0].setTarget(dummy[0]);
            if (m[0].state() == MurkjawEntity.TELL) {
                toldAt[0] = t;      // a tell that starts while it is still settling counts for the next step
            }
            if (t == 59) {
                if (m[0].isInWater() && m[0].getY() > c.getY() + 1.5D) {
                    pass("murkjaw swims in open water (y {} over floor {})", (int) m[0].getY(), c.getY());
                } else {
                    fail("murkjaw sank or left the water (y {}, in water {})", (int) m[0].getY(), m[0].isInWater());
                }
                return true;
            }
            return false;
        });
        float[] before = new float[1];
        step("murkjaw tells and lunges", 600, t -> {
            m[0].setTarget(dummy[0]);
            if (t == 0) {
                before[0] = dummy[0].getHealth();
            }
            if (m[0].state() == MurkjawEntity.TELL && toldAt[0] < 0) {
                toldAt[0] = t;
            }
            if (m[0].state() == MurkjawEntity.LUNGE && toldAt[0] < 0) {
                fail("murkjaw lunged with no tell");
                return true;
            }
            if (dummy[0].getHealth() < before[0] - 0.5F) {
                pass("murkjaw unhinges its jaw (tell) before it lunges, and an undodged lunge hits for {}", before[0] - dummy[0].getHealth());
                return true;
            }
            return false;
        });
        int[] tell = {-1, 0};   // tick the tell began, and whether the stand-in has slipped aside this time
        step("murkjaw dodged into a wall", 900, t -> {
            m[0].setTarget(dummy[0]);
            if (m[0].state() == MurkjawEntity.TELL && tell[0] < 0) {
                tell[0] = t;
            }
            if (tell[0] >= 0 && tell[1] == 0 && t - tell[0] >= 13) {
                // the line is fixed half way through the tell: slip aside late, leaving the wall behind on the line
                tell[1] = 1;
                dummy[0].teleportTo(c.getX() + 7.5, c.getY() + 5, c.getZ() + 17.5);
            }
            if (m[0].state() == MurkjawEntity.STUNNED) {
                float d = probe(m[0], 4);
                if (d > normal[0] * 1.7F) {
                    pass("a dodged lunge into a wall stuns the murkjaw, and stunned it takes {} from a hit that deals {}", d, normal[0]);
                } else {
                    fail("stunned murkjaw took {} vs {} normally", d, normal[0]);
                }
                return true;
            }
            if (tell[1] == 1 && m[0].state() == MurkjawEntity.IDLE) {
                // it missed into open water short of the wall: put the stand-in back and wait for the next tell
                tell[0] = -1;
                tell[1] = 0;
                dummy[0].teleportTo(c.getX() + 0.5, c.getY() + 5, c.getZ() + 13.5);
            }
            return false;
        });
        step("murkjaw cleanup", 2, t -> {
            m[0].discard();
            dummy[0].discard();
            return true;
        });
    }

    // -------------------------------------------------------------------------------------------------- the Lanternray
    /** Between Tidewatch and Deepwork: it stays in the water, and fed glow berries it leads toward the nearest uncharted place. */
    public static void lanternray(ServerLevel level, BlockPos c) {
        LanternrayEntity[] r = new LanternrayEntity[1];
        ServerPlayer[] p = new ServerPlayer[1];
        double[] start = new double[1];
        step("lanternray setup", 5, t -> {
            Vec3 at = new Vec3(c.getX() + 0.5, DrownedTerrain.floor(c.getX(), c.getZ()) + 8, c.getZ() + 0.5);
            r[0] = spawn(level, ModEntities.LANTERNRAY.get(), at);
            CreatureTrial.status = () -> "lanternray at " + r[0].blockPosition().toShortString() + ", leading " + r[0].leading() + ", in water " + r[0].isInWater();
            p[0] = FakePlayerFactory.getMinecraft(level);
            p[0].moveTo(at.add(2, 0, 0));
            DrownedPlaces.chart(p[0], DrownedTerrain.TIDEWATCH, false);
            p[0].setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(Items.GLOW_BERRIES, 4));
            return true;
        });
        step("lanternray leads", 300, t -> {
            if (t == 0) {
                p[0].interactOn(r[0], InteractionHand.MAIN_HAND);
                start[0] = Math.hypot(r[0].getX() - DrownedTerrain.DEEPWORK.x(), r[0].getZ() - DrownedTerrain.DEEPWORK.z());
                if (!r[0].leading()) {
                    fail("fed glow berries, the lanternray does not lead");
                    return true;
                }
                return false;
            }
            p[0].moveTo(r[0].position().add(1.5, 0, 0));   // keep up with it
            double now = Math.hypot(r[0].getX() - DrownedTerrain.DEEPWORK.x(), r[0].getZ() - DrownedTerrain.DEEPWORK.z());
            if (start[0] - now > 12) {
                pass("fed glow berries, a lanternray leads toward the nearest uncharted place ({} blocks closer in {} ticks)", (int) (start[0] - now), t);
                return true;
            }
            if (!r[0].isInWater()) {
                fail("the lanternray left the water");
                return true;
            }
            return false;
        });
        step("lanternray flees", 10, t -> {
            probe(r[0], 2);
            if (!r[0].leading()) {
                pass("struck, a lanternray stops leading and flees");
            } else {
                fail("a struck lanternray kept leading");
            }
            r[0].discard();
            return true;
        });
    }

    // --------------------------------------------------------------------------------------------------- the Deepcaller
    /** At the Abyssal Vault: its attacks are told, it keeps to the dome, phase two and its brood cap, abandonment resets
     *  it, it can be called again, its state survives saving, and the victory pays out once. */
    public static void deepcaller(ServerLevel level) {
        DeepcallerEntity[] b = new DeepcallerEntity[1];
        IronGolem[] dummy = new IronGolem[1];
        ServerPlayer[] by = new ServerPlayer[1];
        boolean[] seen = new boolean[16];
        float[] normal = new float[1];
        step("deepcaller summon", 40, t -> {
            DrownedPlaces.build(level, DrownedTerrain.VAULT);
            DeepcallerEncounter.forceReset(level);
            DeepcallerEncounter.trialHold = true;
            Vec3 c = DeepcallerEncounter.center(level);
            by[0] = FakePlayerFactory.getMinecraft(level);
            by[0].moveTo(c.x, c.y, c.z + 6);
            dummy[0] = dummy(level, c.add(9, -2, 4));
            dummy[0].setNoGravity(true);
            DeepcallerEntity.TRIAL_TARGETS.clear();
            DeepcallerEntity.TRIAL_TARGETS.add(dummy[0]);
            boolean called = DeepcallerEncounter.summon(level, by[0]);
            DeepcallerEncounter e = DeepcallerEncounter.get(level);
            b[0] = e.boss() != null && level.getEntity(e.boss()) instanceof DeepcallerEntity d ? d : null;
            if (called && b[0] != null) {
                e.addParticipant(by[0].getUUID());
                pass("the abyssal bell wakes the Deepcaller (hp {}, armor {})", b[0].getMaxHealth(), b[0].getArmorValue());
                CreatureTrial.status = () -> describe(b[0]);
            } else {
                fail("summon: called {}, boss {}", called, b[0]);
                CreatureTrial.STEPS.clear();
                DeepcallerEncounter.trialHold = false;
            }
            return true;
        });
        step("deepcaller intro", 5, t -> {
            if (probe(b[0], 50) == 0) {
                pass("the rising Deepcaller cannot be hurt");
            } else {
                fail("the rising Deepcaller took damage");
            }
            if (!DeepcallerEncounter.summon(level, by[0])) {
                pass("only one Deepcaller at a time");
            } else {
                fail("a second Deepcaller was called");
            }
            return true;
        });
        step("deepcaller phase one attacks", 2400, t -> {
            seen[b[0].state()] = true;
            if (b[0].state() == DeepcallerEntity.DRIFT && normal[0] == 0) {
                normal[0] = probe(b[0], 10);
            }
            if (seen[DeepcallerEntity.LURE_TELL] && seen[DeepcallerEntity.LURE_FLASH] && seen[DeepcallerEntity.CHARGE_TELL]
                    && seen[DeepcallerEntity.CHARGE] && seen[DeepcallerEntity.VORTEX_TELL] && seen[DeepcallerEntity.VORTEX]) {
                pass("phase one: lure flash, charge and vortex, each with its tell (stand-in lost {})",
                        String.format("%.0f", dummy[0].getMaxHealth() - dummy[0].getHealth()));
                return true;
            }
            return false;
        });
        step("deepcaller stays in its dome", 1, t -> {
            Vec3 c = b[0].center();
            double d = Math.hypot(b[0].getX() - c.x, b[0].getZ() - c.z);
            if (d < DeepcallerEncounter.ARENA_RADIUS) {
                pass("the Deepcaller keeps to its dome ({} blocks from the middle)", String.format("%.1f", d));
            } else {
                fail("the Deepcaller strayed {} blocks from the middle", d);
            }
            return true;
        });
        step("deepcaller phase two", 300, t -> {
            if (t == 0) {
                b[0].invulnerableTime = 0;
                b[0].setHealth(b[0].getMaxHealth() * 0.55F);
                probe(b[0], b[0].getMaxHealth() * 0.08F);
            }
            if (b[0].phase() == 2) {
                pass("phase two at half health, with a roar (state {})", b[0].state());
                return true;
            }
            return false;
        });
        step("deepcaller brood", 2400, t -> {
            List<MurkjawEntity> adds = level.getEntitiesOfClass(MurkjawEntity.class, new AABB(BlockPos.containing(b[0].center())).inflate(40),
                    x -> x.getPersistentData().getBoolean(DeepcallerEncounter.ADD_TAG));
            if (adds.size() > DeepcallerEntity.MAX_BROOD) {
                fail("{} brood alive, over the cap of {}", adds.size(), DeepcallerEntity.MAX_BROOD);
                return true;
            }
            if (!adds.isEmpty() && b[0].state() == DeepcallerEntity.DRIFT) {
                pass("phase two calls its brood ({} alive, never more than {}, each at {} health)", adds.size(), DeepcallerEntity.MAX_BROOD,
                        adds.get(0).getMaxHealth());
                return true;
            }
            return false;
        });
        step("deepcaller stunned", 2400, t -> {
            if (b[0].state() == DeepcallerEntity.STUNNED) {
                float d = probe(b[0], 10);
                if (d > normal[0] * 1.7F) {
                    pass("a charge that misses into the dome wall stuns it: {} from a hit that deals {} normally", d, normal[0]);
                } else {
                    fail("stunned: took {} vs {} normally", d, normal[0]);
                }
                return true;
            }
            return false;
        });
        step("deepcaller save and load", 5, t -> {
            CompoundTag tag = new CompoundTag();
            b[0].saveWithoutId(tag);
            DeepcallerEntity copy = ModEntities.DEEPCALLER.get().create(level);
            copy.load(tag);
            if (copy.phase() == b[0].phase() && copy.center().distanceTo(b[0].center()) < 0.01D && copy.brood().size() == b[0].brood().size()) {
                pass("its phase, dome and brood survive a save and load");
            } else {
                fail("after load: phase {} vs {}, center {} vs {}", copy.phase(), b[0].phase(), copy.center(), b[0].center());
            }
            DeepcallerEntity orphan = ModEntities.DEEPCALLER.get().create(level);
            orphan.moveTo(b[0].center().add(0, 6, 0));
            if (!level.addFreshEntity(orphan)) {
                pass("a Deepcaller with no fight to belong to is turned away");
            } else {
                fail("an orphan Deepcaller joined the world");
                orphan.discard();
            }
            return true;
        });
        step("deepcaller abandoned", DeepcallerEncounter.ABANDON_TICKS + 200, t -> {
            if (t == 0) {
                DeepcallerEncounter.trialHold = false;
            }
            if (!DeepcallerEncounter.get(level).active()) {
                if (!b[0].isAlive() || b[0].isRemoved()) {
                    int adds = level.getEntitiesOfClass(MurkjawEntity.class, new AABB(BlockPos.containing(b[0].center())).inflate(40),
                            x -> x.getPersistentData().getBoolean(DeepcallerEncounter.ADD_TAG)).size();
                    pass("with nobody in the vault for {} s the fight resets: boss gone, {} of its brood left", t / 20, adds);
                } else {
                    fail("fight reset but the boss is still here");
                }
                return true;
            }
            return false;
        });
        step("deepcaller recalled", 20, t -> {
            DeepcallerEncounter.trialHold = true;
            boolean called = DeepcallerEncounter.summon(level, by[0]);
            DeepcallerEncounter e = DeepcallerEncounter.get(level);
            b[0] = e.boss() != null && level.getEntity(e.boss()) instanceof DeepcallerEntity d ? d : null;
            if (called && b[0] != null && b[0].getHealth() >= b[0].getMaxHealth()) {
                e.addParticipant(by[0].getUUID());
                pass("the bell calls it again at full health ({})", b[0].getHealth());
            } else {
                fail("recall: called {}, boss {}", called, b[0]);
                CreatureTrial.STEPS.clear();
                DeepcallerEncounter.trialHold = false;
            }
            return true;
        });
        step("deepcaller victory", 200, t -> {
            if (t == 0) {
                b[0].kill();
            }
            DeepcallerEncounter e = DeepcallerEncounter.get(level);
            List<String> owed = e.owed(by[0].getUUID());
            if (!e.active() && e.kills() >= 1 && !owed.isEmpty()) {
                long undertows = owed.stream().filter(s -> s.contains("undertow")).count();
                if (owed.stream().anyMatch(s -> s.contains("abyssal_pearl")) && undertows == 1) {
                    pass("victory: abyssal pearls and one Undertow owed to a fighter who is away ({})", owed);
                } else {
                    fail("victory rewards wrong: {}", owed);
                }
                return true;
            }
            return false;
        });
        step("deepcaller second victory", 300, t -> {
            if (t == 0) {
                DeepcallerEncounter.trialHold = true;
                DeepcallerEncounter.summon(level, by[0]);
                DeepcallerEncounter e = DeepcallerEncounter.get(level);
                e.addParticipant(by[0].getUUID());
                b[0] = e.boss() != null && level.getEntity(e.boss()) instanceof DeepcallerEntity d ? d : null;
                return false;
            }
            if (t == 60 && b[0] != null) {
                b[0].kill();
            }
            DeepcallerEncounter e = DeepcallerEncounter.get(level);
            if (t > 60 && !e.active() && e.kills() >= 2) {
                long undertows = e.owed(by[0].getUUID()).stream().filter(s -> s.contains("undertow")).count();
                if (undertows == 1) {
                    pass("a second victory pays pearls again but no second Undertow");
                } else {
                    fail("{} Undertows owed after two victories", undertows);
                }
                return true;
            }
            return false;
        });
        step("deepcaller cleanup", 2, t -> {
            DeepcallerEncounter.trialHold = false;
            DeepcallerEntity.TRIAL_TARGETS.clear();
            if (dummy[0] != null) {
                dummy[0].discard();
            }
            return true;
        });
    }
}
