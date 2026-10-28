package com.unstablefrontiers;

import com.mojang.logging.LogUtils;
import com.unstablefrontiers.command.FrontierCommand;
import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.debug.SmokeTest;
import com.unstablefrontiers.ecology.FrontierEvents;
import com.unstablefrontiers.item.SwarmbreakerEvents;
import com.unstablefrontiers.registry.ModItems;
import com.unstablefrontiers.registry.ModStructures;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;

@Mod(UnstableFrontiers.MODID)
public final class UnstableFrontiers {
    public static final String MODID = "unstable_frontiers";
    public static final Logger LOGGER = LogUtils.getLogger();

    public UnstableFrontiers() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        ModItems.register(modBus);
        ModStructures.register(modBus);
        ModLoadingContext.get().registerConfig(ModConfig.Type.COMMON, FrontierConfig.SPEC, "unstable_frontiers-common.toml");

        IEventBus forge = MinecraftForge.EVENT_BUS;
        forge.register(new FrontierEvents());
        forge.register(new SwarmbreakerEvents());
        forge.addListener(FrontierCommand::register);
        forge.register(new SmokeTest());

        LOGGER.info("Unstable Frontiers loading; Antarchy {}", antarchyLoaded() ? "found, using its creatures" : "absent, using vanilla stand-ins");
    }

    public static boolean antarchyLoaded() {
        return ModList.get().isLoaded("antarchy");
    }

    public static ResourceLocation id(String path) {
        return new ResourceLocation(MODID, path);
    }
}
