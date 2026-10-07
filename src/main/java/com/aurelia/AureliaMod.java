package com.aurelia;

import com.aurelia.event.ActTwoEvents;
import com.aurelia.event.CrownEvents;
import com.aurelia.registry.ModBlocks;
import com.aurelia.registry.ModEntities;
import com.aurelia.registry.ModItems;
import com.aurelia.registry.ModTabs;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

/**
 * Aurelia: The Shattered Crown
 * Six realms, six Wardens, one broken crown.
 */
@Mod(AureliaMod.MODID)
public class AureliaMod {
    public static final String MODID = "aurelia";

    public AureliaMod() {
        IEventBus bus = FMLJavaModLoadingContext.get().getModEventBus();
        ModBlocks.BLOCKS.register(bus);
        ModItems.ITEMS.register(bus);
        ModEntities.ENTITIES.register(bus);
        ModTabs.TABS.register(bus);
        bus.addListener(ModEntities::registerAttributes);
        bus.addListener(ModEntities::registerSpawns);
        MinecraftForge.EVENT_BUS.register(new CrownEvents());
        MinecraftForge.EVENT_BUS.register(new ActTwoEvents());
    }
}
