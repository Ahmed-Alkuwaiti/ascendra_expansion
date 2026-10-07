package com.aurelia.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

/**
 * A model built from the part list in MobModels. Animation is driven by a tag on each part:
 * head, legA, legB (opposite phase), armA, armB, wingL, wingR (flap), spin (orbits its pivot), sway (gentle drift), jaw (opens and closes),
 * spinR (reverse), spinS (slow), bloom (petals breathing open and shut), pulse (a heartbeat), undulate (a travelling side-to-side wave down a body), flutter (fins and frills), finL, finR (slow paddling), none.
 * Parts may be nested; a part's name here is its path (parent/child) and children follow their parent.
 */
public class SpecModel<T extends Entity> extends EntityModel<T> {
    private final ModelPart root;
    private final ModelPart[] parts;
    private final String[] anims;
    private final float[] baseX;
    private final float[] baseY;
    private final float[] baseZ;

    public SpecModel(ModelPart root, String[] names, String[] anims) {
        this.root = root;
        this.anims = anims;
        this.parts = new ModelPart[names.length];
        this.baseX = new float[names.length];
        this.baseY = new float[names.length];
        this.baseZ = new float[names.length];
        for (int i = 0; i < names.length; i++) {
            ModelPart node = root;
            for (String segment : names[i].split("/")) {
                node = node.getChild(segment);
            }
            this.parts[i] = node;
            this.baseX[i] = this.parts[i].xRot;
            this.baseY[i] = this.parts[i].yRot;
            this.baseZ[i] = this.parts[i].zRot;
        }
    }

    @Override
    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks,
                          float netHeadYaw, float headPitch) {
        for (int i = 0; i < this.parts.length; i++) {
            ModelPart p = this.parts[i];
            switch (this.anims[i]) {
                case "head" -> {
                    p.yRot = this.baseY[i] + netHeadYaw * Mth.DEG_TO_RAD;
                    p.xRot = this.baseX[i] + headPitch * Mth.DEG_TO_RAD;
                }
                case "legA" -> p.xRot = this.baseX[i] + Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount;
                case "legB" -> p.xRot = this.baseX[i] + Mth.cos(limbSwing * 0.6662F + Mth.PI) * 1.4F * limbSwingAmount;
                case "armA" -> p.xRot = this.baseX[i] + Mth.cos(limbSwing * 0.6662F + Mth.PI) * 0.8F * limbSwingAmount;
                case "armB" -> p.xRot = this.baseX[i] + Mth.cos(limbSwing * 0.6662F) * 0.8F * limbSwingAmount;
                case "wingL" -> p.zRot = this.baseZ[i] + Mth.sin(ageInTicks * 0.6F) * 0.55F;
                case "wingR" -> p.zRot = this.baseZ[i] - Mth.sin(ageInTicks * 0.6F) * 0.55F;
                case "spin" -> p.yRot = this.baseY[i] + ageInTicks * 0.12F;
                case "spinR" -> p.yRot = this.baseY[i] - ageInTicks * 0.09F;
                case "spinS" -> p.yRot = this.baseY[i] + ageInTicks * 0.05F;
                case "bloom" -> p.xRot = this.baseX[i] + Mth.sin(ageInTicks * 0.05F + i * 0.4F) * 0.12F;
                case "jaw" -> p.xRot = this.baseX[i] + (Mth.sin(ageInTicks * 0.07F) * 0.5F + 0.5F) * 0.3F;
                case "pulse" -> {
                    float beat = 1.0F + Math.max(0.0F, Mth.sin(ageInTicks * 0.25F)) * 0.22F;
                    p.xScale = beat;
                    p.yScale = beat;
                    p.zScale = beat;
                }
                case "undulate" -> p.yRot = this.baseY[i] + Mth.sin(ageInTicks * 0.12F - i * 0.35F) * 0.12F;
                case "flutter" -> p.zRot = this.baseZ[i] + Mth.sin(ageInTicks * 0.3F + i * 0.9F) * 0.12F;
                case "finL" -> p.zRot = this.baseZ[i] + Mth.sin(ageInTicks * 0.14F) * 0.3F;
                case "finR" -> p.zRot = this.baseZ[i] - Mth.sin(ageInTicks * 0.14F) * 0.3F;
                case "sway" -> {
                    p.xRot = this.baseX[i] + Mth.sin(ageInTicks * 0.08F + i * 0.7F) * 0.07F;
                    p.zRot = this.baseZ[i] + Mth.cos(ageInTicks * 0.06F + i * 0.5F) * 0.05F;
                }
                default -> { }
            }
        }
    }

    @Override
    public void renderToBuffer(PoseStack poseStack, VertexConsumer buffer, int packedLight, int packedOverlay,
                               float red, float green, float blue, float alpha) {
        this.root.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
    }
}
