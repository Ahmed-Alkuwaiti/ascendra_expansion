package com.unstablefrontiers.block;

import com.mojang.serialization.MapCodec;
import com.unstablefrontiers.abyss.Observatory;
import com.unstablefrontiers.registry.AbyssRegistry;
import com.unstablefrontiers.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
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
 * The Rift Observatory's engine. It takes three components, each won in a different part of the observatory: the
 * Focusing Lens, the Coolant Heart and the Star Chart, in any order. With all three it wakes, the gate beside it opens
 * to the Astral Abyss and stays open, and the lift through the observatory's core starts. The state is the block's own,
 * so it is shared by everyone and survives restarts.
 */
public class RiftEngineBlock extends Block {
    public static final MapCodec<RiftEngineBlock> CODEC = simpleCodec(RiftEngineBlock::new);
    public static final BooleanProperty LENS = BooleanProperty.create("lens");
    public static final BooleanProperty HEART = BooleanProperty.create("heart");
    public static final BooleanProperty CHART = BooleanProperty.create("chart");
    public static final BooleanProperty ACTIVE = BooleanProperty.create("active");

    public RiftEngineBlock(Properties p) {
        super(p);
        registerDefaultState(stateDefinition.any().setValue(LENS, false).setValue(HEART, false).setValue(CHART, false).setValue(ACTIVE, false));
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
        b.add(LENS, HEART, CHART, ACTIVE);
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand,
                                              BlockHitResult hit) {
        BooleanProperty slot = slotFor(stack.getItem());
        if (slot == null || state.getValue(ACTIVE)) {
            return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
        }
        if (state.getValue(slot)) {
            if (!level.isClientSide) {
                player.displayClientMessage(Component.translatable("message.unstable_frontiers.engine_has").withStyle(ChatFormatting.GRAY), true);
            }
            return ItemInteractionResult.sidedSuccess(level.isClientSide);
        }
        if (!level.isClientSide) {
            if (!player.getAbilities().instabuild) {
                stack.shrink(1);
            }
            BlockState next = state.setValue(slot, true);
            level.setBlockAndUpdate(pos, next);
            level.playSound(null, pos, SoundEvents.RESPAWN_ANCHOR_CHARGE, SoundSource.BLOCKS, 1.5F, 0.7F);
            if (next.getValue(LENS) && next.getValue(HEART) && next.getValue(CHART)) {
                level.setBlockAndUpdate(pos, next.setValue(ACTIVE, true));
                level.playSound(null, pos, ModSounds.RIFT_OPEN.get(), SoundSource.BLOCKS, 4.0F, 1.0F);
                if (level instanceof ServerLevel sl && player instanceof ServerPlayer sp) {
                    Observatory.restore(sl, pos, sp);
                }
            } else {
                player.displayClientMessage(Component.translatable("message.unstable_frontiers.engine_progress", count(next))
                        .withStyle(ChatFormatting.AQUA), true);
            }
        }
        return ItemInteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!level.isClientSide) {
            player.displayClientMessage(state.getValue(ACTIVE)
                    ? Component.translatable("message.unstable_frontiers.engine_active").withStyle(ChatFormatting.AQUA)
                    : Component.translatable("message.unstable_frontiers.engine_needs", missing(state)).withStyle(ChatFormatting.GOLD), false);
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    private static int count(BlockState s) {
        return (s.getValue(LENS) ? 1 : 0) + (s.getValue(HEART) ? 1 : 0) + (s.getValue(CHART) ? 1 : 0);
    }

    private static Component missing(BlockState s) {
        StringBuilder sb = new StringBuilder();
        Item[] items = {AbyssRegistry.FOCUSING_LENS.get(), AbyssRegistry.COOLANT_HEART.get(), AbyssRegistry.STAR_CHART.get()};
        BooleanProperty[] props = {LENS, HEART, CHART};
        Component out = Component.empty();
        boolean first = true;
        for (int i = 0; i < 3; i++) {
            if (!s.getValue(props[i])) {
                if (!first) {
                    out = out.copy().append(", ");
                }
                out = out.copy().append(items[i].getDescription());
                first = false;
            }
        }
        return out;
    }

    private static BooleanProperty slotFor(Item item) {
        if (item == AbyssRegistry.FOCUSING_LENS.get()) {
            return LENS;
        }
        if (item == AbyssRegistry.COOLANT_HEART.get()) {
            return HEART;
        }
        if (item == AbyssRegistry.STAR_CHART.get()) {
            return CHART;
        }
        return null;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource r) {
        int n = count(state) + (state.getValue(ACTIVE) ? 4 : 0);
        for (int i = 0; i < n; i++) {
            level.addParticle(state.getValue(ACTIVE) ? ParticleTypes.END_ROD : ParticleTypes.ELECTRIC_SPARK,
                    pos.getX() + 0.5D + (r.nextDouble() - 0.5D) * 1.4D, pos.getY() + 1.1D, pos.getZ() + 0.5D + (r.nextDouble() - 0.5D) * 1.4D,
                    0, 0.05D, 0);
        }
    }
}
