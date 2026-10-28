package com.unstablefrontiers.encounter;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import javax.annotation.Nullable;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;

/** The saved progress of one encounter zone of one landmark. */
public final class ZoneState {
    public enum Status { IDLE, ACTIVE, CLEARED }

    public Status status = Status.IDLE;
    /** Bumped each time the zone starts, so creatures left over from an earlier attempt are recognised and turned away. */
    public int session;
    public int wavesLeft;
    public long nextWaveAt;
    public long lastEngaged;
    /** Prisoners or roosting creatures were placed, dormant, for this session. */
    public boolean dormantPlaced;
    public int broodStart;
    @Nullable public UUID elite;
    public boolean eliteSlain;
    public final Set<UUID> mobs = new HashSet<>();
    public final Set<UUID> participants = new HashSet<>();

    // Not saved: telegraphs and throttles restart harmlessly after a reload.
    public boolean telegraphed;
    public long abilityAt;
    @Nullable public String pendingAbility;
    public long pendingAt;
    public long hintAt;
    public int pylonsSeen = -1;

    CompoundTag save() {
        CompoundTag t = new CompoundTag();
        t.putString("Status", status.name());
        t.putInt("Session", session);
        t.putInt("Waves", wavesLeft);
        t.putLong("Next", nextWaveAt);
        t.putLong("Engaged", lastEngaged);
        t.putBoolean("Dormant", dormantPlaced);
        t.putInt("Brood", broodStart);
        if (elite != null) {
            t.putUUID("Elite", elite);
        }
        t.putBoolean("EliteSlain", eliteSlain);
        t.put("Mobs", uuids(mobs));
        t.put("Players", uuids(participants));
        return t;
    }

    static ZoneState load(CompoundTag t) {
        ZoneState z = new ZoneState();
        try {
            z.status = Status.valueOf(t.getString("Status"));
        } catch (IllegalArgumentException e) {
            z.status = Status.IDLE;
        }
        z.session = t.getInt("Session");
        z.wavesLeft = t.getInt("Waves");
        z.nextWaveAt = t.getLong("Next");
        z.lastEngaged = t.getLong("Engaged");
        z.dormantPlaced = t.getBoolean("Dormant");
        z.broodStart = t.getInt("Brood");
        z.elite = t.hasUUID("Elite") ? t.getUUID("Elite") : null;
        z.eliteSlain = t.getBoolean("EliteSlain");
        read(t.getList("Mobs", Tag.TAG_INT_ARRAY), z.mobs);
        read(t.getList("Players", Tag.TAG_INT_ARRAY), z.participants);
        return z;
    }

    static ListTag uuids(Set<UUID> set) {
        ListTag l = new ListTag();
        for (UUID u : set) {
            l.add(NbtUtils.createUUID(u));
        }
        return l;
    }

    static void read(ListTag l, Set<UUID> into) {
        for (Tag tag : l) {
            into.add(NbtUtils.loadUUID(tag));
        }
    }
}
