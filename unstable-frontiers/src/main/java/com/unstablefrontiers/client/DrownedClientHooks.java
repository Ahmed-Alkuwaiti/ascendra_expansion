package com.unstablefrontiers.client;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.drowned.DivingGearItem;
import com.unstablefrontiers.drowned.DrownedDimension;
import com.unstablefrontiers.drowned.DrownedGear;
import com.unstablefrontiers.drowned.DrownedTerrain;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.material.FogType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.event.ViewportEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;

/**
 * The Drowned Expanse on the client: how far you see under water (short without goggles, much further with them, and
 * further near the sunlit top than in the trench), the water's colour by depth, and the rig's air gauge above the hunger
 * bar. Only the Drowned Expanse is touched; water everywhere else in the pack looks as it always did.
 */
public final class DrownedClientHooks {
    private DrownedClientHooks() {}

    static void init(IEventBus modBus, IEventBus game) {
        modBus.addListener(DrownedClientHooks::layers);
        game.addListener(DrownedClientHooks::fog);
        game.addListener(DrownedClientHooks::fogColor);
    }

    /** Tide glyphs glow only for a player wearing goggles. */
    public static boolean seesGlyphs() {
        LocalPlayer p = Minecraft.getInstance().player;
        return p != null && !DrownedGear.goggles(p).isEmpty();
    }

    /** 0 in the trench, 1 just under the surface. */
    private static float depthLight(double y) {
        return Mth.clamp((float) (y - 40) / (DrownedTerrain.SURFACE - 40), 0.0F, 1.0F);
    }

    private static void fog(ViewportEvent.RenderFog event) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer p = mc.player;
        if (p == null || mc.level == null || !DrownedDimension.is(mc.level) || event.getCamera().getFluidInCamera() != FogType.WATER) {
            return;
        }
        float f = depthLight(event.getCamera().getPosition().y);
        float far;
        if (DrownedGear.deepSight(p)) {
            far = 80 + 24 * f;
        } else if (!DrownedGear.goggles(p).isEmpty()) {
            far = 52 + 28 * f;
        } else {
            far = 14 + 10 * f;
        }
        if (p.hasEffect(MobEffects.NIGHT_VISION) || p.hasEffect(MobEffects.CONDUIT_POWER)) {
            far = Math.max(far, event.getFarPlaneDistance());
        }
        event.setNearPlaneDistance(-8.0F);
        event.setFarPlaneDistance(far);
        event.setCanceled(true);
    }

    private static void fogColor(ViewportEvent.ComputeFogColor event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null || !DrownedDimension.is(mc.level) || event.getCamera().getFluidInCamera() != FogType.WATER) {
            return;
        }
        float f = depthLight(event.getCamera().getPosition().y);
        float lift = DrownedGear.goggles(mc.player).isEmpty() ? 1.0F : 1.25F;
        event.setRed(Math.min(1.0F, Mth.lerp(f, 0.05F, 0.10F) * lift));
        event.setGreen(Math.min(1.0F, Mth.lerp(f, 0.14F, 0.42F) * lift));
        event.setBlue(Math.min(1.0F, Mth.lerp(f, 0.22F, 0.55F) * lift));
    }

    private static void layers(RegisterGuiLayersEvent event) {
        event.registerAbove(VanillaGuiLayers.AIR_LEVEL, UnstableFrontiers.id("rig_air"), DrownedClientHooks::gauge);
    }

    /** The rig's gauge: shown while it is worn and you are under water, or while it is not full. */
    private static void gauge(GuiGraphics g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer p = mc.player;
        if (p == null || mc.options.hideGui || p.isSpectator() || !mc.gameMode.canHurtPlayer()) {
            return;
        }
        ItemStack rig = DrownedGear.rig(p);
        if (rig.isEmpty() || !(rig.getItem() instanceof DivingGearItem gear)) {
            return;
        }
        int air = DivingGearItem.air(rig);
        int cap = gear.capacity();
        if (!p.isUnderWater() && air >= cap) {
            return;
        }
        int w = g.guiWidth(), h = g.guiHeight();
        int x = w / 2 + 10, y = h - mc.gui.rightHeight - 9;
        mc.gui.rightHeight += 10;
        float frac = cap <= 0 ? 0 : Mth.clamp(air / (float) cap, 0.0F, 1.0F);
        int colour = air <= 10 ? ((p.tickCount / 5) % 2 == 0 ? 0xFFFF4040 : 0xFF801010) : air <= 30 ? 0xFFFFD040 : 0xFF40E0FF;
        g.fill(x, y + 2, x + 81, y + 7, 0xA0000000);
        g.fill(x + 1, y + 3, x + 1 + Math.round(79 * frac), y + 6, colour);
        Component label = Component.translatable("hud.unstable_frontiers.rig", air / 60, String.format("%02d", air % 60));
        int tw = mc.font.width(label);
        g.drawString(mc.font, label, x - tw - 3, y, colour, true);
    }
}
