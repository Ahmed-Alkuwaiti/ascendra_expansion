package com.unstablefrontiers.entity;

import com.unstablefrontiers.abyss.EclipseEncounter;
import com.unstablefrontiers.config.FrontierConfig;
import com.unstablefrontiers.registry.ModEntities;
import com.unstablefrontiers.registry.ModSounds;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.RawAnimation;

/**
 * The Eclipse Leviathan, fought over the Hollow Crown. It never leaves the arena, nothing it does throws anyone outward
 * (every push points at the arena's middle or at a marked well), and every attack is shown before it lands:
 * <ul>
 * <li><b>Eclipse Beam</b>: it hangs at the arena's edge, rears, and its corona flares and spins (1.5 s) while a line of
 * light on the floor shows the full sweep. Then the beam sweeps along that line. Stand behind an obelisk (the beam stops
 * at blocks) or where it has already passed.</li>
 * <li><b>Gravity Well</b>: violet rings close around each fighter (1.5 s); when they close, anything inside is dragged to
 * the ring's middle and hurt. Step out of your ring.</li>
 * <li><b>Low Pass</b>: a trail of soul fire marks a line across the arena (1.25 s); it sweeps low along it, and then hangs
 * low at the far side for a moment: the melee window.</li>
 * <li><b>Brood</b> (second phase on): a few Lumen Mites, never more than four at once.</li>
 * <li><b>Eclipse</b> (third phase): it climbs high, the arena darkens, a ring of fire marks the middle; it crashes down
 * there and lies exposed, belly plates open, for six seconds: double damage.</li>
 * </ul>
 * Phases change at two thirds and one third of its health, each with a roar: the second phase sweeps the beam back and
 * forth and adds mites; the third adds more wells and the Eclipse.
 */
public class EclipseLeviathanEntity extends AnimatedMonster {
    public static final int INTRO = 0, CIRCLE = 1, BEAM_TELL = 2, BEAM = 3, WELL_TELL = 4, WELL = 5, PASS_TELL = 6, PASS = 7, LOW = 8,
            SUMMON = 9, ROAR = 10, ECLIPSE_TELL = 11, DIVE = 12, EXPOSED = 13;
    private static final int INTRO_TICKS = 70, BEAM_TELL_TICKS = 30, BEAM_TICKS = 60, WELL_TELL_TICKS = 30, PASS_TELL_TICKS = 25,
            LOW_TICKS = 40, SUMMON_TICKS = 30, ROAR_TICKS = 40, ECLIPSE_TELL_TICKS = 50, EXPOSED_TICKS = 120;
    public static final int MAX_MITES = 4;
    private static final DustParticleOptions BEAM_MARK = new DustParticleOptions(new Vector3f(1.0F, 0.8F, 0.35F), 1.3F);
    private static final DustParticleOptions WELL_MARK = new DustParticleOptions(new Vector3f(0.6F, 0.3F, 1.0F), 1.4F);

    private static final RawAnimation A_SWIM = RawAnimation.begin().thenLoop("animation.eclipse_leviathan.swim");
    private static final RawAnimation A_BEAM_TELL = RawAnimation.begin().thenPlayAndHold("animation.eclipse_leviathan.beam_tell");
    private static final RawAnimation A_BEAM = RawAnimation.begin().thenLoop("animation.eclipse_leviathan.beam");
    private static final RawAnimation A_WELL_TELL = RawAnimation.begin().thenPlayAndHold("animation.eclipse_leviathan.well_tell");
    private static final RawAnimation A_PASS = RawAnimation.begin().thenLoop("animation.eclipse_leviathan.pass");
    private static final RawAnimation A_SUMMON = RawAnimation.begin().thenPlayAndHold("animation.eclipse_leviathan.summon");
    private static final RawAnimation A_ROAR = RawAnimation.begin().thenPlay("animation.eclipse_leviathan.roar").thenLoop("animation.eclipse_leviathan.swim");
    private static final RawAnimation A_EXPOSED = RawAnimation.begin().thenLoop("animation.eclipse_leviathan.exposed");
    private static final RawAnimation A_DEATH = RawAnimation.begin().thenPlayAndHold("animation.eclipse_leviathan.death");

    private final ServerBossEvent bar = (ServerBossEvent) new ServerBossEvent(Component.translatable("entity.unstable_frontiers.eclipse_leviathan")
            .withStyle(ChatFormatting.LIGHT_PURPLE), BossEvent.BossBarColor.PURPLE, BossEvent.BossBarOverlay.NOTCHED_6).setDarkenScreen(true);
    private Vec3 center = Vec3.ZERO;
    private int phase = 1;
    private int cooldown = 40;
    private int cycle;
    private double orbit;
    private Vec3 from = Vec3.ZERO, to = Vec3.ZERO;   // beam sweep or pass line
    private final List<Vec3> wells = new ArrayList<>();
    private final Set<UUID> hitThisPass = new HashSet<>();
    private final List<UUID> mites = new ArrayList<>();
    /** Continuous-integration only: stand-ins (no real players on the test server) treated as fighters for attacks. */
    public static final List<LivingEntity> TRIAL_TARGETS = new ArrayList<>();

    public EclipseLeviathanEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        xpReward = 500;
        setNoGravity(true);
        noPhysics = true;
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 700.0D)
                .add(Attributes.ATTACK_DAMAGE, 18.0D)
                .add(Attributes.ARMOR, 12.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 4.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D)
                .add(Attributes.FOLLOW_RANGE, 64.0D)
                .add(Attributes.FLYING_SPEED, 0.6D);
    }

    /** Set by the encounter when it calls the Leviathan up: the arena floor's middle, at the height of a standing player's feet. */
    public void setCenter(Vec3 c) {
        center = c;
        orbit = random.nextDouble() * Math.PI * 2;
    }

    public Vec3 center() {
        return center;
    }

    public int phase() {
        return phase;
    }

    @Override
    protected void registerGoals() {
        // no goals: the fight is driven in customServerAiStep, around the arena
    }

    // ------------------------------------------------------------------------------------------------- the fight
    public List<ServerPlayer> fighters() {
        List<ServerPlayer> out = new ArrayList<>();
        if (level() instanceof ServerLevel sl) {
            for (ServerPlayer p : sl.players()) {
                if (p.isAlive() && !p.isSpectator() && !p.isCreative() && EclipseEncounter.inArena(center, p.position())) {
                    out.add(p);
                }
            }
        }
        return out;
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        noPhysics = true;
        if (center == Vec3.ZERO) {
            setCenter(position());
        }
        bar.setProgress(getHealth() / getMaxHealth());
        List<ServerPlayer> fighters = fighters();
        cooldown--;
        switch (state()) {
            case INTRO -> {
                moveTo(center.add(0, -24 + 36 * Math.min(1, stateTicks / (double) INTRO_TICKS), 0), 0.6D);
                if (stateTicks == 1) {
                    sound(ModSounds.LEVIATHAN_ROAR.get(), 6.0F, 0.7F);
                }
                if (stateTicks >= INTRO_TICKS) {
                    setState(ROAR);
                }
            }
            case ROAR -> {
                hover(center.add(Math.cos(orbit) * 18, 12, Math.sin(orbit) * 18));
                if (stateTicks == 1) {
                    triggerAnim("main", "roar");
                    sound(ModSounds.LEVIATHAN_ROAR.get(), 6.0F, 1.0F);
                }
                if (stateTicks >= ROAR_TICKS) {
                    setState(CIRCLE);
                    cooldown = 30;
                }
            }
            case CIRCLE -> circle(fighters);
            case BEAM_TELL -> beamTell();
            case BEAM -> beam();
            case WELL_TELL -> wellTell();
            case WELL -> {
                if (stateTicks >= 12) {
                    setState(CIRCLE);
                    cooldown = 50;
                }
            }
            case PASS_TELL -> passTell();
            case PASS -> pass();
            case LOW -> {
                hover(to.add(0, 2.5D, 0));
                if (stateTicks >= LOW_TICKS) {
                    setState(CIRCLE);
                    cooldown = 40;
                }
            }
            case SUMMON -> summon();
            case ECLIPSE_TELL -> eclipseTell(fighters);
            case DIVE -> dive();
            case EXPOSED -> {
                setDeltaMovement(Vec3.ZERO);
                if (stateTicks % 10 == 0) {
                    particles(ParticleTypes.GLOW, position().add(0, 0.5D, 0), 10, 1.5D);
                }
                if (stateTicks >= EXPOSED_TICKS) {
                    setState(CIRCLE);
                    cooldown = 40;
                    sound(ModSounds.LEVIATHAN_ROAR.get(), 4.0F, 1.3F);
                }
            }
            default -> {
            }
        }
        Vec3 v = getDeltaMovement();
        if (state() != BEAM && state() != BEAM_TELL && state() != EXPOSED && v.horizontalDistanceSqr() > 0.004D) {
            setYRot((float) Math.toDegrees(Math.atan2(-v.x, v.z)));
            yBodyRot = getYRot();
            yHeadRot = getYRot();
        }
    }

    private void circle(List<ServerPlayer> fighters) {
        orbit += phase == 3 ? 0.016D : 0.012D;
        hover(center.add(Math.cos(orbit) * 22, 12 + Math.sin(orbit * 2) * 2, Math.sin(orbit) * 22));
        TRIAL_TARGETS.removeIf(e -> !e.isAlive());
        if (cooldown > 0 || fighters.isEmpty() && TRIAL_TARGETS.isEmpty()) {
            return;
        }
        int[] plan = switch (phase) {
            case 1 -> new int[] {BEAM_TELL, PASS_TELL, WELL_TELL};
            case 2 -> new int[] {BEAM_TELL, SUMMON, WELL_TELL, PASS_TELL};
            default -> new int[] {ECLIPSE_TELL, BEAM_TELL, WELL_TELL, PASS_TELL, SUMMON};
        };
        int next = plan[cycle++ % plan.length];
        if (next == SUMMON && liveMites() >= MAX_MITES) {
            next = WELL_TELL;
        }
        startAttack(next, fighters);
    }

    private void startAttack(int s, List<ServerPlayer> fighters) {
        setState(s);
        switch (s) {
            case BEAM_TELL -> {
                // hang at the edge on this side; the sweep runs across the arena, square to its line of sight
                Vec3 edge = new Vec3(Math.cos(orbit), 0, Math.sin(orbit));
                Vec3 side = new Vec3(-edge.z, 0, edge.x);
                from = center.add(side.scale(22)).add(edge.scale(-4));
                to = center.add(side.scale(-22)).add(edge.scale(-4));
                sound(ModSounds.LEVIATHAN_BEAM_TELL.get(), 5.0F, 1.0F);
                tell(fighters, "beam");
            }
            case WELL_TELL -> {
                wells.clear();
                int max = phase == 3 ? 4 : 3;
                List<LivingEntity> marked = new ArrayList<>(fighters);
                marked.addAll(TRIAL_TARGETS);
                for (LivingEntity p : marked) {
                    if (wells.size() < max) {
                        wells.add(new Vec3(p.getX(), center.y, p.getZ()));
                    }
                }
                if (phase == 3 && wells.size() < max) {
                    wells.add(center);
                }
                sound(ModSounds.LEVIATHAN_WELL.get(), 4.0F, 0.8F);
                tell(fighters, "well");
            }
            case PASS_TELL -> {
                // lines run between the obelisks (they stand at 30 degrees off every 60), so a pass never clips one
                double a = Math.round(orbit / (Math.PI / 3)) * (Math.PI / 3);
                Vec3 dir = new Vec3(Math.cos(a), 0, Math.sin(a));
                from = center.add(dir.scale(28));
                to = center.add(dir.scale(-26));
                hitThisPass.clear();
                sound(ModSounds.LEVIATHAN_PASS.get(), 4.0F, 0.8F);
                tell(fighters, "pass");
            }
            case SUMMON -> sound(ModSounds.LEVIATHAN_SUMMON.get(), 4.0F, 1.0F);
            case ECLIPSE_TELL -> {
                sound(ModSounds.LEVIATHAN_ROAR.get(), 6.0F, 0.6F);
                tell(fighters, "eclipse");
            }
            default -> {
            }
        }
    }

    private void tell(List<ServerPlayer> fighters, String attack) {
        for (ServerPlayer p : fighters) {
            p.displayClientMessage(Component.translatable("boss.unstable_frontiers.leviathan." + attack).withStyle(ChatFormatting.YELLOW), true);
        }
    }

    private Vec3 mouth() {
        return position().add(Vec3.directionFromRotation(0, getYRot()).scale(4.5D)).add(0, 1.2D, 0);
    }

    private void beamTell() {
        Vec3 mid = from.add(to).scale(0.5D);
        Vec3 out = mid.subtract(center);
        Vec3 edge = center.add(new Vec3(Math.cos(orbit), 0, Math.sin(orbit)).scale(26)).add(0, 10, 0);
        hover(edge);
        faceTowards(center);
        if (stateTicks % 3 == 0) {
            line(BEAM_MARK, from.add(0, 0.15D, 0), to.add(0, 0.15D, 0), 0.8D);
            particles(ParticleTypes.FLAME, mouth(), 4, 0.6D);
        }
        if (stateTicks >= BEAM_TELL_TICKS) {
            setState(BEAM);
            sound(ModSounds.LEVIATHAN_BEAM.get(), 6.0F, 1.0F);
        }
    }

    private void beam() {
        setDeltaMovement(getDeltaMovement().scale(0.5D));
        int len = phase >= 2 ? BEAM_TICKS * 2 : BEAM_TICKS;
        double t = stateTicks / (double) BEAM_TICKS;
        double f = phase >= 2 ? (t <= 1 ? t : 2 - t) : t;     // the second phase sweeps back again
        Vec3 aim = from.lerp(to, Math.max(0, Math.min(1, f)));
        faceTowards(aim);
        Vec3 m = mouth();
        Vec3 dir = aim.subtract(m).normalize();
        Vec3 end = m.add(dir.scale(m.distanceTo(aim) + 3));
        BlockHitResult clip = level().clip(new ClipContext(m, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this));
        Vec3 stop = clip.getType() == HitResult.Type.BLOCK ? clip.getLocation() : end;
        if (stateTicks % 2 == 0) {
            line(ParticleTypes.END_ROD, m, stop, 0.9D);
            particles(ParticleTypes.FLAME, stop, 6, 0.5D);
        }
        if (stateTicks % 3 == 0) {
            for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(m, stop).inflate(1.5D), this::harmable)) {
                if (OrreryWardenEntity.distanceToLine(e.position().add(0, e.getBbHeight() / 2, 0), m, stop) < 1.3D + e.getBbWidth() / 2) {
                    e.hurt(damageSources().indirectMagic(this, this), attack() * 0.45F);
                    e.igniteForSeconds(2);
                }
            }
        }
        if (stateTicks >= len) {
            setState(CIRCLE);
            cooldown = 50;
        }
    }

    private void wellTell() {
        hover(center.add(Math.cos(orbit) * 20, 14, Math.sin(orbit) * 20));
        double r = 4.5D * (1 - 0.4D * stateTicks / WELL_TELL_TICKS);
        if (stateTicks % 3 == 0) {
            for (Vec3 w : wells) {
                ring(WELL_MARK, w, r);
                particles(ParticleTypes.REVERSE_PORTAL, w.add(0, 0.5D, 0), 6, 0.3D);
            }
        }
        if (stateTicks >= WELL_TELL_TICKS) {
            for (Vec3 w : wells) {
                particles(ParticleTypes.EXPLOSION, w.add(0, 0.5D, 0), 2, 0.5D);
                for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(w, w).inflate(4.5D, 3D, 4.5D), this::harmable)) {
                    if (e.position().distanceToSqr(w) > 4.5D * 4.5D) {
                        continue;
                    }
                    Vec3 pull = w.subtract(e.position());
                    Vec3 flat = new Vec3(pull.x, 0, pull.z);
                    Vec3 v = flat.lengthSqr() < 0.04D ? Vec3.ZERO : flat.normalize().scale(Math.min(0.8D, flat.length() * 0.25D));
                    e.setDeltaMovement(v.x, 0.25D, v.z);       // toward the well's middle, which is on the arena
                    e.hurtMarked = true;
                    e.hurt(damageSources().indirectMagic(this, this), attack() * 0.6F);
                    e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 1));
                }
            }
            sound(ModSounds.LEVIATHAN_WELL.get(), 4.0F, 1.4F);
            setState(WELL);
        }
    }

    private void passTell() {
        moveTo(from.add(0, 6, 0), 0.9D);
        if (stateTicks % 3 == 0) {
            line(ParticleTypes.SOUL_FIRE_FLAME, from.add(0, 0.2D, 0), to.add(0, 0.2D, 0), 1.0D);
        }
        if (stateTicks >= PASS_TELL_TICKS) {
            setState(PASS);
            sound(ModSounds.LEVIATHAN_PASS.get(), 5.0F, 1.2F);
        }
    }

    private void pass() {
        Vec3 target = to.add(0, 1.0D, 0);
        Vec3 d = target.subtract(position());
        if (d.length() < 1.5D || stateTicks > 90) {
            setState(LOW);
            return;
        }
        // down to the floor quickly, then across at a steady speed
        Vec3 v = d.normalize().scale(0.95D);
        setDeltaMovement(v);
        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(0.5D), this::harmable)) {
            if (hitThisPass.add(e.getUUID())) {
                e.hurt(damageSources().mobAttack(this), attack());
                Vec3 in = center.subtract(e.position());
                Vec3 flat = new Vec3(in.x, 0, in.z);
                flat = flat.lengthSqr() < 0.01D ? Vec3.ZERO : flat.normalize().scale(0.35D);
                e.setDeltaMovement(flat.x, 0.35D, flat.z);    // bowled toward the middle, never outward
                e.hurtMarked = true;
            }
        }
    }

    private void summon() {
        hover(center.add(Math.cos(orbit) * 18, 14, Math.sin(orbit) * 18));
        if (stateTicks == 15 && level() instanceof ServerLevel sl) {
            int want = Math.min(2, MAX_MITES - liveMites());
            for (int i = 0; i < want; i++) {
                LumenMiteEntity m = ModEntities.LUMEN_MITE.get().create(sl);
                if (m == null) {
                    continue;
                }
                double a = random.nextDouble() * Math.PI * 2;
                m.moveTo(center.x + Math.cos(a) * 10, center.y + 4, center.z + Math.sin(a) * 10, 0, 0);
                m.setPersistenceRequired();
                m.getPersistentData().putBoolean(EclipseEncounter.ADD_TAG, true);
                sl.addFreshEntity(m);
                mites.add(m.getUUID());
                sl.sendParticles(ParticleTypes.REVERSE_PORTAL, m.getX(), m.getY(), m.getZ(), FrontierConfig.particleCount(20), 0.4, 0.4, 0.4, 0.1);
            }
        }
        if (stateTicks >= SUMMON_TICKS) {
            setState(CIRCLE);
            cooldown = 40;
        }
    }

    private int liveMites() {
        if (!(level() instanceof ServerLevel sl)) {
            return 0;
        }
        mites.removeIf(id -> !(sl.getEntity(id) instanceof Mob m) || !m.isAlive());
        return mites.size();
    }

    public List<UUID> mites() {
        return mites;
    }

    private void eclipseTell(List<ServerPlayer> fighters) {
        moveTo(center.add(0, 22, 0), 0.5D);
        if (stateTicks % 3 == 0) {
            ring(ParticleTypes.FLAME, center.add(0, 0.2D, 0), 6.0D);
            ring(ParticleTypes.FLAME, center.add(0, 0.2D, 0), 3.0D);
        }
        if (stateTicks == 10) {
            for (ServerPlayer p : fighters) {
                p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 70, 0, false, false));
            }
        }
        if (stateTicks >= ECLIPSE_TELL_TICKS) {
            setState(DIVE);
        }
    }

    private void dive() {
        Vec3 d = center.subtract(position());
        if (d.length() < 1.2D || stateTicks > 40) {
            setPos(center.x, center.y, center.z);
            setDeltaMovement(Vec3.ZERO);
            sound(ModSounds.LEVIATHAN_SLAM.get(), 6.0F, 0.8F);
            particles(ParticleTypes.EXPLOSION, center.add(0, 0.5D, 0), 8, 3.0D);
            for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(center, center).inflate(6.5D, 3D, 6.5D), this::harmable)) {
                if (e.position().distanceToSqr(center) < 6.5D * 6.5D) {
                    e.hurt(damageSources().mobAttack(this), attack() * 1.2F);   // no knockback: the landing hurts, it does not throw
                    e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 1));
                }
            }
            setState(EXPOSED);
            return;
        }
        setDeltaMovement(d.normalize().scale(Math.min(1.6D, d.length())));
    }

    private boolean harmable(LivingEntity e) {
        return e != this && e.isAlive() && !StarBoltEntity.isAbyssCreature(e) && !(e instanceof Player p && (p.isCreative() || p.isSpectator()));
    }

    private float attack() {
        return (float) getAttributeValue(Attributes.ATTACK_DAMAGE);
    }

    // ------------------------------------------------------------------------------------------------ movement
    private void hover(Vec3 at) {
        moveTo(at, 0.5D);
    }

    private void moveTo(Vec3 at, double speed) {
        Vec3 d = at.subtract(position());
        Vec3 want = d.lengthSqr() > 1 ? d.normalize().scale(speed) : d.scale(speed);
        setDeltaMovement(getDeltaMovement().scale(0.85D).add(want.scale(0.15D)));
    }

    private void faceTowards(Vec3 at) {
        Vec3 d = at.subtract(position());
        setYRot((float) Math.toDegrees(Math.atan2(-d.x, d.z)));
        yBodyRot = getYRot();
        yHeadRot = getYRot();
    }

    @Override
    public void travel(Vec3 input) {
        if (isAlive()) {
            move(MoverType.SELF, getDeltaMovement());
        } else {
            setDeltaMovement(getDeltaMovement().add(0, -0.02D, 0).scale(0.9D));
            move(MoverType.SELF, getDeltaMovement());
        }
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    protected void doPush(Entity e) {
    }

    @Override
    public boolean removeWhenFarAway(double d) {
        return false;
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }

    // ------------------------------------------------------------------------------------------------- damage
    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.is(DamageTypes.GENERIC_KILL) || source.is(DamageTypes.FELL_OUT_OF_WORLD) && position().y < -64) {
            return super.hurt(source, amount);
        }
        if (state() == INTRO || source.is(DamageTypes.FELL_OUT_OF_WORLD) || source.is(DamageTypes.IN_WALL)
                || source.getEntity() instanceof LumenMiteEntity || source.getEntity() == this) {
            return false;
        }
        if (state() == EXPOSED) {
            amount *= 2.0F;
            particles(ParticleTypes.CRIT, position().add(0, 1.0D, 0), 12, 1.5D);
        } else if (state() == ROAR) {
            amount *= 0.5F;
        }
        float before = getHealth();
        boolean hurt = super.hurt(source, amount);
        if (hurt && isAlive()) {
            float f = getHealth() / getMaxHealth();
            int want = f > 2 / 3F ? 1 : f > 1 / 3F ? 2 : 3;
            if (want > phase && before / getMaxHealth() > f) {
                phase = want;
                setState(ROAR);
                cycle = 0;
                for (ServerPlayer p : fighters()) {
                    p.displayClientMessage(Component.translatable("boss.unstable_frontiers.leviathan.phase" + phase).withStyle(ChatFormatting.LIGHT_PURPLE), false);
                }
            }
        }
        return hurt;
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        if (level() instanceof ServerLevel sl) {
            EclipseEncounter.victory(sl, this);
        }
    }

    // ------------------------------------------------------------------------------------------------- bar and save
    @Override
    public void startSeenByPlayer(ServerPlayer p) {
        super.startSeenByPlayer(p);
        bar.addPlayer(p);
    }

    @Override
    public void stopSeenByPlayer(ServerPlayer p) {
        super.stopSeenByPlayer(p);
        bar.removePlayer(p);
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putDouble("CX", center.x);
        tag.putDouble("CY", center.y);
        tag.putDouble("CZ", center.z);
        tag.putInt("Phase", phase);
        ListTag ids = new ListTag();
        for (UUID u : mites) {
            ids.add(NbtUtils.createUUID(u));
        }
        tag.put("Mites", ids);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        center = new Vec3(tag.getDouble("CX"), tag.getDouble("CY"), tag.getDouble("CZ"));
        phase = Math.max(1, tag.getInt("Phase"));
        mites.clear();
        for (Tag t : tag.getList("Mites", Tag.TAG_INT_ARRAY)) {
            mites.add(NbtUtils.loadUUID(t));
        }
        if (hasCustomName()) {
            bar.setName(getDisplayName());
        }
    }

    @Override
    public String debugInfo() {
        return super.debugInfo() + ", phase " + phase + ", cooldown " + cooldown + ", mites " + mites.size();
    }

    // ------------------------------------------------------------------------------------------------- animation
    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "main", 6, s -> {
            if (isDeadOrDying()) {
                return s.setAndContinue(A_DEATH);
            }
            return s.setAndContinue(switch (state()) {
                case BEAM_TELL -> A_BEAM_TELL;
                case BEAM -> A_BEAM;
                case WELL_TELL -> A_WELL_TELL;
                case PASS_TELL, PASS, DIVE -> A_PASS;
                case SUMMON, ECLIPSE_TELL, INTRO -> A_SUMMON;
                case EXPOSED -> A_EXPOSED;
                default -> A_SWIM;
            });
        }).triggerableAnim("roar", A_ROAR));
    }

    @Override
    protected int deathTicks() {
        return 60;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.LEVIATHAN_AMBIENT.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 200;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.LEVIATHAN_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.LEVIATHAN_DEATH.get();
    }

    @Override
    protected float getSoundVolume() {
        return 5.0F;
    }

    /** Particle helper for the encounter's ambient effects. */
    public void emit(ParticleOptions p, Vec3 at, int n, double spread) {
        particles(p, at, n, spread);
    }
}
