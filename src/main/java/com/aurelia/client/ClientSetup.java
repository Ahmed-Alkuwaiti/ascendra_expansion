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

        spec(event, ModEntities.VORATH.get(), MobModels.VORATH, MobModels.VORATH_NAMES, MobModels.VORATH_ANIMS,
                MobModels.VORATH_SHADOW, "vorath", true);
        spec(event, ModEntities.WHITE_SILENCE.get(), MobModels.WHITE_SILENCE, MobModels.WHITE_SILENCE_NAMES, MobModels.WHITE_SILENCE_ANIMS,
                MobModels.WHITE_SILENCE_SHADOW, "white_silence", false);
        spec(event, ModEntities.KHARZUL.get(), MobModels.KHARZUL, MobModels.KHARZUL_NAMES, MobModels.KHARZUL_ANIMS,
                MobModels.KHARZUL_SHADOW, "kharzul", false);
        spec(event, ModEntities.CORALCLAD_JUGGERNAUT.get(), MobModels.CORALCLAD_JUGGERNAUT, MobModels.CORALCLAD_JUGGERNAUT_NAMES, MobModels.CORALCLAD_JUGGERNAUT_ANIMS,
                MobModels.CORALCLAD_JUGGERNAUT_SHADOW, "coralclad_juggernaut", false);
        spec(event, ModEntities.TIDECALLER.get(), MobModels.TIDECALLER, MobModels.TIDECALLER_NAMES, MobModels.TIDECALLER_ANIMS,
                MobModels.TIDECALLER_SHADOW, "tidecaller", false);
        spec(event, ModEntities.RAZORCLAW.get(), MobModels.RAZORCLAW, MobModels.RAZORCLAW_NAMES, MobModels.RAZORCLAW_ANIMS,
                MobModels.RAZORCLAW_SHADOW, "razorclaw", false);
        spec(event, ModEntities.RIMEGUARD.get(), MobModels.RIMEGUARD, MobModels.RIMEGUARD_NAMES, MobModels.RIMEGUARD_ANIMS,
                MobModels.RIMEGUARD_SHADOW, "rimeguard", false);
        spec(event, ModEntities.HUSHWRAITH.get(), MobModels.HUSHWRAITH, MobModels.HUSHWRAITH_NAMES, MobModels.HUSHWRAITH_ANIMS,
                MobModels.HUSHWRAITH_SHADOW, "hushwraith", false);
        spec(event, ModEntities.RIMEFANG.get(), MobModels.RIMEFANG, MobModels.RIMEFANG_NAMES, MobModels.RIMEFANG_ANIMS,
                MobModels.RIMEFANG_SHADOW, "rimefang", false);
        spec(event, ModEntities.SANDGLASS_SENTINEL.get(), MobModels.SANDGLASS_SENTINEL, MobModels.SANDGLASS_SENTINEL_NAMES, MobModels.SANDGLASS_SENTINEL_ANIMS,
                MobModels.SANDGLASS_SENTINEL_SHADOW, "sandglass_sentinel", false);
        spec(event, ModEntities.SUNSEER.get(), MobModels.SUNSEER, MobModels.SUNSEER_NAMES, MobModels.SUNSEER_ANIMS,
                MobModels.SUNSEER_SHADOW, "sunseer", false);
        spec(event, ModEntities.GLASSWING_SCARAB.get(), MobModels.GLASSWING_SCARAB, MobModels.GLASSWING_SCARAB_NAMES, MobModels.GLASSWING_SCARAB_ANIMS,
                MobModels.GLASSWING_SCARAB_SHADOW, "glasswing_scarab", false);
        // the White Silence's reflections wear her model and her texture
        spec(event, ModEntities.PALE_MIRAGE.get(), MobModels.WHITE_SILENCE, MobModels.WHITE_SILENCE_NAMES, MobModels.WHITE_SILENCE_ANIMS,
                MobModels.WHITE_SILENCE_SHADOW, "white_silence", false);

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
