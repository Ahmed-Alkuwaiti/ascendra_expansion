package com.unstablefrontiers.world;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.FeatureConfiguration;

/**
 * The frontier's own terrain details, one feature with four shapes (configured in worldgen/configured_feature):
 * <ul>
 * <li>talon_spire: a tapering rock needle that hooks over at the top like a claw (Talon Spires).</li>
 * <li>islet: a floating clump of rock and soil 24-40 blocks above the ground, roots trailing (Talon Spires).</li>
 * <li>rib_arch: a bleached rib arching out of the ground (Rustbone Scar).</li>
 * <li>scar_ground: a patch of red, bone-strewn ground (Rustbone Scar).</li>
 * </ul>
 * Each stays within the chunk it is placed in plus its neighbours, as features must.
 */
public class TerrainFeature extends Feature<TerrainFeature.Config> {
    public enum Shape implements StringRepresentable {
        TALON_SPIRE, ISLET, RIB_ARCH, SCAR_GROUND;

        @Override
        public String getSerializedName() {
            return name().toLowerCase();
        }
    }

    public record Config(Shape shape) implements FeatureConfiguration {
        public static final Codec<Config> CODEC = StringRepresentable.fromEnum(Shape::values).fieldOf("shape").codec()
                .xmap(Config::new, Config::shape);
    }

    public TerrainFeature() {
        super(Config.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<Config> ctx) {
        WorldGenLevel level = ctx.level();
        RandomSource r = ctx.random();
        BlockPos o = ctx.origin();
        int y = level.getHeight(Heightmap.Types.WORLD_SURFACE_WG, o.getX(), o.getZ());
        BlockPos base = new BlockPos(o.getX(), y, o.getZ());
        if (!level.getBlockState(base.below()).getFluidState().isEmpty()) {
            return false;
        }
        return switch (ctx.config().shape()) {
            case TALON_SPIRE -> spire(level, r, base);
            case ISLET -> islet(level, r, base.above(24 + r.nextInt(17)));
            case RIB_ARCH -> rib(level, r, base);
            case SCAR_GROUND -> scar(level, r, base);
        };
    }

    private static BlockState rock(RandomSource r) {
        int k = r.nextInt(10);
        return k < 5 ? Blocks.TUFF.defaultBlockState() : k < 8 ? Blocks.CALCITE.defaultBlockState() : Blocks.COBBLED_DEEPSLATE.defaultBlockState();
    }

    private boolean spire(WorldGenLevel level, RandomSource r, BlockPos base) {
        int h = 18 + r.nextInt(16);
        double r0 = 2.6D + r.nextDouble() * 1.2D;
        double dx = r.nextBoolean() ? 1 : -1, dz = r.nextBoolean() ? 1 : -1;
        for (int i = -3; i < h; i++) {
            double t = Math.max(0, i) / (double) h;
            double rad = r0 * (1 - t) + 0.5D;
            // the hook: the top third leans further and further over
            double lean = t > 0.66D ? Math.pow((t - 0.66D) / 0.34D, 2) * 4.0D : 0;
            double cx = base.getX() + dx * lean, cz = base.getZ() + dz * lean;
            int ir = (int) Math.ceil(rad);
            for (int x = -ir; x <= ir; x++) {
                for (int z = -ir; z <= ir; z++) {
                    if (x * x + z * z <= rad * rad) {
                        setBlock(level, BlockPos.containing(cx + x, base.getY() + i, cz + z), rock(r));
                    }
                }
            }
        }
        return true;
    }

    private boolean islet(WorldGenLevel level, RandomSource r, BlockPos c) {
        double rx = 3.5D + r.nextDouble() * 2.5D, rz = 3.0D + r.nextDouble() * 2.5D;
        int depth = 4 + r.nextInt(4);
        for (int x = (int) -rx; x <= rx; x++) {
            for (int z = (int) -rz; z <= rz; z++) {
                double e = (x * x) / (rx * rx) + (z * z) / (rz * rz);
                if (e > 1) {
                    continue;
                }
                int d = (int) Math.round(depth * (1 - e)) + 1;
                for (int k = 0; k < d; k++) {
                    BlockState s = k == 0 ? Blocks.GRASS_BLOCK.defaultBlockState() : k < 3 ? Blocks.DIRT.defaultBlockState() : rock(r);
                    setBlock(level, c.offset(x, -k, z), s);
                }
                if (e < 0.35D && r.nextInt(5) == 0) {
                    for (int k = d; k < d + 2 + r.nextInt(5); k++) {
                        setBlock(level, c.offset(x, -k, z), Blocks.HANGING_ROOTS.defaultBlockState());
                    }
                }
            }
        }
        return true;
    }

    private boolean rib(WorldGenLevel level, RandomSource r, BlockPos base) {
        int span = 7 + r.nextInt(6);
        int height = 6 + r.nextInt(5);
        boolean alongX = r.nextBoolean();
        for (int i = 0; i <= span * 4; i++) {
            double t = i / (double) (span * 4);
            int along = (int) Math.round((t - 0.5D) * span * 2);
            int up = (int) Math.round(Math.sin(Math.PI * t) * height);
            int lean = (int) Math.round(Math.sin(Math.PI * t) * 2);
            BlockPos p = alongX ? base.offset(along, up - 1, lean) : base.offset(lean, up - 1, along);
            setBlock(level, p, Blocks.BONE_BLOCK.defaultBlockState());
            if (up < height / 2) {
                setBlock(level, p.above(), Blocks.BONE_BLOCK.defaultBlockState());
            }
        }
        return true;
    }

    private boolean scar(WorldGenLevel level, RandomSource r, BlockPos base) {
        int rad = 4 + r.nextInt(4);
        for (int x = -rad; x <= rad; x++) {
            for (int z = -rad; z <= rad; z++) {
                if (x * x + z * z > rad * rad || r.nextInt(6) == 0) {
                    continue;
                }
                int y = level.getHeight(Heightmap.Types.WORLD_SURFACE_WG, base.getX() + x, base.getZ() + z) - 1;
                BlockPos p = new BlockPos(base.getX() + x, y, base.getZ() + z);
                BlockState top = level.getBlockState(p);
                if (!top.is(Blocks.GRASS_BLOCK) && !top.is(Blocks.DIRT) && !top.is(Blocks.PODZOL) && !top.is(Blocks.STONE)
                        && !top.is(Blocks.COARSE_DIRT)) {
                    continue;
                }
                int k = r.nextInt(10);
                setBlock(level, p, k < 5 ? Blocks.RED_TERRACOTTA.defaultBlockState() : k < 8 ? Blocks.COARSE_DIRT.defaultBlockState()
                        : Blocks.TERRACOTTA.defaultBlockState());
                if (r.nextInt(40) == 0) {
                    setBlock(level, p.above(), Blocks.BONE_BLOCK.defaultBlockState());
                }
            }
        }
        return true;
    }
}
