package com.aurelia.block;

import com.aurelia.world.Realm;
import com.aurelia.world.Story;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;

/** Wakes a citadel's portal once every puzzle node of one type in range is filled. */
public final class PuzzleLogic {
    private static final int RANGE_XZ = 36;
    private static final int RANGE_Y = 24;

    private PuzzleLogic() {}

    public static void check(ServerLevel level, BlockPos origin, Block nodeBlock) {
        int total = 0;
        int filled = 0;
        List<BlockPos> portals = new ArrayList<>();
        for (BlockPos p : BlockPos.betweenClosed(origin.offset(-RANGE_XZ, -RANGE_Y, -RANGE_XZ),
                origin.offset(RANGE_XZ, RANGE_Y, RANGE_XZ))) {
            if (!level.hasChunkAt(p)) {
                continue;
            }
            BlockState s = level.getBlockState(p);
            if (s.is(nodeBlock)) {
                total++;
                if (s.getValue(PuzzleNodeBlock.FILLED)) {
                    filled++;
                }
            } else if (s.getBlock() instanceof WaygateBlock && !s.getValue(WaygateBlock.ACTIVE)) {
                portals.add(p.immutable());
            }
        }
        if (total == 0 || filled < total || portals.isEmpty()) {
            return;
        }
        for (BlockPos portal : portals) {
            BlockState s = level.getBlockState(portal);
            level.setBlock(portal, s.setValue(WaygateBlock.ACTIVE, true), 3);
            Realm realm = s.getValue(WaygateBlock.REALM);
            level.sendParticles(ParticleTypes.REVERSE_PORTAL, portal.getX() + 0.5, portal.getY() + 1.0,
                    portal.getZ() + 0.5, 120, 0.8, 1.2, 0.8, 0.3);
            level.playSound(null, portal, SoundEvents.END_PORTAL_SPAWN, SoundSource.BLOCKS, 2.0f, 1.0f);
            for (ServerPlayer player : level.getEntitiesOfClass(ServerPlayer.class,
                    new AABB(portal).inflate(RANGE_XZ))) {
                Story.title(player, "The portal awakens", "The way to " + realm.title + " is open.", realm.color);
            }
        }
    }
}
