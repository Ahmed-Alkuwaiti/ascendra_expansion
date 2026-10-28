package com.unstablefrontiers.registry;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.block.CageBeaconBlock;
import com.unstablefrontiers.item.CagewrightKeyItem;
import com.unstablefrontiers.item.RiftLensItem;
import com.unstablefrontiers.item.RiftShardItem;
import com.unstablefrontiers.item.ShackleItem;
import com.unstablefrontiers.item.SwarmbreakerItem;
import com.unstablefrontiers.item.TrophyItem;
import java.util.function.Supplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModItems {
    private static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(UnstableFrontiers.MODID);
    private static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(UnstableFrontiers.MODID);
    private static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, UnstableFrontiers.MODID);

    public static final DeferredItem<Item> RIFT_SHARD = ITEMS.register("rift_shard",
            () -> new RiftShardItem(new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON)));
    public static final DeferredItem<Item> CAGE_TROPHY = ITEMS.register("cage_trophy",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.RARE).fireResistant(), 3));
    public static final DeferredItem<Item> ROOKERY_TALON = ITEMS.register("rookery_talon",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.RARE).fireResistant(), 3));
    public static final DeferredItem<Item> HIVE_HEART = ITEMS.register("hive_heart",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.RARE).fireResistant(), 3));
    public static final DeferredItem<Item> GREAT_CAGE_HEART = ITEMS.register("great_cage_heart",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant().stacksTo(16), 3));
    public static final DeferredItem<Item> CAGEWRIGHT_KEY = ITEMS.register("cagewright_key",
            () -> new CagewrightKeyItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant().stacksTo(1)));
    public static final DeferredItem<Item> RIFT_LENS = ITEMS.register("rift_lens",
            () -> new RiftLensItem(new Item.Properties().rarity(Rarity.UNCOMMON).stacksTo(1)));
    public static final DeferredItem<Item> SHACKLE = ITEMS.register("cagewright_shackle",
            () -> new ShackleItem(new Item.Properties().rarity(Rarity.RARE).durability(6)));
    public static final DeferredItem<Item> SWARMBREAKER = ITEMS.register("swarmbreaker",
            () -> new SwarmbreakerItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant()
                    .attributes(SwarmbreakerItem.attributes())));

    public static final DeferredBlock<Block> CAGE_BEACON = BLOCKS.register("cage_beacon",
            () -> new CageBeaconBlock(Block.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(5.0F, 1200.0F)
                    .requiresCorrectToolForDrops().lightLevel(s -> 13).sound(SoundType.LODESTONE)));
    public static final DeferredItem<BlockItem> CAGE_BEACON_ITEM = ITEMS.registerSimpleBlockItem("cage_beacon", CAGE_BEACON,
            new Item.Properties().rarity(Rarity.EPIC));

    public static final Supplier<CreativeModeTab> TAB = TABS.register("main", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.unstable_frontiers"))
            .icon(() -> new ItemStack(RIFT_SHARD.get()))
            .displayItems((params, out) -> {
                out.accept(RIFT_SHARD.get());
                out.accept(RIFT_LENS.get());
                out.accept(CAGE_TROPHY.get());
                out.accept(ROOKERY_TALON.get());
                out.accept(HIVE_HEART.get());
                out.accept(CAGEWRIGHT_KEY.get());
                out.accept(GREAT_CAGE_HEART.get());
                out.accept(SWARMBREAKER.get());
                out.accept(SHACKLE.get());
                out.accept(CAGE_BEACON_ITEM.get());
            })
            .build());

    private ModItems() {}

    public static void register(IEventBus bus) {
        BLOCKS.register(bus);
        ITEMS.register(bus);
        TABS.register(bus);
    }
}
