package com.unstablefrontiers.item;

import com.unstablefrontiers.ecology.Creatures;
import com.unstablefrontiers.registry.ModSounds;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.AABB;

/**
 * The Cagewright's Shackle. Used on a hostile creature brought below a third of its health, it binds it for 60 seconds:
 * it turns on the hostile creatures around you and will not attack players. When the time is up the shackle claims it
 * and it crumbles, dropping nothing, so it is a tactic, not a farm. Bosses (c:bosses, Antarchy's spell-resistant bosses)
 * and named elites cannot be bound. Six uses; repaired with Rookery Talons.
 */
public class ShackleItem extends TrophyItem {
    public static final int DURATION = 1200;
    private static final TagKey<EntityType<?>> BOSSES = TagKey.create(Registries.ENTITY_TYPE, ResourceLocation.fromNamespaceAndPath("c", "bosses"));
    private static final TagKey<EntityType<?>> ANTARCHY_BOSSES = TagKey.create(Registries.ENTITY_TYPE,
            ResourceLocation.fromNamespaceAndPath("antarchy", "spell_resistant_boss"));

    private record Bond(UUID owner, long until, ServerLevel level) {}

    private static final Map<UUID, Bond> BOUND = new HashMap<>();

    public ShackleItem(Properties properties) {
        super(properties, 3);
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        if (!(player.level() instanceof ServerLevel level) || !(player instanceof ServerPlayer sp)) {
            return InteractionResult.SUCCESS;
        }
        if (!(target instanceof Mob mob) || !(target instanceof Enemy) || BOUND.containsKey(target.getUUID())) {
            return InteractionResult.PASS;
        }
        if (target.getType().is(BOSSES) || target.getType().is(ANTARCHY_BOSSES) || target.hasCustomName()) {
            sp.displayClientMessage(Component.translatable("message.unstable_frontiers.shackle_boss").withStyle(ChatFormatting.RED), true);
            return InteractionResult.FAIL;
        }
        if (target.getHealth() > target.getMaxHealth() / 3.0F) {
            sp.displayClientMessage(Component.translatable("message.unstable_frontiers.shackle_strong").withStyle(ChatFormatting.GRAY), true);
            return InteractionResult.FAIL;
        }
        mob.setTarget(null);
        mob.getPersistentData().putString(Creatures.ROLE, Creatures.ROLE_BOUND);
        BOUND.put(mob.getUUID(), new Bond(sp.getUUID(), level.getGameTime() + DURATION, level));
        stack.hurtAndBreak(1, sp, LivingEntity.getSlotForHand(hand));
        level.playSound(null, mob.blockPosition(), ModSounds.SHACKLE.get(), SoundSource.PLAYERS, 1.0F, 1.0F);
        level.sendParticles(ParticleTypes.ENCHANT, mob.getX(), mob.getY() + mob.getBbHeight(), mob.getZ(), 20, 0.4D, 0.4D, 0.4D, 0.2D);
        sp.displayClientMessage(Component.translatable("message.unstable_frontiers.shackle_bound", mob.getDisplayName()).withStyle(ChatFormatting.AQUA), true);
        return InteractionResult.CONSUME;
    }

    @Override
    public boolean isValidRepairItem(ItemStack stack, ItemStack repair) {
        return repair.is(com.unstablefrontiers.registry.ModItems.ROOKERY_TALON.get());
    }

    public static boolean isBound(Entity e) {
        return BOUND.containsKey(e.getUUID());
    }

    /** Every 10 ticks: bound creatures pick fights with hostiles near their owner; expired bonds crumble. */
    public static void tick(ServerLevel level, long time) {
        if (time % 10 != 0 || BOUND.isEmpty()) {
            return;
        }
        Iterator<Map.Entry<UUID, Bond>> it = BOUND.entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<UUID, Bond> e = it.next();
            if (e.getValue().level() != level) {
                continue;
            }
            Entity ent = level.getEntity(e.getKey());
            if (!(ent instanceof Mob mob) || !mob.isAlive()) {
                it.remove();
                continue;
            }
            if (time >= e.getValue().until()) {
                level.sendParticles(ParticleTypes.SOUL, mob.getX(), mob.getY() + 0.5D, mob.getZ(), 16, 0.4D, 0.5D, 0.4D, 0.02D);
                mob.discard();
                it.remove();
                continue;
            }
            Player owner = level.getPlayerByUUID(e.getValue().owner());
            if (mob.getTarget() == null || !mob.getTarget().isAlive() || mob.getTarget() instanceof Player) {
                AABB area = (owner != null ? owner.getBoundingBox() : mob.getBoundingBox()).inflate(16.0D);
                Mob best = null;
                double bd = Double.MAX_VALUE;
                for (Mob m : level.getEntitiesOfClass(Mob.class, area, m -> m != mob && m.isAlive() && m instanceof Enemy && !isBound(m))) {
                    double d = m.distanceToSqr(mob);
                    if (d < bd) {
                        bd = d;
                        best = m;
                    }
                }
                mob.setTarget(best);
                if (best != null && best.getTarget() == null) {
                    best.setTarget(mob);
                }
                if (best == null && owner != null && mob.distanceToSqr(owner) > 36) {
                    mob.getNavigation().moveTo(owner, 1.1D);
                }
            }
        }
    }

    public static void clearMemory() {
        BOUND.clear();
    }
}
