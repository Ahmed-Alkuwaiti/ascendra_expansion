package com.unstablefrontiers.config;

import net.neoforged.neoforge.common.ModConfigSpec;

/**
 * Every limit that scales combat density. Each numeric limit defaults to -1, which means "use the preset"; any other value
 * overrides the preset for that one limit. Ranges are enforced by Forge: an out-of-range value is reset to its default.
 */
public final class FrontierConfig {
    public enum Preset { CONSERVATIVE, STANDARD, HIGH_DENSITY }

    public static final ModConfigSpec SPEC;

    public static final ModConfigSpec.EnumValue<Preset> PRESET;

    private static final ModConfigSpec.IntValue ENCOUNTER_PER_PLAYER;
    private static final ModConfigSpec.IntValue ENCOUNTER_PER_TOWER;
    private static final ModConfigSpec.IntValue ACTIVE_TOWERS;
    private static final ModConfigSpec.IntValue WAVES_PER_FLOOR;
    private static final ModConfigSpec.IntValue MOBS_PER_WAVE;
    private static final ModConfigSpec.IntValue WAVE_COOLDOWN;
    private static final ModConfigSpec.IntValue AMBIENT_PER_PLAYER;
    private static final ModConfigSpec.IntValue AMBIENT_INTERVAL;
    private static final ModConfigSpec.IntValue RIVALRY_RADIUS;
    private static final ModConfigSpec.IntValue AI_INTERVAL;
    private static final ModConfigSpec.IntValue FIGHTS_PER_PLAYER;
    private static final ModConfigSpec.IntValue DROPS_PER_MOB;
    private static final ModConfigSpec.DoubleValue PARTICLES;

    public static final ModConfigSpec.IntValue PURSUIT_TICKS;
    public static final ModConfigSpec.IntValue RIVALRY_COOLDOWN;
    public static final ModConfigSpec.IntValue LEASH_RADIUS;
    public static final ModConfigSpec.IntValue DISENGAGE_TICKS;
    public static final ModConfigSpec.IntValue RESIDENT_RESPAWN;
    public static final ModConfigSpec.IntValue ABILITY_INTERVAL;
    public static final ModConfigSpec.IntValue BEACON_RADIUS;
    public static final ModConfigSpec.IntValue RETURN_COOLDOWN_SECONDS;


    static {
        ModConfigSpec.Builder b = new ModConfigSpec.Builder();

        b.comment("Combat density. Pick a preset, then override single limits below (-1 = use the preset).",
                "CONSERVATIVE suits weaker machines or busy servers, STANDARD is the default (and suits a 4-core i3-12100 with 32 GB),",
                "HIGH_DENSITY is crowded and best on 6+ cores. The server thread, not the GPU, is what these limits protect.",
                "See README for the exact numbers each preset uses.").push("density");
        PRESET = b.defineEnum("preset", Preset.STANDARD);
        ENCOUNTER_PER_PLAYER = b.comment("Landmark creatures alive at once, per participating player.").defineInRange("encounterMobsPerPlayer", -1, -1, 64);
        ENCOUNTER_PER_TOWER = b.comment("Landmark creatures alive at once in one landmark, however many players.").defineInRange("encounterMobsPerLandmark", -1, -1, 128);
        ACTIVE_TOWERS = b.comment("Landmarks with a fight running at once across the whole server.").defineInRange("simultaneousEncounters", -1, -1, 32);
        WAVES_PER_FLOOR = b.comment("Waves in a wave fight when the landmark does not set its own count.").defineInRange("wavesPerFloor", -1, -1, 10);
        MOBS_PER_WAVE = b.comment("Creatures in one wave before the per-player and per-landmark limits apply.").defineInRange("mobsPerWave", -1, -1, 32);
        WAVE_COOLDOWN = b.comment("Minimum ticks between reinforcement waves (20 ticks = 1 second).").defineInRange("waveCooldownTicks", -1, -1, 12000);
        AMBIENT_PER_PLAYER = b.comment("Most residents (creatures living at carrion fields and similar) placed around one landmark.").defineInRange("residentsPerLandmark", -1, -1, 64);
        AMBIENT_INTERVAL = b.comment("Ticks between night overflights near one player (a hunting flyer crossing the sky).").defineInRange("overflightIntervalTicks", -1, -1, 72000);
        RIVALRY_RADIUS = b.comment("Blocks a predator looks for prey. Searches are boxes of this size, never world scans.").defineInRange("rivalrySearchRadius", -1, -1, 64);
        AI_INTERVAL = b.comment("Ticks between rivalry updates (the only AI this mod adds).").defineInRange("aiUpdateIntervalTicks", -1, -1, 400);
        FIGHTS_PER_PLAYER = b.comment("Predator-versus-prey fights this mod starts near each player at once.").defineInRange("rivalryFightsPerPlayer", -1, -1, 16);
        DROPS_PER_MOB = b.comment("Most item stacks one frontier creature may drop.").defineInRange("maxDropsPerMob", -1, -1, 32);
        PARTICLES = b.comment("Particle multiplier for this mod's effects (0 = none, -1 = preset).").defineInRange("particleDensity", -1.0D, -1.0D, 2.0D);
        b.pop();

        b.push("behaviour");
        PURSUIT_TICKS = b.comment("How long a predator chases its prey before giving up.").defineInRange("pursuitTicks", 200, 20, 2400);
        RIVALRY_COOLDOWN = b.comment("Ticks a predator rests after a fight before it hunts again.").defineInRange("rivalryCooldownTicks", 600, 0, 24000);
        LEASH_RADIUS = b.comment("Blocks a landmark creature may stray from its fight before it is called back.").defineInRange("leashRadius", 40, 12, 128);
        DISENGAGE_TICKS = b.comment("Ticks with no player near before an unfinished fight resets (creatures are removed, cleared parts stay cleared).")
                .defineInRange("disengageTicks", 400, 100, 24000);
        RESIDENT_RESPAWN = b.comment("Ticks before residents that were all killed move back in (24000 = one Minecraft day).")
                .defineInRange("residentReturnTicks", 24000, 1200, 720000);
        ABILITY_INTERVAL = b.comment("Ticks between an elite's telegraphed abilities.").defineInRange("eliteAbilityIntervalTicks", 160, 40, 1200);
        BEACON_RADIUS = b.comment("Blocks around a Cage Beacon where frontier creatures do not spawn naturally and residents do not return.")
                .defineInRange("cageBeaconRadius", 48, 8, 128);
        RETURN_COOLDOWN_SECONDS = b.comment("Cooldown on /frontier return, the recovery route home.").defineInRange("returnCommandCooldownSeconds", 60, 0, 3600);
        b.pop();

        SPEC = b.build();
    }

    private FrontierConfig() {}

    private static int pick(ModConfigSpec.IntValue override, int conservative, int standard, int high) {
        int v = override.get();
        if (v >= 0) {
            return v;
        }
        return switch (PRESET.get()) {
            case CONSERVATIVE -> conservative;
            case HIGH_DENSITY -> high;
            default -> standard;
        };
    }

    // The preset table. Keep README's table in step with these numbers.
    public static int encounterPerPlayer() { return pick(ENCOUNTER_PER_PLAYER, 6, 10, 16); }
    public static int encounterPerLandmark() { return pick(ENCOUNTER_PER_TOWER, 10, 16, 28); }
    public static int activeEncounters() { return pick(ACTIVE_TOWERS, 2, 3, 6); }
    public static int wavesPerFloor() { return Math.max(1, pick(WAVES_PER_FLOOR, 2, 3, 4)); }
    public static int mobsPerWave() { return Math.max(1, pick(MOBS_PER_WAVE, 3, 5, 8)); }
    public static int waveCooldown() { return pick(WAVE_COOLDOWN, 300, 200, 140); }
    public static int residentsPerLandmark() { return pick(AMBIENT_PER_PLAYER, 4, 6, 10); }
    public static int overflightInterval() { return Math.max(600, pick(AMBIENT_INTERVAL, 12000, 6000, 3600)); }
    public static int rivalryRadius() { return Math.max(4, pick(RIVALRY_RADIUS, 16, 24, 32)); }
    public static int aiInterval() { return Math.max(5, pick(AI_INTERVAL, 60, 40, 20)); }
    public static int fightsPerPlayer() { return pick(FIGHTS_PER_PLAYER, 1, 2, 4); }
    public static int dropsPerMob() { return pick(DROPS_PER_MOB, 3, 4, 6); }

    public static double particles() {
        double v = PARTICLES.get();
        if (v >= 0) {
            return v;
        }
        return PRESET.get() == Preset.CONSERVATIVE ? 0.4D : 1.0D;
    }

    /** Scales a particle count, keeping at least one when particles are on at all. */
    public static int particleCount(int base) {
        double p = particles();
        return p <= 0 ? 0 : Math.max(1, (int) Math.round(base * p));
    }

    public static String describe() {
        return "preset=" + PRESET.get() + " encounter/player=" + encounterPerPlayer() + " encounter/landmark=" + encounterPerLandmark()
                + " activeEncounters=" + activeEncounters() + " waves=" + wavesPerFloor() + " mobs/wave=" + mobsPerWave()
                + " waveCooldown=" + waveCooldown() + " residents/landmark=" + residentsPerLandmark() + " overflightInterval=" + overflightInterval()
                + " rivalryRadius=" + rivalryRadius() + " aiInterval=" + aiInterval() + " fights/player=" + fightsPerPlayer()
                + " drops/mob=" + dropsPerMob() + " particles=" + particles();
    }
}
