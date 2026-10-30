package com.unstablefrontiers.drowned;

import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.Equipable;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.CustomData;

/**
 * Wearable diving gear. Each piece goes in its Curios slot (goggles: head, rig: back, fins: feet, charm: necklace) when
 * Curios is installed, as Integrated Boogaloo has it, so the player keeps their armour; it also works worn in the matching
 * armour slot. A rig carries its air in seconds; the bar under the item shows how full it is.
 */
public class DivingGearItem extends Item implements Equipable {
    public enum Kind { GOGGLES, DEEP_GOGGLES, RIG, DEEP_RIG, FINS, CHARM }

    private final Kind kind;

    public DivingGearItem(Properties p, Kind kind) {
        super(p);
        this.kind = kind;
    }

    public Kind kind() {
        return kind;
    }

    public boolean isGoggles() {
        return kind == Kind.GOGGLES || kind == Kind.DEEP_GOGGLES;
    }

    public boolean isRig() {
        return kind == Kind.RIG || kind == Kind.DEEP_RIG;
    }

    /** Air a full tank holds, in seconds. */
    public int capacity() {
        return kind == Kind.DEEP_RIG ? 420 : kind == Kind.RIG ? 180 : 0;
    }

    @Override
    public EquipmentSlot getEquipmentSlot() {
        return switch (kind) {
            case GOGGLES, DEEP_GOGGLES -> EquipmentSlot.HEAD;
            case FINS -> EquipmentSlot.FEET;
            default -> EquipmentSlot.CHEST;
        };
    }

    public static int air(ItemStack s) {
        if (!(s.getItem() instanceof DivingGearItem g) || !g.isRig()) {
            return 0;
        }
        CompoundTag t = s.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
        return t.contains("air") ? t.getInt("air") : g.capacity();
    }

    public static void setAir(ItemStack s, int air) {
        if (s.getItem() instanceof DivingGearItem g && g.isRig()) {
            int v = Mth.clamp(air, 0, g.capacity());
            if (v != air(s) || !s.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag().contains("air")) {
                CustomData.update(DataComponents.CUSTOM_DATA, s, t -> t.putInt("air", v));
            }
        }
    }

    @Override
    public boolean isBarVisible(ItemStack s) {
        return isRig();
    }

    @Override
    public int getBarWidth(ItemStack s) {
        return Math.round(13.0F * air(s) / Math.max(1, capacity()));
    }

    @Override
    public int getBarColor(ItemStack s) {
        float f = air(s) / (float) Math.max(1, capacity());
        return f > 0.3F ? 0x4FC3F7 : f > 0.1F ? 0xFFB74D : 0xE53935;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        String key = "item.unstable_frontiers." + net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(this).getPath();
        if (isRig()) {
            int a = air(stack);
            tooltip.add(Component.translatable("item.unstable_frontiers.rig.air", a / 60, String.format("%02d", a % 60), capacity() / 60)
                    .withStyle(ChatFormatting.AQUA));
        }
        for (int i = 0; i < 3; i++) {
            String k = key + ".tip" + i;
            if (net.minecraft.locale.Language.getInstance().has(k)) {
                tooltip.add(Component.translatable(k).withStyle(i == 0 ? ChatFormatting.GOLD : ChatFormatting.GRAY));
            }
        }
    }
}
