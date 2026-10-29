package com.unstablefrontiers.item;

import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * The Blinkstone, grown in the Starwell: use it to step up to {@link #RANGE} blocks the way you look, through the air, to
 * the farthest spot along that line where you fit. It never puts you inside a block; while you are falling it can carry
 * you back to an island's edge. Three seconds between steps; 240 uses, repaired with Starmetal.
 */
public class BlinkstoneItem extends Item {
    public static final double RANGE = 10.0D;
    private static final int COOLDOWN = 60;

    public BlinkstoneItem(Properties p) {
        super(p);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level instanceof ServerLevel sl && player instanceof ServerPlayer sp) {
            Vec3 to = target(sl, sp);
            if (to == null) {
                sp.displayClientMessage(Component.translatable("message.unstable_frontiers.blink_blocked").withStyle(ChatFormatting.GRAY), true);
                return InteractionResultHolder.fail(stack);
            }
            Vec3 from = sp.position();
            sl.sendParticles(ParticleTypes.REVERSE_PORTAL, from.x, from.y + 1, from.z, 20, 0.3, 0.6, 0.3, 0.05);
            sp.teleportTo(to.x, to.y, to.z);
            sp.setDeltaMovement(sp.getDeltaMovement().multiply(0.3D, 0, 0.3D));
            sp.hurtMarked = true;
            sp.fallDistance = 0;
            sl.sendParticles(ParticleTypes.END_ROD, to.x, to.y + 1, to.z, 16, 0.3, 0.6, 0.3, 0.05);
            sl.playSound(null, BlockPos.containing(to), SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.PLAYERS, 1.2F, 1.6F);
            player.getCooldowns().addCooldown(this, COOLDOWN);
            stack.hurtAndBreak(1, sp, LivingEntity.getSlotForHand(hand));
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    /** The farthest point along the look line (up to RANGE) where the player's body fits, or null. */
    static Vec3 target(ServerLevel level, ServerPlayer p) {
        Vec3 eye = p.getEyePosition();
        Vec3 look = p.getLookAngle();
        BlockHitResult hit = level.clip(new ClipContext(eye, eye.add(look.scale(RANGE)), ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, p));
        double max = hit.getType() == HitResult.Type.BLOCK ? hit.getLocation().distanceTo(eye) - 0.6D : RANGE;
        for (double d = max; d >= 2.0D; d -= 0.5D) {
            Vec3 eyeAt = eye.add(look.scale(d));
            Vec3 feet = eyeAt.subtract(0, p.getEyeHeight(), 0);
            // prefer landing on a floor just below, if one is within reach
            for (int drop = 0; drop <= 3; drop++) {
                Vec3 f = feet.subtract(0, drop, 0);
                if (fits(level, p, f) && (drop == 3 || !fits(level, p, f.subtract(0, 1, 0)))) {
                    return fits(level, p, f) ? f : feet;
                }
            }
            if (fits(level, p, feet)) {
                return feet;
            }
        }
        return null;
    }

    private static boolean fits(ServerLevel level, ServerPlayer p, Vec3 feet) {
        return level.noCollision(p, p.getDimensions(p.getPose()).makeBoundingBox(feet));
    }

    @Override
    public boolean isValidRepairItem(ItemStack stack, ItemStack repair) {
        return repair.is(com.unstablefrontiers.registry.AbyssRegistry.STARMETAL_INGOT.get());
    }

    @Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.unstable_frontiers.blinkstone.tip0").withStyle(ChatFormatting.AQUA));
        tooltip.add(Component.translatable("item.unstable_frontiers.blinkstone.tip1").withStyle(ChatFormatting.GRAY));
    }
}
