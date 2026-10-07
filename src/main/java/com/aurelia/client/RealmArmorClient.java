package com.aurelia.client;

import java.util.HashMap;
import java.util.Map;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;

/** Swaps the vanilla armor shape for the piece's own 3D model (ArmorModels), baked once and reused. */
public class RealmArmorClient implements IClientItemExtensions {
    private static final Map<String, HumanoidModel<LivingEntity>> MODELS = new HashMap<>();
    private final String piece;

    public RealmArmorClient(String piece) {
        this.piece = piece;
    }

    @Override
    public HumanoidModel<?> getHumanoidArmorModel(LivingEntity entity, ItemStack stack, EquipmentSlot slot, HumanoidModel<?> original) {
        return MODELS.computeIfAbsent(this.piece,
                p -> new HumanoidModel<>(Minecraft.getInstance().getEntityModels().bakeLayer(ArmorModels.layer(p))));
    }
}
