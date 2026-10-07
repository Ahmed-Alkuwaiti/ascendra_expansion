package com.aurelia.item;

import com.aurelia.AureliaMod;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Ingredient;

public enum AurelianArmorMaterial implements ArmorMaterial {
    // Texture: assets/aurelia/textures/models/armor/<name>_layer_1.png
    AURELIAN("aurelian", 3000, 6, 4.0f, 0.1f),
    ASCENDANT("ascendant", 6000, 8, 6.0f, 0.25f),
    ETERNAL("eternal", 9000, 10, 8.0f, 0.4f);

    private final String name;
    private final int durability;
    private final int defense;
    private final float toughness;
    private final float knockbackResistance;

    AurelianArmorMaterial(String name, int durability, int defense, float toughness, float knockbackResistance) {
        this.name = name;
        this.durability = durability;
        this.defense = defense;
        this.toughness = toughness;
        this.knockbackResistance = knockbackResistance;
    }

    @Override
    public int getDurabilityForType(ArmorItem.Type type) {
        return this.durability;
    }

    @Override
    public int getDefenseForType(ArmorItem.Type type) {
        return this.defense;
    }

    @Override
    public int getEnchantmentValue() {
        return 30;
    }

    @Override
    public SoundEvent getEquipSound() {
        return SoundEvents.ARMOR_EQUIP_NETHERITE;
    }

    @Override
    public Ingredient getRepairIngredient() {
        return Ingredient.of(Items.NETHER_STAR);
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
}
