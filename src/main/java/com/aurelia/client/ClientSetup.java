package com.aurelia.client;

import com.aurelia.AureliaMod;
import com.aurelia.entity.GroveAnt;
import com.aurelia.entity.HollowShade;
import com.aurelia.entity.SkySentinel;
import com.aurelia.registry.ModEntities;
import net.minecraft.client.model.SpiderModel;
import net.minecraft.client.model.ZombieModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Bosses and citadel guards use MobModels (custom box models). The three older natives reuse vanilla models. */
@Mod.EventBusSubscriber(modid = AureliaMod.MODID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public class ClientSetup {

    private static ResourceLocation tex(String name) {
        return new ResourceLocation(AureliaMod.MODID, "textures/entity/" + name + ".png");
    }

    private static <T extends Mob> void spec(EntityRenderersEvent.RegisterRenderers event, EntityType<T> type,
                                            ModelLayerLocation layer, String[] names, String[] anims, float shadow,
                                            String texture, boolean tilt) {
        event.registerEntityRenderer(type, ctx -> new SpecRenderer<T>(ctx, layer, names, anims, shadow, texture, tilt));
    }

    @SubscribeEvent
    public static void registerLayers(EntityRenderersEvent.RegisterLayerDefinitions event) {
        MobModels.register(event);
    }

    @SubscribeEvent
    public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {
        spec(event, ModEntities.MOSSBACK_TITAN.get(), MobModels.MOSSBACK_TITAN, MobModels.MOSSBACK_TITAN_NAMES, MobModels.MOSSBACK_TITAN_ANIMS,
                MobModels.MOSSBACK_TITAN_SHADOW, "mossback_titan", false);
        spec(event, ModEntities.TEMPEST_ROC.get(), MobModels.TEMPEST_ROC, MobModels.TEMPEST_ROC_NAMES, MobModels.TEMPEST_ROC_ANIMS,
                MobModels.TEMPEST_ROC_SHADOW, "tempest_roc", true);
        spec(event, ModEntities.HOLLOW_KING.get(), MobModels.HOLLOW_KING, MobModels.HOLLOW_KING_NAMES, MobModels.HOLLOW_KING_ANIMS,
                MobModels.HOLLOW_KING_SHADOW, "hollow_king", false);
        spec(event, ModEntities.BRAMBLE_SENTINEL.get(), MobModels.BRAMBLE_SENTINEL, MobModels.BRAMBLE_SENTINEL_NAMES, MobModels.BRAMBLE_SENTINEL_ANIMS,
                MobModels.BRAMBLE_SENTINEL_SHADOW, "bramble_sentinel", false);
        spec(event, ModEntities.SPORECAP.get(), MobModels.SPORECAP, MobModels.SPORECAP_NAMES, MobModels.SPORECAP_ANIMS,
                MobModels.SPORECAP_SHADOW, "sporecap", false);
        spec(event, ModEntities.ROOTSTALKER.get(), MobModels.ROOTSTALKER, MobModels.ROOTSTALKER_NAMES, MobModels.ROOTSTALKER_ANIMS,
                MobModels.ROOTSTALKER_SHADOW, "rootstalker", false);
        spec(event, ModEntities.CALCITE_SENTINEL.get(), MobModels.CALCITE_SENTINEL, MobModels.CALCITE_SENTINEL_NAMES, MobModels.CALCITE_SENTINEL_ANIMS,
                MobModels.CALCITE_SENTINEL_SHADOW, "calcite_sentinel", false);
        spec(event, ModEntities.STORM_WISP.get(), MobModels.STORM_WISP, MobModels.STORM_WISP_NAMES, MobModels.STORM_WISP_ANIMS,
                MobModels.STORM_WISP_SHADOW, "storm_wisp", false);
        spec(event, ModEntities.GALE_TALON.get(), MobModels.GALE_TALON, MobModels.GALE_TALON_NAMES, MobModels.GALE_TALON_ANIMS,
                MobModels.GALE_TALON_SHADOW, "gale_talon", true);
        spec(event, ModEntities.ASHBOUND_KNIGHT.get(), MobModels.ASHBOUND_KNIGHT, MobModels.ASHBOUND_KNIGHT_NAMES, MobModels.ASHBOUND_KNIGHT_ANIMS,
                MobModels.ASHBOUND_KNIGHT_SHADOW, "ashbound_knight", false);
        spec(event, ModEntities.SOUL_JAILER.get(), MobModels.SOUL_JAILER, MobModels.SOUL_JAILER_NAMES, MobModels.SOUL_JAILER_ANIMS,
                MobModels.SOUL_JAILER_SHADOW, "soul_jailer", false);
        spec(event, ModEntities.CINDER_HOUND.get(), MobModels.CINDER_HOUND, MobModels.CINDER_HOUND_NAMES, MobModels.CINDER_HOUND_ANIMS,
                MobModels.CINDER_HOUND_SHADOW, "cinder_hound", false);

        event.registerEntityRenderer(ModEntities.GROVE_ANT.get(),
                ctx -> new ScaledRenderer<GroveAnt, SpiderModel<GroveAnt>>(ctx,
                        new SpiderModel<GroveAnt>(ctx.bakeLayer(ModelLayers.SPIDER)), 1.0f, 1.3f, tex("grove_ant")));
        event.registerEntityRenderer(ModEntities.SKY_SENTINEL.get(),
                ctx -> new ScaledRenderer<SkySentinel, ZombieModel<SkySentinel>>(ctx,
                        new ZombieModel<SkySentinel>(ctx.bakeLayer(ModelLayers.ZOMBIE)), 0.6f, 1.15f, tex("sky_sentinel")));
        event.registerEntityRenderer(ModEntities.HOLLOW_SHADE.get(),
                ctx -> new ScaledRenderer<HollowShade, ZombieModel<HollowShade>>(ctx,
                        new ZombieModel<HollowShade>(ctx.bakeLayer(ModelLayers.ZOMBIE)), 0.5f, 1.0f, tex("hollow_shade")));
    }
}
