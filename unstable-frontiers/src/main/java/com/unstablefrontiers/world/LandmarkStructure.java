package com.unstablefrontiers.world;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.registry.ModStructures;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Optional;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Vec3i;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;

/**
 * A landmark site: one template, turned at random, centred on the chunk the structure set chose. The site is sampled at
 * nine points across the rotated footprint; it is rejected if the ground varies by more than max_slope or stands in water
 * deeper than max_water, so big landmarks only rise where they fit. The template's "ground" row is set at the median
 * surface height (plus y_offset); with clear_site, higher ground inside the footprint is cut back (see LandmarkPiece).
 * Costs eighteen height samples per candidate and nothing else.
 */
public class LandmarkStructure extends Structure {
    public static final MapCodec<LandmarkStructure> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            settingsCodec(i),
            ResourceLocation.CODEC.fieldOf("template").forGetter(s -> s.template),
            Codec.INT.fieldOf("ground").forGetter(s -> s.ground),
            Codec.INT.optionalFieldOf("max_slope", 10).forGetter(s -> s.maxSlope),
            Codec.INT.optionalFieldOf("max_water", 2).forGetter(s -> s.maxWater),
            Codec.INT.optionalFieldOf("y_offset", 0).forGetter(s -> s.yOffset),
            Codec.BOOL.optionalFieldOf("foundation", true).forGetter(s -> s.foundation),
            Codec.BOOL.optionalFieldOf("clear_site", true).forGetter(s -> s.clearSite)
    ).apply(i, LandmarkStructure::new));

    private static final Set<ResourceLocation> WARNED = new HashSet<>();

    private final ResourceLocation template;
    private final int ground;
    private final int maxSlope;
    private final int maxWater;
    private final int yOffset;
    private final boolean foundation;
    private final boolean clearSite;

    public LandmarkStructure(Structure.StructureSettings settings, ResourceLocation template, int ground, int maxSlope, int maxWater,
                             int yOffset, boolean foundation, boolean clearSite) {
        super(settings);
        this.template = template;
        this.ground = ground;
        this.maxSlope = maxSlope;
        this.maxWater = maxWater;
        this.yOffset = yOffset;
        this.foundation = foundation;
        this.clearSite = clearSite;
    }

    public int ground() {
        return ground;
    }

    public boolean clearSite() {
        return clearSite;
    }

    public ResourceLocation template() {
        return template;
    }

    @Override
    protected Optional<Structure.GenerationStub> findGenerationPoint(Structure.GenerationContext ctx) {
        Optional<StructureTemplate> found = ctx.structureTemplateManager().get(template);
        if (found.isEmpty() || found.get().getSize().equals(Vec3i.ZERO)) {
            if (WARNED.add(template)) {
                UnstableFrontiers.LOGGER.error("Landmark template {} is missing; that landmark cannot generate", template);
            }
            return Optional.empty();
        }
        StructureTemplate t = found.get();
        Rotation rotation = Rotation.getRandom(ctx.random());
        BoundingBox local = t.getBoundingBox(LandmarkPiece.settings(rotation), BlockPos.ZERO);
        ChunkPos chunk = ctx.chunkPos();
        int ox = chunk.getMiddleBlockX() - (local.minX() + local.maxX()) / 2;
        int oz = chunk.getMiddleBlockZ() - (local.minZ() + local.maxZ()) / 2;
        int x0 = ox + local.minX(), x1 = ox + local.maxX();
        int z0 = oz + local.minZ(), z1 = oz + local.maxZ();
        int[] ys = new int[9];
        int k = 0;
        for (int sx = 0; sx < 3; sx++) {
            for (int sz = 0; sz < 3; sz++) {
                int x = x0 + (x1 - x0) * sx / 2;
                int z = z0 + (z1 - z0) * sz / 2;
                int surface = height(ctx, x, z, Heightmap.Types.WORLD_SURFACE_WG);
                int floor = height(ctx, x, z, Heightmap.Types.OCEAN_FLOOR_WG);
                if (surface - floor > maxWater) {
                    return Optional.empty();
                }
                ys[k++] = floor;
            }
        }
        Arrays.sort(ys);
        if (ys[8] - ys[0] > maxSlope) {
            return Optional.empty();
        }
        int base = ys[4] + yOffset;
        int oy = base - ground;
        if (oy < ctx.heightAccessor().getMinBuildHeight() + 4 || oy + t.getSize().getY() > ctx.heightAccessor().getMaxBuildHeight() - 2) {
            return Optional.empty();
        }
        BlockPos origin = new BlockPos(ox, oy, oz);
        BlockPos centre = new BlockPos(chunk.getMiddleBlockX(), base, chunk.getMiddleBlockZ());
        return Optional.of(new Structure.GenerationStub(centre,
                builder -> builder.addPiece(new LandmarkPiece(ctx.structureTemplateManager(), template, origin, rotation, foundation,
                        clearSite ? ground : -1))));
    }

    private static int height(Structure.GenerationContext ctx, int x, int z, Heightmap.Types type) {
        return ctx.chunkGenerator().getBaseHeight(x, z, type, ctx.heightAccessor(), ctx.randomState());
    }

    @Override
    public StructureType<?> type() {
        return ModStructures.LANDMARK_TYPE.get();
    }
}
