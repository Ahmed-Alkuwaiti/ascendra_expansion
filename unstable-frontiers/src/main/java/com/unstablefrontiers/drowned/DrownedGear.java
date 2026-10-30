package com.unstablefrontiers.drowned;

import com.unstablefrontiers.UnstableFrontiers;
import java.lang.reflect.Method;
import java.util.Optional;
import java.util.function.Predicate;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.neoforged.fml.ModList;

/**
 * Where diving gear counts as worn: its Curios slot (when Curios is installed; looked up through Curios's public API by
 * reflection, so the addon has no hard dependency on it) or the matching armour slot.
 */
public final class DrownedGear {
    private static boolean looked;
    private static Method getInventory, findFirst, slotStack;

    private DrownedGear() {}

    private static void lookUp() {
        if (looked) {
            return;
        }
        looked = true;
        if (!ModList.get().isLoaded("curios")) {
            return;
        }
        try {
            Class<?> api = Class.forName("top.theillusivec4.curios.api.CuriosApi");
            getInventory = api.getMethod("getCuriosInventory", LivingEntity.class);
            Class<?> handler = Class.forName("top.theillusivec4.curios.api.type.capability.ICuriosItemHandler");
            findFirst = handler.getMethod("findFirstCurio", Predicate.class);
            slotStack = Class.forName("top.theillusivec4.curios.api.SlotResult").getMethod("stack");
        } catch (ReflectiveOperationException e) {
            UnstableFrontiers.LOGGER.warn("Curios is installed but its API was not found ({}); diving gear works in armour slots only", e.toString());
            getInventory = null;
        }
    }

    /** The first worn piece matching the test, or EMPTY. */
    public static ItemStack worn(LivingEntity e, Predicate<ItemStack> test) {
        for (EquipmentSlot s : new EquipmentSlot[] {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.FEET}) {
            ItemStack st = e.getItemBySlot(s);
            if (!st.isEmpty() && test.test(st)) {
                return st;
            }
        }
        lookUp();
        if (getInventory != null) {
            try {
                Optional<?> inv = (Optional<?>) getInventory.invoke(null, e);
                if (inv.isPresent()) {
                    Optional<?> r = (Optional<?>) findFirst.invoke(inv.get(), test);
                    if (r.isPresent()) {
                        return (ItemStack) slotStack.invoke(r.get());
                    }
                }
            } catch (ReflectiveOperationException | RuntimeException ex) {
                // a Curios version with a different API: armour slots still work
            }
        }
        return ItemStack.EMPTY;
    }

    public static ItemStack goggles(LivingEntity e) {
        return worn(e, s -> s.getItem() instanceof DivingGearItem g && g.isGoggles());
    }

    public static boolean deepSight(LivingEntity e) {
        return goggles(e).getItem() instanceof DivingGearItem g && g.kind() == DivingGearItem.Kind.DEEP_GOGGLES;
    }

    public static ItemStack rig(LivingEntity e) {
        return worn(e, s -> s.getItem() instanceof DivingGearItem g && g.isRig());
    }

    public static boolean fins(LivingEntity e) {
        return !worn(e, s -> s.getItem() instanceof DivingGearItem g && g.kind() == DivingGearItem.Kind.FINS).isEmpty();
    }

    public static boolean charm(LivingEntity e) {
        return !worn(e, s -> s.getItem() instanceof DivingGearItem g && g.kind() == DivingGearItem.Kind.CHARM).isEmpty();
    }
}
