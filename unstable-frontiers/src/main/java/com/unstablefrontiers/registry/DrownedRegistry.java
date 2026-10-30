package com.unstablefrontiers.registry;

import com.mojang.serialization.MapCodec;
import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.block.BreathVentBlock;
import com.unstablefrontiers.block.TideBellBlock;
import com.unstablefrontiers.block.TideGateBlock;
import com.unstablefrontiers.block.TideGlyphBlock;
import com.unstablefrontiers.drowned.DivingGearItem;
import com.unstablefrontiers.drowned.DrownedBiomeSource;
import com.unstablefrontiers.drowned.DrownedChunkGenerator;
import com.unstablefrontiers.drowned.EchoSounderItem;
import com.unstablefrontiers.drowned.UndertowItem;
import com.unstablefrontiers.item.TrophyItem;
import java.util.List;
import java.util.function.Function;
import java.util.function.Supplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.biome.BiomeSource;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Everything the Drowned Expanse adds: its stone and markers, the gates and bells, the diving gear and its rewards. */
public final class DrownedRegistry {
    private static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(UnstableFrontiers.MODID);
    private static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(UnstableFrontiers.MODID);
    private static final DeferredRegister<MapCodec<? extends ChunkGenerator>> GENERATORS = DeferredRegister.create(Registries.CHUNK_GENERATOR, UnstableFrontiers.MODID);
    private static final DeferredRegister<MapCodec<? extends BiomeSource>> BIOME_SOURCES = DeferredRegister.create(Registries.BIOME_SOURCE, UnstableFrontiers.MODID);

    private static BlockBehaviour.Properties stone() {
        return BlockBehaviour.Properties.of().mapColor(MapColor.WARPED_NYLIUM).strength(2.0F, 6.0F).requiresCorrectToolForDrops().sound(SoundType.DEEPSLATE);
    }

    private static BlockBehaviour.Properties fixed() {
        return BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_CYAN).strength(-1.0F, 3600000.0F).noLootTable().pushReaction(PushReaction.BLOCK);
    }

    // ------------------------------------------------------------------------------------------------- blocks
    public static final DeferredBlock<Block> BRINE_SLATE = block("brine_slate", Block::new, stone());
    public static final DeferredBlock<Block> BRINE_BRICKS = block("brine_bricks", Block::new, stone().strength(2.5F, 6.0F).sound(SoundType.DEEPSLATE_BRICKS));
    public static final DeferredBlock<Block> CHISELED_BRINE = block("chiseled_brine", Block::new,
            stone().strength(2.5F, 6.0F).sound(SoundType.DEEPSLATE_TILES).lightLevel(s -> 7));
    public static final DeferredBlock<Block> LUMEN_CORAL = block("lumen_coral", Block::new,
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_LIGHT_BLUE).strength(1.0F).sound(SoundType.CORAL_BLOCK).lightLevel(s -> 12));
    public static final DeferredBlock<Block> BREATH_VENT = block("breath_vent", BreathVentBlock::new, stone().strength(3.0F, 6.0F).lightLevel(s -> 9));
    public static final DeferredBlock<Block> TIDE_GLYPH = block("tide_glyph", TideGlyphBlock::new, stone().lightLevel(s -> 1));
    public static final DeferredBlock<Block> TIDE_GATE = block("tide_gate", TideGateBlock::new,
            fixed().noCollission().noOcclusion().sound(SoundType.GLASS).lightLevel(s -> 12));
    public static final DeferredBlock<Block> TIDE_BELL = block("tide_bell", p -> new TideBellBlock(p, false),
            fixed().noOcclusion().sound(SoundType.ANVIL).lightLevel(s -> 10));
    public static final DeferredBlock<Block> ABYSSAL_BELL = block("abyssal_bell", p -> new TideBellBlock(p, true),
            fixed().noOcclusion().sound(SoundType.ANVIL).lightLevel(s -> 6));

    // -------------------------------------------------------------------------------------------------- items
    public static final DeferredItem<Item> GOGGLES = ITEMS.register("abyssal_goggles",
            () -> new DivingGearItem(new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON), DivingGearItem.Kind.GOGGLES));
    public static final DeferredItem<Item> DEEP_GOGGLES = ITEMS.register("deep_sight_goggles",
            () -> new DivingGearItem(new Item.Properties().stacksTo(1).rarity(Rarity.RARE).fireResistant(), DivingGearItem.Kind.DEEP_GOGGLES));
    public static final DeferredItem<Item> RIG = ITEMS.register("diving_rig",
            () -> new DivingGearItem(new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON), DivingGearItem.Kind.RIG));
    public static final DeferredItem<Item> DEEP_RIG = ITEMS.register("deep_rig",
            () -> new DivingGearItem(new Item.Properties().stacksTo(1).rarity(Rarity.RARE).fireResistant(), DivingGearItem.Kind.DEEP_RIG));
    public static final DeferredItem<Item> FINS = ITEMS.register("swim_fins",
            () -> new DivingGearItem(new Item.Properties().stacksTo(1).rarity(Rarity.RARE), DivingGearItem.Kind.FINS));
    public static final DeferredItem<Item> CHARM = ITEMS.register("breath_charm",
            () -> new DivingGearItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant(), DivingGearItem.Kind.CHARM));
    public static final DeferredItem<Item> ECHO_SOUNDER = ITEMS.register("echo_sounder",
            () -> new EchoSounderItem(new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON)));
    public static final DeferredItem<Item> PRESSURE_VALVE = ITEMS.register("pressure_valve",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.RARE).stacksTo(1), 2));
    public static final DeferredItem<Item> KEEL_PLATE = ITEMS.register("keel_plate",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.RARE).stacksTo(1), 2));
    public static final DeferredItem<Item> CHOIR_PEARL = ITEMS.register("choir_pearl",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.RARE).stacksTo(1), 2));
    public static final DeferredItem<Item> ABYSSAL_PEARL = ITEMS.register("abyssal_pearl",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant(), 2));
    public static final DeferredItem<Item> UNDERTOW = ITEMS.register("undertow",
            () -> new UndertowItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant().durability(900)
                    .attributes(UndertowItem.attributes())));

    // ------------------------------------------------------------------------------------------ world generation
    public static final Supplier<MapCodec<DrownedChunkGenerator>> GENERATOR = GENERATORS.register("drowned", () -> DrownedChunkGenerator.CODEC);
    public static final Supplier<MapCodec<DrownedBiomeSource>> BIOMES = BIOME_SOURCES.register("drowned", () -> DrownedBiomeSource.CODEC);

    private DrownedRegistry() {}

    private static DeferredBlock<Block> block(String name, Function<BlockBehaviour.Properties, ? extends Block> make, BlockBehaviour.Properties p) {
        DeferredBlock<Block> b = BLOCKS.register(name, () -> make.apply(p));
        ITEMS.registerSimpleBlockItem(name, b, new Item.Properties());
        return b;
    }

    /** The creative tab, in the order an expedition meets them. */
    public static void addToTab(CreativeModeTab.Output out) {
        for (Supplier<? extends Item> i : List.<Supplier<? extends Item>>of(GOGGLES, RIG, ECHO_SOUNDER, PRESSURE_VALVE, FINS, CHOIR_PEARL,
                DEEP_GOGGLES, KEEL_PLATE, DEEP_RIG, ABYSSAL_PEARL, UNDERTOW, CHARM)) {
            out.accept(i.get());
        }
        for (DeferredBlock<Block> b : List.of(BRINE_SLATE, BRINE_BRICKS, CHISELED_BRINE, LUMEN_CORAL, BREATH_VENT, TIDE_GLYPH)) {
            out.accept(b.get());
        }
    }

    public static void register(IEventBus bus) {
        BLOCKS.register(bus);
        ITEMS.register(bus);
        GENERATORS.register(bus);
        BIOME_SOURCES.register(bus);
    }
}
