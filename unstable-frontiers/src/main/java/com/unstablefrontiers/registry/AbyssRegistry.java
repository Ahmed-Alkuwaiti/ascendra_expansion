package com.unstablefrontiers.registry;

import com.mojang.serialization.MapCodec;
import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.abyss.AbyssBiomeSource;
import com.unstablefrontiers.abyss.AbyssChunkGenerator;
import com.unstablefrontiers.block.AbyssGateBlock;
import com.unstablefrontiers.block.EclipseAltarBlock;
import com.unstablefrontiers.block.RiftEngineBlock;
import com.unstablefrontiers.block.UpdraftVentBlock;
import com.unstablefrontiers.block.UpdraftVentBlockEntity;
import com.unstablefrontiers.block.VoidCystBlock;
import com.unstablefrontiers.block.VoidTendrilBlock;
import com.unstablefrontiers.item.AstrolabeItem;
import com.unstablefrontiers.item.BlinkstoneItem;
import com.unstablefrontiers.item.CoronaItem;
import com.unstablefrontiers.item.TrophyItem;
import java.util.List;
import java.util.function.Function;
import java.util.function.Supplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.biome.BiomeSource;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.DropExperienceBlock;
import net.minecraft.world.level.block.FlowerBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.TransparentBlock;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Everything the Rift Observatory and the Astral Abyss add: blocks, items, the vent's block entity and the generator. */
public final class AbyssRegistry {
    private static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(UnstableFrontiers.MODID);
    private static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(UnstableFrontiers.MODID);
    private static final DeferredRegister<BlockEntityType<?>> BE = DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, UnstableFrontiers.MODID);
    private static final DeferredRegister<MapCodec<? extends ChunkGenerator>> GENERATORS = DeferredRegister.create(Registries.CHUNK_GENERATOR, UnstableFrontiers.MODID);
    private static final DeferredRegister<MapCodec<? extends BiomeSource>> BIOME_SOURCES = DeferredRegister.create(Registries.BIOME_SOURCE, UnstableFrontiers.MODID);

    private static BlockBehaviour.Properties stone() {
        return BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLUE).strength(2.0F, 6.0F).requiresCorrectToolForDrops().sound(SoundType.DEEPSLATE);
    }

    // ------------------------------------------------------------------------------------------------- blocks
    public static final DeferredBlock<Block> ASTRAL_SHALE = block("astral_shale", Block::new, stone());
    public static final DeferredBlock<Block> ASTRAL_BRICKS = block("astral_bricks", Block::new, stone().strength(2.5F, 6.0F).sound(SoundType.DEEPSLATE_BRICKS));
    public static final DeferredBlock<Block> CHISELED_ASTRAL = block("chiseled_astral", Block::new,
            stone().strength(2.5F, 6.0F).sound(SoundType.DEEPSLATE_TILES).lightLevel(s -> 5));
    public static final DeferredBlock<Block> STARMOSS = block("starmoss", Block::new,
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_CYAN).strength(0.9F).sound(SoundType.MOSS));
    public static final DeferredBlock<Block> LUMEN_CRYSTAL = block("lumen_crystal", Block::new,
            BlockBehaviour.Properties.of().mapColor(MapColor.DIAMOND).strength(1.2F).sound(SoundType.AMETHYST).lightLevel(s -> 13).noOcclusion());
    public static final DeferredBlock<Block> RIFT_GLASS = block("rift_glass", TransparentBlock::new,
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(0.6F).sound(SoundType.GLASS).noOcclusion()
                    .isValidSpawn((s, l, p, t) -> false).isRedstoneConductor((s, l, p) -> false).isSuffocating((s, l, p) -> false)
                    .isViewBlocking((s, l, p) -> false));
    public static final DeferredBlock<Block> ASTRAL_ORE = block("astral_ore", p -> new DropExperienceBlock(UniformInt.of(2, 5), p),
            stone().strength(3.5F, 6.0F));
    public static final DeferredBlock<Block> STARBLOOM = block("starbloom", p -> new FlowerBlock(MobEffects.NIGHT_VISION, 8.0F, p),
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_LIGHT_BLUE).noCollission().instabreak().sound(SoundType.SPORE_BLOSSOM)
                    .lightLevel(s -> 7).offsetType(BlockBehaviour.OffsetType.XZ).pushReaction(PushReaction.DESTROY));
    public static final DeferredBlock<Block> VOID_TENDRIL = block("void_tendril", VoidTendrilBlock::new,
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).noCollission().instabreak().sound(SoundType.CAVE_VINES)
                    .lightLevel(s -> 4).pushReaction(PushReaction.DESTROY));
    public static final DeferredBlock<Block> VOID_CYST = block("void_cyst", VoidCystBlock::new,
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(0.4F).sound(SoundType.SLIME_BLOCK).lightLevel(s -> 6)
                    .noOcclusion().pushReaction(PushReaction.DESTROY));
    public static final DeferredBlock<Block> ABYSS_GATE = block("abyss_gate", AbyssGateBlock::new,
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(-1.0F, 3600000.0F).noLootTable().sound(SoundType.GLASS)
                    .lightLevel(s -> s.getValue(AbyssGateBlock.OPEN) ? 15 : 3).noOcclusion().pushReaction(PushReaction.BLOCK));
    public static final DeferredBlock<Block> RIFT_ENGINE = block("rift_engine", RiftEngineBlock::new,
            BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1.0F, 3600000.0F).noLootTable().sound(SoundType.NETHERITE_BLOCK)
                    .lightLevel(s -> s.getValue(RiftEngineBlock.ACTIVE) ? 15 : 6));
    public static final DeferredBlock<Block> UPDRAFT_VENT = block("updraft_vent", UpdraftVentBlock::new,
            stone().strength(3.0F, 6.0F).lightLevel(s -> 9));
    public static final DeferredBlock<Block> ECLIPSE_ALTAR = block("eclipse_altar", EclipseAltarBlock::new,
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(-1.0F, 3600000.0F).noLootTable()
                    .sound(SoundType.LODESTONE).lightLevel(s -> 8));

    public static final Supplier<BlockEntityType<UpdraftVentBlockEntity>> UPDRAFT_VENT_BE = BE.register("updraft_vent",
            () -> BlockEntityType.Builder.of(UpdraftVentBlockEntity::new, UPDRAFT_VENT.get()).build(null));

    // -------------------------------------------------------------------------------------------------- items
    public static final DeferredItem<Item> FOCUSING_LENS = ITEMS.register("focusing_lens",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.RARE).fireResistant().stacksTo(1), 2));
    public static final DeferredItem<Item> COOLANT_HEART = ITEMS.register("coolant_heart",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.RARE).fireResistant().stacksTo(1), 2));
    public static final DeferredItem<Item> STAR_CHART = ITEMS.register("star_chart",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.RARE).fireResistant().stacksTo(1), 2));
    public static final DeferredItem<Item> ASTROLABE = ITEMS.register("astrolabe",
            () -> new AstrolabeItem(new Item.Properties().rarity(Rarity.UNCOMMON).stacksTo(1)));
    public static final DeferredItem<Item> SIGIL_SHARD = ITEMS.register("sigil_shard",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.RARE).fireResistant(), 2));
    public static final DeferredItem<Item> ECLIPSE_SIGIL = ITEMS.register("eclipse_sigil",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant().stacksTo(1), 2));
    public static final DeferredItem<Item> RAW_STARMETAL = ITEMS.registerSimpleItem("raw_starmetal");
    public static final DeferredItem<Item> STARMETAL_INGOT = ITEMS.register("starmetal_ingot",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.UNCOMMON), 1));
    public static final DeferredItem<Item> LUMEN_CORE = ITEMS.register("lumen_core",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.UNCOMMON), 1));
    public static final DeferredItem<Item> ECLIPSE_SCALE = ITEMS.register("eclipse_scale",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant(), 2));
    public static final DeferredItem<Item> BLINKSTONE = ITEMS.register("blinkstone",
            () -> new BlinkstoneItem(new Item.Properties().rarity(Rarity.RARE).stacksTo(1).durability(240)));
    public static final DeferredItem<Item> CORONA = ITEMS.register("corona",
            () -> new CoronaItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant().attributes(CoronaItem.attributes())));
    public static final DeferredItem<Item> STAR_BOLT = ITEMS.registerSimpleItem("star_bolt");

    // ------------------------------------------------------------------------------------------ world generation
    public static final Supplier<MapCodec<AbyssChunkGenerator>> ABYSS_GENERATOR = GENERATORS.register("abyss", () -> AbyssChunkGenerator.CODEC);
    public static final Supplier<MapCodec<AbyssBiomeSource>> ABYSS_BIOMES = BIOME_SOURCES.register("abyss", () -> AbyssBiomeSource.CODEC);

    private AbyssRegistry() {}

    private static DeferredBlock<Block> block(String name, Function<BlockBehaviour.Properties, ? extends Block> make, BlockBehaviour.Properties p) {
        DeferredBlock<Block> b = BLOCKS.register(name, () -> make.apply(p));
        ITEMS.registerSimpleBlockItem(name, b, new Item.Properties());
        return b;
    }

    /** What the creative tab lists, in the order the adventure meets them. */
    public static void addToTab(CreativeModeTab.Output out) {
        for (Supplier<? extends Item> i : List.<Supplier<? extends Item>>of(ASTROLABE, FOCUSING_LENS, COOLANT_HEART, STAR_CHART, SIGIL_SHARD,
                ECLIPSE_SIGIL, BLINKSTONE, RAW_STARMETAL, STARMETAL_INGOT, LUMEN_CORE, ECLIPSE_SCALE, CORONA)) {
            out.accept(i.get());
        }
        for (DeferredBlock<Block> b : List.of(ASTRAL_SHALE, ASTRAL_BRICKS, CHISELED_ASTRAL, STARMOSS, LUMEN_CRYSTAL, RIFT_GLASS, ASTRAL_ORE,
                STARBLOOM, VOID_TENDRIL, VOID_CYST, UPDRAFT_VENT)) {
            out.accept(b.get());
        }
    }

    public static void register(IEventBus bus) {
        BLOCKS.register(bus);
        ITEMS.register(bus);
        BE.register(bus);
        GENERATORS.register(bus);
        BIOME_SOURCES.register(bus);
    }
}
