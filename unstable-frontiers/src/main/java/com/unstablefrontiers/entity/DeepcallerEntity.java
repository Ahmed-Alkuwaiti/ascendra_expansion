package com.unstablefrontiers.entity;

import com.unstablefrontiers.drowned.DeepcallerEncounter;
import com.unstablefrontiers.registry.ModEntities;
import com.unstablefrontiers.registry.ModSounds;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import net.minecraft.ChatFormatting;
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
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.RawAnimation;

/**
 * The Deepcaller, fought in the Sunless Vault's flooded dome. It swims the whole dome, above, below and around you, and every
 * attack is shown first:
 * <ul>
 * <li><b>Lure Flash</b>: its lure swells and brightens, with a rising whine (1.5 s). Anyone looking at the lure when it
 * flashes is dazed (slowed and weakened for 3 s). Look away, or put a pillar between you.</li>
 * <li><b>Charge</b>: it rears back and a trail of bubbles marks its path (1.25 s; the path is fixed half way through), then
 * it rams along it. If it hits a pillar or the wall, it is stunned on the floor for five seconds and takes double damage.</li>
 * <li><b>Undertow</b>: water spirals in toward it (1.5 s), then for four seconds it drags everyone in the dome gently
 * toward it, and anyone right beside it is hurt. Swim against the pull.</li>
 * <li><b>Brood</b> (second half): two young Murkjaws, never more than three alive.</li>
 * </ul>
 * At half health it roars (half damage while it does), charges twice in a row and adds its brood. It never leaves the dome,
 * and nothing it does stops you breathing: the dome has breath vents.
 */
public class DeepcallerEntity extends AnimatedMonster {
    public static final int INTRO = 0, DRIFT = 1, LURE_TELL = 2, LURE_FLASH = 3, CHARGE_TELL = 4, CHARGE = 5, STUNNED = 6,
            VORTEX_TELL = 7, VORTEX = 8, BROOD = 9, ROAR = 10;
    private static final int INTRO_TICKS = 60, LURE_TELL_TICKS = 30, CHARGE_TELL_TICKS = 25, CHARGE_LOCK = 13, STUN_TICKS = 100,
            VORTEX_TELL_TICKS = 30, VORTEX_TICKS = 80, BROOD_TICKS = 30, ROAR_TICKS = 40;
    public static final int MAX_BROOD = 3;
    private static final RawAnimation A_SWIM = RawAnimation.begin().thenLoop("animation.deepcaller.swim");
    private static final RawAnimation A_LURE_TELL = RawAnimation.begin().thenPlayAndHold("animation.deepcaller.lure_tell");
    private static final RawAnimation A_LURE_FLASH = RawAnimation.begin().thenPlay("animation.deepcaller.lure_flash");
    private static final RawAnimation A_CHARGE_TELL = RawAnimation.begin().thenPlayAndHold("animation.deepcaller.charge_tell");
    private static final RawAnimation A_CHARGE = RawAnimation.begin().thenLoop("animation.deepcaller.charge");
    private static final RawAnimation A_STUNNED = RawAnimation.begin().thenLoop("animation.deepcaller.stunned");
    private static final RawAnimation A_VORTEX = RawAnimation.begin().thenLoop("animation.deepcaller.vortex");
    private static final RawAnimation A_BROOD = RawAnimation.begin().thenPlayAndHold("animation.deepcaller.brood");
    private static final RawAnimation A_ROAR = RawAnimation.begin().thenPlay("animation.deepcaller.roar").thenLoop("animation.deepcaller.swim");
    private static final RawAnimation A_DEATH = RawAnimation.begin().thenPlayAndHold("animation.deepcaller.death");

    private final ServerBossEvent bar = (ServerBossEvent) new ServerBossEvent(Component.translatable("entity.unstable_frontiers.deepcaller")
            .withStyle(ChatFormatting.DARK_AQUA), BossEvent.BossBarColor.BLUE, BossEvent.BossBarOverlay.NOTCHED_10).setDarkenScreen(false);
    private Vec3 center = Vec3.ZERO;
    private int phase = 1;
    private int cooldown = 40;
    private int cycle;
    private int charges;
    private double orbit;
    private Vec3 dir = Vec3.ZERO;
    private Vec3 chargeFrom = Vec3.ZERO;
    private final Set<UUID> hitThisCharge = new HashSet<>();
    private final List<UUID> brood = new ArrayList<>();
    /** Continuous-integration only: stand-ins (no real players on the test server) treated as divers. */
    public static final List<LivingEntity> TRIAL_TARGETS = new ArrayList<>();

    public DeepcallerEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        xpReward = 400;
        setNoGravity(true);
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 600.0D)
                .add(Attributes.ATTACK_DAMAGE, 16.0D)
                .add(Attributes.ARMOR, 10.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 3.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D)
                .add(Attributes.FOLLOW_RANGE, 48.0D);
    }

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

    public List<UUID> brood() {
        return brood;
    }

    @Override
    protected void registerGoals() {
    }

    @Override
    public boolean canBreatheUnderwater() {
        return true;
    }

    /** Divers in the dome. */
    public List<LivingEntity> divers() {
        List<LivingEntity> out = new ArrayList<>();
        if (level() instanceof ServerLevel sl) {
            for (ServerPlayer p : sl.players()) {
                if (p.isAlive() && !p.isSpectator() && !p.isCreative() && DeepcallerEncounter.inArena(center, p.position())) {
                    out.add(p);
                }
            }
        }
        TRIAL_TARGETS.removeIf(e -> !e.isAlive());
        out.addAll(TRIAL_TARGETS);
        return out;
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (center == Vec3.ZERO) {
            setCenter(position());
        }
        bar.setProgress(getHealth() / getMaxHealth());
        cooldown--;
        List<LivingEntity> divers = divers();
        switch (state()) {
            case INTRO -> {
                moveTo(center.add(0, -14 + 14 * Math.min(1, stateTicks / (double) INTRO_TICKS), 0), 0.5D);
                if (stateTicks == 1) {
                    sound(ModSounds.DEEPCALLER_ROAR.get(), 5.0F, 0.6F);
                }
                if (stateTicks >= INTRO_TICKS) {
                    setState(DRIFT);
                    cooldown = 30;
                }
            }
            case DRIFT -> drift(divers);
            case LURE_TELL -> lureTell(divers);
            case LURE_FLASH -> {
                if (stateTicks >= 10) {
                    setState(DRIFT);
                    cooldown = 45;
                }
            }
            case CHARGE_TELL -> chargeTell(divers);
            case CHARGE -> charge();
            case STUNNED -> {
                setDeltaMovement(getDeltaMovement().scale(0.7D).add(0, -0.03D, 0));
                if (stateTicks % 10 == 0) {
                    particles(ParticleTypes.BUBBLE, position().add(0, 1, 0), 8, 1.2D);
                }
                if (stateTicks >= STUN_TICKS) {
                    setState(DRIFT);
                    cooldown = 30;
                }
            }
            case VORTEX_TELL -> {
                moveTo(center, 0.4D);
                if (stateTicks % 3 == 0) {
                    spiral(stateTicks);
                }
                if (stateTicks >= VORTEX_TELL_TICKS) {
                    setState(VORTEX);
                    sound(ModSounds.DEEPCALLER_VORTEX.get(), 4.0F, 1.0F);
                }
            }
            case VORTEX -> vortex(divers);
            case BROOD -> brood();
            case ROAR -> {
                setDeltaMovement(getDeltaMovement().scale(0.8D));
                if (stateTicks == 1) {
                    triggerAnim("main", "roar");
                    sound(ModSounds.DEEPCALLER_ROAR.get(), 5.0F, 0.9F);
                }
                if (stateTicks >= ROAR_TICKS) {
                    setState(DRIFT);
                    cooldown = 30;
                }
            }
            default -> {
            }
        }
        if (state() != CHARGE && state() != CHARGE_TELL && state() != STUNNED) {
            Vec3 v = getDeltaMovement();
            if (v.lengthSqr() > 0.003D) {
                face(position().add(v));
            }
        }
    }

    private void drift(List<LivingEntity> divers) {
        orbit += phase == 2 ? 0.014D : 0.010D;
        double r = 12;
        moveTo(center.add(Math.cos(orbit) * r, Math.sin(orbit * 2.3) * 6, Math.sin(orbit) * r), 0.35D);
        if (cooldown > 0 || divers.isEmpty()) {
            return;
        }
        int[] plan = phase == 1 ? new int[] {CHARGE_TELL, LURE_TELL, CHARGE_TELL, VORTEX_TELL}
                : new int[] {CHARGE_TELL, BROOD, LURE_TELL, VORTEX_TELL, CHARGE_TELL};
        int next = plan[cycle++ % plan.length];
        if (next == BROOD && liveBrood() >= MAX_BROOD) {
            next = LURE_TELL;
        }
        if (next == CHARGE_TELL) {
            charges = phase == 2 ? 2 : 1;
        }
        start(next, divers);
    }

    private void start(int s, List<LivingEntity> divers) {
        setState(s);
        switch (s) {
            case LURE_TELL -> {
                sound(ModSounds.DEEPCALLER_LURE.get(), 4.0F, 1.0F);
                tell(divers, "lure");
            }
            case CHARGE_TELL -> {
                sound(ModSounds.DEEPCALLER_CHARGE_TELL.get(), 4.0F, 1.0F);
                tell(divers, "charge");
            }
            case VORTEX_TELL -> tell(divers, "vortex");
            case BROOD -> sound(ModSounds.DEEPCALLER_BROOD.get(), 4.0F, 1.0F);
            default -> {
            }
        }
    }

    private void tell(List<LivingEntity> divers, String attack) {
        for (LivingEntity e : divers) {
            if (e instanceof ServerPlayer p) {
                p.displayClientMessage(Component.translatable("boss.unstable_frontiers.deepcaller." + attack).withStyle(ChatFormatting.YELLOW), true);
            }
        }
    }

    public Vec3 lure() {
        return position().add(Vec3.directionFromRotation(-20, getYRot()).scale(3.4D)).add(0, 2.2D, 0);
    }

    private void lureTell(List<LivingEntity> divers) {
        setDeltaMovement(getDeltaMovement().scale(0.8D));
        LivingEntity t = nearest(divers);
        if (t != null) {
            face(t.position());
        }
        if (stateTicks % 2 == 0) {
            particles(ParticleTypes.GLOW, lure(), 2 + stateTicks / 6, 0.2D + stateTicks * 0.01D);
        }
        if (stateTicks >= LURE_TELL_TICKS) {
            Vec3 l = lure();
            particles(ParticleTypes.FLASH, l, 1, 0.0D);
            particles(ParticleTypes.END_ROD, l, 30, 1.5D);
            for (LivingEntity e : divers) {
                Vec3 to = l.subtract(e.getEyePosition()).normalize();
                boolean looking = e.getLookAngle().dot(to) > 0.55D;
                boolean clear = level().clip(new ClipContext(e.getEyePosition(), l, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, e))
                        .getType() == HitResult.Type.MISS;
                if (looking && clear && e.distanceTo(this) < 36) {
                    e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 2));
                    e.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 60, 1));
                    e.hurt(damageSources().indirectMagic(this, this), 4.0F);
                }
            }
            setState(LURE_FLASH);
            triggerAnim("main", "flash");
        }
    }

    private void chargeTell(List<LivingEntity> divers) {
        setDeltaMovement(getDeltaMovement().scale(0.75D));
        LivingEntity t = nearest(divers);
        if (t != null && stateTicks <= CHARGE_LOCK) {
            dir = t.position().add(0, t.getBbHeight() / 2, 0).subtract(position().add(0, getBbHeight() / 2, 0)).normalize();
            face(t.position());
        }
        if (stateTicks % 2 == 0) {
            Vec3 from = position().add(0, getBbHeight() / 2, 0);
            line(ParticleTypes.BUBBLE, from, from.add(dir.scale(30)), 1.0D);
        }
        if (stateTicks >= CHARGE_TELL_TICKS) {
            chargeFrom = position();
            hitThisCharge.clear();
            setState(CHARGE);
            sound(ModSounds.DEEPCALLER_CHARGE.get(), 5.0F, 1.0F);
        }
    }

    private void charge() {
        setDeltaMovement(dir.scale(1.3D));
        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(0.8D), this::harmable)) {
            if (hitThisCharge.add(e.getUUID())) {
                e.hurt(damageSources().mobAttack(this), attack() * 1.3F);
                Vec3 side = new Vec3(-dir.z, 0, dir.x).scale(0.6D);
                e.setDeltaMovement(side.x, 0.2D, side.z);     // shouldered aside, never pinned
                e.hurtMarked = true;
            }
        }
        if (horizontalCollision || verticalCollision && stateTicks > 3) {
            setState(STUNNED);
            setDeltaMovement(dir.scale(-0.3D));
            sound(ModSounds.DEEPCALLER_SLAM.get(), 5.0F, 1.0F);
            particles(ParticleTypes.EXPLOSION, position().add(dir.scale(2)), 3, 1.0D);
            return;
        }
        boolean far = position().distanceTo(chargeFrom) > 30 || Math.hypot(getX() - center.x, getZ() - center.z) > DeepcallerEncounter.ARENA_RADIUS - 2;
        if (stateTicks >= 30 || far) {
            if (--charges > 0) {
                setState(CHARGE_TELL);
            } else {
                setState(DRIFT);
                cooldown = 40;
            }
        }
    }

    private void spiral(int t) {
        if (level() instanceof ServerLevel sl) {
            for (int k = 0; k < 3; k++) {
                double a = t * 0.3D + k * Math.PI * 2 / 3;
                double r = 14 - t * 0.35D;
                sl.sendParticles(ParticleTypes.BUBBLE, center.x + Math.cos(a) * r, center.y + (k - 1) * 3, center.z + Math.sin(a) * r, 2, 0.2, 0.2, 0.2, 0.0);
            }
        }
    }

    private void vortex(List<LivingEntity> divers) {
        setDeltaMovement(getDeltaMovement().scale(0.5D));
        setYRot(getYRot() + 12);
        yBodyRot = getYRot();
        if (stateTicks % 3 == 0) {
            spiral(stateTicks + 30);
        }
        for (LivingEntity e : divers) {
            Vec3 in = position().subtract(e.position());
            double d = in.length();
            if (d > 0.5D) {
                Vec3 pull = in.normalize().scale(phase == 2 ? 0.055D : 0.045D);
                e.setDeltaMovement(e.getDeltaMovement().add(pull));
                e.hurtMarked = true;
            }
            if (d < 4.5D && stateTicks % 20 == 0) {
                e.hurt(damageSources().mobAttack(this), attack() * 0.35F);
            }
        }
        if (stateTicks >= VORTEX_TICKS) {
            setState(DRIFT);
            cooldown = 50;
        }
    }

    private void brood() {
        setDeltaMovement(getDeltaMovement().scale(0.8D));
        if (stateTicks == 15 && level() instanceof ServerLevel sl) {
            int want = Math.min(2, MAX_BROOD - liveBrood());
            for (int i = 0; i < want; i++) {
                MurkjawEntity m = ModEntities.MURKJAW.get().create(sl);
                if (m == null) {
                    continue;
                }
                double a = random.nextDouble() * Math.PI * 2;
                m.moveTo(center.x + Math.cos(a) * 8, center.y, center.z + Math.sin(a) * 8, 0, 0);
                m.getAttribute(Attributes.MAX_HEALTH).setBaseValue(m.getAttribute(Attributes.MAX_HEALTH).getBaseValue() * 0.6D);
                m.setHealth(m.getMaxHealth());
                m.setPersistenceRequired();
                m.getPersistentData().putBoolean(DeepcallerEncounter.ADD_TAG, true);
                sl.addFreshEntity(m);
                brood.add(m.getUUID());
                particles(ParticleTypes.BUBBLE_POP, m.position(), 12, 0.6D);
            }
        }
        if (stateTicks >= BROOD_TICKS) {
            setState(DRIFT);
            cooldown = 40;
        }
    }

    private int liveBrood() {
        if (!(level() instanceof ServerLevel sl)) {
            return 0;
        }
        brood.removeIf(id -> !(sl.getEntity(id) instanceof Mob m) || !m.isAlive());
        return brood.size();
    }

    private LivingEntity nearest(List<LivingEntity> divers) {
        LivingEntity best = null;
        double bd = Double.MAX_VALUE;
        for (LivingEntity e : divers) {
            double d = e.distanceToSqr(this);
            if (d < bd) {
                bd = d;
                best = e;
            }
        }
        return best;
    }

    private boolean harmable(LivingEntity e) {
        return e != this && e.isAlive() && !(e instanceof MurkjawEntity) && !(e instanceof Player p && (p.isCreative() || p.isSpectator()));
    }

    private float attack() {
        return (float) getAttributeValue(Attributes.ATTACK_DAMAGE);
    }

    private void moveTo(Vec3 at, double speed) {
        // never leave the dome
        Vec3 off = at.subtract(center);
        double flat = Math.hypot(off.x, off.z);
        if (flat > DeepcallerEncounter.ARENA_RADIUS - 4) {
            off = new Vec3(off.x * (DeepcallerEncounter.ARENA_RADIUS - 4) / flat, off.y, off.z * (DeepcallerEncounter.ARENA_RADIUS - 4) / flat);
            at = center.add(off);
        }
        Vec3 d = at.subtract(position());
        Vec3 want = d.lengthSqr() > 1 ? d.normalize().scale(speed) : d.scale(speed);
        setDeltaMovement(getDeltaMovement().scale(0.85D).add(want.scale(0.15D)));
    }

    private void face(Vec3 at) {
        Vec3 d = at.subtract(position());
        setYRot((float) Math.toDegrees(Math.atan2(-d.x, d.z)));
        yBodyRot = getYRot();
        yHeadRot = getYRot();
    }

    @Override
    public void travel(Vec3 input) {
        move(MoverType.SELF, getDeltaMovement());
        if (!isAlive()) {
            setDeltaMovement(getDeltaMovement().add(0, -0.01D, 0).scale(0.9D));
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

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.is(DamageTypes.GENERIC_KILL) || source.is(DamageTypes.FELL_OUT_OF_WORLD) && position().y < -64) {
            return super.hurt(source, amount);
        }
        if (state() == INTRO || source.is(DamageTypes.IN_WALL) || source.is(DamageTypes.DROWN) || source.getEntity() instanceof MurkjawEntity
                || source.getEntity() == this) {
            return false;
        }
        if (state() == STUNNED) {
            amount *= 2.0F;
            particles(ParticleTypes.CRIT, position().add(0, 1.0D, 0), 10, 1.2D);
        } else if (state() == ROAR) {
            amount *= 0.5F;
        }
        float before = getHealth();
        boolean hurt = super.hurt(source, amount);
        if (hurt && isAlive() && phase == 1 && getHealth() / getMaxHealth() <= 0.5F && before / getMaxHealth() > 0.5F) {
            phase = 2;
            cycle = 0;
            setState(ROAR);
            for (LivingEntity e : divers()) {
                if (e instanceof ServerPlayer p) {
                    p.displayClientMessage(Component.translatable("boss.unstable_frontiers.deepcaller.phase2").withStyle(ChatFormatting.DARK_AQUA), false);
                }
            }
        }
        return hurt;
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        if (level() instanceof ServerLevel sl) {
            DeepcallerEncounter.victory(sl, this);
        }
    }

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
        for (UUID u : brood) {
            ids.add(NbtUtils.createUUID(u));
        }
        tag.put("Brood", ids);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        center = new Vec3(tag.getDouble("CX"), tag.getDouble("CY"), tag.getDouble("CZ"));
        phase = Math.max(1, tag.getInt("Phase"));
        brood.clear();
        for (Tag t : tag.getList("Brood", Tag.TAG_INT_ARRAY)) {
            brood.add(NbtUtils.loadUUID(t));
        }
    }

    @Override
    public String debugInfo() {
        return super.debugInfo() + ", phase " + phase + ", cooldown " + cooldown + ", brood " + brood.size();
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "main", 5, s -> {
            if (isDeadOrDying()) {
                return s.setAndContinue(A_DEATH);
            }
            return s.setAndContinue(switch (state()) {
                case LURE_TELL -> A_LURE_TELL;
                case CHARGE_TELL -> A_CHARGE_TELL;
                case CHARGE -> A_CHARGE;
                case STUNNED -> A_STUNNED;
                case VORTEX_TELL, VORTEX -> A_VORTEX;
                case BROOD, INTRO -> A_BROOD;
                default -> A_SWIM;
            });
        }).triggerableAnim("roar", A_ROAR).triggerableAnim("flash", A_LURE_FLASH));
    }

    @Override
    protected int deathTicks() {
        return 50;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.DEEPCALLER_AMBIENT.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 200;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.DEEPCALLER_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.DEEPCALLER_DEATH.get();
    }

    @Override
    protected float getSoundVolume() {
        return 4.0F;
    }
}
