package com.unstablefrontiers.world;

import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.Vec3;

/** A generated tower: its id (the start chunk, packed), the corner of its footprint and the height of its platform. */
public record TowerRef(long id, int originX, int baseY, int originZ) {
    public int localX(double x) { return (int) Math.floor(x) - originX; }
    public int localY(double y) { return (int) Math.floor(y) - baseY; }
    public int localZ(double z) { return (int) Math.floor(z) - originZ; }

    /** Middle of a stage, one block above its floor. */
    public Vec3 stageCentre(int stage) {
        return new Vec3(originX + TowerBlueprint.C + 0.5, baseY + TowerBlueprint.stageFloor(stage) + 1, originZ + TowerBlueprint.C + 0.5);
    }

    public BlockPos vault() {
        return new BlockPos(originX + TowerBlueprint.C, baseY + TowerBlueprint.CROWN_Y + 2, originZ + TowerBlueprint.C);
    }

    public BlockPos top() {
        return new BlockPos(originX + TowerBlueprint.C, baseY + TowerBlueprint.TOP, originZ + TowerBlueprint.C);
    }
}
