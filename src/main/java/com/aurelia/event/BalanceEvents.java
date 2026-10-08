package com.aurelia.event;

import com.aurelia.AureliaConfig;
import com.aurelia.entity.AureliaBoss;
import com.aurelia.entity.Lieutenant;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/** Applies the config's multipliers to each Aurelia creature once, the first time it enters a world. */
public class BalanceEvents {
    private static final String TAG = "aurelia_scaled";

    @SubscribeEvent
    public void onJoin(EntityJoinLevelEvent event) {
        if (event.getLevel().isClientSide() || !(event.getEntity() instanceof LivingEntity mob)) {
            return;
        }
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(mob.getType());
        if (id == null || !"aurelia".equals(id.getNamespace()) || mob.getPersistentData().getBoolean(TAG)) {
            return;
        }
        double health, damage;
        if (mob instanceof AureliaBoss) {
            health = AureliaConfig.WARDEN_HEALTH.get();
            damage = AureliaConfig.WARDEN_DAMAGE.get();
        } else if (mob instanceof Lieutenant) {
            health = AureliaConfig.LIEUTENANT_HEALTH.get();
            damage = AureliaConfig.LIEUTENANT_DAMAGE.get();
        } else if (mob instanceof Enemy) {
            health = AureliaConfig.GUARD_HEALTH.get();
            damage = AureliaConfig.GUARD_DAMAGE.get();
        } else {
            return;                                                     // the realms' wildlife is left alone
        }
        mob.getPersistentData().putBoolean(TAG, true);
        if (health != 1.0) {
            scale(mob, Attributes.MAX_HEALTH, health);
            mob.setHealth(mob.getMaxHealth());
        }
        if (damage != 1.0) {
            scale(mob, Attributes.ATTACK_DAMAGE, damage);
        }
    }

    private static void scale(LivingEntity mob, Attribute attribute, double by) {
        AttributeInstance a = mob.getAttribute(attribute);
        if (a != null) {
            a.setBaseValue(a.getBaseValue() * by);
        }
    }
}
