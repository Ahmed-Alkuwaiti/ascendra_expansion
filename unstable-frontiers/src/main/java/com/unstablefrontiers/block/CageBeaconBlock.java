package com.unstablefrontiers.block;

import com.unstablefrontiers.encounter.CageBeacons;
import com.unstablefrontiers.registry.ModAttachments;
import com.unstablefrontiers.world.FrontierDimension;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The Cage Beacon, made from the Great Cage's heart. Placed in the frontier it makes safe ground: frontier creatures do
 * not spawn naturally within cageBeaconRadius and landmark residents there do not return. The player who places it is
 * anchored to it: their Rift Shard brings them in beside it instead of at the matching overworld position.
 */
public class CageBeaconBlock extends Block {
    public static final String ANCHOR = "anchor";

    public CageBeaconBlock(Properties properties) {
        super(properties);
    }

    @Override
    public void setPlacedBy(Level level, BlockPos pos, BlockState state, @Nullable LivingEntity placer, ItemStack stack) {
        super.setPlacedBy(level, pos, state, placer, stack);
        if (level instanceof ServerLevel sl && FrontierDimension.is(sl)) {
            CageBeacons.get(sl).add(pos);
            if (placer instanceof Player p) {
                ModAttachments.of(p).putLong(ANCHOR, pos.asLong());
                p.displayClientMessage(Component.translatable("message.unstable_frontiers.beacon_anchored").withStyle(ChatFormatting.AQUA), false);
            }
        }
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean moved) {
        if (!state.is(newState.getBlock()) && level instanceof ServerLevel sl) {
            CageBeacons.get(sl).remove(pos);
        }
        super.onRemove(state, level, pos, newState, moved);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(3) == 0) {
            level.addParticle(ParticleTypes.END_ROD, pos.getX() + 0.5D, pos.getY() + 1.1D, pos.getZ() + 0.5D,
                    (random.nextDouble() - 0.5D) * 0.02D, 0.06D, (random.nextDouble() - 0.5D) * 0.02D);
        }
    }

    /** The beacon a player is anchored to, if it still stands. */
    @Nullable
    public static BlockPos anchor(Player p, ServerLevel frontier) {
        CompoundTag d = ModAttachments.of(p);
        if (!d.contains(ANCHOR)) {
            return null;
        }
        BlockPos pos = BlockPos.of(d.getLong(ANCHOR));
        frontier.getChunk(pos);
        return frontier.getBlockState(pos).getBlock() instanceof CageBeaconBlock ? pos : null;
    }
}
