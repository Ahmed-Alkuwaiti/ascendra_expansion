package com.unstablefrontiers.entity;

import com.unstablefrontiers.registry.AbyssRegistry;
import com.unstablefrontiers.registry.ModEntities;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;

/**
 * A spark of stolen starlight: slow, straight, glowing, gone after three seconds. Spat by Lumen Mites. It never hurts the
 * abyss's own creatures, and it carries no knockback, so it cannot throw anyone off an island.
 */
public class StarBoltEntity extends ThrowableItemProjectile {
    public static final int LIFETIME = 60;
    private float damage = 6.0F;

    public StarBoltEntity(EntityType<? extends StarBoltEntity> type, Level level) {
        super(type, level);
    }

    public StarBoltEntity(Level level, LivingEntity owner, float damage) {
        super(ModEntities.STAR_BOLT.get(), owner, level);
        this.damage = damage;
    }

    @Override
    protected Item getDefaultItem() {
        return AbyssRegistry.STAR_BOLT.get();
    }

    @Override
    protected double getDefaultGravity() {
        return 0.0D;
    }

    @Override
    public void tick() {
        super.tick();
        if (!level().isClientSide && tickCount > LIFETIME) {
            discard();
        }
        if (level().isClientSide && tickCount % 2 == 0) {
            level().addParticle(ParticleTypes.END_ROD, getX(), getY(), getZ(), 0, 0, 0);
        }
    }

    public static boolean isAbyssCreature(Object e) {
        return e instanceof LumenMiteEntity || e instanceof OrreryWardenEntity || e instanceof EclipseLeviathanEntity;
    }

    @Override
    protected void onHitEntity(EntityHitResult hit) {
        if (hit.getEntity() instanceof LivingEntity e && !isAbyssCreature(e)) {
            double kb = e.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.KNOCKBACK_RESISTANCE);
            var v = e.getDeltaMovement();
            e.hurt(damageSources().indirectMagic(this, getOwner()), damage);
            e.setDeltaMovement(v);   // no knockback
            e.hurtMarked = kb >= 0;
        }
    }

    @Override
    protected void onHit(HitResult hit) {
        if (hit instanceof EntityHitResult eh && isAbyssCreature(eh.getEntity())) {
            return;   // passes through its own kind
        }
        super.onHit(hit);
        if (level() instanceof ServerLevel sl) {
            sl.sendParticles(ParticleTypes.END_ROD, getX(), getY(), getZ(), 6, 0.2D, 0.2D, 0.2D, 0.05D);
            discard();
        }
    }
}
