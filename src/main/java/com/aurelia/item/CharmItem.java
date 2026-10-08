package com.aurelia.item;

import com.aurelia.world.Realm;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

/** A Realm Charm, made from the trophies of a realm's lieutenants. Carried anywhere in the inventory, it grants the realm's boon. */
public class CharmItem extends Item {
    public final Realm realm;

    public CharmItem(Properties properties, Realm realm) {
        super(properties);
        this.realm = realm;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.aurelia." + realm.id + "_charm.lore").withStyle(ChatFormatting.LIGHT_PURPLE));
        tooltip.add(Component.literal("Works anywhere in your inventory.").withStyle(ChatFormatting.DARK_GRAY, ChatFormatting.ITALIC));
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return true;
    }
}
