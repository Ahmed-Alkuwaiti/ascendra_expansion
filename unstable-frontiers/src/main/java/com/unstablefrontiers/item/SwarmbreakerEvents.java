package com.unstablefrontiers.item;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.tags.TagKey;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.block.Block;
import com.unstablefrontiers.ecology.Creatures;
import com.unstablefrontiers.registry.ModItems;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.tags.EntityTypeTags;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.player.Player;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.living.LivingFallEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * Server-side effects of the Swarmbreaker, the brood-breaker: 50% more damage to insects, and the Pounce landing, whose
 * shockwave smashes every egg clutch around you (a hatchery's waves come from its clutches, so this ends them sooner)
 * and staggers the insects it hits (slowed and weakened for three seconds).
 */
public final class SwarmbreakerEvents {
    private static final double SHOCK_RADIUS = 4.5D;
    private static final float SHOCK_DAMAGE = 6.0F;
    private static final long LEAP_TIMEOUT = 100;

    public static boolean isInsect(LivingEntity e) {
        return e.getType().is(Creatures.INSECTS) || e.getType().is(EntityTypeTags.ARTHROPOD);
    }

    @SubscribeEvent
    public void onHurt(LivingIncomingDamageEvent event) {
        if (event.getSource().getDirectEntity() instanceof Player p && p.getMainHandItem().is(ModItems.SWARMBREAKER.get()) && isInsect(event.getEntity())) {
            event.setAmount(event.getAmount() * 1.5F);
        }
    }

    @SubscribeEvent
    public void onFall(LivingFallEvent event) {
        if (event.getEntity() instanceof Player p && p.getPersistentData().contains(SwarmbreakerItem.LEAP)) {
            event.setDamageMultiplier(0.0F);
        }
    }

    @SubscribeEvent
    public void onPlayerTick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer p)) {
            return;
        }
        CompoundTag d = p.getPersistentData();
        if (!d.contains(SwarmbreakerItem.LEAP)) {
            return;
        }
        long age = p.level().getGameTime() - d.getLong(SwarmbreakerItem.LEAP);
        if (age > LEAP_TIMEOUT) {
            d.remove(SwarmbreakerItem.LEAP);
            return;
        }
        if (age < 5 || !p.onGround()) {
            return;
        }
        d.remove(SwarmbreakerItem.LEAP);
        shockwave((ServerLevel) p.level(), p);
    }

    public static final TagKey<Block> BROOD = TagKey.create(Registries.BLOCK, UnstableFrontiers.id("brood"));

    private static void shockwave(ServerLevel level, ServerPlayer p) {
        int smashed = 0;
        BlockPos c = p.blockPosition();
        int r = (int) Math.ceil(SHOCK_RADIUS);
        for (BlockPos b : BlockPos.betweenClosed(c.offset(-r, -2, -r), c.offset(r, 2, r))) {
            if (b.distSqr(c) <= SHOCK_RADIUS * SHOCK_RADIUS && level.getBlockState(b).is(BROOD)) {
                level.destroyBlock(b, false, p);
                smashed++;
            }
        }
        if (smashed > 0) {
            level.playSound(null, c, ModSounds.BROOD.get(), SoundSource.PLAYERS, 1.0F, 1.3F);
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.brood_smashed", smashed).withStyle(ChatFormatting.GREEN), true);
        }
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(SHOCK_RADIUS, 1.5D, SHOCK_RADIUS))) {
            if (e == p || e instanceof Player || !e.isAlive() || (e instanceof OwnableEntity o && p.getUUID().equals(o.getOwnerUUID()))) {
                continue;
            }
            boolean insect = isInsect(e);
            e.hurt(p.damageSources().playerAttack(p), insect ? SHOCK_DAMAGE * 1.5F : SHOCK_DAMAGE);
            if (insect) {
                e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 1));
                e.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 60, 0));
            }
            double dx = e.getX() - p.getX();
            double dz = e.getZ() - p.getZ();
            e.knockback(0.9D, -dx, -dz);
        }
        int n = FrontierConfig.particleCount(12);
        if (n > 0) {
            level.sendParticles(ParticleTypes.SWEEP_ATTACK, p.getX(), p.getY() + 0.3D, p.getZ(), n, SHOCK_RADIUS / 2, 0.1D, SHOCK_RADIUS / 2, 0.0D);
            level.sendParticles(ParticleTypes.EXPLOSION, p.getX(), p.getY() + 0.2D, p.getZ(), Math.max(1, n / 4), 1.0D, 0.1D, 1.0D, 0.0D);
        }
        level.playSound(null, p.blockPosition(), SoundEvents.GENERIC_EXPLODE.value(), SoundSource.PLAYERS, 0.6F, 1.4F);
    }
}
