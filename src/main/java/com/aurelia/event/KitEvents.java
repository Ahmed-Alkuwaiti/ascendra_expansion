package com.aurelia.event;

import com.aurelia.item.RealmArmorItem;
import com.aurelia.item.RealmArmorMaterial;
import com.aurelia.item.RealmTier;
import com.aurelia.item.RealmWeaponItem;
import com.aurelia.item.WorldsunderItem;
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
import net.minecraft.tags.DamageTypeTags;
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
import net.minecraftforge.event.entity.living.LivingDamageEvent;
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
    private static final String LAST_HEART = "aurelia_last_heart";
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
            case GENESIS -> ParticleTypes.END_ROD;
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
            com.aurelia.Perf.particles(level, aura(set), p.getX(), p.getY() + 1.0, p.getZ(), 6, 0.5, 0.8, 0.5, 0.01);
        }
        switch (set) {
            case VERDANT -> {
                keep(p, MobEffects.REGENERATION, 0);
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
                    keep(p, MobEffects.DAMAGE_BOOST, 0);
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
            case GENESIS -> {                                               // Genesis armor
                keep(p, MobEffects.DAMAGE_BOOST, 1);
                keep(p, MobEffects.DAMAGE_RESISTANCE, 0);
                keep(p, MobEffects.FIRE_RESISTANCE, 0);
                keep(p, MobEffects.NIGHT_VISION, 0);
                keep(p, MobEffects.WATER_BREATHING, 0);
                p.removeEffect(MobEffects.POISON);
                p.removeEffect(MobEffects.WITHER);
                p.setTicksFrozen(0);
                if (p.level() instanceof ServerLevel level) {
                    com.aurelia.Perf.particles(level, ParticleTypes.REVERSE_PORTAL, p.getX(), p.getY() + 1.0, p.getZ(), 8, 0.4, 0.8, 0.4, 0.05);
                }
            }
            default -> { }
        }
    }

    /** The Genesis glide: crouching in mid-air while falling lets the wearer drift down. Checked every tick so it answers at once. */
    @SubscribeEvent
    public void onGlide(TickEvent.PlayerTickEvent event) {
        Player p = event.player;
        if (event.phase == TickEvent.Phase.END && !p.level().isClientSide && !p.onGround() && p.isCrouching()
                && p.getDeltaMovement().y < -0.1 && RealmArmorItem.fullSet(p) == RealmArmorMaterial.GENESIS) {
            p.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 10, 0, true, false, true));
        }
    }

    /** Sunglass turns a third of projectiles aside before they land. */
    @SubscribeEvent
    public void onAttacked(LivingAttackEvent event) {
        if (!(event.getEntity() instanceof Player p) || !(event.getSource().getDirectEntity() instanceof Projectile)) {
            return;
        }
        RealmArmorMaterial set = RealmArmorItem.fullSet(p);
        if (set == RealmArmorMaterial.SUNGLASS && p.getRandom().nextInt(3) == 0) {
            event.setCanceled(true);
            p.level().playSound(null, p.blockPosition(), SoundEvents.SHIELD_BLOCK, SoundSource.PLAYERS, 1.0f, 1.5f);
        } else if (set == RealmArmorMaterial.GENESIS && p.getRandom().nextBoolean()) {     // Event Horizon swallows half of them
            event.setCanceled(true);
            event.getSource().getDirectEntity().discard();
            if (p.level() instanceof ServerLevel level) {
                com.aurelia.Perf.particles(level, ParticleTypes.REVERSE_PORTAL, p.getX(), p.getY() + 1.2, p.getZ(), 20, 0.3, 0.4, 0.3, 0.1);
            }
            p.level().playSound(null, p.blockPosition(), SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 0.8f, 0.5f);
        }
    }

    /** Event Horizon: while Genesis armor is worn, no single blow takes more than 30% of the wearer's health. */
    @SubscribeEvent
    public void onDamage(LivingDamageEvent event) {
        if (event.getEntity() instanceof Player p && !event.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY)
                && RealmArmorItem.fullSet(p) == RealmArmorMaterial.GENESIS) {
            event.setAmount(Math.min(event.getAmount(), p.getMaxHealth() * 0.3f));
        }
    }

    /** Eightfold Retaliation: one realm's curse, chosen at random, on whatever strikes the Genesis wearer. */
    private static void retaliate(Player p, LivingEntity attacker) {
        attacker.hurt(p.damageSources().thorns(p), 6.0f);
        switch (p.getRandom().nextInt(8)) {
            case 0 -> attacker.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 3));
            case 1 -> {
                if (p.level() instanceof ServerLevel level) {
                    LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(level);
                    if (bolt != null) {
                        bolt.moveTo(attacker.getX(), attacker.getY(), attacker.getZ());
                        bolt.setVisualOnly(true);
                        level.addFreshEntity(bolt);
                    }
                }
                attacker.hurt(p.damageSources().lightningBolt(), 6.0f);
            }
            case 2 -> attacker.setSecondsOnFire(8);
            case 3 -> {
                Vec3 in = p.position().subtract(attacker.position()).normalize().scale(0.8);
                attacker.push(in.x, 0.2, in.z);
                attacker.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 1));
            }
            case 4 -> attacker.setTicksFrozen(attacker.getTicksRequiredToFreeze() + 120);
            case 5 -> attacker.hurt(p.damageSources().thorns(p), 4.0f);
            case 6 -> attacker.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 100, 1));
            default -> attacker.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 1));
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
                    case GENESIS -> retaliate(p, attacker);
                    default -> { }
                }
            }
        }
        if (event.getSource().getDirectEntity() instanceof LivingEntity attacker && attacker != victim
                && attacker.getMainHandItem().getItem() instanceof WorldsunderItem) {               // Unmaking
            event.setAmount(event.getAmount() + WorldsunderItem.unmaking(victim));
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
        if (!(event.getEntity() instanceof Player p) || event.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            return;
        }
        RealmArmorMaterial set = RealmArmorItem.fullSet(p);
        if (set == RealmArmorMaterial.GENESIS) {
            lastHeart(event, p);
            return;
        }
        if (set != RealmArmorMaterial.CHRONITE) {
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
            com.aurelia.Perf.particles(level, ParticleTypes.REVERSE_PORTAL, p.getX(), p.getY() + 1, p.getZ(), 120, 0.5, 1.0, 0.5, 0.3);
        }
        p.level().playSound(null, p.blockPosition(), SoundEvents.BELL_RESONATE, SoundSource.PLAYERS, 2.0f, 0.6f);
        p.displayClientMessage(net.minecraft.network.chat.Component.literal("Borrowed Time. The clock winds you back.")
                .withStyle(net.minecraft.ChatFormatting.LIGHT_PURPLE), true);
    }

    /** The Last Heart: Genesis refuses a killing blow once every two minutes, and the refusal throws back everything near. */
    private static void lastHeart(LivingDeathEvent event, Player p) {
        CompoundTag data = p.getPersistentData();
        long now = p.level().getGameTime();
        if (now - data.getLong(LAST_HEART) < 2400) {
            return;
        }
        data.putLong(LAST_HEART, now);
        event.setCanceled(true);
        p.setHealth(p.getMaxHealth() * 0.5f);
        p.clearFire();
        p.addEffect(new MobEffectInstance(MobEffects.ABSORPTION, 600, 3));
        p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 60, 4));
        for (LivingEntity e : p.level().getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(8.0), e -> e != p && e.isAlive()
                && !(e instanceof Player))) {
            e.hurt(p.damageSources().playerAttack(p), 12.0f);
            Vec3 out = e.position().subtract(p.position()).normalize().scale(1.8);
            e.push(out.x, 0.6, out.z);
            e.hurtMarked = true;
        }
        if (p.level() instanceof ServerLevel level) {
            com.aurelia.Perf.particles(level, ParticleTypes.SONIC_BOOM, p.getX(), p.getY() + 1, p.getZ(), 1, 0, 0, 0, 0);
            com.aurelia.Perf.particles(level, ParticleTypes.END_ROD, p.getX(), p.getY() + 1, p.getZ(), 150, 0.5, 1.0, 0.5, 0.5);
        }
        p.level().playSound(null, p.blockPosition(), SoundEvents.WARDEN_SONIC_BOOM, SoundSource.PLAYERS, 2.0f, 0.7f);
        p.level().playSound(null, p.blockPosition(), SoundEvents.TOTEM_USE, SoundSource.PLAYERS, 1.0f, 0.6f);
        p.displayClientMessage(net.minecraft.network.chat.Component.literal("The Last Heart. You were unmade, and you refused.")
                .withStyle(net.minecraft.ChatFormatting.DARK_PURPLE), true);
    }

    @SubscribeEvent
    public void onFall(LivingFallEvent event) {
        RealmArmorMaterial set = event.getEntity() instanceof Player p ? RealmArmorItem.fullSet(p) : null;
        if (set == RealmArmorMaterial.STORMGLASS || set == RealmArmorMaterial.GENESIS) {
            event.setDistance(0.0f);
            event.setDamageMultiplier(0.0f);
        }
    }
}
