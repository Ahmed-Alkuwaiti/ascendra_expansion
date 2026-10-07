package com.aurelia.event;

import com.aurelia.item.RealmArmorItem;
import com.aurelia.item.RealmArmorMaterial;
import com.aurelia.item.RealmTier;
import com.aurelia.item.RealmWeaponItem;
import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.enchantment.FrostWalkerEnchantment;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingFallEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * The realm armor sets' full-set powers (and their auras), and the weapons' situational damage.
 * Chronite's Borrowed Time keeps five seconds of each wearer's positions to throw them back to.
 */
public class KitEvents {
    private static final String BORROWED = "aurelia_borrowed_time";
    private final Map<UUID, ArrayDeque<Vec3>> history = new HashMap<>();

    private static void keep(Player p, MobEffect effect, int amplifier) {
        p.addEffect(new MobEffectInstance(effect, effect == MobEffects.NIGHT_VISION ? 400 : 60, amplifier, true, false, true));
    }

    private static ParticleOptions aura(RealmArmorMaterial set) {
        return switch (set) {
            case VERDANT -> ParticleTypes.SPORE_BLOSSOM_AIR;
            case STORMGLASS -> ParticleTypes.ELECTRIC_SPARK;
            case EMBERHEART -> ParticleTypes.LAVA;
            case TIDESTONE -> ParticleTypes.BUBBLE_POP;
            case RIME -> ParticleTypes.SNOWFLAKE;
            case SUNGLASS -> ParticleTypes.WAX_OFF;
            case CHRONITE -> ParticleTypes.REVERSE_PORTAL;
            default -> ParticleTypes.CRIMSON_SPORE;
        };
    }

    @SubscribeEvent
    public void onPlayerTick(TickEvent.PlayerTickEvent event) {
        Player p = event.player;
        if (event.phase != TickEvent.Phase.END || p.level().isClientSide) {
            return;
        }
        RealmArmorMaterial set = RealmArmorItem.fullSet(p);
        if (set == RealmArmorMaterial.RIME && p.onGround()) {          // frost walker, every tick
            FrostWalkerEnchantment.onEntityMoved(p, p.level(), p.blockPosition(), 2);
        }
        if (p.tickCount % 20 != 0) {
            return;
        }
        if (set == RealmArmorMaterial.CHRONITE) {
            ArrayDeque<Vec3> q = this.history.computeIfAbsent(p.getUUID(), k -> new ArrayDeque<>());
            q.addLast(p.position());
            while (q.size() > 5) {
                q.pollFirst();
            }
        }
        if (set == null) {
            return;
        }
        if (p.level() instanceof ServerLevel level) {
            level.sendParticles(aura(set), p.getX(), p.getY() + 1.0, p.getZ(), 6, 0.5, 0.8, 0.5, 0.01);
        }
        switch (set) {
            case VERDANT -> {
                keep(p, MobEffects.REGENERATION, 1);
                p.removeEffect(MobEffects.POISON);
            }
            case STORMGLASS -> {
                keep(p, MobEffects.JUMP, 2);
                keep(p, MobEffects.MOVEMENT_SPEED, 0);
            }
            case EMBERHEART -> {
                keep(p, MobEffects.FIRE_RESISTANCE, 0);
                keep(p, MobEffects.DAMAGE_BOOST, 0);
            }
            case TIDESTONE -> {
                keep(p, MobEffects.WATER_BREATHING, 0);
                if (p.isInWaterOrRain()) {
                    keep(p, MobEffects.DOLPHINS_GRACE, 0);
                    keep(p, MobEffects.CONDUIT_POWER, 0);
                    keep(p, MobEffects.REGENERATION, 0);
                }
            }
            case RIME -> {
                p.setTicksFrozen(0);
                keep(p, MobEffects.DAMAGE_RESISTANCE, 0);
            }
            case SUNGLASS -> {
                if (p.level().getDayTime() % 24000L < 12500L) {
                    keep(p, MobEffects.DIG_SPEED, 1);
                    keep(p, MobEffects.DAMAGE_BOOST, 1);
                } else {
                    keep(p, MobEffects.NIGHT_VISION, 0);
                }
            }
            case CHRONITE -> {
                keep(p, MobEffects.MOVEMENT_SPEED, 1);
                keep(p, MobEffects.DIG_SPEED, 1);
            }
            case BLOOMSPORE -> {
                keep(p, MobEffects.NIGHT_VISION, 0);
                p.removeEffect(MobEffects.POISON);
                p.removeEffect(MobEffects.WITHER);
                if (p.tickCount % 200 == 0 && p.getFoodData().getFoodLevel() < 18) {
                    p.getFoodData().eat(2, 0.6f);
                }
                for (Player ally : p.level().getEntitiesOfClass(Player.class, p.getBoundingBox().inflate(6.0), a -> a != p)) {
                    ally.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 60, 0, true, true));
                }
            }
            default -> { }
        }
    }

    /** Sunglass turns a third of projectiles aside before they land. */
    @SubscribeEvent
    public void onAttacked(LivingAttackEvent event) {
        if (event.getEntity() instanceof Player p && event.getSource().getDirectEntity() instanceof Projectile
                && RealmArmorItem.fullSet(p) == RealmArmorMaterial.SUNGLASS && p.getRandom().nextInt(3) == 0) {
            event.setCanceled(true);
            p.level().playSound(null, p.blockPosition(), SoundEvents.SHIELD_BLOCK, SoundSource.PLAYERS, 1.0f, 1.5f);
        }
    }

    @SubscribeEvent
    public void onHurt(LivingHurtEvent event) {
        LivingEntity victim = event.getEntity();
        if (victim instanceof Player p && event.getSource().getEntity() instanceof LivingEntity attacker && attacker != p) {
            RealmArmorMaterial set = RealmArmorItem.fullSet(p);
            if (set != null) {
                switch (set) {
                    case VERDANT -> {
                        attacker.hurt(p.damageSources().thorns(p), 4.0f);
                        attacker.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 3));
                    }
                    case STORMGLASS -> {
                        if (p.getRandom().nextInt(3) == 0 && p.level() instanceof ServerLevel level) {
                            LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(level);
                            if (bolt != null) {
                                bolt.moveTo(attacker.getX(), attacker.getY(), attacker.getZ());
                                bolt.setVisualOnly(true);
                                level.addFreshEntity(bolt);
                            }
                            attacker.hurt(p.damageSources().lightningBolt(), 6.0f);
                        }
                    }
                    case EMBERHEART -> attacker.setSecondsOnFire(6);
                    case RIME -> {
                        attacker.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 3));
                        attacker.setTicksFrozen(attacker.getTicksRequiredToFreeze() + 100);
                    }
                    case BLOOMSPORE -> attacker.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 1));
                    default -> { }
                }
            }
        }
        if (event.getSource().getDirectEntity() instanceof LivingEntity attacker
                && attacker.getMainHandItem().getItem() instanceof RealmWeaponItem weapon) {
            if (weapon.realm() == RealmTier.TIDESTONE && victim.isInWater()) {
                event.setAmount(event.getAmount() * 1.5f);
            } else if (weapon.realm() == RealmTier.RIME && attacker.isCrouching()) {
                event.setAmount(event.getAmount() * 2.0f);
            }
        }
    }

    /** Chronite's Borrowed Time: the blow that would kill you throws you back five seconds instead. */
    @SubscribeEvent
    public void onDeath(LivingDeathEvent event) {
        if (!(event.getEntity() instanceof Player p) || RealmArmorItem.fullSet(p) != RealmArmorMaterial.CHRONITE) {
            return;
        }
        CompoundTag data = p.getPersistentData();
        long now = p.level().getGameTime();
        if (now - data.getLong(BORROWED) < 1800) {
            return;
        }
        data.putLong(BORROWED, now);
        event.setCanceled(true);
        p.setHealth(p.getMaxHealth() * 0.5f);
        ArrayDeque<Vec3> past = this.history.get(p.getUUID());
        if (past != null && !past.isEmpty()) {
            Vec3 then = past.peekFirst();
            p.teleportTo(then.x, then.y, then.z);
        }
        p.fallDistance = 0;
        p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 60, 4));
        if (p.level() instanceof ServerLevel level) {
            level.sendParticles(ParticleTypes.REVERSE_PORTAL, p.getX(), p.getY() + 1, p.getZ(), 120, 0.5, 1.0, 0.5, 0.3);
        }
        p.level().playSound(null, p.blockPosition(), SoundEvents.BELL_RESONATE, SoundSource.PLAYERS, 2.0f, 0.6f);
        p.displayClientMessage(net.minecraft.network.chat.Component.literal("Borrowed Time. The clock winds you back.")
                .withStyle(net.minecraft.ChatFormatting.LIGHT_PURPLE), true);
    }

    @SubscribeEvent
    public void onFall(LivingFallEvent event) {
        if (event.getEntity() instanceof Player p && RealmArmorItem.fullSet(p) == RealmArmorMaterial.STORMGLASS) {
            event.setDistance(0.0f);
            event.setDamageMultiplier(0.0f);
        }
    }
}
