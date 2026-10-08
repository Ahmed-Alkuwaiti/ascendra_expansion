package com.aurelia.event;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.Deque;

import com.mojang.logging.LogUtils;
import net.minecraft.server.MinecraftServer;
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
            int result = server.getCommands().getDispatcher().execute(command, server.createCommandSourceStack());
            LOGGER.info("SMOKE ok ({}): {}", result, command);
        } catch (Exception e) {
            LOGGER.error("SMOKE FAILED: {} -> {}", command, e.getMessage());
        }
    }
}
