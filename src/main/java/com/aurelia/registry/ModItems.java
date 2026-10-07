package com.aurelia.registry;

import com.aurelia.AureliaMod;
import com.aurelia.item.AscendantCrownItem;
import com.aurelia.item.AurelianCrownItem;
import com.aurelia.item.LoreItem;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModItems {
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, AureliaMod.MODID);

    // ---- Blocks ----
    public static final RegistryObject<Item> WAYGATE = ITEMS.register("waygate",
            () -> new BlockItem(ModBlocks.WAYGATE.get(), new Item.Properties().rarity(Rarity.RARE)));
    public static final RegistryObject<Item> WARDEN_ALTAR = ITEMS.register("warden_altar",
            () -> new BlockItem(ModBlocks.WARDEN_ALTAR.get(), new Item.Properties().rarity(Rarity.RARE)));
    public static final RegistryObject<Item> SPORE_PLANTER = ITEMS.register("spore_planter",
            () -> new BlockItem(ModBlocks.SPORE_PLANTER.get(), new Item.Properties()));
    public static final RegistryObject<Item> STORM_PYLON = ITEMS.register("storm_pylon",
            () -> new BlockItem(ModBlocks.STORM_PYLON.get(), new Item.Properties()));
    public static final RegistryObject<Item> SOUL_SOCKET = ITEMS.register("soul_socket",
            () -> new BlockItem(ModBlocks.SOUL_SOCKET.get(), new Item.Properties()));

    // ---- Puzzle items (dropped by citadel guards, also found in chests) ----
    public static final RegistryObject<Item> SPORE_HEART = ITEMS.register("spore_heart",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.UNCOMMON), "item.aurelia.spore_heart.lore"));
    public static final RegistryObject<Item> SOUL_SIGIL = ITEMS.register("soul_sigil",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.UNCOMMON).fireResistant(), "item.aurelia.soul_sigil.lore"));


    // ---- Citadel gimmicks, ores, and realm materials ----
    public static final RegistryObject<Item> BRAMBLE_SEAL = ITEMS.register("bramble_seal",
            () -> new BlockItem(ModBlocks.BRAMBLE_SEAL.get(), new Item.Properties()));
    public static final RegistryObject<Item> STORM_SEAL = ITEMS.register("storm_seal",
            () -> new BlockItem(ModBlocks.STORM_SEAL.get(), new Item.Properties()));
    public static final RegistryObject<Item> ASH_SEAL = ITEMS.register("ash_seal",
            () -> new BlockItem(ModBlocks.ASH_SEAL.get(), new Item.Properties()));
    public static final RegistryObject<Item> SPORE_VENT = ITEMS.register("spore_vent",
            () -> new BlockItem(ModBlocks.SPORE_VENT.get(), new Item.Properties()));
    public static final RegistryObject<Item> GALE_PLATE = ITEMS.register("gale_plate",
            () -> new BlockItem(ModBlocks.GALE_PLATE.get(), new Item.Properties()));
    public static final RegistryObject<Item> EMBER_VENT = ITEMS.register("ember_vent",
            () -> new BlockItem(ModBlocks.EMBER_VENT.get(), new Item.Properties()));
    public static final RegistryObject<Item> ROOT_HEART = ITEMS.register("root_heart",
            () -> new BlockItem(ModBlocks.ROOT_HEART.get(), new Item.Properties()));
    public static final RegistryObject<Item> VERDANT_ORE = ITEMS.register("verdant_ore",
            () -> new BlockItem(ModBlocks.VERDANT_ORE.get(), new Item.Properties()));
    public static final RegistryObject<Item> STORMGLASS_ORE = ITEMS.register("stormglass_ore",
            () -> new BlockItem(ModBlocks.STORMGLASS_ORE.get(), new Item.Properties()));
    public static final RegistryObject<Item> EMBERHEART_ORE = ITEMS.register("emberheart_ore",
            () -> new BlockItem(ModBlocks.EMBERHEART_ORE.get(), new Item.Properties()));
    public static final RegistryObject<Item> VERDANT_BLOCK = ITEMS.register("verdant_block",
            () -> new BlockItem(ModBlocks.VERDANT_BLOCK.get(), new Item.Properties()));
    public static final RegistryObject<Item> STORMGLASS_BLOCK = ITEMS.register("stormglass_block",
            () -> new BlockItem(ModBlocks.STORMGLASS_BLOCK.get(), new Item.Properties()));
    public static final RegistryObject<Item> EMBERHEART_BLOCK = ITEMS.register("emberheart_block",
            () -> new BlockItem(ModBlocks.EMBERHEART_BLOCK.get(), new Item.Properties()));
    public static final RegistryObject<Item> VERDANT_SHARD = ITEMS.register("verdant_shard",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.UNCOMMON), "item.aurelia.verdant_shard.lore"));
    public static final RegistryObject<Item> STORMGLASS_SHARD = ITEMS.register("stormglass_shard",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.UNCOMMON), "item.aurelia.stormglass_shard.lore"));
    public static final RegistryObject<Item> EMBERHEART = ITEMS.register("emberheart",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.UNCOMMON), "item.aurelia.emberheart.lore"));

    // ---- Crown shards (Warden drops) ----
    public static final RegistryObject<Item> GROVE_SHARD = ITEMS.register("grove_shard",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant(), "item.aurelia.grove_shard.lore"));
    public static final RegistryObject<Item> STORM_SHARD = ITEMS.register("storm_shard",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant(), "item.aurelia.storm_shard.lore"));
    public static final RegistryObject<Item> VOID_SHARD = ITEMS.register("void_shard",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant(), "item.aurelia.void_shard.lore"));

    // ---- The reward ----
    public static final RegistryObject<Item> CROWN = ITEMS.register("crown_of_aurelia",
            () -> new AurelianCrownItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant()));

    // ---- Spawn eggs (handy for testing) ----
    public static final RegistryObject<Item> TITAN_EGG = ITEMS.register("mossback_titan_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.MOSSBACK_TITAN, 0x3A7D2C, 0xB6F26B, new Item.Properties()));
    public static final RegistryObject<Item> ROC_EGG = ITEMS.register("tempest_roc_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.TEMPEST_ROC, 0x4A6FA5, 0xE8F4FF, new Item.Properties()));
    public static final RegistryObject<Item> KING_EGG = ITEMS.register("hollow_king_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.HOLLOW_KING, 0x15101C, 0xB04CFF, new Item.Properties()));
    public static final RegistryObject<Item> ANT_EGG = ITEMS.register("grove_ant_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.GROVE_ANT, 0x8B2E1A, 0xF2C14E, new Item.Properties()));
    public static final RegistryObject<Item> SENTINEL_EGG = ITEMS.register("sky_sentinel_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.SKY_SENTINEL, 0xC9D3E0, 0x6FD2FF, new Item.Properties()));
    public static final RegistryObject<Item> SHADE_EGG = ITEMS.register("hollow_shade_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.HOLLOW_SHADE, 0x0A0A12, 0x7A5CFF, new Item.Properties()));
    public static final RegistryObject<Item> BRAMBLE_SENTINEL_EGG = ITEMS.register("bramble_sentinel_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.BRAMBLE_SENTINEL, 0x3F6B2B, 0x9BE564, new Item.Properties()));
    public static final RegistryObject<Item> SPORECAP_EGG = ITEMS.register("sporecap_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.SPORECAP, 0xC8302E, 0xEEE4CF, new Item.Properties()));
    public static final RegistryObject<Item> ROOTSTALKER_EGG = ITEMS.register("rootstalker_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.ROOTSTALKER, 0x4E5A38, 0x96FF5A, new Item.Properties()));
    public static final RegistryObject<Item> CALCITE_SENTINEL_EGG = ITEMS.register("calcite_sentinel_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.CALCITE_SENTINEL, 0xE2E4E8, 0x5AC8EB, new Item.Properties()));
    public static final RegistryObject<Item> STORM_WISP_EGG = ITEMS.register("storm_wisp_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.STORM_WISP, 0x5AE1FF, 0xE1FFFF, new Item.Properties()));
    public static final RegistryObject<Item> GALE_TALON_EGG = ITEMS.register("gale_talon_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.GALE_TALON, 0x1C2856, 0xF0F4FA, new Item.Properties()));
    public static final RegistryObject<Item> ASHBOUND_KNIGHT_EGG = ITEMS.register("ashbound_knight_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.ASHBOUND_KNIGHT, 0x2A262C, 0xFF7A1E, new Item.Properties()));
    public static final RegistryObject<Item> SOUL_JAILER_EGG = ITEMS.register("soul_jailer_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.SOUL_JAILER, 0x14181F, 0x5AE6FF, new Item.Properties()));
    public static final RegistryObject<Item> CINDER_HOUND_EGG = ITEMS.register("cinder_hound_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.CINDER_HOUND, 0x30292E, 0xFF6E1C, new Item.Properties()));

    // ==================================================================== act two
    public static final RegistryObject<Item> TIDE_BELL = ITEMS.register("tide_bell",
            () -> new BlockItem(ModBlocks.TIDE_BELL.get(), new Item.Properties().rarity(Rarity.RARE)));
    public static final RegistryObject<Item> HUSH_STONE = ITEMS.register("hush_stone",
            () -> new BlockItem(ModBlocks.HUSH_STONE.get(), new Item.Properties()));
    public static final RegistryObject<Item> SUNWELL = ITEMS.register("sunwell",
            () -> new BlockItem(ModBlocks.SUNWELL.get(), new Item.Properties().rarity(Rarity.RARE)));
    public static final RegistryObject<Item> SUN_MIRROR = ITEMS.register("sun_mirror",
            () -> new BlockItem(ModBlocks.SUN_MIRROR.get(), new Item.Properties()));
    public static final RegistryObject<Item> SUN_LENS = ITEMS.register("sun_lens",
            () -> new BlockItem(ModBlocks.SUN_LENS.get(), new Item.Properties()));
    public static final RegistryObject<Item> CORAL_SEAL = ITEMS.register("coral_seal",
            () -> new BlockItem(ModBlocks.CORAL_SEAL.get(), new Item.Properties()));
    public static final RegistryObject<Item> RIME_SEAL = ITEMS.register("rime_seal",
            () -> new BlockItem(ModBlocks.RIME_SEAL.get(), new Item.Properties()));
    public static final RegistryObject<Item> SUN_SEAL = ITEMS.register("sun_seal",
            () -> new BlockItem(ModBlocks.SUN_SEAL.get(), new Item.Properties()));
    public static final RegistryObject<Item> BRINE_GRATE = ITEMS.register("brine_grate",
            () -> new BlockItem(ModBlocks.BRINE_GRATE.get(), new Item.Properties()));
    public static final RegistryObject<Item> FROST_RUNE = ITEMS.register("frost_rune",
            () -> new BlockItem(ModBlocks.FROST_RUNE.get(), new Item.Properties()));
    public static final RegistryObject<Item> SUNFLARE_PLATE = ITEMS.register("sunflare_plate",
            () -> new BlockItem(ModBlocks.SUNFLARE_PLATE.get(), new Item.Properties()));
    public static final RegistryObject<Item> TIDESTONE_ORE = ITEMS.register("tidestone_ore",
            () -> new BlockItem(ModBlocks.TIDESTONE_ORE.get(), new Item.Properties()));
    public static final RegistryObject<Item> RIME_ORE = ITEMS.register("rime_ore",
            () -> new BlockItem(ModBlocks.RIME_ORE.get(), new Item.Properties()));
    public static final RegistryObject<Item> SUNGLASS_ORE = ITEMS.register("sunglass_ore",
            () -> new BlockItem(ModBlocks.SUNGLASS_ORE.get(), new Item.Properties()));
    public static final RegistryObject<Item> TIDESTONE_BLOCK = ITEMS.register("tidestone_block",
            () -> new BlockItem(ModBlocks.TIDESTONE_BLOCK.get(), new Item.Properties()));
    public static final RegistryObject<Item> RIME_BLOCK = ITEMS.register("rime_block",
            () -> new BlockItem(ModBlocks.RIME_BLOCK.get(), new Item.Properties()));
    public static final RegistryObject<Item> SUNGLASS_BLOCK = ITEMS.register("sunglass_block",
            () -> new BlockItem(ModBlocks.SUNGLASS_BLOCK.get(), new Item.Properties()));

    // ---- outer realm materials
    public static final RegistryObject<Item> TIDESTONE_SHARD = ITEMS.register("tidestone_shard",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.UNCOMMON), "item.aurelia.tidestone_shard.lore"));
    public static final RegistryObject<Item> RIME_CRYSTAL = ITEMS.register("rime_crystal",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.UNCOMMON), "item.aurelia.rime_crystal.lore"));
    public static final RegistryObject<Item> SUNGLASS_SHARD = ITEMS.register("sunglass_shard",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.UNCOMMON).fireResistant(), "item.aurelia.sunglass_shard.lore"));

    // ---- the outer Wardens' relics
    public static final RegistryObject<Item> LEVIATHAN_PEARL = ITEMS.register("leviathan_pearl",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant(), "item.aurelia.leviathan_pearl.lore"));
    public static final RegistryObject<Item> FROZEN_TEAR = ITEMS.register("frozen_tear",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant(), "item.aurelia.frozen_tear.lore"));
    public static final RegistryObject<Item> REAPERS_HOURGLASS = ITEMS.register("reapers_hourglass",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant(), "item.aurelia.reapers_hourglass.lore"));

    // ---- the capstone
    public static final RegistryObject<Item> ASCENDANT_CROWN = ITEMS.register("ascendant_crown",
            () -> new AscendantCrownItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant()));

    // ---- spawn eggs
    public static final RegistryObject<Item> VORATH_EGG = ITEMS.register("vorath_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.VORATH, 0x10222C, 0x46FFD6, new Item.Properties()));
    public static final RegistryObject<Item> WHITE_SILENCE_EGG = ITEMS.register("white_silence_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.WHITE_SILENCE, 0xE2E4E6, 0xAAEEFF, new Item.Properties()));
    public static final RegistryObject<Item> KHARZUL_EGG = ITEMS.register("kharzul_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.KHARZUL, 0x7A1A1E, 0xFF4A3C, new Item.Properties()));
    public static final RegistryObject<Item> PALE_MIRAGE_EGG = ITEMS.register("pale_mirage_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.PALE_MIRAGE, 0xB0B6BE, 0xE2F6FF, new Item.Properties()));
    public static final RegistryObject<Item> CORALCLAD_JUGGERNAUT_EGG = ITEMS.register("coralclad_juggernaut_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.CORALCLAD_JUGGERNAUT, 0xA87A34, 0x46FFD6, new Item.Properties()));
    public static final RegistryObject<Item> TIDECALLER_EGG = ITEMS.register("tidecaller_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.TIDECALLER, 0x1E4648, 0x5AD2FF, new Item.Properties()));
    public static final RegistryObject<Item> RAZORCLAW_EGG = ITEMS.register("razorclaw_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.RAZORCLAW, 0xE2566E, 0xCEC6B0, new Item.Properties()));
    public static final RegistryObject<Item> RIMEGUARD_EGG = ITEMS.register("rimeguard_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.RIMEGUARD, 0xC4D6E4, 0xAAEEFF, new Item.Properties()));
    public static final RegistryObject<Item> HUSHWRAITH_EGG = ITEMS.register("hushwraith_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.HUSHWRAITH, 0xB0B6BE, 0x09080B, new Item.Properties()));
    public static final RegistryObject<Item> RIMEFANG_EGG = ITEMS.register("rimefang_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.RIMEFANG, 0xD4D6D8, 0xAAEEFF, new Item.Properties()));
    public static final RegistryObject<Item> SANDGLASS_SENTINEL_EGG = ITEMS.register("sandglass_sentinel_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.SANDGLASS_SENTINEL, 0xB25628, 0xFFBA50, new Item.Properties()));
    public static final RegistryObject<Item> SUNSEER_EGG = ITEMS.register("sunseer_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.SUNSEER, 0x7A1A1E, 0xFFD65A, new Item.Properties()));
    public static final RegistryObject<Item> GLASSWING_SCARAB_EGG = ITEMS.register("glasswing_scarab_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.GLASSWING_SCARAB, 0x341E1E, 0xFF4A3C, new Item.Properties()));
}
