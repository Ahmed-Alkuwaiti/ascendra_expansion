package com.aurelia.item;

import com.aurelia.registry.ModItems;
import java.util.function.Supplier;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.crafting.Ingredient;

/** The metal of each realm's signature weapon and tools, and of the Unmaker's. */
public enum RealmTier implements Tier {
    VERDANT(1800, 4.0f, () -> ModItems.VERDANTITE_INGOT.get()),
    STORMGLASS(1800, 4.0f, () -> ModItems.AETHERIUM_INGOT.get()),
    EMBERHEART(1900, 4.0f, () -> ModItems.SOULSTEEL_INGOT.get()),
    TIDESTONE(2100, 4.5f, () -> ModItems.TIDESTEEL_INGOT.get()),
    RIME(2100, 4.5f, () -> ModItems.RIME_CRYSTAL.get()),
    SUNGLASS(2200, 5.0f, () -> ModItems.SUNGLASS_SHARD.get()),
    CHRONITE(2500, 5.0f, () -> ModItems.CHRONITE_INGOT.get()),
    BLOOMSPORE(2500, 5.5f, () -> ModItems.MYCELIAL_INGOT.get()),
    GENESIS(4000, 8.0f, () -> ModItems.GENESIS_INGOT.get());

    private final int uses;
    private final float damage;
    private final Supplier<Item> repair;

    RealmTier(int uses, float damage, Supplier<Item> repair) {
        this.uses = uses;
        this.damage = damage;
        this.repair = repair;
    }

    @Override
    public int getUses() {
        return this.uses;
    }

    @Override
    public float getSpeed() {
        return this == GENESIS ? 12.0f : 9.0f;
    }

    @Override
    public float getAttackDamageBonus() {
        return this.damage;
    }

    @Override
    @SuppressWarnings("deprecation")
    public int getLevel() {
        return 4;
    }

    @Override
    public int getEnchantmentValue() {
        return 18;
    }

    @Override
    public Ingredient getRepairIngredient() {
        return Ingredient.of(this.repair.get());
    }
}
