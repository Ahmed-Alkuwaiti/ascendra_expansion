package com.unstablefrontiers.travel;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.block.CageBeaconBlock;
import com.unstablefrontiers.registry.ModAttachments;
import com.unstablefrontiers.registry.ModStructures;
import com.unstablefrontiers.world.FrontierDimension;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;

/**
 * Travel to and from the frontier. Going in remembers where you left (a player attachment, kept through death); coming
 * back returns you there, or to your respawn point, or to world spawn, whichever still exists. Arrival is always on a
 * safe spot: the top solid block at that column, or a small platform if the column is water, lava or empty.
 */
public final class RiftTravel {
    private static final String RETURN = "unstable_frontiers.return";

    private RiftTravel() {}

    /** In the frontier: go home. Anywhere else: go to the frontier. */
    public static void use(ServerPlayer player) {
        if (com.unstablefrontiers.abyss.AbyssDimension.is(player.level())) {
            com.unstablefrontiers.abyss.AbyssTravel.leave(player);
        } else if (FrontierDimension.is(player.level())) {
            goHome(player);
        } else {
            goToFrontier(player);
        }
    }

    public static void goToFrontier(ServerPlayer player) {
        MinecraftServer server = player.server;
        ServerLevel frontier = server.getLevel(FrontierDimension.LEVEL);
        if (frontier == null) {
            player.displayClientMessage(Component.translatable("message.unstable_frontiers.no_frontier").withStyle(ChatFormatting.RED), false);
            return;
        }
        if (!com.unstablefrontiers.abyss.AbyssDimension.is(player.level())) {
            // (from the abyss the way home stays the one remembered when you entered the frontier)
            CompoundTag ret = new CompoundTag();
            ret.putString("Dim", player.level().dimension().location().toString());
            ret.putDouble("X", player.getX());
            ret.putDouble("Y", player.getY());
            ret.putDouble("Z", player.getZ());
            persisted(player).put(RETURN, ret);
        }

        BlockPos anchor = CageBeaconBlock.anchor(player, frontier);
        BlockPos at;
        if (anchor != null) {
            at = safeSpot(frontier, anchor.getX() + 2, anchor.getZ());
        } else {
            double border = frontier.getWorldBorder().getSize() / 2 - 64;
            int x = Mth.floor(Mth.clamp(player.getX(), -border, border));
            int z = Mth.floor(Mth.clamp(player.getZ(), -border, border));
            at = safeSpot(frontier, x, z);
        }
        teleport(player, frontier, at);
        if (anchor == null) {
            hintNearestCamp(player, frontier, at);
        }
    }

    public static void goHome(ServerPlayer player) {
        MinecraftServer server = player.server;
        CompoundTag ret = persisted(player).getCompound(RETURN);
        ServerLevel level = null;
        BlockPos at = null;
        if (ret.contains("Dim")) {
            ResourceLocation id = ResourceLocation.tryParse(ret.getString("Dim"));
            if (id != null) {
                level = server.getLevel(ResourceKey.create(Registries.DIMENSION, id));
            }
            if (level != null && !FrontierDimension.is(level) && !com.unstablefrontiers.abyss.AbyssDimension.is(level)) {
                at = BlockPos.containing(ret.getDouble("X"), ret.getDouble("Y"), ret.getDouble("Z"));
                level.getChunk(at); // load the destination before checking it
                if (!clear(level, at)) {
                    at = safeSpot(level, at.getX(), at.getZ());
                }
            }
        }
        if (at == null) {
            // No saved spot (lost, or that dimension is gone): respawn point, then world spawn.
            level = server.getLevel(player.getRespawnDimension());
            BlockPos respawn = player.getRespawnPosition();
            if (level == null || respawn == null || FrontierDimension.is(level) || com.unstablefrontiers.abyss.AbyssDimension.is(level)) {
                level = server.overworld();
                respawn = level.getSharedSpawnPos();
            }
            at = safeSpot(level, respawn.getX(), respawn.getZ());
        }
        teleport(player, level, at);
    }

    private static CompoundTag persisted(Player player) {
        return ModAttachments.of(player);
    }

    private static void teleport(ServerPlayer player, ServerLevel level, BlockPos at) {
        player.stopRiding();
        player.fallDistance = 0;
        player.teleportTo(level, at.getX() + 0.5D, at.getY(), at.getZ() + 0.5D, player.getYRot(), player.getXRot());
        level.playSound(null, at, SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 1.0F, 0.6F);
    }

    /** Feet position on safe ground in this column, building a 3x3 platform if there is none. Loads one chunk. */
    public static BlockPos safeSpot(ServerLevel level, int x, int z) {
        level.getChunk(x >> 4, z >> 4);
        int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
        BlockPos feet = new BlockPos(x, y, z);
        BlockState below = level.getBlockState(feet.below());
        boolean empty = y <= level.getMinBuildHeight() + 1;
        boolean bad = empty || !below.getFluidState().isEmpty() || below.is(Blocks.MAGMA_BLOCK) || below.is(Blocks.POWDER_SNOW)
                || below.is(Blocks.CACTUS) || below.is(Blocks.CAMPFIRE) || below.is(Blocks.SOUL_CAMPFIRE);
        if (!bad) {
            return feet;
        }
        int py = empty ? Math.max(level.getSeaLevel() + 1, 100) : Math.max(y, level.getSeaLevel() + 1);
        BlockState floor = level.dimension() == Level.NETHER ? Blocks.OBSIDIAN.defaultBlockState() : Blocks.COBBLED_DEEPSLATE.defaultBlockState();
        for (int dx = -1; dx <= 1; dx++) {
            for (int dz = -1; dz <= 1; dz++) {
                BlockPos p = new BlockPos(x + dx, py - 1, z + dz);
                if (level.getBlockState(p).canBeReplaced()) {
                    level.setBlockAndUpdate(p, floor);
                }
                for (int up = 0; up < 2; up++) {
                    BlockPos a = p.above(1 + up);
                    if (!level.getFluidState(a).isEmpty()) {
                        level.setBlockAndUpdate(a, Blocks.AIR.defaultBlockState());
                    }
                }
            }
        }
        return new BlockPos(x, py, z);
    }

    private static boolean clear(ServerLevel level, BlockPos feet) {
        return level.getBlockState(feet).getCollisionShape(level, feet).isEmpty()
                && level.getBlockState(feet.above()).getCollisionShape(level, feet.above()).isEmpty()
                && level.getFluidState(feet).isEmpty()
                && !level.getBlockState(feet.below()).getCollisionShape(level, feet.below()).isEmpty();
    }

    /** One bounded search (the same one /locate uses, limited to 20 chunks) to point newcomers at an expedition camp. */
    private static void hintNearestCamp(ServerPlayer player, ServerLevel level, BlockPos from) {
        BlockPos camp = level.findNearestMapStructure(ModStructures.CAMPS, from, 20, false);
        if (camp == null) {
            player.displayClientMessage(Component.translatable("message.unstable_frontiers.arrive_none"), false);
            return;
        }
        int dx = camp.getX() - from.getX();
        int dz = camp.getZ() - from.getZ();
        int dist = (int) Math.sqrt((double) dx * dx + (double) dz * dz);
        player.displayClientMessage(Component.translatable("message.unstable_frontiers.arrive", dist, direction(dx, dz))
                .withStyle(ChatFormatting.DARK_RED), false);
        UnstableFrontiers.LOGGER.debug("{} arrived {} blocks from a camp", player.getGameProfile().getName(), dist);
    }

    private static Component direction(int dx, int dz) {
        String[] names = {"east", "southeast", "south", "southwest", "west", "northwest", "north", "northeast"};
        double a = Math.toDegrees(Math.atan2(dz, dx));
        int i = Math.floorMod((int) Math.round(a / 45.0D), 8);
        return Component.translatable("direction.unstable_frontiers." + names[i]);
    }
}
