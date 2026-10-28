package com.unstablefrontiers.registry;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.world.LandmarkPiece;
import com.unstablefrontiers.world.LandmarkStructure;
import com.unstablefrontiers.world.TerrainFeature;
import net.minecraft.world.level.levelgen.feature.Feature;
import java.util.function.Supplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModStructures {
    private static final DeferredRegister<StructureType<?>> TYPES = DeferredRegister.create(Registries.STRUCTURE_TYPE, UnstableFrontiers.MODID);
    private static final DeferredRegister<StructurePieceType> PIECES = DeferredRegister.create(Registries.STRUCTURE_PIECE, UnstableFrontiers.MODID);

    public static final Supplier<StructureType<LandmarkStructure>> LANDMARK_TYPE = TYPES.register("landmark", () -> () -> LandmarkStructure.CODEC);
    private static final DeferredRegister<Feature<?>> FEATURES = DeferredRegister.create(Registries.FEATURE, UnstableFrontiers.MODID);
    public static final Supplier<TerrainFeature> TERRAIN = FEATURES.register("terrain", TerrainFeature::new);

    public static final Supplier<StructurePieceType> LANDMARK_PIECE = PIECES.register("landmark",
            () -> (StructurePieceType.StructureTemplateType) LandmarkPiece::new);

    /** Every landmark, and the groups the Rift Lens surveys (data/unstable_frontiers/tags/worldgen/structure). */
    public static final TagKey<Structure> LANDMARKS = tag("landmarks");
    public static final TagKey<Structure> CAGES = tag("lens/cages");
    public static final TagKey<Structure> LAIRS = tag("lens/lairs");
    public static final TagKey<Structure> CAMPS = tag("lens/camps");
    public static final TagKey<Structure> GREAT_CAGE = tag("lens/great_cage");

    private ModStructures() {}

    private static TagKey<Structure> tag(String path) {
        return TagKey.create(Registries.STRUCTURE, UnstableFrontiers.id(path));
    }

    public static void register(IEventBus bus) {
        TYPES.register(bus);
        PIECES.register(bus);
        FEATURES.register(bus);
    }
}
