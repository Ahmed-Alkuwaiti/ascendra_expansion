package com.unstablefrontiers.drowned;

import com.unstablefrontiers.registry.DrownedRegistry;
import com.unstablefrontiers.registry.ModSounds;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.EntityTypeTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * The Undertow: the Deepcaller's reward, a barbed harpoon on a line. In melee a heavy spear (32). Used, it casts its line up
 * to 24 blocks: a creature it strikes (not a boss) is dragged to you and held slow for two seconds; a block it strikes
 * pulls you to it. Under water or not, so it grounds frontier flyers, catches Lumen Mites and crosses Abyss gaps as well
 * as it hauls you up a trench wall. Two seconds between casts; repaired with Abyssal Pearls.
 */
public class UndertowItem extends SwordItem {
    public static final int RANGE = 24;
    private static final TagKey<EntityType<?>> BOSSES = TagKey.create(net.minecraft.core.registries.Registries.ENTITY_TYPE,
            net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("c", "bosses"));
    public static final Tier TIER = new Tier() {
        @Override public int getUses() { return 900; }
        @Override public float getSpeed() { return 8.0F; }
        @Override public float getAttackDamageBonus() { return 4.0F; }
        @Override public TagKey<Block> getIncorrectBlocksForDrops() { return BlockTags.INCORRECT_FOR_NETHERITE_TOOL; }
        @Override public int getEnchantmentValue() { return 16; }
        @Override public Ingredient getRepairIngredient() { return Ingredient.of(DrownedRegistry.ABYSSAL_PEARL.get()); }
    };

    public UndertowItem(Properties p) {
        super(TIER, p);
    }

    /** 1 base + 4 tier + 27 = 32. */
    public static ItemAttributeModifiers attributes() {
        return SwordItem.createAttributes(TIER, 27, -2.8F);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(level instanceof ServerLevel sl)) {
            return InteractionResultHolder.sidedSuccess(stack, true);
        }
        Vec3 eye = player.getEyePosition();
        Vec3 end = eye.add(player.getLookAngle().scale(RANGE));
        BlockHitResult block = level.clip(new ClipContext(eye, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player));
        Vec3 stop = block.getType() == HitResult.Type.BLOCK ? block.getLocation() : end;
        EntityHitResult ent = ProjectileUtil.getEntityHitResult(level, player, eye, stop, new AABB(eye, stop).inflate(1.0D),
                e -> e instanceof LivingEntity && e.isAlive() && !e.isSpectator() && e != player, 0.3F);
        player.getCooldowns().addCooldown(this, 40);
        if (ent != null && ent.getEntity() instanceof LivingEntity target) {
            Vec3 hitAt = target.position().add(0, target.getBbHeight() / 2, 0);
            drawLine(sl, eye.add(0, -0.3D, 0), hitAt);
            if (target.getType().is(BOSSES)) {
                player.displayClientMessage(Component.translatable("message.unstable_frontiers.undertow_boss").withStyle(ChatFormatting.GRAY), true);
            } else {
                Vec3 pull = player.position().subtract(target.position());
                double d = pull.length();
                Vec3 v = pull.normalize().scale(Math.min(2.2D, 0.35D + d * 0.11D));
                target.setDeltaMovement(v.x, v.y + 0.15D, v.z);
                target.hurtMarked = true;
                target.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.MOVEMENT_SLOWDOWN, 40, 2));
                target.hurt(level.damageSources().playerAttack(player), 4.0F);
            }
            stack.hurtAndBreak(1, player, hand == InteractionHand.MAIN_HAND ? EquipmentSlot.MAINHAND : EquipmentSlot.OFFHAND);
        } else if (block.getType() == HitResult.Type.BLOCK) {
            drawLine(sl, eye.add(0, -0.3D, 0), stop);
            Vec3 pull = stop.subtract(player.position());
            Vec3 v = pull.normalize().scale(Math.min(1.8D, 0.4D + pull.length() * 0.09D));
            player.setDeltaMovement(v.x, v.y + 0.2D, v.z);
            player.hurtMarked = true;
            player.fallDistance = 0;
            stack.hurtAndBreak(1, player, hand == InteractionHand.MAIN_HAND ? EquipmentSlot.MAINHAND : EquipmentSlot.OFFHAND);
        } else {
            drawLine(sl, eye.add(0, -0.3D, 0), stop);
        }
        level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.UNDERTOW_CAST.get(), SoundSource.PLAYERS, 1.0F, 1.0F);
        return InteractionResultHolder.sidedSuccess(stack, false);
    }

    private static void drawLine(ServerLevel level, Vec3 a, Vec3 b) {
        int n = (int) Math.min(48, a.distanceTo(b) * 2);
        for (int i = 0; i <= n; i++) {
            Vec3 q = a.lerp(b, i / (double) Math.max(1, n));
            level.sendParticles(ParticleTypes.BUBBLE_POP, q.x, q.y, q.z, 1, 0, 0, 0, 0);
        }
    }

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        // the barbs bite harder into anything that lives in water
        if (target.getType().is(EntityTypeTags.AQUATIC) || target.isInWaterOrBubble()) {
            target.invulnerableTime = 0;
            target.hurt(attacker.damageSources().generic(), 6.0F);
        }
        return super.hurtEnemy(stack, target, attacker);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        for (int i = 0; i < 3; i++) {
            tooltip.add(Component.translatable("item.unstable_frontiers.undertow.tip" + i).withStyle(i == 0 ? ChatFormatting.GOLD : ChatFormatting.GRAY));
        }
    }
}
