package com.aurelia.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Mob;

/** Renders a mob with a vanilla model at a custom size and with a custom texture. */
public class ScaledRenderer<T extends Mob, M extends EntityModel<T>> extends MobRenderer<T, M> {
    protected final ResourceLocation texture;
    protected final float scale;

    public ScaledRenderer(EntityRendererProvider.Context context, M model, float shadowRadius,
                          float scale, ResourceLocation texture) {
        super(context, model, shadowRadius);
        this.scale = scale;
        this.texture = texture;
    }

    @Override
    protected void scale(T entity, PoseStack poseStack, float partialTick) {
        poseStack.scale(this.scale, this.scale, this.scale);
    }

    @Override
    public ResourceLocation getTextureLocation(T entity) {
        return this.texture;
    }
}
