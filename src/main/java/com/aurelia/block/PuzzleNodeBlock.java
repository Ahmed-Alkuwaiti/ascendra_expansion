package com.aurelia.block;

import java.util.function.Supplier;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.BlockHitResult;

/**
 * One node of a citadel's portal puzzle.
 *  PLANTER (Rootbound): plant a Spore Heart.   SOCKET (Ashen): insert a Soul Sigil.
 *  PYLON (Stormwatch): charged by Storm Wisp lightning, no item.
 *  HUSH (Rimefast): fills after a player crouches on it, perfectly still, for five seconds (see ActTwoEvents).
 *  LENS (Sunscar): fills when the Sunwell's beam passes through it (see SunBeam).
 * When every node of this type near a portal is filled, the portal wakes (see PuzzleLogic).
 */
public class PuzzleNodeBlock extends Block {
    public static final BooleanProperty FILLED = BooleanProperty.create("filled");

    public enum Kind { PLANTER, PYLON, SOCKET, HUSH, LENS }

    private final Kind kind;
    private final Supplier<Item> item;

    public PuzzleNodeBlock(Properties properties, Kind kind, Supplier<Item> item) {
        super(properties);
        this.kind = kind;
        this.item = item;
        this.registerDefaultState(this.stateDefinition.any().setValue(FILLED, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FILLED);
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player,
                                 InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }
        if (state.getValue(FILLED)) {
            player.displayClientMessage(Component.literal(switch (this.kind) {
                case PLANTER -> "A spore heart is already growing here.";
                case PYLON -> "The pylon crackles with stored lightning.";
                case SOCKET -> "A soul sigil already burns in this socket.";
                case HUSH -> "The stone has heard your silence. It is satisfied.";
                case LENS -> "The lens holds the sun's light. It glows like a coal.";
            }), true);
            return InteractionResult.CONSUME;
        }
        if (this.kind == Kind.PYLON) {
            player.displayClientMessage(Component.literal(
                    "A storm pylon. It wants lightning, and the Storm Wisps here make plenty. Stand beside it."), true);
            return InteractionResult.CONSUME;
        }
        if (this.kind == Kind.HUSH) {
            player.displayClientMessage(Component.literal(
                    "A hush stone. Crouch on top of it and keep perfectly still until it has listened long enough."), true);
            return InteractionResult.CONSUME;
        }
        if (this.kind == Kind.LENS) {
            player.displayClientMessage(Component.literal(
                    "A sunglass lens. It is waiting for the Sunwell's beam. Turn the mirrors to guide the light here."), true);
            return InteractionResult.CONSUME;
        }
        ItemStack held = player.getItemInHand(hand);
        if (held.is(this.item.get())) {
            if (!player.getAbilities().instabuild) {
                held.shrink(1);
            }
            fill(level, pos, state);
            return InteractionResult.CONSUME;
        }
        player.displayClientMessage(Component.literal(this.kind == Kind.PLANTER
                ? "Plant a Spore Heart here. Sporecaps carry them." : "Insert a Soul Sigil. Soul Jailers carry them."), true);
        return InteractionResult.CONSUME;
    }

    public static void fill(Level level, BlockPos pos, BlockState state) {
        level.setBlock(pos, state.setValue(FILLED, true), 3);
        if (level instanceof ServerLevel serverLevel) {
            var particle = ParticleTypes.HAPPY_VILLAGER;
            if (state.getBlock() instanceof PuzzleNodeBlock node) {
                particle = switch (node.kind) {
                    case PLANTER -> ParticleTypes.HAPPY_VILLAGER;
                    case PYLON -> ParticleTypes.ELECTRIC_SPARK;
                    case SOCKET -> ParticleTypes.SOUL_FIRE_FLAME;
                    case HUSH -> ParticleTypes.SNOWFLAKE;
                    case LENS -> ParticleTypes.END_ROD;
                };
            }
            com.aurelia.Perf.particles(serverLevel, particle, pos.getX() + 0.5, pos.getY() + 1.2, pos.getZ() + 0.5, 20, 0.3, 0.4, 0.3, 0.05);
            serverLevel.playSound(null, pos, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.BLOCKS, 1.5f, 0.8f);
            PuzzleLogic.check(serverLevel, pos, state.getBlock());
        }
    }

    public Kind kind() {
        return this.kind;
    }

    /** Called by lightning: charges every uncharged pylon within the radius. */
    public static void chargeNearby(ServerLevel level, BlockPos center, int radius) {
        for (BlockPos p : BlockPos.betweenClosed(center.offset(-radius, -radius, -radius), center.offset(radius, radius, radius))) {
            BlockState s = level.getBlockState(p);
            if (s.getBlock() instanceof PuzzleNodeBlock node && node.kind == Kind.PYLON && !s.getValue(FILLED)) {
                fill(level, p.immutable(), s);
            }
        }
    }
}
