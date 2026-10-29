package com.unstablefrontiers.abyss;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.unstablefrontiers.registry.AbyssRegistry;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.world.level.LevelHeightAccessor;
import net.minecraft.world.level.NoiseColumn;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.biome.BiomeManager;
import net.minecraft.world.level.biome.BiomeSource;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.chunk.LevelChunkSection;
import net.minecraft.world.level.levelgen.GenerationStep;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.blending.Blender;

/**
 * Builds the Astral Abyss from {@link AbyssTerrain}: island spans of astral shale with starmoss tops, ore and lumen veins
 * inside, starbloom on top and void tendrils hanging underneath, all chosen by position hashes so a chunk always comes
 * out the same. No caves, carvers or noise router: nothing here depends on the world seed.
 */
public class AbyssChunkGenerator extends ChunkGenerator {
    public static final MapCodec<AbyssChunkGenerator> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            BiomeSource.CODEC.fieldOf("biome_source").forGetter(g -> g.biomeSource)).apply(i, AbyssChunkGenerator::new));
    private static final int MIN_Y = 0;
    private static final int HEIGHT = 256;

    public AbyssChunkGenerator(BiomeSource biomeSource) {
        super(biomeSource);
    }

    @Override
    protected MapCodec<? extends ChunkGenerator> codec() {
        return CODEC;
    }

    static double hash(int x, int y, int z, long salt) {
        return AbyssTerrain.rnd(x * 31L + y, z * 17L - y, salt);
    }

    @Override
    public CompletableFuture<ChunkAccess> fillFromNoise(Blender blender, RandomState randomState, StructureManager structures, ChunkAccess chunk) {
        BlockState shale = AbyssRegistry.ASTRAL_SHALE.get().defaultBlockState();
        BlockState moss = AbyssRegistry.STARMOSS.get().defaultBlockState();
        BlockState bricks = AbyssRegistry.ASTRAL_BRICKS.get().defaultBlockState();
        BlockState ore = AbyssRegistry.ASTRAL_ORE.get().defaultBlockState();
        BlockState lumen = AbyssRegistry.LUMEN_CRYSTAL.get().defaultBlockState();
        BlockState bloom = AbyssRegistry.STARBLOOM.get().defaultBlockState();
        BlockState tendril = AbyssRegistry.VOID_TENDRIL.get().defaultBlockState();
        Heightmap ocean = chunk.getOrCreateHeightmapUnprimed(Heightmap.Types.OCEAN_FLOOR_WG);
        Heightmap surface = chunk.getOrCreateHeightmapUnprimed(Heightmap.Types.WORLD_SURFACE_WG);
        int x0 = chunk.getPos().getMinBlockX(), z0 = chunk.getPos().getMinBlockZ();
        List<AbyssTerrain.Stone> stones = AbyssTerrain.stonesNear(chunk.getPos().x, chunk.getPos().z);
        LevelChunkSection[] sections = chunk.getSections();
        for (LevelChunkSection s : sections) {
            s.acquire();
        }
        try {
            for (int lx = 0; lx < 16; lx++) {
                for (int lz = 0; lz < 16; lz++) {
                    int x = x0 + lx, z = z0 + lz;
                    List<int[]> spans = AbyssTerrain.column(x, z, stones);
                    for (int[] sp : spans) {
                        int top = Math.min(HEIGHT - 2, sp[0]), bottom = Math.max(MIN_Y + 1, sp[1]);
                        boolean stone = top - bottom <= 1 && AbyssTerrain.anchorProfile(x, z) == null && isStone(x, z, top, stones);
                        for (int y = bottom; y <= top; y++) {
                            BlockState st;
                            if (stone) {
                                st = bricks;
                            } else if (y == top) {
                                st = moss;
                            } else if (y < top - 3 && hash(x, y, z, 5) < 0.012) {
                                st = ore;
                            } else if (y < top - 2 && hash(x, y, z, 6) < 0.004) {
                                st = lumen;
                            } else {
                                st = shale;
                            }
                            set(chunk, sections, lx, y, lz, st, ocean, surface);
                        }
                        if (stone || top + 1 >= HEIGHT) {
                            continue;
                        }
                        double r = hash(x, top, z, 7);
                        if (r < 0.06) {
                            set(chunk, sections, lx, top + 1, lz, bloom, ocean, surface);
                        } else if (r < 0.068) {
                            set(chunk, sections, lx, top + 1, lz, lumen, ocean, surface);
                        }
                        // tendrils hang from the undersides of thicker islands
                        if (top - bottom > 4 && hash(x, bottom, z, 8) < 0.09) {
                            int len = 1 + (int) (hash(x, bottom, z, 9) * 5);
                            for (int k = 1; k <= len && bottom - k > MIN_Y; k++) {
                                set(chunk, sections, lx, bottom - k, lz, tendril, ocean, surface);
                            }
                        }
                    }
                }
            }
        } finally {
            for (LevelChunkSection s : sections) {
                s.release();
            }
        }
        return CompletableFuture.completedFuture(chunk);
    }

    private static boolean isStone(int x, int z, int top, List<AbyssTerrain.Stone> stones) {
        return AbyssTerrain.stoneAt(x, z, stones) == top;
    }

    private static void set(ChunkAccess chunk, LevelChunkSection[] sections, int lx, int y, int lz, BlockState st, Heightmap a, Heightmap b) {
        int idx = chunk.getSectionIndex(y);
        if (idx < 0 || idx >= sections.length) {
            return;
        }
        LevelChunkSection sec = sections[idx];
        if (!sec.getBlockState(lx, y & 15, lz).isAir() && st.is(AbyssRegistry.VOID_TENDRIL.get())) {
            return;   // a tendril never replaces rock
        }
        sec.setBlockState(lx, y & 15, lz, st, false);
        a.update(lx, y, lz, st);
        b.update(lx, y, lz, st);
    }

    @Override
    public void buildSurface(WorldGenRegion region, StructureManager structures, RandomState randomState, ChunkAccess chunk) {
        // the surface is laid by fillFromNoise
    }

    @Override
    public void applyCarvers(WorldGenRegion region, long seed, RandomState randomState, BiomeManager biomes, StructureManager structures,
                             ChunkAccess chunk, GenerationStep.Carving step) {
        // no caves
    }

    @Override
    public void spawnOriginalMobs(WorldGenRegion region) {
    }

    @Override
    public int getGenDepth() {
        return HEIGHT;
    }

    @Override
    public int getSeaLevel() {
        return MIN_Y - 1;
    }

    @Override
    public int getMinY() {
        return MIN_Y;
    }

    @Override
    public int getBaseHeight(int x, int z, Heightmap.Types type, LevelHeightAccessor level, RandomState randomState) {
        List<int[]> spans = AbyssTerrain.column(x, z, AbyssTerrain.stonesNear(x >> 4, z >> 4));
        return spans.isEmpty() ? level.getMinBuildHeight() : spans.get(0)[0] + 1;
    }

    @Override
    public NoiseColumn getBaseColumn(int x, int z, LevelHeightAccessor level, RandomState randomState) {
        BlockState[] states = new BlockState[level.getHeight()];
        java.util.Arrays.fill(states, Blocks.AIR.defaultBlockState());
        BlockState shale = AbyssRegistry.ASTRAL_SHALE.get().defaultBlockState();
        for (int[] sp : AbyssTerrain.column(x, z, AbyssTerrain.stonesNear(x >> 4, z >> 4))) {
            for (int y = Math.max(level.getMinBuildHeight(), sp[1]); y <= sp[0] && y < level.getMaxBuildHeight(); y++) {
                states[y - level.getMinBuildHeight()] = shale;
            }
        }
        return new NoiseColumn(level.getMinBuildHeight(), states);
    }

    @Override
    public void addDebugScreenInfo(List<String> info, RandomState randomState, BlockPos pos) {
        AbyssTerrain.Anchor a = AbyssTerrain.clearSky(pos.getX(), pos.getZ());
        info.add("Astral Abyss" + (a == null ? "" : " near " + a.name()));
    }
}
