package com.unstablefrontiers.config;

import java.util.List;
import net.minecraftforge.common.ForgeConfigSpec;

/**
 * Every limit that scales combat density. Each numeric limit defaults to -1, which means "use the preset"; any other value
 * overrides the preset for that one limit. Ranges are enforced by Forge: an out-of-range value is reset to its default.
 */
public final class FrontierConfig {
    public enum Preset { CONSERVATIVE, STANDARD, HIGH_DENSITY }

    public static final ForgeConfigSpec SPEC;

    public static final ForgeConfigSpec.EnumValue<Preset> PRESET;

    private static final ForgeConfigSpec.IntValue ENCOUNTER_PER_PLAYER;
    private static final ForgeConfigSpec.IntValue ENCOUNTER_PER_TOWER;
    private static final ForgeConfigSpec.IntValue ACTIVE_TOWERS;
    private static final ForgeConfigSpec.IntValue WAVES_PER_FLOOR;
    private static final ForgeConfigSpec.IntValue MOBS_PER_WAVE;
    private static final ForgeConfigSpec.IntValue WAVE_COOLDOWN;
    private static final ForgeConfigSpec.IntValue AMBIENT_PER_PLAYER;
    private static final ForgeConfigSpec.IntValue AMBIENT_INTERVAL;
    private static final ForgeConfigSpec.IntValue RIVALRY_RADIUS;
    private static final ForgeConfigSpec.IntValue AI_INTERVAL;
    private static final ForgeConfigSpec.IntValue FIGHTS_PER_PLAYER;
    private static final ForgeConfigSpec.IntValue DROPS_PER_MOB;
    private static final ForgeConfigSpec.DoubleValue PARTICLES;

    public static final ForgeConfigSpec.IntValue PURSUIT_TICKS;
    public static final ForgeConfigSpec.IntValue RIVALRY_COOLDOWN;
    public static final ForgeConfigSpec.IntValue LEASH_RADIUS;
    public static final ForgeConfigSpec.IntValue DISENGAGE_TICKS;
    public static final ForgeConfigSpec.IntValue TOWER_CHANCE;
    public static final ForgeConfigSpec.IntValue RETURN_COOLDOWN_SECONDS;

    public static final ForgeConfigSpec.ConfigValue<List<? extends String>> FLOOR0, FLOOR1, FLOOR2, CROWN, CROWN_ESCORTS;
    public static final ForgeConfigSpec.ConfigValue<List<? extends String>> FLOOR0_FALLBACK, FLOOR1_FALLBACK, FLOOR2_FALLBACK,
            CROWN_FALLBACK, CROWN_ESCORTS_FALLBACK;
    public static final ForgeConfigSpec.ConfigValue<List<? extends String>> SWARM, RAPTORS_DAY, RAPTORS_NIGHT;
    public static final ForgeConfigSpec.ConfigValue<List<? extends String>> SWARM_FALLBACK, RAPTORS_DAY_FALLBACK, RAPTORS_NIGHT_FALLBACK;

    static {
        ForgeConfigSpec.Builder b = new ForgeConfigSpec.Builder();

        b.comment("Combat density. Pick a preset, then override single limits below (-1 = use the preset).",
                "CONSERVATIVE suits weaker machines or busy servers, STANDARD is the default, HIGH_DENSITY is crowded.",
                "See README for the exact numbers each preset uses.").push("density");
        PRESET = b.defineEnum("preset", Preset.STANDARD);
        ENCOUNTER_PER_PLAYER = b.comment("Tower creatures alive at once, per participating player.").defineInRange("encounterMobsPerPlayer", -1, -1, 64);
        ENCOUNTER_PER_TOWER = b.comment("Tower creatures alive at once in one tower, however many players.").defineInRange("encounterMobsPerTower", -1, -1, 128);
        ACTIVE_TOWERS = b.comment("Tower floors fighting at once across the whole server.").defineInRange("simultaneousTowerEncounters", -1, -1, 32);
        WAVES_PER_FLOOR = b.comment("Waves on each of the three cage floors (the crown is always one wave).").defineInRange("wavesPerFloor", -1, -1, 10);
        MOBS_PER_WAVE = b.comment("Creatures in one wave before the per-player and per-tower limits apply.").defineInRange("mobsPerWave", -1, -1, 32);
        WAVE_COOLDOWN = b.comment("Minimum ticks between reinforcement waves (20 ticks = 1 second).").defineInRange("waveCooldownTicks", -1, -1, 12000);
        AMBIENT_PER_PLAYER = b.comment("Wild frontier creatures this mod keeps near each player.").defineInRange("ambientMobsPerPlayer", -1, -1, 64);
        AMBIENT_INTERVAL = b.comment("Ticks between wild spawn attempts for each player.").defineInRange("ambientSpawnIntervalTicks", -1, -1, 12000);
        RIVALRY_RADIUS = b.comment("Blocks a predator looks for prey. Searches are boxes of this size, never world scans.").defineInRange("rivalrySearchRadius", -1, -1, 64);
        AI_INTERVAL = b.comment("Ticks between rivalry updates (the only AI this mod adds).").defineInRange("aiUpdateIntervalTicks", -1, -1, 400);
        FIGHTS_PER_PLAYER = b.comment("Predator-versus-prey fights this mod starts near each player at once.").defineInRange("rivalryFightsPerPlayer", -1, -1, 16);
        DROPS_PER_MOB = b.comment("Most item stacks one frontier creature may drop.").defineInRange("maxDropsPerMob", -1, -1, 32);
        PARTICLES = b.comment("Particle multiplier for this mod's effects (0 = none, -1 = preset).").defineInRange("particleDensity", -1.0D, -1.0D, 2.0D);
        b.pop();

        b.push("behaviour");
        PURSUIT_TICKS = b.comment("How long a predator chases its prey before giving up.").defineInRange("pursuitTicks", 200, 20, 2400);
        RIVALRY_COOLDOWN = b.comment("Ticks a predator rests after a fight before it hunts again.").defineInRange("rivalryCooldownTicks", 600, 0, 24000);
        LEASH_RADIUS = b.comment("Blocks a tower creature may stray from its floor before it is called back.").defineInRange("towerLeashRadius", 40, 12, 128);
        DISENGAGE_TICKS = b.comment("Ticks with no player near before an unfinished tower floor resets (creatures are removed, cleared floors stay cleared).")
                .defineInRange("disengageTicks", 400, 100, 24000);
        TOWER_CHANCE = b.comment("Percent of possible tower sites that actually build a tower. Affects newly generated chunks only.")
                .defineInRange("towerChancePercent", 100, 0, 100);
        RETURN_COOLDOWN_SECONDS = b.comment("Cooldown on /frontier return, the recovery route home.").defineInRange("returnCommandCooldownSeconds", 60, 0, 3600);
        b.pop();

        b.comment("Creature rosters. Entries are entity ids, optionally with @N to allow at most N per wave or group.",
                "The first list is used when Antarchy is installed; the fallback list (vanilla stand-ins) when it is not.",
                "Unknown ids are skipped with one warning in the log.").push("rosters");
        FLOOR0 = list(b, "swarmPen", List.of("antarchy:mantis", "antarchy:scorpion"));
        FLOOR0_FALLBACK = list(b, "swarmPenFallback", List.of("minecraft:spider", "minecraft:cave_spider"));
        FLOOR1 = list(b, "hatchery", List.of("antarchy:scorpion", "antarchy:wasp", "antarchy:springbug@1"));
        FLOOR1_FALLBACK = list(b, "hatcheryFallback", List.of("minecraft:cave_spider", "minecraft:spider"));
        FLOOR2 = list(b, "aerie", List.of("antarchy:stratoshark", "antarchy:wasp", "antarchy:brutalfly@1", "minecraft:blaze@1"));
        FLOOR2_FALLBACK = list(b, "aerieFallback", List.of("minecraft:phantom", "minecraft:blaze@1"));
        CROWN = list(b, "crownGuardian", List.of("antarchy:alpha_mantis@1"));
        CROWN_FALLBACK = list(b, "crownGuardianFallback", List.of("minecraft:ravager@1"));
        CROWN_ESCORTS = list(b, "crownEscorts", List.of("antarchy:mantis@2"));
        CROWN_ESCORTS_FALLBACK = list(b, "crownEscortsFallback", List.of("minecraft:spider@2"));
        SWARM = list(b, "wildSwarm", List.of("antarchy:mantis", "antarchy:scorpion"));
        SWARM_FALLBACK = list(b, "wildSwarmFallback", List.of("minecraft:spider"));
        RAPTORS_DAY = list(b, "wildRaptorsDay", List.of("antarchy:stratoshark", "antarchy:brutalfly@1"));
        RAPTORS_DAY_FALLBACK = list(b, "wildRaptorsDayFallback", List.of());
        RAPTORS_NIGHT = list(b, "wildRaptorsNight", List.of("antarchy:nightmare@1", "antarchy:stratoshark"));
        RAPTORS_NIGHT_FALLBACK = list(b, "wildRaptorsNightFallback", List.of("minecraft:phantom"));
        b.pop();

        SPEC = b.build();
    }

    private static ForgeConfigSpec.ConfigValue<List<? extends String>> list(ForgeConfigSpec.Builder b, String name, List<String> def) {
        return b.defineListAllowEmpty(List.of(name), () -> def, o -> o instanceof String s && s.matches("[a-z0-9_.-]+:[a-z0-9_/.-]+(@\\d+)?"));
    }

    private FrontierConfig() {}

    private static int pick(ForgeConfigSpec.IntValue override, int conservative, int standard, int high) {
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
    public static int encounterPerTower() { return pick(ENCOUNTER_PER_TOWER, 10, 16, 28); }
    public static int activeTowers() { return pick(ACTIVE_TOWERS, 2, 3, 6); }
    public static int wavesPerFloor() { return Math.max(1, pick(WAVES_PER_FLOOR, 2, 3, 4)); }
    public static int mobsPerWave() { return Math.max(1, pick(MOBS_PER_WAVE, 3, 5, 8)); }
    public static int waveCooldown() { return pick(WAVE_COOLDOWN, 300, 200, 140); }
    public static int ambientPerPlayer() { return pick(AMBIENT_PER_PLAYER, 5, 9, 16); }
    public static int ambientInterval() { return Math.max(20, pick(AMBIENT_INTERVAL, 400, 240, 140)); }
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
        return "preset=" + PRESET.get() + " encounter/player=" + encounterPerPlayer() + " encounter/tower=" + encounterPerTower()
                + " activeTowers=" + activeTowers() + " waves=" + wavesPerFloor() + " mobs/wave=" + mobsPerWave()
                + " waveCooldown=" + waveCooldown() + " ambient/player=" + ambientPerPlayer() + " ambientInterval=" + ambientInterval()
                + " rivalryRadius=" + rivalryRadius() + " aiInterval=" + aiInterval() + " fights/player=" + fightsPerPlayer()
                + " drops/mob=" + dropsPerMob() + " particles=" + particles();
    }
}
