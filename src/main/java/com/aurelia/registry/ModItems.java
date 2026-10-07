package com.aurelia.registry;

import com.aurelia.AureliaMod;
import com.aurelia.item.AscendantCrownItem;
import com.aurelia.item.AurelianCrownItem;
import com.aurelia.item.EternalCrownItem;
import com.aurelia.item.HandOfGenesisItem;
import com.aurelia.item.RelicItem;
import com.aurelia.item.RealmArmorItem;
import com.aurelia.item.RealmArmorMaterial;
import com.aurelia.item.RealmTier;
import com.aurelia.item.RealmWeaponItem;
import com.aurelia.item.WorldsunderItem;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.AxeItem;
import net.minecraft.world.item.PickaxeItem;
import net.minecraft.world.item.ShovelItem;
import com.aurelia.entity.AureliaBoss;
import com.aurelia.world.Realm;
import javax.annotation.Nullable;
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

    // ==================================================================== act three
    public static final RegistryObject<Item> CLOCK_DIAL = ITEMS.register("clock_dial",
            () -> new BlockItem(ModBlocks.CLOCK_DIAL.get(), new Item.Properties().rarity(Rarity.RARE)));
    public static final RegistryObject<Item> MASTER_CLOCK = ITEMS.register("master_clock",
            () -> new BlockItem(ModBlocks.MASTER_CLOCK.get(), new Item.Properties().rarity(Rarity.RARE)));
    public static final RegistryObject<Item> SPORE_VALVE = ITEMS.register("spore_valve",
            () -> new BlockItem(ModBlocks.SPORE_VALVE.get(), new Item.Properties().rarity(Rarity.RARE)));
    public static final RegistryObject<Item> PARADOX_SEAL = ITEMS.register("paradox_seal",
            () -> new BlockItem(ModBlocks.PARADOX_SEAL.get(), new Item.Properties()));
    public static final RegistryObject<Item> ROOT_SEAL = ITEMS.register("root_seal",
            () -> new BlockItem(ModBlocks.ROOT_SEAL.get(), new Item.Properties()));
    public static final RegistryObject<Item> TIME_SNARE = ITEMS.register("time_snare",
            () -> new BlockItem(ModBlocks.TIME_SNARE.get(), new Item.Properties()));
    public static final RegistryObject<Item> ROOT_SNARE = ITEMS.register("root_snare",
            () -> new BlockItem(ModBlocks.ROOT_SNARE.get(), new Item.Properties()));
    public static final RegistryObject<Item> CHRONITE_BLOCK = ITEMS.register("chronite_block",
            () -> new BlockItem(ModBlocks.CHRONITE_BLOCK.get(), new Item.Properties()));
    public static final RegistryObject<Item> BLOOMSPORE_BLOCK = ITEMS.register("bloomspore_block",
            () -> new BlockItem(ModBlocks.BLOOMSPORE_BLOCK.get(), new Item.Properties()));
    public static final RegistryObject<Item> CHRONITE_SHARD = ITEMS.register("chronite_shard",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.UNCOMMON), "item.aurelia.chronite_shard.lore"));
    public static final RegistryObject<Item> BLOOMSPORE = ITEMS.register("bloomspore",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.UNCOMMON), "item.aurelia.bloomspore.lore"));
    public static final RegistryObject<Item> HOUR_CORE = ITEMS.register("hour_core",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant(), "item.aurelia.hour_core.lore"));
    public static final RegistryObject<Item> BLOOM_HEART = ITEMS.register("bloom_heart",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant(), "item.aurelia.bloom_heart.lore"));
    public static final RegistryObject<Item> ETERNAL_CROWN = ITEMS.register("eternal_crown",
            () -> new EternalCrownItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> VEXOR_EGG = ITEMS.register("vexor_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.VEXOR, 0x221F28, 0xA846FF, new Item.Properties()));
    public static final RegistryObject<Item> BLOOM_MOTHER_EGG = ITEMS.register("bloom_mother_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.BLOOM_MOTHER, 0xDED2BA, 0xFF46DC, new Item.Properties()));
    public static final RegistryObject<Item> GEARSKITTER_EGG = ITEMS.register("gearskitter_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.GEARSKITTER, 0xB28436, 0x221F28, new Item.Properties()));
    public static final RegistryObject<Item> SECONDHAND_EGG = ITEMS.register("secondhand_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.SECONDHAND, 0xA846FF, 0xFFCE5A, new Item.Properties()));
    public static final RegistryObject<Item> HOUR_WARDEN_EGG = ITEMS.register("hour_warden_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.HOUR_WARDEN, 0x221F28, 0xB28436, new Item.Properties()));
    public static final RegistryObject<Item> ROOT_GRUB_EGG = ITEMS.register("root_grub_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.ROOT_GRUB, 0xDED2BA, 0x96289F, new Item.Properties()));
    public static final RegistryObject<Item> SPORE_DRIFTER_EGG = ITEMS.register("spore_drifter_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.SPORE_DRIFTER, 0x96289F, 0xFF46DC, new Item.Properties()));
    public static final RegistryObject<Item> HUSK_GUARD_EGG = ITEMS.register("husk_guard_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.HUSK_GUARD, 0xE0D8C6, 0x6E2A78, new Item.Properties()));

    // ==================================================================== the finale
    public static final RegistryObject<Item> ROOTBOUND_HEART = ITEMS.register("rootbound_heart",
            () -> new RelicItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant(), "item.aurelia.rootbound_heart.lore"));
    public static final RegistryObject<Item> STORM_TALON = ITEMS.register("storm_talon",
            () -> new RelicItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant(), "item.aurelia.storm_talon.lore"));
    public static final RegistryObject<Item> SOVEREIGN_HAND = ITEMS.register("sovereign_hand",
            () -> new RelicItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant(), "item.aurelia.sovereign_hand.lore"));
    public static final RegistryObject<Item> ABYSSAL_FANG = ITEMS.register("abyssal_fang",
            () -> new RelicItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant(), "item.aurelia.abyssal_fang.lore"));
    public static final RegistryObject<Item> FROZEN_VOICE = ITEMS.register("frozen_voice",
            () -> new RelicItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant(), "item.aurelia.frozen_voice.lore"));
    public static final RegistryObject<Item> GLASS_STINGER = ITEMS.register("glass_stinger",
            () -> new RelicItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant(), "item.aurelia.glass_stinger.lore"));
    public static final RegistryObject<Item> CHRONAL_EYE = ITEMS.register("chronal_eye",
            () -> new RelicItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant(), "item.aurelia.chronal_eye.lore"));
    public static final RegistryObject<Item> LIVING_SPORE = ITEMS.register("living_spore",
            () -> new RelicItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant(), "item.aurelia.living_spore.lore"));
    public static final RegistryObject<Item> HAND_OF_GENESIS = ITEMS.register("hand_of_genesis",
            () -> new HandOfGenesisItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> RELIC_PEDESTAL = ITEMS.register("relic_pedestal",
            () -> new BlockItem(ModBlocks.RELIC_PEDESTAL.get(), new Item.Properties().rarity(Rarity.RARE)));
    public static final RegistryObject<Item> REALM_NODE = ITEMS.register("realm_node",
            () -> new BlockItem(ModBlocks.REALM_NODE.get(), new Item.Properties().rarity(Rarity.RARE)));
    public static final RegistryObject<Item> UNMAKING_ANCHOR = ITEMS.register("unmaking_anchor",
            () -> new BlockItem(ModBlocks.UNMAKING_ANCHOR.get(), new Item.Properties()));
    public static final RegistryObject<Item> UNMAKER_EGG = ITEMS.register("unmaker_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.UNMAKER, 0xE2DAC8, 0x1C1A22, new Item.Properties()));

    // ---- the Unmaker's arsenal: Fractured Genesis (its drop), Genesis Ingots, Genesis armor, Worldsunder and the Genesis tools
    public static final RegistryObject<Item> FRACTURED_GENESIS = ITEMS.register("fractured_genesis",
            () -> new LoreItem(new Item.Properties().stacksTo(16).rarity(Rarity.EPIC).fireResistant(), "item.aurelia.fractured_genesis.lore"));
    public static final RegistryObject<Item> GENESIS_INGOT = ITEMS.register("genesis_ingot",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant(), "item.aurelia.genesis_ingot.lore"));
    public static final RegistryObject<Item> GENESIS_HELMET = ITEMS.register("genesis_helmet",
            () -> new RealmArmorItem(RealmArmorMaterial.GENESIS, ArmorItem.Type.HELMET, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> GENESIS_CHESTPLATE = ITEMS.register("genesis_chestplate",
            () -> new RealmArmorItem(RealmArmorMaterial.GENESIS, ArmorItem.Type.CHESTPLATE, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> GENESIS_LEGGINGS = ITEMS.register("genesis_leggings",
            () -> new RealmArmorItem(RealmArmorMaterial.GENESIS, ArmorItem.Type.LEGGINGS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> GENESIS_BOOTS = ITEMS.register("genesis_boots",
            () -> new RealmArmorItem(RealmArmorMaterial.GENESIS, ArmorItem.Type.BOOTS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> WORLDSUNDER = ITEMS.register("worldsunder",
            () -> new WorldsunderItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> GENESIS_PICKAXE = ITEMS.register("genesis_pickaxe",
            () -> new PickaxeItem(RealmTier.GENESIS, 1, -2.8f, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> GENESIS_AXE = ITEMS.register("genesis_axe",
            () -> new AxeItem(RealmTier.GENESIS, 5.0f, -3.0f, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> GENESIS_SHOVEL = ITEMS.register("genesis_shovel",
            () -> new ShovelItem(RealmTier.GENESIS, 1.5f, -3.0f, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));

    /** The relic each realm's Warden leaves behind, in realm order. */
    @Nullable
    public static Item relicFor(Realm realm) {
        return switch (realm) {
            case GROVE -> ROOTBOUND_HEART.get();
            case SKYREACH -> STORM_TALON.get();
            case HOLLOW -> SOVEREIGN_HAND.get();
            case DROWNED -> ABYSSAL_FANG.get();
            case PALE -> FROZEN_VOICE.get();
            case SCARLET -> GLASS_STINGER.get();
            case CLOCKWORK -> CHRONAL_EYE.get();
            case MYCELIAL -> LIVING_SPORE.get();
            default -> null;
        };
    }

    /** The relic a Warden drops on death, or null (the Unmaker drops none). */
    @Nullable
    public static Item relicOf(AureliaBoss boss) {
        if (boss instanceof com.aurelia.entity.MossbackTitan) {
            return ROOTBOUND_HEART.get();
        }
        if (boss instanceof com.aurelia.entity.TempestRoc) {
            return STORM_TALON.get();
        }
        if (boss instanceof com.aurelia.entity.HollowKing) {
            return SOVEREIGN_HAND.get();
        }
        if (boss instanceof com.aurelia.entity.Vorath) {
            return ABYSSAL_FANG.get();
        }
        if (boss instanceof com.aurelia.entity.WhiteSilence) {
            return FROZEN_VOICE.get();
        }
        if (boss instanceof com.aurelia.entity.Kharzul) {
            return GLASS_STINGER.get();
        }
        if (boss instanceof com.aurelia.entity.Vexor) {
            return CHRONAL_EYE.get();
        }
        if (boss instanceof com.aurelia.entity.BloomMother) {
            return LIVING_SPORE.get();
        }
        return null;
    }

    // ==================================================================== realm kits: armor, weapons, food, wildlife
    public static final RegistryObject<Item> VERDANT_HELMET = ITEMS.register("verdant_helmet",
            () -> new RealmArmorItem(RealmArmorMaterial.VERDANT, ArmorItem.Type.HELMET, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> VERDANT_CHESTPLATE = ITEMS.register("verdant_chestplate",
            () -> new RealmArmorItem(RealmArmorMaterial.VERDANT, ArmorItem.Type.CHESTPLATE, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> VERDANT_LEGGINGS = ITEMS.register("verdant_leggings",
            () -> new RealmArmorItem(RealmArmorMaterial.VERDANT, ArmorItem.Type.LEGGINGS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> VERDANT_BOOTS = ITEMS.register("verdant_boots",
            () -> new RealmArmorItem(RealmArmorMaterial.VERDANT, ArmorItem.Type.BOOTS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> ROOTBREAKER = ITEMS.register("rootbreaker",
            () -> new RealmWeaponItem(RealmTier.VERDANT, 7, -3.1f, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> VERDANT_FIG = ITEMS.register("verdant_fig",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder().nutrition(6).saturationMod(0.6f).effect(() -> new MobEffectInstance(MobEffects.REGENERATION, 100, 0), 1.0f).alwaysEat().build())));
    public static final RegistryObject<Item> MOSSLING_EGG = ITEMS.register("mossling_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.MOSSLING, 0x4A6830, 0xE6D25A, new Item.Properties()));
    public static final RegistryObject<Item> STORMGLASS_HELMET = ITEMS.register("stormglass_helmet",
            () -> new RealmArmorItem(RealmArmorMaterial.STORMGLASS, ArmorItem.Type.HELMET, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> STORMGLASS_CHESTPLATE = ITEMS.register("stormglass_chestplate",
            () -> new RealmArmorItem(RealmArmorMaterial.STORMGLASS, ArmorItem.Type.CHESTPLATE, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> STORMGLASS_LEGGINGS = ITEMS.register("stormglass_leggings",
            () -> new RealmArmorItem(RealmArmorMaterial.STORMGLASS, ArmorItem.Type.LEGGINGS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> STORMGLASS_BOOTS = ITEMS.register("stormglass_boots",
            () -> new RealmArmorItem(RealmArmorMaterial.STORMGLASS, ArmorItem.Type.BOOTS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> STORMPIERCER = ITEMS.register("stormpiercer",
            () -> new RealmWeaponItem(RealmTier.STORMGLASS, 5, -2.6f, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> SKY_JELLY = ITEMS.register("sky_jelly",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder().nutrition(4).saturationMod(0.5f).effect(() -> new MobEffectInstance(MobEffects.SLOW_FALLING, 300, 0), 1.0f).alwaysEat().build())));
    public static final RegistryObject<Item> CLOUD_RAY_EGG = ITEMS.register("cloud_ray_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.CLOUD_RAY, 0xCEE2F0, 0x5AB4E6, new Item.Properties()));
    public static final RegistryObject<Item> EMBERHEART_HELMET = ITEMS.register("emberheart_helmet",
            () -> new RealmArmorItem(RealmArmorMaterial.EMBERHEART, ArmorItem.Type.HELMET, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> EMBERHEART_CHESTPLATE = ITEMS.register("emberheart_chestplate",
            () -> new RealmArmorItem(RealmArmorMaterial.EMBERHEART, ArmorItem.Type.CHESTPLATE, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> EMBERHEART_LEGGINGS = ITEMS.register("emberheart_leggings",
            () -> new RealmArmorItem(RealmArmorMaterial.EMBERHEART, ArmorItem.Type.LEGGINGS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> EMBERHEART_BOOTS = ITEMS.register("emberheart_boots",
            () -> new RealmArmorItem(RealmArmorMaterial.EMBERHEART, ArmorItem.Type.BOOTS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> SOULCLEAVER = ITEMS.register("soulcleaver",
            () -> new RealmWeaponItem(RealmTier.EMBERHEART, 7, -3.0f, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> CHARRED_MORSEL = ITEMS.register("charred_morsel",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder().nutrition(6).saturationMod(0.7f).effect(() -> new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 600, 0), 1.0f).alwaysEat().build())));
    public static final RegistryObject<Item> EMBER_BEETLE_EGG = ITEMS.register("ember_beetle_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.EMBER_BEETLE, 0x181416, 0xFF8C28, new Item.Properties()));
    public static final RegistryObject<Item> TIDESTONE_HELMET = ITEMS.register("tidestone_helmet",
            () -> new RealmArmorItem(RealmArmorMaterial.TIDESTONE, ArmorItem.Type.HELMET, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> TIDESTONE_CHESTPLATE = ITEMS.register("tidestone_chestplate",
            () -> new RealmArmorItem(RealmArmorMaterial.TIDESTONE, ArmorItem.Type.CHESTPLATE, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> TIDESTONE_LEGGINGS = ITEMS.register("tidestone_leggings",
            () -> new RealmArmorItem(RealmArmorMaterial.TIDESTONE, ArmorItem.Type.LEGGINGS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> TIDESTONE_BOOTS = ITEMS.register("tidestone_boots",
            () -> new RealmArmorItem(RealmArmorMaterial.TIDESTONE, ArmorItem.Type.BOOTS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> TIDEBINDER = ITEMS.register("tidebinder",
            () -> new RealmWeaponItem(RealmTier.TIDESTONE, 6, -2.8f, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> GLOWING_GEL = ITEMS.register("glowing_gel",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder().nutrition(4).saturationMod(0.5f).effect(() -> new MobEffectInstance(MobEffects.WATER_BREATHING, 600, 0), 1.0f).effect(() -> new MobEffectInstance(MobEffects.NIGHT_VISION, 600, 0), 1.0f).alwaysEat().build())));
    public static final RegistryObject<Item> LANTERN_JELLY_EGG = ITEMS.register("lantern_jelly_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.LANTERN_JELLY, 0x5AD2C8, 0xDCFFFA, new Item.Properties()));
    public static final RegistryObject<Item> RIME_HELMET = ITEMS.register("rime_helmet",
            () -> new RealmArmorItem(RealmArmorMaterial.RIME, ArmorItem.Type.HELMET, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> RIME_CHESTPLATE = ITEMS.register("rime_chestplate",
            () -> new RealmArmorItem(RealmArmorMaterial.RIME, ArmorItem.Type.CHESTPLATE, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> RIME_LEGGINGS = ITEMS.register("rime_leggings",
            () -> new RealmArmorItem(RealmArmorMaterial.RIME, ArmorItem.Type.LEGGINGS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> RIME_BOOTS = ITEMS.register("rime_boots",
            () -> new RealmArmorItem(RealmArmorMaterial.RIME, ArmorItem.Type.BOOTS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> SILENT_REQUIEM = ITEMS.register("silent_requiem",
            () -> new RealmWeaponItem(RealmTier.RIME, 7, -3.0f, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> FROST_HARE_HAUNCH = ITEMS.register("frost_hare_haunch",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder().nutrition(8).saturationMod(0.9f).build())));
    public static final RegistryObject<Item> FROST_HARE_EGG = ITEMS.register("frost_hare_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.FROST_HARE, 0xEEF2F6, 0xDCAAB4, new Item.Properties()));
    public static final RegistryObject<Item> SUNGLASS_HELMET = ITEMS.register("sunglass_helmet",
            () -> new RealmArmorItem(RealmArmorMaterial.SUNGLASS, ArmorItem.Type.HELMET, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> SUNGLASS_CHESTPLATE = ITEMS.register("sunglass_chestplate",
            () -> new RealmArmorItem(RealmArmorMaterial.SUNGLASS, ArmorItem.Type.CHESTPLATE, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> SUNGLASS_LEGGINGS = ITEMS.register("sunglass_leggings",
            () -> new RealmArmorItem(RealmArmorMaterial.SUNGLASS, ArmorItem.Type.LEGGINGS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> SUNGLASS_BOOTS = ITEMS.register("sunglass_boots",
            () -> new RealmArmorItem(RealmArmorMaterial.SUNGLASS, ArmorItem.Type.BOOTS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> VENOMFANGS = ITEMS.register("venomfangs",
            () -> new RealmWeaponItem(RealmTier.SUNGLASS, 3, -1.6f, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> SUNBAKED_TAIL = ITEMS.register("sunbaked_tail",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder().nutrition(5).saturationMod(0.6f).effect(() -> new MobEffectInstance(MobEffects.DIG_SPEED, 400, 0), 1.0f).alwaysEat().build())));
    public static final RegistryObject<Item> SAND_SKINK_EGG = ITEMS.register("sand_skink_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.SAND_SKINK, 0xC44628, 0xF0BE78, new Item.Properties()));
    public static final RegistryObject<Item> CHRONITE_HELMET = ITEMS.register("chronite_helmet",
            () -> new RealmArmorItem(RealmArmorMaterial.CHRONITE, ArmorItem.Type.HELMET, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> CHRONITE_CHESTPLATE = ITEMS.register("chronite_chestplate",
            () -> new RealmArmorItem(RealmArmorMaterial.CHRONITE, ArmorItem.Type.CHESTPLATE, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> CHRONITE_LEGGINGS = ITEMS.register("chronite_leggings",
            () -> new RealmArmorItem(RealmArmorMaterial.CHRONITE, ArmorItem.Type.LEGGINGS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> CHRONITE_BOOTS = ITEMS.register("chronite_boots",
            () -> new RealmArmorItem(RealmArmorMaterial.CHRONITE, ArmorItem.Type.BOOTS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> HOURSHATTER = ITEMS.register("hourshatter",
            () -> new RealmWeaponItem(RealmTier.CHRONITE, 4, -2.4f, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> TICKBERRY = ITEMS.register("tickberry",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder().nutrition(3).saturationMod(0.4f).effect(() -> new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 400, 0), 1.0f).alwaysEat().build())));
    public static final RegistryObject<Item> COGLING_EGG = ITEMS.register("cogling_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.COGLING, 0xC49646, 0xAA46FF, new Item.Properties()));
    public static final RegistryObject<Item> BLOOMSPORE_HELMET = ITEMS.register("bloomspore_helmet",
            () -> new RealmArmorItem(RealmArmorMaterial.BLOOMSPORE, ArmorItem.Type.HELMET, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> BLOOMSPORE_CHESTPLATE = ITEMS.register("bloomspore_chestplate",
            () -> new RealmArmorItem(RealmArmorMaterial.BLOOMSPORE, ArmorItem.Type.CHESTPLATE, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> BLOOMSPORE_LEGGINGS = ITEMS.register("bloomspore_leggings",
            () -> new RealmArmorItem(RealmArmorMaterial.BLOOMSPORE, ArmorItem.Type.LEGGINGS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> BLOOMSPORE_BOOTS = ITEMS.register("bloomspore_boots",
            () -> new RealmArmorItem(RealmArmorMaterial.BLOOMSPORE, ArmorItem.Type.BOOTS, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> SPORETHORN = ITEMS.register("sporethorn",
            () -> new RealmWeaponItem(RealmTier.BLOOMSPORE, 5, -2.8f, new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> PUFFCAP = ITEMS.register("puffcap",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder().nutrition(6).saturationMod(0.8f).effect(() -> new MobEffectInstance(MobEffects.SATURATION, 1, 0), 1.0f).effect(() -> new MobEffectInstance(MobEffects.REGENERATION, 100, 0), 1.0f).alwaysEat().build())));
    public static final RegistryObject<Item> SPORE_PUFF_EGG = ITEMS.register("spore_puff_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.SPORE_PUFF, 0xC846BE, 0xFFDCFA, new Item.Properties()));
    // ==================================================================== the arsenals: each realm's tools and materials
    public static final RegistryObject<Item> VERDANTITE_INGOT = ITEMS.register("verdantite_ingot",
            () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON)));
    public static final RegistryObject<Item> LIVING_ROOT_FIBER = ITEMS.register("living_root_fiber",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.RARE), "item.aurelia.living_root_fiber.lore"));
    public static final RegistryObject<Item> VERDANTITE_PICKAXE = ITEMS.register("verdantite_pickaxe",
            () -> new PickaxeItem(RealmTier.VERDANT, 1, -2.8f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> VERDANTITE_AXE = ITEMS.register("verdantite_axe",
            () -> new AxeItem(RealmTier.VERDANT, 5.0f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> VERDANTITE_SHOVEL = ITEMS.register("verdantite_shovel",
            () -> new ShovelItem(RealmTier.VERDANT, 1.5f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> AETHERIUM_INGOT = ITEMS.register("aetherium_ingot",
            () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON)));
    public static final RegistryObject<Item> AETHERIUM_PICKAXE = ITEMS.register("aetherium_pickaxe",
            () -> new PickaxeItem(RealmTier.STORMGLASS, 1, -2.8f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> AETHERIUM_AXE = ITEMS.register("aetherium_axe",
            () -> new AxeItem(RealmTier.STORMGLASS, 5.0f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> AETHERIUM_SHOVEL = ITEMS.register("aetherium_shovel",
            () -> new ShovelItem(RealmTier.STORMGLASS, 1.5f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> SOULSTEEL_INGOT = ITEMS.register("soulsteel_ingot",
            () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON)));
    public static final RegistryObject<Item> CAGED_SOUL_EMBER = ITEMS.register("caged_soul_ember",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.RARE), "item.aurelia.caged_soul_ember.lore"));
    public static final RegistryObject<Item> SOULSTEEL_PICKAXE = ITEMS.register("soulsteel_pickaxe",
            () -> new PickaxeItem(RealmTier.EMBERHEART, 1, -2.8f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> SOULSTEEL_AXE = ITEMS.register("soulsteel_axe",
            () -> new AxeItem(RealmTier.EMBERHEART, 5.0f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> SOULSTEEL_SHOVEL = ITEMS.register("soulsteel_shovel",
            () -> new ShovelItem(RealmTier.EMBERHEART, 1.5f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> TIDESTEEL_INGOT = ITEMS.register("tidesteel_ingot",
            () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON)));
    public static final RegistryObject<Item> TIDESTEEL_PICKAXE = ITEMS.register("tidesteel_pickaxe",
            () -> new PickaxeItem(RealmTier.TIDESTONE, 1, -2.8f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> TIDESTEEL_AXE = ITEMS.register("tidesteel_axe",
            () -> new AxeItem(RealmTier.TIDESTONE, 5.0f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> TIDESTEEL_SHOVEL = ITEMS.register("tidesteel_shovel",
            () -> new ShovelItem(RealmTier.TIDESTONE, 1.5f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> FROZEN_BLACK_FLAME_CORE = ITEMS.register("frozen_black_flame_core",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.RARE), "item.aurelia.frozen_black_flame_core.lore"));
    public static final RegistryObject<Item> RIMECRYSTAL_PICKAXE = ITEMS.register("rimecrystal_pickaxe",
            () -> new PickaxeItem(RealmTier.RIME, 1, -2.8f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> RIMECRYSTAL_AXE = ITEMS.register("rimecrystal_axe",
            () -> new AxeItem(RealmTier.RIME, 5.0f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> RIMECRYSTAL_SHOVEL = ITEMS.register("rimecrystal_shovel",
            () -> new ShovelItem(RealmTier.RIME, 1.5f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> AMBER_VENOM_VIAL = ITEMS.register("amber_venom_vial",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.RARE), "item.aurelia.amber_venom_vial.lore"));
    public static final RegistryObject<Item> SCARLET_PICKAXE = ITEMS.register("scarlet_pickaxe",
            () -> new PickaxeItem(RealmTier.SUNGLASS, 1, -2.8f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> SCARLET_AXE = ITEMS.register("scarlet_axe",
            () -> new AxeItem(RealmTier.SUNGLASS, 5.0f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> SCARLET_SHOVEL = ITEMS.register("scarlet_shovel",
            () -> new ShovelItem(RealmTier.SUNGLASS, 1.5f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> CHRONITE_INGOT = ITEMS.register("chronite_ingot",
            () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON)));
    public static final RegistryObject<Item> TEMPORAL_CORE = ITEMS.register("temporal_core",
            () -> new LoreItem(new Item.Properties().rarity(Rarity.RARE), "item.aurelia.temporal_core.lore"));
    public static final RegistryObject<Item> CHRONITE_PICKAXE = ITEMS.register("chronite_pickaxe",
            () -> new PickaxeItem(RealmTier.CHRONITE, 1, -2.8f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> CHRONITE_AXE = ITEMS.register("chronite_axe",
            () -> new AxeItem(RealmTier.CHRONITE, 5.0f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> CHRONITE_SHOVEL = ITEMS.register("chronite_shovel",
            () -> new ShovelItem(RealmTier.CHRONITE, 1.5f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> MYCELIAL_INGOT = ITEMS.register("mycelial_ingot",
            () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON)));
    public static final RegistryObject<Item> MYCELIAL_PICKAXE = ITEMS.register("mycelial_pickaxe",
            () -> new PickaxeItem(RealmTier.BLOOMSPORE, 1, -2.8f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> MYCELIAL_AXE = ITEMS.register("mycelial_axe",
            () -> new AxeItem(RealmTier.BLOOMSPORE, 5.0f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    public static final RegistryObject<Item> MYCELIAL_SHOVEL = ITEMS.register("mycelial_shovel",
            () -> new ShovelItem(RealmTier.BLOOMSPORE, 1.5f, -3.0f, new Item.Properties().rarity(Rarity.RARE).fireResistant()));

    public static final RegistryObject<Item> CHRONITE_ORE = ITEMS.register("chronite_ore",
            () -> new BlockItem(ModBlocks.CHRONITE_ORE.get(), new Item.Properties()));
    public static final RegistryObject<Item> BLOOMSPORE_ORE = ITEMS.register("bloomspore_ore",
            () -> new BlockItem(ModBlocks.BLOOMSPORE_ORE.get(), new Item.Properties()));

    /** What each realm creature eats, follows and breeds on. */
    public static Item critterFood(net.minecraft.world.entity.EntityType<?> type) {
        if (type == ModEntities.MOSSLING.get()) {
            return VERDANT_FIG.get();
        }
        if (type == ModEntities.CLOUD_RAY.get()) {
            return SKY_JELLY.get();
        }
        if (type == ModEntities.EMBER_BEETLE.get()) {
            return CHARRED_MORSEL.get();
        }
        if (type == ModEntities.LANTERN_JELLY.get()) {
            return GLOWING_GEL.get();
        }
        if (type == ModEntities.FROST_HARE.get()) {
            return FROST_HARE_HAUNCH.get();
        }
        if (type == ModEntities.SAND_SKINK.get()) {
            return SUNBAKED_TAIL.get();
        }
        if (type == ModEntities.COGLING.get()) {
            return TICKBERRY.get();
        }
        if (type == ModEntities.SPORE_PUFF.get()) {
            return PUFFCAP.get();
        }
        return net.minecraft.world.item.Items.WHEAT;
    }
}
