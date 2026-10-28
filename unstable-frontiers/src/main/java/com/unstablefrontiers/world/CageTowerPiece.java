package com.unstablefrontiers.world;

import com.unstablefrontiers.registry.ModStructures;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.RandomizableContainer;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;
import net.minecraft.world.level.storage.loot.LootTable;

/**
 * One cage tower. Built column by column from {@link TowerBlueprint}, clipped to the chunk being generated, so a tower
 * costs nothing beyond the chunks it stands in. The origin and base height are saved with the piece; the encounter system
 * reads them back from the structure start.
 */
public class CageTowerPiece extends StructurePiece {
    private static final int FOUNDATION_DEPTH = 40;
    private final int originX;
    private final int baseY;
    private final int originZ;
    private final int variant;

    public CageTowerPiece(int originX, int baseY, int originZ, int variant) {
        super(ModStructures.CAGE_TOWER_PIECE.get(), 0, box(originX, baseY, originZ));
        this.originX = originX;
        this.baseY = baseY;
        this.originZ = originZ;
        this.variant = variant;
        this.setOrientation(null);
    }

    public CageTowerPiece(CompoundTag tag) {
        super(ModStructures.CAGE_TOWER_PIECE.get(), tag);
        this.originX = tag.getInt("OX");
        this.baseY = tag.getInt("BY");
        this.originZ = tag.getInt("OZ");
        this.variant = tag.getInt("V");
    }

    private static BoundingBox box(int x, int y, int z) {
        return new BoundingBox(x, y - 1, z, x + TowerBlueprint.SIZE - 1, y + TowerBlueprint.TOP, z + TowerBlueprint.SIZE - 1);
    }

    public int originX() { return originX; }
    public int baseY() { return baseY; }
    public int originZ() { return originZ; }

    @Override
    protected void addAdditionalSaveData(StructurePieceSerializationContext context, CompoundTag tag) {
        tag.putInt("OX", originX);
        tag.putInt("BY", baseY);
        tag.putInt("OZ", originZ);
        tag.putInt("V", variant);
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager structures, ChunkGenerator generator, RandomSource random,
                            BoundingBox chunkBox, ChunkPos chunkPos, BlockPos pivot) {
        int minX = Math.max(originX, chunkBox.minX());
        int maxX = Math.min(originX + TowerBlueprint.SIZE - 1, chunkBox.maxX());
        int minZ = Math.max(originZ, chunkBox.minZ());
        int maxZ = Math.min(originZ + TowerBlueprint.SIZE - 1, chunkBox.maxZ());
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        for (int x = minX; x <= maxX; x++) {
            for (int z = minZ; z <= maxZ; z++) {
                int lx = x - originX;
                int lz = z - originZ;
                foundation(level, p, x, z);
                for (int ly = 0; ly <= TowerBlueprint.TOP; ly++) {
                    BlockState state = TowerBlueprint.stateAt(lx, ly, lz, variant);
                    if (state == null) {
                        continue;
                    }
                    p.set(x, baseY + ly, z);
                    if (!chunkBox.isInside(p)) {
                        continue;
                    }
                    if (state.isAir() && level.getBlockState(p).isAir()) {
                        continue;
                    }
                    level.setBlock(p, state, 2);
                    if (state.is(Blocks.IRON_BARS)) {
                        level.getChunk(p).markPosForPostprocessing(p); // join the bars to their neighbours
                    }
                    ResourceKey<LootTable> loot = TowerBlueprint.lootAt(lx, ly, lz);
                    if (loot != null && state.is(Blocks.CHEST)) {
                        RandomizableContainer.setBlockEntityLootTable(level, random, p.immutable(), loot);
                    }
                }
            }
        }
    }

    /** Fill under the platform down to solid ground so the tower never floats over a cliff or a lake. */
    private void foundation(WorldGenLevel level, BlockPos.MutableBlockPos p, int x, int z) {
        for (int y = baseY - 1; y >= baseY - FOUNDATION_DEPTH && y > level.getMinBuildHeight(); y--) {
            p.set(x, y, z);
            BlockState s = level.getBlockState(p);
            boolean soft = s.isAir() || !s.getFluidState().isEmpty() || s.canBeReplaced() || s.is(BlockTags.LEAVES) || s.is(BlockTags.LOGS);
            if (!soft) {
                return;
            }
            level.setBlock(p, TowerBlueprint.FOUNDATION, 2);
        }
    }
}
