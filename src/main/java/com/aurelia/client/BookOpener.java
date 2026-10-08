package com.aurelia.client;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.inventory.BookViewScreen;
import net.minecraft.world.item.ItemStack;

/** Client only: opens a written book on screen without it ever being in the player's hand. */
public final class BookOpener {
    private BookOpener() {}

    public static void open(ItemStack book, int page) {
        BookViewScreen screen = new BookViewScreen(new BookViewScreen.WrittenBookAccess(book));
        Minecraft.getInstance().setScreen(screen);
        screen.setPage(page);
    }
}
