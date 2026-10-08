package com.aurelia.block;

import com.aurelia.entity.Lieutenant;
import com.aurelia.entity.LieutenantKind;
import com.aurelia.registry.LieutenantEntities;
import com.aurelia.world.Realm;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;

/**
 * The seal at the heart of each lair. Crouch and touch it to call out the lieutenant who holds the lair; slot says which of the
 * realm's lieutenants that is. A lieutenant already dead can be called out again, for its spoils.
 */
public class LairSealBlock extends Block {
    public static final IntegerProperty SLOT = IntegerProperty.create("slot", 0, 2);

    public LairSealBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(SLOT, 0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(SLOT);
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }
        Realm realm = Realm.of(level);
        LieutenantKind kind = realm == null ? null : LieutenantKind.of(realm, state.getValue(SLOT));
        if (kind == null) {
            player.displayClientMessage(Component.literal("The seal is cold. Nothing answers here."), true);
            return InteractionResult.CONSUME;
        }
        String name = Component.translatable("entity.aurelia." + kind.id).getString();
        if (!player.isShiftKeyDown()) {
            player.displayClientMessage(Component.literal("Crouch and touch the seal to call out " + name + ", " + kind.title + "."), true);
            return InteractionResult.CONSUME;
        }
        ServerLevel server = (ServerLevel) level;
        if (!server.getEntitiesOfClass(Lieutenant.class, new AABB(pos).inflate(80), l -> l.kind() == kind).isEmpty()) {
            player.displayClientMessage(Component.literal(name + " is already awake."), true);
            return InteractionResult.CONSUME;
        }
        EntityType<Lieutenant> type = LieutenantEntities.type(kind);
        Lieutenant lt = type == null ? null : type.create(server);
        if (lt == null) {
            return InteractionResult.CONSUME;
        }
        lt.moveTo(pos.getX() + 0.5, pos.getY() + 1 + (kind.flying ? 4 : 0), pos.getZ() - 8.5, 0.0f, 0.0f);
        lt.finalizeSpawn(server, server.getCurrentDifficultyAt(pos), MobSpawnType.EVENT, null, null);
        lt.setLair(pos);
        server.addFreshEntity(lt);
        lt.awaken();
        server.playSound(null, pos, SoundEvents.WITHER_SPAWN, SoundSource.HOSTILE, 1.0f, 1.3f);
        return InteractionResult.CONSUME;
    }
}
