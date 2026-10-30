package com.unstablefrontiers.registry;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.entity.AcidGlobEntity;
import com.unstablefrontiers.entity.DeepcallerEntity;
import com.unstablefrontiers.entity.LanternrayEntity;
import com.unstablefrontiers.entity.MurkjawEntity;
import com.unstablefrontiers.entity.ChainedMatriarchEntity;
import com.unstablefrontiers.entity.EclipseLeviathanEntity;
import com.unstablefrontiers.entity.GnashbackEntity;
import com.unstablefrontiers.entity.LumenMiteEntity;
import com.unstablefrontiers.entity.OrreryWardenEntity;
import com.unstablefrontiers.entity.StarBoltEntity;
import com.unstablefrontiers.entity.ShrikewingEntity;
import java.util.function.Supplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.levelgen.Heightmap;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.event.entity.RegisterSpawnPlacementsEvent;
import net.neoforged.neoforge.registries.DeferredRegister;

/** The frontier's own creatures. Sizes match the models (tools/models) so hitboxes cover what you see. */
public final class ModEntities {
    private static final DeferredRegister<EntityType<?>> TYPES = DeferredRegister.create(Registries.ENTITY_TYPE, UnstableFrontiers.MODID);

    public static final Supplier<EntityType<GnashbackEntity>> GNASHBACK = TYPES.register("gnashback",
            () -> EntityType.Builder.<GnashbackEntity>of(GnashbackEntity::new, MobCategory.MONSTER).sized(2.4F, 1.9F).eyeHeight(1.3F)
                    .clientTrackingRange(10).build("gnashback"));
    public static final Supplier<EntityType<ShrikewingEntity>> SHRIKEWING = TYPES.register("shrikewing",
            () -> EntityType.Builder.<ShrikewingEntity>of(ShrikewingEntity::new, MobCategory.MONSTER).sized(2.2F, 1.3F).eyeHeight(0.9F)
                    .clientTrackingRange(12).build("shrikewing"));
    public static final Supplier<EntityType<ChainedMatriarchEntity>> CHAINED_MATRIARCH = TYPES.register("chained_matriarch",
            () -> EntityType.Builder.<ChainedMatriarchEntity>of(ChainedMatriarchEntity::new, MobCategory.MONSTER).sized(4.0F, 4.6F)
                    .eyeHeight(3.8F).fireImmune().clientTrackingRange(12).build("chained_matriarch"));
    public static final Supplier<EntityType<AcidGlobEntity>> ACID_GLOB = TYPES.register("acid_glob",
            () -> EntityType.Builder.<AcidGlobEntity>of(AcidGlobEntity::new, MobCategory.MISC).sized(0.5F, 0.5F)
                    .clientTrackingRange(6).updateInterval(10).build("acid_glob"));

    public static final Supplier<EntityType<LumenMiteEntity>> LUMEN_MITE = TYPES.register("lumen_mite",
            () -> EntityType.Builder.<LumenMiteEntity>of(LumenMiteEntity::new, MobCategory.MONSTER).sized(0.8F, 0.6F).eyeHeight(0.35F)
                    .clientTrackingRange(8).build("lumen_mite"));
    public static final Supplier<EntityType<OrreryWardenEntity>> ORRERY_WARDEN = TYPES.register("orrery_warden",
            () -> EntityType.Builder.<OrreryWardenEntity>of(OrreryWardenEntity::new, MobCategory.MONSTER).sized(1.8F, 2.0F).eyeHeight(1.25F)
                    .fireImmune().clientTrackingRange(10).build("orrery_warden"));
    public static final Supplier<EntityType<EclipseLeviathanEntity>> ECLIPSE_LEVIATHAN = TYPES.register("eclipse_leviathan",
            () -> EntityType.Builder.<EclipseLeviathanEntity>of(EclipseLeviathanEntity::new, MobCategory.MONSTER).sized(8.0F, 2.6F).eyeHeight(1.6F)
                    .fireImmune().clientTrackingRange(16).updateInterval(2).build("eclipse_leviathan"));
    public static final Supplier<EntityType<StarBoltEntity>> STAR_BOLT = TYPES.register("star_bolt",
            () -> EntityType.Builder.<StarBoltEntity>of(StarBoltEntity::new, MobCategory.MISC).sized(0.4F, 0.4F)
                    .clientTrackingRange(6).updateInterval(5).build("star_bolt"));

    // the Drowned Expanse
    public static final Supplier<EntityType<LanternrayEntity>> LANTERNRAY = TYPES.register("lanternray",
            () -> EntityType.Builder.<LanternrayEntity>of(LanternrayEntity::new, MobCategory.WATER_CREATURE).sized(2.4F, 0.6F).eyeHeight(0.3F)
                    .clientTrackingRange(10).build("lanternray"));
    public static final Supplier<EntityType<MurkjawEntity>> MURKJAW = TYPES.register("murkjaw",
            () -> EntityType.Builder.<MurkjawEntity>of(MurkjawEntity::new, MobCategory.MONSTER).sized(1.4F, 0.8F).eyeHeight(0.4F)
                    .clientTrackingRange(8).build("murkjaw"));
    public static final Supplier<EntityType<DeepcallerEntity>> DEEPCALLER = TYPES.register("deepcaller",
            () -> EntityType.Builder.<DeepcallerEntity>of(DeepcallerEntity::new, MobCategory.MONSTER).sized(4.4F, 3.0F).eyeHeight(1.8F)
                    .clientTrackingRange(12).updateInterval(2).build("deepcaller"));

    private ModEntities() {}

    public static void register(IEventBus bus) {
        TYPES.register(bus);
        bus.addListener(ModEntities::attributes);
        bus.addListener(ModEntities::placements);
    }

    private static void attributes(EntityAttributeCreationEvent event) {
        event.put(GNASHBACK.get(), GnashbackEntity.attributes().build());
        event.put(SHRIKEWING.get(), ShrikewingEntity.attributes().build());
        event.put(CHAINED_MATRIARCH.get(), ChainedMatriarchEntity.attributes().build());
        event.put(LUMEN_MITE.get(), LumenMiteEntity.attributes().build());
        event.put(ORRERY_WARDEN.get(), OrreryWardenEntity.attributes().build());
        event.put(ECLIPSE_LEVIATHAN.get(), EclipseLeviathanEntity.attributes().build());
        event.put(LANTERNRAY.get(), LanternrayEntity.attributes().build());
        event.put(MURKJAW.get(), MurkjawEntity.attributes().build());
        event.put(DEEPCALLER.get(), DeepcallerEntity.attributes().build());
    }

    private static void placements(RegisterSpawnPlacementsEvent event) {
        event.register(GNASHBACK.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                Monster::checkAnyLightMonsterSpawnRules, RegisterSpawnPlacementsEvent.Operation.REPLACE);
        // Both live in the open by day as well as by night (the biome spawn weights keep them few).
        event.register(SHRIKEWING.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                Monster::checkAnyLightMonsterSpawnRules, RegisterSpawnPlacementsEvent.Operation.REPLACE);
        // the abyss's creatures hover over the islands they spawn on
        event.register(LUMEN_MITE.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                Monster::checkAnyLightMonsterSpawnRules, RegisterSpawnPlacementsEvent.Operation.REPLACE);
        event.register(ORRERY_WARDEN.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                Monster::checkAnyLightMonsterSpawnRules, RegisterSpawnPlacementsEvent.Operation.REPLACE);
        // the Expanse's creatures spawn anywhere in its water (their numbers are capped by FrontierEvents)
        event.register(LANTERNRAY.get(), SpawnPlacementTypes.IN_WATER, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                (type, level, reason, pos, random) -> level.getFluidState(pos).is(net.minecraft.tags.FluidTags.WATER), RegisterSpawnPlacementsEvent.Operation.REPLACE);
        event.register(MURKJAW.get(), SpawnPlacementTypes.IN_WATER, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                (type, level, reason, pos, random) -> level.getFluidState(pos).is(net.minecraft.tags.FluidTags.WATER)
                        && level.getDifficulty() != net.minecraft.world.Difficulty.PEACEFUL, RegisterSpawnPlacementsEvent.Operation.REPLACE);
    }
}
