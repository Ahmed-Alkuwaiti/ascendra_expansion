package com.unstablefrontiers.encounter;

import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.Map;
import javax.annotation.Nullable;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

/** Every landmark the frontier has seen, saved with the frontier dimension. Landmarks are added as players come near them. */
public final class LandmarkData extends SavedData {
    private static final String NAME = "unstable_frontiers_landmarks";
    private final Map<Long, LandmarkState> states = new LinkedHashMap<>();

    public static LandmarkData get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(new SavedData.Factory<>(LandmarkData::new, LandmarkData::load, null), NAME);
    }

    private static LandmarkData load(CompoundTag tag, HolderLookup.Provider registries) {
        LandmarkData d = new LandmarkData();
        for (Tag t : tag.getList("Landmarks", Tag.TAG_COMPOUND)) {
            try {
                LandmarkState s = LandmarkState.load((CompoundTag) t);
                d.states.put(s.key(), s);
            } catch (RuntimeException ignored) {
                // A damaged entry loses only that landmark's progress.
            }
        }
        return d;
    }

    @Override
    public CompoundTag save(CompoundTag tag, HolderLookup.Provider registries) {
        ListTag l = new ListTag();
        for (LandmarkState s : states.values()) {
            l.add(s.save());
        }
        tag.put("Landmarks", l);
        return tag;
    }

    @Nullable
    public LandmarkState get(long key) {
        return states.get(key);
    }

    public void add(LandmarkState s) {
        states.put(s.key(), s);
        setDirty();
    }

    public void remove(long key) {
        states.remove(key);
        setDirty();
    }

    public Collection<LandmarkState> all() {
        return states.values();
    }
}
