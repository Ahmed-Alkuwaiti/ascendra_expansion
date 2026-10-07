package com.aurelia.block;

import com.aurelia.entity.AureliaBoss;
import com.aurelia.world.Realm;
import com.aurelia.world.Story;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;

/** Crouch and touch the altar to wake that realm's Warden. */
public class AltarBlock extends Block {

    public AltarBlock(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player,
                                 InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }
        Realm realm = Realm.of(level);
        if (realm == null) {
            player.displayClientMessage(
                    Component.literal("The altar is dormant. It only wakes inside the realms."), true);
            return InteractionResult.CONSUME;
        }

        if (!player.isShiftKeyDown()) {
            player.displayClientMessage(Component.literal(
                    "Crouch and touch the altar to wake the Warden of " + realm.title + "."), true);
            return InteractionResult.CONSUME;
        }

        ServerLevel serverLevel = (ServerLevel) level;
        AABB zone = new AABB(pos).inflate(80);
        if (!serverLevel.getEntitiesOfClass(AureliaBoss.class, zone).isEmpty()) {
            player.displayClientMessage(Component.literal("The Warden is already awake."), true);
            return InteractionResult.CONSUME;
        }

        AureliaBoss boss = realm.bossType().create(serverLevel);
        if (boss == null) {
            return InteractionResult.CONSUME;
        }
        boss.moveTo(pos.getX() + 0.5, pos.getY() + 1 + boss.spawnHeightOffset(), pos.getZ() - 4.5, 0.0f, 0.0f);
        boss.setArena(pos);
        serverLevel.addFreshEntity(boss);

        String name = boss.getDisplayName().getString();
        for (ServerPlayer nearby : serverLevel.getEntitiesOfClass(ServerPlayer.class, zone)) {
            Story.title(nearby, name, boss.awakenLine(), realm.color);
        }
        serverLevel.playSound(null, pos, SoundEvents.WITHER_SPAWN, SoundSource.HOSTILE, 1.0f, 0.8f);
        return InteractionResult.CONSUME;
    }
}
