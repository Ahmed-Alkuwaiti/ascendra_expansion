package com.unstablefrontiers.encounter;

import com.unstablefrontiers.landmark.LandmarkDef;
import com.unstablefrontiers.world.LandmarkPiece;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.minecraft.world.phys.Vec3;

/**
 * One landmark in the world: where its template was placed and how far each of its fights has got. Positions in the
 * landmark's definition are template-local; {@link #world} turns them into world positions with the same rotation the
 * template was placed with.
 */
public final class LandmarkState {
    public final ResourceLocation id;
    public final BlockPos origin;
    public final Rotation rotation;
    public final List<ZoneState> zones = new ArrayList<>();
    public final Set<UUID> residents = new HashSet<>();
    public long residentsAt = Long.MIN_VALUE;
    public final Set<UUID> rewarded = new HashSet<>();
    public final Set<UUID> visitors = new HashSet<>();
    public final Set<String> openGates = new HashSet<>();

    public LandmarkState(ResourceLocation id, BlockPos origin, Rotation rotation) {
        this.id = id;
        this.origin = origin;
        this.rotation = rotation;
    }

    public long key() {
        return origin.asLong();
    }

    /** The zone states, grown to match the definition if a datapack added zones since this landmark was saved. */
    public ZoneState zone(LandmarkDef.Zone z) {
        while (zones.size() <= z.index()) {
            zones.add(new ZoneState());
        }
        return zones.get(z.index());
    }

    public BlockPos world(BlockPos local) {
        return StructureTemplate.calculateRelativePosition(LandmarkPiece.settings(rotation), local).offset(origin);
    }

    public Vec3 feet(BlockPos local) {
        BlockPos p = world(local);
        return new Vec3(p.getX() + 0.5D, p.getY(), p.getZ() + 0.5D);
    }

    public BoundingBox world(BoundingBox local) {
        BlockPos a = world(new BlockPos(local.minX(), local.minY(), local.minZ()));
        BlockPos b = world(new BlockPos(local.maxX(), local.maxY(), local.maxZ()));
        return BoundingBox.fromCorners(a, b);
    }

    public BoundingBox bounds(LandmarkDef def) {
        BlockPos s = def.size();
        return world(new BoundingBox(0, 0, 0, s.getX() - 1, s.getY() - 1, s.getZ() - 1));
    }

    public BlockPos centre(LandmarkDef def) {
        BoundingBox b = bounds(def);
        return new BlockPos((b.minX() + b.maxX()) / 2, b.minY() + def.ground(), (b.minZ() + b.maxZ()) / 2);
    }

    CompoundTag save() {
        CompoundTag t = new CompoundTag();
        t.putString("Id", id.toString());
        t.putLong("Origin", origin.asLong());
        t.putString("Rot", rotation.name());
        ListTag zl = new ListTag();
        for (ZoneState z : zones) {
            zl.add(z.save());
        }
        t.put("Zones", zl);
        t.put("Residents", ZoneState.uuids(residents));
        t.putLong("ResidentsAt", residentsAt);
        t.put("Rewarded", ZoneState.uuids(rewarded));
        t.put("Visitors", ZoneState.uuids(visitors));
        ListTag gates = new ListTag();
        for (String g : openGates) {
            gates.add(StringTag.valueOf(g));
        }
        t.put("Gates", gates);
        return t;
    }

    static LandmarkState load(CompoundTag t) {
        Rotation rot;
        try {
            rot = Rotation.valueOf(t.getString("Rot"));
        } catch (IllegalArgumentException e) {
            rot = Rotation.NONE;
        }
        LandmarkState s = new LandmarkState(ResourceLocation.parse(t.getString("Id")), BlockPos.of(t.getLong("Origin")), rot);
        for (Tag z : t.getList("Zones", Tag.TAG_COMPOUND)) {
            s.zones.add(ZoneState.load((CompoundTag) z));
        }
        ZoneState.read(t.getList("Residents", Tag.TAG_INT_ARRAY), s.residents);
        s.residentsAt = t.contains("ResidentsAt") ? t.getLong("ResidentsAt") : Long.MIN_VALUE;
        ZoneState.read(t.getList("Rewarded", Tag.TAG_INT_ARRAY), s.rewarded);
        ZoneState.read(t.getList("Visitors", Tag.TAG_INT_ARRAY), s.visitors);
        for (Tag g : t.getList("Gates", Tag.TAG_STRING)) {
            s.openGates.add(g.getAsString());
        }
        return s;
    }
}
