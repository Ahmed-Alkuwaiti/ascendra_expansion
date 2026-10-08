package com.aurelia.event;

import com.aurelia.AureliaConfig;
import com.aurelia.registry.ExtraContent;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** The first time a player joins a world: a short guide to the quest, the Wayfinder's Lodestar and the Aurelian Bestiary. */
public class OnboardingEvents {
    private static final String TAG = "aurelia_welcomed";

    private static final String[] GUIDE = {
            "§lWAYFARER'S GUIDE§r\n\nAurelia's crown is broken. Eight realms lie behind eight Waygates, each kept by a Warden.\n\nThis is how to begin.",
            "§l1. Find a citadel§r\n\nUse the Wayfinder's Lodestar in the Overworld: it points to the nearest citadel.\n\nThe first is the Rootbound Citadel, grown into a giant tree in a forest.",
            "§l2. Open the way§r\n\nKill the guardians of the seal at the door, then finish the citadel's rite. The lecterns inside explain it.\n\nWhen the rite is done, the Waygate wakes.",
            "§l3. The lieutenants§r\n\nStep through. Lairs ring the landing pad, each with a beacon. Crouch and use a lair's seal to wake its lieutenant, and kill it.\n\nThe Lodestar points to the nearest lair.",
            "§l4. The Warden§r\n\nWhen every lair is dark, crouch and touch the altar on the pad. Beat the Warden for its shard and its relic.\n\nThe Waygate on the pad takes you home.",
            "§l5. Grow stronger§r\n\nEvery realm has its own ore, armour, weapon and tools, a creature, landmarks, and a dungeon in each of its three biomes.\n\nLieutenant trophies make realm charms.",
            "§l6. The road§r\n\nGrove, Skyreach, Hollow: the Crown of Aurelia.\n\nDrowned, Pale, Scarlet: the Ascendant Crown.\n\nClockwork, Mycelial: the Eternal Crown.",
            "§l7. The end§r\n\nAll eight relics wake the Convergence Gate. Beyond it lies the Last Realm, and the Unmaker.\n\nThe Bestiary knows every foe. Good luck.\n\n§8- The Last Archivist"
    };

    public static ItemStack guide() {
        ItemStack book = new ItemStack(Items.WRITTEN_BOOK);
        var tag = book.getOrCreateTag();
        tag.putString("title", "Wayfarer's Guide");
        tag.putString("author", "The Last Archivist");
        ListTag pages = new ListTag();
        for (String page : GUIDE) {
            pages.add(StringTag.valueOf(Component.Serializer.toJson(Component.literal(page))));
        }
        tag.put("pages", pages);
        return book;
    }

    @SubscribeEvent
    public void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        Player player = event.getEntity();
        if (player.level().isClientSide || !AureliaConfig.STARTER_KIT.get()) {
            return;
        }
        var data = player.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        if (data.getBoolean(TAG)) {
            return;
        }
        data.putBoolean(TAG, true);
        player.getPersistentData().put(Player.PERSISTED_NBT_TAG, data);
        for (ItemStack stack : new ItemStack[] {guide(), new ItemStack(ExtraContent.WAYFINDERS_LODESTAR.get()),
                new ItemStack(ExtraContent.AURELIAN_BESTIARY.get())}) {
            if (!player.getInventory().add(stack)) {
                player.drop(stack, false);
            }
        }
        player.sendSystemMessage(Component.literal("Aurelia: The Shattered Crown").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD));
        player.sendSystemMessage(Component.literal("Read the Wayfarer's Guide, then use the Lodestar to find your first citadel.")
                .withStyle(ChatFormatting.GRAY));
    }
}
