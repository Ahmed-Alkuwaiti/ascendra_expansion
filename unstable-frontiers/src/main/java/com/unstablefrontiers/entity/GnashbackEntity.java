package com.unstablefrontiers.entity;

import com.unstablefrontiers.registry.ModSounds;
import java.util.EnumSet;
import javax.annotation.Nullable;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.PlayState;
import software.bernie.geckolib.animation.RawAnimation;

/**
 * The Gnashback: a giant, territorial beetle of the Gnashwood, its shell grown around old cage bars.
 *
 * <p>It ignores you until you come within about ten blocks (or hit it). Close in, it bites. At range it charges: it
 * lowers its head, cracks its shell open and scrapes the ground for over a second (the tell), then runs in a straight
 * line. It fixes that line half a second before it runs, so stepping aside in the last half of the tell is the dodge. Step aside and let it hit a wall or a tree, and it stuns itself for several seconds with
 * its soft back exposed: it takes double damage and cannot fight back. A charge that hits you is brutal.
 */
public class GnashbackEntity extends AnimatedMonster {
    public static final int IDLE = 0, TELL = 1, CHARGE = 2, STUNNED = 3;
    private static final int TELL_TICKS = 25;
    /** When in the tell it fixes its line (half a second before it runs): after this, stepping aside is the dodge. */
    private static final int AIM_TICKS = 15;
    private static final int CHARGE_TICKS = 40;
    private static final int STUN_TICKS = 80;

    private static final RawAnimation A_IDLE = RawAnimation.begin().thenLoop("animation.gnashback.idle");
    private static final RawAnimation A_WALK = RawAnimation.begin().thenLoop("animation.gnashback.walk");
    private static final RawAnimation A_TELL = RawAnimation.begin().thenPlayAndHold("animation.gnashback.charge_tell");
    private static final RawAnimation A_CHARGE = RawAnimation.begin().thenLoop("animation.gnashback.charge");
    private static final RawAnimation A_STUNNED = RawAnimation.begin().thenLoop("animation.gnashback.stunned");
    private static final RawAnimation A_DEATH = RawAnimation.begin().thenPlayAndHold("animation.gnashback.death");
    private static final RawAnimation A_BITE = RawAnimation.begin().thenPlay("animation.gnashback.bite");

    private int chargeCooldown = 20;
    private Vec3 chargeDir = Vec3.ZERO;

    public GnashbackEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        xpReward = 25;
    }

    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 110.0D)
                .add(Attributes.ATTACK_DAMAGE, 12.0D)
                .add(Attributes.ARMOR, 10.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 4.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.24D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.9D)
                .add(Attributes.FOLLOW_RANGE, 24.0D)
                .add(Attributes.STEP_HEIGHT, 1.5D)
                .add(Attributes.ATTACK_KNOCKBACK, 1.0D);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new ChargeGoal());
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.15D, false) {
            @Override
            public boolean canUse() {
                return state() == IDLE && super.canUse();
            }

            @Override
            public boolean canContinueToUse() {
                return state() == IDLE && super.canContinueToUse();
            }
        });
        goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.8D));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 12.0F));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        // territorial: it only notices players who come close
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false, p -> p.distanceToSqr(this) < 11 * 11));
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit) {
            triggerAnim("attack", "bite");
            sound(ModSounds.GNASHBACK_BITE.get(), 1.0F, 0.9F + random.nextFloat() * 0.2F);
        }
        return hit;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (state() == STUNNED) {
            amount *= 2.0F;   // the soft back is exposed
            particles(ParticleTypes.CRIT, position().add(0, 1.6D, 0), 10, 0.8D);
        }
        return super.hurt(source, amount);
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (!level().isClientSide && state() == STUNNED) {
            getNavigation().stop();
            if (stateTicks % 10 == 0) {
                particles(ParticleTypes.CRIT, position().add(0, 2.2D, 0), 4, 0.4D);
            }
            if (stateTicks >= STUN_TICKS) {
                setState(IDLE);
            }
        }
        if (chargeCooldown > 0) {
            chargeCooldown--;
        }
    }

    @Override
    public String debugInfo() {
        return super.debugInfo() + ", charge cooldown " + chargeCooldown + ", goals " + goalSelector.getAvailableGoals().stream()
                .filter(net.minecraft.world.entity.ai.goal.WrappedGoal::isRunning).map(w -> w.getGoal().getClass().getSimpleName()).toList();
    }

    @Override
    public boolean isImmobile() {
        return super.isImmobile() || state() == STUNNED;
    }

    /** The tell, the straight-line run, and what it hits. */
    private class ChargeGoal extends Goal {
        ChargeGoal() {
            setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
        }

        @Override
        public boolean canUse() {
            LivingEntity t = getTarget();
            if (t == null || !t.isAlive() || chargeCooldown > 0 || state() != IDLE || !onGround()) {
                return false;
            }
            double d = distanceToSqr(t);
            return d > 5 * 5 && d < 18 * 18 && hasLineOfSight(t);
        }

        @Override
        public boolean canContinueToUse() {
            return state() == TELL || state() == CHARGE;
        }

        @Override
        public void start() {
            getNavigation().stop();
            chargeDir = Vec3.ZERO;
            setState(TELL);
            sound(ModSounds.GNASHBACK_SCRAPE.get(), 1.6F, 1.0F);
        }

        @Override
        public void tick() {
            LivingEntity t = getTarget();
            if (state() == TELL) {
                if (t != null && stateTicks <= AIM_TICKS) {
                    getLookControl().setLookAt(t, 30.0F, 30.0F);
                    lookAtTarget(t);
                    Vec3 to = t.position().subtract(position());
                    chargeDir = new Vec3(to.x, 0, to.z).normalize();
                }
                if (stateTicks % 4 == 0) {
                    BlockState ground = level().getBlockState(blockPosition().below());
                    particles(new BlockParticleOption(ParticleTypes.BLOCK, ground), position().add(getLookAngle().scale(1.5D)), 8, 0.6D);
                }
                if (stateTicks >= TELL_TICKS) {
                    if (chargeDir.lengthSqr() < 1.0E-4) {
                        chargeDir = new Vec3(getLookAngle().x, 0, getLookAngle().z).normalize();
                    }
                    setState(CHARGE);
                    sound(ModSounds.GNASHBACK_CHARGE.get(), 2.0F, 1.0F);
                }
                return;
            }
            // CHARGE: a straight run at the place the target stood when the tell ended
            setYRot((float) Math.toDegrees(Math.atan2(-chargeDir.x, chargeDir.z)));
            yBodyRot = getYRot();
            yHeadRot = getYRot();
            setDeltaMovement(chargeDir.x * 0.85D, getDeltaMovement().y, chargeDir.z * 0.85D);
            for (LivingEntity hit : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(0.5D),
                    e -> e != GnashbackEntity.this && e.isAlive() && !(e instanceof GnashbackEntity))) {
                hit.hurt(damageSources().mobAttack(GnashbackEntity.this), (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * 1.4F);
                hit.knockback(2.2D, -chargeDir.x, -chargeDir.z);
                hit.setDeltaMovement(hit.getDeltaMovement().add(0, 0.45D, 0));
                hit.hurtMarked = true;
                sound(ModSounds.GNASHBACK_IMPACT.get(), 1.5F, 1.2F);
                endCharge(false);
                return;
            }
            if (horizontalCollision) {
                sound(ModSounds.GNASHBACK_IMPACT.get(), 2.0F, 0.7F);
                particles(ParticleTypes.EXPLOSION, position().add(chargeDir.scale(1.5D)).add(0, 1, 0), 3, 0.6D);
                endCharge(true);
                return;
            }
            if (stateTicks >= CHARGE_TICKS) {
                endCharge(false);
            }
        }

        private void endCharge(boolean stunned) {
            setDeltaMovement(Vec3.ZERO);
            setState(stunned ? STUNNED : IDLE);
            chargeCooldown = 100 + random.nextInt(60);
        }

        private void lookAtTarget(LivingEntity t) {
            Vec3 d = t.position().subtract(position());
            setYRot((float) Math.toDegrees(Math.atan2(-d.x, d.z)));
            yBodyRot = getYRot();
        }

        @Override
        public void stop() {
            if (state() == TELL || state() == CHARGE) {
                setState(IDLE);
            }
        }
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "main", 4, s -> {
            if (isDeadOrDying()) {
                return s.setAndContinue(A_DEATH);
            }
            return s.setAndContinue(switch (state()) {
                case TELL -> A_TELL;
                case CHARGE -> A_CHARGE;
                case STUNNED -> A_STUNNED;
                default -> s.isMoving() ? A_WALK : A_IDLE;
            });
        }));
        controllers.add(new AnimationController<>(this, "attack", 2, s -> PlayState.STOP).triggerableAnim("bite", A_BITE));
    }

    @Override
    protected int deathTicks() {
        return 34;
    }

    @Nullable
    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.GNASHBACK_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.GNASHBACK_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.GNASHBACK_DEATH.get();
    }

    @Override
    protected float getSoundVolume() {
        return 1.4F;
    }
}
