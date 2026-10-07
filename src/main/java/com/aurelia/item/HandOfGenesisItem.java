package com.aurelia.item;

import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * The Unmaker's drop: the hand that cut the worlds apart. It holds one power from each of the eight realms.
 * Use to cast the chosen power (2.5 s cooldown); sneak and use to choose the next.
 */
public class HandOfGenesisItem extends Item {
    private static final String[] POWERS = {"Verdant Bloom", "Tempest Leap", "Sovereign's Wrath", "Undertow", "Silence", "Last Grain",
            "Haste of Hours", "Spore Bloom"};
    private static final ChatFormatting[] COLORS = {ChatFormatting.GREEN, ChatFormatting.AQUA, ChatFormatting.GOLD, ChatFormatting.DARK_AQUA,
            ChatFormatting.WHITE, ChatFormatting.RED, ChatFormatting.YELLOW, ChatFormatting.LIGHT_PURPLE};

    public HandOfGenesisItem(Properties properties) {
        super(properties);
    }

    private static int power(ItemStack stack) {
        return Math.floorMod(stack.getOrCreateTag().getInt("Power"), POWERS.length);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.isShiftKeyDown()) {
            int next = (power(stack) + 1) % POWERS.length;
            stack.getOrCreateTag().putInt("Power", next);
            if (!level.isClientSide) {
                player.displayClientMessage(Component.literal(POWERS[next]).withStyle(COLORS[next], ChatFormatting.BOLD), true);
            }
            player.playSound(SoundEvents.AMETHYST_BLOCK_CHIME, 1.0f, 0.6f + next * 0.12f);
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
        }
        if (level instanceof ServerLevel server) {
            cast(server, player, power(stack));
        }
        player.getCooldowns().addCooldown(this, 50);
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    private static List<LivingEntity> foes(ServerLevel level, Player player, double r) {
        return level.getEntitiesOfClass(LivingEntity.class, new AABB(player.blockPosition()).inflate(r),
                e -> e != player && e.isAlive() && e instanceof Enemy);
    }

    private static void cast(ServerLevel level, Player player, int p) {
        Vec3 look = player.getLookAngle();
        switch (p) {
            case 0 -> {                                                  // Grove: heal you and everyone near you
                for (Player ally : level.getEntitiesOfClass(Player.class, player.getBoundingBox().inflate(8.0))) {
                    ally.heal(6.0f);
                    ally.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 100, 1));
                }
                level.sendParticles(ParticleTypes.HAPPY_VILLAGER, player.getX(), player.getY() + 1.0, player.getZ(), 40, 3.0, 1.0, 3.0, 0.1);
            }
            case 1 -> {                                                  // Skyreach: leap on the wind
                player.push(look.x * 1.6, 0.9, look.z * 1.6);
                player.hurtMarked = true;
                player.fallDistance = 0;
                player.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 120, 0));
                level.sendParticles(ParticleTypes.CLOUD, player.getX(), player.getY(), player.getZ(), 30, 0.6, 0.2, 0.6, 0.1);
            }
            case 2 -> {                                                  // Hollow: a cone of soul fire
                for (LivingEntity e : foes(level, player, 7.0)) {
                    Vec3 to = e.position().subtract(player.position()).normalize();
                    if (to.dot(look) > 0.5) {
                        e.hurt(player.damageSources().playerAttack(player), 12.0f);
                        e.setSecondsOnFire(5);
                    }
                }
                for (int k = 1; k < 7; k++) {
                    Vec3 at = player.getEyePosition().add(look.scale(k));
                    level.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, at.x, at.y, at.z, 6, 0.3 * k / 3, 0.3 * k / 3, 0.3 * k / 3, 0.01);
                }
            }
            case 3 -> {                                                  // Drowned: drag every foe to you; breathe water
                for (LivingEntity e : foes(level, player, 12.0)) {
                    Vec3 in = player.position().subtract(e.position()).normalize().scale(1.2);
                    e.push(in.x, 0.3, in.z);
                    e.hurtMarked = true;
                    e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 1));
                }
                player.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 600, 0));
                player.addEffect(new MobEffectInstance(MobEffects.DOLPHINS_GRACE, 600, 0));
                level.sendParticles(ParticleTypes.BUBBLE_POP, player.getX(), player.getY() + 1.0, player.getZ(), 60, 4.0, 1.0, 4.0, 0.1);
            }
            case 4 -> {                                                  // Pale: freeze everything near you; vanish
                for (LivingEntity e : foes(level, player, 10.0)) {
                    e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 4));
                    e.setTicksFrozen(e.getTicksRequiredToFreeze() + 100);
                }
                player.addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, 100, 0));
                level.sendParticles(ParticleTypes.SNOWFLAKE, player.getX(), player.getY() + 1.0, player.getZ(), 80, 5.0, 1.5, 5.0, 0.02);
            }
            case 5 -> {                                                  // Scarlet: a beam of burning light
                Vec3 from = player.getEyePosition();
                for (int k = 1; k <= 24; k++) {
                    Vec3 at = from.add(look.scale(k));
                    level.sendParticles(ParticleTypes.FLAME, at.x, at.y, at.z, 2, 0.05, 0.05, 0.05, 0.0);
                    List<LivingEntity> hit = level.getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(0.8),
                            e -> e != player && e.isAlive());
                    if (!hit.isEmpty()) {
                        hit.get(0).hurt(player.damageSources().playerAttack(player), 16.0f);
                        hit.get(0).setSecondsOnFire(6);
                        break;
                    }
                    if (!level.getBlockState(net.minecraft.core.BlockPos.containing(at)).isAir()) {
                        break;
                    }
                }
            }
            case 6 -> {                                                  // Clockwork: your time runs faster than theirs
                player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 200, 2));
                player.addEffect(new MobEffectInstance(MobEffects.DIG_SPEED, 200, 2));
                for (LivingEntity e : foes(level, player, 10.0)) {
                    e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 2));
                }
                level.sendParticles(ParticleTypes.REVERSE_PORTAL, player.getX(), player.getY() + 1.0, player.getZ(), 50, 1.0, 1.0, 1.0, 0.2);
            }
            default -> {                                                 // Mycelial: a bloom of poison spores
                for (LivingEntity e : foes(level, player, 8.0)) {
                    e.addEffect(new MobEffectInstance(MobEffects.POISON, 120, 1));
                    e.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 120, 1));
                }
                level.sendParticles(ParticleTypes.SPORE_BLOSSOM_AIR, player.getX(), player.getY() + 1.0, player.getZ(), 120, 4.0, 1.5, 4.0, 0.02);
            }
        }
        level.playSound(null, player.blockPosition(), SoundEvents.BEACON_POWER_SELECT, SoundSource.PLAYERS, 1.0f, 0.7f + p * 0.1f);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        int p = power(stack);
        tooltip.add(Component.translatable("item.aurelia.hand_of_genesis.mode", POWERS[p]).withStyle(COLORS[p]));
        tooltip.add(Component.translatable("item.aurelia.hand_of_genesis.use").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("item.aurelia.hand_of_genesis.lore").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.ITALIC));
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return true;
    }
}
