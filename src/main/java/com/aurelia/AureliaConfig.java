package com.aurelia;

import net.minecraftforge.common.ForgeConfigSpec;

/**
 * config/aurelia-common.toml. Multipliers on every Aurelia creature's health and damage, applied once when it first appears, so a
 * pack can tune the whole mod against its own gear without rebuilding it. 1.0 is the mod's own balance (tuned for Ascendra:
 * Armageddon, Goety and Apotheosis gear, no spells).
 */
public final class AureliaConfig {
    private AureliaConfig() {}

    public static final ForgeConfigSpec SPEC;
    public static final ForgeConfigSpec.DoubleValue WARDEN_HEALTH;
    public static final ForgeConfigSpec.DoubleValue WARDEN_DAMAGE;
    public static final ForgeConfigSpec.DoubleValue LIEUTENANT_HEALTH;
    public static final ForgeConfigSpec.DoubleValue LIEUTENANT_DAMAGE;
    public static final ForgeConfigSpec.DoubleValue GUARD_HEALTH;
    public static final ForgeConfigSpec.DoubleValue GUARD_DAMAGE;
    public static final ForgeConfigSpec.DoubleValue PARTICLE_DENSITY;
    public static final ForgeConfigSpec.BooleanValue STARTER_KIT;
    public static final ForgeConfigSpec.IntValue GUARD_SLEEP_DISTANCE;
    public static final ForgeConfigSpec.IntValue GUARD_SLEEP_INTERVAL;

    static {
        ForgeConfigSpec.Builder b = new ForgeConfigSpec.Builder();
        b.comment("Health and damage multipliers. 1.0 is the mod's own balance. They apply to creatures as they first appear.").push("balance");
        WARDEN_HEALTH = b.comment("The eight Wardens and the Unmaker: health").defineInRange("wardenHealth", 1.0, 0.1, 20.0);
        WARDEN_DAMAGE = b.comment("The eight Wardens and the Unmaker: damage, including their signature moves").defineInRange("wardenDamage", 1.0, 0.1, 20.0);
        LIEUTENANT_HEALTH = b.comment("The lieutenants and the Heralds: health").defineInRange("lieutenantHealth", 1.0, 0.1, 20.0);
        LIEUTENANT_DAMAGE = b.comment("The lieutenants and the Heralds: damage").defineInRange("lieutenantDamage", 1.0, 0.1, 20.0);
        GUARD_HEALTH = b.comment("Citadel, dungeon and realm guards: health").defineInRange("guardHealth", 1.0, 0.1, 20.0);
        GUARD_DAMAGE = b.comment("Citadel, dungeon and realm guards: damage").defineInRange("guardDamage", 1.0, 0.1, 20.0);
        b.pop();
        b.comment("Getting started.").push("onboarding");
        STARTER_KIT = b.comment("Give each player, once, a Wayfarer's Guide, the Wayfinder's Lodestar and the Aurelian Bestiary when they first join.")
                .define("starterKit", true);
        b.pop();
        b.comment("Smoothness. Lower these if fights, citadels or dungeons stutter.").push("performance");
        PARTICLE_DENSITY = b.comment("Share of the mod's ambient and effect particles that are sent (1.0 all, 0.5 half, 0 none).",
                "Attack warnings always show in full.").defineInRange("particleDensity", 0.7, 0.0, 1.0);
        GUARD_SLEEP_DISTANCE = b.comment("Guards with no player within this many blocks doze: they skip most of their ticks until someone comes near.",
                "Citadels, lairs and dungeons hold hundreds of guards; this keeps the ones nobody is near from costing anything. 0 turns it off.")
                .defineInRange("guardSleepDistance", 48, 0, 256);
        GUARD_SLEEP_INTERVAL = b.comment("A dozing guard still ticks once every this many ticks, so it stays alive to the world.")
                .defineInRange("guardSleepInterval", 20, 2, 200);
        b.pop();
        SPEC = b.build();
    }
}
