package com.unstablefrontiers.registry;

import com.unstablefrontiers.UnstableFrontiers;
import java.util.function.Supplier;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.player.Player;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

/** Per-player data that must survive death and restarts: the return point and whether the first tower was rewarded. */
public final class ModAttachments {
    private static final DeferredRegister<AttachmentType<?>> TYPES = DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, UnstableFrontiers.MODID);

    public static final Supplier<AttachmentType<CompoundTag>> PLAYER = TYPES.register("player",
            () -> AttachmentType.builder(() -> new CompoundTag()).serialize(CompoundTag.CODEC).copyOnDeath().build());

    private ModAttachments() {}

    /** The player's saved frontier data. Changes to the returned tag are saved with the player. */
    public static CompoundTag of(Player player) {
        return player.getData(PLAYER);
    }

    public static void register(IEventBus bus) {
        TYPES.register(bus);
    }
}
