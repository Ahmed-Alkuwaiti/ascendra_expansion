package com.aurelia.item;

import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

/**
 * The Crown of Aurelia. The actual powers (flight, regeneration, night vision,
 * water breathing, resistance) are applied in {@link com.aurelia.event.CrownEvents}.
 */
public class AurelianCrownItem extends ArmorItem {

    public AurelianCrownItem(Properties properties) {
        super(AurelianArmorMaterial.AURELIAN, ArmorItem.Type.HELMET, properties);
    }

    /** The crown never breaks. */
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
        tooltip.add(Component.literal("Worn by the Sovereign. Reforged by you.")
                .withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
        tooltip.add(Component.empty());
        tooltip.add(Component.literal("While worn:").withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.literal(" - Creative-style flight").withStyle(ChatFormatting.YELLOW));
        tooltip.add(Component.literal(" - Regeneration, Resistance, Night Vision").withStyle(ChatFormatting.YELLOW));
        tooltip.add(Component.literal(" - Water Breathing").withStyle(ChatFormatting.YELLOW));
        tooltip.add(Component.literal(" - Never breaks").withStyle(ChatFormatting.YELLOW));
        tooltip.add(Component.empty());
        tooltip.add(Component.literal("Three of its settings sit empty. Somewhere under the sea, a bell answers.")
                .withStyle(ChatFormatting.DARK_AQUA, ChatFormatting.ITALIC));
    }
}
