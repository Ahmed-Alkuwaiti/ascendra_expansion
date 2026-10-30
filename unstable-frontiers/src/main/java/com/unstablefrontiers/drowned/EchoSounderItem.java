package com.unstablefrontiers.drowned;

import com.unstablefrontiers.item.RiftLensItem;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
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
import net.minecraft.world.phys.Vec3;

/**
 * The Echo Sounder. In the Drowned Expanse, held: distance, direction and depth to the charted place you have picked, in
 * the action bar. Use: pick the next charted place and send a ping, a trail of bubbles a dozen blocks toward it. Sneak-use:
 * list every place you have charted. Elsewhere it does nothing.
 */
public class EchoSounderItem extends Item {
    private static final String TARGET = "uf_sounder_target";

    public EchoSounderItem(Properties p) {
        super(p);
    }

    private static List<DrownedTerrain.Anchor> charted(ServerPlayer p) {
        List<DrownedTerrain.Anchor> out = new ArrayList<>();
        for (DrownedTerrain.Anchor a : DrownedTerrain.ANCHORS) {
            if (DrownedPlaces.charted(p, a)) {
                out.add(a);
            }
        }
        return out;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(level instanceof ServerLevel sl) || !(player instanceof ServerPlayer sp)) {
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
        }
        player.getCooldowns().addCooldown(this, 10);
        if (!DrownedDimension.is(level)) {
            player.displayClientMessage(Component.translatable("message.unstable_frontiers.sounder_elsewhere").withStyle(ChatFormatting.GRAY), true);
            return InteractionResultHolder.sidedSuccess(stack, false);
        }
        List<DrownedTerrain.Anchor> known = charted(sp);
        if (known.isEmpty()) {
            return InteractionResultHolder.sidedSuccess(stack, false);
        }
        if (player.isShiftKeyDown()) {
            for (DrownedTerrain.Anchor a : known) {
                player.displayClientMessage(line(sp, a).withStyle(ChatFormatting.GRAY), false);
            }
            return InteractionResultHolder.sidedSuccess(stack, false);
        }
        int t = (sp.getPersistentData().getInt(TARGET) + 1) % known.size();
        sp.getPersistentData().putInt(TARGET, t);
        DrownedTerrain.Anchor a = known.get(t);
        player.displayClientMessage(line(sp, a).withStyle(ChatFormatting.AQUA), false);
        // the ping: bubbles a dozen blocks along the way
        Vec3 from = sp.getEyePosition();
        Vec3 to = new Vec3(a.x() + 0.5D, a.floor() + 3, a.z() + 0.5D);
        Vec3 dir = to.subtract(from).normalize();
        for (int i = 2; i < 14; i++) {
            Vec3 q = from.add(dir.scale(i));
            sl.sendParticles(sp, ParticleTypes.BUBBLE_POP, true, q.x, q.y, q.z, 2, 0.05, 0.05, 0.05, 0.0);
        }
        return InteractionResultHolder.sidedSuccess(stack, false);
    }

    private static net.minecraft.network.chat.MutableComponent line(ServerPlayer p, DrownedTerrain.Anchor a) {
        double dx = a.x() + 0.5 - p.getX(), dz = a.z() + 0.5 - p.getZ();
        int dy = a.floor() + 2 - (int) p.getY();
        return Component.translatable("message.unstable_frontiers.sounder_line", Component.translatable("place.unstable_frontiers." + a.name()),
                (int) Math.hypot(dx, dz), RiftLensItem.direction((int) dx, (int) dz), dy > 3 ? "▲" + dy : dy < -3 ? "▼" + (-dy) : "");
    }

    @Override
    public void inventoryTick(ItemStack stack, Level level, Entity e, int slot, boolean selected) {
        if (selected && e instanceof ServerPlayer sp && DrownedDimension.is(level) && sp.tickCount % 10 == 0) {
            List<DrownedTerrain.Anchor> known = charted(sp);
            if (!known.isEmpty()) {
                DrownedTerrain.Anchor a = known.get(Math.floorMod(sp.getPersistentData().getInt(TARGET), known.size()));
                sp.displayClientMessage(line(sp, a).withStyle(ChatFormatting.AQUA), true);
            }
        }
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        for (int i = 0; i < 3; i++) {
            tooltip.add(Component.translatable("item.unstable_frontiers.echo_sounder.tip" + i).withStyle(i == 0 ? ChatFormatting.AQUA : ChatFormatting.GRAY));
        }
    }
}
