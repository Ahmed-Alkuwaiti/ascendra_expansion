package com.aurelia;

import net.minecraftforge.common.ForgeConfigSpec;

/** config/aurelia-client.toml: settings that only change what this computer draws. */
public final class AureliaClientConfig {
    private AureliaClientConfig() {}

    public static final ForgeConfigSpec SPEC;
    public static final ForgeConfigSpec.IntValue MOB_RENDER_DISTANCE;

    static {
        ForgeConfigSpec.Builder b = new ForgeConfigSpec.Builder();
        b.comment("Smoothness on this computer.").push("performance");
        MOB_RENDER_DISTANCE = b.comment("The mod's guards and creatures are not drawn past this many blocks (their models are detailed). Wardens and",
                "lieutenants are always drawn. 0 draws them at any distance.").defineInRange("mobRenderDistance", 64, 0, 512);
        b.pop();
        SPEC = b.build();
    }
}
