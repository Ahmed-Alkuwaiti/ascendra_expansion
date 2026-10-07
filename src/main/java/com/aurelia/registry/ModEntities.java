package com.aurelia.registry;

import com.aurelia.AureliaMod;
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
    }
}
