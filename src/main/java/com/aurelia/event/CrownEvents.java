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
        boolean wearing = player.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.CROWN.get());
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

    /** Keep story progress (book given, return point) across death. */
    @SubscribeEvent
    public void onClone(PlayerEvent.Clone event) {
        if (event.isWasDeath()) {
            event.getEntity().getPersistentData().merge(event.getOriginal().getPersistentData());
        }
    }
}
