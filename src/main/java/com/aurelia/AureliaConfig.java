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
        SPEC = b.build();
    }
}
