package com.unstablefrontiers.item;

import com.unstablefrontiers.encounter.EncounterManager;
import com.unstablefrontiers.world.FrontierDimension;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.context.UseOnContext;

/** Made from the three trophies; used on the lock of the Great Cage, it opens the way in and wakes what is kept there. */
public class CagewrightKeyItem extends TrophyItem {
    public CagewrightKeyItem(Properties properties) {
        super(properties, 3);
    }

    @Override
    public InteractionResult useOn(UseOnContext ctx) {
        if (!(ctx.getLevel() instanceof ServerLevel level) || !(ctx.getPlayer() instanceof ServerPlayer player)) {
            return InteractionResult.SUCCESS;
        }
        if (FrontierDimension.is(level) && EncounterManager.useKey(level, player, ctx.getClickedPos())) {
            if (!player.getAbilities().instabuild) {
                ctx.getItemInHand().shrink(1);
            }
            return InteractionResult.CONSUME;
        }
        player.displayClientMessage(Component.translatable("message.unstable_frontiers.key_no_lock").withStyle(ChatFormatting.GRAY), true);
        return InteractionResult.FAIL;
    }
}
