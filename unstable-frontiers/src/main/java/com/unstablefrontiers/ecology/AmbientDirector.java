package com.unstablefrontiers.ecology;

import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.registry.ModStructures;
import com.unstablefrontiers.world.CageTowerPiece;
import com.unstablefrontiers.world.FrontierDimension;
import com.unstablefrontiers.world.TowerBlueprint;
import com.unstablefrontiers.world.TowerLocator;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.StructureSet;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * Keeps the frontier inhabited around each player: every so often, if fewer than the cap of this mod's wild creatures
 * are near, it stages a small skirmish (a few ground insects, and by night or now and then by day a flying predator
 * above them that {@link Rivalry} will send after them). Skirmishes favour the foot of a nearby tower, so towers are
 * where the fighting is. Only loaded chunks are used; nothing is generated or force-loaded. Wild creatures are not
 * persistent, so the vanilla despawn rules clear them once players leave.
 */
public final class AmbientDirector {
    private static final double COUNT_RADIUS = 64.0D;
    private static final int TOWER_RADIUS = 160;

    private AmbientDirector() {}

    public static void tick(ServerLevel level, long time) {
        int interval = FrontierConfig.ambientInterval();
        for (ServerPlayer p : level.players()) {
            if (!p.isSpectator() && (time + p.getId() * 31L) % interval == 0) {
                trySkirmish(level, p);
            }
        }
    }

    private static void trySkirmish(ServerLevel level, ServerPlayer p) {
        int cap = FrontierConfig.ambientPerPlayer();
        if (cap <= 0) {
            return;
        }
        AABB box = p.getBoundingBox().inflate(COUNT_RADIUS, 48.0D, COUNT_RADIUS);
        int count = level.getEntitiesOfClass(Mob.class, box, Creatures::isAmbient).size();
        if (count >= cap) {
            return;
        }
        RandomSource r = level.random;
        BlockPos tower = nearestTower(level, p.blockPosition());
        boolean quiet = level.getBiome(p.blockPosition()).is(FrontierDimension.HUSHED_BARRENS);
        if (quiet && tower == null && r.nextInt(4) != 0) {
            return; // breathing room
        }
        BlockPos anchor = tower != null && r.nextInt(3) != 0 ? around(tower, 16, 30, r) : around(p.blockPosition(), 24, 44, r);
        anchor = ground(level, anchor);
        if (anchor == null || anchor.distSqr(p.blockPosition()) < 16 * 16) {
            return;
        }
        boolean night = !level.isDay();
        int room = cap - count;
        List<EntityType<?>> prey = Creatures.pick(Rosters.swarm(), Math.min(room, 2 + r.nextInt(2)), r);
        for (EntityType<?> type : prey) {
            BlockPos at = ground(level, around(anchor, 0, 4, r));
            if (at != null && spawn(level, type, Vec3.atBottomCenterOf(at)) != null) {
                room--;
            }
        }
        if (room > 0 && (night || r.nextInt(100) < 40)) {
            List<EntityType<?>> raptor = Creatures.pick(Rosters.raptors(night), 1, r);
            if (!raptor.isEmpty()) {
                spawn(level, raptor.get(0), Vec3.atBottomCenterOf(anchor).add(0, 10 + r.nextInt(6), 0));
            }
        }
    }

    @Nullable
    private static Mob spawn(ServerLevel level, EntityType<?> type, Vec3 at) {
        Mob mob = Creatures.create(level, type, at);
        if (mob == null) {
            return null;
        }
        Creatures.tagAmbient(mob);
        return level.addFreshEntity(mob) ? mob : null;
    }

    private static BlockPos around(BlockPos c, int min, int max, RandomSource r) {
        double a = r.nextDouble() * Math.PI * 2;
        int d = min + (max > min ? r.nextInt(max - min + 1) : 0);
        return c.offset(Mth.floor(Math.cos(a) * d), 0, Mth.floor(Math.sin(a) * d));
    }

    /** Standing spot on loaded, dry ground outside any tower, or null. */
    @Nullable
    private static BlockPos ground(ServerLevel level, BlockPos pos) {
        if (!level.isLoaded(pos)) {
            return null;
        }
        int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, pos.getX(), pos.getZ());
        BlockPos at = new BlockPos(pos.getX(), y, pos.getZ());
        if (y <= level.getMinBuildHeight() + 1 || !level.getBlockState(at.below()).getFluidState().isEmpty()) {
            return null;
        }
        return TowerLocator.at(level, at, true) != null ? null : at;
    }

    /**
     * The centre of a tower near this position whose chunk is already loaded, or null. Works out the candidate chunks
     * from the structure set's spacing (arithmetic only) and reads the structure start stored in those chunks.
     */
    @Nullable
    public static BlockPos nearestTower(ServerLevel level, BlockPos pos) {
        StructureSet set = level.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).get(ModStructures.CAGE_TOWER_SET);
        Structure tower = TowerLocator.tower(level);
        if (set == null || tower == null || !(set.placement() instanceof RandomSpreadStructurePlacement spread)) {
            return null;
        }
        long seed = level.getChunkSource().getGeneratorState().getLevelSeed();
        ChunkPos here = new ChunkPos(pos);
        BlockPos best = null;
        double bestD = (double) TOWER_RADIUS * TOWER_RADIUS;
        for (int dx = -1; dx <= 1; dx++) {
            for (int dz = -1; dz <= 1; dz++) {
                ChunkPos cand = spread.getPotentialStructureChunk(seed, here.x + dx * spread.spacing(), here.z + dz * spread.spacing());
                if (!level.hasChunk(cand.x, cand.z)) {
                    continue;
                }
                StructureStart start = level.getChunk(cand.x, cand.z).getStartForStructure(tower);
                if (start == null || !start.isValid()) {
                    continue;
                }
                for (StructurePiece piece : start.getPieces()) {
                    if (piece instanceof CageTowerPiece t) {
                        BlockPos c = new BlockPos(t.originX() + TowerBlueprint.C, t.baseY(), t.originZ() + TowerBlueprint.C);
                        double d = c.distSqr(pos);
                        if (d < bestD) {
                            bestD = d;
                            best = c;
                        }
                    }
                }
            }
        }
        return best;
    }
}
