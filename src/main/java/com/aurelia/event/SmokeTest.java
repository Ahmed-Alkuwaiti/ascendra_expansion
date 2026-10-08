package com.aurelia.event;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.mojang.logging.LogUtils;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import org.slf4j.Logger;

/**
 * Continuous-integration only: when the AURELIA_SMOKE environment variable names a file of commands, the server runs them one
 * every two seconds once it has started, logs each with its outcome, and then stops. Without the variable this does nothing.
 */
public class SmokeTest {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Pattern PLACE = Pattern.compile("^(?:execute in (\\S+) run )?place (structure|template|jigsaw) \\S+.* (-?\\d+) (-?\\d+) (-?\\d+)$");
    private final Set<String> loaded = new HashSet<>();
    private final Deque<String> pending = new ArrayDeque<>();
    private boolean active;
    private int wait;

    @SubscribeEvent
    public void onStarted(ServerStartedEvent event) {
        String file = System.getenv("AURELIA_SMOKE");
        if (file == null || file.isBlank()) {
            return;
        }
        try {
            for (String line : Files.readAllLines(Path.of(file))) {
                if (!line.isBlank() && !line.startsWith("#")) {
                    pending.add(line.trim());
                }
            }
            active = true;
            wait = 40;
            LOGGER.info("SMOKE start: {} commands", pending.size());
        } catch (Exception e) {
            LOGGER.error("SMOKE could not read {}", file, e);
        }
    }

    @SubscribeEvent
    public void onTick(TickEvent.ServerTickEvent event) {
        if (!active || event.phase != TickEvent.Phase.END || --wait > 0) {
            return;
        }
        MinecraftServer server = event.getServer();
        String command = pending.poll();
        if (command == null) {
            active = false;
            LOGGER.info("SMOKE finished");
            server.halt(false);
            return;
        }
        wait = 40;
        LOGGER.info("SMOKE> {}", command);
        try {
            loadAround(server, command);
            int result = server.getCommands().getDispatcher().execute(command, server.createCommandSourceStack());
            LOGGER.info("SMOKE ok ({}): {}", result, command);
        } catch (Exception e) {
            LOGGER.error("SMOKE FAILED: {} -> {}", command, e.getMessage());
        }
    }

    /** "place" needs every chunk the piece covers to be loaded, so generate and force the area first (once per spot). */
    private void loadAround(MinecraftServer server, String command) {
        Matcher m = PLACE.matcher(command);
        if (!m.matches()) {
            return;
        }
        ResourceKey<Level> key = m.group(1) == null ? Level.OVERWORLD
                : ResourceKey.create(Registries.DIMENSION, new ResourceLocation(m.group(1)));
        ServerLevel level = server.getLevel(key);
        if (level == null) {
            return;
        }
        int cx = Integer.parseInt(m.group(3)) >> 4;
        int cz = Integer.parseInt(m.group(5)) >> 4;
        boolean structure = !m.group(2).equals("template");
        if (!loaded.add(key.location() + " " + cx + " " + cz + " " + structure)) {
            return;
        }
        int lo = structure ? -9 : -1;
        int hi = structure ? 9 : 14;
        long start = System.currentTimeMillis();
        for (int x = cx + lo; x <= cx + hi; x++) {
            for (int z = cz + lo; z <= cz + hi; z++) {
                level.setChunkForced(x, z, true);
                level.getChunk(x, z);
            }
        }
        LOGGER.info("SMOKE loaded {} chunks in {} ms", (hi - lo + 1) * (hi - lo + 1), System.currentTimeMillis() - start);
    }
}
