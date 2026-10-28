package com.unstablefrontiers;

import com.mojang.logging.LogUtils;
import com.unstablefrontiers.command.FrontierCommand;
import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.debug.SmokeTest;
import com.unstablefrontiers.ecology.FrontierEvents;
import com.unstablefrontiers.item.SwarmbreakerEvents;
import com.unstablefrontiers.registry.ModAttachments;
import com.unstablefrontiers.registry.ModItems;
import com.unstablefrontiers.registry.ModStructures;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.neoforge.common.NeoForge;
import org.slf4j.Logger;

@Mod(UnstableFrontiers.MODID)
public final class UnstableFrontiers {
    public static final String MODID = "unstable_frontiers";
    public static final Logger LOGGER = LogUtils.getLogger();

    public UnstableFrontiers(IEventBus modBus, ModContainer container) {
        ModItems.register(modBus);
        ModStructures.register(modBus);
        ModAttachments.register(modBus);
        container.registerConfig(ModConfig.Type.COMMON, FrontierConfig.SPEC, "unstable_frontiers-common.toml");

        IEventBus game = NeoForge.EVENT_BUS;
        game.register(new FrontierEvents());
        game.register(new SwarmbreakerEvents());
        game.addListener(FrontierCommand::register);
        game.register(new SmokeTest());

        LOGGER.info("Unstable Frontiers loading; Antarchy {}", antarchyLoaded() ? "found, using its creatures" : "absent, using vanilla stand-ins");
    }

    public static boolean antarchyLoaded() {
        return ModList.get().isLoaded("antarchy");
    }

    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MODID, path);
    }
}
