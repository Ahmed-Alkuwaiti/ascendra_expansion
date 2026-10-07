package com.aurelia.client;

import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.EyesLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Mob;

/** Draws a mob's glow texture at full brightness, so eyes, runes, hearts and lava cracks shine in the dark. */
public class GlowLayer<T extends Mob> extends EyesLayer<T, SpecModel<T>> {
    private final RenderType type;

    public GlowLayer(RenderLayerParent<T, SpecModel<T>> parent, ResourceLocation glowTexture) {
        super(parent);
        this.type = RenderType.eyes(glowTexture);
    }

    @Override
    public RenderType renderType() {
        return this.type;
    }
}
