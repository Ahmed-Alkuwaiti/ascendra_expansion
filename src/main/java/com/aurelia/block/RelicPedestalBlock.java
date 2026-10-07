package com.aurelia.block;

import com.aurelia.registry.ModItems;
import com.aurelia.world.Realm;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * A pedestal before the Convergence Gate, waiting for one Warden's relic (REALM). Lay the right relic on it and it stays
 * (FILLED); when all eight in range are filled, the gate's Waygate wakes.
 */
public class RelicPedestalBlock extends Block {
    public static final EnumProperty<Realm> REALM = EnumProperty.create("realm", Realm.class, r -> r != Realm.LAST);
    public static final BooleanProperty FILLED = BooleanProperty.create("filled");
    private static final VoxelShape SHAPE = Shapes.or(Block.box(0, 0, 0, 16, 4, 16), Block.box(3, 4, 3, 13, 10, 13), Block.box(2, 10, 2, 14, 12.5, 14));
    private static final String[] WARDEN = {"Mossback", "the Tempest Roc", "the Hollow King", "Vorath", "the White Silence", "Kharzul",
            "Vexor", "the Bloom Mother"};

    public RelicPedestalBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(REALM, Realm.GROVE).setValue(FILLED, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(REALM, FILLED);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }
        Realm realm = state.getValue(REALM);
        Item want = ModItems.relicFor(realm);
        if (want == null) {
            return InteractionResult.PASS;
        }
        String name = want.getDescription().getString();
        if (state.getValue(FILLED)) {
            player.displayClientMessage(Component.literal("The " + name + " is home."), true);
            return InteractionResult.CONSUME;
        }
        ItemStack held = player.getItemInHand(hand);
        if (!held.is(want)) {
            player.displayClientMessage(Component.literal("This pedestal waits for the " + name + ", taken from "
                    + WARDEN[realm.ordinal()] + "."), true);
            return InteractionResult.CONSUME;
        }
        if (!player.getAbilities().instabuild) {
            held.shrink(1);
        }
        ServerLevel server = (ServerLevel) level;
        server.setBlock(pos, state.setValue(FILLED, true), 3);
        server.playSound(null, pos, SoundEvents.END_PORTAL_FRAME_FILL, SoundSource.BLOCKS, 2.0f, 0.8f);
        server.sendParticles(ParticleTypes.END_ROD, pos.getX() + 0.5, pos.getY() + 1.3, pos.getZ() + 0.5, 40, 0.3, 0.6, 0.3, 0.05);
        int filled = 0;
        int total = 0;
        for (BlockPos p : BlockPos.betweenClosed(pos.offset(-36, -8, -36), pos.offset(36, 8, 36))) {
            BlockState s = server.getBlockState(p);
            if (s.getBlock() instanceof RelicPedestalBlock) {
                total++;
                if (s.getValue(FILLED)) {
                    filled++;
                }
            }
        }
        player.displayClientMessage(Component.literal(filled + " of " + total + " relics are home.").withStyle(ChatFormatting.LIGHT_PURPLE), true);
        PuzzleLogic.check(server, pos, this, FILLED);
        return InteractionResult.CONSUME;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (state.getValue(FILLED) && random.nextInt(3) == 0) {
            level.addParticle(ParticleTypes.END_ROD, pos.getX() + 0.3 + random.nextDouble() * 0.4, pos.getY() + 1.6,
                    pos.getZ() + 0.3 + random.nextDouble() * 0.4, 0.0, 0.03, 0.0);
        }
    }
}
