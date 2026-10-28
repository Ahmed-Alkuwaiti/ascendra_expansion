package com.unstablefrontiers.encounter;

import com.unstablefrontiers.world.TowerBlueprint;
import com.unstablefrontiers.world.TowerRef;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.Set;
import java.util.UUID;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;

/**
 * Everything the server remembers about one tower. Saved in the frontier's data folder, so cleared floors, completion
 * and who has been rewarded survive unloading and restarts. Creatures are tracked by UUID; each one also carries its
 * tower id and the session number it was spawned in, so a creature from an abandoned or reset fight is removed the
 * moment its chunk loads again.
 */
public final class TowerState {
    public final TowerRef ref;
    /** Bit per stage: set once that stage has been beaten. */
    public int cleared;
    public boolean completed;
    /** The stage being fought now, or -1. */
    public int activeStage = -1;
    public int session;
    public int wave;
    public long nextWaveTime;
    public long lastPresence;
    public final Set<UUID> alive = new LinkedHashSet<>();
    public final Set<UUID> participants = new HashSet<>();
    public final Set<UUID> rewarded = new HashSet<>();

    public TowerState(TowerRef ref) {
        this.ref = ref;
    }

    public boolean isCleared(int stage) {
        return (cleared & (1 << stage)) != 0;
    }

    public boolean allCleared() {
        return cleared == (1 << TowerBlueprint.STAGES) - 1;
    }

    CompoundTag save() {
        CompoundTag t = new CompoundTag();
        t.putLong("Id", ref.id());
        t.putInt("OX", ref.originX());
        t.putInt("BY", ref.baseY());
        t.putInt("OZ", ref.originZ());
        t.putInt("Cleared", cleared);
        t.putBoolean("Completed", completed);
        t.putInt("Active", activeStage);
        t.putInt("Session", session);
        t.putInt("Wave", wave);
        t.putLong("NextWave", nextWaveTime);
        t.putLong("Presence", lastPresence);
        t.put("Alive", uuids(alive));
        t.put("Participants", uuids(participants));
        t.put("Rewarded", uuids(rewarded));
        return t;
    }

    static TowerState load(CompoundTag t) {
        TowerState s = new TowerState(new TowerRef(t.getLong("Id"), t.getInt("OX"), t.getInt("BY"), t.getInt("OZ")));
        s.cleared = t.getInt("Cleared");
        s.completed = t.getBoolean("Completed");
        s.activeStage = t.getInt("Active");
        s.session = t.getInt("Session");
        s.wave = t.getInt("Wave");
        s.nextWaveTime = t.getLong("NextWave");
        s.lastPresence = t.getLong("Presence");
        read(t.getList("Alive", Tag.TAG_INT_ARRAY), s.alive);
        read(t.getList("Participants", Tag.TAG_INT_ARRAY), s.participants);
        read(t.getList("Rewarded", Tag.TAG_INT_ARRAY), s.rewarded);
        return s;
    }

    private static ListTag uuids(Set<UUID> set) {
        ListTag list = new ListTag();
        for (UUID u : set) {
            list.add(NbtUtils.createUUID(u));
        }
        return list;
    }

    private static void read(ListTag list, Set<UUID> into) {
        for (Tag tag : list) {
            into.add(NbtUtils.loadUUID(tag));
        }
    }
}
