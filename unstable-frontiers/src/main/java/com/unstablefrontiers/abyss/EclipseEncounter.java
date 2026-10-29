package com.unstablefrontiers.abyss;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.entity.EclipseLeviathanEntity;
import com.unstablefrontiers.registry.AbyssRegistry;
import com.unstablefrontiers.registry.ModEntities;
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
 * The Hollow Crown's fight, as world state:
 * <ul>
 * <li>An Eclipse Sigil at the altar calls the Leviathan (only one at a time). Its health grows by half for each extra
 * fighter on the arena when it rises, up to four.</li>
 * <li>Everyone who stands on the arena during the fight is a participant. When it dies, each participant gets two
 * Eclipse Scales and two Starmetal Ingots, and the Corona the first time; anyone away (logged out) gets theirs when they
 * next log in.</li>
 * <li>If nobody is on the arena for thirty seconds (everyone died, fled, or logged out), it sinks back: it and its mites are
 * removed, and the altar stays charged so the next call costs no sigil.</li>
 * <li>A Leviathan that loads without a live fight (a crash, a restore from backup) is removed.</li>
 * </ul>
 */
public final class EclipseEncounter extends SavedData {
    private static final String NAME = "unstable_frontiers_eclipse";
    public static final String ADD_TAG = "uf_eclipse_add";
    public static final double ARENA_RADIUS = 40.0D;
    public static final int ABANDON_TICKS = 600;
    /** Continuous-integration only: keeps the fight engaged with no real player in the arena. */
    public static boolean trialHold;

    @Nullable
    private UUID boss;
    private boolean charged;
    private long lastEngaged;
    private int kills;
    private final Set<UUID> participants = new HashSet<>();
    private final Set<UUID> coronaGiven = new HashSet<>();
    private final Map<UUID, List<String>> pending = new HashMap<>();

    public static EclipseEncounter get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(new SavedData.Factory<>(EclipseEncounter::new, EclipseEncounter::load), NAME);
    }

    public static Vec3 center() {
        return AbyssPlaces.standing(AbyssTerrain.HOLLOW_CROWN);
    }

    public static boolean inArena(Vec3 c, Vec3 p) {
        return Math.hypot(p.x - c.x, p.z - c.z) <= ARENA_RADIUS && p.y > c.y - 12 && p.y < c.y + 40;
    }

    public boolean active() {
        return boss != null;
    }

    // ---------------------------------------------------------------------------------------------- the altar
    /** Calls the Leviathan. Returns true if a sigil was used (false: nothing happened, or the charge paid for it). */
    public static boolean summon(ServerLevel level, BlockPos altar, ServerPlayer by) {
        EclipseEncounter e = get(level);
        if (e.active()) {
            by.displayClientMessage(Component.translatable("message.unstable_frontiers.eclipse_awake").withStyle(ChatFormatting.RED), true);
            return false;
        }
        boolean free = e.charged;
        Vec3 c = center();
        EclipseLeviathanEntity boss = ModEntities.ECLIPSE_LEVIATHAN.get().create(level);
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
        boss.moveTo(c.x, c.y - 24, c.z, 0, 0);
        boss.setCenter(c);
        boss.setPersistenceRequired();
        level.addFreshEntity(boss);
        e.boss = boss.getUUID();
        e.charged = false;
        e.lastEngaged = level.getGameTime();
        e.participants.clear();
        for (ServerPlayer p : on) {
            e.participants.add(p.getUUID());
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.eclipse_rises").withStyle(ChatFormatting.LIGHT_PURPLE), false);
        }
        e.setDirty();
        return !free;
    }

    public static void describe(ServerLevel level, BlockPos altar, ServerPlayer p) {
        EclipseEncounter e = get(level);
        if (e.charged && !e.active()) {
            // a charged altar answers an empty hand
            summon(level, altar, p);
            return;
        }
        p.displayClientMessage(Component.translatable(e.active() ? "message.unstable_frontiers.eclipse_awake" : "message.unstable_frontiers.eclipse_altar",
                e.kills).withStyle(ChatFormatting.GRAY), false);
    }

    // ----------------------------------------------------------------------------------------------- the tick
    public static void tick(ServerLevel level) {
        if (level.getGameTime() % 20 != 0) {
            return;
        }
        EclipseEncounter e = get(level);
        if (!e.active()) {
            return;
        }
        Vec3 c = center();
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
            e.reset(level, "message.unstable_frontiers.eclipse_sinks");
        }
    }

    private void reset(ServerLevel level, String why) {
        Entity b = boss == null ? null : level.getEntity(boss);
        if (b instanceof EclipseLeviathanEntity lev) {
            for (UUID m : lev.mites()) {
                Entity mite = level.getEntity(m);
                if (mite != null) {
                    mite.discard();
                }
            }
        }
        if (b != null) {
            b.discard();
        }
        boss = null;
        charged = true;
        setDirty();
        for (UUID u : participants) {
            if (level.getServer().getPlayerList().getPlayer(u) instanceof ServerPlayer p) {
                p.displayClientMessage(Component.translatable(why).withStyle(ChatFormatting.GRAY), false);
            }
        }
        UnstableFrontiers.LOGGER.info("Eclipse Leviathan fight reset ({})", why);
    }

    /** For operator commands and tests. */
    public static void forceReset(ServerLevel level) {
        EclipseEncounter e = get(level);
        if (e.active()) {
            e.reset(level, "message.unstable_frontiers.eclipse_sinks");
        }
    }

    // ------------------------------------------------------------------------------------------------ victory
    public static void victory(ServerLevel level, EclipseLeviathanEntity dead) {
        EclipseEncounter e = get(level);
        if (e.boss == null || !e.boss.equals(dead.getUUID())) {
            return;
        }
        for (UUID m : dead.mites()) {
            Entity mite = level.getEntity(m);
            if (mite != null) {
                mite.kill();
            }
        }
        e.boss = null;
        e.kills++;
        for (UUID u : e.participants) {
            List<String> loot = new ArrayList<>(List.of(id(AbyssRegistry.ECLIPSE_SCALE.get()) + "*2", id(AbyssRegistry.STARMETAL_INGOT.get()) + "*2"));
            if (e.coronaGiven.add(u)) {
                loot.add(id(AbyssRegistry.CORONA.get()) + "*1");
            }
            if (level.getServer().getPlayerList().getPlayer(u) instanceof ServerPlayer p) {
                give(p, loot);
            } else {
                e.pending.computeIfAbsent(u, k -> new ArrayList<>()).addAll(loot);
            }
        }
        e.setDirty();
        for (ServerPlayer p : arenaPlayers(level, center())) {
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.eclipse_falls").withStyle(ChatFormatting.GOLD), false);
        }
    }

    private static String id(Item i) {
        return BuiltInRegistries.ITEM.getKey(i).toString();
    }

    private static void give(ServerPlayer p, List<String> loot) {
        for (String s : loot) {
            String[] parts = s.split("\\*");
            Item item = BuiltInRegistries.ITEM.get(ResourceLocation.parse(parts[0]));
            ItemStack stack = new ItemStack(item, Integer.parseInt(parts[1]));
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.reward", stack.getHoverName()).withStyle(ChatFormatting.GOLD), false);
            if (!p.getInventory().add(stack)) {
                p.drop(stack, false);
            }
        }
    }

    @SubscribeEvent
    public void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer p) {
            ServerLevel abyss = p.server.getLevel(AbyssDimension.LEVEL);
            if (abyss == null) {
                return;
            }
            EclipseEncounter e = get(abyss);
            List<String> loot = e.pending.remove(p.getUUID());
            if (loot != null) {
                give(p, loot);
                e.setDirty();
            }
        }
    }

    /** A Leviathan or one of its mites that loads with no live fight to belong to is turned away. */
    @SubscribeEvent
    public void onJoin(EntityJoinLevelEvent event) {
        if (!(event.getLevel() instanceof ServerLevel level) || !AbyssDimension.is(level)) {
            return;
        }
        Entity ent = event.getEntity();
        EclipseEncounter e = get(level);
        if (ent instanceof EclipseLeviathanEntity && (e.boss == null || !e.boss.equals(ent.getUUID()))) {
            event.setCanceled(true);
        } else if (ent.getPersistentData().getBoolean(ADD_TAG) && !e.active()) {
            event.setCanceled(true);
        }
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

    public int kills() {
        return kills;
    }

    public boolean charged() {
        return charged;
    }

    @Nullable
    public UUID boss() {
        return boss;
    }

    /** For tests: counts someone (a stand-in) as having fought, so the victory owes them its rewards. */
    public void addParticipant(UUID u) {
        participants.add(u);
        setDirty();
    }

    /** Rewards waiting for someone who was not online at the victory. */
    public List<String> owed(UUID u) {
        return pending.getOrDefault(u, List.of());
    }

    // ------------------------------------------------------------------------------------------------- saving
    private static EclipseEncounter load(CompoundTag t, HolderLookup.Provider registries) {
        EclipseEncounter e = new EclipseEncounter();
        if (t.hasUUID("Boss")) {
            e.boss = t.getUUID("Boss");
        }
        e.charged = t.getBoolean("Charged");
        e.lastEngaged = t.getLong("LastEngaged");
        e.kills = t.getInt("Kills");
        for (Tag u : t.getList("Participants", Tag.TAG_INT_ARRAY)) {
            e.participants.add(NbtUtils.loadUUID(u));
        }
        for (Tag u : t.getList("Corona", Tag.TAG_INT_ARRAY)) {
            e.coronaGiven.add(NbtUtils.loadUUID(u));
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
        t.putBoolean("Charged", charged);
        t.putLong("LastEngaged", lastEngaged);
        t.putInt("Kills", kills);
        ListTag ps = new ListTag();
        for (UUID u : participants) {
            ps.add(NbtUtils.createUUID(u));
        }
        t.put("Participants", ps);
        ListTag cs = new ListTag();
        for (UUID u : coronaGiven) {
            cs.add(NbtUtils.createUUID(u));
        }
        t.put("Corona", cs);
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
