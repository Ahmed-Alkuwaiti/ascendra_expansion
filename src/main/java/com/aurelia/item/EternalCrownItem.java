package com.aurelia.item;

import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

/** The Eternal Crown: the Ascendant Crown with the Hour Core and the Bloom Heart set in it. Powers in CrownEvents. */
public class EternalCrownItem extends ArmorItem {

    public EternalCrownItem(Properties properties) {
        super(AurelianArmorMaterial.ETERNAL, ArmorItem.Type.HELMET, properties);
    }

    @Override
    public boolean isDamageable(ItemStack stack) {
        return false;
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("It does not tick. It does not grow. It simply is.").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
        tooltip.add(Component.empty());
        tooltip.add(Component.literal("While worn:").withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.literal(" - Everything the Ascendant Crown gives").withStyle(ChatFormatting.YELLOW));
        tooltip.add(Component.literal(" - The rift: Speed, and once every five minutes, a killing blow stops time instead").withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.literal(" - The deep: Health Boost and Saturation").withStyle(ChatFormatting.LIGHT_PURPLE));
        tooltip.add(Component.literal(" - Never breaks").withStyle(ChatFormatting.YELLOW));
    }
}
