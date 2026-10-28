package com.unstablefrontiers.encounter;

import com.unstablefrontiers.registry.ModAttachments;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.player.Player;

/** A player's record of conquered landmarks by kind, kept through death (used by the Rift Lens and the field guide). */
public final class Progress {
    private static final String KEY = "conquered";

    private Progress() {}

    public static void conquered(Player p, String kind) {
        CompoundTag all = ModAttachments.of(p);
        CompoundTag c = all.getCompound(KEY);
        c.putInt(kind, c.getInt(kind) + 1);
        all.put(KEY, c);
    }

    public static int count(Player p, String kind) {
        return ModAttachments.of(p).getCompound(KEY).getInt(kind);
    }
}
