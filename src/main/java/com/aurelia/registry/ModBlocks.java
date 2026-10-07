package com.aurelia.registry;

import com.aurelia.AureliaMod;
import com.aurelia.block.AltarBlock;
import com.aurelia.block.PuzzleNodeBlock;
import com.aurelia.block.SealBlock;
import com.aurelia.block.TrapBlock;
import com.aurelia.block.WaygateBlock;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.DropExperienceBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/** Puzzle blocks are unbreakable in survival so nobody can soft-lock a citadel. Creative mode can still remove them. */
public class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS =
            DeferredRegister.create(ForgeRegistries.BLOCKS, AureliaMod.MODID);

    public static final RegistryObject<Block> WAYGATE = BLOCKS.register("waygate",
            () -> new WaygateBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.GOLD)
                    .strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> state.getValue(WaygateBlock.ACTIVE) ? 15 : 4)
                    .sound(SoundType.AMETHYST)));

    public static final RegistryObject<Block> WARDEN_ALTAR = BLOCKS.register("warden_altar",
            () -> new AltarBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_PURPLE)
                    .strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> 8)
                    .sound(SoundType.STONE)));

    public static final RegistryObject<Block> SPORE_PLANTER = BLOCKS.register("spore_planter",
            () -> new PuzzleNodeBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.PLANT)
                    .strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> state.getValue(PuzzleNodeBlock.FILLED) ? 12 : 0)
                    .sound(SoundType.MOSS),
                    PuzzleNodeBlock.Kind.PLANTER, () -> ModItems.SPORE_HEART.get()));

    public static final RegistryObject<Block> STORM_PYLON = BLOCKS.register("storm_pylon",
            () -> new PuzzleNodeBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_LIGHT_BLUE)
                    .strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> state.getValue(PuzzleNodeBlock.FILLED) ? 15 : 2)
                    .sound(SoundType.COPPER),
                    PuzzleNodeBlock.Kind.PYLON, () -> null));

    public static final RegistryObject<Block> SOUL_SOCKET = BLOCKS.register("soul_socket",
            () -> new PuzzleNodeBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_BLACK)
                    .strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> state.getValue(PuzzleNodeBlock.FILLED) ? 10 : 0)
                    .sound(SoundType.DEEPSLATE),
                    PuzzleNodeBlock.Kind.SOCKET, () -> ModItems.SOUL_SIGIL.get()));

    // ---- Citadel gimmicks: sealed doors and floor traps ----
    public static final RegistryObject<Block> BRAMBLE_SEAL = BLOCKS.register("bramble_seal",
            () -> new SealBlock(BlockBehaviour.Properties.of().mapColor(MapColor.PLANT).strength(-1.0f, 3600000.0f).noLootTable()
                    .sound(SoundType.WOOD), () -> ModEntities.BRAMBLE_SENTINEL.get(), "Bramble Sentinel"));
    public static final RegistryObject<Block> STORM_SEAL = BLOCKS.register("storm_seal",
            () -> new SealBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_LIGHT_BLUE).strength(-1.0f, 3600000.0f).noLootTable()
                    .lightLevel(state -> 8).sound(SoundType.GLASS), () -> ModEntities.CALCITE_SENTINEL.get(), "Calcite Sentinel"));
    public static final RegistryObject<Block> ASH_SEAL = BLOCKS.register("ash_seal",
            () -> new SealBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(-1.0f, 3600000.0f).noLootTable()
                    .lightLevel(state -> 6).sound(SoundType.DEEPSLATE), () -> ModEntities.ASHBOUND_KNIGHT.get(), "Ashbound Knight"));

    public static final RegistryObject<Block> SPORE_VENT = BLOCKS.register("spore_vent",
            () -> new TrapBlock(BlockBehaviour.Properties.of().mapColor(MapColor.PLANT).strength(3.0f).sound(SoundType.MOSS), TrapBlock.Kind.SPORE));
    public static final RegistryObject<Block> GALE_PLATE = BLOCKS.register("gale_plate",
            () -> new TrapBlock(BlockBehaviour.Properties.of().mapColor(MapColor.QUARTZ).strength(3.0f).lightLevel(state -> 7)
                    .sound(SoundType.COPPER), TrapBlock.Kind.GALE));
    public static final RegistryObject<Block> EMBER_VENT = BLOCKS.register("ember_vent",
            () -> new TrapBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(3.0f).lightLevel(state -> 9)
                    .sound(SoundType.DEEPSLATE), TrapBlock.Kind.EMBER));

    // ---- Mossback's gimmick ----
    public static final RegistryObject<Block> ROOT_HEART = BLOCKS.register("root_heart",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.PLANT).strength(2.0f).noLootTable()
                    .lightLevel(state -> 12).sound(SoundType.ROOTS)));

    // ---- Realm ores and their storage blocks ----
    public static final RegistryObject<Block> VERDANT_ORE = BLOCKS.register("verdant_ore",
            () -> new DropExperienceBlock(BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(3.0f, 3.0f)
                    .requiresCorrectToolForDrops().sound(SoundType.STONE), UniformInt.of(2, 5)));
    public static final RegistryObject<Block> STORMGLASS_ORE = BLOCKS.register("stormglass_ore",
            () -> new DropExperienceBlock(BlockBehaviour.Properties.of().mapColor(MapColor.QUARTZ).strength(3.0f, 3.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 4).sound(SoundType.CALCITE), UniformInt.of(2, 5)));
    public static final RegistryObject<Block> EMBERHEART_ORE = BLOCKS.register("emberheart_ore",
            () -> new DropExperienceBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(3.5f, 4.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 6).sound(SoundType.DEEPSLATE), UniformInt.of(3, 6)));
    public static final RegistryObject<Block> VERDANT_BLOCK = BLOCKS.register("verdant_block",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.EMERALD).strength(5.0f, 6.0f)
                    .requiresCorrectToolForDrops().sound(SoundType.AMETHYST)));
    public static final RegistryObject<Block> STORMGLASS_BLOCK = BLOCKS.register("stormglass_block",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_LIGHT_BLUE).strength(5.0f, 6.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 10).sound(SoundType.AMETHYST)));
    public static final RegistryObject<Block> EMBERHEART_BLOCK = BLOCKS.register("emberheart_block",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_ORANGE).strength(5.0f, 6.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 12).sound(SoundType.AMETHYST)));
}
