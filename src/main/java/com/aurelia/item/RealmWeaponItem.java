package com.aurelia.item;

import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * Each realm's signature weapon (a warhammer, spear, cleaver, trident, scythe, twin daggers, a bladed repeating crossbow and a
 * staff), with the realm's power on every hit. Damage bonuses that depend on the situation (the Tidebinder in water, the
 * Silent Requiem from a crouch) are applied in KitEvents. Use: the weapon's special, on a cooldown.
 */
public class RealmWeaponItem extends SwordItem {
    private final RealmTier realm;

    public RealmWeaponItem(RealmTier tier, int damage, float speed, Properties properties) {
        super(tier, damage, speed, properties);
        this.realm = tier;
    }

    public RealmTier realm() {
        return this.realm;
    }

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        boolean r = super.hurtEnemy(stack, target, attacker);
        if (!(target.level() instanceof ServerLevel level)) {
            return r;
        }
        switch (this.realm) {
            case VERDANT -> {
                target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 2));
                target.addEffect(new MobEffectInstance(MobEffects.POISON, 60, 0));
                attacker.heal(2.0f);
            }
            case STORMGLASS -> {
                target.push(0.0, 0.7, 0.0);
                LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(level);
                if (bolt != null && level.random.nextInt(3) == 0) {
                    bolt.moveTo(target.getX(), target.getY(), target.getZ());
                    bolt.setVisualOnly(true);
                    level.addFreshEntity(bolt);
                }
            }
            case EMBERHEART -> {
                target.setSecondsOnFire(5);
                target.addEffect(new MobEffectInstance(MobEffects.WITHER, 60, 0));
            }
            case TIDESTONE -> {
                Vec3 in = attacker.position().subtract(target.position()).normalize().scale(0.6);
                target.push(in.x, 0.1, in.z);
            }
            case RIME -> {
                target.setTicksFrozen(target.getTicksRequiredToFreeze() + 80);
                target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 2));
            }
            case SUNGLASS -> {
                target.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 1));
                for (LivingEntity other : level.getEntitiesOfClass(LivingEntity.class, target.getBoundingBox().inflate(2.5),
                        e -> e != target && e != attacker && e.isAlive() && !(e instanceof Player))) {
                    other.hurt(attacker.damageSources().mobAttack(attacker), this.getDamage() * 0.5f);
                }
            }
            case CHRONITE -> {
                target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 1));
                target.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 60, 0));
            }
            case BLOOMSPORE -> {
                for (LivingEntity other : level.getEntitiesOfClass(LivingEntity.class, target.getBoundingBox().inflate(3.0),
                        e -> e != attacker && e.isAlive() && !(e instanceof Player))) {
                    other.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 1));
                    other.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 80, 0));
                }
            }
            default -> { }
        }
        return r;
    }

    // ---- the right-click special

    private static final int[] COOLDOWN = {160, 120, 200, 200, 120, 160, 60, 200};

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level instanceof ServerLevel server) {
            special(server, player);
            stack.hurtAndBreak(2, player, p -> p.broadcastBreakEvent(hand));
        }
        player.getCooldowns().addCooldown(this, COOLDOWN[this.realm.ordinal()]);
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    private static List<LivingEntity> foes(ServerLevel level, Player player, Vec3 at, double r) {
        return level.getEntitiesOfClass(LivingEntity.class, new net.minecraft.world.phys.AABB(at, at).inflate(r),
                e -> e != player && e.isAlive() && (e instanceof Enemy || (e instanceof net.minecraft.world.entity.Mob m && m.getTarget() == player)));
    }

    private void special(ServerLevel level, Player player) {
        Vec3 look = player.getLookAngle().multiply(1, 0, 1).normalize();
        Vec3 here = player.position();
        switch (this.realm) {
            case VERDANT -> {                                              // Bramble Eruption
                for (int k = 1; k <= 8; k++) {
                    Vec3 at = here.add(look.scale(k));
                    com.aurelia.Perf.particles(level, net.minecraft.core.particles.ParticleTypes.COMPOSTER, at.x, at.y + 0.3, at.z, 12, 0.4, 0.6, 0.4, 0.05);
                    com.aurelia.Perf.particles(level, new net.minecraft.core.particles.BlockParticleOption(ParticleTypes.BLOCK,
                            net.minecraft.world.level.block.Blocks.ROOTED_DIRT.defaultBlockState()), at.x, at.y + 0.2, at.z, 10, 0.3, 0.4, 0.3, 0.1);
                    for (LivingEntity e : foes(level, player, at, 1.6)) {
                        e.hurt(player.damageSources().playerAttack(player), 10.0f);
                        e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 4));
                        e.push(0.0, 0.6, 0.0);
                    }
                }
                level.playSound(null, player.blockPosition(), SoundEvents.ROOTED_DIRT_BREAK, SoundSource.PLAYERS, 2.0f, 0.6f);
            }
            case STORMGLASS -> {                                           // Tempest Dash
                Vec3 to = here.add(look.scale(8));
                for (int k = 1; k <= 8; k++) {
                    Vec3 at = here.add(look.scale(k));
                    com.aurelia.Perf.particles(level, ParticleTypes.CLOUD, at.x, at.y + 1.0, at.z, 6, 0.3, 0.3, 0.3, 0.02);
                    for (LivingEntity e : foes(level, player, at, 3.0)) {
                        if (e.hurt(player.damageSources().playerAttack(player), 12.0f)) {
                            LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(level);
                            if (bolt != null) {
                                bolt.moveTo(e.getX(), e.getY(), e.getZ());
                                bolt.setVisualOnly(true);
                                level.addFreshEntity(bolt);
                            }
                        }
                    }
                }
                player.push(look.x * 2.4, 0.35, look.z * 2.4);
                player.hurtMarked = true;
                player.fallDistance = 0;
                player.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 40, 0, false, false));
                level.playSound(null, player.blockPosition(), SoundEvents.TRIDENT_RIPTIDE_3, SoundSource.PLAYERS, 2.0f, 1.0f);
            }
            case EMBERHEART -> {                                           // Soul Inferno
                for (int k = 0; k < 48; k++) {
                    double a = k * Math.PI / 24;
                    com.aurelia.Perf.particles(level, ParticleTypes.SOUL_FIRE_FLAME, here.x + Math.cos(a) * 5, here.y + 0.3, here.z + Math.sin(a) * 5, 3, 0.1, 0.4, 0.1, 0.02);
                }
                for (LivingEntity e : foes(level, player, here, 5.5)) {
                    e.hurt(player.damageSources().playerAttack(player), 14.0f);
                    e.setSecondsOnFire(8);
                    Vec3 out = e.position().subtract(here).normalize().scale(1.2);
                    e.push(out.x, 0.5, out.z);
                }
                level.playSound(null, player.blockPosition(), SoundEvents.BLAZE_SHOOT, SoundSource.PLAYERS, 2.0f, 0.5f);
            }
            case TIDESTONE -> {                                            // Maelstrom
                for (LivingEntity e : foes(level, player, here, 12.0)) {
                    Vec3 in = here.subtract(e.position()).normalize().scale(1.4);
                    e.push(in.x, 0.3, in.z);
                    e.hurt(player.damageSources().drown(), 8.0f);
                    e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 2));
                }
                com.aurelia.Perf.particles(level, ParticleTypes.BUBBLE_COLUMN_UP, here.x, here.y + 1, here.z, 200, 6.0, 1.0, 6.0, 0.3);
                player.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 400, 0));
                level.playSound(null, player.blockPosition(), SoundEvents.CONDUIT_ACTIVATE, SoundSource.PLAYERS, 2.0f, 0.6f);
            }
            case RIME -> {                                                 // Whiteout Step
                Vec3 eye = player.getEyePosition();
                Vec3 reach = eye.add(player.getLookAngle().scale(16));
                net.minecraft.world.phys.EntityHitResult hit = net.minecraft.world.entity.projectile.ProjectileUtil.getEntityHitResult(level, player, eye, reach,
                        player.getBoundingBox().expandTowards(player.getLookAngle().scale(16)).inflate(1.0), e -> e instanceof LivingEntity && e != player);
                if (hit != null && hit.getEntity() instanceof LivingEntity e) {
                    Vec3 behind = e.position().subtract(e.getLookAngle().multiply(1, 0, 1).normalize().scale(1.5));
                    com.aurelia.Perf.particles(level, ParticleTypes.SNOWFLAKE, player.getX(), player.getY() + 1, player.getZ(), 60, 0.4, 0.8, 0.4, 0.05);
                    player.teleportTo(behind.x, e.getY(), behind.z);
                    e.hurt(player.damageSources().playerAttack(player), 18.0f);
                    e.setTicksFrozen(e.getTicksRequiredToFreeze() + 140);
                    e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 4));
                    player.addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, 60, 0, false, false));
                    level.playSound(null, player.blockPosition(), SoundEvents.GLASS_BREAK, SoundSource.PLAYERS, 2.0f, 1.4f);
                }
            }
            case SUNGLASS -> {                                             // Fang Flurry
                for (int k = 0; k < 36; k++) {
                    double a = k * Math.PI / 18;
                    com.aurelia.Perf.particles(level, ParticleTypes.SWEEP_ATTACK, here.x + Math.cos(a) * 3.5, here.y + 1, here.z + Math.sin(a) * 3.5, 1, 0, 0, 0, 0);
                }
                for (LivingEntity e : foes(level, player, here, 6.0)) {
                    e.hurt(player.damageSources().playerAttack(player), 16.0f);
                    e.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 1));
                }
                level.playSound(null, player.blockPosition(), SoundEvents.PLAYER_ATTACK_SWEEP, SoundSource.PLAYERS, 2.0f, 0.5f);
            }
            case CHRONITE -> {                                             // Hour Volley: five bolts in a fan
                for (int k = -2; k <= 2; k++) {
                    net.minecraft.world.entity.projectile.Arrow bolt = new net.minecraft.world.entity.projectile.Arrow(level, player);
                    bolt.shootFromRotation(player, player.getXRot(), player.getYRot() + k * 6.0f, 0.0f, 3.2f, 0.5f);
                    bolt.setBaseDamage(6.0);
                    bolt.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 9));
                    bolt.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 80, 4));
                    bolt.pickup = net.minecraft.world.entity.projectile.AbstractArrow.Pickup.DISALLOWED;
                    level.addFreshEntity(bolt);
                }
                com.aurelia.Perf.particles(level, ParticleTypes.REVERSE_PORTAL, player.getX(), player.getEyeY(), player.getZ(), 30, 0.3, 0.3, 0.3, 0.1);
                level.playSound(null, player.blockPosition(), SoundEvents.CROSSBOW_SHOOT, SoundSource.PLAYERS, 1.5f, 0.7f);
                level.playSound(null, player.blockPosition(), SoundEvents.BELL_BLOCK, SoundSource.PLAYERS, 0.8f, 1.6f);
            }
            default -> {                                                   // Bloom Burst
                int caught = 0;
                for (LivingEntity e : foes(level, player, here, 6.0)) {
                    e.addEffect(new MobEffectInstance(MobEffects.POISON, 120, 2));
                    e.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 120, 0));
                    caught++;
                }
                player.heal(2.0f * caught);
                com.aurelia.Perf.particles(level, ParticleTypes.SPORE_BLOSSOM_AIR, here.x, here.y + 1, here.z, 250, 5.0, 1.5, 5.0, 0.02);
                level.playSound(null, player.blockPosition(), SoundEvents.MOSS_BREAK, SoundSource.PLAYERS, 2.0f, 0.5f);
            }
        }
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable(this.getDescriptionId() + ".power").withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable(this.getDescriptionId() + ".ability").withStyle(ChatFormatting.LIGHT_PURPLE));
    }
}
