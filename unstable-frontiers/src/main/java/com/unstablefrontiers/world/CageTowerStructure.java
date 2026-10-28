package com.unstablefrontiers.world;

import com.mojang.serialization.MapCodec;
import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.registry.ModStructures;
import java.util.Arrays;
import java.util.Optional;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;

/**
 * Picks a site for a cage tower: the middle of the chunk the structure set chose, at the median ground height of five
 * samples (centre and corners). Spacing and separation come from the structure set, which keeps towers apart; the config
 * can thin them further. Each site samples the height map five times and nothing else.
 */
public class CageTowerStructure extends Structure {
    public static final MapCodec<CageTowerStructure> CODEC = simpleCodec(CageTowerStructure::new);

    public CageTowerStructure(Structure.StructureSettings settings) {
        super(settings);
    }

    @Override
    protected Optional<Structure.GenerationStub> findGenerationPoint(Structure.GenerationContext ctx) {
        if (ctx.random().nextInt(100) >= FrontierConfig.TOWER_CHANCE.get()) {
            return Optional.empty();
        }
        ChunkPos chunk = ctx.chunkPos();
        int x0 = chunk.getMiddleBlockX() - TowerBlueprint.C;
        int z0 = chunk.getMiddleBlockZ() - TowerBlueprint.C;
        int last = TowerBlueprint.SIZE - 1;
        int[] ys = {
                height(ctx, x0 + TowerBlueprint.C, z0 + TowerBlueprint.C), height(ctx, x0, z0), height(ctx, x0 + last, z0),
                height(ctx, x0, z0 + last), height(ctx, x0 + last, z0 + last)};
        Arrays.sort(ys);
        int base = ys[2];
        int min = ctx.heightAccessor().getMinBuildHeight() + 8;
        int max = ctx.heightAccessor().getMaxBuildHeight() - TowerBlueprint.TOP - 4;
        if (base < min || base > max) {
            return Optional.empty();
        }
        int floor = ctx.chunkGenerator().getBaseHeight(x0 + TowerBlueprint.C, z0 + TowerBlueprint.C, Heightmap.Types.OCEAN_FLOOR_WG,
                ctx.heightAccessor(), ctx.randomState());
        if (base - floor > 24) {
            return Optional.empty(); // deep water: the foundation would not reach the bottom
        }
        int variant = ctx.random().nextInt();
        BlockPos at = new BlockPos(x0 + TowerBlueprint.C, base, z0 + TowerBlueprint.C);
        return Optional.of(new Structure.GenerationStub(at, builder -> builder.addPiece(new CageTowerPiece(x0, base, z0, variant))));
    }

    private static int height(Structure.GenerationContext ctx, int x, int z) {
        return ctx.chunkGenerator().getBaseHeight(x, z, Heightmap.Types.WORLD_SURFACE_WG, ctx.heightAccessor(), ctx.randomState());
    }

    @Override
    public StructureType<?> type() {
        return ModStructures.CAGE_TOWER_TYPE.get();
    }
}
