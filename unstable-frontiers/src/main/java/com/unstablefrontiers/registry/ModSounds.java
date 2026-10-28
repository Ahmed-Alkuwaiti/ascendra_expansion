package com.unstablefrontiers.registry;

import com.unstablefrontiers.UnstableFrontiers;
import java.util.function.Supplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.sounds.SoundEvent;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * The addon's sound events. Each is defined in assets/unstable_frontiers/sounds.json from vanilla sound files (played at
 * other pitches and mixed), so they carry their own subtitles and can be replaced by a resource pack without code.
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

    private ModSounds() {}

    private static Supplier<SoundEvent> event(String name) {
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(UnstableFrontiers.id(name)));
    }

    public static void register(IEventBus bus) {
        SOUNDS.register(bus);
    }
}
