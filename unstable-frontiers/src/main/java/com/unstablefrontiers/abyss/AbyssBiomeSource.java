package com.unstablefrontiers.abyss;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.stream.Stream;
import net.minecraft.core.Holder;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.BiomeSource;
import net.minecraft.world.level.biome.Climate;

/**
 * Three regions: the Starlit Shoals everywhere by default, the Shattered Reach around the drifting archive and in broad
 * western bands, and the Eclipse Hollow around the Hollow Crown and in patches to the south. Fixed by position, like the
 * terrain.
 */
public class AbyssBiomeSource extends BiomeSource {
    public static final MapCodec<AbyssBiomeSource> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            Biome.CODEC.fieldOf("shoals").forGetter(s -> s.shoals),
            Biome.CODEC.fieldOf("reach").forGetter(s -> s.reach),
            Biome.CODEC.fieldOf("hollow").forGetter(s -> s.hollow)).apply(i, AbyssBiomeSource::new));
    private final Holder<Biome> shoals, reach, hollow;

    public AbyssBiomeSource(Holder<Biome> shoals, Holder<Biome> reach, Holder<Biome> hollow) {
        this.shoals = shoals;
        this.reach = reach;
        this.hollow = hollow;
    }

    @Override
    protected MapCodec<? extends BiomeSource> codec() {
        return CODEC;
    }

    @Override
    protected Stream<Holder<Biome>> collectPossibleBiomes() {
        return Stream.of(shoals, reach, hollow);
    }

    @Override
    public Holder<Biome> getNoiseBiome(int qx, int qy, int qz, Climate.Sampler sampler) {
        return switch (region(qx << 2, qz << 2)) {
            case 1 -> reach;
            case 2 -> hollow;
            default -> shoals;
        };
    }

    /** 0 shoals, 1 reach, 2 hollow. */
    public static int region(int x, int z) {
        AbyssTerrain.Anchor crown = AbyssTerrain.HOLLOW_CROWN;
        if (Math.hypot(x - crown.x(), z - crown.z()) < crown.radius() + 90) {
            return 2;
        }
        AbyssTerrain.Anchor archive = AbyssTerrain.ARCHIVE;
        if (Math.hypot(x - archive.x(), z - archive.z()) < archive.radius() + 70) {
            return 1;
        }
        double v = AbyssTerrain.fbm(x / 260.0, z / 260.0, 301, 2);
        if (v > 0.64) {
            return 1;
        }
        return v < 0.33 && z > 150 ? 2 : 0;
    }
}
