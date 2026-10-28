package com.unstablefrontiers.item;

import com.unstablefrontiers.registry.ModItems;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * The tower's signature reward: a glaive that hits like a netherite sword (8) but is built for the frontier. It deals 50%
 * more to insects, and its Pounce leaps you forward and up; when you land, a shockwave hurts and throws back everything
 * around you (insects most). Fall damage is cancelled for that landing. Repaired with Cage Trophies.
 */
public class SwarmbreakerItem extends SwordItem {
    public static final int POUNCE_COOLDOWN = 160;
    public static final String LEAP = "unstable_frontiers.pounce";

    public static final Tier TIER = new Tier() {
        @Override public int getUses() { return 1800; }
        @Override public float getSpeed() { return 9.0F; }
        @Override public float getAttackDamageBonus() { return 4.0F; }
        @Override public int getLevel() { return 4; }
        @Override public int getEnchantmentValue() { return 15; }
        @Override public Ingredient getRepairIngredient() { return Ingredient.of(ModItems.CAGE_TROPHY.get()); }
    };

    public SwarmbreakerItem(Properties properties) {
        super(TIER, 3, -2.5F, properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!level.isClientSide) {
            Vec3 look = player.getLookAngle();
            Vec3 flat = new Vec3(look.x, 0, look.z).normalize();
            player.setDeltaMovement(flat.x * 1.3D, 0.75D, flat.z * 1.3D);
            player.hurtMarked = true; // send the new motion to the client
            player.getPersistentData().putLong(LEAP, level.getGameTime());
            player.getCooldowns().addCooldown(this, POUNCE_COOLDOWN);
            stack.hurtAndBreak(2, player, p -> p.broadcastBreakEvent(hand));
            level.playSound(null, player.blockPosition(), SoundEvents.PHANTOM_FLAP, SoundSource.PLAYERS, 1.0F, 0.8F);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.unstable_frontiers.swarmbreaker.tip0").withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable("item.unstable_frontiers.swarmbreaker.tip1").withStyle(ChatFormatting.GRAY));
    }
}
