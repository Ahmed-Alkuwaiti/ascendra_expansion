package com.aurelia.item;

import com.google.common.collect.ImmutableMultimap;
import com.google.common.collect.Multimap;
import java.util.List;
import java.util.UUID;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import java.util.function.Consumer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

/** A piece of a realm's armor set. The full-set bonus lives in KitEvents. */
public class RealmArmorItem extends ArmorItem {
    private final RealmArmorMaterial realm;

    public RealmArmorItem(RealmArmorMaterial material, Type type, Properties properties) {
        super(material, type, properties);
        this.realm = material;
    }

    public RealmArmorMaterial realm() {
        return this.realm;
    }

    /** The full set this player is wearing, or null. */
    @Nullable
    public static RealmArmorMaterial fullSet(Player player) {
        RealmArmorMaterial set = null;
        for (EquipmentSlot slot : new EquipmentSlot[] {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET}) {
            ItemStack s = player.getItemBySlot(slot);
            if (!(s.getItem() instanceof RealmArmorItem a)) {
                return null;
            }
            if (set == null) {
                set = a.realm;
            } else if (set != a.realm) {
                return null;
            }
        }
        return set;
    }

    private String piece() {
        return this.realm.id() + "_" + switch (this.getType()) {
            case HELMET -> "helmet";
            case CHESTPLATE -> "chestplate";
            case LEGGINGS -> "leggings";
            default -> "boots";
        };
    }

    /** Each piece wears its own painted texture, matching its 3D model. */
    @Override
    public String getArmorTexture(ItemStack stack, Entity entity, EquipmentSlot slot, String type) {
        return "aurelia:textures/models/armor/" + piece() + ".png";
    }

    @Override
    public void initializeClient(Consumer<IClientItemExtensions> consumer) {
        consumer.accept(new com.aurelia.client.RealmArmorClient(piece()));
    }

    private static final UUID[] VIGOR = {UUID.fromString("5d1c7a52-8f0e-4b3a-9c6e-1a2b3c4d5e01"), UUID.fromString("5d1c7a52-8f0e-4b3a-9c6e-1a2b3c4d5e02"),
            UUID.fromString("5d1c7a52-8f0e-4b3a-9c6e-1a2b3c4d5e03"), UUID.fromString("5d1c7a52-8f0e-4b3a-9c6e-1a2b3c4d5e04")};

    /** Each piece of Genesis armor also adds 5 max health. */
    @Override
    public Multimap<Attribute, AttributeModifier> getAttributeModifiers(EquipmentSlot slot, ItemStack stack) {
        Multimap<Attribute, AttributeModifier> base = super.getAttributeModifiers(slot, stack);
        if (this.realm != RealmArmorMaterial.GENESIS || slot != this.getEquipmentSlot()) {
            return base;
        }
        ImmutableMultimap.Builder<Attribute, AttributeModifier> out = ImmutableMultimap.builder();
        out.putAll(base);
        out.put(Attributes.MAX_HEALTH, new AttributeModifier(VIGOR[slot.getIndex()], "Genesis vigor", 5.0, AttributeModifier.Operation.ADDITION));
        return out.build();
    }

    @Override
    public boolean canWalkOnPowderedSnow(ItemStack stack, LivingEntity wearer) {
        return this.realm == RealmArmorMaterial.RIME && this.getType() == Type.BOOTS;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.aurelia.armor_bonus." + this.realm.id()).withStyle(ChatFormatting.GOLD));
        if (this.realm == RealmArmorMaterial.GENESIS) {
            for (int i = 0; i < 5; i++) {
                tooltip.add(Component.literal(" ").append(Component.translatable("item.aurelia.armor_bonus.genesis." + i))
                        .withStyle(i == 3 ? ChatFormatting.LIGHT_PURPLE : ChatFormatting.GRAY));
            }
        }
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return this.realm == RealmArmorMaterial.GENESIS || super.isFoil(stack);
    }
}
