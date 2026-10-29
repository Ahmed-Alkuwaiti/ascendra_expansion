package com.unstablefrontiers.client;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.BufferUploader;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.Tesselator;
import com.mojang.blaze3d.vertex.VertexBuffer;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.mojang.math.Axis;
import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.abyss.AbyssTerrain;
import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.DimensionSpecialEffects;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;

/**
 * The Astral Abyss's sky, drawn without shaders: a dense starfield in three colours, a nebula band wound around the sky,
 * a dark ringed world eclipsing a pale sun high in the south, the far-off silhouettes of leviathans drifting along the
 * horizon, and a coloured beam over each of the abyss's places so they can be found from anywhere (each fades as you
 * come close enough to see the place itself). Everything sits behind the world at sky distance, so it costs the same at
 * any render distance.
 */
public class AbyssSkyEffects extends DimensionSpecialEffects {
    private static final ResourceLocation NEBULA = UnstableFrontiers.id("textures/environment/abyss_nebula.png");
    private static final ResourceLocation PLANET = UnstableFrontiers.id("textures/environment/abyss_planet.png");
    private static final ResourceLocation DRIFTER = UnstableFrontiers.id("textures/environment/abyss_drifter.png");
    private static final float[][] BEAM_COLORS = {
            {0.55F, 0.95F, 1.0F},   // landing
            {0.6F, 1.0F, 0.75F},    // starwell
            {0.75F, 0.7F, 1.0F},    // archive
            {1.0F, 0.85F, 0.5F},    // tether spire
            {1.0F, 0.45F, 0.35F},   // hollow crown
    };
    private VertexBuffer stars;

    public AbyssSkyEffects() {
        super(Float.NaN, false, SkyType.NONE, false, false);
    }

    @Override
    public Vec3 getBrightnessDependentFogColor(Vec3 fogColor, float brightness) {
        return fogColor;
    }

    @Override
    public boolean isFoggyAt(int x, int y) {
        return false;
    }

    @Override
    public boolean renderClouds(ClientLevel level, int ticks, float partialTick, PoseStack poseStack, double camX, double camY, double camZ,
                                Matrix4f modelViewMatrix, Matrix4f projectionMatrix) {
        return true;   // no clouds in the void
    }

    @Override
    public boolean renderSky(ClientLevel level, int ticks, float partialTick, Matrix4f modelViewMatrix, Camera camera, Matrix4f projectionMatrix,
                             boolean isFoggy, Runnable setupFog) {
        float t = ticks + partialTick;
        PoseStack ps = new PoseStack();
        ps.mulPose(modelViewMatrix);
        RenderSystem.depthMask(false);
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();

        // the nebula band, slowly turning
        ps.pushPose();
        ps.mulPose(Axis.YP.rotationDegrees(t * 0.004F));
        ps.mulPose(Axis.ZP.rotationDegrees(28.0F));
        band(ps.last().pose());
        ps.popPose();

        // stars (additive), turning with the band
        RenderSystem.blendFunc(com.mojang.blaze3d.platform.GlStateManager.SourceFactor.SRC_ALPHA, com.mojang.blaze3d.platform.GlStateManager.DestFactor.ONE);
        if (stars == null) {
            stars = buildStars();
        }
        ps.pushPose();
        ps.mulPose(Axis.YP.rotationDegrees(t * 0.004F));
        RenderSystem.setShaderColor(1, 1, 1, 1);
        stars.bind();
        stars.drawWithShader(ps.last().pose(), projectionMatrix, GameRenderer.getPositionColorShader());
        VertexBuffer.unbind();
        ps.popPose();

        // beams over the abyss's places
        beams(ps.last().pose(), camera.getPosition(), t);
        RenderSystem.defaultBlendFunc();

        // the ringed world high in the south, and the drifters on the horizon
        ps.pushPose();
        ps.mulPose(Axis.YP.rotationDegrees(180.0F));
        ps.mulPose(Axis.XP.rotationDegrees(-38.0F));
        quad(ps.last().pose(), PLANET, 0, 0, -100, 46, 1.0F);
        ps.popPose();
        for (int i = 0; i < 3; i++) {
            ps.pushPose();
            ps.mulPose(Axis.YP.rotationDegrees(i * 120 + t * (0.006F + i * 0.002F)));
            ps.mulPose(Axis.XP.rotationDegrees(-6.0F - i * 5));
            quad(ps.last().pose(), DRIFTER, 0, 0, -100, 9 + i * 3, 0.85F);
            ps.popPose();
        }
        RenderSystem.setShaderColor(1, 1, 1, 1);
        RenderSystem.disableBlend();
        RenderSystem.depthMask(true);
        return true;
    }

    private static VertexBuffer buildStars() {
        RandomSource r = RandomSource.create(4123L);
        BufferBuilder b = Tesselator.getInstance().begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR);
        for (int i = 0; i < 2600; i++) {
            double x = r.nextFloat() * 2 - 1, y = r.nextFloat() * 2 - 1, z = r.nextFloat() * 2 - 1;
            double d = x * x + y * y + z * z;
            if (d < 0.01D || d > 1.0D) {
                continue;
            }
            d = 1 / Math.sqrt(d);
            x *= d * 100;
            y *= d * 100;
            z *= d * 100;
            float size = 0.12F + r.nextFloat() * (r.nextInt(14) == 0 ? 0.55F : 0.22F);
            float c = r.nextFloat();
            float red = c < 0.15F ? 1.0F : c < 0.45F ? 0.7F : 0.95F;
            float green = c < 0.15F ? 0.85F : c < 0.45F ? 0.85F : 0.95F;
            float blue = c < 0.15F ? 0.6F : 1.0F;
            float a = 0.45F + r.nextFloat() * 0.55F;
            // a small quad facing the centre
            Vec3 n = new Vec3(x, y, z).normalize();
            Vec3 u = Math.abs(n.y) < 0.9 ? n.cross(new Vec3(0, 1, 0)).normalize() : n.cross(new Vec3(1, 0, 0)).normalize();
            Vec3 v = n.cross(u);
            double rot = r.nextDouble() * Math.PI;
            Vec3 uu = u.scale(Math.cos(rot)).add(v.scale(Math.sin(rot))).scale(size);
            Vec3 vv = n.cross(uu);
            Vec3 c0 = new Vec3(x, y, z);
            Vec3[] q = {c0.subtract(uu).subtract(vv), c0.add(uu).subtract(vv), c0.add(uu).add(vv), c0.subtract(uu).add(vv)};
            for (Vec3 p : q) {
                b.addVertex((float) p.x, (float) p.y, (float) p.z).setColor(red, green, blue, a);
            }
        }
        VertexBuffer vb = new VertexBuffer(VertexBuffer.Usage.STATIC);
        vb.bind();
        vb.upload(b.buildOrThrow());
        VertexBuffer.unbind();
        return vb;
    }

    /** A ring of 24 textured panels around the sky: the nebula. */
    private static void band(Matrix4f m) {
        RenderSystem.setShader(GameRenderer::getPositionTexColorShader);
        RenderSystem.setShaderTexture(0, NEBULA);
        BufferBuilder b = Tesselator.getInstance().begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_TEX_COLOR);
        int n = 24;
        float r = 100, h = 34;
        for (int i = 0; i < n; i++) {
            double a0 = 2 * Math.PI * i / n, a1 = 2 * Math.PI * (i + 1) / n;
            float x0 = (float) (Math.cos(a0) * r), z0 = (float) (Math.sin(a0) * r), x1 = (float) (Math.cos(a1) * r), z1 = (float) (Math.sin(a1) * r);
            float u0 = (float) i / n * 3, u1 = (float) (i + 1) / n * 3;
            b.addVertex(m, x0, -h, z0).setUv(u0, 1).setColor(1, 1, 1, 0.9F);
            b.addVertex(m, x1, -h, z1).setUv(u1, 1).setColor(1, 1, 1, 0.9F);
            b.addVertex(m, x1, h, z1).setUv(u1, 0).setColor(1, 1, 1, 0.9F);
            b.addVertex(m, x0, h, z0).setUv(u0, 0).setColor(1, 1, 1, 0.9F);
        }
        BufferUploader.drawWithShader(b.buildOrThrow());
    }

    private static void quad(Matrix4f m, ResourceLocation tex, float x, float y, float z, float s, float alpha) {
        RenderSystem.setShader(GameRenderer::getPositionTexColorShader);
        RenderSystem.setShaderTexture(0, tex);
        BufferBuilder b = Tesselator.getInstance().begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_TEX_COLOR);
        b.addVertex(m, x - s, y - s, z).setUv(0, 1).setColor(1, 1, 1, alpha);
        b.addVertex(m, x + s, y - s, z).setUv(1, 1).setColor(1, 1, 1, alpha);
        b.addVertex(m, x + s, y + s, z).setUv(1, 0).setColor(1, 1, 1, alpha);
        b.addVertex(m, x - s, y + s, z).setUv(0, 0).setColor(1, 1, 1, alpha);
        BufferUploader.drawWithShader(b.buildOrThrow());
    }

    /** A thin upright beam on the sky in the direction of each place, fading as the place itself comes into view. */
    private static void beams(Matrix4f m, Vec3 cam, float t) {
        RenderSystem.setShader(GameRenderer::getPositionColorShader);
        BufferBuilder b = Tesselator.getInstance().begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR);
        boolean any = false;
        for (int i = 0; i < AbyssTerrain.ANCHORS.length; i++) {
            AbyssTerrain.Anchor a = AbyssTerrain.ANCHORS[i];
            double dx = a.x() + 0.5 - cam.x, dz = a.z() + 0.5 - cam.z;
            double dist = Math.hypot(dx, dz);
            if (dist < 40) {
                continue;
            }
            float alpha = (float) Math.min(0.55, (dist - 40) / 160.0) * (0.85F + 0.15F * (float) Math.sin(t * 0.05F + i));
            double ux = dx / dist, uz = dz / dist;
            float px = (float) (ux * 95), pz = (float) (uz * 95);
            float wx = (float) (-uz * (i == 4 ? 1.4 : 0.8)), wz = (float) (ux * (i == 4 ? 1.4 : 0.8));
            float[] c = BEAM_COLORS[i];
            float bottom = (float) Math.max(-40, (a.top() - cam.y) * 95 / dist - 2), top = 70;
            b.addVertex(m, px - wx, bottom, pz - wz).setColor(c[0], c[1], c[2], alpha);
            b.addVertex(m, px + wx, bottom, pz + wz).setColor(c[0], c[1], c[2], alpha);
            b.addVertex(m, px + wx, top, pz + wz).setColor(c[0], c[1], c[2], 0.0F);
            b.addVertex(m, px - wx, top, pz - wz).setColor(c[0], c[1], c[2], 0.0F);
            any = true;
        }
        if (any) {
            BufferUploader.drawWithShader(b.buildOrThrow());
        } else {
            b.build();
        }
    }
}
