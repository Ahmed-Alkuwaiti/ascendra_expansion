package com.unstablefrontiers.world;

import com.unstablefrontiers.registry.ModStructures;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.TemplateStructurePiece;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;
import net.minecraft.world.level.levelgen.structure.templatesystem.BlockIgnoreProcessor;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;

/**
 * One landmark, placed from its saved template (data/unstable_frontiers/structure) with a rotation. Air in the template
 * is placed, so rooms are carved out of the ground; positions the template leaves unset keep the terrain. With
 * foundation on, every solid block of the template's lowest layer is continued straight down to the ground (at most
 * 40 blocks), so nothing stands on air where the land falls away.
 */
public class LandmarkPiece extends TemplateStructurePiece {
    private static final int MAX_FOUNDATION = 40;
    private static final int RIM = 12;
    private final boolean foundation;
    /** Template rows below the ground row; -1 = do not clear the site. */
    private final int clearFrom;

    public LandmarkPiece(StructureTemplateManager manager, ResourceLocation template, BlockPos origin, Rotation rotation, boolean foundation,
                         int clearFrom) {
        super(ModStructures.LANDMARK_PIECE.get(), 0, manager, template, template.toString(), settings(rotation), origin);
        this.foundation = foundation;
        this.clearFrom = clearFrom;
    }

    public LandmarkPiece(StructureTemplateManager manager, CompoundTag tag) {
        super(ModStructures.LANDMARK_PIECE.get(), tag, manager, id -> settings(rotation(tag)));
        this.foundation = tag.getBoolean("Foundation");
        this.clearFrom = tag.contains("Clear") ? tag.getInt("Clear") : -1;
    }

    public static StructurePlaceSettings settings(Rotation rotation) {
        return new StructurePlaceSettings().setRotation(rotation).addProcessor(new BlockIgnoreProcessor(List.of(Blocks.STRUCTURE_VOID)));
    }

    private static Rotation rotation(CompoundTag tag) {
        try {
            return Rotation.valueOf(tag.getString("Rot"));
        } catch (IllegalArgumentException e) {
            return Rotation.NONE;
        }
    }

    public ResourceLocation template() {
        return ResourceLocation.parse(templateName);
    }

    public BlockPos origin() {
        return templatePosition;
    }

    public Rotation rotation() {
        return placeSettings.getRotation();
    }

    @Override
    protected void addAdditionalSaveData(StructurePieceSerializationContext context, CompoundTag tag) {
        super.addAdditionalSaveData(context, tag);
        tag.putString("Rot", rotation().name());
        tag.putBoolean("Foundation", foundation);
        tag.putInt("Clear", clearFrom);
    }

    @Override
    protected void handleDataMarker(String name, BlockPos pos, ServerLevelAccessor level, RandomSource random, BoundingBox box) {}

    @Override
    public void postProcess(WorldGenLevel level, StructureManager structures, ChunkGenerator generator, RandomSource random,
                            BoundingBox chunkBox, ChunkPos chunkPos, BlockPos pivot) {
        if (clearFrom >= 0) {
            clearSite(level, chunkBox);
        }
        super.postProcess(level, structures, generator, random, chunkBox, chunkPos, pivot);
        if (foundation) {
            fillFoundation(level, chunkBox);
        }
    }

    /**
     * Cuts back terrain that rises above the ground row inside the footprint's inscribed ellipse, so a landmark on a slope
     * stands in a clearing rather than half inside a hill. Toward the rim the cut rises (up to 12 blocks at the edge), so
     * the clearing meets the hillside as a slope, not a wall. Runs before the template, so nothing of the landmark is cut.
     */
    private void clearSite(WorldGenLevel level, BoundingBox chunkBox) {
        BoundingBox box = getBoundingBox();
        int ground = templatePosition.getY() + clearFrom;
        double cx = (box.minX() + box.maxX()) / 2.0D, cz = (box.minZ() + box.maxZ()) / 2.0D;
        double rx = box.getXSpan() / 2.0D, rz = box.getZSpan() / 2.0D;
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        BlockState air = Blocks.AIR.defaultBlockState();
        for (int x = Math.max(box.minX(), chunkBox.minX()); x <= Math.min(box.maxX(), chunkBox.maxX()); x++) {
            for (int z = Math.max(box.minZ(), chunkBox.minZ()); z <= Math.min(box.maxZ(), chunkBox.maxZ()); z++) {
                double e = Math.sqrt(Math.pow((x - cx) / rx, 2) + Math.pow((z - cz) / rz, 2));
                if (e > 1.0D) {
                    continue;
                }
                int from = ground + 1 + (int) Math.round(Math.max(0, (e - 0.75D) / 0.25D) * RIM);
                for (int y = from; y <= box.maxY(); y++) {
                    if (!level.getBlockState(p.set(x, y, z)).isAir()) {
                        level.setBlock(p, air, 2);
                    }
                }
            }
        }
    }

    private void fillFoundation(WorldGenLevel level, BoundingBox chunkBox) {
        BoundingBox box = getBoundingBox();
        int y0 = box.minY();
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        for (int x = Math.max(box.minX(), chunkBox.minX()); x <= Math.min(box.maxX(), chunkBox.maxX()); x++) {
            for (int z = Math.max(box.minZ(), chunkBox.minZ()); z <= Math.min(box.maxZ(), chunkBox.maxZ()); z++) {
                BlockState top = level.getBlockState(p.set(x, y0, z));
                if (top.isAir() || !top.getFluidState().isEmpty() || !top.blocksMotion()) {
                    continue;
                }
                BlockState fill = top.getBlock().defaultBlockState();
                for (int y = y0 - 1; y >= Math.max(level.getMinBuildHeight(), y0 - MAX_FOUNDATION); y--) {
                    BlockState below = level.getBlockState(p.set(x, y, z));
                    if (below.blocksMotion() && below.getFluidState().isEmpty()) {
                        break;
                    }
                    level.setBlock(p, fill, 2);
                }
            }
        }
    }
}
