package com.unstablefrontiers.block;

import com.mojang.serialization.MapCodec;
import com.unstablefrontiers.abyss.EclipseEncounter;
import com.unstablefrontiers.registry.AbyssRegistry;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

/** The Hollow Crown's altar: an Eclipse Sigil set into it calls the Eclipse Leviathan up from the void. */
public class EclipseAltarBlock extends Block {
    public static final MapCodec<EclipseAltarBlock> CODEC = simpleCodec(EclipseAltarBlock::new);

    public EclipseAltarBlock(Properties p) {
        super(p);
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand,
                                              BlockHitResult hit) {
        if (!stack.is(AbyssRegistry.ECLIPSE_SIGIL.get())) {
            return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
        }
        if (level instanceof ServerLevel sl && player instanceof ServerPlayer sp && EclipseEncounter.summon(sl, pos, sp)) {
            if (!player.getAbilities().instabuild) {
                stack.shrink(1);
            }
        }
        return ItemInteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (level instanceof ServerLevel sl && player instanceof ServerPlayer sp) {
            EclipseEncounter.describe(sl, pos, sp);
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource r) {
        if (r.nextInt(2) == 0) {
            level.addParticle(ParticleTypes.SCULK_SOUL, pos.getX() + 0.5D + (r.nextDouble() - 0.5D), pos.getY() + 1.1D,
                    pos.getZ() + 0.5D + (r.nextDouble() - 0.5D), 0, 0.03D, 0);
        }
    }
}
