package com.aurelia.world;

import com.aurelia.registry.ModBlocks;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
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
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

public final class RealmTravel {
    /** Radius of the circular landing pad / boss arena. */
    public static final int RADIUS = 12;

    private static final String RET_DIM = "aurelia_ret_dim";
    private static final String RET_X = "aurelia_ret_x";
    private static final String RET_Y = "aurelia_ret_y";
    private static final String RET_Z = "aurelia_ret_z";
    private static final String BOOK = "aurelia_book";
    private static final String BOOK2 = "aurelia_book2";
    private static final String BOOK3 = "aurelia_book3";

    private RealmTravel() {}

    public static void enter(ServerPlayer player, Realm realm) {
        ServerLevel dest = player.server.getLevel(realm.dimension);
        if (dest == null) {
            player.sendSystemMessage(Component.literal("The Waygate flickers, but the realm of " + realm.title
                    + " cannot be found. The dimension did not load - check latest.log.")
                    .withStyle(ChatFormatting.RED));
            return;
        }

        CompoundTag data = player.getPersistentData();
        data.putString(RET_DIM, player.level().dimension().location().toString());
        data.putDouble(RET_X, player.getX());
        data.putDouble(RET_Y, player.getY());
        data.putDouble(RET_Z, player.getZ());

        BlockPos c = center(dest, realm);
        player.fallDistance = 0;
        playDepartureEffects(player);
        player.teleportTo(dest, c.getX() + 0.5, c.getY(), c.getZ() + 6.5, 180.0f, 0.0f);
        player.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 30, 0, false, false, false));
        dest.sendParticles(ParticleTypes.REVERSE_PORTAL, c.getX() + 0.5, c.getY() + 1.0, c.getZ() + 6.5,
                150, 0.6, 1.2, 0.6, 0.25);

        Story.title(player, realm.title, realm.subtitle, realm.color);
        for (String line : realm.enterLines) {
            Story.narrate(player, line);
        }
        if (!data.getBoolean(BOOK)) {
            data.putBoolean(BOOK, true);
            ItemStack book = Story.chronicle();
            if (!player.getInventory().add(book)) {
                player.drop(book, false);
            }
            Story.narrate(player, "A worn book was waiting on the pad. You tuck it away.");
        }
        if (realm.ordinal() >= Realm.DROWNED.ordinal() && realm.ordinal() < Realm.CLOCKWORK.ordinal() && !data.getBoolean(BOOK2)) {
            data.putBoolean(BOOK2, true);
            ItemStack book = Story.secondChronicle();
            if (!player.getInventory().add(book)) {
                player.drop(book, false);
            }
            Story.narrate(player, "A second book lies on the stone, its pages swollen with seawater. Someone left it for you.");
        }
        if (realm.ordinal() >= Realm.CLOCKWORK.ordinal() && !data.getBoolean(BOOK3)) {
            data.putBoolean(BOOK3, true);
            ItemStack book = Story.riftChronicle();
            if (!player.getInventory().add(book)) {
                player.drop(book, false);
            }
            Story.narrate(player, "A third book waits for you, its pages ticking faintly.");
        }
    }

    /** Lightning, a portal burst and a roll of thunder at the gate the player is leaving. */
    private static void playDepartureEffects(ServerPlayer player) {
        if (!(player.level() instanceof ServerLevel from)) {
            return;
        }
        from.sendParticles(ParticleTypes.REVERSE_PORTAL, player.getX(), player.getY() + 1.0, player.getZ(),
                120, 0.5, 1.0, 0.5, 0.3);
        from.playSound(null, player.blockPosition(), SoundEvents.END_PORTAL_SPAWN, SoundSource.PLAYERS, 1.0f, 1.0f);
        LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(from);
        if (bolt != null) {
            bolt.moveTo(Vec3.atBottomCenterOf(player.blockPosition()));
            bolt.setVisualOnly(true);
            from.addFreshEntity(bolt);
        }
    }

    public static void leave(ServerPlayer player) {
        MinecraftServer server = player.server;
        CompoundTag data = player.getPersistentData();

        ServerLevel target = server.overworld();
        BlockPos spawn = target.getSharedSpawnPos();
        double x = spawn.getX() + 0.5;
        double z = spawn.getZ() + 0.5;
        double y = target.getHeight(Heightmap.Types.MOTION_BLOCKING, spawn.getX(), spawn.getZ());

        if (data.contains(RET_DIM)) {
            ResourceLocation rl = ResourceLocation.tryParse(data.getString(RET_DIM));
            ServerLevel saved = rl == null ? null : server.getLevel(ResourceKey.create(Registries.DIMENSION, rl));
            if (saved != null) {
                target = saved;
                x = data.getDouble(RET_X);
                y = data.getDouble(RET_Y);
                z = data.getDouble(RET_Z);
            }
        }
        player.fallDistance = 0;
        player.teleportTo(target, x, y, z, player.getYRot(), 0.0f);
        Story.narrate(player, "The Waygate lets you go. The world remembers you.");
    }

    /** Returns the standing position of the pad centre, building the pad the first time. */
    private static BlockPos center(ServerLevel level, Realm realm) {
        RealmData data = RealmData.get(level);
        if (data.center() != null) {
            return data.center();
        }
        int y = realm.fixedY;
        if (y == Integer.MIN_VALUE) {
            level.getChunk(0, 0); // force generation before reading the heightmap
            y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, 0, 0);
            y = Mth.clamp(y, level.getMinBuildHeight() + 16, level.getMaxBuildHeight() - 24);
        }
        BlockPos c = new BlockPos(0, y, 0);
        buildPad(level, realm, c);
        data.setCenter(c);
        return c;
    }

    /** c is the standing level: the pad surface is at c.y - 1. */
    private static void buildPad(ServerLevel level, Realm realm, BlockPos c) {
        BlockState air = Blocks.AIR.defaultBlockState();
        BlockState pad = realm.pad.defaultBlockState();
        BlockState foundation = realm.foundation.defaultBlockState();
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();

        for (int dx = -RADIUS; dx <= RADIUS; dx++) {
            for (int dz = -RADIUS; dz <= RADIUS; dz++) {
                if (dx * dx + dz * dz > RADIUS * RADIUS) {
                    continue;
                }
                for (int dy = 0; dy <= 14; dy++) {
                    p.set(c.getX() + dx, c.getY() + dy, c.getZ() + dz);
                    level.setBlock(p, air, 2);
                }
                for (int dy = 2; dy <= 6; dy++) {
                    p.set(c.getX() + dx, c.getY() - dy, c.getZ() + dz);
                    level.setBlock(p, foundation, 2);
                }
                p.set(c.getX() + dx, c.getY() - 1, c.getZ() + dz);
                level.setBlock(p, pad, 2);
            }
        }

        // Four corner pillars with a light on top.
        int[][] corners = {{-8, -8}, {8, -8}, {-8, 8}, {8, 8}};
        for (int[] corner : corners) {
            for (int dy = 0; dy < 4; dy++) {
                level.setBlock(c.offset(corner[0], dy, corner[1]), pad, 2);
            }
            level.setBlock(c.offset(corner[0], 4, corner[1]), realm.light.defaultBlockState(), 2);
        }

        // Altar in the middle, return Waygate near the edge.
        level.setBlock(c, ModBlocks.WARDEN_ALTAR.get().defaultBlockState(), 3);
        level.setBlock(c.offset(0, 0, 9), ModBlocks.WAYGATE.get().defaultBlockState()
                .setValue(com.aurelia.block.WaygateBlock.REALM, realm)
                .setValue(com.aurelia.block.WaygateBlock.ACTIVE, true), 3);
        ArenaBuilder.decorate(level, realm, c);
    }
}
