package com.aurelia.registry;

import com.aurelia.AureliaMod;
import com.aurelia.entity.CoralcladJuggernaut;
import com.aurelia.entity.GlasswingScarab;
import com.aurelia.entity.Hushwraith;
import com.aurelia.entity.Kharzul;
import com.aurelia.entity.PaleMirage;
import com.aurelia.entity.Razorclaw;
import com.aurelia.entity.Rimefang;
import com.aurelia.entity.Rimeguard;
import com.aurelia.entity.SandglassSentinel;
import com.aurelia.entity.Sunseer;
import com.aurelia.entity.Tidecaller;
import com.aurelia.entity.Vorath;
import com.aurelia.entity.WhiteSilence;
import com.aurelia.entity.AshboundKnight;
import com.aurelia.entity.BrambleSentinel;
import com.aurelia.entity.CalciteSentinel;
import com.aurelia.entity.CinderHound;
import com.aurelia.entity.GaleTalon;
import com.aurelia.entity.GroveAnt;
import com.aurelia.entity.HollowKing;
import com.aurelia.entity.HollowShade;
import com.aurelia.entity.MossbackTitan;
import com.aurelia.entity.Rootstalker;
import com.aurelia.entity.SkySentinel;
import com.aurelia.entity.SoulJailer;
import com.aurelia.entity.Sporecap;
import com.aurelia.entity.StormWisp;
import com.aurelia.entity.TempestRoc;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITIES =
            DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, AureliaMod.MODID);

    private static String id(String name) {
        return new ResourceLocation(AureliaMod.MODID, name).toString();
    }

    public static final RegistryObject<EntityType<MossbackTitan>> MOSSBACK_TITAN = ENTITIES.register("mossback_titan",
            () -> EntityType.Builder.of(MossbackTitan::new, MobCategory.MONSTER)
                    .sized(3.4f, 6.6f).clientTrackingRange(10).fireImmune().build(id("mossback_titan")));

    public static final RegistryObject<EntityType<TempestRoc>> TEMPEST_ROC = ENTITIES.register("tempest_roc",
            () -> EntityType.Builder.of(TempestRoc::new, MobCategory.MONSTER)
                    .sized(4.0f, 2.4f).clientTrackingRange(12).fireImmune().build(id("tempest_roc")));

    public static final RegistryObject<EntityType<HollowKing>> HOLLOW_KING = ENTITIES.register("hollow_king",
            () -> EntityType.Builder.of(HollowKing::new, MobCategory.MONSTER)
                    .sized(2.2f, 7.4f).clientTrackingRange(10).fireImmune().build(id("hollow_king")));

    public static final RegistryObject<EntityType<GroveAnt>> GROVE_ANT = ENTITIES.register("grove_ant",
            () -> EntityType.Builder.of(GroveAnt::new, MobCategory.MONSTER)
                    .sized(1.8f, 1.2f).clientTrackingRange(8).build(id("grove_ant")));

    public static final RegistryObject<EntityType<SkySentinel>> SKY_SENTINEL = ENTITIES.register("sky_sentinel",
            () -> EntityType.Builder.of(SkySentinel::new, MobCategory.MONSTER)
                    .sized(0.7f, 2.2f).clientTrackingRange(8).build(id("sky_sentinel")));

    public static final RegistryObject<EntityType<HollowShade>> HOLLOW_SHADE = ENTITIES.register("hollow_shade",
            () -> EntityType.Builder.of(HollowShade::new, MobCategory.MONSTER)
                    .sized(0.6f, 1.95f).clientTrackingRange(8).build(id("hollow_shade")));

    public static final RegistryObject<EntityType<BrambleSentinel>> BRAMBLE_SENTINEL = ENTITIES.register("bramble_sentinel",
            () -> EntityType.Builder.of(BrambleSentinel::new, MobCategory.MONSTER)
                    .sized(1.2f, 2.7f).clientTrackingRange(8).build(id("bramble_sentinel")));

    public static final RegistryObject<EntityType<Sporecap>> SPORECAP = ENTITIES.register("sporecap",
            () -> EntityType.Builder.of(Sporecap::new, MobCategory.MONSTER)
                    .sized(0.7f, 1.9f).clientTrackingRange(8).build(id("sporecap")));

    public static final RegistryObject<EntityType<Rootstalker>> ROOTSTALKER = ENTITIES.register("rootstalker",
            () -> EntityType.Builder.of(Rootstalker::new, MobCategory.MONSTER)
                    .sized(0.9f, 1.4f).clientTrackingRange(8).build(id("rootstalker")));

    public static final RegistryObject<EntityType<CalciteSentinel>> CALCITE_SENTINEL = ENTITIES.register("calcite_sentinel",
            () -> EntityType.Builder.of(CalciteSentinel::new, MobCategory.MONSTER)
                    .sized(0.8f, 2.4f).clientTrackingRange(8).build(id("calcite_sentinel")));

    public static final RegistryObject<EntityType<StormWisp>> STORM_WISP = ENTITIES.register("storm_wisp",
            () -> EntityType.Builder.of(StormWisp::new, MobCategory.MONSTER)
                    .sized(1.0f, 2.0f).clientTrackingRange(8).build(id("storm_wisp")));

    public static final RegistryObject<EntityType<GaleTalon>> GALE_TALON = ENTITIES.register("gale_talon",
            () -> EntityType.Builder.of(GaleTalon::new, MobCategory.MONSTER)
                    .sized(0.9f, 1.1f).clientTrackingRange(8).build(id("gale_talon")));

    public static final RegistryObject<EntityType<AshboundKnight>> ASHBOUND_KNIGHT = ENTITIES.register("ashbound_knight",
            () -> EntityType.Builder.of(AshboundKnight::new, MobCategory.MONSTER)
                    .sized(0.8f, 2.4f).clientTrackingRange(8).fireImmune().build(id("ashbound_knight")));

    public static final RegistryObject<EntityType<SoulJailer>> SOUL_JAILER = ENTITIES.register("soul_jailer",
            () -> EntityType.Builder.of(SoulJailer::new, MobCategory.MONSTER)
                    .sized(0.8f, 2.2f).clientTrackingRange(8).build(id("soul_jailer")));

    public static final RegistryObject<EntityType<CinderHound>> CINDER_HOUND = ENTITIES.register("cinder_hound",
            () -> EntityType.Builder.of(CinderHound::new, MobCategory.MONSTER)
                    .sized(1.0f, 1.4f).clientTrackingRange(8).fireImmune().build(id("cinder_hound")));

    // ==================================================================== act two
    public static final RegistryObject<EntityType<Vorath>> VORATH = ENTITIES.register("vorath",
            () -> EntityType.Builder.of(Vorath::new, MobCategory.MONSTER)
                    .sized(5.0f, 3.2f).clientTrackingRange(12).build(id("vorath")));

    public static final RegistryObject<EntityType<WhiteSilence>> WHITE_SILENCE = ENTITIES.register("white_silence",
            () -> EntityType.Builder.of(WhiteSilence::new, MobCategory.MONSTER)
                    .sized(1.6f, 7.2f).clientTrackingRange(10).immuneTo(net.minecraft.world.level.block.Blocks.POWDER_SNOW).build(id("white_silence")));

    public static final RegistryObject<EntityType<Kharzul>> KHARZUL = ENTITIES.register("kharzul",
            () -> EntityType.Builder.of(Kharzul::new, MobCategory.MONSTER)
                    .sized(2.0f, 6.8f).clientTrackingRange(10).fireImmune().build(id("kharzul")));

    public static final RegistryObject<EntityType<PaleMirage>> PALE_MIRAGE = ENTITIES.register("pale_mirage",
            () -> EntityType.Builder.of(PaleMirage::new, MobCategory.MONSTER)
                    .sized(1.6f, 7.2f).clientTrackingRange(10).immuneTo(net.minecraft.world.level.block.Blocks.POWDER_SNOW).build(id("pale_mirage")));

    public static final RegistryObject<EntityType<CoralcladJuggernaut>> CORALCLAD_JUGGERNAUT = ENTITIES.register("coralclad_juggernaut",
            () -> EntityType.Builder.of(CoralcladJuggernaut::new, MobCategory.MONSTER)
                    .sized(1.3f, 2.8f).clientTrackingRange(8).build(id("coralclad_juggernaut")));

    public static final RegistryObject<EntityType<Tidecaller>> TIDECALLER = ENTITIES.register("tidecaller",
            () -> EntityType.Builder.of(Tidecaller::new, MobCategory.MONSTER)
                    .sized(0.8f, 2.3f).clientTrackingRange(8).build(id("tidecaller")));

    public static final RegistryObject<EntityType<Razorclaw>> RAZORCLAW = ENTITIES.register("razorclaw",
            () -> EntityType.Builder.of(Razorclaw::new, MobCategory.MONSTER)
                    .sized(1.4f, 0.9f).clientTrackingRange(8).build(id("razorclaw")));

    public static final RegistryObject<EntityType<Rimeguard>> RIMEGUARD = ENTITIES.register("rimeguard",
            () -> EntityType.Builder.of(Rimeguard::new, MobCategory.MONSTER)
                    .sized(0.9f, 2.5f).clientTrackingRange(8).immuneTo(net.minecraft.world.level.block.Blocks.POWDER_SNOW).build(id("rimeguard")));

    public static final RegistryObject<EntityType<Hushwraith>> HUSHWRAITH = ENTITIES.register("hushwraith",
            () -> EntityType.Builder.of(Hushwraith::new, MobCategory.MONSTER)
                    .sized(0.8f, 2.4f).clientTrackingRange(8).immuneTo(net.minecraft.world.level.block.Blocks.POWDER_SNOW).build(id("hushwraith")));

    public static final RegistryObject<EntityType<Rimefang>> RIMEFANG = ENTITIES.register("rimefang",
            () -> EntityType.Builder.of(Rimefang::new, MobCategory.MONSTER)
                    .sized(0.9f, 1.4f).clientTrackingRange(8).immuneTo(net.minecraft.world.level.block.Blocks.POWDER_SNOW).build(id("rimefang")));

    public static final RegistryObject<EntityType<SandglassSentinel>> SANDGLASS_SENTINEL = ENTITIES.register("sandglass_sentinel",
            () -> EntityType.Builder.of(SandglassSentinel::new, MobCategory.MONSTER)
                    .sized(1.4f, 2.8f).clientTrackingRange(8).fireImmune().build(id("sandglass_sentinel")));

    public static final RegistryObject<EntityType<Sunseer>> SUNSEER = ENTITIES.register("sunseer",
            () -> EntityType.Builder.of(Sunseer::new, MobCategory.MONSTER)
                    .sized(0.8f, 2.3f).clientTrackingRange(8).fireImmune().build(id("sunseer")));

    public static final RegistryObject<EntityType<GlasswingScarab>> GLASSWING_SCARAB = ENTITIES.register("glasswing_scarab",
            () -> EntityType.Builder.of(GlasswingScarab::new, MobCategory.MONSTER)
                    .sized(1.1f, 0.9f).clientTrackingRange(8).fireImmune().build(id("glasswing_scarab")));

    public static void registerAttributes(EntityAttributeCreationEvent event) {
        event.put(MOSSBACK_TITAN.get(), MossbackTitan.createAttributes().build());
        event.put(TEMPEST_ROC.get(), TempestRoc.createAttributes().build());
        event.put(HOLLOW_KING.get(), HollowKing.createAttributes().build());
        event.put(GROVE_ANT.get(), GroveAnt.createAttributes().build());
        event.put(SKY_SENTINEL.get(), SkySentinel.createAttributes().build());
        event.put(HOLLOW_SHADE.get(), HollowShade.createAttributes().build());
        event.put(BRAMBLE_SENTINEL.get(), BrambleSentinel.createAttributes().build());
        event.put(SPORECAP.get(), Sporecap.createAttributes().build());
        event.put(ROOTSTALKER.get(), Rootstalker.createAttributes().build());
        event.put(CALCITE_SENTINEL.get(), CalciteSentinel.createAttributes().build());
        event.put(STORM_WISP.get(), StormWisp.createAttributes().build());
        event.put(GALE_TALON.get(), GaleTalon.createAttributes().build());
        event.put(ASHBOUND_KNIGHT.get(), AshboundKnight.createAttributes().build());
        event.put(SOUL_JAILER.get(), SoulJailer.createAttributes().build());
        event.put(CINDER_HOUND.get(), CinderHound.createAttributes().build());
        event.put(VORATH.get(), Vorath.createAttributes().build());
        event.put(WHITE_SILENCE.get(), WhiteSilence.createAttributes().build());
        event.put(KHARZUL.get(), Kharzul.createAttributes().build());
        event.put(PALE_MIRAGE.get(), PaleMirage.createAttributes().build());
        event.put(CORALCLAD_JUGGERNAUT.get(), CoralcladJuggernaut.createAttributes().build());
        event.put(TIDECALLER.get(), Tidecaller.createAttributes().build());
        event.put(RAZORCLAW.get(), Razorclaw.createAttributes().build());
        event.put(RIMEGUARD.get(), Rimeguard.createAttributes().build());
        event.put(HUSHWRAITH.get(), Hushwraith.createAttributes().build());
        event.put(RIMEFANG.get(), Rimefang.createAttributes().build());
        event.put(SANDGLASS_SENTINEL.get(), SandglassSentinel.createAttributes().build());
        event.put(SUNSEER.get(), Sunseer.createAttributes().build());
        event.put(GLASSWING_SCARAB.get(), GlasswingScarab.createAttributes().build());
    }

    public static void registerSpawns(SpawnPlacementRegisterEvent event) {
        event.register(GROVE_ANT.get(), SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Mob::checkMobSpawnRules,
                SpawnPlacementRegisterEvent.Operation.OR);
        event.register(SKY_SENTINEL.get(), SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Mob::checkMobSpawnRules,
                SpawnPlacementRegisterEvent.Operation.OR);
        event.register(HOLLOW_SHADE.get(), SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Monster::checkMonsterSpawnRules,
                SpawnPlacementRegisterEvent.Operation.OR);
        // the outer realms' natural wildlife (their citadel garrisons are placed by the structures)
        event.register(RAZORCLAW.get(), SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Mob::checkMobSpawnRules,
                SpawnPlacementRegisterEvent.Operation.OR);
        event.register(RIMEFANG.get(), SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Mob::checkMobSpawnRules,
                SpawnPlacementRegisterEvent.Operation.OR);
        event.register(GLASSWING_SCARAB.get(), SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Mob::checkMobSpawnRules,
                SpawnPlacementRegisterEvent.Operation.OR);
    }
}
