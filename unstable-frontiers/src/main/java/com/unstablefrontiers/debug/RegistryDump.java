package com.unstablefrontiers.debug;

import com.unstablefrontiers.UnstableFrontiers;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.world.item.component.ItemAttributeModifiers;

/**
 * Debug only: logs the real, in-game numbers of another mod's creatures and items (after that mod's and the pack's own
 * configuration and scripts have applied), so the addon is balanced against what players actually meet.
 * Run with /frontier debug dump &lt;namespace&gt;. Each line starts with DUMP so CI can pick them out.
 */
public final class RegistryDump {
    private RegistryDump() {}

    public static int dump(ServerLevel level, String ns) {
        int n = 0;
        for (ResourceLocation id : BuiltInRegistries.ENTITY_TYPE.keySet()) {
            if (!id.getNamespace().equals(ns)) {
                continue;
            }
            EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.get(id);
            String line;
            try {
                Entity e = type.create(level);
                if (e instanceof LivingEntity) {
                    // add it to the world briefly so spawn-time scaling (the pack's scripts) applies, then read it
                    e.moveTo(0.5D, level.getMaxBuildHeight() - 20, 0.5D);
                    e.setNoGravity(true);
                    level.addFreshEntity(e);
                }
                if (e instanceof LivingEntity le) {
                    line = String.format("entity %s category=%s size=%.2fx%.2f class=%s health=%.1f attack=%s armor=%s follow=%s speed=%s flying=%s fireImmune=%s",
                            id, type.getCategory(), type.getWidth(), type.getHeight(), e.getClass().getSimpleName(), le.getMaxHealth(),
                            val(le, Attributes.ATTACK_DAMAGE), val(le, Attributes.ARMOR), val(le, Attributes.FOLLOW_RANGE),
                            val(le, Attributes.MOVEMENT_SPEED), le.getAttributes().hasAttribute(Attributes.FLYING_SPEED), type.fireImmune());
                    if (e instanceof Mob m) {
                        line += " persistent=" + m.isPersistenceRequired() + " canPickUp=" + m.canPickUpLoot();
                    }
                } else {
                    line = "entity " + id + " category=" + type.getCategory() + " (not living)";
                }
                if (e != null) {
                    e.discard();
                }
            } catch (Throwable t) {
                line = "entity " + id + " could not be created: " + t;
            }
            UnstableFrontiers.LOGGER.info("DUMP {}", line);
            n++;
        }
        for (ResourceLocation id : BuiltInRegistries.ITEM.keySet()) {
            if (!id.getNamespace().equals(ns)) {
                continue;
            }
            Item item = BuiltInRegistries.ITEM.get(id);
            ItemStack stack = new ItemStack(item);
            StringBuilder sb = new StringBuilder("item ").append(id);
            if (stack.isDamageableItem()) {
                sb.append(" durability=").append(stack.getMaxDamage());
            }
            ItemAttributeModifiers mods = stack.getOrDefault(DataComponents.ATTRIBUTE_MODIFIERS, ItemAttributeModifiers.EMPTY);
            mods.modifiers().forEach(e -> sb.append(' ').append(e.attribute().unwrapKey().map(k -> k.location().getPath()).orElse("?"))
                    .append('=').append(String.format("%.2f", e.modifier().amount())).append('@').append(e.slot().getSerializedName()));
            if (stack.has(DataComponents.FOOD)) {
                sb.append(" food");
            }
            UnstableFrontiers.LOGGER.info("DUMP {}", sb);
            n++;
        }
        return n;
    }

    private static String val(LivingEntity e, Holder<Attribute> a) {
        return e.getAttributes().hasAttribute(a) ? String.format("%.2f", e.getAttributeValue(a)) : "-";
    }
}
