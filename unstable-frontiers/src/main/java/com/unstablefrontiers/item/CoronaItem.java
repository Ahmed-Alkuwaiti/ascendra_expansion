package com.unstablefrontiers.item;

import com.unstablefrontiers.registry.AbyssRegistry;
import com.unstablefrontiers.registry.ModSounds;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * The Corona, the Eclipse Leviathan's reward: a glaive (Better Combat glaive moves in the pack) that stores light.
 * Every melee hit on a creature stores one charge (up to {@link #maxCharge}); use it to release them all as a beam of
 * eclipse fire along your line of sight, piercing every creature on it for 10 per charge (so a full charge is 50 at
 * tier one). Blocks stop the beam. Each Eclipse Scale set into it (sneak-use with the scale in the off hand) adds two
 * charges and four blocks of range, twice. It deals 38 in melee: below Antarchy's Ultimate weapons, above most of what
 * the frontier drops; its point is that the same weapon answers both a creature at your feet and one across a gap.
 */
public class CoronaItem extends SwordItem {
    private static final String CHARGE = "corona_charge";
    private static final String TIER = "corona_tier";
    private static final int PER_CHARGE = 10;

    public static final Tier CORONA_TIER = new Tier() {
        @Override public int getUses() { return 2400; }
        @Override public float getSpeed() { return 9.0F; }
        @Override public float getAttackDamageBonus() { return 4.0F; }
        @Override public TagKey<Block> getIncorrectBlocksForDrops() { return BlockTags.INCORRECT_FOR_NETHERITE_TOOL; }
        @Override public int getEnchantmentValue() { return 18; }
        @Override public Ingredient getRepairIngredient() { return Ingredient.of(AbyssRegistry.ECLIPSE_SCALE.get()); }
    };

    public CoronaItem(Properties p) {
        super(CORONA_TIER, p);
    }

    /** 1 base + 4 tier + 33 = 38. */
    public static ItemAttributeModifiers attributes() {
        return SwordItem.createAttributes(CORONA_TIER, 33, -2.6F);
    }

    private static CompoundTag data(ItemStack s) {
        return s.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
    }

    public static int charge(ItemStack s) {
        return data(s).getInt(CHARGE);
    }

    public static int tier(ItemStack s) {
        return data(s).getInt(TIER);
    }

    public static int maxCharge(ItemStack s) {
        return 5 + 2 * tier(s);
    }

    private static void put(ItemStack s, String key, int v) {
        CompoundTag t = data(s);
        t.putInt(key, v);
        s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
    }

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        boolean r = super.hurtEnemy(stack, target, attacker);
        int c = charge(stack);
        if (c < maxCharge(stack)) {
            put(stack, CHARGE, c + 1);
            if (attacker.level() instanceof ServerLevel sl) {
                sl.sendParticles(ParticleTypes.FLAME, target.getX(), target.getY() + target.getBbHeight() / 2, target.getZ(), 4, 0.2, 0.2, 0.2, 0.02);
            }
        }
        return r;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(level instanceof ServerLevel sl) || !(player instanceof ServerPlayer sp)) {
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
        }
        ItemStack off = player.getOffhandItem();
        if (player.isShiftKeyDown() && hand == InteractionHand.MAIN_HAND && off.is(AbyssRegistry.ECLIPSE_SCALE.get())) {
            if (tier(stack) >= 2) {
                sp.displayClientMessage(Component.translatable("message.unstable_frontiers.corona_max").withStyle(ChatFormatting.GRAY), true);
            } else {
                off.shrink(1);
                put(stack, TIER, tier(stack) + 1);
                sl.playSound(null, sp.blockPosition(), ModSounds.RIFT_OPEN.get(), SoundSource.PLAYERS, 1.0F, 1.6F);
                sp.displayClientMessage(Component.translatable("message.unstable_frontiers.corona_tier", tier(stack) + 1, maxCharge(stack))
                        .withStyle(ChatFormatting.GOLD), true);
            }
            return InteractionResultHolder.success(stack);
        }
        int c = charge(stack);
        if (c <= 0) {
            sp.displayClientMessage(Component.translatable("message.unstable_frontiers.corona_empty").withStyle(ChatFormatting.GRAY), true);
            return InteractionResultHolder.fail(stack);
        }
        double range = 20 + 4 * tier(stack);
        Vec3 eye = sp.getEyePosition();
        Vec3 end = eye.add(sp.getLookAngle().scale(range));
        BlockHitResult hit = sl.clip(new ClipContext(eye, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, sp));
        Vec3 stop = hit.getType() == HitResult.Type.BLOCK ? hit.getLocation() : end;
        int hits = 0;
        for (LivingEntity e : sl.getEntitiesOfClass(LivingEntity.class, new AABB(eye, stop).inflate(1.0D), e -> e != sp && e.isAlive())) {
            AABB box = e.getBoundingBox().inflate(0.3D);
            if (box.clip(eye, stop).isPresent() || box.contains(eye)) {
                e.hurt(sl.damageSources().playerAttack(sp), PER_CHARGE * c);
                e.igniteForSeconds(3);
                hits++;
            }
        }
        double len = eye.distanceTo(stop);
        for (int i = 0; i < (int) (len * 2); i++) {
            Vec3 q = eye.lerp(stop, i / (len * 2)).add(0, -0.2D, 0);
            sl.sendParticles(i % 3 == 0 ? ParticleTypes.FLAME : ParticleTypes.END_ROD, q.x, q.y, q.z, 1, 0, 0, 0, 0);
        }
        sl.playSound(null, sp.blockPosition(), ModSounds.LEVIATHAN_BEAM.get(), SoundSource.PLAYERS, 1.0F, 1.5F);
        put(stack, CHARGE, 0);
        sp.getCooldowns().addCooldown(this, 20);
        stack.hurtAndBreak(1, sp, LivingEntity.getSlotForHand(hand));
        return InteractionResultHolder.success(stack);
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return charge(stack) >= maxCharge(stack);
    }

    @Override
    public boolean isBarVisible(ItemStack stack) {
        return true;
    }

    @Override
    public int getBarWidth(ItemStack stack) {
        return Math.round(13.0F * charge(stack) / maxCharge(stack));
    }

    @Override
    public int getBarColor(ItemStack stack) {
        return 0xFFC24A;
    }

    @Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.unstable_frontiers.corona.tip0", charge(stack), maxCharge(stack)).withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable("item.unstable_frontiers.corona.tip1").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("item.unstable_frontiers.corona.tip2", tier(stack) + 1).withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("item.unstable_frontiers.corona.tip3", stack.getMaxDamage() - stack.getDamageValue(), stack.getMaxDamage())
                .withStyle(ChatFormatting.DARK_GRAY));
    }
}
