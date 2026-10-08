package com.aurelia.world;

import com.aurelia.AureliaMod;
import com.aurelia.entity.LieutenantKind;
import java.util.List;
import java.util.Optional;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.minecraft.world.phys.Vec3;

/**
 * Builds each realm's lieutenant lairs the first time anyone arrives (or the first time after this was added), and keeps count of
 * the lieutenants slain. The lairs stand LAIR_DISTANCE blocks out from the landing pad, a third of a turn apart, each crowned with
 * a beacon whose beam goes dark when its lieutenant dies. Templates: data/aurelia/structures/lair_<id>.nbt (gen_lairs.py), with
 * their sizes, floor heights, seals and beacons in LairLayout (generated alongside).
 */
public final class LairBuilder {
    private LairBuilder() {}

    private static final org.slf4j.Logger LOGGER = com.mojang.logging.LogUtils.getLogger();
    public static final int LAIR_DISTANCE = 150;
    private static final String[] DIRS = {"east", "south-east", "south", "south-west", "west", "north-west", "north", "north-east"};

    private enum Ground { SURFACE, FLOAT, CAVERN }

    private static Ground ground(Realm realm) {
        return switch (realm) {
            case SKYREACH, CLOCKWORK, LAST -> Ground.FLOAT;
            case HOLLOW, MYCELIAL -> Ground.CAVERN;
            default -> Ground.SURFACE;
        };
    }

    /** Where the first lair stands, in degrees round the pad; the others follow a third of a turn apart. */
    private static double baseAngle(Realm realm) {
        return realm.ordinal() * 47.0 + 20.0;
    }

    public static void ensure(ServerLevel level, Realm realm, BlockPos center) {
        RealmData data = RealmData.get(level);
        if (data.lairsBuilt()) {
            return;
        }
        List<LieutenantKind> kinds = LieutenantKind.of(realm);
        for (LieutenantKind kind : kinds) {
            int[] lay = LairLayout.get(kind.id);
            if (lay == null) {
                continue;
            }
            int w = lay[0], h = lay[1], l = lay[2], floor = lay[3];
            double a = Math.toRadians(baseAngle(realm) + kind.slot * 360.0 / kinds.size());
            int x = center.getX() + (int) Math.round(Math.cos(a) * LAIR_DISTANCE);
            int z = center.getZ() + (int) Math.round(Math.sin(a) * LAIR_DISTANCE);
            for (int cx = (x - w / 2) >> 4; cx <= (x + w / 2) >> 4; cx++) {
                for (int cz = (z - l / 2) >> 4; cz <= (z + l / 2) >> 4; cz++) {
                    level.getChunk(cx, cz);                                         // generate the ground before reading it
                }
            }
            Ground g = ground(realm);
            int y = switch (g) {
                case SURFACE -> level.getHeight(Heightmap.Types.WORLD_SURFACE, x, z) - floor;
                default -> center.getY() - floor;
            };
            y = Math.max(level.getMinBuildHeight() + 2, Math.min(level.getMaxBuildHeight() - h - 2, y));
            BlockPos origin = new BlockPos(x - w / 2, y, z - l / 2);
            if (g == Ground.CAVERN) {
                carve(level, origin, w, h, l, floor);
            } else {
                clear(level, origin, w, h, l, floor);
            }
            Optional<StructureTemplate> t = level.getStructureManager().get(new ResourceLocation(AureliaMod.MODID, "lair_" + kind.id));
            if (t.isEmpty()) {
                LOGGER.warn("Missing lair template lair_{}", kind.id);
                continue;
            }
            t.get().placeInWorld(level, origin, origin, new StructurePlaceSettings(), level.random, 2);
            data.setLair(kind.slot, origin.offset(lay[4], lay[5], lay[6]), origin.offset(lay[7], lay[8], lay[9]));
        }
        data.setLairsBuilt();
    }

    /** Clears the lair's volume above its floor (hills, trees, sea ice): the templates leave that air out to stay small. */
    private static void clear(ServerLevel level, BlockPos o, int w, int h, int l, int floor) {
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        double cx = o.getX() + w / 2.0, cz = o.getZ() + l / 2.0, r = Math.min(w, l) / 2.0;
        for (int x = o.getX(); x < o.getX() + w; x++) {
            for (int z = o.getZ(); z < o.getZ() + l; z++) {
                if (Math.hypot(x - cx, z - cz) > r) {
                    continue;
                }
                for (int y = o.getY() + floor; y < o.getY() + h; y++) {
                    p.set(x, y, z);
                    if (!level.getBlockState(p).isAir() && level.getFluidState(p).isEmpty()) {
                        level.setBlock(p, Blocks.AIR.defaultBlockState(), 2);
                    }
                }
            }
        }
    }

    /** A cavern for a lair under a rock ceiling: an open dome above the floor, so the lair stands in its own vast hollow. */
    private static void carve(ServerLevel level, BlockPos o, int w, int h, int l, int floor) {
        double cx = o.getX() + w / 2.0, cz = o.getZ() + l / 2.0, cy = o.getY() + floor;
        double rx = w / 2.0 + 6, rz = l / 2.0 + 6, ry = h - floor + 4;
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        for (int x = (int) (cx - rx); x <= cx + rx; x++) {
            for (int z = (int) (cz - rz); z <= cz + rz; z++) {
                double dx = (x - cx) / rx, dz = (z - cz) / rz;
                double r2 = dx * dx + dz * dz;
                if (r2 > 1.0) {
                    continue;
                }
                int top = (int) (cy + ry * Math.sqrt(1.0 - r2));
                for (int y = (int) cy; y <= top && y < level.getMaxBuildHeight() - 1; y++) {
                    level.setBlock(p.set(x, y, z), Blocks.CAVE_AIR.defaultBlockState(), 2);
                }
            }
        }
    }

    /** A lieutenant has died: count it, put out its lair's beacon, and tell the realm how many remain. */
    public static void onLieutenantSlain(ServerLevel level, LieutenantKind kind) {
        RealmData data = RealmData.get(level);
        boolean first = !data.defeated(kind.slot);
        data.defeat(kind.slot);
        BlockPos beacon = data.beacon(kind.slot);
        if (beacon != null && level.getBlockState(beacon).is(Blocks.BEACON)) {
            level.setBlock(beacon, Blocks.CRYING_OBSIDIAN.defaultBlockState(), 3);
        }
        List<LieutenantKind> kinds = LieutenantKind.of(kind.realm);
        int slain = 0;
        for (LieutenantKind k : kinds) {
            slain += data.defeated(k.slot) ? 1 : 0;
        }
        if (!first) {
            return;
        }
        String head = slain >= kinds.size()
                ? "The last of the lieutenants is dead. On its altar, the Warden of " + kind.realm.title + " stirs."
                : slain + " of " + kinds.size() + " lieutenants slain. The Warden will not wake while the others stand.";
        for (ServerPlayer p : level.players()) {
            Story.narrate(p, head);
        }
        if (slain >= kinds.size() && data.center() != null) {
            LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(level);
            if (bolt != null) {
                bolt.moveTo(Vec3.atBottomCenterOf(data.center()));
                bolt.setVisualOnly(true);
                level.addFreshEntity(bolt);
            }
            level.playSound(null, data.center(), SoundEvents.WITHER_SPAWN, SoundSource.HOSTILE, 4.0f, 0.5f);
        }
    }

    /** True when every lieutenant of the realm is dead (or the realm has none). */
    public static boolean cleared(ServerLevel level, Realm realm) {
        RealmData data = RealmData.get(level);
        for (LieutenantKind k : LieutenantKind.of(realm)) {
            if (!data.defeated(k.slot)) {
                return false;
            }
        }
        return true;
    }

    /** Which lieutenants still stand, where their lairs are, and which way from here. */
    public static void tellStatus(ServerPlayer player, ServerLevel level, Realm realm) {
        RealmData data = RealmData.get(level);
        List<LieutenantKind> kinds = LieutenantKind.of(realm);
        if (kinds.isEmpty()) {
            return;
        }
        int left = 0;
        for (LieutenantKind k : kinds) {
            if (data.defeated(k.slot)) {
                continue;
            }
            left++;
            BlockPos seal = data.seal(k.slot);
            String where = "";
            if (seal != null) {
                double dx = seal.getX() - player.getX(), dz = seal.getZ() - player.getZ();
                int dir = (int) Math.round(Math.toDegrees(Math.atan2(dz, dx)) / 45.0) & 7;
                where = String.format(" - %s, %d blocks (%d, %d, %d)", DIRS[dir], (int) Math.sqrt(dx * dx + dz * dz), seal.getX(), seal.getY(), seal.getZ());
            }
            player.sendSystemMessage(Component.literal("  " + Component.translatable("entity.aurelia." + k.id).getString() + ", " + k.title + where)
                    .withStyle(ChatFormatting.GRAY));
        }
        Story.narrate(player, left == 0 ? "Every lieutenant here is dead. The Warden waits on its altar."
                : left + " of the Warden's lieutenants still stand. Follow the beacons to their lairs.");
    }
}
