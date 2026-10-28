package com.unstablefrontiers.item;

import com.unstablefrontiers.travel.RiftTravel;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

/** Use it anywhere to enter the frontier; use it in the frontier to go back. Never consumed. */
public class RiftShardItem extends Item {
    private static final int COOLDOWN = 100;

    public RiftShardItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!level.isClientSide && player instanceof ServerPlayer sp) {
            player.getCooldowns().addCooldown(this, COOLDOWN);
            RiftTravel.use(sp);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        for (int i = 0; i < 3; i++) {
            tooltip.add(Component.translatable("item.unstable_frontiers.rift_shard.tip" + i).withStyle(i == 0 ? ChatFormatting.DARK_PURPLE : ChatFormatting.GRAY));
        }
    }
}
