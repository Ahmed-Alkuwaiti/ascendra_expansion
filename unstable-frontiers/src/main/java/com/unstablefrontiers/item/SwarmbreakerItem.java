package com.unstablefrontiers.item;

import com.unstablefrontiers.registry.ModItems;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * The brood-breaker, forged from a Hive Heart: a glaive (Better Combat's glaive moves when that mod is present) that hits
 * like a netherite sword (8). It deals 50% more to insects; its Pounce leaps you forward and up, and the landing's
 * shockwave hurts and throws back everything around you, staggers insects and smashes egg clutches. Fall damage is
 * cancelled for that landing. Its role is crowd and nest control in the frontier's brood fights, not raw damage: it
 * does not out-damage Antarchy's Ultimate or Big Bertha weapons. Repaired with Cage Trophies.
 */
public class SwarmbreakerItem extends SwordItem {
    public static final int POUNCE_COOLDOWN = 160;
    public static final String LEAP = "unstable_frontiers.pounce";

    public static final Tier TIER = new Tier() {
        @Override public int getUses() { return 1800; }
        @Override public float getSpeed() { return 9.0F; }
        @Override public float getAttackDamageBonus() { return 4.0F; }
        @Override public TagKey<Block> getIncorrectBlocksForDrops() { return BlockTags.INCORRECT_FOR_NETHERITE_TOOL; }
        @Override public int getEnchantmentValue() { return 15; }
        @Override public Ingredient getRepairIngredient() { return Ingredient.of(ModItems.CAGE_TROPHY.get()); }
    };

    public SwarmbreakerItem(Properties properties) {
        super(TIER, properties);
    }

    /** 1 base + 4 tier + 3 = 8 attack damage, like a netherite sword; slightly slower swing. */
    public static ItemAttributeModifiers attributes() {
        return SwordItem.createAttributes(TIER, 3, -2.5F);
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
            stack.hurtAndBreak(2, player, LivingEntity.getSlotForHand(hand));
            level.playSound(null, player.blockPosition(), SoundEvents.PHANTOM_FLAP, SoundSource.PLAYERS, 1.0F, 0.8F);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    @Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.unstable_frontiers.swarmbreaker.tip0").withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable("item.unstable_frontiers.swarmbreaker.tip1").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("item.unstable_frontiers.swarmbreaker.tip2").withStyle(ChatFormatting.GRAY));
    }
}
