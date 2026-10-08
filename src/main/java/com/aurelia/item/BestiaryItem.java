package com.aurelia.item;

import com.aurelia.world.BestiaryPages;
import com.aurelia.world.Realm;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;

/**
 * The Aurelian Bestiary: every Warden and every lieutenant, their health, what they do and how to beat them. It never runs out
 * and never turns into a plain book; it opens at the section for the realm you are standing in.
 */
public class BestiaryItem extends Item {
    public BestiaryItem(Properties properties) {
        super(properties);
    }

    /** The bestiary as a written book, for the client's book screen. */
    public static ItemStack asBook() {
        ItemStack book = new ItemStack(Items.WRITTEN_BOOK);
        var tag = book.getOrCreateTag();
        tag.putString("title", "The Aurelian Bestiary");
        tag.putString("author", "The Last Archivist");
        tag.putBoolean("resolved", true);
        ListTag list = new ListTag();
        for (String page : BestiaryPages.PAGES) {
            list.add(StringTag.valueOf(Component.Serializer.toJson(Component.literal(page))));
        }
        tag.put("pages", list);
        return book;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level.isClientSide) {
            Realm realm = Realm.of(level);
            int page = realm == null ? 0 : BestiaryPages.start(realm.id);
            DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> com.aurelia.client.BookOpener.open(asBook(), page));
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.aurelia.aurelian_bestiary.lore").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
    }
}
