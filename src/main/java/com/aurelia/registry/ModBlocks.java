package com.aurelia.registry;

import com.aurelia.AureliaMod;
import com.aurelia.block.AltarBlock;
import com.aurelia.block.ClockDialBlock;
import com.aurelia.block.MasterClockBlock;
import com.aurelia.block.SporeValveBlock;
import com.aurelia.block.PuzzleNodeBlock;
import com.aurelia.block.RealmNodeBlock;
import com.aurelia.block.RelicPedestalBlock;
import com.aurelia.block.SealBlock;
import com.aurelia.block.SunMirrorBlock;
import com.aurelia.block.SunwellBlock;
import com.aurelia.block.TideBellBlock;
import com.aurelia.block.TrapBlock;
import com.aurelia.block.WaygateBlock;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.DropExperienceBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/** Puzzle blocks are unbreakable in survival so nobody can soft-lock a citadel. Creative mode can still remove them. */
public class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS =
            DeferredRegister.create(ForgeRegistries.BLOCKS, AureliaMod.MODID);

    public static final RegistryObject<Block> WAYGATE = BLOCKS.register("waygate",
            () -> new WaygateBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.GOLD)
                    .strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> state.getValue(WaygateBlock.ACTIVE) ? 15 : 4)
                    .sound(SoundType.AMETHYST)));

    public static final RegistryObject<Block> WARDEN_ALTAR = BLOCKS.register("warden_altar",
            () -> new AltarBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_PURPLE)
                    .strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> 8)
                    .sound(SoundType.STONE)));

    public static final RegistryObject<Block> SPORE_PLANTER = BLOCKS.register("spore_planter",
            () -> new PuzzleNodeBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.PLANT)
                    .strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> state.getValue(PuzzleNodeBlock.FILLED) ? 12 : 0)
                    .sound(SoundType.MOSS),
                    PuzzleNodeBlock.Kind.PLANTER, () -> ModItems.SPORE_HEART.get()));

    public static final RegistryObject<Block> STORM_PYLON = BLOCKS.register("storm_pylon",
            () -> new PuzzleNodeBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_LIGHT_BLUE)
                    .strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> state.getValue(PuzzleNodeBlock.FILLED) ? 15 : 2)
                    .sound(SoundType.COPPER),
                    PuzzleNodeBlock.Kind.PYLON, () -> null));

    public static final RegistryObject<Block> SOUL_SOCKET = BLOCKS.register("soul_socket",
            () -> new PuzzleNodeBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_BLACK)
                    .strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> state.getValue(PuzzleNodeBlock.FILLED) ? 10 : 0)
                    .sound(SoundType.DEEPSLATE),
                    PuzzleNodeBlock.Kind.SOCKET, () -> ModItems.SOUL_SIGIL.get()));

    // ---- Citadel gimmicks: sealed doors and floor traps ----
    public static final RegistryObject<Block> BRAMBLE_SEAL = BLOCKS.register("bramble_seal",
            () -> new SealBlock(BlockBehaviour.Properties.of().mapColor(MapColor.PLANT).strength(-1.0f, 3600000.0f).noLootTable()
                    .sound(SoundType.WOOD), () -> ModEntities.BRAMBLE_SENTINEL.get(), "Bramble Sentinel"));
    public static final RegistryObject<Block> STORM_SEAL = BLOCKS.register("storm_seal",
            () -> new SealBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_LIGHT_BLUE).strength(-1.0f, 3600000.0f).noLootTable()
                    .lightLevel(state -> 8).sound(SoundType.GLASS), () -> ModEntities.CALCITE_SENTINEL.get(), "Calcite Sentinel"));
    public static final RegistryObject<Block> ASH_SEAL = BLOCKS.register("ash_seal",
            () -> new SealBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(-1.0f, 3600000.0f).noLootTable()
                    .lightLevel(state -> 6).sound(SoundType.DEEPSLATE), () -> ModEntities.ASHBOUND_KNIGHT.get(), "Ashbound Knight"));

    public static final RegistryObject<Block> SPORE_VENT = BLOCKS.register("spore_vent",
            () -> new TrapBlock(BlockBehaviour.Properties.of().mapColor(MapColor.PLANT).strength(3.0f).sound(SoundType.MOSS), TrapBlock.Kind.SPORE));
    public static final RegistryObject<Block> GALE_PLATE = BLOCKS.register("gale_plate",
            () -> new TrapBlock(BlockBehaviour.Properties.of().mapColor(MapColor.QUARTZ).strength(3.0f).lightLevel(state -> 7)
                    .sound(SoundType.COPPER), TrapBlock.Kind.GALE));
    public static final RegistryObject<Block> EMBER_VENT = BLOCKS.register("ember_vent",
            () -> new TrapBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(3.0f).lightLevel(state -> 9)
                    .sound(SoundType.DEEPSLATE), TrapBlock.Kind.EMBER));

    // ---- Mossback's gimmick ----
    public static final RegistryObject<Block> ROOT_HEART = BLOCKS.register("root_heart",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.PLANT).strength(2.0f).noLootTable()
                    .lightLevel(state -> 12).sound(SoundType.ROOTS)));

    // ---- Realm ores and their storage blocks ----
    public static final RegistryObject<Block> VERDANT_ORE = BLOCKS.register("verdant_ore",
            () -> new DropExperienceBlock(BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(3.0f, 3.0f)
                    .requiresCorrectToolForDrops().sound(SoundType.STONE), UniformInt.of(2, 5)));
    public static final RegistryObject<Block> STORMGLASS_ORE = BLOCKS.register("stormglass_ore",
            () -> new DropExperienceBlock(BlockBehaviour.Properties.of().mapColor(MapColor.QUARTZ).strength(3.0f, 3.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 4).sound(SoundType.CALCITE), UniformInt.of(2, 5)));
    public static final RegistryObject<Block> EMBERHEART_ORE = BLOCKS.register("emberheart_ore",
            () -> new DropExperienceBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(3.5f, 4.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 6).sound(SoundType.DEEPSLATE), UniformInt.of(3, 6)));
    public static final RegistryObject<Block> VERDANT_BLOCK = BLOCKS.register("verdant_block",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.EMERALD).strength(5.0f, 6.0f)
                    .requiresCorrectToolForDrops().sound(SoundType.AMETHYST)));
    public static final RegistryObject<Block> STORMGLASS_BLOCK = BLOCKS.register("stormglass_block",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_LIGHT_BLUE).strength(5.0f, 6.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 10).sound(SoundType.AMETHYST)));
    public static final RegistryObject<Block> EMBERHEART_BLOCK = BLOCKS.register("emberheart_block",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_ORANGE).strength(5.0f, 6.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 12).sound(SoundType.AMETHYST)));

    // ==================================================================== act two
    // ---- citadel rituals
    public static final RegistryObject<Block> TIDE_BELL = BLOCKS.register("tide_bell",
            () -> new TideBellBlock(BlockBehaviour.Properties.of().mapColor(MapColor.GOLD).strength(-1.0f, 3600000.0f)
                    .noOcclusion().lightLevel(state -> state.getValue(TideBellBlock.RUNG) ? 12 : 4).sound(SoundType.ANVIL)));
    public static final RegistryObject<Block> HUSH_STONE = BLOCKS.register("hush_stone",
            () -> new PuzzleNodeBlock(BlockBehaviour.Properties.of().mapColor(MapColor.SNOW).strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> state.getValue(PuzzleNodeBlock.FILLED) ? 12 : 2).sound(SoundType.CALCITE),
                    PuzzleNodeBlock.Kind.HUSH, () -> null));
    public static final RegistryObject<Block> SUNWELL = BLOCKS.register("sunwell",
            () -> new SunwellBlock(BlockBehaviour.Properties.of().mapColor(MapColor.GOLD).strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> 13).sound(SoundType.METAL)));
    public static final RegistryObject<Block> SUN_MIRROR = BLOCKS.register("sun_mirror",
            () -> new SunMirrorBlock(BlockBehaviour.Properties.of().mapColor(MapColor.GOLD).strength(-1.0f, 3600000.0f)
                    .noOcclusion().sound(SoundType.GLASS)));
    public static final RegistryObject<Block> SUN_LENS = BLOCKS.register("sun_lens",
            () -> new PuzzleNodeBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_RED).strength(-1.0f, 3600000.0f)
                    .noOcclusion().lightLevel(state -> state.getValue(PuzzleNodeBlock.FILLED) ? 15 : 3).sound(SoundType.GLASS),
                    PuzzleNodeBlock.Kind.LENS, () -> null));

    // ---- seals and floor traps
    public static final RegistryObject<Block> CORAL_SEAL = BLOCKS.register("coral_seal",
            () -> new SealBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PINK).strength(-1.0f, 3600000.0f).noLootTable()
                    .lightLevel(state -> 5).sound(SoundType.CORAL_BLOCK), () -> ModEntities.CORALCLAD_JUGGERNAUT.get(), "Coralclad Juggernaut"));
    public static final RegistryObject<Block> RIME_SEAL = BLOCKS.register("rime_seal",
            () -> new SealBlock(BlockBehaviour.Properties.of().mapColor(MapColor.ICE).strength(-1.0f, 3600000.0f).noLootTable()
                    .lightLevel(state -> 6).sound(SoundType.GLASS), () -> ModEntities.RIMEGUARD.get(), "Rimeguard"));
    public static final RegistryObject<Block> SUN_SEAL = BLOCKS.register("sun_seal",
            () -> new SealBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_ORANGE).strength(-1.0f, 3600000.0f).noLootTable()
                    .lightLevel(state -> 8).sound(SoundType.STONE), () -> ModEntities.SANDGLASS_SENTINEL.get(), "Sandglass Sentinel"));
    public static final RegistryObject<Block> BRINE_GRATE = BLOCKS.register("brine_grate",
            () -> new TrapBlock(BlockBehaviour.Properties.of().mapColor(MapColor.WARPED_WART_BLOCK).strength(3.0f).lightLevel(state -> 4)
                    .sound(SoundType.METAL), TrapBlock.Kind.BRINE));
    public static final RegistryObject<Block> FROST_RUNE = BLOCKS.register("frost_rune",
            () -> new TrapBlock(BlockBehaviour.Properties.of().mapColor(MapColor.ICE).strength(3.0f).lightLevel(state -> 6)
                    .sound(SoundType.GLASS), TrapBlock.Kind.FROST));
    public static final RegistryObject<Block> SUNFLARE_PLATE = BLOCKS.register("sunflare_plate",
            () -> new TrapBlock(BlockBehaviour.Properties.of().mapColor(MapColor.GOLD).strength(3.0f).lightLevel(state -> 8)
                    .sound(SoundType.METAL), TrapBlock.Kind.SUNFLARE));

    // ---- outer realm ores and storage blocks
    public static final RegistryObject<Block> TIDESTONE_ORE = BLOCKS.register("tidestone_ore",
            () -> new DropExperienceBlock(BlockBehaviour.Properties.of().mapColor(MapColor.WARPED_NYLIUM).strength(3.5f, 4.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 5).sound(SoundType.STONE), UniformInt.of(3, 6)));
    public static final RegistryObject<Block> RIME_ORE = BLOCKS.register("rime_ore",
            () -> new DropExperienceBlock(BlockBehaviour.Properties.of().mapColor(MapColor.ICE).strength(3.5f, 4.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 3).sound(SoundType.STONE), UniformInt.of(3, 6)));
    public static final RegistryObject<Block> SUNGLASS_ORE = BLOCKS.register("sunglass_ore",
            () -> new DropExperienceBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_ORANGE).strength(3.5f, 4.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 5).sound(SoundType.STONE), UniformInt.of(3, 6)));
    public static final RegistryObject<Block> TIDESTONE_BLOCK = BLOCKS.register("tidestone_block",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.WARPED_NYLIUM).strength(5.0f, 6.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 10).sound(SoundType.AMETHYST)));
    public static final RegistryObject<Block> RIME_BLOCK = BLOCKS.register("rime_block",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.ICE).strength(5.0f, 6.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 8).sound(SoundType.AMETHYST)));
    public static final RegistryObject<Block> SUNGLASS_BLOCK = BLOCKS.register("sunglass_block",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_RED).strength(5.0f, 6.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 12).sound(SoundType.AMETHYST)));

    // ==================================================================== act three
    public static final RegistryObject<Block> CLOCK_DIAL = BLOCKS.register("clock_dial",
            () -> new ClockDialBlock(BlockBehaviour.Properties.of().mapColor(MapColor.GOLD).strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> state.getValue(ClockDialBlock.FILLED) ? 15 : 6).sound(SoundType.METAL)));
    public static final RegistryObject<Block> MASTER_CLOCK = BLOCKS.register("master_clock",
            () -> new MasterClockBlock(BlockBehaviour.Properties.of().mapColor(MapColor.GOLD).strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> 12).sound(SoundType.METAL)));
    public static final RegistryObject<Block> SPORE_VALVE = BLOCKS.register("spore_valve",
            () -> new SporeValveBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_MAGENTA).strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> state.getValue(SporeValveBlock.OPEN) ? 14 : 4).sound(SoundType.BONE_BLOCK)));
    public static final RegistryObject<Block> PARADOX_SEAL = BLOCKS.register("paradox_seal",
            () -> new SealBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(-1.0f, 3600000.0f).noLootTable()
                    .lightLevel(state -> 8).sound(SoundType.METAL), () -> ModEntities.HOUR_WARDEN.get(), "Hour Warden"));
    public static final RegistryObject<Block> ROOT_SEAL = BLOCKS.register("root_seal",
            () -> new SealBlock(BlockBehaviour.Properties.of().mapColor(MapColor.TERRACOTTA_WHITE).strength(-1.0f, 3600000.0f).noLootTable()
                    .lightLevel(state -> 5).sound(SoundType.ROOTS), () -> ModEntities.HUSK_GUARD.get(), "Husk Guard"));
    public static final RegistryObject<Block> TIME_SNARE = BLOCKS.register("time_snare",
            () -> new TrapBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(3.0f).lightLevel(state -> 7)
                    .sound(SoundType.METAL), TrapBlock.Kind.TIME));
    public static final RegistryObject<Block> ROOT_SNARE = BLOCKS.register("root_snare",
            () -> new TrapBlock(BlockBehaviour.Properties.of().mapColor(MapColor.TERRACOTTA_WHITE).strength(3.0f).lightLevel(state -> 5)
                    .sound(SoundType.ROOTS), TrapBlock.Kind.ROOT));
    public static final RegistryObject<Block> CHRONITE_BLOCK = BLOCKS.register("chronite_block",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(5.0f, 6.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 12).sound(SoundType.AMETHYST)));
    public static final RegistryObject<Block> BLOOMSPORE_BLOCK = BLOCKS.register("bloomspore_block",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_MAGENTA).strength(2.0f, 3.0f)
                    .lightLevel(state -> 12).sound(SoundType.SHROOMLIGHT)));

    // ==================================================================== the finale
    public static final RegistryObject<Block> RELIC_PEDESTAL = BLOCKS.register("relic_pedestal",
            () -> new RelicPedestalBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(-1.0f, 3600000.0f).noOcclusion()
                    .lightLevel(state -> state.getValue(RelicPedestalBlock.FILLED) ? 12 : 3).sound(SoundType.STONE)));
    public static final RegistryObject<Block> REALM_NODE = BLOCKS.register("realm_node",
            () -> new RealmNodeBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> state.getValue(RealmNodeBlock.LIT) ? 15 : 4).sound(SoundType.AMETHYST)));
    public static final RegistryObject<Block> UNMAKING_ANCHOR = BLOCKS.register("unmaking_anchor",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(2.0f, 6.0f).noLootTable()
                    .lightLevel(state -> 9).sound(SoundType.AMETHYST)));

    // ==================================================================== realm kits: the two rift ores
    public static final RegistryObject<Block> CHRONITE_ORE = BLOCKS.register("chronite_ore",
            () -> new DropExperienceBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(4.0f, 5.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 6).sound(SoundType.DEEPSLATE), UniformInt.of(3, 7)));
    public static final RegistryObject<Block> BLOOMSPORE_ORE = BLOCKS.register("bloomspore_ore",
            () -> new DropExperienceBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_MAGENTA).strength(4.0f, 5.0f)
                    .requiresCorrectToolForDrops().lightLevel(state -> 7).sound(SoundType.STONE), UniformInt.of(3, 7)));

    // ==================================================================== the lieutenants' lairs
    public static final RegistryObject<Block> LAIR_SEAL = BLOCKS.register("lair_seal",
            () -> new com.aurelia.block.LairSealBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).strength(-1.0f, 3600000.0f)
                    .lightLevel(state -> 11).sound(SoundType.LODESTONE)));
}
