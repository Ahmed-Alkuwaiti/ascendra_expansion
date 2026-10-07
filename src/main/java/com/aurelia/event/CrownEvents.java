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
        boolean ascendant = player.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.ASCENDANT_CROWN.get());
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
        } else if (event.getCrafting().is(ModItems.ASCENDANT_CROWN.get())) {
            com.aurelia.world.Story.narrate(event.getEntity(), "Pearl, tear and hourglass settle into place. For a moment you hear all six realms "
                    + "at once: the garden, the wind, the dark, the sea, the silence and the sand. Then only your own heartbeat. It is finished.");
        }
    }

    /** Keep story progress (book given, return point) across death. */
    @SubscribeEvent
    public void onClone(PlayerEvent.Clone event) {
        if (event.isWasDeath()) {
            event.getEntity().getPersistentData().merge(event.getOriginal().getPersistentData());
        }
    }
}
