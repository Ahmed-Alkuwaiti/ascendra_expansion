package com.aurelia.entity;

import com.aurelia.registry.ModItems;
import com.aurelia.world.LairBuilder;
import com.aurelia.world.Realm;
import com.aurelia.world.RealmData;
import com.aurelia.world.Story;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.SmallFireball;
import net.minecraft.world.entity.projectile.WitherSkull;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * A Warden's lieutenant: a mini-boss holding a lair out in the realm. Every lieutenant shares this class; what it is and how it
 * fights come from its LieutenantKind (generated from tools/lieutenants.py): its body (walking or flying), its stats, its element
 * and the abilities it draws on from the library below. Lieutenants carry a boss bar, a cap on damage per hit and per second,
 * and enrage at half health (faster, abilities twice as often). Their deaths are counted in the realm's RealmData; the Warden's
 * altar will not wake until all of them are dead.
 */
public class Lieutenant extends Monster {
    protected final LieutenantKind kind;
    private final ServerBossEvent bossEvent;
    private int abilityTimer = 80;
    private int chargeTicks = 0;
    private int bulwarkTicks = 0;
    private boolean leaping = false;
    private boolean enraged = false;
    private double orbit;
    private float windowDamage = 0.0f;
    private int windowTicks = 0;
    @Nullable
    private BlockPos lair;

    private static final float HIT_CAP = 0.06f;
    private static final float SECOND_CAP = 0.12f;

    public Lieutenant(EntityType<? extends Lieutenant> type, Level level, LieutenantKind kind) {
        super(type, level);
        this.kind = kind;
        this.bossEvent = new ServerBossEvent(Component.translatable("entity.aurelia." + kind.id), kind.barColor(), BossEvent.BossBarOverlay.NOTCHED_6);
        this.xpReward = 300;
        this.setPersistenceRequired();
        this.orbit = this.random.nextDouble() * Math.PI * 2;
        if (kind.flying) {
            this.moveControl = new FlyingMoveControl(this, 20, true);
            this.setNoGravity(true);
        }
    }

    public static AttributeSupplier.Builder attributes(LieutenantKind kind) {
        AttributeSupplier.Builder b = Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, kind.health)
                .add(Attributes.ATTACK_DAMAGE, kind.damage)
                .add(Attributes.MOVEMENT_SPEED, kind.speed)
                .add(Attributes.FOLLOW_RANGE, 48.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.9)
                .add(Attributes.ARMOR, 8.0 + kind.realm.ordinal())
                .add(Attributes.ARMOR_TOUGHNESS, 4.0);
        if (kind.flying) {
            b.add(Attributes.FLYING_SPEED, kind.speed * 1.6);
        }
        return b;
    }

    public LieutenantKind kind() {
        return this.kind;
    }

    public void setLair(BlockPos pos) {
        this.lair = pos;
        this.restrictTo(pos, 40);
    }

    // ------------------------------------------------------------------------------------------------ behaviour
    @Override
    protected void registerGoals() {
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        if (this.isFlyingKind()) {
            return;
        }
        this.goalSelector.addGoal(1, new FloatGoal(this));
        this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.15, true));
        this.goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.7));
        this.goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 24.0f));
        this.goalSelector.addGoal(7, new RandomLookAroundGoal(this));
    }

    /** registerGoals runs inside Mob's constructor, before kind is set: read the flag off the entity type instead. */
    private boolean isFlyingKind() {
        LieutenantKind k = this.kind != null ? this.kind : LieutenantKind.byType(this.getType());
        return k != null && k.flying;
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        this.bossEvent.setProgress(this.getHealth() / this.getMaxHealth());
        if (++this.windowTicks >= 20) {
            this.windowTicks = 0;
            this.windowDamage = 0.0f;
        }
        ServerLevel level = (ServerLevel) this.level();
        if (this.tickCount % 10 == 0) {                                  // the element hangs about it
            level.sendParticles(this.particle(), getX(), getY() + getBbHeight() * 0.6, getZ(), enraged ? 6 : 2,
                    getBbWidth() * 0.6, getBbHeight() * 0.4, getBbWidth() * 0.6, 0.01);
        }
        if (!this.enraged && this.getHealth() <= this.getMaxHealth() * 0.5f) {
            this.enraged = true;
            this.playSound(SoundEvents.RAVAGER_ROAR, 3.0f, 0.6f);
            this.say(Component.translatable("entity.aurelia." + kind.id).getString() + " is enraged.");
            this.getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(kind.speed * 1.3);
            this.bulwarkTicks = 40;
        }
        if (this.bulwarkTicks > 0) {
            this.bulwarkTicks--;
            level.sendParticles(ParticleTypes.ENCHANTED_HIT, getX(), getY() + getBbHeight() / 2, getZ(), 4, getBbWidth() / 2, getBbHeight() / 3, getBbWidth() / 2, 0.05);
        }
        LivingEntity target = this.getTarget();
        if (target != null && !target.isAlive()) {
            target = null;
        }
        if (kind.flying && target != null) {
            this.orbit += enraged ? 0.08 : 0.05;
            double r = 7.0 + kind.width;
            if (this.chargeTicks > 0) {
                this.getMoveControl().setWantedPosition(target.getX(), target.getY() + 1.0, target.getZ(), 2.0);
            } else {
                this.getMoveControl().setWantedPosition(target.getX() + Math.cos(orbit) * r, target.getY() + 4.0 + Math.sin(orbit * 0.7) * 1.5,
                        target.getZ() + Math.sin(orbit) * r, 1.0);
            }
            this.getLookControl().setLookAt(target, 30.0f, 30.0f);
            if (this.distanceToSqr(target) < (kind.width + 2.0) * (kind.width + 2.0) && this.tickCount % 20 == 0) {
                this.doHurtTarget(target);
            }
        }
        if (this.chargeTicks > 0) {                                        // a charge or dive tramples whatever it meets
            this.chargeTicks--;
            for (Player p : level.getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(1.2))) {
                if (p.invulnerableTime == 0) {
                    p.hurt(this.damageSources().mobAttack(this), kind.damage * 1.2f);
                    Vec3 away = p.position().subtract(this.position()).normalize();
                    p.push(away.x * 1.6, 0.6, away.z * 1.6);
                    p.hurtMarked = true;
                    this.affect(p);
                }
            }
        }
        if (this.leaping && this.onGround() && this.tickCount % 2 == 0 && this.getDeltaMovement().y <= 0.0) {
            this.leaping = false;
            this.slam(5.0, 0.8f);
        }
        if (target != null && --this.abilityTimer <= 0) {
            this.abilityTimer = (enraged ? 50 : 90) + this.random.nextInt(30);
            Ability a = kind.abilities[this.random.nextInt(kind.abilities.length)];
            this.cast(a, target);
        }
    }

    // ------------------------------------------------------------------------------------------------ the ability library
    public enum Ability { SLAM, CHARGE, LEAP, BOLT, VOLLEY, FIREBALLS, SKULLS, SUMMON, PULL, NOVA, BLINK, ZONE, STORM, ROOT, BULWARK }

    protected void cast(Ability a, LivingEntity target) {
        ServerLevel level = (ServerLevel) this.level();
        switch (a) {
            case SLAM -> this.slam(7.0, 0.9f);
            case CHARGE -> {
                Vec3 dir = target.position().subtract(this.position()).normalize();
                this.setDeltaMovement(dir.x * 1.8, kind.flying ? dir.y * 1.2 : 0.25, dir.z * 1.8);
                this.hurtMarked = true;
                this.chargeTicks = 16;
                this.playSound(SoundEvents.RAVAGER_ROAR, 2.0f, 1.2f);
            }
            case LEAP -> {
                if (kind.flying) {
                    this.cast(Ability.CHARGE, target);
                    return;
                }
                Vec3 dir = target.position().subtract(this.position());
                double d = Math.max(1.0, dir.horizontalDistance());
                this.setDeltaMovement(dir.x / d * Math.min(1.6, d * 0.12), 1.1, dir.z / d * Math.min(1.6, d * 0.12));
                this.hurtMarked = true;
                this.leaping = true;
                this.playSound(SoundEvents.RAVAGER_STEP, 2.0f, 0.5f);
            }
            case BOLT -> this.bolt(target, 1.0f);
            case VOLLEY -> {
                for (Player p : this.players(22.0)) {
                    this.bolt(p, 0.7f);
                }
            }
            case FIREBALLS -> {
                for (int k = 0; k < 3; k++) {
                    Vec3 to = target.getEyePosition().subtract(this.getEyePosition()).add(random.nextGaussian(), random.nextGaussian() * 0.5, random.nextGaussian());
                    SmallFireball f = new SmallFireball(level, this, to.x, to.y, to.z);
                    f.setPos(this.getX(), this.getEyeY(), this.getZ());
                    level.addFreshEntity(f);
                }
                this.playSound(SoundEvents.BLAZE_SHOOT, 2.0f, 0.6f);
            }
            case SKULLS -> {
                for (int k = 0; k < 2; k++) {
                    Vec3 to = target.getEyePosition().subtract(this.getEyePosition()).add(random.nextGaussian(), 0, random.nextGaussian());
                    WitherSkull s = new WitherSkull(level, this, to.x, to.y, to.z);
                    s.setPos(this.getX(), this.getEyeY() + 0.5, this.getZ());
                    level.addFreshEntity(s);
                }
                this.playSound(SoundEvents.WITHER_SHOOT, 2.0f, 0.7f);
            }
            case SUMMON -> this.summon(target);
            case PULL -> {
                for (Player p : this.players(16.0)) {
                    Vec3 in = this.position().subtract(p.position()).normalize().scale(1.4);
                    p.push(in.x, 0.35, in.z);
                    p.hurtMarked = true;
                    p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 1));
                    this.line(p.getEyePosition(), this.getEyePosition());
                }
                this.playSound(SoundEvents.CHAIN_BREAK, 2.0f, 0.5f);
            }
            case NOVA -> {
                for (int k = 0; k < 60; k++) {
                    double t = k * Math.PI * 2 / 60;
                    level.sendParticles(this.particle(), getX() + Math.cos(t) * 6, getY() + 1, getZ() + Math.sin(t) * 6, 2, 0.2, 0.6, 0.2, 0.02);
                }
                for (Player p : this.players(8.0)) {
                    p.hurt(this.damageSources().mobAttack(this), kind.damage * 0.8f);
                    this.affect(p);
                }
                this.playSound(this.elementSound(), 3.0f, 0.6f);
            }
            case BLINK -> {
                Vec3 behind = target.position().subtract(target.getLookAngle().multiply(1, 0, 1).normalize().scale(2.5));
                level.sendParticles(ParticleTypes.REVERSE_PORTAL, getX(), getY() + 1, getZ(), 40, 0.5, 1.0, 0.5, 0.2);
                if (level.noCollision(this, this.getBoundingBox().move(behind.subtract(this.position())))) {
                    this.teleportTo(behind.x, behind.y + (kind.flying ? 1.0 : 0.0), behind.z);
                }
                this.lookAt(target, 360f, 360f);
                target.hurt(this.damageSources().mobAttack(this), kind.damage * 1.1f);
                this.affect(target);
                this.playSound(SoundEvents.ENDERMAN_TELEPORT, 2.0f, 0.6f);
            }
            case ZONE -> {
                AreaEffectCloud cloud = new AreaEffectCloud(level, target.getX(), target.getY(), target.getZ());
                cloud.setOwner(this);
                cloud.setRadius(4.5f);
                cloud.setDuration(140);
                cloud.setRadiusPerTick(-0.01f);
                cloud.setParticle(this.particle());
                cloud.addEffect(this.zoneEffect());
                level.addFreshEntity(cloud);
                this.playSound(SoundEvents.SPLASH_POTION_BREAK, 2.0f, 0.5f);
            }
            case STORM -> {
                for (Player p : this.players(20.0)) {
                    LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(level);
                    if (bolt != null) {
                        bolt.moveTo(p.getX(), p.getY(), p.getZ());
                        bolt.setVisualOnly(true);
                        level.addFreshEntity(bolt);
                    }
                    p.hurt(this.damageSources().lightningBolt(), kind.damage * 0.7f);
                }
            }
            case ROOT -> {
                for (Player p : this.players(12.0)) {
                    p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 5));
                    p.addEffect(new MobEffectInstance(MobEffects.JUMP, 60, 128));         // jump boost 129 cancels jumping
                    level.sendParticles(this.particle(), p.getX(), p.getY() + 0.2, p.getZ(), 30, 0.5, 0.1, 0.5, 0.02);
                }
                this.playSound(this.elementSound(), 2.0f, 0.4f);
            }
            case BULWARK -> {
                this.bulwarkTicks = 80;
                this.playSound(SoundEvents.IRON_GOLEM_REPAIR, 2.0f, 0.5f);
            }
        }
    }

    /** A shockwave: everyone within r is hurt, thrown up and away, and given the element's effect. */
    private void slam(double r, float scale) {
        ServerLevel level = (ServerLevel) this.level();
        for (int k = 0; k < 48; k++) {
            double t = k * Math.PI * 2 / 48;
            level.sendParticles(ParticleTypes.EXPLOSION, getX() + Math.cos(t) * r * 0.7, getY() + 0.2, getZ() + Math.sin(t) * r * 0.7, 1, 0, 0, 0, 0);
            level.sendParticles(this.particle(), getX() + Math.cos(t) * r, getY() + 0.3, getZ() + Math.sin(t) * r, 2, 0.1, 0.2, 0.1, 0.02);
        }
        for (Player p : this.players(r)) {
            p.hurt(this.damageSources().mobAttack(this), kind.damage * scale);
            Vec3 away = p.position().subtract(this.position()).multiply(1, 0, 1).normalize();
            p.push(away.x * 1.2, 0.8, away.z * 1.2);
            p.hurtMarked = true;
            this.affect(p);
        }
        this.playSound(SoundEvents.GENERIC_EXPLODE, 2.5f, 0.6f);
    }

    /** A bolt of the element, drawn from the eyes to the target; it lands if nothing solid is in the way. */
    private void bolt(LivingEntity target, float scale) {
        Vec3 from = this.getEyePosition();
        Vec3 to = target.getEyePosition();
        HitResult hit = this.level().clip(new ClipContext(from, to, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this));
        this.line(from, hit.getLocation());
        if (hit.getType() == HitResult.Type.MISS) {
            target.hurt(this.damageSources().indirectMagic(this, this), kind.damage * scale);
            this.affect(target);
        }
        this.playSound(this.elementSound(), 1.5f, 1.4f);
    }

    private void line(Vec3 from, Vec3 to) {
        ServerLevel level = (ServerLevel) this.level();
        Vec3 d = to.subtract(from);
        int n = (int) (d.length() * 2);
        for (int i = 0; i <= n; i++) {
            Vec3 p = from.add(d.scale(i / (double) Math.max(1, n)));
            level.sendParticles(this.particle(), p.x, p.y, p.z, 1, 0.02, 0.02, 0.02, 0.0);
        }
    }

    private void summon(LivingEntity target) {
        if (kind.minion == null) {
            this.cast(Ability.NOVA, target);
            return;
        }
        EntityType<?> type = ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(kind.minion));
        if (type == null) {
            return;
        }
        ServerLevel level = (ServerLevel) this.level();
        int near = level.getEntities(type, this.getBoundingBox().inflate(24), e -> e.isAlive()).size();
        for (int k = near; k < Math.min(6, near + 3); k++) {
            Entity e = type.create(level);
            if (!(e instanceof Mob m)) {
                return;
            }
            double a = this.random.nextDouble() * Math.PI * 2;
            m.moveTo(getX() + Math.cos(a) * 4, getY() + 0.5, getZ() + Math.sin(a) * 4, this.random.nextFloat() * 360, 0);
            m.finalizeSpawn(level, level.getCurrentDifficultyAt(m.blockPosition()), MobSpawnType.MOB_SUMMONED, null, null);
            m.setTarget(target);
            level.addFreshEntity(m);
            level.sendParticles(this.particle(), m.getX(), m.getY() + 1, m.getZ(), 20, 0.4, 0.8, 0.4, 0.05);
        }
        this.playSound(SoundEvents.EVOKER_PREPARE_SUMMON, 2.0f, 0.6f);
    }

    private List<Player> players(double r) {
        return this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(r), p -> p.isAlive() && !p.isSpectator() && !p.isCreative());
    }

    // ------------------------------------------------------------------------------------------------ the element
    private ParticleOptions particle() {
        return switch (kind.realm) {
            case GROVE -> ParticleTypes.COMPOSTER;
            case SKYREACH -> ParticleTypes.ELECTRIC_SPARK;
            case HOLLOW -> ParticleTypes.SOUL_FIRE_FLAME;
            case DROWNED -> ParticleTypes.SPLASH;
            case PALE -> ParticleTypes.SNOWFLAKE;
            case SCARLET -> ParticleTypes.FLAME;
            case CLOCKWORK -> ParticleTypes.REVERSE_PORTAL;
            case MYCELIAL -> ParticleTypes.SPORE_BLOSSOM_AIR;
            default -> ParticleTypes.END_ROD;
        };
    }

    private SoundEvent elementSound() {
        return switch (kind.realm) {
            case GROVE -> SoundEvents.ROOTED_DIRT_BREAK;
            case SKYREACH -> SoundEvents.TRIDENT_THUNDER;
            case HOLLOW -> SoundEvents.BLAZE_SHOOT;
            case DROWNED -> SoundEvents.ELDER_GUARDIAN_CURSE;
            case PALE -> SoundEvents.GLASS_BREAK;
            case SCARLET -> SoundEvents.FIRECHARGE_USE;
            case CLOCKWORK -> SoundEvents.BELL_BLOCK;
            case MYCELIAL -> SoundEvents.MOSS_BREAK;
            default -> SoundEvents.WARDEN_SONIC_BOOM;
        };
    }

    /** What the element does to whatever it touches. */
    private void affect(LivingEntity e) {
        switch (kind.realm) {
            case GROVE -> {
                e.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 1));
                e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 1));
            }
            case SKYREACH -> e.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 20, 1));
            case HOLLOW -> {
                e.setSecondsOnFire(5);
                e.addEffect(new MobEffectInstance(MobEffects.WITHER, 60, 0));
            }
            case DROWNED -> {
                e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 2));
                e.setAirSupply(Math.max(0, e.getAirSupply() - 100));
            }
            case PALE -> {
                e.setTicksFrozen(e.getTicksRequiredToFreeze() + 100);
                e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 2));
            }
            case SCARLET -> {
                e.setSecondsOnFire(4);
                e.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 80, 0));
            }
            case CLOCKWORK -> {
                e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 3));
                e.addEffect(new MobEffectInstance(MobEffects.DIG_SLOWDOWN, 80, 1));
            }
            case MYCELIAL -> {
                e.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 1));
                e.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 100, 0));
            }
            default -> {
                e.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 80, 0));
                e.addEffect(new MobEffectInstance(MobEffects.WITHER, 60, 1));
            }
        }
    }

    private MobEffectInstance zoneEffect() {
        return switch (kind.realm) {
            case GROVE, MYCELIAL -> new MobEffectInstance(MobEffects.POISON, 60, 1);
            case HOLLOW, LAST -> new MobEffectInstance(MobEffects.WITHER, 60, 1);
            case SCARLET -> new MobEffectInstance(MobEffects.HARM, 1, 0);
            default -> new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 2);
        };
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && target instanceof LivingEntity e) {
            this.affect(e);
        }
        return hit;
    }

    // ------------------------------------------------------------------------------------------------ damage, death and loot
    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean bypass = source.is(DamageTypeTags.BYPASSES_INVULNERABILITY);
        if (!bypass) {
            if (this.bulwarkTicks > 0) {
                amount *= 0.3f;
            }
            amount = Math.min(amount, this.getMaxHealth() * HIT_CAP);
            float room = this.getMaxHealth() * SECOND_CAP - this.windowDamage;
            if (room <= 0.0f) {
                this.playSound(SoundEvents.SHIELD_BLOCK, 1.0f, 0.8f);
                return false;
            }
            amount = Math.min(amount, room);
        }
        boolean hit = super.hurt(source, amount);
        if (hit && !bypass) {
            this.windowDamage += amount;
        }
        return hit;
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    protected void dropCustomDeathLoot(DamageSource source, int looting, boolean recentlyHit) {
        super.dropCustomDeathLoot(source, looting, recentlyHit);
        Item[] loot = ModItems.lieutenantLoot(kind.realm);
        this.drop(new ItemStack(loot[0], 4 + this.random.nextInt(5) + looting));
        this.drop(new ItemStack(loot[1], 1 + this.random.nextInt(2)));
        Item trophy = com.aurelia.registry.ExtraContent.trophy(kind);      // and always its trophy, for the realm's charm
        if (trophy != null) {
            this.drop(new ItemStack(trophy));
        }
    }

    private void drop(ItemStack stack) {
        ItemEntity item = new ItemEntity(this.level(), getX(), getY() + 1.0, getZ(), stack);
        item.setGlowingTag(true);
        item.setDefaultPickUpDelay();
        this.level().addFreshEntity(item);
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        if (this.level() instanceof ServerLevel level) {
            this.say(kind.deathLine);
            LairBuilder.onLieutenantSlain(level, kind);
        }
    }

    public void awaken() {
        this.say(kind.awakenLine);
        for (ServerPlayer p : this.level().getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(48))) {
            Story.title(p, Component.translatable("entity.aurelia." + kind.id).getString(), kind.title, kind.realm.color);
        }
        this.playSound(SoundEvents.WITHER_SPAWN, 2.0f, 1.2f);
    }

    private void say(String text) {
        for (Player p : this.level().getEntitiesOfClass(Player.class, this.getBoundingBox().inflate(64.0))) {
            Story.narrate(p, text);
        }
    }

    // ------------------------------------------------------------------------------------------------ boss bar plumbing
    @Override
    public void startSeenByPlayer(ServerPlayer player) {
        super.startSeenByPlayer(player);
        this.bossEvent.addPlayer(player);
    }

    @Override
    public void stopSeenByPlayer(ServerPlayer player) {
        super.stopSeenByPlayer(player);
        this.bossEvent.removePlayer(player);
    }

    @Override
    public void remove(Entity.RemovalReason reason) {
        super.remove(reason);
        this.bossEvent.removeAllPlayers();
    }

    @Override
    protected boolean shouldDespawnInPeaceful() {
        return false;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("Enraged", this.enraged);
        if (this.lair != null) {
            tag.putLong("Lair", this.lair.asLong());
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        this.enraged = tag.getBoolean("Enraged");
        if (tag.contains("Lair")) {
            this.setLair(BlockPos.of(tag.getLong("Lair")));
        }
    }
}
