package com.aurelia.item;

import com.aurelia.registry.ModItems;
import java.util.function.Supplier;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.crafting.Ingredient;

/** The metal of each realm's signature weapon. */
public enum RealmTier implements Tier {
    VERDANT(1800, 4.0f, () -> ModItems.VERDANT_SHARD.get()),
    STORMGLASS(1800, 4.0f, () -> ModItems.STORMGLASS_SHARD.get()),
    EMBERHEART(1900, 4.0f, () -> ModItems.EMBERHEART.get()),
    TIDESTONE(2100, 4.5f, () -> ModItems.TIDESTONE_SHARD.get()),
    RIME(2100, 4.5f, () -> ModItems.RIME_CRYSTAL.get()),
    SUNGLASS(2200, 5.0f, () -> ModItems.SUNGLASS_SHARD.get()),
    CHRONITE(2500, 5.0f, () -> ModItems.CHRONITE_SHARD.get()),
    BLOOMSPORE(2500, 5.5f, () -> ModItems.BLOOMSPORE.get());

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
        return 9.0f;
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
