package com.aurelia.block;

import com.aurelia.entity.Unmaker;
import com.aurelia.world.Realm;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;

/**
 * One of the eight nodes on the rim of the Last Realm's arena, one per realm. When the Unmaker borrows a Warden's power the
 * matching node lights (LIT); touching it returns the power and staggers the Unmaker.
 */
public class RealmNodeBlock extends Block {
    public static final EnumProperty<Realm> REALM = EnumProperty.create("realm", Realm.class, r -> r != Realm.LAST);
    public static final BooleanProperty LIT = BooleanProperty.create("lit");

    public RealmNodeBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(REALM, Realm.GROVE).setValue(LIT, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(REALM, LIT);
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }
        Realm realm = state.getValue(REALM);
        if (!state.getValue(LIT)) {
            player.displayClientMessage(Component.literal("The " + realm.title + " node is quiet."), true);
            return InteractionResult.CONSUME;
        }
        for (Unmaker boss : level.getEntitiesOfClass(Unmaker.class, new AABB(pos).inflate(80.0))) {
            boss.onNodeTouched((ServerLevel) level, realm, player);
        }
        return InteractionResult.CONSUME;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (state.getValue(LIT)) {
            for (int i = 0; i < 3; i++) {
                level.addParticle(ParticleTypes.END_ROD, pos.getX() + random.nextDouble(), pos.getY() + 1.0 + random.nextDouble() * 2.0,
                        pos.getZ() + random.nextDouble(), 0.0, 0.08, 0.0);
            }
        }
    }
}
