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
 * The Ascendant Crown: the Crown of Aurelia with all six settings filled. Everything the Crown does, plus the gifts of
 * the outer realms. The powers are applied in {@link com.aurelia.event.CrownEvents}.
 */
public class AscendantCrownItem extends ArmorItem {

    public AscendantCrownItem(Properties properties) {
        super(AurelianArmorMaterial.ASCENDANT, ArmorItem.Type.HELMET, properties);
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
        tooltip.add(Component.literal("Six realms, six Wardens, one crown. Finished at last.")
                .withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
        tooltip.add(Component.empty());
        tooltip.add(Component.literal("While worn:").withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.literal(" - Everything the Crown of Aurelia gives").withStyle(ChatFormatting.YELLOW));
        tooltip.add(Component.literal(" - The sea: Conduit Power, Dolphin's Grace").withStyle(ChatFormatting.DARK_AQUA));
        tooltip.add(Component.literal(" - The silence: the cold cannot touch you").withStyle(ChatFormatting.WHITE));
        tooltip.add(Component.literal(" - The sand: Fire Resistance, Strength, Haste").withStyle(ChatFormatting.RED));
        tooltip.add(Component.literal(" - Never breaks").withStyle(ChatFormatting.YELLOW));
    }
}
