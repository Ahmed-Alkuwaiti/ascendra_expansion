package com.unstablefrontiers.item;

import com.unstablefrontiers.ecology.Creatures;
import com.unstablefrontiers.entity.ChainedMatriarchEntity;
import com.unstablefrontiers.entity.GnashbackEntity;
import com.unstablefrontiers.entity.ShrikewingEntity;
import com.unstablefrontiers.registry.ModAttachments;
import com.unstablefrontiers.registry.ModItems;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.EntityTypeTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.living.LivingChangeTargetEvent;
import net.neoforged.neoforge.event.entity.living.LivingFallEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.living.LivingKnockBackEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * What the creatures' gear does, and the one-line hint each creature gives the first time it hunts you:
 * <ul>
 * <li>Gnashback Carapace (full set): no knockback, and insects deal 25% less damage.</li>
 * <li>Shrike Impaler: double damage to anything airborne; flyers are driven down, Shrikewings grounded.</li>
 * <li>Matriarch's Mantle: Wingsail glide and no fall damage; the brood truce.</li>
 * </ul>
 */
public final class CreatureGearEvents {
    private static final TagKey<EntityType<?>> BOSSES = TagKey.create(Registries.ENTITY_TYPE, ResourceLocation.fromNamespaceAndPath("c", "bosses"));

    public static boolean isInsect(Entity e) {
        return e != null && (e.getType().is(EntityTypeTags.ARTHROPOD) || e.getType().is(Creatures.INSECTS) || e instanceof GnashbackEntity);
    }

    public static boolean fullCarapace(LivingEntity e) {
        return e.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.CARAPACE_HELMET.get())
                && e.getItemBySlot(EquipmentSlot.CHEST).is(ModItems.CARAPACE_CHESTPLATE.get())
                && e.getItemBySlot(EquipmentSlot.LEGS).is(ModItems.CARAPACE_LEGGINGS.get())
                && e.getItemBySlot(EquipmentSlot.FEET).is(ModItems.CARAPACE_BOOTS.get());
    }

    @SubscribeEvent
    public void onDamage(LivingIncomingDamageEvent event) {
        LivingEntity victim = event.getEntity();
        Entity attacker = event.getSource().getEntity();
        if (victim.level().isClientSide) {
            return;
        }
        // the carapace
        if (attacker != null && isInsect(attacker) && fullCarapace(victim)) {
            event.setAmount(event.getAmount() * 0.75F);
        }
        // the impaler: a melee strike by its holder
        if (attacker instanceof Player p && event.getSource().getDirectEntity() == p && p.getMainHandItem().is(ModItems.SHRIKE_IMPALER.get())
                && ShrikeImpalerItem.airborne(victim)) {
            event.setAmount(event.getAmount() * 2.0F);
            if (victim instanceof ShrikewingEntity s) {
                s.ground();
            } else {
                Vec3 v = victim.getDeltaMovement();
                victim.setDeltaMovement(v.x * 0.3D, Math.min(v.y, -0.9D), v.z * 0.3D);
                victim.hurtMarked = true;
            }
            if (victim.level() instanceof ServerLevel sl) {
                sl.sendParticles(ParticleTypes.CRIT, victim.getX(), victim.getY() + victim.getBbHeight() / 2, victim.getZ(), 12, 0.4D, 0.4D, 0.4D, 0.2D);
            }
        }
    }

    @SubscribeEvent
    public void onKnockback(LivingKnockBackEvent event) {
        if (fullCarapace(event.getEntity())) {
            event.setCanceled(true);
        }
    }

    @SubscribeEvent
    public void onFall(LivingFallEvent event) {
        if (event.getEntity() instanceof Player p && MatriarchMantleItem.carried(p, ModItems.MATRIARCH_MANTLE.get())) {
            event.setDamageMultiplier(0);
        }
    }

    @SubscribeEvent
    public void onPlayerTick(PlayerTickEvent.Post event) {
        Player p = event.getEntity();
        if (p.level().isClientSide || p.tickCount % 5 != 0 || p.isSpectator()) {
            return;
        }
        if (p.fallDistance > 3.0F && !p.onGround() && !p.isShiftKeyDown() && !p.isFallFlying() && !p.getAbilities().flying
                && p.getDeltaMovement().y < 0 && MatriarchMantleItem.carried(p, ModItems.MATRIARCH_MANTLE.get())) {
            p.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 15, 0, false, false, true));
        }
    }

    @SubscribeEvent
    public void onTarget(LivingChangeTargetEvent event) {
        if (!(event.getNewAboutToBeSetTarget() instanceof ServerPlayer p)) {
            return;
        }
        LivingEntity hunter = event.getEntity();
        // the brood truce: insects leave the Mantle's bearer alone unless the bearer struck first
        if (isInsect(hunter) && !(hunter instanceof ChainedMatriarchEntity) && !hunter.getType().is(BOSSES)
                && hunter.getLastHurtByMob() != p && MatriarchMantleItem.carried(p, ModItems.MATRIARCH_MANTLE.get())
                && !(hunter instanceof Mob m && Creatures.isEncounter(m))) {
            event.setCanceled(true);
            return;
        }
        // the first time each frontier creature hunts a player, one line on how to fight it
        String key = hunter instanceof GnashbackEntity ? "gnashback" : hunter instanceof ShrikewingEntity ? "shrikewing"
                : hunter instanceof ChainedMatriarchEntity ? "chained_matriarch" : null;
        if (key != null) {
            CompoundTag d = ModAttachments.of(p);
            if (!d.getBoolean("hint_" + key)) {
                d.putBoolean("hint_" + key, true);
                p.displayClientMessage(Component.translatable("hint.unstable_frontiers." + key).withStyle(ChatFormatting.YELLOW), false);
            }
        }
    }
}
