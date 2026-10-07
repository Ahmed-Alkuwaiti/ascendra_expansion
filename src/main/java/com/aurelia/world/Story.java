package com.aurelia.world;

import net.minecraft.ChatFormatting;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

/** All of the narrative text in one place so it is easy to rewrite. */
public final class Story {
    private Story() {}

    // ---- Boss phase lines (shown when a Warden crosses 50% health) ----
    public static final String TITAN_PHASE = "Mossback roars. The whole grove answers.";
    public static final String ROC_PHASE = "The sky darkens. Thunder gathers under the Roc's wings.";
    public static final String KING_PHASE = "The Hollow King's armour splits. The dark pours out of him.";

    // ---- Boss final-phase lines (shown at 33% health) ----
    public static final String TITAN_FINAL = "Mossback tears up the roots and throws away the last of his gentleness.";
    public static final String ROC_FINAL = "The storm stops pretending to be weather.";
    public static final String KING_FINAL = "The Hollow King speaks once, in the Sovereign's voice: \"Please.\"";

    // ---- Boss death lines (the story beats) ----
    public static final String TITAN_DEATH =
            "The roots fall still. \"I only wanted it to keep growing,\" Mossback whispers. "
                    + "A Grove Shard glows where he fell. Carry it in your hand to the Stormwatch Citadel in the mountains; its portal will know you.";
    public static final String ROC_DEATH =
            "The storm breaks and the Roc spirals down through the cloud. \"The sky was only trying to hold on,\" says the wind. "
                    + "A Storm Shard falls into your hands. Carry it down to the Ashen Citadel under the badlands; its portal will know you.";
    public static final String KING_DEATH =
            "The Hollow King kneels, and his helm rolls away. Underneath is the Sovereign's own face. "
                    + "\"I took the dark into myself so it could not reach the others,\" she says. \"Finish what I started.\" "
                    + "A Void Shard cools in the ash. Three shards, and a block of each realm's heart-stone: verdant, stormglass, emberheart. Reforge the crown.";

    // ---- Act two: the outer realms ----
    public static final String VORATH_PHASE = "Vorath rolls over in the deep, and the whole sea tilts with him.";
    public static final String VORATH_FINAL = "Vorath stops circling. He is not hunting any more. He is simply hungry.";
    public static final String VORATH_DEATH =
            "Vorath sinks, slowly, and for the first time in an age the sea lies flat and quiet. "
                    + "\"They were safe inside me,\" rumbles the deep. \"Nothing could drown them twice.\" "
                    + "A Leviathan's Pearl rolls onto the stone. Carry it north to the Rimefast Citadel in the snow; its portal will know you.";
    public static final String SILENCE_PHASE = "The White Silence tilts its mask. It has heard enough of you to make copies.";
    public static final String SILENCE_FINAL = "The snow stops falling. Even the wind holds its breath.";
    public static final String SILENCE_DEATH =
            "The mask cracks down the middle. Behind it there is no face, only a voice you last heard in the Hollow: "
                    + "\"Thank you for being quiet with me.\" "
                    + "A Frozen Tear lies in the snow where it stood. Carry it south to the Sunscar Citadel in the desert.";
    public static final String KHARZUL_PHASE = "Kharzul flips his hourglass. The sand begins to fall upward.";
    public static final String KHARZUL_FINAL = "Cracks race across the Reaper's glass. He does not slow down. He has never once slowed down.";
    public static final String KHARZUL_DEATH =
            "The hourglass in Kharzul's chest shatters and the sand pours out at last. "
                    + "\"She asked me for more time,\" he says. \"I took it from everyone else.\" "
                    + "The Reaper's Hourglass cools in your hand. Set it in the Crown beside the pearl and the tear.";

    public static void title(ServerPlayer player, String title, String subtitle, ChatFormatting color) {
        player.connection.send(new ClientboundSetTitlesAnimationPacket(15, 90, 30));
        player.connection.send(new ClientboundSetSubtitleTextPacket(
                Component.literal(subtitle).withStyle(ChatFormatting.GRAY)));
        player.connection.send(new ClientboundSetTitleTextPacket(
                Component.literal(title).withStyle(color, ChatFormatting.BOLD)));
    }

    public static void narrate(Player player, String line) {
        player.sendSystemMessage(Component.literal(line).withStyle(ChatFormatting.GOLD, ChatFormatting.ITALIC));
    }

    /** The second book, found the first time a player reaches one of the outer realms. */
    public static ItemStack secondChronicle() {
        String[] pages = {
                "THE OUTER CHRONICLE\n\nYou have reforged the Crown of Aurelia. Look closely at it. "
                        + "Three of its settings are empty, and they always were.",
                "Aurelia had three realms. Beyond them lay three more, and the Sovereign never spoke of them: "
                        + "the Drowned Expanse, the Pale Wastes, and the Scarlet Sands.",
                "Vorath kept the sea that carried her fleet. The White Silence kept every sound she could not bear to hear. "
                        + "Kharzul kept her time, and gave her as much of it as he could steal.",
                "When the crown broke, the outer Wardens did not sour. They kept going, exactly as they had been told, "
                        + "and that was worse.",
                "Each Tidewrack, Rimefast and Sunscar citadel holds a door, and a rite to open it. "
                        + "Bring the pearl, the tear and the hourglass home, and the crown will finally be finished.\n\n- The Last Archivist"
        };
        ItemStack book = new ItemStack(Items.WRITTEN_BOOK);
        var tag = book.getOrCreateTag();
        tag.putString("title", "The Outer Chronicle");
        tag.putString("author", "The Last Archivist");
        ListTag list = new ListTag();
        for (String page : pages) {
            list.add(StringTag.valueOf(Component.Serializer.toJson(Component.literal(page))));
        }
        tag.put("pages", list);
        return book;
    }

    /** The written book given to a player the first time they enter any realm. */
    public static ItemStack chronicle() {
        String[] pages = {
                "THE CHRONICLE OF AURELIA\n\nLong before the Waygates fell silent, Aurelia was a kingdom of three realms, "
                        + "bound together by a single crown. The Sovereign wore it, and the realms were at peace.",
                "Each realm kept a Warden, and each Warden held one shard of the crown in trust.\n\n"
                        + "In the Gaudy Grove, Mossback tended a garden that grew too joyfully to stop.",
                "In Skyreach, the Tempest Roc kept the winds.\n\n"
                        + "In the Hollow, a knight called the Hollow King kept the dark away from the others.",
                "Then the Sovereign vanished and the crown broke.\n\nThe shards soured the Wardens. "
                        + "The Grove grew wild. Skyreach tore itself into islands. The Hollow swallowed its king.",
                "If you are reading this, a Waygate has chosen you.\n\n"
                        + "Wake each Warden with its realm's sigil at its altar. Take back the shards.\n\n"
                        + "What waits at the end is not a reward. It is an answer.\n\n- The Last Archivist"
        };
        ItemStack book = new ItemStack(Items.WRITTEN_BOOK);
        var tag = book.getOrCreateTag();
        tag.putString("title", "The Chronicle of Aurelia");
        tag.putString("author", "The Last Archivist");
        ListTag list = new ListTag();
        for (String page : pages) {
            list.add(StringTag.valueOf(Component.Serializer.toJson(Component.literal(page))));
        }
        tag.put("pages", list);
        return book;
    }
}
