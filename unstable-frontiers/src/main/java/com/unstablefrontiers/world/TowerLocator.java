package com.unstablefrontiers.world;

import com.unstablefrontiers.registry.ModStructures;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.StructureStart;

/** Finds the tower at a position from the structure references already stored in that chunk. Never searches the world. */
public final class TowerLocator {
    private TowerLocator() {}

    @Nullable
    public static Structure tower(ServerLevel level) {
        return level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(ModStructures.CAGE_TOWER);
    }

    /**
     * The tower whose footprint holds this position, or null. The chunk must already be loaded. With ignoreY, any height
     * above or below the footprint counts, which the debug commands use.
     */
    @Nullable
    public static TowerRef at(ServerLevel level, BlockPos pos, boolean ignoreY) {
        Structure tower = tower(level);
        if (tower == null || !level.isLoaded(pos)) {
            return null;
        }
        for (StructureStart start : level.structureManager().startsForStructure(new ChunkPos(pos), s -> s == tower)) {
            for (StructurePiece piece : start.getPieces()) {
                if (!(piece instanceof CageTowerPiece t)) {
                    continue;
                }
                BoundingBox b = piece.getBoundingBox();
                boolean inXZ = pos.getX() >= b.minX() && pos.getX() <= b.maxX() && pos.getZ() >= b.minZ() && pos.getZ() <= b.maxZ();
                boolean inY = ignoreY || (pos.getY() >= b.minY() - 2 && pos.getY() <= b.maxY() + 4);
                if (inXZ && inY) {
                    return new TowerRef(start.getChunkPos().toLong(), t.originX(), t.baseY(), t.originZ());
                }
            }
        }
        return null;
    }
}
