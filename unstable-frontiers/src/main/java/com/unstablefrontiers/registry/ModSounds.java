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

    private ModSounds() {}

    private static Supplier<SoundEvent> event(String name) {
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(UnstableFrontiers.id(name)));
    }

    public static void register(IEventBus bus) {
        SOUNDS.register(bus);
    }
}
