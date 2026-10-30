package com.unstablefrontiers.drowned;

import com.unstablefrontiers.registry.ModAttachments;
import com.unstablefrontiers.registry.ModSounds;
import com.unstablefrontiers.travel.RiftTravel;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.living.LivingDropsEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.EntityTickEvent;

/**
 * Getting to and around the Drowned Expanse, and getting out of trouble there.
 * <ul>
 * <li><b>In</b>: the tide gate at the bottom of a frontier Sunken Gate, wearing Abyssal Goggles and a Diving Rig (or a
 * Breath Charm in place of the rig). Without them the gate refuses and says what is missing. You arrive inside the
 * Tidewatch Station's air dome.</li>
 * <li><b>Out</b>: the Tidewatch's tide gate, the Rift Shard or /frontier return: back to where you came in.</li>
 * <li><b>Shelters</b>: ring a station's tide bell to make it your shelter; sneak and ring to travel to the next shelter
 * you have rung.</li>
 * <li><b>Black-outs</b>: run out of air and fall low on health, and the tide carries you back to your shelter, unhurt
 * further, once a minute at most. Nothing is taken from you.</li>
 * <li><b>Drops</b>: items sink (they do not float off 200 blocks up) and keep for fifteen minutes after a death; you are
 * told where.</li>
 * </ul>
 */
public final class DrownedTravel {
    private static final String RETURN = "drowned_return";
    private static final String SHELTER = "drowned_shelter";
    private static final String BELLS = "drowned_bells";
    private static final String WELCOMED = "drowned_welcomed";
    private static final String GATE_COOLDOWN = "uf_tide_gate_cooldown";
    private static final String REFUSED = "uf_tide_gate_refused";
    private static final String RESCUED = "uf_drowned_rescued";

    public DrownedTravel() {}

    // -------------------------------------------------------------------------------------------------- the gate
    public static void throughGate(ServerPlayer p, BlockPos gate) {
        long now = p.level().getGameTime();
        CompoundTag d = p.getPersistentData();
        if (now - d.getLong(GATE_COOLDOWN) < 60 && d.getLong(GATE_COOLDOWN) <= now) {
            return;
        }
        if (DrownedDimension.is(p.level())) {
            d.putLong(GATE_COOLDOWN, now);
            leave(p);
            return;
        }
        Component missing = missingGear(p);
        if (missing != null) {
            if (now - d.getLong(REFUSED) > 80 || d.getLong(REFUSED) > now) {
                d.putLong(REFUSED, now);
                p.displayClientMessage(Component.translatable("message.unstable_frontiers.tide_gate_refuses", missing).withStyle(ChatFormatting.GOLD), false);
                p.level().playSound(null, gate, ModSounds.TIDE_GATE_REFUSE.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
            }
            return;
        }
        d.putLong(GATE_COOLDOWN, now);
        enter(p, gate);
    }

    /** What the gate still wants before it lets this player through, or null. */
    @Nullable
    public static Component missingGear(Player p) {
        boolean goggles = !DrownedGear.goggles(p).isEmpty();
        boolean air = !DrownedGear.rig(p).isEmpty() || DrownedGear.charm(p);
        if (goggles && air) {
            return null;
        }
        if (!goggles && !air) {
            return Component.translatable("message.unstable_frontiers.need_both");
        }
        return Component.translatable(goggles ? "message.unstable_frontiers.need_rig" : "message.unstable_frontiers.need_goggles");
    }

    public static void enter(ServerPlayer p, @Nullable BlockPos gate) {
        ServerLevel sea = p.server.getLevel(DrownedDimension.LEVEL);
        if (sea == null) {
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.no_drowned").withStyle(ChatFormatting.RED), false);
            return;
        }
        CompoundTag ret = new CompoundTag();
        ret.putString("Dim", p.level().dimension().location().toString());
        Vec3 back = gate != null ? Vec3.atBottomCenterOf(gate).add(0, 0, 3) : p.position();
        if (gate != null) {
            // come back beside the pool, on dry ground, not into the gate again
            BlockPos dry = RiftTravel.safeSpot((ServerLevel) p.level(), gate.getX() + 6, gate.getZ());
            back = Vec3.atBottomCenterOf(dry);
        }
        ret.putDouble("X", back.x);
        ret.putDouble("Y", back.y);
        ret.putDouble("Z", back.z);
        ModAttachments.of(p).put(RETURN, ret);
        Vec3 at = DrownedPlaces.arrival(sea);
        teleport(p, sea, at, 180);
        setShelter(p, BlockPos.containing(at));
        DrownedPlaces.chart(p, DrownedTerrain.TIDEWATCH, false);
        DrownedPlaces.chart(p, DrownedTerrain.DEEPWORK, false);
        DrownedPlaces.chart(p, DrownedTerrain.CHOIR, false);
        if (!ModAttachments.of(p).getBoolean(WELCOMED)) {
            ModAttachments.of(p).putBoolean(WELCOMED, true);
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.drowned_welcome").withStyle(ChatFormatting.AQUA), false);
        }
    }

    public static void leave(ServerPlayer p) {
        CompoundTag ret = ModAttachments.of(p).getCompound(RETURN);
        ServerLevel level = null;
        if (ret.contains("Dim")) {
            ResourceLocation id = ResourceLocation.tryParse(ret.getString("Dim"));
            if (id != null) {
                level = p.server.getLevel(ResourceKey.create(Registries.DIMENSION, id));
            }
        }
        if (level == null || DrownedDimension.is(level)) {
            RiftTravel.goToFrontier(p);
            return;
        }
        BlockPos at = BlockPos.containing(ret.getDouble("X"), ret.getDouble("Y"), ret.getDouble("Z"));
        level.getChunk(at);
        if (!standable(level, at)) {
            at = RiftTravel.safeSpot(level, at.getX(), at.getZ());
        }
        teleport(p, level, Vec3.atBottomCenterOf(at), p.getYRot());
    }

    static boolean standable(ServerLevel level, BlockPos feet) {
        return level.getBlockState(feet).getCollisionShape(level, feet).isEmpty()
                && level.getBlockState(feet.above()).getCollisionShape(level, feet.above()).isEmpty()
                && !level.getBlockState(feet.below()).getCollisionShape(level, feet.below()).isEmpty();
    }

    static void teleport(ServerPlayer p, ServerLevel level, Vec3 at, float yaw) {
        p.stopRiding();
        p.fallDistance = 0;
        p.teleportTo(level, at.x, at.y, at.z, yaw, p.getXRot());
        if (p instanceof net.neoforged.neoforge.common.util.FakePlayer && p.level() == level) {
            p.moveTo(at.x, at.y, at.z, yaw, p.getXRot());
        }
        level.playSound(null, BlockPos.containing(at), ModSounds.TIDE_GATE.get(), SoundSource.PLAYERS, 1.0F, 1.0F);
    }

    // ---------------------------------------------------------------------------------------------- shelters
    public static void setShelter(ServerPlayer p, BlockPos at) {
        ModAttachments.of(p).putLong(SHELTER, at.asLong());
    }

    @Nullable
    public static BlockPos shelter(ServerPlayer p) {
        CompoundTag t = ModAttachments.of(p);
        return t.contains(SHELTER) ? BlockPos.of(t.getLong(SHELTER)) : null;
    }

    /** A tide bell: ring it to make this shelter yours; sneak-ring to travel to the next shelter you have rung. */
    public static void ringBell(ServerLevel level, BlockPos bell, ServerPlayer p, boolean travel) {
        level.playSound(null, bell, ModSounds.TIDE_BELL.get(), SoundSource.BLOCKS, 1.5F, 1.0F);
        DrownedTerrain.Anchor here = DrownedTerrain.nearest(bell.getX(), bell.getZ());
        CompoundTag all = ModAttachments.of(p);
        CompoundTag bells = all.getCompound(BELLS);
        boolean fresh = !bells.contains(here.name());
        bells.putLong(here.name(), p.blockPosition().asLong());
        all.put(BELLS, bells);
        setShelter(p, p.blockPosition());
        if (!travel) {
            p.displayClientMessage(Component.translatable(fresh ? "message.unstable_frontiers.bell_new" : "message.unstable_frontiers.bell_rung",
                    Component.translatable("place.unstable_frontiers." + here.name())).withStyle(ChatFormatting.AQUA), false);
            StringBuilder others = new StringBuilder();
            for (DrownedTerrain.Anchor a : DrownedTerrain.ANCHORS) {
                if (a != here && bells.contains(a.name())) {
                    others.append(others.isEmpty() ? "" : ", ").append(Component.translatable("place.unstable_frontiers." + a.name()).getString());
                }
            }
            p.displayClientMessage(Component.translatable(others.isEmpty() ? "message.unstable_frontiers.bell_none" : "message.unstable_frontiers.bell_list",
                    others.toString()).withStyle(ChatFormatting.GRAY), false);
            return;
        }
        // travel: the next rung shelter after this one, in the Expanse's order
        int start = java.util.Arrays.asList(DrownedTerrain.ANCHORS).indexOf(here);
        for (int i = 1; i < DrownedTerrain.ANCHORS.length; i++) {
            DrownedTerrain.Anchor a = DrownedTerrain.ANCHORS[(start + i) % DrownedTerrain.ANCHORS.length];
            if (bells.contains(a.name())) {
                BlockPos to = BlockPos.of(bells.getLong(a.name()));
                level.getChunk(to);
                teleport(p, level, Vec3.atBottomCenterOf(to), p.getYRot());
                setShelter(p, to);
                p.displayClientMessage(Component.translatable("message.unstable_frontiers.bell_travel",
                        Component.translatable("place.unstable_frontiers." + a.name())).withStyle(ChatFormatting.AQUA), true);
                return;
            }
        }
        p.displayClientMessage(Component.translatable("message.unstable_frontiers.bell_none").withStyle(ChatFormatting.GRAY), true);
    }

    /** Out of air and failing: back to the shelter, once a minute at most. Returns true if it happened. */
    public static boolean rescue(ServerPlayer p) {
        long now = p.level().getGameTime();
        CompoundTag d = p.getPersistentData();
        if (d.contains(RESCUED) && now - d.getLong(RESCUED) < 1200 && d.getLong(RESCUED) <= now) {
            return false;
        }
        d.putLong(RESCUED, now);
        ServerLevel level = (ServerLevel) p.level();
        BlockPos to = shelter(p);
        Vec3 at;
        if (to != null) {
            level.getChunk(to);
            at = Vec3.atBottomCenterOf(to);
        } else {
            at = DrownedPlaces.arrival(level);
        }
        p.setDeltaMovement(Vec3.ZERO);
        teleport(p, level, at, p.getYRot());
        p.setAirSupply(p.getMaxAirSupply());
        p.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 80, 0, false, false));
        p.displayClientMessage(Component.translatable("message.unstable_frontiers.drowned_rescue").withStyle(ChatFormatting.LIGHT_PURPLE), false);
        return true;
    }

    // ------------------------------------------------------------------------------------------------- drops
    @SubscribeEvent
    public void onEntityTick(EntityTickEvent.Post event) {
        if (event.getEntity() instanceof ItemEntity item && !item.level().isClientSide && DrownedDimension.is(item.level()) && item.isInWater()) {
            // items sink and settle instead of floating away to the surface
            Vec3 v = item.getDeltaMovement();
            item.setDeltaMovement(v.x * 0.7D, Math.min(v.y, -0.03D), v.z * 0.7D);
        }
    }

    @SubscribeEvent
    public void onDrops(LivingDropsEvent event) {
        if (event.getEntity() instanceof Player p && DrownedDimension.is(p.level())) {
            for (ItemEntity e : event.getDrops()) {
                e.lifespan = Math.max(e.lifespan, 20 * 60 * 15);
            }
            if (p instanceof ServerPlayer sp && !event.getDrops().isEmpty()) {
                ModAttachments.of(sp).putLong("drowned_death", sp.blockPosition().asLong());
            }
        }
    }

    @SubscribeEvent
    public void onRespawn(PlayerEvent.PlayerRespawnEvent event) {
        if (event.getEntity() instanceof ServerPlayer sp && ModAttachments.of(sp).contains("drowned_death")) {
            BlockPos at = BlockPos.of(ModAttachments.of(sp).getLong("drowned_death"));
            ModAttachments.of(sp).remove("drowned_death");
            sp.displayClientMessage(Component.translatable("message.unstable_frontiers.drowned_belongings", at.getX(), at.getY(), at.getZ())
                    .withStyle(ChatFormatting.GOLD), false);
        }
    }
}
