package com.aurelia.item;

import com.aurelia.AureliaMod;
import com.aurelia.registry.ModItems;
import java.util.function.Supplier;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.crafting.Ingredient;

/** One armor set per realm, made from that realm's material. Texture: textures/models/armor/<name>_layer_1.png and _2. */
public enum RealmArmorMaterial implements ArmorMaterial {
    VERDANT("verdant", 34, new int[] {3, 8, 6, 3}, 15, 2.0f, 0.0f, () -> ModItems.VERDANT_SHARD.get()),
    STORMGLASS("stormglass", 34, new int[] {3, 8, 6, 3}, 15, 2.0f, 0.0f, () -> ModItems.STORMGLASS_SHARD.get()),
    EMBERHEART("emberheart", 36, new int[] {3, 8, 6, 3}, 15, 2.5f, 0.05f, () -> ModItems.EMBERHEART.get()),
    TIDESTONE("tidestone", 37, new int[] {3, 8, 6, 3}, 16, 3.0f, 0.05f, () -> ModItems.TIDESTONE_SHARD.get()),
    RIME("rime", 37, new int[] {3, 8, 6, 3}, 16, 3.0f, 0.05f, () -> ModItems.RIME_CRYSTAL.get()),
    SUNGLASS("sunglass", 38, new int[] {3, 8, 6, 3}, 16, 3.0f, 0.1f, () -> ModItems.SUNGLASS_SHARD.get()),
    CHRONITE("chronite", 40, new int[] {4, 9, 7, 4}, 18, 3.5f, 0.1f, () -> ModItems.CHRONITE_SHARD.get()),
    BLOOMSPORE("bloomspore", 40, new int[] {4, 9, 7, 4}, 18, 3.5f, 0.1f, () -> ModItems.BLOOMSPORE.get());

    private static final int[] BASE_DURABILITY = {11, 16, 15, 13};   // helmet, chestplate, leggings, boots
    private final String name;
    private final int durability;
    private final int[] defense;
    private final int enchantment;
    private final float toughness;
    private final float knockbackResistance;
    private final Supplier<Item> repair;

    RealmArmorMaterial(String name, int durability, int[] defense, int enchantment, float toughness, float knockbackResistance,
                       Supplier<Item> repair) {
        this.name = name;
        this.durability = durability;
        this.defense = defense;
        this.enchantment = enchantment;
        this.toughness = toughness;
        this.knockbackResistance = knockbackResistance;
        this.repair = repair;
    }

    private static int slot(ArmorItem.Type type) {
        return switch (type) {
            case HELMET -> 0;
            case CHESTPLATE -> 1;
            case LEGGINGS -> 2;
            default -> 3;
        };
    }

    @Override
    public int getDurabilityForType(ArmorItem.Type type) {
        return BASE_DURABILITY[slot(type)] * this.durability;
    }

    @Override
    public int getDefenseForType(ArmorItem.Type type) {
        return this.defense[slot(type)];
    }

    @Override
    public int getEnchantmentValue() {
        return this.enchantment;
    }

    @Override
    public SoundEvent getEquipSound() {
        return SoundEvents.ARMOR_EQUIP_DIAMOND;
    }

    @Override
    public Ingredient getRepairIngredient() {
        return Ingredient.of(this.repair.get());
    }

    @Override
    public String getName() {
        return AureliaMod.MODID + ":" + this.name;
    }

    @Override
    public float getToughness() {
        return this.toughness;
    }

    @Override
    public float getKnockbackResistance() {
        return this.knockbackResistance;
    }

    public String id() {
        return this.name;
    }
}
