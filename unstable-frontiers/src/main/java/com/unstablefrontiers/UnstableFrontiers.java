package com.unstablefrontiers;

import com.mojang.logging.LogUtils;
import com.unstablefrontiers.command.FrontierCommand;
import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.debug.SmokeTest;
import com.unstablefrontiers.ecology.FrontierEvents;
import com.unstablefrontiers.item.SwarmbreakerEvents;
import com.unstablefrontiers.registry.ModAttachments;
import com.unstablefrontiers.registry.ModEntities;
import com.unstablefrontiers.registry.ModItems;
import com.unstablefrontiers.registry.ModSounds;
import com.unstablefrontiers.registry.ModStructures;
import com.unstablefrontiers.landmark.FrontierData;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.neoforge.common.NeoForge;
import org.slf4j.Logger;

@Mod(UnstableFrontiers.MODID)
public final class UnstableFrontiers {
    public static final String MODID = "unstable_frontiers";
    public static final Logger LOGGER = LogUtils.getLogger();

    public UnstableFrontiers(IEventBus modBus, ModContainer container) {
        ModItems.register(modBus);
        ModSounds.register(modBus);
        ModEntities.register(modBus);
        com.unstablefrontiers.registry.AbyssRegistry.register(modBus);
        com.unstablefrontiers.registry.DrownedRegistry.register(modBus);
        ModStructures.register(modBus);
        ModAttachments.register(modBus);
        if (FMLEnvironment.dist == Dist.CLIENT) {
            com.unstablefrontiers.client.FrontierClient.init(modBus);
        }
        container.registerConfig(ModConfig.Type.COMMON, FrontierConfig.SPEC, "unstable_frontiers-common.toml");

        IEventBus game = NeoForge.EVENT_BUS;
        game.register(new FrontierEvents());
        game.register(new FrontierData());
        game.register(new SwarmbreakerEvents());
        game.register(new com.unstablefrontiers.item.CreatureGearEvents());
        game.register(new com.unstablefrontiers.abyss.AbyssTravel());
        game.register(new com.unstablefrontiers.abyss.EclipseEncounter());
        game.register(new com.unstablefrontiers.drowned.DrownedTravel());
        game.register(new com.unstablefrontiers.drowned.DrownedBreathing());
        game.register(new com.unstablefrontiers.drowned.DeepcallerEncounter());
        game.addListener(FrontierCommand::register);
        game.register(new SmokeTest());
        game.register(new com.unstablefrontiers.debug.CreatureTrial());

        // Antarchy is a required dependency (neoforge.mods.toml), so NeoForge itself refuses to start without it and names
        // the missing mod. The version is logged so a mismatch with the targeted 2.2.9 build is visible in latest.log.
        LOGGER.info("Unstable Frontiers loading with Antarchy {}", ModList.get().getModContainerById("antarchy")
                .map(c -> c.getModInfo().getVersion().toString()).orElse("(missing)"));
    }

    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MODID, path);
    }
}
