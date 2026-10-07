package com.aurelia.item;

import com.aurelia.AureliaMod;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Ingredient;

public enum AurelianArmorMaterial implements ArmorMaterial {
    AURELIAN;

    @Override
    public int getDurabilityForType(ArmorItem.Type type) {
        return 3000;
    }

    @Override
    public int getDefenseForType(ArmorItem.Type type) {
        return 6;
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
        // Texture: assets/aurelia/textures/models/armor/aurelian_layer_1.png
        return AureliaMod.MODID + ":aurelian";
    }

    @Override
    public float getToughness() {
        return 4.0f;
    }

    @Override
    public float getKnockbackResistance() {
        return 0.1f;
    }
}
