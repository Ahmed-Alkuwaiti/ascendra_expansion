package com.unstablefrontiers.drowned;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.entity.DeepcallerEntity;
import com.unstablefrontiers.registry.DrownedRegistry;
import com.unstablefrontiers.registry.ModEntities;
import com.unstablefrontiers.registry.ModSounds;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;

/**
 * The Deepcaller's fight in the Sunless Vault.
 * <ul>
 * <li>Ring the abyssal bell to call it (only one at a time). Its health grows by half for each extra diver in the vault.</li>
 * <li>Everyone in the vault while it lives takes part. When it dies, each gets two Abyssal Pearls, and the Undertow the
 * first time; anyone offline gets theirs at their next login.</li>
 * <li>If nobody is in the vault for 30 s, it sinks back into the dark: it and its brood are removed. Ring again to retry.</li>
 * <li>A Deepcaller or brood that loads with no fight to belong to is turned away.</li>
 * </ul>
 */
public final class DeepcallerEncounter extends SavedData {
    private static final String NAME = "unstable_frontiers_deepcaller";
    public static final String ADD_TAG = "uf_deepcaller_add";
    public static final double ARENA_RADIUS = 24.0D;
    public static final int ABANDON_TICKS = 600;
    /** Continuous-integration only: keeps the fight engaged with no real player in the vault. */
    public static boolean trialHold;

    @Nullable
    private UUID boss;
    private long lastEngaged;
    private int kills;
    private final Set<UUID> participants = new HashSet<>();
    private final Set<UUID> undertowGiven = new HashSet<>();
    private final Map<UUID, List<String>> pending = new HashMap<>();

    public DeepcallerEncounter() {}

    public static DeepcallerEncounter get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(new SavedData.Factory<>(DeepcallerEncounter::new, DeepcallerEncounter::load), NAME);
    }

    /** The middle of the vault's flooded dome. */
    public static Vec3 center(ServerLevel level) {
        BlockPos p = DrownedPlaces.point(level, DrownedTerrain.VAULT, "centre");
        return p != null ? Vec3.atCenterOf(p) : new Vec3(DrownedTerrain.VAULT.x() + 0.5D, DrownedTerrain.VAULT.floor() + 12, DrownedTerrain.VAULT.z() + 0.5D);
    }

    public static boolean inArena(Vec3 c, Vec3 p) {
        return Math.hypot(p.x - c.x, p.z - c.z) <= ARENA_RADIUS && Math.abs(p.y - c.y) < 20;
    }

    public boolean active() {
        return boss != null;
    }

    @Nullable
    public UUID boss() {
        return boss;
    }

    public int kills() {
        return kills;
    }

    public void addParticipant(UUID u) {
        participants.add(u);
        setDirty();
    }

    public List<String> owed(UUID u) {
        return pending.getOrDefault(u, List.of());
    }

    public static List<ServerPlayer> arenaPlayers(ServerLevel level, Vec3 c) {
        List<ServerPlayer> out = new ArrayList<>();
        for (ServerPlayer p : level.players()) {
            if (p.isAlive() && !p.isSpectator() && inArena(c, p.position())) {
                out.add(p);
            }
        }
        return out;
    }

    // ---------------------------------------------------------------------------------------------------- the bell
    public static void ring(ServerLevel level, BlockPos bell, ServerPlayer by) {
        level.playSound(null, bell, ModSounds.ABYSSAL_BELL.get(), SoundSource.BLOCKS, 3.0F, 0.6F);
        summon(level, by);
    }

    /** Calls the Deepcaller. Returns true if one was called. */
    public static boolean summon(ServerLevel level, ServerPlayer by) {
        DeepcallerEncounter e = get(level);
        if (e.active()) {
            by.displayClientMessage(Component.translatable("message.unstable_frontiers.deepcaller_awake").withStyle(ChatFormatting.RED), true);
            return false;
        }
        Vec3 c = center(level);
        DeepcallerEntity boss = ModEntities.DEEPCALLER.get().create(level);
        if (boss == null) {
            return false;
        }
        List<ServerPlayer> on = arenaPlayers(level, c);
        int extra = Math.max(0, Math.min(3, on.size() - 1));
        if (extra > 0) {
            boss.getAttribute(Attributes.MAX_HEALTH).addPermanentModifier(new AttributeModifier(UnstableFrontiers.id("party"), 0.5D * extra,
                    AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
        }
        boss.setHealth(boss.getMaxHealth());
        boss.moveTo(c.x, c.y - 14, c.z, 0, 0);
        boss.setCenter(c);
        boss.setPersistenceRequired();
        e.boss = boss.getUUID();   // first: the join check turns away any Deepcaller the fight does not name
        if (!level.addFreshEntity(boss)) {
            e.boss = null;
            return false;
        }
        e.lastEngaged = level.getGameTime();
        e.participants.clear();
        for (ServerPlayer p : on) {
            e.participants.add(p.getUUID());
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.deepcaller_rises").withStyle(ChatFormatting.DARK_AQUA), false);
        }
        e.setDirty();
        return true;
    }

    // ----------------------------------------------------------------------------------------------------- the tick
    public static void tick(ServerLevel level) {
        if (level.getGameTime() % 20 != 0) {
            return;
        }
        DeepcallerEncounter e = get(level);
        if (!e.active()) {
            return;
        }
        Vec3 c = center(level);
        List<ServerPlayer> on = arenaPlayers(level, c);
        for (ServerPlayer p : on) {
            if (e.participants.add(p.getUUID())) {
                e.setDirty();
            }
        }
        if (!on.isEmpty() || trialHold) {
            e.lastEngaged = level.getGameTime();
            return;
        }
        if (level.getGameTime() - e.lastEngaged > ABANDON_TICKS) {
            e.reset(level);
        }
    }

    private void reset(ServerLevel level) {
        Entity b = boss == null ? null : level.getEntity(boss);
        if (b instanceof DeepcallerEntity d) {
            for (UUID m : d.brood()) {
                Entity mob = level.getEntity(m);
                if (mob != null) {
                    mob.discard();
                }
            }
        }
        if (b != null) {
            b.discard();
        }
        boss = null;
        setDirty();
        for (UUID u : participants) {
            if (level.getServer().getPlayerList().getPlayer(u) instanceof ServerPlayer p) {
                p.displayClientMessage(Component.translatable("message.unstable_frontiers.deepcaller_sinks").withStyle(ChatFormatting.GRAY), false);
            }
        }
        UnstableFrontiers.LOGGER.info("Deepcaller fight reset (nobody in the vault)");
    }

    public static void forceReset(ServerLevel level) {
        DeepcallerEncounter e = get(level);
        if (e.active()) {
            e.reset(level);
        }
    }

    // --------------------------------------------------------------------------------------------------- victory
    public static void victory(ServerLevel level, DeepcallerEntity dead) {
        DeepcallerEncounter e = get(level);
        if (e.boss == null || !e.boss.equals(dead.getUUID())) {
            return;
        }
        for (UUID m : dead.brood()) {
            Entity mob = level.getEntity(m);
            if (mob != null) {
                mob.kill();
            }
        }
        e.boss = null;
        e.kills++;
        for (UUID u : e.participants) {
            List<String> loot = new ArrayList<>(List.of(id(DrownedRegistry.ABYSSAL_PEARL.get()) + "*2"));
            if (e.undertowGiven.add(u)) {
                loot.add(id(DrownedRegistry.UNDERTOW.get()) + "*1");
            }
            if (level.getServer().getPlayerList().getPlayer(u) instanceof ServerPlayer p) {
                give(p, loot);
            } else {
                e.pending.computeIfAbsent(u, k -> new ArrayList<>()).addAll(loot);
            }
        }
        e.setDirty();
        for (ServerPlayer p : arenaPlayers(level, center(level))) {
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.deepcaller_falls").withStyle(ChatFormatting.GOLD), false);
        }
    }

    private static String id(Item i) {
        return BuiltInRegistries.ITEM.getKey(i).toString();
    }

    private static void give(ServerPlayer p, List<String> loot) {
        for (String s : loot) {
            String[] parts = s.split("\\*");
            ItemStack stack = new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.parse(parts[0])), Integer.parseInt(parts[1]));
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.reward", stack.getHoverName()).withStyle(ChatFormatting.GOLD), false);
            if (!p.getInventory().add(stack)) {
                p.drop(stack, false);
            }
        }
    }

    @SubscribeEvent
    public void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer p) {
            ServerLevel sea = p.server.getLevel(DrownedDimension.LEVEL);
            if (sea == null) {
                return;
            }
            DeepcallerEncounter e = get(sea);
            List<String> loot = e.pending.remove(p.getUUID());
            if (loot != null) {
                give(p, loot);
                e.setDirty();
            }
        }
    }

    @SubscribeEvent
    public void onJoin(EntityJoinLevelEvent event) {
        if (!(event.getLevel() instanceof ServerLevel level) || !DrownedDimension.is(level)) {
            return;
        }
        Entity ent = event.getEntity();
        DeepcallerEncounter e = get(level);
        if (ent instanceof DeepcallerEntity && (e.boss == null || !e.boss.equals(ent.getUUID()))) {
            event.setCanceled(true);
        } else if (ent.getPersistentData().getBoolean(ADD_TAG) && !e.active()) {
            event.setCanceled(true);
        }
    }

    // ---------------------------------------------------------------------------------------------------- saving
    private static DeepcallerEncounter load(CompoundTag t, HolderLookup.Provider registries) {
        DeepcallerEncounter e = new DeepcallerEncounter();
        if (t.hasUUID("Boss")) {
            e.boss = t.getUUID("Boss");
        }
        e.lastEngaged = t.getLong("LastEngaged");
        e.kills = t.getInt("Kills");
        for (Tag u : t.getList("Participants", Tag.TAG_INT_ARRAY)) {
            e.participants.add(NbtUtils.loadUUID(u));
        }
        for (Tag u : t.getList("Undertow", Tag.TAG_INT_ARRAY)) {
            e.undertowGiven.add(NbtUtils.loadUUID(u));
        }
        CompoundTag pend = t.getCompound("Pending");
        for (String k : pend.getAllKeys()) {
            List<String> l = new ArrayList<>();
            for (Tag s : pend.getList(k, Tag.TAG_STRING)) {
                l.add(s.getAsString());
            }
            e.pending.put(UUID.fromString(k), l);
        }
        return e;
    }

    @Override
    public CompoundTag save(CompoundTag t, HolderLookup.Provider registries) {
        if (boss != null) {
            t.putUUID("Boss", boss);
        }
        t.putLong("LastEngaged", lastEngaged);
        t.putInt("Kills", kills);
        ListTag ps = new ListTag();
        for (UUID u : participants) {
            ps.add(NbtUtils.createUUID(u));
        }
        t.put("Participants", ps);
        ListTag us = new ListTag();
        for (UUID u : undertowGiven) {
            us.add(NbtUtils.createUUID(u));
        }
        t.put("Undertow", us);
        CompoundTag pend = new CompoundTag();
        for (Map.Entry<UUID, List<String>> en : pending.entrySet()) {
            ListTag l = new ListTag();
            for (String s : en.getValue()) {
                l.add(StringTag.valueOf(s));
            }
            pend.put(en.getKey().toString(), l);
        }
        t.put("Pending", pend);
        return t;
    }
}
