package com.aurelia.world;

import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

/** Stores where the landing pad (and altar) of a realm was built. One instance per realm dimension. */
public class RealmData extends SavedData {
    private static final String NAME = "aurelia_realm";
    private BlockPos center;

    public static RealmData get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(RealmData::load, RealmData::new, NAME);
    }

    public static RealmData load(CompoundTag tag) {
        RealmData data = new RealmData();
        if (tag.contains("center")) {
            data.center = BlockPos.of(tag.getLong("center"));
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        if (center != null) {
            tag.putLong("center", center.asLong());
        }
        return tag;
    }

    @Nullable
    public BlockPos center() {
        return center;
    }

    public void setCenter(BlockPos pos) {
        this.center = pos;
        setDirty();
    }
}
