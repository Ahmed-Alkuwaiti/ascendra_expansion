package com.aurelia.block;

import com.aurelia.world.Realm;
import com.aurelia.world.RealmTravel;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.BlockHitResult;

/**
 * A citadel's portal. Dormant until its puzzle is solved (ACTIVE), then right-click to travel to its REALM.
 * Later realms also ask you to hold the previous Warden's relic (the Drowned Expanse wants the Crown, held or worn).
 * Inside a realm, any Waygate returns you home.
 */
public class WaygateBlock extends Block {
    public static final EnumProperty<Realm> REALM = EnumProperty.create("realm", Realm.class);
    public static final BooleanProperty ACTIVE = BooleanProperty.create("active");

    public WaygateBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(REALM, Realm.GROVE).setValue(ACTIVE, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(REALM, ACTIVE);
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player,
                                 InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }
        if (!(player instanceof ServerPlayer serverPlayer)) {
            return InteractionResult.PASS;
        }
        if (Realm.of(level) != null) {
            RealmTravel.leave(serverPlayer);
            return InteractionResult.CONSUME;
        }
        if (!state.getValue(ACTIVE)) {
            player.displayClientMessage(Component.literal(
                    "The portal is dormant. Solve this citadel's trial to wake it."), true);
            return InteractionResult.CONSUME;
        }
        Realm target = state.getValue(REALM);
        Item required = target.requiredItem();
        ItemStack held = player.getItemInHand(hand);
        boolean worn = required != null && player.getItemBySlot(EquipmentSlot.HEAD).is(required);
        if (required != null && !held.is(required) && !worn) {
            player.displayClientMessage(Component.literal("The portal hums, but it will only open for someone holding a "
                    + required.getDescription().getString() + "."), true);
            return InteractionResult.CONSUME;
        }
        RealmTravel.enter(serverPlayer, target);
        return InteractionResult.CONSUME;
    }
}
