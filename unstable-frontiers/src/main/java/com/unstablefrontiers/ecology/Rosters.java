package com.unstablefrontiers.ecology;

import static com.unstablefrontiers.config.FrontierConfig.*;

import java.util.List;

/** The rosters for each tower stage and the wild, read from the config every time (they are a handful of entries). */
public final class Rosters {
    private Rosters() {}

    public static List<Creatures.Entry> stage(int stage) {
        return switch (stage) {
            case 0 -> Creatures.roster(FLOOR0::get, FLOOR0_FALLBACK::get);
            case 1 -> Creatures.roster(FLOOR1::get, FLOOR1_FALLBACK::get);
            case 2 -> Creatures.roster(FLOOR2::get, FLOOR2_FALLBACK::get);
            default -> Creatures.roster(CROWN::get, CROWN_FALLBACK::get);
        };
    }

    public static List<Creatures.Entry> crownEscorts() {
        return Creatures.roster(CROWN_ESCORTS::get, CROWN_ESCORTS_FALLBACK::get);
    }

    public static List<Creatures.Entry> swarm() {
        return Creatures.roster(SWARM::get, SWARM_FALLBACK::get);
    }

    public static List<Creatures.Entry> raptors(boolean night) {
        return night ? Creatures.roster(RAPTORS_NIGHT::get, RAPTORS_NIGHT_FALLBACK::get)
                : Creatures.roster(RAPTORS_DAY::get, RAPTORS_DAY_FALLBACK::get);
    }
}
