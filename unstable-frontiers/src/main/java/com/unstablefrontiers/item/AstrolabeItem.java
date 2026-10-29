package com.unstablefrontiers.item;

import com.unstablefrontiers.abyss.AbyssDimension;
import com.unstablefrontiers.abyss.AbyssPlaces;
import com.unstablefrontiers.abyss.AbyssTerrain;
import com.unstablefrontiers.abyss.EclipseEncounter;
import com.unstablefrontiers.registry.ModStructures;
import com.unstablefrontiers.world.FrontierDimension;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

/**
 * The observatory's astrolabe. In the frontier, use it to point at the nearest Rift Observatory. In the Astral Abyss,
 * hold it and it shows, above your hotbar, the way and distance to the place it is set on; use it to step to the next
 * place (sneak and use to list them all).
 */
public class AstrolabeItem extends Item {
    private static final String TARGET = "uf_astrolabe_target";

    public AstrolabeItem(Properties p) {
        super(p);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(level instanceof ServerLevel sl) || !(player instanceof ServerPlayer sp)) {
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
        }
        player.getCooldowns().addCooldown(this, 10);
        if (AbyssDimension.is(level)) {
            if (player.isShiftKeyDown()) {
                list(sl, sp);
            } else {
                int t = (sp.getPersistentData().getInt(TARGET) + 1) % AbyssTerrain.ANCHORS.length;
                sp.getPersistentData().putInt(TARGET, t);
                show(sl, sp, true);
            }
        } else if (FrontierDimension.is(level)) {
            BlockPos at = sl.findNearestMapStructure(ModStructures.OBSERVATORY, player.blockPosition(), 64, false);
            if (at == null) {
                player.displayClientMessage(Component.translatable("message.unstable_frontiers.astrolabe_none").withStyle(ChatFormatting.GRAY), false);
            } else {
                player.displayClientMessage(Component.translatable("message.unstable_frontiers.astrolabe_observatory",
                        (int) Math.sqrt(at.distToCenterSqr(player.position())), RiftLensItem.direction((int) (at.getX() - player.getX()), (int) (at.getZ() - player.getZ())))
                        .withStyle(ChatFormatting.AQUA), false);
            }
        } else {
            player.displayClientMessage(Component.translatable("message.unstable_frontiers.astrolabe_elsewhere").withStyle(ChatFormatting.GRAY), true);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    @Override
    public void inventoryTick(ItemStack stack, Level level, Entity e, int slot, boolean selected) {
        if (selected && e instanceof ServerPlayer sp && level instanceof ServerLevel sl && AbyssDimension.is(level) && sp.tickCount % 10 == 0) {
            show(sl, sp, false);
        }
    }

    private static void show(ServerLevel level, ServerPlayer p, boolean chat) {
        AbyssTerrain.Anchor a = AbyssTerrain.ANCHORS[Math.floorMod(p.getPersistentData().getInt(TARGET), AbyssTerrain.ANCHORS.length)];
        double dx = a.x() + 0.5 - p.getX(), dz = a.z() + 0.5 - p.getZ();
        int dist = (int) Math.hypot(dx, dz);
        int dy = a.top() + 2 - (int) p.getY();
        Component line = Component.translatable("message.unstable_frontiers.astrolabe_line", Component.translatable("place.unstable_frontiers." + a.name()),
                dist, RiftLensItem.direction((int) dx, (int) dz), dy > 3 ? "▲" + dy : dy < -3 ? "▼" + (-dy) : "")
                .withStyle(ChatFormatting.AQUA);
        p.displayClientMessage(line, !chat);
        if (chat) {
            p.displayClientMessage(line, true);
        }
    }

    private static void list(ServerLevel level, ServerPlayer p) {
        AbyssPlaces places = AbyssPlaces.get(level);
        for (AbyssTerrain.Anchor a : AbyssTerrain.ANCHORS) {
            double dx = a.x() + 0.5 - p.getX(), dz = a.z() + 0.5 - p.getZ();
            String state = a == AbyssTerrain.HOLLOW_CROWN && EclipseEncounter.get(level).active() ? "awake"
                    : places.isBuilt(a) ? "seen" : "unseen";
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.astrolabe_entry",
                    Component.translatable("place.unstable_frontiers." + a.name()), (int) Math.hypot(dx, dz), RiftLensItem.direction((int) dx, (int) dz),
                    Component.translatable("place.unstable_frontiers.state." + state)).withStyle(ChatFormatting.GRAY), false);
        }
    }

    @Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        for (int i = 0; i < 3; i++) {
            tooltip.add(Component.translatable("item.unstable_frontiers.astrolabe.tip" + i).withStyle(i == 0 ? ChatFormatting.AQUA : ChatFormatting.GRAY));
        }
    }
}
