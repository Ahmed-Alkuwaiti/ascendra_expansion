package com.unstablefrontiers.abyss;

import com.unstablefrontiers.registry.ModAttachments;
import com.unstablefrontiers.registry.ModSounds;
import com.unstablefrontiers.travel.RiftTravel;
import com.unstablefrontiers.world.FrontierDimension;
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
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.living.LivingDropsEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.EntityTickEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * Getting into and out of the Astral Abyss, and staying safe there. None of this changes inventory rules anywhere else:
 * <ul>
 * <li><b>In</b>: through an open rift gate (the restored observatory's). You arrive on the landing, beside its own gate.
 * Where you came from is remembered (a player attachment, kept through death).</li>
 * <li><b>Out</b>: the landing's gate, the Rift Shard, or /frontier return: all take you back to where you came in,
 * or to the frontier if that place is gone.</li>
 * <li><b>Falling</b>: below y {@link AbyssDimension#CATCH_Y} the rift catches you and sets you back on the last solid
 * ground you stood on (or the landing): it costs a fifth of your health, never the last of it.</li>
 * <li><b>Items</b>: anything dropped that falls toward the void is carried to the nearest of the abyss's places. Items a
 * player drops on death there keep for fifteen minutes instead of five.</li>
 * </ul>
 */
public final class AbyssTravel {
    private static final String RETURN = "abyss_return";
    private static final String SAFE = "abyss_safe";
    private static final String GATE_COOLDOWN = "uf_gate_cooldown";
    private static final String WELCOMED = "abyss_welcomed";

    public AbyssTravel() {}

    /** Stepped into an open gate: the observatory's takes you in, the landing's takes you out. */
    public static void throughGate(ServerPlayer p, BlockPos gate) {
        long now = p.level().getGameTime();
        CompoundTag d = p.getPersistentData();
        if (now - d.getLong(GATE_COOLDOWN) < 60 && d.getLong(GATE_COOLDOWN) <= now) {
            return;
        }
        d.putLong(GATE_COOLDOWN, now);
        if (AbyssDimension.is(p.level())) {
            leave(p);
        } else {
            enter(p, gate);
        }
    }

    public static void enter(ServerPlayer p, @Nullable BlockPos gate) {
        ServerLevel abyss = p.server.getLevel(AbyssDimension.LEVEL);
        if (abyss == null) {
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.no_abyss").withStyle(ChatFormatting.RED), false);
            return;
        }
        CompoundTag ret = new CompoundTag();
        ret.putString("Dim", p.level().dimension().location().toString());
        Vec3 back = gate != null ? stepAway(p, gate) : p.position();
        ret.putDouble("X", back.x);
        ret.putDouble("Y", back.y);
        ret.putDouble("Z", back.z);
        ModAttachments.of(p).put(RETURN, ret);
        AbyssPlaces.build(abyss, AbyssTerrain.LANDING);
        Vec3 at = arrival();
        teleport(p, abyss, at, 180);
        CompoundTag safe = new CompoundTag();
        safe.putLong("Pos", BlockPos.containing(at).asLong());
        ModAttachments.of(p).put(SAFE, safe);
        if (!ModAttachments.of(p).getBoolean(WELCOMED)) {
            ModAttachments.of(p).putBoolean(WELCOMED, true);
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.abyss_welcome").withStyle(ChatFormatting.AQUA), false);
        }
    }

    /** Where arrivals stand: on the landing, a few blocks in front of its gate. */
    public static Vec3 arrival() {
        return AbyssPlaces.standing(AbyssTerrain.LANDING).add(0, 0, 5);
    }

    /** Out of the abyss: back to where you came in, or to the frontier. */
    public static void leave(ServerPlayer p) {
        CompoundTag ret = ModAttachments.of(p).getCompound(RETURN);
        ServerLevel level = null;
        if (ret.contains("Dim")) {
            ResourceLocation id = ResourceLocation.tryParse(ret.getString("Dim"));
            if (id != null) {
                level = p.server.getLevel(ResourceKey.create(Registries.DIMENSION, id));
            }
        }
        if (level == null || AbyssDimension.is(level)) {
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

    private static Vec3 stepAway(ServerPlayer p, BlockPos gate) {
        // come back a couple of blocks out of the gate, on the side you entered from
        Vec3 c = Vec3.atBottomCenterOf(gate);
        Vec3 d = p.position().subtract(c);
        Vec3 flat = new Vec3(d.x, 0, d.z);
        flat = flat.lengthSqr() < 1.0E-3 ? new Vec3(0, 0, 1) : flat.normalize();
        return c.add(flat.scale(3)).add(0, 0.1D, 0);
    }

    private static boolean standable(ServerLevel level, BlockPos feet) {
        return level.getBlockState(feet).getCollisionShape(level, feet).isEmpty()
                && level.getBlockState(feet.above()).getCollisionShape(level, feet.above()).isEmpty()
                && !level.getBlockState(feet.below()).getCollisionShape(level, feet.below()).isEmpty();
    }

    private static void teleport(ServerPlayer p, ServerLevel level, Vec3 at, float yaw) {
        p.stopRiding();
        p.fallDistance = 0;
        p.teleportTo(level, at.x, at.y, at.z, yaw, p.getXRot());
        level.playSound(null, BlockPos.containing(at), ModSounds.RIFT_OPEN.get(), SoundSource.PLAYERS, 1.0F, 1.4F);
    }

    // ---------------------------------------------------------------------------------------------- safety
    @SubscribeEvent
    public void onPlayerTick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer p) || !AbyssDimension.is(p.level()) || p.isSpectator()) {
            return;
        }
        if (p.getY() < AbyssDimension.CATCH_Y && !p.isCreative()) {
            catchFall(p);
            return;
        }
        if (p.tickCount % 10 == 0 && p.onGround() && p.getY() > AbyssDimension.CATCH_Y + 12) {
            BlockPos below = p.blockPosition().below();
            BlockState st = p.level().getBlockState(below);
            if (!st.getCollisionShape(p.level(), below).isEmpty() && standable((ServerLevel) p.level(), p.blockPosition())) {
                CompoundTag safe = new CompoundTag();
                safe.putLong("Pos", p.blockPosition().asLong());
                ModAttachments.of(p).put(SAFE, safe);
            }
        }
    }

    /** The rift catches a falling player: back to the last safe ground, a fifth of their health the poorer (never the last of it). */
    public static void catchFall(ServerPlayer p) {
        ServerLevel level = (ServerLevel) p.level();
        CompoundTag safe = ModAttachments.of(p).getCompound(SAFE);
        Vec3 at = null;
        if (safe.contains("Pos")) {
            BlockPos pos = BlockPos.of(safe.getLong("Pos"));
            level.getChunk(pos);
            if (standable(level, pos)) {
                at = Vec3.atBottomCenterOf(pos);
            }
        }
        if (at == null) {
            AbyssPlaces.build(level, AbyssTerrain.LANDING);
            at = arrival();
        }
        p.setDeltaMovement(Vec3.ZERO);
        teleport(p, level, at, p.getYRot());
        p.hurtMarked = true;
        float cost = p.getMaxHealth() * 0.2F;
        p.setHealth(Math.max(1.0F, p.getHealth() - cost));
        p.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 60, 0, false, false));
        p.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 25, 0, false, false));
        p.displayClientMessage(Component.translatable("message.unstable_frontiers.rift_catch").withStyle(ChatFormatting.LIGHT_PURPLE), true);
    }

    @SubscribeEvent
    public void onEntityTick(EntityTickEvent.Pre event) {
        if (event.getEntity() instanceof ItemEntity item && !item.level().isClientSide && item.getY() < AbyssDimension.ITEM_RESCUE_Y
                && AbyssDimension.is(item.level())) {
            AbyssTerrain.Anchor near = nearest(item.getX(), item.getZ());
            Vec3 at = AbyssPlaces.safeSpot((ServerLevel) item.level(), near).add(0, 0.5D, 0);
            item.setDeltaMovement(Vec3.ZERO);
            item.teleportTo(at.x, at.y, at.z);
        }
    }

    public static AbyssTerrain.Anchor nearest(double x, double z) {
        AbyssTerrain.Anchor best = AbyssTerrain.LANDING;
        double bd = Double.MAX_VALUE;
        for (AbyssTerrain.Anchor a : AbyssTerrain.ANCHORS) {
            double d = Math.hypot(x - a.x(), z - a.z());
            if (d < bd) {
                bd = d;
                best = a;
            }
        }
        return best;
    }

    @SubscribeEvent
    public void onDrops(LivingDropsEvent event) {
        if (event.getEntity() instanceof Player p && AbyssDimension.is(p.level())) {
            for (ItemEntity e : event.getDrops()) {
                e.lifespan = Math.max(e.lifespan, 20 * 60 * 15);
            }
            if (p instanceof ServerPlayer sp && !event.getDrops().isEmpty()) {
                BlockPos at = sp.blockPosition();
                ModAttachments.of(sp).putLong("abyss_death", at.asLong());
            }
        }
    }

    @SubscribeEvent
    public void onRespawn(PlayerEvent.PlayerRespawnEvent event) {
        if (event.getEntity() instanceof ServerPlayer sp && ModAttachments.of(sp).contains("abyss_death")) {
            BlockPos at = BlockPos.of(ModAttachments.of(sp).getLong("abyss_death"));
            ModAttachments.of(sp).remove("abyss_death");
            sp.displayClientMessage(Component.translatable("message.unstable_frontiers.abyss_belongings", at.getX(), at.getY(), at.getZ())
                    .withStyle(ChatFormatting.GOLD), false);
        }
    }

    public static boolean inFrontier(ServerPlayer p) {
        return FrontierDimension.is(p.level());
    }
}
