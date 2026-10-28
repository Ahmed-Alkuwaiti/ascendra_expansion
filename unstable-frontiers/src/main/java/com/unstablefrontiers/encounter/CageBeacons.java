package com.unstablefrontiers.encounter;

import com.unstablefrontiers.config.FrontierConfig;
import java.util.ArrayList;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.LongArrayTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

/** Placed Cage Beacons in one dimension: the frontier's safe ground. */
public final class CageBeacons extends SavedData {
    private static final String NAME = "unstable_frontiers_beacons";
    private final List<BlockPos> beacons = new ArrayList<>();

    public static CageBeacons get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(new SavedData.Factory<>(CageBeacons::new, CageBeacons::load, null), NAME);
    }

    private static CageBeacons load(CompoundTag tag, HolderLookup.Provider registries) {
        CageBeacons b = new CageBeacons();
        for (long l : tag.getLongArray("Beacons")) {
            b.beacons.add(BlockPos.of(l));
        }
        return b;
    }

    @Override
    public CompoundTag save(CompoundTag tag, HolderLookup.Provider registries) {
        tag.put("Beacons", new LongArrayTag(beacons.stream().mapToLong(BlockPos::asLong).toArray()));
        return tag;
    }

    public void add(BlockPos p) {
        if (!beacons.contains(p)) {
            beacons.add(p.immutable());
            setDirty();
        }
    }

    public void remove(BlockPos p) {
        if (beacons.remove(p)) {
            setDirty();
        }
    }

    @Nullable
    public BlockPos nearest(BlockPos to, double within) {
        BlockPos best = null;
        double bd = within * within;
        for (BlockPos b : beacons) {
            double d = b.distSqr(to);
            if (d <= bd) {
                bd = d;
                best = b;
            }
        }
        return best;
    }

    public static boolean covers(ServerLevel level, BlockPos pos) {
        return get(level).nearest(pos, FrontierConfig.BEACON_RADIUS.get()) != null;
    }
}
