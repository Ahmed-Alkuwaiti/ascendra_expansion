package com.unstablefrontiers.abyss;

import com.unstablefrontiers.block.AbyssGateBlock;
import com.unstablefrontiers.encounter.EncounterManager;
import com.unstablefrontiers.encounter.Feedback;
import com.unstablefrontiers.encounter.LandmarkState;
import com.unstablefrontiers.landmark.FrontierData;
import com.unstablefrontiers.landmark.LandmarkDef;
import com.unstablefrontiers.registry.AbyssRegistry;
import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;

/**
 * The Rift Observatory once the engine wakes: its gate opens (every connected gate block within reach of the engine),
 * the lift shaft through its core is unsealed, and everyone nearby is told. All of it is world state, so it stays done.
 */
public final class Observatory {
    private static final int GATE_SEARCH = 40;

    private Observatory() {}

    public static void restore(ServerLevel level, BlockPos engine, ServerPlayer by) {
        int opened = openGates(level, engine);
        LandmarkState s = EncounterManager.at(level, engine, 16);
        if (s != null) {
            LandmarkDef def = FrontierData.landmark(s.id);
            s.openGates.add("rift_engine");
            if (def != null && def.gates().containsKey("lift")) {
                EncounterManager.openGate(level, s, def, "lift");
            }
            EncounterManager.data(level).setDirty();
        }
        level.sendParticles(ParticleTypes.END_ROD, engine.getX() + 0.5D, engine.getY() + 1.5D, engine.getZ() + 0.5D, 60, 1.5D, 3.0D, 1.5D, 0.1D);
        List<ServerPlayer> near = level.getEntitiesOfClass(ServerPlayer.class, new AABB(engine).inflate(64));
        Feedback.title(near, Component.translatable("message.unstable_frontiers.rift_open_title").withStyle(ChatFormatting.AQUA),
                Component.translatable("message.unstable_frontiers.rift_open_sub").withStyle(ChatFormatting.GRAY));
        if (opened == 0) {
            by.displayClientMessage(Component.translatable("message.unstable_frontiers.rift_no_gate").withStyle(ChatFormatting.RED), false);
        }
    }

    /** Opens every gate block connected to one within reach of the engine. Returns how many. */
    static int openGates(ServerLevel level, BlockPos engine) {
        ArrayDeque<BlockPos> todo = new ArrayDeque<>();
        Set<BlockPos> seen = new HashSet<>();
        for (BlockPos p : BlockPos.betweenClosed(engine.offset(-12, -4, -12), engine.offset(12, 12, 12))) {
            if (level.getBlockState(p).is(AbyssRegistry.ABYSS_GATE.get())) {
                todo.add(p.immutable());
            }
        }
        int n = 0;
        while (!todo.isEmpty() && n < 400) {
            BlockPos p = todo.poll();
            if (!seen.add(p) || p.distManhattan(engine) > GATE_SEARCH) {
                continue;
            }
            BlockState st = level.getBlockState(p);
            if (!st.is(AbyssRegistry.ABYSS_GATE.get())) {
                continue;
            }
            if (!st.getValue(AbyssGateBlock.OPEN)) {
                level.setBlock(p, st.setValue(AbyssGateBlock.OPEN, true), 2);
                n++;
            }
            for (Direction d : Direction.values()) {
                todo.add(p.relative(d));
            }
        }
        return n;
    }
}
