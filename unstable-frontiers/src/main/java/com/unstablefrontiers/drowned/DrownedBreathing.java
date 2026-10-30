package com.unstablefrontiers.drowned;

import com.unstablefrontiers.UnstableFrontiers;
import com.unstablefrontiers.block.BreathVentBlock;
import com.unstablefrontiers.registry.DrownedRegistry;
import com.unstablefrontiers.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.AABB;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.common.NeoForgeMod;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * One breathing system: the Diving Rig. While your head is under water and nothing else lets you breathe there (water
 * breathing, a conduit, a Breath Charm, another mod's ability: all of those are left alone and the rig is not used), the rig
 * keeps your breath full and spends its own air, one second a second. A basic rig spends three a second below the deep line
 * (y {@value DrownedTerrain#DEEP_LINE}); the Deep Rig does not. It refills in air (any dimension), faster at a breath vent's
 * stream or a station's air pocket. When it runs dry, vanilla breath takes over as usual; warnings come at 30 and 10 seconds.
 * Swim Fins add swimming speed; Deep-Sight Goggles outline predators within 16 blocks.
 */
public final class DrownedBreathing {
    private static final AttributeModifier FINS = new AttributeModifier(UnstableFrontiers.id("swim_fins"), 0.7D,
            AttributeModifier.Operation.ADD_MULTIPLIED_BASE);
    private static final String WARNED = "uf_rig_warned";
    private static final String DEEP_TOLD = "uf_deep_told";

    public DrownedBreathing() {}

    public static boolean breathesUnderwater(ServerPlayer p) {
        return p.canBreatheUnderwater() || p.hasEffect(MobEffects.WATER_BREATHING) || p.hasEffect(MobEffects.CONDUIT_POWER) || DrownedGear.charm(p);
    }

    /** Air seconds spent per second at this player's depth with this rig. */
    public static int drain(ServerPlayer p, ItemStack rig) {
        boolean deep = p.getY() < DrownedTerrain.DEEP_LINE && DrownedDimension.is(p.level());
        return deep && rig.getItem() == DrownedRegistry.RIG.get() ? 3 : 1;
    }

    /** A breath vent within its reach below the player? */
    public static boolean atVent(ServerPlayer p) {
        BlockPos at = p.blockPosition();
        for (int k = 0; k <= BreathVentBlock.REACH; k++) {
            BlockPos b = at.below(k);
            var st = p.level().getBlockState(b);
            if (st.is(DrownedRegistry.BREATH_VENT.get())) {
                return true;
            }
            if (!st.getFluidState().is(FluidTags.WATER) && !st.isAir() && k > 0) {
                return false;
            }
        }
        return false;
    }

    @SubscribeEvent
    public void onPlayerTick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer p) || p.isSpectator()) {
            return;
        }
        fins(p);
        ItemStack rig = DrownedGear.rig(p);
        boolean underwater = p.isEyeInFluid(FluidTags.WATER);
        boolean inSea = DrownedDimension.is(p.level());
        if (!rig.isEmpty() && underwater && !breathesUnderwater(p) && !p.isCreative()) {
            int air = DivingGearItem.air(rig);
            if (air > 0) {
                p.setAirSupply(p.getMaxAirSupply());
            }
            if (p.tickCount % 20 == 0) {
                int next = atVent(p) ? Math.min(((DivingGearItem) rig.getItem()).capacity(), air + 20) : air - drain(p, rig);
                DivingGearItem.setAir(rig, next);
                warn(p, rig, air, Math.max(0, next));
            }
        } else if (!rig.isEmpty() && p.tickCount % 20 == 0) {
            int air = DivingGearItem.air(rig);
            int cap = ((DivingGearItem) rig.getItem()).capacity();
            if (air < cap && (!underwater || atVent(p))) {
                DivingGearItem.setAir(rig, air + (underwater ? 20 : inSea ? 15 : 6));
                p.getPersistentData().putInt(WARNED, 0);
            }
        }
        if (!inSea) {
            return;
        }
        if (p.tickCount % 20 == 0 && underwater && !rig.isEmpty() && rig.getItem() == DrownedRegistry.RIG.get() && p.getY() < DrownedTerrain.DEEP_LINE
                && !p.getPersistentData().getBoolean(DEEP_TOLD)) {
            p.getPersistentData().putBoolean(DEEP_TOLD, true);
            p.displayClientMessage(Component.translatable("message.unstable_frontiers.deep_line").withStyle(ChatFormatting.GOLD), false);
        }
        if (p.getY() > DrownedTerrain.DEEP_LINE + 10) {
            p.getPersistentData().putBoolean(DEEP_TOLD, false);
        }
        // black-out: out of breath and failing
        if (underwater && p.getAirSupply() <= 0 && p.getHealth() <= p.getMaxHealth() * 0.35F && !p.isCreative()) {
            DrownedTravel.rescue(p);
        }
        if (p.tickCount % 40 == 0 && underwater && DrownedGear.deepSight(p)) {
            for (Mob m : p.level().getEntitiesOfClass(Mob.class, new AABB(p.blockPosition()).inflate(16), e -> e instanceof Monster && e.isAlive())) {
                m.addEffect(new MobEffectInstance(MobEffects.GLOWING, 50, 0, false, false));
            }
        }
    }

    private static void fins(ServerPlayer p) {
        if (p.tickCount % 10 != 0) {
            return;
        }
        AttributeInstance swim = p.getAttribute(NeoForgeMod.SWIM_SPEED);
        if (swim == null) {
            return;
        }
        boolean want = p.isInWater() && DrownedGear.fins(p);
        if (want && !swim.hasModifier(FINS.id())) {
            swim.addTransientModifier(FINS);
        } else if (!want && swim.hasModifier(FINS.id())) {
            swim.removeModifier(FINS.id());
        }
    }

    private static void warn(ServerPlayer p, ItemStack rig, int before, int now) {
        int stage = now <= 0 ? 3 : now <= 10 ? 2 : now <= 30 ? 1 : 0;
        int told = p.getPersistentData().getInt(WARNED);
        if (stage > told) {
            p.getPersistentData().putInt(WARNED, stage);
            String key = stage == 3 ? "message.unstable_frontiers.rig_empty" : stage == 2 ? "message.unstable_frontiers.rig_10" : "message.unstable_frontiers.rig_30";
            p.displayClientMessage(Component.translatable(key).withStyle(stage == 1 ? ChatFormatting.GOLD : ChatFormatting.RED), stage < 3);
            if (stage == 3) {
                p.displayClientMessage(Component.translatable(key).withStyle(ChatFormatting.RED), false);
            }
            ((ServerLevel) p.level()).playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.RIG_WARN.get(), SoundSource.PLAYERS, 1.0F,
                    stage == 3 ? 0.6F : stage == 2 ? 0.9F : 1.2F);
        } else if (stage < told) {
            p.getPersistentData().putInt(WARNED, stage);
        }
    }
}
