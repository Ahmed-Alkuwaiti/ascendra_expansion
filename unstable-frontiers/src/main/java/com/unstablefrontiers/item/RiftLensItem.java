package com.unstablefrontiers.item;

import com.unstablefrontiers.encounter.EncounterManager;
import com.unstablefrontiers.encounter.LandmarkState;
import com.unstablefrontiers.encounter.Progress;
import com.unstablefrontiers.encounter.ZoneState;
import com.unstablefrontiers.landmark.FrontierData;
import com.unstablefrontiers.landmark.LandmarkDef;
import com.unstablefrontiers.registry.ModItems;
import com.unstablefrontiers.registry.ModSounds;
import com.unstablefrontiers.registry.ModStructures;
import com.unstablefrontiers.world.FrontierDimension;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.structure.Structure;

/**
 * The surveyor's lens, found in expedition camps. In the frontier it names the nearest cage, lair and camp, with distance,
 * direction and whether you have already conquered it. The Great Cage shows only once you carry the Cagewright's Key or
 * have conquered a cage, a rookery and a hive. Each survey uses the same bounded search /locate uses.
 */
public class RiftLensItem extends TrophyItem {
    private static final int COOLDOWN = 200;
    private static final int RADIUS = 32;

    public RiftLensItem(Properties properties) {
        super(properties, 3);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level instanceof ServerLevel sl && player instanceof ServerPlayer sp) {
            if (!FrontierDimension.is(level)) {
                sp.displayClientMessage(Component.translatable("message.unstable_frontiers.lens_elsewhere").withStyle(ChatFormatting.GRAY), true);
                return InteractionResultHolder.fail(stack);
            }
            sp.getCooldowns().addCooldown(this, COOLDOWN);
            sl.playSound(null, sp.blockPosition(), ModSounds.LENS.get(), SoundSource.PLAYERS, 1.0F, 1.0F);
            sp.displayClientMessage(Component.translatable("message.unstable_frontiers.lens_title").withStyle(ChatFormatting.DARK_PURPLE), false);
            survey(sl, sp, ModStructures.CAGES, "cages");
            survey(sl, sp, ModStructures.LAIRS, "lairs");
            survey(sl, sp, ModStructures.CAMPS, "camps");
            boolean ready = sp.getInventory().contains(new ItemStack(ModItems.CAGEWRIGHT_KEY.get()))
                    || (Progress.count(sp, "cage_tower") > 0 && Progress.count(sp, "rookery") > 0 && Progress.count(sp, "hive") > 0);
            if (ready) {
                survey(sl, sp, ModStructures.GREAT_CAGE, "great_cage");
            } else {
                sp.displayClientMessage(Component.translatable("message.unstable_frontiers.lens_clouded").withStyle(ChatFormatting.DARK_GRAY), false);
            }
            // the Rift Observatories show once the Great Cage has fallen (or to whoever already carries an astrolabe)
            if (Progress.count(sp, "great_cage") > 0 || sp.getInventory().contains(new ItemStack(com.unstablefrontiers.registry.AbyssRegistry.ASTROLABE.get()))) {
                survey(sl, sp, ModStructures.OBSERVATORY, "observatory");
            }
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    private static void survey(ServerLevel level, ServerPlayer p, TagKey<Structure> tag, String what) {
        BlockPos found = level.findNearestMapStructure(tag, p.blockPosition(), what.equals("great_cage") || what.equals("observatory") ? RADIUS * 3 : RADIUS, false);
        Component label = Component.translatable("lens.unstable_frontiers." + what);
        if (found == null) {
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.lens_none", label).withStyle(ChatFormatting.GRAY), false);
            return;
        }
        int dx = found.getX() - p.getBlockX();
        int dz = found.getZ() - p.getBlockZ();
        int dist = (int) Math.sqrt((double) dx * dx + (double) dz * dz);
        String state = "unknown";
        LandmarkState s = EncounterManager.at(level, new BlockPos(found.getX(), p.getBlockY(), found.getZ()), 64);
        LandmarkDef def = s == null ? null : FrontierData.landmark(s.id);
        if (def != null && def.finalZone() != null) {
            state = s.zone(def.finalZone()).status == ZoneState.Status.CLEARED ? "conquered" : "standing";
        }
        p.displayClientMessage(Component.translatable("message.unstable_frontiers.lens_line", label, dist, direction(dx, dz),
                Component.translatable("lens.unstable_frontiers.state." + state)).withStyle(ChatFormatting.LIGHT_PURPLE), false);
    }

    public static Component direction(int dx, int dz) {
        String[] names = {"east", "southeast", "south", "southwest", "west", "northwest", "north", "northeast"};
        double a = Math.toDegrees(Math.atan2(dz, dx));
        int i = Math.floorMod((int) Math.round(a / 45.0D), 8);
        return Component.translatable("direction.unstable_frontiers." + names[i]);
    }

    @Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        super.appendHoverText(stack, context, tooltip, flag);
    }
}
