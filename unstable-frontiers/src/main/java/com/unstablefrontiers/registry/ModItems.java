package com.unstablefrontiers.registry;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.item.RiftShardItem;
import com.unstablefrontiers.item.SwarmbreakerItem;
import java.util.function.Supplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModItems {
    private static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(UnstableFrontiers.MODID);
    private static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, UnstableFrontiers.MODID);

    public static final DeferredItem<Item> RIFT_SHARD = ITEMS.register("rift_shard",
            () -> new RiftShardItem(new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON)));
    public static final DeferredItem<Item> CAGE_TROPHY = ITEMS.register("cage_trophy",
            () -> new Item(new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final DeferredItem<Item> SWARMBREAKER = ITEMS.register("swarmbreaker",
            () -> new SwarmbreakerItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant()
                    .attributes(SwarmbreakerItem.attributes())));

    public static final Supplier<CreativeModeTab> TAB = TABS.register("main", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.unstable_frontiers"))
            .icon(() -> new ItemStack(RIFT_SHARD.get()))
            .displayItems((params, out) -> {
                out.accept(RIFT_SHARD.get());
                out.accept(CAGE_TROPHY.get());
                out.accept(SWARMBREAKER.get());
            })
            .build());

    private ModItems() {}

    public static void register(IEventBus bus) {
        ITEMS.register(bus);
        TABS.register(bus);
    }
}
