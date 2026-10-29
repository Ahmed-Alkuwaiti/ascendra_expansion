package com.unstablefrontiers.client;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.registry.ModEntities;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraft.world.entity.Entity;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import software.bernie.geckolib.animatable.GeoAnimatable;
import software.bernie.geckolib.model.DefaultedEntityGeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/**
 * Client-only setup: the creatures are drawn by GeckoLib from assets/unstable_frontiers/{geo,animations,textures}/entity, with
 * the glowing parts (eyes, the Matriarch's sac) from each texture's _glowmask. Only loaded on the physical client.
 */
public final class FrontierClient {
    private FrontierClient() {}

    public static void init(IEventBus modBus) {
        modBus.addListener(FrontierClient::renderers);
    }

    private static void renderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(ModEntities.GNASHBACK.get(), ctx -> new Renderer<>(ctx, "gnashback", 1.0F, 1.3F));
        event.registerEntityRenderer(ModEntities.SHRIKEWING.get(), ctx -> new Renderer<>(ctx, "shrikewing", 1.4F, 1.0F));
        event.registerEntityRenderer(ModEntities.CHAINED_MATRIARCH.get(), ctx -> new Renderer<>(ctx, "chained_matriarch", 1.0F, 2.4F));
        event.registerEntityRenderer(ModEntities.ACID_GLOB.get(), ctx -> new ThrownItemRenderer<>(ctx, 1.5F, true));
    }

    /** A creature renderer: the model, a glow layer, a shadow that matches its size, and no vanilla death tip-over. */
    static class Renderer<T extends Entity & GeoAnimatable> extends GeoEntityRenderer<T> {
        Renderer(EntityRendererProvider.Context ctx, String name, float scale, float shadow) {
            super(ctx, new DefaultedEntityGeoModel<>(UnstableFrontiers.id(name)));
            withScale(scale);
            addRenderLayer(new AutoGlowingGeoLayer<>(this));
            shadowRadius = shadow;
        }

        @Override
        protected float getDeathMaxRotation(T animatable) {
            return 0.0F;   // each creature has its own death animation
        }
    }
}
