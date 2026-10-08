package com.aurelia.item;

import com.aurelia.world.LairBuilder;
import com.aurelia.world.Realm;
import com.aurelia.world.RealmData;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.phys.Vec3;

/**
 * The Wayfinder's Lodestar. Used in the overworld it finds the nearest citadel; inside a realm, the nearest lair whose lieutenant
 * still stands, or the Warden's altar once they are all dead. It names the direction and distance and draws a trail of light that way.
 */
public class WayfinderItem extends Item {
    public static final TagKey<Structure> CITADELS = TagKey.create(Registries.STRUCTURE, new ResourceLocation("aurelia", "citadels"));
    private static final String[] DIRS = {"east", "south-east", "south", "south-west", "west", "north-west", "north", "north-east"};

    public WayfinderItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(level instanceof ServerLevel server) || !(player instanceof ServerPlayer sp)) {
            return InteractionResultHolder.success(stack);
        }
        player.getCooldowns().addCooldown(this, 60);
        BlockPos target = null;
        String what;
        Realm realm = Realm.of(level);
        if (realm != null) {
            target = LairBuilder.nearestStanding(server, realm, player.blockPosition());
            what = "the nearest standing lair";
            if (target == null) {
                target = RealmData.get(server).center();
                what = "the Warden's altar";
            }
        } else if (level.dimension() == Level.OVERWORLD) {
            target = server.findNearestMapStructure(CITADELS, player.blockPosition(), 50, false);
            what = "the nearest citadel";
        } else {
            what = "nothing";
        }
        if (target == null) {
            sp.displayClientMessage(Component.literal("The Lodestar spins and finds nothing to point at.").withStyle(ChatFormatting.GRAY), true);
            server.playSound(null, player.blockPosition(), SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 0.8f, 0.6f);
            return InteractionResultHolder.consume(stack);
        }
        double dx = target.getX() + 0.5 - player.getX(), dz = target.getZ() + 0.5 - player.getZ();
        int dist = (int) Math.sqrt(dx * dx + dz * dz);
        int dir = (int) Math.round(Math.toDegrees(Math.atan2(dz, dx)) / 45.0) & 7;
        sp.displayClientMessage(Component.literal("The Lodestar points to " + what + ": " + DIRS[dir] + ", " + dist + " blocks")
                .withStyle(ChatFormatting.LIGHT_PURPLE), true);
        Vec3 eye = player.getEyePosition();
        Vec3 way = new Vec3(dx, 0, dz).normalize();
        for (int i = 2; i <= 18; i++) {                                       // a trail of light, seen only by its holder
            Vec3 p = eye.add(way.scale(i * 0.9)).add(0, -0.4 - i * 0.02, 0);
            com.aurelia.Perf.particles(server, sp, ParticleTypes.END_ROD, true, p.x, p.y, p.z, 1, 0.02, 0.02, 0.02, 0.0);
        }
        server.playSound(null, player.blockPosition(), SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.PLAYERS, 1.0f, 1.2f);
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.aurelia.wayfinders_lodestar.lore").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return true;
    }
}
