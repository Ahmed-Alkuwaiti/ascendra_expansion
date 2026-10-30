package com.unstablefrontiers.ecology;

import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.encounter.CageBeacons;
import com.unstablefrontiers.encounter.Elites;
import com.unstablefrontiers.encounter.EncounterManager;
import com.unstablefrontiers.item.ShackleItem;
import com.unstablefrontiers.landmark.FrontierData;
import com.unstablefrontiers.world.FrontierDimension;
import java.util.Iterator;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.entity.living.FinalizeSpawnEvent;
import net.neoforged.neoforge.event.entity.living.LivingChangeTargetEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.living.LivingDropsEvent;
import net.neoforged.neoforge.event.entity.living.LivingExperienceDropEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * Server-side hooks for the frontier. Everything is limited to the frontier dimension and to creatures this mod placed
 * (plus creatures bound with the Shackle, wherever they are).
 *
 * <p>Loot eligibility: a frontier creature drops items and experience only if a player hurt it recently, so predators
 * killing prey (or a fight nobody watched) never piles up items, and at most maxDropsPerMob stacks drop.
 */
public final class FrontierEvents {
    @SubscribeEvent
    public void onServerTick(ServerTickEvent.Post event) {
        for (ServerLevel l : event.getServer().getAllLevels()) {
            ShackleItem.tick(l, l.getGameTime());
        }
        ServerLevel abyss = event.getServer().getLevel(com.unstablefrontiers.abyss.AbyssDimension.LEVEL);
        // the abyss's fights and places run while someone is there, while the Leviathan's fight is on, or where an operator force-loads it
        if (abyss != null && (!abyss.players().isEmpty() || com.unstablefrontiers.abyss.EclipseEncounter.get(abyss).active()
                || !abyss.getForcedChunks().isEmpty())) {
            com.unstablefrontiers.abyss.AbyssPlaces.tick(abyss);
            com.unstablefrontiers.abyss.EclipseEncounter.tick(abyss);
            EncounterManager.tick(abyss);
        }
        ServerLevel drowned = event.getServer().getLevel(com.unstablefrontiers.drowned.DrownedDimension.LEVEL);
        // the same for the Drowned Expanse and the Deepcaller's fight
        if (drowned != null && (!drowned.players().isEmpty() || com.unstablefrontiers.drowned.DeepcallerEncounter.get(drowned).active()
                || !drowned.getForcedChunks().isEmpty())) {
            com.unstablefrontiers.drowned.DrownedPlaces.tick(drowned);
            com.unstablefrontiers.drowned.DeepcallerEncounter.tick(drowned);
            EncounterManager.tick(drowned);
        }
        ServerLevel level = event.getServer().getLevel(FrontierDimension.LEVEL);
        if (level == null || level.players().isEmpty() && !EncounterManager.anyActive(level)) {
            return;
        }
        long time = level.getGameTime();
        EncounterManager.tick(level);
        Rivalry.tick(level, time);
        Overflight.tick(level, time);
    }

    /** A landmark creature whose fight was reset or finished while its chunk was unloaded is turned away when it loads. */
    @SubscribeEvent(priority = EventPriority.HIGH)
    public void onJoin(EntityJoinLevelEvent event) {
        Entity e = event.getEntity();
        if (!(event.getLevel() instanceof ServerLevel level) || !Creatures.isEncounter(e)) {
            return;
        }
        if (!FrontierDimension.is(level) && !com.unstablefrontiers.abyss.AbyssDimension.is(level)
                && !com.unstablefrontiers.drowned.DrownedDimension.is(level) || !EncounterManager.belongs(level, e)) {
            event.setCanceled(true);
        }
    }

    @SubscribeEvent
    public void onDeath(LivingDeathEvent event) {
        Entity e = event.getEntity();
        if (e.level() instanceof ServerLevel level && (Creatures.isEncounter(e) || Creatures.isResident(e))) {
            EncounterManager.onDeath(level, e);
        }
    }

    @SubscribeEvent
    public void onDamage(LivingIncomingDamageEvent event) {
        Entity e = event.getEntity();
        if (!(e.level() instanceof ServerLevel level) || !Creatures.isEncounter(e)) {
            return;
        }
        if (Creatures.isDormant(e)) {
            EncounterManager.provoke(level, e, event.getSource().getEntity() instanceof ServerPlayer p ? p : null);
        }
        event.setAmount(Elites.shield(level, e, event.getAmount()));
    }

    /** A bound creature never turns on players. */
    @SubscribeEvent
    public void onTarget(LivingChangeTargetEvent event) {
        if (event.getNewAboutToBeSetTarget() instanceof Player && ShackleItem.isBound(event.getEntity())) {
            event.setCanceled(true);
        }
    }

    /** The Great Cage's pylon cores are crying obsidian; while its fight runs they break about ten times faster. */
    @SubscribeEvent
    public void onBreakSpeed(PlayerEvent.BreakSpeed event) {
        if (event.getEntity().level() instanceof ServerLevel level && FrontierDimension.is(level) && event.getPosition().isPresent()
                && Elites.isActivePylon(level, event.getPosition().get())) {
            event.setNewSpeed(event.getNewSpeed() * 10.0F);
        }
    }

    /** Safe ground around a Cage Beacon: nothing spawns there naturally. */
    @SubscribeEvent
    public void onFinalizeSpawn(FinalizeSpawnEvent event) {
        if (event.getLevel().getLevel() instanceof ServerLevel level && FrontierDimension.is(level)
                && (event.getSpawnType() == MobSpawnType.NATURAL || event.getSpawnType() == MobSpawnType.CHUNK_GENERATION)
                && CageBeacons.covers(level, event.getEntity().blockPosition())) {
            event.setSpawnCancelled(true);
        }
        // The Abyss: no natural spawns on the landing or in the Hollow Crown, and at most 8 of its creatures near any spot.
        if (event.getLevel().getLevel() instanceof ServerLevel level && com.unstablefrontiers.abyss.AbyssDimension.is(level)
                && (event.getSpawnType() == MobSpawnType.NATURAL || event.getSpawnType() == MobSpawnType.CHUNK_GENERATION)
                && com.unstablefrontiers.abyss.AbyssDimension.crowded(level, event.getEntity().position())) {
            event.setSpawnCancelled(true);
        }
        // The Drowned Expanse: nothing hostile spawns naturally inside a shelter or place, and at most 8 creatures near any spot.
        if (event.getLevel().getLevel() instanceof ServerLevel level && com.unstablefrontiers.drowned.DrownedDimension.is(level)
                && (event.getSpawnType() == MobSpawnType.NATURAL || event.getSpawnType() == MobSpawnType.CHUNK_GENERATION)
                && com.unstablefrontiers.drowned.DrownedDimension.crowded(level, event.getEntity())) {
            event.setSpawnCancelled(true);
        }
    }

    /** Operators are told about data problems (missing creatures, broken rosters) when they join. */
    @SubscribeEvent
    public void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        List<String> problems = FrontierData.problems();
        if (problems.isEmpty() || !(event.getEntity() instanceof ServerPlayer p) || !p.hasPermissions(2)) {
            return;
        }
        p.displayClientMessage(Component.translatable("message.unstable_frontiers.problems", problems.size()).withStyle(ChatFormatting.RED), false);
        for (int i = 0; i < Math.min(3, problems.size()); i++) {
            p.displayClientMessage(Component.literal(" - " + problems.get(i)).withStyle(ChatFormatting.GRAY), false);
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
        ShackleItem.clearMemory();
        Overflight.clearMemory();
    }
}
