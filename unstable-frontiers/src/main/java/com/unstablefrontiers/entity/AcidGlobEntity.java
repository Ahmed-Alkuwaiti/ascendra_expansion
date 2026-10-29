package com.unstablefrontiers.entity;

import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.registry.ModEntities;
import com.unstablefrontiers.registry.ModItems;
import com.unstablefrontiers.registry.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;

/** The Matriarch's acid: a lobbed glob that stings on a direct hit and leaves a short-lived puddle of poison. */
public class AcidGlobEntity extends ThrowableItemProjectile {
    public AcidGlobEntity(EntityType<? extends AcidGlobEntity> type, Level level) {
        super(type, level);
    }

    public AcidGlobEntity(Level level, LivingEntity owner) {
        super(ModEntities.ACID_GLOB.get(), owner, level);
    }

    @Override
    protected Item getDefaultItem() {
        return ModItems.ACID_GLOB.get();
    }

    @Override
    protected void onHitEntity(EntityHitResult hit) {
        super.onHitEntity(hit);
        if (hit.getEntity() instanceof LivingEntity e && !(e instanceof ChainedMatriarchEntity)) {
            e.hurt(damageSources().thrown(this, getOwner()), 6.0F);
        }
    }

    @Override
    protected void onHit(HitResult hit) {
        super.onHit(hit);
        if (level() instanceof ServerLevel sl) {
            AreaEffectCloud cloud = new AreaEffectCloud(sl, getX(), getY(), getZ());
            if (getOwner() instanceof LivingEntity owner) {
                cloud.setOwner(owner);
            }
            cloud.setRadius(2.2F);
            cloud.setRadiusOnUse(0);
            cloud.setRadiusPerTick(-0.01F);
            cloud.setDuration(80);
            cloud.setWaitTime(4);
            cloud.setParticle(ParticleTypes.ITEM_SLIME);
            cloud.addEffect(new MobEffectInstance(MobEffects.POISON, 60, 1));
            sl.addFreshEntity(cloud);
            sl.sendParticles(ParticleTypes.ITEM_SLIME, getX(), getY(), getZ(), Math.max(1, FrontierConfig.particleCount(10)), 0.4D, 0.2D, 0.4D, 0.05D);
            sl.playSound(null, getX(), getY(), getZ(), ModSounds.MATRIARCH_ACID.get(), getSoundSource(), 1.2F, 0.9F + random.nextFloat() * 0.2F);
            discard();
        }
    }
}
