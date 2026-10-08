package com.aurelia.world;

import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

/** Stores where the landing pad (and altar) of a realm was built, where its lieutenants' lairs stand and which are dead. One per realm dimension. */
public class RealmData extends SavedData {
    private static final String NAME = "aurelia_realm";
    private BlockPos center;
    private boolean lairsBuilt;
    private int defeated;
    private final long[] seals = {Long.MIN_VALUE, Long.MIN_VALUE, Long.MIN_VALUE};
    private final long[] beacons = {Long.MIN_VALUE, Long.MIN_VALUE, Long.MIN_VALUE};

    public static RealmData get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(RealmData::load, RealmData::new, NAME);
    }

    public static RealmData load(CompoundTag tag) {
        RealmData data = new RealmData();
        if (tag.contains("center")) {
            data.center = BlockPos.of(tag.getLong("center"));
        }
        data.lairsBuilt = tag.getBoolean("lairs");
        data.defeated = tag.getInt("defeated");
        for (int i = 0; i < 3; i++) {
            if (tag.contains("seal" + i)) {
                data.seals[i] = tag.getLong("seal" + i);
                data.beacons[i] = tag.getLong("beacon" + i);
            }
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        if (center != null) {
            tag.putLong("center", center.asLong());
        }
        tag.putBoolean("lairs", lairsBuilt);
        tag.putInt("defeated", defeated);
        for (int i = 0; i < 3; i++) {
            if (seals[i] != Long.MIN_VALUE) {
                tag.putLong("seal" + i, seals[i]);
                tag.putLong("beacon" + i, beacons[i]);
            }
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

    // ---- the lieutenants' lairs (LairBuilder)

    public boolean lairsBuilt() {
        return lairsBuilt;
    }

    public void setLairsBuilt() {
        this.lairsBuilt = true;
        setDirty();
    }

    public void setLair(int slot, BlockPos seal, BlockPos beacon) {
        seals[slot] = seal.asLong();
        beacons[slot] = beacon.asLong();
        setDirty();
    }

    @Nullable
    public BlockPos seal(int slot) {
        return seals[slot] == Long.MIN_VALUE ? null : BlockPos.of(seals[slot]);
    }

    @Nullable
    public BlockPos beacon(int slot) {
        return beacons[slot] == Long.MIN_VALUE ? null : BlockPos.of(beacons[slot]);
    }

    public boolean defeated(int slot) {
        return (defeated & (1 << slot)) != 0;
    }

    public void defeat(int slot) {
        defeated |= 1 << slot;
        setDirty();
    }
}
