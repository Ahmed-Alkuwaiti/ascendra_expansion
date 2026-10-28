package com.unstablefrontiers.command;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.ecology.Rivalry;
import com.unstablefrontiers.encounter.EncounterManager;
import com.unstablefrontiers.encounter.TowerData;
import com.unstablefrontiers.encounter.TowerState;
import com.unstablefrontiers.registry.ModStructures;
import com.unstablefrontiers.travel.RiftTravel;
import com.unstablefrontiers.world.FrontierDimension;
import com.unstablefrontiers.world.TowerBlueprint;
import com.unstablefrontiers.world.TowerLocator;
import com.unstablefrontiers.world.TowerRef;
import java.util.function.BiFunction;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.SectionPos;
import com.unstablefrontiers.world.CageTowerPiece;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePiecesBuilder;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.RegisterCommandsEvent;

/**
 * /frontier return is for everyone (the recovery route home, on a cooldown). Everything else needs permission level 2:
 * travel, locating a tower, and inspecting, starting, resetting or forgetting the tower at your position.
 */
public final class FrontierCommand {
    private static final String RETURN_USED = "unstable_frontiers.return_used";

    private FrontierCommand() {}

    public static void register(RegisterCommandsEvent event) {
        CommandDispatcher<CommandSourceStack> d = event.getDispatcher();
        d.register(Commands.literal("frontier")
                .then(Commands.literal("return").executes(FrontierCommand::returnHome))
                .then(Commands.literal("go").requires(s -> s.hasPermission(2)).executes(c -> {
                    RiftTravel.goToFrontier(c.getSource().getPlayerOrException());
                    return 1;
                }))
                .then(Commands.literal("locate").requires(s -> s.hasPermission(2)).executes(FrontierCommand::locate))
                .then(Commands.literal("stats").requires(s -> s.hasPermission(2)).executes(FrontierCommand::stats))
                .then(Commands.literal("tower").requires(s -> s.hasPermission(2))
                        .then(Commands.literal("build").executes(FrontierCommand::build))
                        .then(Commands.literal("info").executes(c -> withTower(c, FrontierCommand::info)))
                        .then(Commands.literal("reset").executes(c -> withTower(c, (level, s) -> {
                            EncounterManager.reset(level, TowerData.get(level), s);
                            return "reset: floors uncleared, creatures removed (rewarded players stay rewarded)";
                        })))
                        .then(Commands.literal("forget").executes(c -> withTower(c, (level, s) -> {
                            EncounterManager.abandon(level, TowerData.get(level), s);
                            TowerData.get(level).remove(s.ref.id());
                            return "forgotten: this tower starts fresh and can reward everyone again";
                        })))
                        .then(Commands.literal("start").then(Commands.argument("stage", IntegerArgumentType.integer(0, TowerBlueprint.STAGES - 1))
                                .executes(c -> {
                                    int stage = IntegerArgumentType.getInteger(c, "stage");
                                    return withTower(c, (level, s) -> {
                                        EncounterManager.start(level, TowerData.get(level), s, stage, level.getGameTime(), true);
                                        return "started stage " + stage + " (" + TowerBlueprint.STAGE_NAMES[stage] + ")";
                                    });
                                })))));
    }

    private static int returnHome(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer p = c.getSource().getPlayerOrException();
        if (!FrontierDimension.is(p.level())) {
            c.getSource().sendFailure(Component.translatable("message.unstable_frontiers.return_not_here"));
            return 0;
        }
        CompoundTag d = p.getPersistentData();
        long now = p.level().getGameTime();
        long wait = FrontierConfig.RETURN_COOLDOWN_SECONDS.get() * 20L - (now - d.getLong(RETURN_USED));
        if (d.contains(RETURN_USED) && wait > 0 && !c.getSource().hasPermission(2)) {
            c.getSource().sendFailure(Component.translatable("message.unstable_frontiers.return_cooldown", (wait + 19) / 20));
            return 0;
        }
        d.putLong(RETURN_USED, now);
        RiftTravel.goHome(p);
        return 1;
    }

    /**
     * Builds a tower at your position, registered like a generated one (so encounters, /frontier tower and /locate all see
     * it). Unlike /place structure, which builds the blocks but leaves no structure record behind.
     */
    private static int build(CommandContext<CommandSourceStack> c) {
        ServerLevel level = frontier(c);
        Structure tower = level == null ? null : TowerLocator.tower(level);
        if (tower == null) {
            return 0;
        }
        BlockPos pos = BlockPos.containing(c.getSource().getPosition());
        ChunkPos cp = new ChunkPos(pos);
        int x0 = cp.getMiddleBlockX() - TowerBlueprint.C;
        int z0 = cp.getMiddleBlockZ() - TowerBlueprint.C;
        level.getChunk(cp.x, cp.z);
        int base = Math.max(level.getHeight(Heightmap.Types.WORLD_SURFACE, cp.getMiddleBlockX(), cp.getMiddleBlockZ()), level.getSeaLevel() + 1);
        base = Math.min(base, level.getMaxBuildHeight() - TowerBlueprint.TOP - 4);
        StructurePiecesBuilder pieces = new StructurePiecesBuilder();
        pieces.addPiece(new CageTowerPiece(x0, base, z0, level.random.nextInt()));
        StructureStart start = new StructureStart(tower, cp, 0, pieces.build());
        BoundingBox bb = start.getBoundingBox();
        int cx0 = SectionPos.blockToSectionCoord(bb.minX()), cx1 = SectionPos.blockToSectionCoord(bb.maxX());
        int cz0 = SectionPos.blockToSectionCoord(bb.minZ()), cz1 = SectionPos.blockToSectionCoord(bb.maxZ());
        level.getChunk(cp.x, cp.z).setStartForStructure(tower, start);
        for (int x = cx0; x <= cx1; x++) {
            for (int z = cz0; z <= cz1; z++) {
                ChunkAccess chunk = level.getChunk(x, z);
                chunk.addReferenceForStructure(tower, cp.toLong());
                chunk.setUnsaved(true);
                BoundingBox area = new BoundingBox(x << 4, level.getMinBuildHeight(), z << 4, (x << 4) + 15, level.getMaxBuildHeight(), (z << 4) + 15);
                start.placeInChunk(level, level.structureManager(), level.getChunkSource().getGenerator(), level.getRandom(), area, new ChunkPos(x, z));
            }
        }
        // Chunks that are already live are not post-processed again, so join the bars here.
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        for (int x = bb.minX(); x <= bb.maxX(); x++) {
            for (int z = bb.minZ(); z <= bb.maxZ(); z++) {
                for (int y = bb.minY(); y <= bb.maxY(); y++) {
                    p.set(x, y, z);
                    BlockState st = level.getBlockState(p);
                    if (st.is(Blocks.IRON_BARS)) {
                        level.setBlock(p, Block.updateFromNeighbourShapes(st, level, p), 2);
                    }
                }
            }
        }
        int fb = base;
        c.getSource().sendSuccess(() -> Component.literal("Built a cage tower centred at " + (x0 + TowerBlueprint.C) + " " + fb + " " + (z0 + TowerBlueprint.C)), true);
        return 1;
    }

    private static int locate(CommandContext<CommandSourceStack> c) {
        ServerLevel level = frontier(c);
        if (level == null) {
            return 0;
        }
        BlockPos from = BlockPos.containing(c.getSource().getPosition());
        BlockPos at = level.findNearestMapStructure(ModStructures.CAGE_TOWERS, from, 64, false);
        if (at == null) {
            c.getSource().sendFailure(Component.literal("No cage tower within 64 chunks"));
            return 0;
        }
        c.getSource().sendSuccess(() -> Component.literal("Nearest cage tower: " + at.getX() + " ~ " + at.getZ()), false);
        return 1;
    }

    private static int stats(CommandContext<CommandSourceStack> c) {
        ServerLevel level = c.getSource().getServer().getLevel(FrontierDimension.LEVEL);
        if (level == null) {
            return 0;
        }
        TowerData data = TowerData.get(level);
        int completed = 0;
        for (TowerState s : data.all()) {
            if (s.completed) {
                completed++;
            }
        }
        String msg = "towers known=" + data.all().size() + " completed=" + completed + " fighting=" + data.active().size()
                + " tracked creatures=" + EncounterManager.trackedCount(data) + " rivalry fights=" + Rivalry.fightCount()
                + " | " + FrontierConfig.describe();
        c.getSource().sendSuccess(() -> Component.literal(msg), false);
        return 1;
    }

    private static String info(ServerLevel level, TowerState s) {
        StringBuilder b = new StringBuilder("tower ").append(s.ref.id()).append(" centre ")
                .append(s.ref.originX() + TowerBlueprint.C).append(' ').append(s.ref.baseY()).append(' ').append(s.ref.originZ() + TowerBlueprint.C)
                .append(" | completed=").append(s.completed).append(" cleared=[");
        for (int i = 0; i < TowerBlueprint.STAGES; i++) {
            b.append(s.isCleared(i) ? TowerBlueprint.STAGE_NAMES[i] + " " : "");
        }
        b.append("] active=").append(s.activeStage < 0 ? "none" : TowerBlueprint.STAGE_NAMES[s.activeStage])
                .append(" wave=").append(s.wave).append(" alive=").append(s.alive.size()).append(" session=").append(s.session)
                .append(" participants=").append(s.participants.size()).append(" rewarded=").append(s.rewarded.size());
        return b.toString();
    }

    private static int withTower(CommandContext<CommandSourceStack> c, BiFunction<ServerLevel, TowerState, String> action) {
        ServerLevel level = frontier(c);
        if (level == null) {
            return 0;
        }
        TowerRef ref = TowerLocator.at(level, BlockPos.containing(c.getSource().getPosition()), true);
        if (ref == null) {
            c.getSource().sendFailure(Component.literal("Not standing in a cage tower's footprint"));
            return 0;
        }
        TowerState s = TowerData.get(level).getOrCreate(ref);
        String msg = action.apply(level, s);
        c.getSource().sendSuccess(() -> Component.literal(msg), true);
        return 1;
    }

    private static ServerLevel frontier(CommandContext<CommandSourceStack> c) {
        ServerLevel level = c.getSource().getLevel();
        if (!FrontierDimension.is(level)) {
            c.getSource().sendFailure(Component.literal("Run this in the frontier (or with: execute in unstable_frontiers:frontier ...)"));
            return null;
        }
        return level;
    }
}
