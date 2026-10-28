package com.unstablefrontiers.registry;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.world.CageTowerPiece;
import com.unstablefrontiers.world.CageTowerStructure;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureSet;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;
import java.util.function.Supplier;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModStructures {
    private static final DeferredRegister<StructureType<?>> TYPES = DeferredRegister.create(Registries.STRUCTURE_TYPE, UnstableFrontiers.MODID);
    private static final DeferredRegister<StructurePieceType> PIECES = DeferredRegister.create(Registries.STRUCTURE_PIECE, UnstableFrontiers.MODID);

    public static final Supplier<StructureType<CageTowerStructure>> CAGE_TOWER_TYPE = TYPES.register("cage_tower", () -> () -> CageTowerStructure.CODEC);
    public static final Supplier<StructurePieceType> CAGE_TOWER_PIECE = PIECES.register("cage_tower",
            () -> (StructurePieceType.ContextlessType) CageTowerPiece::new);

    /** The structure as configured in data/unstable_frontiers/worldgen/structure/cage_tower.json. */
    public static final ResourceKey<Structure> CAGE_TOWER = ResourceKey.create(Registries.STRUCTURE, UnstableFrontiers.id("cage_tower"));
    public static final ResourceKey<StructureSet> CAGE_TOWER_SET = ResourceKey.create(Registries.STRUCTURE_SET, UnstableFrontiers.id("cage_towers"));
    public static final TagKey<Structure> CAGE_TOWERS = TagKey.create(Registries.STRUCTURE, UnstableFrontiers.id("cage_towers"));

    private ModStructures() {}

    public static void register(IEventBus bus) {
        TYPES.register(bus);
        PIECES.register(bus);
    }
}
