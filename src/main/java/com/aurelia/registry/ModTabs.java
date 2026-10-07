package com.aurelia.registry;

import com.aurelia.AureliaMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public class ModTabs {
    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, AureliaMod.MODID);

    public static final RegistryObject<CreativeModeTab> MAIN = TABS.register("main",
            () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.aurelia"))
                    .icon(() -> new ItemStack(ModItems.CROWN.get()))
                    .displayItems((params, out) -> {
                        out.accept(ModItems.WAYGATE.get());
                        out.accept(ModItems.WARDEN_ALTAR.get());
                        out.accept(ModItems.SPORE_PLANTER.get());
                        out.accept(ModItems.STORM_PYLON.get());
                        out.accept(ModItems.SOUL_SOCKET.get());
                        out.accept(ModItems.SPORE_HEART.get());
                        out.accept(ModItems.SOUL_SIGIL.get());
                        out.accept(ModItems.BRAMBLE_SEAL.get());
                        out.accept(ModItems.STORM_SEAL.get());
                        out.accept(ModItems.ASH_SEAL.get());
                        out.accept(ModItems.SPORE_VENT.get());
                        out.accept(ModItems.GALE_PLATE.get());
                        out.accept(ModItems.EMBER_VENT.get());
                        out.accept(ModItems.ROOT_HEART.get());
                        out.accept(ModItems.VERDANT_ORE.get());
                        out.accept(ModItems.STORMGLASS_ORE.get());
                        out.accept(ModItems.EMBERHEART_ORE.get());
                        out.accept(ModItems.VERDANT_BLOCK.get());
                        out.accept(ModItems.STORMGLASS_BLOCK.get());
                        out.accept(ModItems.EMBERHEART_BLOCK.get());
                        out.accept(ModItems.VERDANT_SHARD.get());
                        out.accept(ModItems.STORMGLASS_SHARD.get());
                        out.accept(ModItems.EMBERHEART.get());
                        out.accept(ModItems.GROVE_SHARD.get());
                        out.accept(ModItems.STORM_SHARD.get());
                        out.accept(ModItems.VOID_SHARD.get());
                        out.accept(ModItems.CROWN.get());
                        out.accept(ModItems.TITAN_EGG.get());
                        out.accept(ModItems.ROC_EGG.get());
                        out.accept(ModItems.KING_EGG.get());
                        out.accept(ModItems.ANT_EGG.get());
                        out.accept(ModItems.SENTINEL_EGG.get());
                        out.accept(ModItems.SHADE_EGG.get());
                        out.accept(ModItems.BRAMBLE_SENTINEL_EGG.get());
                        out.accept(ModItems.SPORECAP_EGG.get());
                        out.accept(ModItems.ROOTSTALKER_EGG.get());
                        out.accept(ModItems.CALCITE_SENTINEL_EGG.get());
                        out.accept(ModItems.STORM_WISP_EGG.get());
                        out.accept(ModItems.GALE_TALON_EGG.get());
                        out.accept(ModItems.ASHBOUND_KNIGHT_EGG.get());
                        out.accept(ModItems.SOUL_JAILER_EGG.get());
                        out.accept(ModItems.CINDER_HOUND_EGG.get());
                    })
                    .build());
}
