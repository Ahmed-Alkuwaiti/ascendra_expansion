package com.unstablefrontiers.item;

import com.unstablefrontiers.registry.ModItems;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.FlyingMob;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.block.Block;

/**
 * The Shrike Impaler: a spear of Shrikewing talons (Better Combat's spear moves and reach when that mod is present). It
 * deals 34, and double that to anything in the air: flyers, leaping or knocked-up creatures. A struck flyer is driven
 * toward the ground, and a Shrikewing is knocked out of the sky entirely. Its role is anti-air, the frontier's
 * missing answer to what circles overhead; it does not out-damage Antarchy's best blades on the ground.
 */
public class ShrikeImpalerItem extends SwordItem {
    public static final Tier TIER = new Tier() {
        @Override public int getUses() { return 1600; }
        @Override public float getSpeed() { return 8.0F; }
        @Override public float getAttackDamageBonus() { return 4.0F; }
        @Override public TagKey<Block> getIncorrectBlocksForDrops() { return BlockTags.INCORRECT_FOR_NETHERITE_TOOL; }
        @Override public int getEnchantmentValue() { return 15; }
        @Override public Ingredient getRepairIngredient() { return Ingredient.of(ModItems.SHRIKE_TALON.get()); }
    };

    public ShrikeImpalerItem(Properties properties) {
        super(TIER, properties);
    }

    /** 1 base + 4 tier + 29 = 34 attack damage, slower than a sword. */
    public static ItemAttributeModifiers attributes() {
        return SwordItem.createAttributes(TIER, 29, -2.8F);
    }

    /** Whether a creature counts as airborne for the Impaler. */
    public static boolean airborne(LivingEntity e) {
        return e instanceof FlyingMob || e.isNoGravity() || !e.onGround() && !e.isInWater() && !e.onClimbable() && e.fallDistance > 0.3F
                || !e.onGround() && e.getDeltaMovement().y > 0.2D;
    }

    @Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.unstable_frontiers.shrike_impaler.tip0").withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable("item.unstable_frontiers.shrike_impaler.tip1").withStyle(ChatFormatting.GRAY));
    }
}
