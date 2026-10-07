package com.aurelia.item;

import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

/** One of the eight Warden relics: lore, and a pointer to the Convergence Gate. */
public class RelicItem extends LoreItem {
    public RelicItem(Properties properties, String loreKey) {
        super(properties, loreKey);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        super.appendHoverText(stack, level, tooltip, flag);
        tooltip.add(Component.translatable("item.aurelia.relic.hint").withStyle(ChatFormatting.DARK_PURPLE));
    }
}
