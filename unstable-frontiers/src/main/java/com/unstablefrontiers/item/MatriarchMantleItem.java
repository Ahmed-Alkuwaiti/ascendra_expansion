package com.unstablefrontiers.item;

import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

/**
 * The Matriarch's Mantle, cut from her wings: the Great Cage's reward, and the one that changes how you travel.
 * Carried in the hotbar or off hand:
 * <ul>
 * <li>Wingsail: falling more than a few blocks, you glide down slowly instead (hold sneak to drop normally), and you
 * take no fall damage.</li>
 * <li>Brood truce: insects (Antarchy's arthropods and the frontier's own) no longer seek you out. Strike one and it
 * answers as usual. Bosses ignore the truce.</li>
 * </ul>
 */
public class MatriarchMantleItem extends Item {
    public MatriarchMantleItem(Properties properties) {
        super(properties);
    }

    /** Whether the player carries a Mantle where it works (hotbar or off hand). */
    public static boolean carried(Player player, Item mantle) {
        if (player.getOffhandItem().is(mantle)) {
            return true;
        }
        for (int i = 0; i < 9; i++) {
            if (player.getInventory().getItem(i).is(mantle)) {
                return true;
            }
        }
        return false;
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        for (int i = 0; i < 4; i++) {
            tooltip.add(Component.translatable("item.unstable_frontiers.matriarch_mantle.tip" + i)
                    .withStyle(i == 0 ? ChatFormatting.GOLD : ChatFormatting.GRAY));
        }
    }
}
