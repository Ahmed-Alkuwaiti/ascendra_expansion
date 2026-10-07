package com.aurelia.event;

import com.aurelia.registry.ModItems;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.LogicalSide;

public class CrownEvents {
    private static final String FLY_TAG = "aurelia_crown_flight";

    @SubscribeEvent
    public void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || event.side != LogicalSide.SERVER) {
            return;
        }
        Player player = event.player;
        boolean eternal = player.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.ETERNAL_CROWN.get());
        boolean ascendant = eternal || player.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.ASCENDANT_CROWN.get());
        boolean wearing = ascendant || player.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.CROWN.get());
        CompoundTag data = player.getPersistentData();

        if (wearing) {
            if (!player.getAbilities().mayfly) {
                player.getAbilities().mayfly = true;
                data.putBoolean(FLY_TAG, true);
                player.onUpdateAbilities();
            }
            if (player.tickCount % 40 == 0) {
                player.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 420, 0, true, false, false));
                player.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 120, 0, true, false, false));
                player.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 100, 0, true, false, false));
                player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 100, 0, true, false, false));
                if (ascendant) {
                    player.addEffect(new MobEffectInstance(MobEffects.CONDUIT_POWER, 120, 0, true, false, false));
                    player.addEffect(new MobEffectInstance(MobEffects.DOLPHINS_GRACE, 120, 0, true, false, false));
                    player.addEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 120, 0, true, false, false));
                    player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 120, 0, true, false, false));
                    player.addEffect(new MobEffectInstance(MobEffects.DIG_SPEED, 120, 0, true, false, false));
                }
                if (eternal) {
                    player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 120, 0, true, false, false));
                    player.addEffect(new MobEffectInstance(MobEffects.HEALTH_BOOST, 120, 1, true, false, false));
                    player.addEffect(new MobEffectInstance(MobEffects.SATURATION, 1, 0, true, false, false));
                }
            }
            if (ascendant && player.getTicksFrozen() > 0) {
                player.setTicksFrozen(0);
            }
        } else if (data.getBoolean(FLY_TAG)) {
            data.putBoolean(FLY_TAG, false);
            if (!player.isCreative() && !player.isSpectator()) {
                player.getAbilities().mayfly = false;
                player.getAbilities().flying = false;
                player.onUpdateAbilities();
            }
        }
    }

    /** Reforging the Crown points the player at act two; finishing the Ascendant Crown closes the story. */
    @SubscribeEvent
    public void onCrafted(PlayerEvent.ItemCraftedEvent event) {
        if (event.getEntity().level().isClientSide) {
            return;
        }
        if (event.getCrafting().is(ModItems.CROWN.get())) {
            com.aurelia.world.Story.narrate(event.getEntity(), "The crown is whole, and warm, and wrong: three of its settings sit empty. "
                    + "Far away, under the sea, a bell rings once. Look for the Tidewrack Citadel in the ocean.");
        } else if (event.getCrafting().is(ModItems.ETERNAL_CROWN.get())) {
            com.aurelia.world.Story.narrate(event.getEntity(), "The core stops ticking. The heart stops growing. The crown is eternal, and so, nearly, are you.");
        } else if (event.getCrafting().is(ModItems.ASCENDANT_CROWN.get())) {
            com.aurelia.world.Story.narrate(event.getEntity(), "Pearl, tear and hourglass settle into place. For a moment you hear all six realms "
                    + "at once: the garden, the wind, the dark, the sea, the silence and the sand. Then, under them, something ticking, "
                    + "and something growing. Look for the Paradox Keep on the open plains.");
        }
    }

    /** The Eternal Crown: once every five minutes, a killing blow stops time instead of killing you. */
    @SubscribeEvent
    public void onDeath(net.minecraftforge.event.entity.living.LivingDeathEvent event) {
        if (!(event.getEntity() instanceof Player player) || player.level().isClientSide
                || !player.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.ETERNAL_CROWN.get())) {
            return;
        }
        CompoundTag data = player.getPersistentData();
        long now = player.level().getGameTime();
        if (now - data.getLong("aurelia_eternal_last") < 6000) {
            return;
        }
        data.putLong("aurelia_eternal_last", now);
        event.setCanceled(true);
        player.setHealth(player.getMaxHealth() * 0.5f);
        player.removeAllEffects();
        player.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 200, 2));
        player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 100, 3));
        for (net.minecraft.world.entity.LivingEntity near : player.level().getEntitiesOfClass(net.minecraft.world.entity.LivingEntity.class,
                player.getBoundingBox().inflate(12.0), e -> e != player)) {
            near.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 4));
        }
        com.aurelia.world.Story.narrate(player, "The Hour Core in your crown stops time a heartbeat before the end. You get the heartbeat back.");
    }

    /** Keep story progress (book given, return point) across death. */
    @SubscribeEvent
    public void onClone(PlayerEvent.Clone event) {
        if (event.isWasDeath()) {
            event.getEntity().getPersistentData().merge(event.getOriginal().getPersistentData());
        }
    }
}
