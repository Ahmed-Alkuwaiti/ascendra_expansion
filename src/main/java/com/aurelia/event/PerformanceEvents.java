package com.aurelia.event;

import com.aurelia.AureliaConfig;
import com.aurelia.entity.AureliaBoss;
import com.aurelia.entity.Lieutenant;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Lets the mod's guards doze. A citadel, a lair ring or a dungeon can hold dozens of guards, and every one ticks its AI while its
 * chunk is loaded, whether anyone is near or not. A guard with no player within the configured distance, no target and no fresh
 * hurt skips its ticks, waking for one every so often, and wakes fully the moment a player comes in range. Wardens and lieutenants
 * never doze.
 */
public class PerformanceEvents {
    @SubscribeEvent(priority = EventPriority.HIGH)
    public void onLivingTick(LivingEvent.LivingTickEvent event) {
        LivingEntity entity = event.getEntity();
        if (entity.level().isClientSide || !(entity instanceof Mob mob) || !(entity instanceof Enemy)
                || entity instanceof AureliaBoss || entity instanceof Lieutenant || !entity.getClass().getName().startsWith("com.aurelia.")) {
            return;
        }
        int distance = AureliaConfig.GUARD_SLEEP_DISTANCE.get();
        if (distance <= 0 || mob.getTarget() != null || mob.hurtTime > 0 || mob.isOnFire()) {
            return;
        }
        if ((mob.level().getGameTime() + mob.getId()) % AureliaConfig.GUARD_SLEEP_INTERVAL.get() == 0) {
            return;                                                     // its occasional tick, spread across guards so they never all tick at once
        }
        if (mob.level().hasNearbyAlivePlayer(mob.getX(), mob.getY(), mob.getZ(), distance)) {
            return;
        }
        event.setCanceled(true);
    }
}
