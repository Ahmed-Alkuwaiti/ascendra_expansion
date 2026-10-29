package com.unstablefrontiers.registry;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.entity.AcidGlobEntity;
import com.unstablefrontiers.entity.ChainedMatriarchEntity;
import com.unstablefrontiers.entity.GnashbackEntity;
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
    }

    private static void placements(RegisterSpawnPlacementsEvent event) {
        event.register(GNASHBACK.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                Monster::checkAnyLightMonsterSpawnRules, RegisterSpawnPlacementsEvent.Operation.REPLACE);
        // Both live in the open by day as well as by night (the biome spawn weights keep them few).
        event.register(SHRIKEWING.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                Monster::checkAnyLightMonsterSpawnRules, RegisterSpawnPlacementsEvent.Operation.REPLACE);
    }
}
