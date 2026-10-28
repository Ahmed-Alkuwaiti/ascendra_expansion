package com.unstablefrontiers.ecology;

import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.encounter.EncounterManager;
import com.unstablefrontiers.world.FrontierDimension;
import java.util.Iterator;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.event.entity.living.LivingExperienceDropEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Server-side hooks for the frontier. Everything is limited to the frontier dimension and to creatures this mod spawned.
 *
 * <p>Loot eligibility: a frontier creature drops items and experience only if a player hurt it recently, so predators
 * killing prey (or a tower fight nobody watched) never piles up items, and at most maxDropsPerMob stacks drop.
 */
public final class FrontierEvents {
    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        ServerLevel level = event.getServer().getLevel(FrontierDimension.LEVEL);
        if (level == null || level.players().isEmpty() && !EncounterManager.anyActive(level)) {
            return;
        }
        long time = level.getGameTime();
        EncounterManager.tick(level);
        AmbientDirector.tick(level, time);
        Rivalry.tick(level, time);
    }

    /** A tower creature whose fight was reset or finished while its chunk was unloaded is turned away when it loads. */
    @SubscribeEvent(priority = EventPriority.HIGH)
    public void onJoin(EntityJoinLevelEvent event) {
        Entity e = event.getEntity();
        if (!(event.getLevel() instanceof ServerLevel level) || !Creatures.isEncounter(e)) {
            return;
        }
        if (!FrontierDimension.is(level) || !EncounterManager.belongs(level, e)) {
            event.setCanceled(true);
        }
    }

    @SubscribeEvent
    public void onDeath(LivingDeathEvent event) {
        Entity e = event.getEntity();
        if (e.level() instanceof ServerLevel level && Creatures.isEncounter(e)) {
            EncounterManager.onDeath(level, e);
        }
    }

    @SubscribeEvent(priority = EventPriority.LOW)
    public void onDrops(LivingDropsEvent event) {
        if (!Creatures.isOurs(event.getEntity())) {
            return;
        }
        if (!event.isRecentlyHit()) {
            event.setCanceled(true);
            return;
        }
        int max = FrontierConfig.dropsPerMob();
        Iterator<ItemEntity> it = event.getDrops().iterator();
        for (int n = 0; it.hasNext(); n++) {
            it.next();
            if (n >= max) {
                it.remove();
            }
        }
    }

    @SubscribeEvent(priority = EventPriority.LOW)
    public void onExperience(LivingExperienceDropEvent event) {
        if (Creatures.isOurs(event.getEntity()) && event.getAttackingPlayer() == null) {
            event.setCanceled(true);
        }
    }

    @SubscribeEvent
    public void onStopped(ServerStoppedEvent event) {
        EncounterManager.clearMemory();
        Rivalry.clearMemory();
    }
}
