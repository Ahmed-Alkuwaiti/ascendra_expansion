package com.aurelia.event;

import com.aurelia.item.CharmItem;
import com.aurelia.world.Realm;
import java.util.EnumSet;
import java.util.Set;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** Every two seconds, each Realm Charm a player carries renews its boon. */
public class CharmEvents {
    private static final int PERIOD = 40;
    private static final int LENGTH = 260;                                    // long enough that night vision never flickers

    @SubscribeEvent
    public void onPlayerTick(TickEvent.PlayerTickEvent event) {
        Player player = event.player;
        if (event.phase != TickEvent.Phase.END || player.level().isClientSide || player.tickCount % PERIOD != 0) {
            return;
        }
        Set<Realm> held = EnumSet.noneOf(Realm.class);
        for (ItemStack stack : player.getInventory().items) {
            if (stack.getItem() instanceof CharmItem charm) {
                held.add(charm.realm);
            }
        }
        for (ItemStack stack : player.getInventory().offhand) {
            if (stack.getItem() instanceof CharmItem charm) {
                held.add(charm.realm);
            }
        }
        for (Realm realm : held) {
            switch (realm) {
                case GROVE -> {                                                // the Grove's charm mends you only when you are hurt
                    if (player.getHealth() < player.getMaxHealth() * 0.5f) {
                        player.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 60, 0, true, false, true));
                    }
                }
                case SKYREACH -> give(player, MobEffects.SLOW_FALLING);
                case HOLLOW -> give(player, MobEffects.FIRE_RESISTANCE);
                case DROWNED -> {
                    give(player, MobEffects.WATER_BREATHING);
                    give(player, MobEffects.DOLPHINS_GRACE);
                }
                case PALE -> {
                    give(player, MobEffects.NIGHT_VISION);
                    player.setTicksFrozen(0);                                  // the cold cannot take hold
                }
                case SCARLET -> give(player, MobEffects.DIG_SPEED);
                case CLOCKWORK -> give(player, MobEffects.MOVEMENT_SPEED);
                case MYCELIAL -> {
                    player.removeEffect(MobEffects.POISON);                    // spores and venom cannot take hold
                    player.removeEffect(MobEffects.CONFUSION);
                    give(player, MobEffects.LUCK);
                }
                case LAST -> {
                    give(player, MobEffects.DAMAGE_BOOST);
                    give(player, MobEffects.DAMAGE_RESISTANCE);
                }
            }
        }
    }

    private static void give(Player player, MobEffect effect) {
        player.addEffect(new MobEffectInstance(effect, LENGTH, 0, true, false, true));
    }
}
