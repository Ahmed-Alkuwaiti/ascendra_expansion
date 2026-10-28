package com.unstablefrontiers.item;

import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

/** A landmark's trophy. Its uses are crafting ones (see the recipes), told in its tooltip: lang keys item.&lt;id&gt;.tip0..tipN. */
public class TrophyItem extends Item {
    private final int lines;

    public TrophyItem(Properties properties, int lines) {
        super(properties);
        this.lines = lines;
    }

    @Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        for (int i = 0; i < lines; i++) {
            tooltip.add(Component.translatable(getDescriptionId() + ".tip" + i).withStyle(i == 0 ? ChatFormatting.GOLD : ChatFormatting.GRAY));
        }
    }
}
