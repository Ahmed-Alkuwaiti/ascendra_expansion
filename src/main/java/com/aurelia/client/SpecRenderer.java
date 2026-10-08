package com.aurelia.client;

import com.aurelia.AureliaMod;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Mob;

/** Renders any mob whose model comes from MobModels. Flying mobs can pitch with their flight direction. */
public class SpecRenderer<T extends Mob> extends MobRenderer<T, SpecModel<T>> {
    private final ResourceLocation texture;
    private final boolean tilt;

    public SpecRenderer(EntityRendererProvider.Context context, ModelLayerLocation layer, String[] names,
                        String[] anims, float shadow, String textureName, boolean tilt) {
        super(context, new SpecModel<T>(context.bakeLayer(layer), names, anims), shadow);
        this.texture = new ResourceLocation(AureliaMod.MODID, "textures/entity/" + textureName + ".png");
        this.tilt = tilt;
        this.addLayer(new GlowLayer<T>(this, new ResourceLocation(AureliaMod.MODID, "textures/entity/" + textureName + "_glow.png")));
    }

    @Override
    protected void setupRotations(T entity, PoseStack poseStack, float ageInTicks, float rotationYaw, float partialTicks) {
        super.setupRotations(entity, poseStack, ageInTicks, rotationYaw, partialTicks);
        if (this.tilt) {
            poseStack.mulPose(Axis.XP.rotationDegrees(entity.getXRot()));
        }
    }

    /** Past the client's configured distance, ordinary guards and creatures are not drawn; Wardens and lieutenants always are. */
    @Override
    public boolean shouldRender(T entity, net.minecraft.client.renderer.culling.Frustum frustum, double camX, double camY, double camZ) {
        if (!super.shouldRender(entity, frustum, camX, camY, camZ)) {
            return false;
        }
        int d = com.aurelia.AureliaClientConfig.MOB_RENDER_DISTANCE.get();
        if (d <= 0 || entity instanceof com.aurelia.entity.AureliaBoss || entity instanceof com.aurelia.entity.Lieutenant) {
            return true;
        }
        return entity.distanceToSqr(camX, camY, camZ) <= (double) d * d;
    }

    @Override
    public ResourceLocation getTextureLocation(T entity) {
        return this.texture;
    }
}
