package com.unstablefrontiers.registry;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.block.CageBeaconBlock;
import com.unstablefrontiers.item.CagewrightKeyItem;
import com.unstablefrontiers.item.MatriarchMantleItem;
import com.unstablefrontiers.item.ShrikeImpalerItem;
import com.unstablefrontiers.item.RiftLensItem;
import com.unstablefrontiers.item.RiftShardItem;
import com.unstablefrontiers.item.ShackleItem;
import com.unstablefrontiers.item.SwarmbreakerItem;
import com.unstablefrontiers.item.TrophyItem;
import java.util.EnumMap;
import java.util.List;
import java.util.function.Supplier;
import net.minecraft.Util;
import net.minecraft.core.Holder;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.crafting.Ingredient;
import net.neoforged.neoforge.registries.DeferredHolder;
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
    private static final DeferredRegister<ArmorMaterial> ARMOR = DeferredRegister.create(Registries.ARMOR_MATERIAL, UnstableFrontiers.MODID);

    /** Gnashback Carapace: netherite's protection with a little more toughness and knockback resistance (see CreatureGearEvents). */
    public static final DeferredHolder<ArmorMaterial, ArmorMaterial> CARAPACE = ARMOR.register("carapace", () -> new ArmorMaterial(
            Util.make(new EnumMap<>(ArmorItem.Type.class), m -> {
                m.put(ArmorItem.Type.BOOTS, 3);
                m.put(ArmorItem.Type.LEGGINGS, 6);
                m.put(ArmorItem.Type.CHESTPLATE, 8);
                m.put(ArmorItem.Type.HELMET, 3);
                m.put(ArmorItem.Type.BODY, 11);
            }), 15, SoundEvents.ARMOR_EQUIP_NETHERITE, () -> Ingredient.of(ModItems.GNASHBACK_PLATE.get()),
            List.of(new ArmorMaterial.Layer(UnstableFrontiers.id("carapace"))), 3.5F, 0.15F));

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

    /** The Matriarch's projectile, as an item only so it can be drawn in flight. Not obtainable. */
    public static final DeferredItem<Item> ACID_GLOB = ITEMS.registerSimpleItem("acid_glob");

    public static final DeferredItem<Item> GNASHBACK_PLATE = ITEMS.register("gnashback_plate",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.UNCOMMON), 1));
    public static final DeferredItem<Item> SHRIKE_TALON = ITEMS.register("shrike_talon",
            () -> new TrophyItem(new Item.Properties().rarity(Rarity.UNCOMMON), 1));
    public static final DeferredItem<Item> CARAPACE_HELMET = armor("carapace_helmet", ArmorItem.Type.HELMET);
    public static final DeferredItem<Item> CARAPACE_CHESTPLATE = armor("carapace_chestplate", ArmorItem.Type.CHESTPLATE);
    public static final DeferredItem<Item> CARAPACE_LEGGINGS = armor("carapace_leggings", ArmorItem.Type.LEGGINGS);
    public static final DeferredItem<Item> CARAPACE_BOOTS = armor("carapace_boots", ArmorItem.Type.BOOTS);
    public static final DeferredItem<Item> SHRIKE_IMPALER = ITEMS.register("shrike_impaler",
            () -> new ShrikeImpalerItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant().attributes(ShrikeImpalerItem.attributes())));
    public static final DeferredItem<Item> MATRIARCH_MANTLE = ITEMS.register("matriarch_mantle",
            () -> new MatriarchMantleItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant().stacksTo(1)));

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
                out.accept(GNASHBACK_PLATE.get());
                out.accept(SHRIKE_TALON.get());
                out.accept(CARAPACE_HELMET.get());
                out.accept(CARAPACE_CHESTPLATE.get());
                out.accept(CARAPACE_LEGGINGS.get());
                out.accept(CARAPACE_BOOTS.get());
                out.accept(SHRIKE_IMPALER.get());
                out.accept(MATRIARCH_MANTLE.get());
                AbyssRegistry.addToTab(out);
                DrownedRegistry.addToTab(out);
            })
            .build());

    private ModItems() {}

    private static DeferredItem<Item> armor(String name, ArmorItem.Type type) {
        return ITEMS.register(name, () -> new ArmorItem(CARAPACE, type, new Item.Properties().rarity(Rarity.RARE).fireResistant()
                .durability(type.getDurability(40))));
    }

    public static void register(IEventBus bus) {
        ARMOR.register(bus);
        BLOCKS.register(bus);
        ITEMS.register(bus);
        TABS.register(bus);
    }
}
