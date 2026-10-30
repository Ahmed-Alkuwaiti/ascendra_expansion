package com.unstablefrontiers.drowned;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.stream.Stream;
import net.minecraft.core.Holder;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.BiomeSource;
import net.minecraft.world.level.biome.Climate;

/** Four regions by the floor's depth (see {@link DrownedTerrain#region}): shallows, kelpwood, the reach and the trench. */
public class DrownedBiomeSource extends BiomeSource {
    public static final MapCodec<DrownedBiomeSource> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            Biome.CODEC.fieldOf("shallows").forGetter(s -> s.shallows),
            Biome.CODEC.fieldOf("kelpwood").forGetter(s -> s.kelpwood),
            Biome.CODEC.fieldOf("reach").forGetter(s -> s.reach),
            Biome.CODEC.fieldOf("trench").forGetter(s -> s.trench)).apply(i, DrownedBiomeSource::new));
    private final Holder<Biome> shallows, kelpwood, reach, trench;

    public DrownedBiomeSource(Holder<Biome> shallows, Holder<Biome> kelpwood, Holder<Biome> reach, Holder<Biome> trench) {
        this.shallows = shallows;
        this.kelpwood = kelpwood;
        this.reach = reach;
        this.trench = trench;
    }

    @Override
    protected MapCodec<? extends BiomeSource> codec() {
        return CODEC;
    }

    @Override
    protected Stream<Holder<Biome>> collectPossibleBiomes() {
        return Stream.of(shallows, kelpwood, reach, trench);
    }

    @Override
    public Holder<Biome> getNoiseBiome(int qx, int qy, int qz, Climate.Sampler sampler) {
        int x = qx << 2, z = qz << 2;
        return switch (DrownedTerrain.region(x, z, DrownedTerrain.floor(x, z))) {
            case DrownedTerrain.SHALLOWS -> shallows;
            case DrownedTerrain.KELPWOOD -> kelpwood;
            case DrownedTerrain.REACH -> reach;
            default -> trench;
        };
    }
}
