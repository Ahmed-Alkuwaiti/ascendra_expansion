package com.aurelia.world;

import com.aurelia.AureliaMod;
import com.aurelia.entity.AureliaBoss;
import com.aurelia.registry.ModEntities;
import com.aurelia.registry.ModItems;
import java.util.function.Supplier;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;

public enum Realm implements StringRepresentable {
    GROVE("grove", Integer.MIN_VALUE,
            Blocks.MOSSY_STONE_BRICKS, Blocks.STONE_BRICKS, Blocks.SHROOMLIGHT,
            "The Gaudy Grove", "Everything here grew too big, too bright, too loud.", ChatFormatting.GREEN,
            new String[] {
                    "You step out onto a landing pad of mossy stone. The air smells like sugar and rot.",
                    "At the centre of the pad stands the Warden's Altar. Crouch and touch it to wake the Warden.",
                    "The glowing Waygate behind you is your way home."
            },
            () -> null, () -> ModEntities.MOSSBACK_TITAN.get()),

    SKYREACH("skyreach", 120,
            Blocks.QUARTZ_BRICKS, Blocks.QUARTZ_BLOCK, Blocks.SEA_LANTERN,
            "Skyreach", "The sky tore itself into islands. It never stopped falling apart.", ChatFormatting.AQUA,
            new String[] {
                    "The wind shoves at you. Below the pad there is only cloud, and below the cloud, nothing.",
                    "Crouch and touch the Warden's Altar to call the Tempest Roc. Do not fall.",
                    "The Waygate at the edge of the pad will carry you home."
            },
            () -> ModItems.GROVE_SHARD.get(), () -> ModEntities.TEMPEST_ROC.get()),

    HOLLOW("hollow", 70,
            Blocks.POLISHED_BLACKSTONE_BRICKS, Blocks.BLACKSTONE, Blocks.SOUL_LANTERN,
            "The Hollow", "Something kept the dark here so it could not reach the others.", ChatFormatting.DARK_PURPLE,
            new String[] {
                    "There is no sky here, only a black stone ceiling and ash falling through the dark. The ground is warm, as if something just left.",
                    "Crouch and touch the Warden's Altar to face the Hollow King.",
                    "The Waygate behind you still hums. It remembers the way back."
            },
            () -> ModItems.STORM_SHARD.get(), () -> ModEntities.HOLLOW_KING.get());

    public final String id;
    public final ResourceKey<Level> dimension;
    /** Fixed standing height of the landing pad, or MIN_VALUE to use the terrain height at 0,0. */
    public final int fixedY;
    public final Block pad;
    public final Block foundation;
    public final Block light;
    public final String title;
    public final String subtitle;
    public final ChatFormatting color;
    public final String[] enterLines;
    private final Supplier<Item> requiredItem;
    private final Supplier<EntityType<? extends AureliaBoss>> boss;

    Realm(String id, int fixedY, Block pad, Block foundation, Block light,
          String title, String subtitle, ChatFormatting color, String[] enterLines,
          Supplier<Item> requiredItem, Supplier<EntityType<? extends AureliaBoss>> boss) {
        this.id = id;
        this.dimension = ResourceKey.create(Registries.DIMENSION, new ResourceLocation(AureliaMod.MODID, id));
        this.fixedY = fixedY;
        this.pad = pad;
        this.foundation = foundation;
        this.light = light;
        this.title = title;
        this.subtitle = subtitle;
        this.color = color;
        this.enterLines = enterLines;
        this.requiredItem = requiredItem;
        this.boss = boss;
    }

    /** The previous Warden's shard you must hold to use this realm's portal, or null for none. */
    @Nullable
    public Item requiredItem() {
        return requiredItem.get();
    }

    @Override
    public String getSerializedName() {
        return id;
    }

    public EntityType<? extends AureliaBoss> bossType() {
        return boss.get();
    }

    /** Returns the realm a level belongs to, or null for any other dimension. */
    @Nullable
    public static Realm of(Level level) {
        for (Realm realm : values()) {
            if (level.dimension().equals(realm.dimension)) {
                return realm;
            }
        }
        return null;
    }
}
