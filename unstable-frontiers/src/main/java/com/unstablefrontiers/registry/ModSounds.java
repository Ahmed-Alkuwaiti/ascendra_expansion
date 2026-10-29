package com.unstablefrontiers.registry;

import com.unstablefrontiers.UnstableFrontiers;
import java.util.function.Supplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.sounds.SoundEvent;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * The addon's sound events, defined in assets/unstable_frontiers/sounds.json: landmark cues reuse vanilla sounds at other
 * pitches; the creatures have their own original sounds, synthesised by tools/sounds/synth.py. All carry subtitles and can
 * be replaced by a resource pack without code.
 */
public final class ModSounds {
    private static final DeferredRegister<SoundEvent> SOUNDS = DeferredRegister.create(Registries.SOUND_EVENT, UnstableFrontiers.MODID);

    public static final Supplier<SoundEvent> DISCOVER = event("landmark.discover");
    public static final Supplier<SoundEvent> WAKE = event("landmark.wake");
    public static final Supplier<SoundEvent> WAVE = event("landmark.wave");
    public static final Supplier<SoundEvent> GATE = event("landmark.gate");
    public static final Supplier<SoundEvent> CONQUER = event("landmark.conquer");
    public static final Supplier<SoundEvent> ELITE_TELL = event("elite.tell");
    public static final Supplier<SoundEvent> ELITE_SLAM = event("elite.slam");
    public static final Supplier<SoundEvent> PYLON = event("finale.pylon");
    public static final Supplier<SoundEvent> SHIELD = event("finale.shield");
    public static final Supplier<SoundEvent> BROOD = event("brood.crack");
    public static final Supplier<SoundEvent> SHACKLE = event("item.shackle");
    public static final Supplier<SoundEvent> LENS = event("item.lens");
    // the creatures' own sounds (tools/sounds/synth.py)
    public static final Supplier<SoundEvent> GNASHBACK_AMBIENT = event("gnashback.ambient");
    public static final Supplier<SoundEvent> GNASHBACK_HURT = event("gnashback.hurt");
    public static final Supplier<SoundEvent> GNASHBACK_DEATH = event("gnashback.death");
    public static final Supplier<SoundEvent> GNASHBACK_BITE = event("gnashback.bite");
    public static final Supplier<SoundEvent> GNASHBACK_SCRAPE = event("gnashback.scrape");
    public static final Supplier<SoundEvent> GNASHBACK_CHARGE = event("gnashback.charge");
    public static final Supplier<SoundEvent> GNASHBACK_IMPACT = event("gnashback.impact");
    public static final Supplier<SoundEvent> SHRIKEWING_AMBIENT = event("shrikewing.ambient");
    public static final Supplier<SoundEvent> SHRIKEWING_HURT = event("shrikewing.hurt");
    public static final Supplier<SoundEvent> SHRIKEWING_DEATH = event("shrikewing.death");
    public static final Supplier<SoundEvent> SHRIKEWING_SCREECH = event("shrikewing.screech");
    public static final Supplier<SoundEvent> SHRIKEWING_FLAP = event("shrikewing.flap");
    public static final Supplier<SoundEvent> MATRIARCH_AMBIENT = event("matriarch.ambient");
    public static final Supplier<SoundEvent> MATRIARCH_HURT = event("matriarch.hurt");
    public static final Supplier<SoundEvent> MATRIARCH_DEATH = event("matriarch.death");
    public static final Supplier<SoundEvent> MATRIARCH_ROAR = event("matriarch.roar");
    public static final Supplier<SoundEvent> MATRIARCH_BROOD = event("matriarch.brood");
    public static final Supplier<SoundEvent> MATRIARCH_SWEEP_TELL = event("matriarch.sweep_tell");
    public static final Supplier<SoundEvent> MATRIARCH_SWEEP = event("matriarch.sweep");
    public static final Supplier<SoundEvent> MATRIARCH_SPIT = event("matriarch.spit");
    public static final Supplier<SoundEvent> MATRIARCH_SLAM = event("matriarch.slam");
    public static final Supplier<SoundEvent> MATRIARCH_ACID = event("matriarch.acid");

    // the Rift Observatory and the Astral Abyss
    public static final Supplier<SoundEvent> MITE_AMBIENT = event("mite.ambient");
    public static final Supplier<SoundEvent> MITE_HURT = event("mite.hurt");
    public static final Supplier<SoundEvent> MITE_DEATH = event("mite.death");
    public static final Supplier<SoundEvent> MITE_TELL = event("mite.tell");
    public static final Supplier<SoundEvent> MITE_SPIT = event("mite.spit");
    public static final Supplier<SoundEvent> WARDEN_AMBIENT = event("warden.ambient");
    public static final Supplier<SoundEvent> WARDEN_HURT = event("warden.hurt");
    public static final Supplier<SoundEvent> WARDEN_DEATH = event("warden.death");
    public static final Supplier<SoundEvent> WARDEN_TELL = event("warden.tell");
    public static final Supplier<SoundEvent> WARDEN_BEAM = event("warden.beam");
    public static final Supplier<SoundEvent> WARDEN_STALL = event("warden.stall");
    public static final Supplier<SoundEvent> WARDEN_RECOVER = event("warden.recover");
    public static final Supplier<SoundEvent> WARDEN_PULSE = event("warden.pulse");
    public static final Supplier<SoundEvent> LEVIATHAN_AMBIENT = event("leviathan.ambient");
    public static final Supplier<SoundEvent> LEVIATHAN_HURT = event("leviathan.hurt");
    public static final Supplier<SoundEvent> LEVIATHAN_DEATH = event("leviathan.death");
    public static final Supplier<SoundEvent> LEVIATHAN_ROAR = event("leviathan.roar");
    public static final Supplier<SoundEvent> LEVIATHAN_BEAM_TELL = event("leviathan.beam_tell");
    public static final Supplier<SoundEvent> LEVIATHAN_BEAM = event("leviathan.beam");
    public static final Supplier<SoundEvent> LEVIATHAN_WELL = event("leviathan.well");
    public static final Supplier<SoundEvent> LEVIATHAN_PASS = event("leviathan.pass");
    public static final Supplier<SoundEvent> LEVIATHAN_SUMMON = event("leviathan.summon");
    public static final Supplier<SoundEvent> LEVIATHAN_SLAM = event("leviathan.slam");
    public static final Supplier<SoundEvent> RIFT_OPEN = event("rift.open");
    public static final Supplier<SoundEvent> ABYSS_AMBIENT = event("abyss.ambient");

    private ModSounds() {}

    private static Supplier<SoundEvent> event(String name) {
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(UnstableFrontiers.id(name)));
    }

    public static void register(IEventBus bus) {
        SOUNDS.register(bus);
    }
}
