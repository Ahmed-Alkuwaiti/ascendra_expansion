package com.unstablefrontiers.drowned;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.unstablefrontiers.registry.DrownedRegistry;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.world.level.LevelHeightAccessor;
import net.minecraft.world.level.NoiseColumn;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.biome.BiomeManager;
import net.minecraft.world.level.biome.BiomeSource;
import net.minecraft.world.level.block.BaseCoralWallFanBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.KelpBlock;
import net.minecraft.world.level.block.SeaPickleBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.chunk.LevelChunkSection;
import net.minecraft.world.level.levelgen.GenerationStep;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.blending.Blender;

/**
 * Builds the Drowned Expanse from {@link DrownedTerrain}: rock to the floor, water to the surface, air above. The floor is
 * dressed by region: coral reefs, sand and sea pickles in the shallows; kelp forests over clay and gravel in the Kelpwood;
 * brine slate, seagrass and lumen coral in the Reach; basalt, brine slate and bioluminescent coral down the trench. Caves
 * are carved water. Breath vents and the surveyors' glyph posts are placed from the terrain's lists. Seedless, like the
 * Astral Abyss: the same in every world.
 */
public class DrownedChunkGenerator extends ChunkGenerator {
    public static final MapCodec<DrownedChunkGenerator> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            BiomeSource.CODEC.fieldOf("biome_source").forGetter(g -> g.biomeSource)).apply(i, DrownedChunkGenerator::new));
    private static final Block[] CORAL_BLOCKS = {Blocks.TUBE_CORAL_BLOCK, Blocks.BRAIN_CORAL_BLOCK, Blocks.BUBBLE_CORAL_BLOCK,
            Blocks.FIRE_CORAL_BLOCK, Blocks.HORN_CORAL_BLOCK};
    private static final Block[] CORALS = {Blocks.TUBE_CORAL, Blocks.BRAIN_CORAL, Blocks.BUBBLE_CORAL, Blocks.FIRE_CORAL, Blocks.HORN_CORAL,
            Blocks.TUBE_CORAL_FAN, Blocks.BRAIN_CORAL_FAN, Blocks.BUBBLE_CORAL_FAN, Blocks.FIRE_CORAL_FAN, Blocks.HORN_CORAL_FAN};

    public DrownedChunkGenerator(BiomeSource biomeSource) {
        super(biomeSource);
    }

    @Override
    protected MapCodec<? extends ChunkGenerator> codec() {
        return CODEC;
    }

    @Override
    public CompletableFuture<ChunkAccess> fillFromNoise(Blender blender, RandomState randomState, StructureManager structures, ChunkAccess chunk) {
        BlockState water = Blocks.WATER.defaultBlockState();
        BlockState stone = Blocks.STONE.defaultBlockState();
        BlockState deepslate = Blocks.DEEPSLATE.defaultBlockState();
        BlockState slate = DrownedRegistry.BRINE_SLATE.get().defaultBlockState();
        BlockState bricks = DrownedRegistry.BRINE_BRICKS.get().defaultBlockState();
        BlockState glyph = DrownedRegistry.TIDE_GLYPH.get().defaultBlockState();
        BlockState vent = DrownedRegistry.BREATH_VENT.get().defaultBlockState();
        BlockState lumen = DrownedRegistry.LUMEN_CORAL.get().defaultBlockState();
        Heightmap ocean = chunk.getOrCreateHeightmapUnprimed(Heightmap.Types.OCEAN_FLOOR_WG);
        Heightmap surface = chunk.getOrCreateHeightmapUnprimed(Heightmap.Types.WORLD_SURFACE_WG);
        int x0 = chunk.getPos().getMinBlockX(), z0 = chunk.getPos().getMinBlockZ();
        LevelChunkSection[] sections = chunk.getSections();
        for (LevelChunkSection s : sections) {
            s.acquire();
        }
        try {
            for (int lx = 0; lx < 16; lx++) {
                for (int lz = 0; lz < 16; lz++) {
                    int x = x0 + lx, z = z0 + lz;
                    int floor = DrownedTerrain.floor(x, z);
                    int region = DrownedTerrain.region(x, z, floor);
                    set(chunk, sections, lx, 0, lz, Blocks.BEDROCK.defaultBlockState(), ocean, surface);
                    for (int y = 1; y <= DrownedTerrain.SURFACE; y++) {
                        BlockState st;
                        if (y <= floor) {
                            if (DrownedTerrain.cave(x, y, z, floor)) {
                                st = water;
                            } else {
                                st = rock(region, x, y, z, floor, stone, deepslate, slate);
                            }
                        } else {
                            st = water;
                        }
                        set(chunk, sections, lx, y, lz, st, ocean, surface);
                    }
                    dress(chunk, sections, lx, lz, x, z, floor, region, lumen, ocean, surface);
                    if (DrownedTerrain.isVent(x, z)) {
                        set(chunk, sections, lx, floor, lz, vent, ocean, surface);
                    }
                }
            }
            // glyph posts: two courses of bricks with the glyph on top
            for (int[] p : DrownedTerrain.postsNear(chunk.getPos().x, chunk.getPos().z)) {
                int lx = p[0] - x0, lz = p[1] - z0;
                int f = DrownedTerrain.floor(p[0], p[1]);
                set(chunk, sections, lx, f + 1, lz, bricks, ocean, surface);
                set(chunk, sections, lx, f + 2, lz, bricks, ocean, surface);
                set(chunk, sections, lx, f + 3, lz, glyph, ocean, surface);
            }
        } finally {
            for (LevelChunkSection s : sections) {
                s.release();
            }
        }
        return CompletableFuture.completedFuture(chunk);
    }

    private static BlockState rock(int region, int x, int y, int z, int floor, BlockState stone, BlockState deepslate, BlockState slate) {
        int depth = floor - y;
        double h = DrownedTerrain.rnd(x, y, z, 21);
        return switch (region) {
            case DrownedTerrain.SHALLOWS -> depth == 0 ? (h < 0.08 ? Blocks.GRAVEL.defaultBlockState() : Blocks.SAND.defaultBlockState())
                    : depth < 4 ? Blocks.SANDSTONE.defaultBlockState() : stone;
            case DrownedTerrain.KELPWOOD -> depth == 0 ? (h < 0.45 ? Blocks.CLAY.defaultBlockState() : h < 0.8 ? Blocks.GRAVEL.defaultBlockState()
                    : Blocks.SAND.defaultBlockState()) : depth < 3 ? Blocks.GRAVEL.defaultBlockState() : stone;
            case DrownedTerrain.REACH -> depth == 0 ? (h < 0.5 ? slate : Blocks.GRAVEL.defaultBlockState())
                    : depth < 3 ? slate : y < 120 ? deepslate : stone;
            default -> depth == 0 ? (h < 0.4 ? slate : h < 0.7 ? Blocks.BASALT.defaultBlockState() : Blocks.SMOOTH_BASALT.defaultBlockState())
                    : h < 0.25 ? slate : deepslate;
        };
    }

    /** Life on the floor: reefs, kelp, seagrass, pickles, lumen coral. Nothing on the places' pads. */
    private static void dress(ChunkAccess chunk, LevelChunkSection[] sections, int lx, int lz, int x, int z, int floor, int region,
                              BlockState lumen, Heightmap a, Heightmap b) {
        for (DrownedTerrain.Anchor an : DrownedTerrain.ANCHORS) {
            if (Math.hypot(x - an.x(), z - an.z()) < an.radius() + 3) {
                return;
            }
        }
        double r = DrownedTerrain.rnd(x, floor, z, 31);
        int y = floor + 1;
        switch (region) {
            case DrownedTerrain.SHALLOWS -> {
                double reef = DrownedTerrain.fbm(x / 18.0, z / 18.0, 33, 2);
                if (reef > 0.58) {
                    int hgt = 1 + (int) ((reef - 0.58) * 14);
                    Block cb = CORAL_BLOCKS[(int) (DrownedTerrain.fbm(x / 9.0, z / 9.0, 35, 1) * 5) % 5];
                    for (int k = 0; k < hgt; k++) {
                        set(chunk, sections, lx, y + k, lz, cb.defaultBlockState(), a, b);
                    }
                    if (r < 0.5) {
                        set(chunk, sections, lx, y + hgt, lz, CORALS[(int) (r * 20) % CORALS.length].defaultBlockState(), a, b);
                    } else if (r < 0.56) {
                        set(chunk, sections, lx, y + hgt, lz, lumen, a, b);
                    }
                } else if (r < 0.03) {
                    set(chunk, sections, lx, y, lz, Blocks.SEA_PICKLE.defaultBlockState().setValue(SeaPickleBlock.PICKLES, 1 + (int) (r * 100) % 4), a, b);
                } else if (r < 0.25) {
                    set(chunk, sections, lx, y, lz, Blocks.SEAGRASS.defaultBlockState(), a, b);
                } else if (r < 0.32) {
                    kelp(chunk, sections, lx, lz, y, 4 + (int) (r * 40) % 8, a, b);
                }
            }
            case DrownedTerrain.KELPWOOD -> {
                double forest = DrownedTerrain.fbm(x / 30.0, z / 30.0, 37, 2);
                if (forest > 0.42 && r < 0.42) {
                    kelp(chunk, sections, lx, lz, y, 12 + (int) (DrownedTerrain.rnd(x, 1, z, 39) * 24), a, b);
                } else if (r < 0.62) {
                    set(chunk, sections, lx, y, lz, r < 0.5 ? Blocks.SEAGRASS.defaultBlockState() : Blocks.TALL_SEAGRASS.defaultBlockState(), a, b);
                    if (r >= 0.5) {
                        set(chunk, sections, lx, y + 1, lz, Blocks.TALL_SEAGRASS.defaultBlockState()
                                .setValue(net.minecraft.world.level.block.TallSeagrassBlock.HALF, net.minecraft.world.level.block.state.properties.DoubleBlockHalf.UPPER), a, b);
                    }
                } else if (r < 0.64) {
                    set(chunk, sections, lx, y, lz, Blocks.SEA_PICKLE.defaultBlockState().setValue(SeaPickleBlock.PICKLES, 3), a, b);
                }
            }
            case DrownedTerrain.REACH -> {
                if (r < 0.012) {
                    set(chunk, sections, lx, floor, lz, lumen, a, b);
                } else if (r < 0.14) {
                    set(chunk, sections, lx, y, lz, Blocks.SEAGRASS.defaultBlockState(), a, b);
                } else if (r < 0.15) {
                    set(chunk, sections, lx, y, lz, Blocks.SEA_PICKLE.defaultBlockState().setValue(SeaPickleBlock.PICKLES, 4), a, b);
                } else if (r < 0.19 && DrownedTerrain.fbm(x / 22.0, z / 22.0, 41, 1) > 0.6) {
                    kelp(chunk, sections, lx, lz, y, 6 + (int) (r * 100) % 10, a, b);
                }
            }
            default -> {
                // the trench: little grows, but what does glows
                if (r < 0.05) {
                    int hgt = 1 + (int) (r * 60);
                    for (int k = 0; k < hgt; k++) {
                        set(chunk, sections, lx, y + k, lz, lumen, a, b);
                    }
                } else if (r < 0.09) {
                    set(chunk, sections, lx, y, lz, Blocks.SEA_PICKLE.defaultBlockState().setValue(SeaPickleBlock.PICKLES, 4), a, b);
                }
            }
        }
    }

    private static void kelp(ChunkAccess chunk, LevelChunkSection[] sections, int lx, int lz, int y, int height, Heightmap a, Heightmap b) {
        int top = Math.min(y + height, DrownedTerrain.SURFACE - 2);
        for (int k = y; k < top; k++) {
            set(chunk, sections, lx, k, lz, Blocks.KELP_PLANT.defaultBlockState(), a, b);
        }
        set(chunk, sections, lx, top, lz, Blocks.KELP.defaultBlockState().setValue(KelpBlock.AGE, 25), a, b);
    }

    private static void set(ChunkAccess chunk, LevelChunkSection[] sections, int lx, int y, int lz, BlockState st, Heightmap a, Heightmap b) {
        int idx = chunk.getSectionIndex(y);
        if (idx < 0 || idx >= sections.length) {
            return;
        }
        sections[idx].setBlockState(lx, y & 15, lz, st, false);
        a.update(lx, y, lz, st);
        b.update(lx, y, lz, st);
    }

    @Override
    public void buildSurface(WorldGenRegion region, StructureManager structures, RandomState randomState, ChunkAccess chunk) {
    }

    @Override
    public void applyCarvers(WorldGenRegion region, long seed, RandomState randomState, BiomeManager biomes, StructureManager structures,
                             ChunkAccess chunk, GenerationStep.Carving step) {
    }

    @Override
    public void spawnOriginalMobs(WorldGenRegion region) {
    }

    @Override
    public int getGenDepth() {
        return DrownedTerrain.HEIGHT;
    }

    @Override
    public int getSeaLevel() {
        return DrownedTerrain.SURFACE + 1;
    }

    @Override
    public int getMinY() {
        return DrownedTerrain.MIN_Y;
    }

    @Override
    public int getBaseHeight(int x, int z, Heightmap.Types type, LevelHeightAccessor level, RandomState randomState) {
        return type.isOpaque().test(Blocks.WATER.defaultBlockState()) ? DrownedTerrain.SURFACE + 1 : DrownedTerrain.floor(x, z) + 1;
    }

    @Override
    public NoiseColumn getBaseColumn(int x, int z, LevelHeightAccessor level, RandomState randomState) {
        BlockState[] states = new BlockState[level.getHeight()];
        int floor = DrownedTerrain.floor(x, z);
        for (int i = 0; i < states.length; i++) {
            int y = level.getMinBuildHeight() + i;
            states[i] = y <= floor ? Blocks.STONE.defaultBlockState() : y <= DrownedTerrain.SURFACE ? Blocks.WATER.defaultBlockState() : Blocks.AIR.defaultBlockState();
        }
        return new NoiseColumn(level.getMinBuildHeight(), states);
    }

    @Override
    public void addDebugScreenInfo(List<String> info, RandomState randomState, BlockPos pos) {
        info.add("Drowned Expanse, floor " + DrownedTerrain.floor(pos.getX(), pos.getZ()) + ", nearest " + DrownedTerrain.nearest(pos.getX(), pos.getZ()).name());
    }
}
