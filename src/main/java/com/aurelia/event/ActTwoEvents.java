package com.aurelia.event;

import com.aurelia.block.PuzzleNodeBlock;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.LogicalSide;

/**
 * The Rimefast Citadel's rite: a Hush Stone fills once a player has crouched on it for five seconds without moving and
 * without being hurt. Any step, standing up, or a blow restarts the count.
 */
public class ActTwoEvents {
    private static final String STONE = "aurelia_hush_stone";
    private static final String TICKS = "aurelia_hush_ticks";
    private static final String WHERE = "aurelia_hush_where";
    private static final int NEEDED = 100;
    private static final int STEP = 5;

    @SubscribeEvent
    public void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || event.side != LogicalSide.SERVER || event.player.tickCount % STEP != 0) {
            return;
        }
        Player player = event.player;
        if (!(player.level() instanceof ServerLevel level)) {
            return;
        }
        CompoundTag data = player.getPersistentData();
        BlockPos below = player.getOnPos();
        BlockState state = level.getBlockState(below);
        boolean onStone = state.getBlock() instanceof PuzzleNodeBlock node && node.kind() == PuzzleNodeBlock.Kind.HUSH
                && !state.getValue(PuzzleNodeBlock.FILLED);
        if (!onStone) {
            if (data.contains(STONE)) {
                data.remove(STONE);
                data.remove(TICKS);
                data.remove(WHERE);
            }
            return;
        }
        long stone = below.asLong();
        long where = BlockPos.containing(player.getX() * 4.0, player.getY() * 4.0, player.getZ() * 4.0).asLong();
        boolean still = player.isCrouching() && player.hurtTime == 0
                && data.getLong(STONE) == stone && data.getLong(WHERE) == where;
        int ticks = still ? data.getInt(TICKS) + STEP : 0;
        if (!still && data.getInt(TICKS) > 0) {
            player.displayClientMessage(Component.literal("The stone heard you. Begin again.").withStyle(ChatFormatting.GRAY), true);
        }
        data.putLong(STONE, stone);
        data.putLong(WHERE, where);
        data.putInt(TICKS, ticks);
        if (!player.isCrouching()) {
            player.displayClientMessage(Component.literal("A hush stone. Crouch, and be perfectly still."), true);
            return;
        }
        if (ticks >= NEEDED) {
            data.remove(STONE);
            data.remove(TICKS);
            data.remove(WHERE);
            PuzzleNodeBlock.fill(level, below, state);
            player.displayClientMessage(Component.literal("The stone has listened long enough. It is satisfied.").withStyle(ChatFormatting.AQUA), true);
        } else if (ticks > 0) {
            int pct = ticks * 100 / NEEDED;
            player.displayClientMessage(Component.literal("The stone is listening... " + pct + "%").withStyle(ChatFormatting.WHITE), true);
            level.sendParticles(ParticleTypes.SNOWFLAKE, below.getX() + 0.5, below.getY() + 1.1, below.getZ() + 0.5, 3, 0.3, 0.1, 0.3, 0.0);
        }
    }
}
