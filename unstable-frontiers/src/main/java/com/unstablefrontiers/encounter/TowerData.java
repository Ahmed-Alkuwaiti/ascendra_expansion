package com.unstablefrontiers.encounter;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.world.TowerRef;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import javax.annotation.Nullable;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

/** All tower states in the frontier, saved as data/unstable_frontiers_towers.dat in the dimension's folder. */
public final class TowerData extends SavedData {
    /** Bump when the saved layout changes; load() upgrades older layouts. */
    public static final int DATA_VERSION = 1;
    private static final String NAME = UnstableFrontiers.MODID + "_towers";

    private final Long2ObjectOpenHashMap<TowerState> towers = new Long2ObjectOpenHashMap<>();

    public static TowerData get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(TowerData::load, TowerData::new, NAME);
    }

    @Nullable
    public TowerState get(long id) {
        return towers.get(id);
    }

    public TowerState getOrCreate(TowerRef ref) {
        TowerState s = towers.get(ref.id());
        if (s == null) {
            s = new TowerState(ref);
            towers.put(ref.id(), s);
            setDirty();
        }
        return s;
    }

    public void remove(long id) {
        if (towers.remove(id) != null) {
            setDirty();
        }
    }

    public Collection<TowerState> all() {
        return towers.values();
    }

    public List<TowerState> active() {
        List<TowerState> out = new ArrayList<>();
        for (TowerState s : towers.values()) {
            if (s.activeStage >= 0) {
                out.add(s);
            }
        }
        return out;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        tag.putInt("DataVersion", DATA_VERSION);
        ListTag list = new ListTag();
        for (TowerState s : towers.values()) {
            list.add(s.save());
        }
        tag.put("Towers", list);
        return tag;
    }

    private static TowerData load(CompoundTag tag) {
        TowerData data = new TowerData();
        int version = tag.getInt("DataVersion");
        if (version > DATA_VERSION) {
            UnstableFrontiers.LOGGER.warn("Tower data was saved by a newer version ({} > {}); reading what this version understands", version, DATA_VERSION);
        }
        for (Tag t : tag.getList("Towers", Tag.TAG_COMPOUND)) {
            TowerState s = TowerState.load((CompoundTag) t);
            data.towers.put(s.ref.id(), s);
        }
        return data;
    }
}
