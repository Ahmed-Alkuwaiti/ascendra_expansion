package com.unstablefrontiers.world;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.StructureStart;

/** Finds landmarks from the structure references already stored in loaded chunks. Never searches or generates the world. */
public final class LandmarkLocator {
    private LandmarkLocator() {}

    /** Landmark pieces referenced by the chunks within `radius` chunks of pos that are loaded. */
    public static List<LandmarkPiece> near(ServerLevel level, BlockPos pos, int radius) {
        List<LandmarkPiece> out = new ArrayList<>();
        ChunkPos c = new ChunkPos(pos);
        for (int dx = -radius; dx <= radius; dx++) {
            for (int dz = -radius; dz <= radius; dz++) {
                if (!level.hasChunk(c.x + dx, c.z + dz)) {
                    continue;
                }
                for (StructureStart start : level.structureManager().startsForStructure(new ChunkPos(c.x + dx, c.z + dz),
                        s -> s instanceof LandmarkStructure)) {
                    for (StructurePiece piece : start.getPieces()) {
                        if (piece instanceof LandmarkPiece lp && !out.contains(lp)) {
                            out.add(lp);
                        }
                    }
                }
            }
        }
        return out;
    }
}
