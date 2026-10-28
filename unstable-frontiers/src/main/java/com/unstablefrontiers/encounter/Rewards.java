package com.unstablefrontiers.encounter;

import com.unstablefrontiers.registry.ModItems;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;

/**
 * The tower's completion reward, given by the server straight into the inventory (or at the player's feet if full).
 * Each player is rewarded once per tower, and the Swarmbreaker only on a player's first tower; both are recorded where
 * they survive restarts (the tower's saved state, and the player's persisted data, which survives death).
 */
final class Rewards {
    private static final String FIRST_TOWER = "unstable_frontiers.first_tower_done";
    private static final double REWARD_RADIUS = 96.0D;

    private Rewards() {}

    static void completeTower(ServerLevel level, TowerState s) {
        Vec3 c = s.ref.stageCentre(3);
        for (UUID id : s.participants) {
            ServerPlayer p = level.getServer().getPlayerList().getPlayer(id);
            if (p == null || p.level() != level || p.distanceToSqr(c) > REWARD_RADIUS * REWARD_RADIUS || s.rewarded.contains(id)) {
                continue;
            }
            s.rewarded.add(id);
            grant(level, p);
        }
    }

    private static void grant(ServerLevel level, ServerPlayer p) {
        int trophies = 2 + level.random.nextInt(2);
        give(p, new ItemStack(ModItems.CAGE_TROPHY.get(), trophies));
        p.giveExperiencePoints(150);
        CompoundTag persisted = p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        if (!persisted.getBoolean(FIRST_TOWER)) {
            persisted.putBoolean(FIRST_TOWER, true);
            p.getPersistentData().put(Player.PERSISTED_NBT_TAG, persisted);
            give(p, new ItemStack(ModItems.SWARMBREAKER.get()));
            p.sendSystemMessage(Component.translatable("message.unstable_frontiers.first_reward").withStyle(ChatFormatting.GOLD));
        }
        p.sendSystemMessage(Component.translatable("message.unstable_frontiers.tower_complete", trophies).withStyle(ChatFormatting.GOLD));
    }

    private static void give(ServerPlayer p, ItemStack stack) {
        if (!p.getInventory().add(stack) && !stack.isEmpty()) {
            p.drop(stack, false);
        }
    }
}
