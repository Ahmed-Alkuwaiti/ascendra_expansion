package com.unstablefrontiers.command;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.debug.RegistryDump;
import com.unstablefrontiers.ecology.Rivalry;
import com.unstablefrontiers.ecology.Roster;
import com.unstablefrontiers.encounter.EncounterManager;
import com.unstablefrontiers.encounter.LandmarkData;
import com.unstablefrontiers.encounter.LandmarkState;
import com.unstablefrontiers.encounter.ZoneState;
import com.unstablefrontiers.landmark.FrontierData;
import com.unstablefrontiers.landmark.LandmarkDef;
import com.unstablefrontiers.registry.ModStructures;
import com.unstablefrontiers.travel.RiftTravel;
import com.unstablefrontiers.world.FrontierDimension;
import com.unstablefrontiers.world.LandmarkPiece;
import com.unstablefrontiers.world.LandmarkStructure;
import java.util.List;
import java.util.Map;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.core.BlockPos;
import net.minecraft.core.SectionPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePiecesBuilder;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.neoforged.neoforge.event.RegisterCommandsEvent;

/**
 * /frontier return is for everyone (the recovery route home, on a cooldown). Everything else needs permission level 2:
 * travel, locating landmarks, building and driving landmarks for testing, and checking the pack integration.
 */
public final class FrontierCommand {
    private static final String RETURN_USED = "unstable_frontiers.return_used";
    private static final Map<String, TagKey<Structure>> GROUPS = Map.of("any", ModStructures.LANDMARKS, "cage", ModStructures.CAGES,
            "lair", ModStructures.LAIRS, "camp", ModStructures.CAMPS, "great_cage", ModStructures.GREAT_CAGE, "observatory", ModStructures.OBSERVATORY,
            "sunken", ModStructures.SUNKEN);

    private FrontierCommand() {}

    public static void register(RegisterCommandsEvent event) {
        CommandDispatcher<CommandSourceStack> d = event.getDispatcher();
        d.register(Commands.literal("frontier")
                .then(Commands.literal("return").executes(FrontierCommand::returnHome))
                .then(Commands.literal("go").requires(s -> s.hasPermission(2)).executes(c -> {
                    RiftTravel.goToFrontier(c.getSource().getPlayerOrException());
                    return 1;
                }))
                .then(Commands.literal("abyss").requires(s -> s.hasPermission(2)).executes(c -> {
                    com.unstablefrontiers.abyss.AbyssTravel.enter(c.getSource().getPlayerOrException(), null);
                    return 1;
                })
                        // the nearest rift engine (within 32) takes all three parts from you, as if you set them in
                        .then(Commands.literal("restore").executes(FrontierCommand::restoreEngine))
                        // the Eclipse Leviathan, called as if a sigil went into the Hollow Crown's altar; and sent back
                        .then(Commands.literal("summon").executes(c -> {
                            ServerPlayer p = c.getSource().getPlayerOrException();
                            ServerLevel abyss = p.server.getLevel(com.unstablefrontiers.abyss.AbyssDimension.LEVEL);
                            if (abyss == null) {
                                return 0;
                            }
                            com.unstablefrontiers.abyss.AbyssPlaces.build(abyss, com.unstablefrontiers.abyss.AbyssTerrain.HOLLOW_CROWN);
                            com.unstablefrontiers.abyss.EclipseEncounter.summon(abyss, BlockPos.containing(com.unstablefrontiers.abyss.EclipseEncounter.center()), p);
                            return 1;
                        }))
                        .then(Commands.literal("reset").executes(c -> {
                            ServerLevel abyss = c.getSource().getServer().getLevel(com.unstablefrontiers.abyss.AbyssDimension.LEVEL);
                            if (abyss != null) {
                                com.unstablefrontiers.abyss.EclipseEncounter.forceReset(abyss);
                            }
                            return 1;
                        })))
                .then(Commands.literal("drowned").requires(s -> s.hasPermission(2)).executes(c -> {
                    com.unstablefrontiers.drowned.DrownedTravel.enter(c.getSource().getPlayerOrException(), null);
                    return 1;
                })
                        // builds every place of the Expanse now (they otherwise build as divers come near)
                        .then(Commands.literal("build").executes(c -> {
                            ServerLevel dl = c.getSource().getServer().getLevel(com.unstablefrontiers.drowned.DrownedDimension.LEVEL);
                            if (dl == null) {
                                return 0;
                            }
                            for (com.unstablefrontiers.drowned.DrownedTerrain.Anchor a : com.unstablefrontiers.drowned.DrownedTerrain.ANCHORS) {
                                com.unstablefrontiers.drowned.DrownedPlaces.build(dl, a);
                            }
                            return 1;
                        }))
                        // the Deepcaller, called as if its bell were rung; and sent back
                        .then(Commands.literal("summon").executes(c -> {
                            ServerPlayer p = c.getSource().getPlayerOrException();
                            ServerLevel dl = p.server.getLevel(com.unstablefrontiers.drowned.DrownedDimension.LEVEL);
                            if (dl == null) {
                                return 0;
                            }
                            com.unstablefrontiers.drowned.DrownedPlaces.build(dl, com.unstablefrontiers.drowned.DrownedTerrain.VAULT);
                            return com.unstablefrontiers.drowned.DeepcallerEncounter.summon(dl, p) ? 1 : 0;
                        }))
                        .then(Commands.literal("reset").executes(c -> {
                            ServerLevel dl = c.getSource().getServer().getLevel(com.unstablefrontiers.drowned.DrownedDimension.LEVEL);
                            if (dl != null) {
                                com.unstablefrontiers.drowned.DeepcallerEncounter.forceReset(dl);
                            }
                            return 1;
                        })))
                .then(Commands.literal("locate").requires(s -> s.hasPermission(2))
                        .then(Commands.argument("group", StringArgumentType.word())
                                .suggests((c, b) -> SharedSuggestionProvider.suggest(GROUPS.keySet(), b))
                                .executes(c -> locate(c, StringArgumentType.getString(c, "group")))))
                .then(Commands.literal("stats").requires(s -> s.hasPermission(2)).executes(FrontierCommand::stats))
                .then(Commands.literal("debug").requires(s -> s.hasPermission(2))
                        .then(Commands.literal("dump").then(Commands.argument("namespace", StringArgumentType.word())
                                .executes(c -> RegistryDump.dump(c.getSource().getLevel(), StringArgumentType.getString(c, "namespace")))))
                        .then(Commands.literal("rosters").executes(FrontierCommand::rosters))
                        .then(Commands.literal("sites").executes(FrontierCommand::sites))
                        .then(Commands.literal("pose").then(Commands.argument("targets", net.minecraft.commands.arguments.EntityArgument.entities())
                                .then(Commands.argument("state", com.mojang.brigadier.arguments.IntegerArgumentType.integer(0, 15)).executes(c -> {
                                    int n = 0;
                                    for (var e : net.minecraft.commands.arguments.EntityArgument.getEntities(c, "targets")) {
                                        if (e instanceof com.unstablefrontiers.entity.AnimatedMonster m) {
                                            m.debugPose(com.mojang.brigadier.arguments.IntegerArgumentType.getInteger(c, "state"));
                                            n++;
                                        }
                                    }
                                    return n;
                                }))))
                        .then(Commands.literal("trial").then(Commands.argument("creature", StringArgumentType.word()).executes(FrontierCommand::trial))))
                .then(Commands.literal("landmark").requires(s -> s.hasPermission(2))
                        .then(Commands.literal("build").then(Commands.argument("id", StringArgumentType.string())
                                .suggests((c, b) -> SharedSuggestionProvider.suggest(
                                        FrontierData.landmarks().keySet().stream().map(ResourceLocation::getPath), b))
                                .executes(c -> build(c, StringArgumentType.getString(c, "id"), Rotation.NONE))
                                .then(Commands.argument("rotation", StringArgumentType.word())
                                        .suggests((c, b) -> SharedSuggestionProvider.suggest(List.of("none", "clockwise_90", "clockwise_180",
                                                "counterclockwise_90"), b))
                                        .executes(c -> build(c, StringArgumentType.getString(c, "id"),
                                                Rotation.valueOf(StringArgumentType.getString(c, "rotation").toUpperCase()))))))
                        .then(Commands.literal("info").executes(FrontierCommand::info))
                        .then(Commands.literal("forget").executes(FrontierCommand::forget))
                        .then(Commands.literal("zone").then(Commands.argument("zone", StringArgumentType.word())
                                .then(Commands.literal("start").executes(c -> zone(c, "start")))
                                .then(Commands.literal("clear").executes(c -> zone(c, "clear")))
                                .then(Commands.literal("reset").executes(c -> zone(c, "reset")))))));
    }

    private static int returnHome(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        ServerPlayer p = c.getSource().getPlayerOrException();
        boolean abyss = com.unstablefrontiers.abyss.AbyssDimension.is(p.level());
        boolean drowned = com.unstablefrontiers.drowned.DrownedDimension.is(p.level());
        if (!FrontierDimension.is(p.level()) && !abyss && !drowned) {
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
        if (abyss) {
            com.unstablefrontiers.abyss.AbyssTravel.leave(p);
        } else if (drowned) {
            com.unstablefrontiers.drowned.DrownedTravel.leave(p);
        } else {
            RiftTravel.goHome(p);
        }
        return 1;
    }

    /**
     * Builds a landmark centred on your chunk, registered like a generated one (a structure start with references in every
     * chunk it covers), so fights, the Rift Lens and /locate all see it. Its ground row is set at the surface there.
     */
    private static int build(CommandContext<CommandSourceStack> c, String name, Rotation rotation) {
        ServerLevel level = frontier(c);
        if (level == null) {
            return 0;
        }
        ResourceLocation id = name.contains(":") ? ResourceLocation.parse(name) : UnstableFrontiers.id(name);
        LandmarkDef def = FrontierData.landmark(id);
        if (def == null) {
            c.getSource().sendFailure(Component.literal("No landmark " + id));
            return 0;
        }
        Structure structure = null;
        for (Structure s : level.registryAccess().registryOrThrow(Registries.STRUCTURE)) {
            if (s instanceof LandmarkStructure ls && ls.template().equals(def.template())) {
                structure = s;
                break;
            }
        }
        StructureTemplate t = level.getStructureManager().get(def.template()).orElse(null);
        if (structure == null || t == null) {
            c.getSource().sendFailure(Component.literal("No structure uses template " + def.template()));
            return 0;
        }
        BlockPos pos = BlockPos.containing(c.getSource().getPosition());
        ChunkPos cp = new ChunkPos(pos);
        BoundingBox local = t.getBoundingBox(LandmarkPiece.settings(rotation), BlockPos.ZERO);
        int ox = cp.getMiddleBlockX() - (local.minX() + local.maxX()) / 2;
        int oz = cp.getMiddleBlockZ() - (local.minZ() + local.maxZ()) / 2;
        level.getChunk(cp.x, cp.z);
        int ground = level.getHeight(Heightmap.Types.OCEAN_FLOOR, cp.getMiddleBlockX(), cp.getMiddleBlockZ());
        int oy = Math.min(ground - def.ground(), level.getMaxBuildHeight() - t.getSize().getY() - 2);
        BlockPos origin = new BlockPos(ox, oy, oz);
        StructurePiecesBuilder pieces = new StructurePiecesBuilder();
        pieces.addPiece(new LandmarkPiece(level.getStructureManager(), def.template(), origin, rotation, true,
                ((LandmarkStructure) structure).clearSite() ? def.ground() : -1));
        StructureStart start = new StructureStart(structure, cp, 0, pieces.build());
        BoundingBox bb = start.getBoundingBox();
        level.getChunk(cp.x, cp.z).setStartForStructure(structure, start);
        for (int x = SectionPos.blockToSectionCoord(bb.minX()); x <= SectionPos.blockToSectionCoord(bb.maxX()); x++) {
            for (int z = SectionPos.blockToSectionCoord(bb.minZ()); z <= SectionPos.blockToSectionCoord(bb.maxZ()); z++) {
                ChunkAccess chunk = level.getChunk(x, z);
                chunk.addReferenceForStructure(structure, cp.toLong());
                chunk.setUnsaved(true);
                BoundingBox area = new BoundingBox(x << 4, level.getMinBuildHeight(), z << 4, (x << 4) + 15, level.getMaxBuildHeight(), (z << 4) + 15);
                start.placeInChunk(level, level.structureManager(), level.getChunkSource().getGenerator(), level.getRandom(), area, new ChunkPos(x, z));
            }
        }
        LandmarkData data = EncounterManager.data(level);
        data.remove(origin.asLong());
        LandmarkState s = new LandmarkState(def.id(), origin, rotation);
        data.add(s);
        BlockPos centre = s.centre(def);
        c.getSource().sendSuccess(() -> Component.literal("Built " + def.title() + " (" + def.id() + ") origin " + origin.toShortString()
                + " centre " + centre.toShortString() + " rotation " + rotation), true);
        return 1;
    }

    private static int info(CommandContext<CommandSourceStack> c) {
        ServerLevel level = frontier(c);
        LandmarkState s = level == null ? null : here(c, level);
        if (s == null) {
            return 0;
        }
        for (String line : EncounterManager.describe(level, s)) {
            c.getSource().sendSuccess(() -> Component.literal(line), false);
            UnstableFrontiers.LOGGER.info("LANDMARK {}", line);
        }
        return 1;
    }

    private static int forget(CommandContext<CommandSourceStack> c) {
        ServerLevel level = frontier(c);
        LandmarkState s = level == null ? null : here(c, level);
        if (s == null) {
            return 0;
        }
        LandmarkDef def = FrontierData.landmark(s.id);
        if (def != null) {
            for (LandmarkDef.Zone z : def.zones()) {
                if (s.zone(z).status == ZoneState.Status.ACTIVE) {
                    EncounterManager.force(level, s, z.id(), "reset", c.getSource().getPlayer());
                }
            }
        }
        EncounterManager.data(level).remove(s.key());
        c.getSource().sendSuccess(() -> Component.literal("Forgotten: " + s.id + " starts fresh (gates already opened stay open)"), true);
        return 1;
    }

    private static int zone(CommandContext<CommandSourceStack> c, String action) throws CommandSyntaxException {
        ServerLevel level = frontier(c);
        LandmarkState s = level == null ? null : here(c, level);
        if (s == null) {
            return 0;
        }
        ServerPlayer by = c.getSource().getPlayer();
        if (by == null) {
            by = level.players().isEmpty() ? null : level.players().get(0);
        }
        if (by == null && !action.equals("reset")) {
            // Fights need a player to aim at; for console runs (CI) a fake player stands in.
            by = net.neoforged.neoforge.common.util.FakePlayerFactory.getMinecraft(level);
            by.moveTo(c.getSource().getPosition());
        }
        String msg = EncounterManager.force(level, s, StringArgumentType.getString(c, "zone"), action, by);
        c.getSource().sendSuccess(() -> Component.literal(msg), true);
        UnstableFrontiers.LOGGER.info("LANDMARK zone {} {}: {}", StringArgumentType.getString(c, "zone"), action, msg);
        return 1;
    }

    private static int locate(CommandContext<CommandSourceStack> c, String group) {
        ServerLevel level = frontier(c);
        TagKey<Structure> tag = GROUPS.get(group);
        if (level == null || tag == null) {
            return 0;
        }
        BlockPos from = BlockPos.containing(c.getSource().getPosition());
        BlockPos at = level.findNearestMapStructure(tag, from, 64, false);
        if (at == null) {
            c.getSource().sendFailure(Component.literal("No " + group + " landmark within 64 chunks"));
            return 0;
        }
        c.getSource().sendSuccess(() -> Component.literal("Nearest " + group + ": " + at.getX() + " ~ " + at.getZ()), false);
        UnstableFrontiers.LOGGER.info("LOCATE {} {} {} from {} {} distance {}", group, at.getX(), at.getZ(), from.getX(), from.getZ(),
                (int) Math.sqrt(Math.pow(at.getX() - from.getX(), 2) + Math.pow(at.getZ() - from.getZ(), 2)));
        return 1;
    }

    private static int rosters(CommandContext<CommandSourceStack> c) {
        int bad = 0;
        for (Roster r : FrontierData.rosters().values()) {
            List<ResourceLocation> missing = r.missing();
            String line = "ROSTER " + r.id() + (missing.isEmpty() ? " ok" : " MISSING " + missing) + " mobs=" + r.mobs().size()
                    + " flyers=" + r.flyers().size() + (r.elite() == null ? "" : " elite=" + r.elite().type());
            UnstableFrontiers.LOGGER.info(line);
            c.getSource().sendSuccess(() -> Component.literal(line), false);
            bad += missing.isEmpty() ? 0 : 1;
        }
        for (String p : FrontierData.problems()) {
            UnstableFrontiers.LOGGER.info("ROSTER PROBLEM {}", p);
        }
        int fb = bad;
        UnstableFrontiers.LOGGER.info("ROSTER summary: {} rosters, {} unusable, {} landmarks", FrontierData.rosters().size(), bad,
                FrontierData.landmarks().size());
        c.getSource().sendSuccess(() -> Component.literal(FrontierData.rosters().size() + " rosters, " + fb + " unusable, "
                + FrontierData.landmarks().size() + " landmarks"), false);
        return bad == 0 ? 1 : 0;
    }

    /** Why candidate landmark sites were accepted or rejected since the server started (generation statistics). */
    private static int sites(CommandContext<CommandSourceStack> c) {
        LandmarkStructure.SITES.forEach((id, n) -> {
            String line = "SITES " + id.getPath() + " tried=" + n[0] + " water=" + n[1] + " slope=" + n[2] + " height=" + n[3] + " placed=" + n[4];
            UnstableFrontiers.LOGGER.info(line);
            c.getSource().sendSuccess(() -> Component.literal(line), false);
        });
        return 1;
    }

    private static int stats(CommandContext<CommandSourceStack> c) {
        ServerLevel level = c.getSource().getServer().getLevel(FrontierDimension.LEVEL);
        if (level == null) {
            return 0;
        }
        int known = 0, active = 0, tracked = 0, residents = 0;
        for (LandmarkState s : EncounterManager.data(level).all()) {
            known++;
            residents += s.residents.size();
            for (ZoneState z : s.zones) {
                active += z.status == ZoneState.Status.ACTIVE ? 1 : 0;
                tracked += z.mobs.size();
            }
        }
        String msg = "landmarks known=" + known + " fights=" + active + " tracked creatures=" + tracked + " residents=" + residents
                + " rivalry fights=" + Rivalry.fightCount() + " | " + FrontierConfig.describe();
        c.getSource().sendSuccess(() -> Component.literal(msg), false);
        UnstableFrontiers.LOGGER.info("STATS {}", msg);
        return 1;
    }

    private static int restoreEngine(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer p = c.getSource().getPlayerOrException();
        ServerLevel level = p.serverLevel();
        for (BlockPos q : BlockPos.betweenClosed(p.blockPosition().offset(-32, -16, -32), p.blockPosition().offset(32, 16, 32))) {
            if (level.getBlockState(q).is(com.unstablefrontiers.registry.AbyssRegistry.RIFT_ENGINE.get())) {
                BlockPos engine = q.immutable();
                for (net.minecraft.world.item.Item part : List.of(com.unstablefrontiers.registry.AbyssRegistry.FOCUSING_LENS.get(),
                        com.unstablefrontiers.registry.AbyssRegistry.COOLANT_HEART.get(), com.unstablefrontiers.registry.AbyssRegistry.STAR_CHART.get())) {
                    level.getBlockState(engine).useItemOn(new net.minecraft.world.item.ItemStack(part), level, p, net.minecraft.world.InteractionHand.MAIN_HAND,
                            new net.minecraft.world.phys.BlockHitResult(net.minecraft.world.phys.Vec3.atCenterOf(engine), net.minecraft.core.Direction.UP, engine, false));
                }
                c.getSource().sendSuccess(() -> Component.literal("Rift engine at " + engine.toShortString() + " restored"), true);
                return 1;
            }
        }
        c.getSource().sendFailure(Component.literal("No rift engine within 32 blocks"));
        return 0;
    }

    /** CI: plays a creature's fight against a dummy (see CreatureTrial). */
    private static int trial(CommandContext<CommandSourceStack> c) {
        ServerLevel level = frontier(c);
        if (level == null) {
            return 0;
        }
        BlockPos at = BlockPos.containing(c.getSource().getPosition());
        switch (StringArgumentType.getString(c, "creature")) {
            case "gnashback" -> com.unstablefrontiers.debug.CreatureTrial.gnashback(level, at);
            case "shrikewing" -> com.unstablefrontiers.debug.CreatureTrial.shrikewing(level, at);
            case "matriarch" -> com.unstablefrontiers.debug.CreatureTrial.matriarch(level, at);
            case "warden" -> com.unstablefrontiers.debug.AbyssTrial.warden(level, at);
            case "mite" -> com.unstablefrontiers.debug.AbyssTrial.mite(level, at);
            case "observatory" -> com.unstablefrontiers.debug.AbyssTrial.observatory(level, at);
            case "abyss" -> com.unstablefrontiers.debug.AbyssTrial.places(level);
            case "leviathan" -> com.unstablefrontiers.debug.AbyssTrial.leviathan(level);
            case "murkjaw" -> com.unstablefrontiers.debug.DrownedTrial.murkjaw(level, at);
            case "lanternray" -> com.unstablefrontiers.debug.DrownedTrial.lanternray(level, at);
            case "gate" -> com.unstablefrontiers.debug.DrownedTrial.gate(level, at);
            case "drowned" -> com.unstablefrontiers.debug.DrownedTrial.places(level);
            case "breathing" -> com.unstablefrontiers.debug.DrownedTrial.breathing(level);
            case "deepcaller" -> com.unstablefrontiers.debug.DrownedTrial.deepcaller(level);
            default -> {
                c.getSource().sendFailure(Component.literal("gnashback, shrikewing, matriarch, warden, mite, observatory, abyss, leviathan, "
                        + "murkjaw, lanternray, gate, drowned, breathing or deepcaller"));
                return 0;
            }
        }
        return 1;
    }

    private static LandmarkState here(CommandContext<CommandSourceStack> c, ServerLevel level) {
        LandmarkState s = EncounterManager.at(level, BlockPos.containing(c.getSource().getPosition()), 8);
        if (s == null) {
            c.getSource().sendFailure(Component.literal("Not standing in a landmark"));
        }
        return s;
    }

    private static ServerLevel frontier(CommandContext<CommandSourceStack> c) {
        ServerLevel level = c.getSource().getLevel();
        if (!FrontierDimension.is(level) && !com.unstablefrontiers.abyss.AbyssDimension.is(level)
                && !com.unstablefrontiers.drowned.DrownedDimension.is(level)) {
            c.getSource().sendFailure(Component.literal("Run this in the frontier (or with: execute in unstable_frontiers:frontier ...)"));
            return null;
        }
        return level;
    }
}
