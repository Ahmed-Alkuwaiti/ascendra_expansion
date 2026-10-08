package com.aurelia.item;

import com.google.common.collect.ImmutableMultimap;
import com.google.common.collect.Multimap;
import java.util.List;
import java.util.UUID;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.ForgeMod;
import org.joml.Vector3f;

/**
 * Worldsunder: the eight realm weapons melted into one round a Fractured Genesis. 24 attack damage at 1.0 speed and
 * 1.5 blocks of extra reach. Every hit also carries the next realm's power in turn, and (in KitEvents) a bite of the target's
 * own health, so it keeps pace with bosses that have thousands. Use: Singularity.
 */
public class WorldsunderItem extends SwordItem {
    private static final UUID REACH = UUID.fromString("9a3e61d4-0c27-4f5b-8e11-77d2a4c6b0f1");
    private static final String EDGE = "Edge";
    private static final String[] EDGES = {"Root", "Storm", "Fire", "Tide", "Frost", "Sweep", "Time", "Spores"};
    private static final Vector3f[] COLORS = {new Vector3f(0.43f, 0.9f, 0.35f), new Vector3f(0.43f, 0.84f, 1.0f), new Vector3f(1.0f, 0.55f, 0.16f),
            new Vector3f(0.24f, 0.9f, 0.78f), new Vector3f(0.86f, 0.93f, 1.0f), new Vector3f(0.98f, 0.24f, 0.24f), new Vector3f(1.0f, 0.8f, 0.31f),
            new Vector3f(1.0f, 0.35f, 0.88f)};
    private static final int COOLDOWN = 400;

    public WorldsunderItem(Properties properties) {
        super(RealmTier.GENESIS, 15, -3.0f, properties);
    }

    /** The extra damage each hit does: 3% of the target's max health, at most 15. */
    public static float unmaking(LivingEntity target) {
        return Math.min(15.0f, target.getMaxHealth() * 0.03f);
    }

    @Override
    public Multimap<Attribute, AttributeModifier> getAttributeModifiers(EquipmentSlot slot, ItemStack stack) {
        Multimap<Attribute, AttributeModifier> base = super.getAttributeModifiers(slot, stack);
        if (slot != EquipmentSlot.MAINHAND) {
            return base;
        }
        ImmutableMultimap.Builder<Attribute, AttributeModifier> out = ImmutableMultimap.builder();
        out.putAll(base);
        out.put(ForgeMod.ENTITY_REACH.get(), new AttributeModifier(REACH, "Worldsunder reach", 1.5, AttributeModifier.Operation.ADDITION));
        return out.build();
    }

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        boolean r = super.hurtEnemy(stack, target, attacker);
        if (!(target.level() instanceof ServerLevel level)) {
            return r;
        }
        int edge = Math.floorMod(stack.getOrCreateTag().getInt(EDGE), 8);
        stack.getOrCreateTag().putInt(EDGE, (edge + 1) % 8);
        com.aurelia.Perf.particles(level, new DustParticleOptions(COLORS[edge], 1.6f), target.getX(), target.getY() + target.getBbHeight() * 0.6, target.getZ(),
                24, 0.4, 0.5, 0.4, 0.0);
        switch (edge) {
            case 0 -> {                                                    // Root
                target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 3));
                target.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 1));
                attacker.heal(3.0f);
            }
            case 1 -> {                                                    // Storm
                target.push(0.0, 0.8, 0.0);
                LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(level);
                if (bolt != null) {
                    bolt.moveTo(target.getX(), target.getY(), target.getZ());
                    bolt.setVisualOnly(true);
                    level.addFreshEntity(bolt);
                }
            }
            case 2 -> {                                                    // Fire
                target.setSecondsOnFire(8);
                target.addEffect(new MobEffectInstance(MobEffects.WITHER, 80, 1));
            }
            case 3 -> {                                                    // Tide
                Vec3 in = attacker.position().subtract(target.position()).normalize().scale(0.8);
                target.push(in.x, 0.15, in.z);
                target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 1));
            }
            case 4 -> {                                                    // Frost
                target.setTicksFrozen(target.getTicksRequiredToFreeze() + 120);
                target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 4));
            }
            case 5 -> {                                                    // Sweep: half the blow cuts everything else near
                for (LivingEntity other : level.getEntitiesOfClass(LivingEntity.class, target.getBoundingBox().inflate(3.0),
                        e -> e != target && e != attacker && e.isAlive() && !(e instanceof Player))) {
                    other.hurt(attacker.damageSources().mobAttack(attacker), this.getDamage() * 0.5f);
                }
                com.aurelia.Perf.particles(level, ParticleTypes.SWEEP_ATTACK, target.getX(), target.getY() + 1.0, target.getZ(), 3, 1.0, 0.2, 1.0, 0.0);
            }
            case 6 -> {                                                    // Time
                target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 6));
                target.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 100, 1));
                target.setDeltaMovement(Vec3.ZERO);
            }
            default -> {                                                   // Spores
                for (LivingEntity other : level.getEntitiesOfClass(LivingEntity.class, target.getBoundingBox().inflate(3.5),
                        e -> e != attacker && e.isAlive() && !(e instanceof Player))) {
                    other.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 2));
                    other.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 100, 0));
                }
            }
        }
        return r;
    }

    // ---- Singularity: a black hole six blocks ahead drags in everything within twelve, then collapses

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level instanceof ServerLevel server) {
            singularity(server, player);
            stack.hurtAndBreak(4, player, p -> p.broadcastBreakEvent(hand));
        }
        player.getCooldowns().addCooldown(this, COOLDOWN);
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    private static void singularity(ServerLevel level, Player player) {
        Vec3 eye = player.getEyePosition();
        Vec3 want = eye.add(player.getLookAngle().scale(6.0));
        Vec3 at = level.clip(new ClipContext(eye, want, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player)).getLocation();
        List<LivingEntity> caught = level.getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(12.0),
                e -> e != player && e.isAlive() && (e instanceof Enemy || (e instanceof Mob m && m.getTarget() == player)));
        for (LivingEntity e : caught) {
            Vec3 in = at.subtract(e.position());
            double d = Math.max(1.0, in.length());
            Vec3 pull = in.normalize().scale(Math.min(2.2, 0.5 + d * 0.18));
            e.push(pull.x, Math.min(0.6, pull.y + 0.25), pull.z);
            e.hurtMarked = true;
            e.hurt(player.damageSources().playerAttack(player), 30.0f);
            e.addEffect(new MobEffectInstance(MobEffects.WITHER, 100, 1));
            e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 2));
        }
        for (int k = 0; k < 40; k++) {                                     // the disc, then the collapse
            double a = k * Math.PI / 20;
            com.aurelia.Perf.particles(level, new DustParticleOptions(COLORS[k % 8], 2.0f), at.x + Math.cos(a) * 3.0, at.y, at.z + Math.sin(a) * 3.0,
                    2, 0.1, 0.1, 0.1, 0.0);
        }
        com.aurelia.Perf.particles(level, ParticleTypes.REVERSE_PORTAL, at.x, at.y, at.z, 260, 4.0, 4.0, 4.0, 0.6);
        com.aurelia.Perf.particles(level, ParticleTypes.SQUID_INK, at.x, at.y, at.z, 80, 0.6, 0.6, 0.6, 0.05);
        com.aurelia.Perf.particles(level, ParticleTypes.SONIC_BOOM, at.x, at.y, at.z, 1, 0.0, 0.0, 0.0, 0.0);
        level.playSound(null, at.x, at.y, at.z, SoundEvents.WARDEN_SONIC_BOOM, SoundSource.PLAYERS, 3.0f, 0.5f);
        level.playSound(null, at.x, at.y, at.z, SoundEvents.END_PORTAL_SPAWN, SoundSource.PLAYERS, 1.0f, 1.6f);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        int edge = Math.floorMod(stack.getOrCreateTag().getInt(EDGE), 8);
        tooltip.add(Component.translatable(this.getDescriptionId() + ".power").withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable(this.getDescriptionId() + ".ability").withStyle(ChatFormatting.LIGHT_PURPLE));
        tooltip.add(Component.literal("Next edge: " + EDGES[edge]).withStyle(ChatFormatting.AQUA));
        tooltip.add(Component.translatable(this.getDescriptionId() + ".lore").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.ITALIC));
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return true;
    }
}
