package com.unstablefrontiers.client;

import com.mojang.logging.LogUtils;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.Deque;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.client.server.IntegratedServer;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import org.slf4j.Logger;

/**
 * Continuous-integration only: when UF_SHOTS names a script, the client (started straight into a world) plays it to
 * take in-game screenshots of the creatures, gear and landmarks. Script lines:
 * <pre>
 *   /command          run on the integrated server as the player, with operator rights
 *   wait N            let N client ticks pass (chunks render, animations play)
 *   shot NAME         save screenshots/NAME.png
 *   gui on|off        show or hide the HUD
 *   screen inventory|none
 *   camera front|first
 *   quit
 * </pre>
 * Until the world is joined, whatever is on screen is captured every 30 seconds (boot_N.png), so a stuck start shows why.
 */
public final class ClientShots {
    private static final Logger LOGGER = LogUtils.getLogger();
    private final Deque<String> lines = new ArrayDeque<>();
    private int wait;
    private int idle;
    private int boot;

    private ClientShots(Path script) throws Exception {
        for (String l : Files.readAllLines(script)) {
            if (!l.isBlank() && !l.startsWith("#")) {
                lines.add(l.trim());
            }
        }
        LOGGER.info("SHOTS script {} with {} lines", script, lines.size());
    }

    public static void init(net.neoforged.bus.api.IEventBus gameBus) {
        String file = System.getenv("UF_SHOTS");
        if (file == null || file.isBlank()) {
            return;
        }
        try {
            gameBus.register(new ClientShots(Path.of(file)));
        } catch (Exception e) {
            LOGGER.error("SHOTS could not read {}", file, e);
        }
    }

    @SubscribeEvent
    public void onTick(ClientTickEvent.Post event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null) {
            if (++idle % 600 == 0) {
                shot(mc, "boot_" + (++boot));
                LOGGER.info("SHOTS waiting for the world; screen {}", mc.screen == null ? "none" : mc.screen.getClass().getName());
            }
            return;
        }
        if (wait > 0) {
            wait--;
            return;
        }
        String line = lines.poll();
        if (line == null) {
            return;
        }
        LOGGER.info("SHOTS> {}", line);
        try {
            if (line.startsWith("/")) {
                IntegratedServer server = mc.getSingleplayerServer();
                String cmd = line.substring(1);
                if (server != null) {
                    server.execute(() -> {
                        ServerPlayer p = server.getPlayerList().getPlayer(mc.player.getUUID());
                        if (p != null) {
                            server.getCommands().performPrefixedCommand(p.createCommandSourceStack().withPermission(4).withSuppressedOutput(), cmd);
                        }
                    });
                }
                wait = 2;
            } else if (line.startsWith("wait ")) {
                wait = Integer.parseInt(line.substring(5).trim());
            } else if (line.startsWith("shot ")) {
                shot(mc, line.substring(5).trim());
            } else if (line.equals("gui off")) {
                mc.options.hideGui = true;
            } else if (line.equals("gui on")) {
                mc.options.hideGui = false;
            } else if (line.equals("screen inventory")) {
                mc.setScreen(new InventoryScreen(mc.player));
            } else if (line.equals("screen none")) {
                mc.setScreen(null);
            } else if (line.equals("camera front")) {
                mc.options.setCameraType(net.minecraft.client.CameraType.THIRD_PERSON_FRONT);
            } else if (line.equals("camera first")) {
                mc.options.setCameraType(net.minecraft.client.CameraType.FIRST_PERSON);
            } else if (line.equals("quit")) {
                LOGGER.info("SHOTS finished");
                mc.stop();
            }
        } catch (Exception e) {
            LOGGER.error("SHOTS line failed: {}", line, e);
        }
    }

    private static void shot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, name + ".png", mc.getMainRenderTarget(), msg -> LOGGER.info("SHOTS saved {}: {}", name, msg.getString()));
    }
}
