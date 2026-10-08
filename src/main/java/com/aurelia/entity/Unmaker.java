package com.aurelia.entity;

import com.aurelia.block.RealmNodeBlock;
import com.aurelia.registry.ModBlocks;
import com.aurelia.registry.ModEntities;
import com.aurelia.registry.ModItems;
import com.aurelia.world.ArenaBuilder;
import com.aurelia.world.Realm;
import com.aurelia.world.Story;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.item.FallingBlockEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * The Unmaker, the thing behind the worlds (12000 HP). A broken colossus of bone-white and black round a black hole, eight
 * stolen relic-shards in a halo over its mask, two vast hands. It hovers over the Last Realm's arena.
 * Its shell turns most blows aside: it takes 25% damage (60% in phase three), and full damage while staggered.
 *
 *  I. BORROWED GODS (all phases). Every 30 seconds it borrows one Warden's power: that realm's node on the arena rim lights up,
 *     the realm's weather fills the arena, and a ten-second channel begins. Touch the lit node to return the power: the Unmaker
 *     STAGGERS for 8 seconds (full damage, caps 2.5x). Fail and the realm's catastrophe falls on everyone (35% of max health
 *     plus that realm's curse) and it heals.
 *  II. WORLD BREAKER (66%). It tears pieces off the islands and throws them down (marked first), calls the dead Wardens'
 *     heavy guards back as echoes, and raises Unmaking Anchors that mend it while they stand. Break them.
 *  III. THE LAST HEART (33%). The heart is bare. It drags everyone toward it and begins THE UNMAKING: deal 4% of its health
 *     within six seconds to break the channel and stagger it; fail and a wedge of the arena falls away into the void.
 * Attacks: the Grasp (a marked circle under each player, then a hand slams down), the Void Lance, and the Collapse.
 */
public class Unmaker extends AureliaBoss {
    private static final Realm[] GODS = {Realm.GROVE, Realm.SKYREACH, Realm.HOLLOW, Realm.DROWNED, Realm.PALE, Realm.SCARLET,
            Realm.CLOCKWORK, Realm.MYCELIAL};
    private static final String[] WARDEN = {"Mossback", "the Tempest Roc", "the Hollow King", "Vorath", "the White Silence", "Kharzul",
            "Vexor", "the Bloom Mother"};
    private static final String[] POWER = {"the Root Hearts", "the Storm", "the Annihilation", "the Undertow", "the White", "the Last Grain",
            "the Hour", "the Inhale"};

    private int borrowTimer = 300;
    private int borrowTicks = 0;
    @Nullable
    private Realm borrowed;
    @Nullable
    private Realm lastBorrowed;
    private int staggerTicks = 0;
    private int worldfallTimer = 240;
    private int echoTimer = 500;
    private int anchorTimer = 160;
    private final List<BlockPos> anchors = new ArrayList<>();
    private int unmakeTimer = 300;
    private int unmakeTicks = 0;
    private float unmakeDamage = 0.0f;
    private int wedgesLost = 0;
    private boolean restored = false;
    private double angle = 0.0;
    private int casts = 0;
    private final List<Vec3> slamAt = new ArrayList<>();
    private final List<Integer> slamTicks = new ArrayList<>();
    private final Map<UUID, ArrayDeque<Vec3>> history = new HashMap<>();

    public Unmaker(EntityType<? extends Unmaker> type, Level level) {
        super(type, level, BossEvent.BossBarColor.PURPLE);
        this.moveControl = new FlyingMoveControl(this, 20, true);
        this.setNoGravity(true);
        this.xpReward = 2000;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return baseAttributes(12000.0, 32.0, 0.2).add(Attributes.FLYING_SPEED, 0.4).add(Attributes.ARMOR, 20.0);
    }

    @Override
    protected Item shardItem() {
        return ModItems.HAND_OF_GENESIS.get();
    }

    @Override
    protected String phaseLine() {
        return Story.UNMAKER_PHASE;
    }

    @Override
    protected String finalPhaseLine() {
        return Story.UNMAKER_FINAL;
    }

    @Override
    protected String deathLine() {
        return Story.UNMAKER_DEATH;
    }

    @Override
    public String awakenLine() {
        return "I - Borrowed Gods";
    }

    @Override
    public Vec3 spawnPosition(BlockPos altar) {
        return new Vec3(altar.getX() + 0.5, altar.getY() + 5.0, altar.getZ() - 1.5);
    }

    @Override
    protected int abilityInterval() {
        return phase >= 3 ? 55 : phase == 2 ? 70 : 85;
    }

    @Override
    protected void registerGoals() {
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
    }

    private Vec3 centre() {
        return this.arena != null ? Vec3.atBottomCenterOf(this.arena) : this.position();
    }

    private List<ServerPlayer> players(ServerLevel level) {
        List<ServerPlayer> out = new ArrayList<>();
        for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(56.0))) {
            if (!p.isCreative() && !p.isSpectator()) {
                out.add(p);
            }
        }
        return out;
    }

    private void announce(ServerLevel level, String title, String subtitle) {
        for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(80.0))) {
            Story.title(p, title, subtitle, ChatFormatting.DARK_PURPLE);
        }
    }

    // ---- the fight

    @Override
    protected void tickBoss(@Nullable LivingEntity target) {
        if (!(this.level() instanceof ServerLevel level)) {
            return;
        }
        if (!this.restored && this.arena != null) {
            this.restored = true;
            ArenaBuilder.restoreLast(level, this.arena);              // every fight starts on a whole arena
        }
        Vec3 c = centre();
        recordHistory(level);
        tickSlams(level);
        tickAnchors(level);

        if (this.staggerTicks > 0) {
            this.staggerTicks--;
            this.getMoveControl().setWantedPosition(c.x, c.y + 1.5, c.z - 1.5, 1.0);
            level.sendParticles(ParticleTypes.REVERSE_PORTAL, getX(), getY() + 9.0, getZ(), 20, 3.0, 4.0, 3.0, 0.1);
            if (this.staggerTicks == 0) {
                this.playSound(SoundEvents.WITHER_AMBIENT, 4.0f, 0.4f);
            }
            return;
        }
        this.angle += 0.01;
        double bob = Math.sin(this.tickCount * 0.03) * 1.0;
        double height = phase >= 3 ? 3.0 : 5.0;
        this.getMoveControl().setWantedPosition(c.x + Math.cos(this.angle) * 5.0, c.y + height + bob, c.z + Math.sin(this.angle) * 5.0, 1.0);
        if (target != null) {
            this.getLookControl().setLookAt(target, 10.0f, 10.0f);
        }
        if (phase >= 3) {
            singularity(level, c);
        }
        tickBorrowed(level, target);
        if (phase >= 2 && target != null) {
            if (--this.worldfallTimer <= 0) {
                this.worldfallTimer = phase >= 3 ? 200 : 260;
                worldfall(level);
            }
            if (--this.echoTimer <= 0) {
                this.echoTimer = 700;
                summonEchoes(level, target);
            }
            if (this.anchors.isEmpty() && --this.anchorTimer <= 0) {
                this.anchorTimer = 900;
                raiseAnchors(level, c);
            }
        }
        if (phase >= 3 && target != null) {
            tickUnmaking(level, c);
        }
    }

    // ---- I. Borrowed Gods

    private void tickBorrowed(ServerLevel level, @Nullable LivingEntity target) {
        if (this.borrowed != null) {
            this.borrowTicks--;
            int i = this.borrowed.ordinal();
            if (this.tickCount % 20 == 0) {
                weather(level, this.borrowed);
                for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(56.0))) {
                    p.displayClientMessage(Component.literal("Return " + POWER[i] + " to the " + this.borrowed.title + " node  ("
                            + this.borrowTicks / 20 + ")").withStyle(ChatFormatting.LIGHT_PURPLE), true);
                }
            }
            if (this.arena != null) {
                BlockPos n = ArenaBuilder.nodePos(this.arena, this.borrowed);
                level.sendParticles(ParticleTypes.END_ROD, n.getX() + 0.5, n.getY() + 1.5, n.getZ() + 0.5, 3, 0.3, 1.5, 0.3, 0.02);
            }
            if (this.borrowTicks <= 0) {
                Realm r = this.borrowed;
                this.borrowed = null;
                setNode(level, r, false);
                catastrophe(level, r);
            }
            return;
        }
        if (target != null && --this.borrowTimer <= 0) {
            this.borrowTimer = phase >= 3 ? 420 : phase == 2 ? 520 : 600;
            Realm r;
            do {
                r = GODS[this.random.nextInt(GODS.length)];
            } while (r == this.lastBorrowed);
            this.lastBorrowed = r;
            this.borrowed = r;
            this.borrowTicks = phase >= 3 ? 160 : 200;
            setNode(level, r, true);
            this.playSound(SoundEvents.ELDER_GUARDIAN_CURSE, 4.0f, 0.6f);
            announce(level, "BORROWED: " + POWER[r.ordinal()].toUpperCase(), "Return it to the " + r.title + " node.");
            this.say("The Unmaker wears " + WARDEN[r.ordinal()] + "'s power like a glove.");
        }
    }

    private void setNode(ServerLevel level, Realm r, boolean lit) {
        if (this.arena == null) {
            return;
        }
        BlockPos n = ArenaBuilder.nodePos(this.arena, r);
        BlockState s = level.getBlockState(n);
        if (s.getBlock() instanceof RealmNodeBlock) {
            level.setBlock(n, s.setValue(RealmNodeBlock.LIT, lit), 3);
        }
    }

    /** Called by a Realm Node when someone touches it. */
    public void onNodeTouched(ServerLevel level, Realm realm, Player player) {
        if (this.borrowed != realm) {
            player.displayClientMessage(Component.literal("Nothing of " + realm.title + " is borrowed. Not yet."), true);
            return;
        }
        this.borrowed = null;
        setNode(level, realm, false);
        this.staggerTicks = 160;
        this.playSound(SoundEvents.WITHER_HURT, 4.0f, 0.5f);
        level.sendParticles(ParticleTypes.EXPLOSION_EMITTER, getX(), getY() + 9.0, getZ(), 1, 0, 0, 0, 0);
        announce(level, "RETURNED", realm.title + " remembers itself. The Unmaker staggers.");
    }

    /** The borrowed realm's weather, once a second while the channel runs. */
    private void weather(ServerLevel level, Realm r) {
        Vec3 c = centre();
        for (ServerPlayer p : players(level)) {
            switch (r) {
                case GROVE -> {
                    if (p.onGround()) {
                        p.addEffect(new MobEffectInstance(MobEffects.POISON, 40, 0));
                    }
                }
                case SKYREACH -> {
                    if (this.tickCount % 40 == 0 && this.random.nextInt(3) == 0) {
                        LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(level);
                        if (bolt != null) {
                            bolt.moveTo(p.getX() + this.random.nextInt(5) - 2, p.getY(), p.getZ() + this.random.nextInt(5) - 2);
                            level.addFreshEntity(bolt);
                        }
                    }
                }
                case HOLLOW -> p.addEffect(new MobEffectInstance(MobEffects.WITHER, 40, 0));
                case DROWNED -> {
                    Vec3 out = p.position().subtract(c).multiply(1, 0, 1).normalize().scale(0.18);
                    p.push(out.x, 0.0, out.z);
                    p.hurtMarked = true;
                    p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 0));
                }
                case PALE -> {
                    if (!p.isCrouching()) {
                        p.setTicksFrozen(Math.min(p.getTicksRequiredToFreeze() + 40, p.getTicksFrozen() + 50));
                    }
                }
                case SCARLET -> p.setSecondsOnFire(2);
                case CLOCKWORK -> p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 1));
                case MYCELIAL -> {
                    Vec3 in = this.position().subtract(p.position()).multiply(1, 0, 1).normalize().scale(0.15);
                    p.push(in.x, 0.0, in.z);
                    p.hurtMarked = true;
                    p.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 60, 0));
                }
                default -> { }
            }
        }
    }

    /** The power was not returned: the realm's worst day falls on everyone. */
    private void catastrophe(ServerLevel level, Realm r) {
        this.say("The Unmaker spends " + POWER[r.ordinal()] + ". " + r.title + " remembers how it ended.");
        this.playSound(SoundEvents.GENERIC_EXPLODE, 4.0f, 0.5f);
        for (ServerPlayer p : players(level)) {
            p.hurt(this.damageSources().magic(), p.getMaxHealth() * 0.35f);
            switch (r) {
                case GROVE -> {
                    p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 3));
                    p.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 1));
                }
                case SKYREACH -> {
                    p.push(0.0, 1.3, 0.0);
                    p.hurtMarked = true;
                }
                case HOLLOW -> p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 120, 0));
                case DROWNED -> {
                    Vec3 out = p.position().subtract(centre()).multiply(1, 0, 1).normalize().scale(1.1);
                    p.push(out.x, 0.3, out.z);
                    p.hurtMarked = true;
                }
                case PALE -> {
                    p.setTicksFrozen(p.getTicksRequiredToFreeze() + 160);
                    p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 2));
                }
                case SCARLET -> p.setSecondsOnFire(8);
                case CLOCKWORK -> {
                    ArrayDeque<Vec3> past = this.history.get(p.getUUID());
                    if (past != null && !past.isEmpty()) {
                        Vec3 then = past.peekFirst();
                        level.sendParticles(ParticleTypes.REVERSE_PORTAL, p.getX(), p.getY() + 1.0, p.getZ(), 50, 0.4, 1.0, 0.4, 0.2);
                        p.teleportTo(then.x, then.y, then.z);
                        p.fallDistance = 0;
                    }
                }
                case MYCELIAL -> {
                    p.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 2));
                    p.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 160, 0));
                }
                default -> { }
            }
        }
        this.heal(this.getMaxHealth() * 0.03f);
    }

    private void recordHistory(ServerLevel level) {
        if (this.tickCount % 20 != 0) {
            return;
        }
        for (ServerPlayer player : level.getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(64.0))) {
            ArrayDeque<Vec3> q = this.history.computeIfAbsent(player.getUUID(), k -> new ArrayDeque<>());
            q.addLast(player.position());
            while (q.size() > 5) {
                q.pollFirst();
            }
        }
    }

    // ---- II. World Breaker

    private static BlockState chunkOf(Realm r) {
        return switch (r) {
            case GROVE -> Blocks.MOSS_BLOCK.defaultBlockState();
            case SKYREACH -> Blocks.CALCITE.defaultBlockState();
            case HOLLOW -> Blocks.MAGMA_BLOCK.defaultBlockState();
            case DROWNED -> Blocks.PRISMARINE_BRICKS.defaultBlockState();
            case PALE -> Blocks.PACKED_ICE.defaultBlockState();
            case SCARLET -> Blocks.RED_SANDSTONE.defaultBlockState();
            case CLOCKWORK -> Blocks.DEEPSLATE_TILES.defaultBlockState();
            default -> Blocks.BONE_BLOCK.defaultBlockState();
        };
    }

    /** Pieces of the islands come down on everyone; a ring of smoke marks each spot first. */
    private void worldfall(ServerLevel level) {
        List<ServerPlayer> ps = players(level);
        for (int i = 0; i < Math.min(6, ps.size()); i++) {
            ServerPlayer p = ps.get(i);
            Realm r = GODS[this.random.nextInt(GODS.length)];
            BlockPos ground = p.blockPosition().offset(this.random.nextInt(5) - 2, 0, this.random.nextInt(5) - 2);
            for (int k = 0; k < 3; k++) {
                BlockPos sky = ground.offset(this.random.nextInt(3) - 1, 18 + k * 2, this.random.nextInt(3) - 1);
                if (level.getBlockState(sky).isAir()) {
                    FallingBlockEntity rock = FallingBlockEntity.fall(level, sky, chunkOf(r));
                    rock.setHurtsEntities(3.0f, 40);
                    rock.dropItem = false;
                }
            }
            level.sendParticles(ParticleTypes.LARGE_SMOKE, ground.getX() + 0.5, ground.getY() + 0.2, ground.getZ() + 0.5, 30, 1.5, 0.1, 1.5, 0.01);
        }
        this.playSound(SoundEvents.WITHER_BREAK_BLOCK, 3.0f, 0.5f);
    }

    @SuppressWarnings("unchecked")
    private static final Supplier<EntityType<? extends Mob>>[] ECHOES = new Supplier[] {
            () -> ModEntities.BRAMBLE_SENTINEL.get(), () -> ModEntities.CALCITE_SENTINEL.get(), () -> ModEntities.ASHBOUND_KNIGHT.get(),
            () -> ModEntities.CORALCLAD_JUGGERNAUT.get(), () -> ModEntities.RIMEGUARD.get(), () -> ModEntities.SANDGLASS_SENTINEL.get(),
            () -> ModEntities.HOUR_WARDEN.get(), () -> ModEntities.HUSK_GUARD.get()};

    /** Two of one dead realm's heavy guards walk back out of the dark. */
    private void summonEchoes(ServerLevel level, LivingEntity target) {
        int existing = level.getEntitiesOfClass(Mob.class, this.getBoundingBox().inflate(48.0), m -> m != this && m.isAlive()).size();
        int r = this.random.nextInt(ECHOES.length);
        Vec3 c = centre();
        for (int i = 0; i < 2 && existing + i < 6; i++) {
            Mob echo = ECHOES[r].get().create(level);
            if (echo == null) {
                continue;
            }
            double a = this.random.nextDouble() * Math.PI * 2.0;
            echo.moveTo(c.x + Math.cos(a) * 17.0, c.y, c.z + Math.sin(a) * 17.0, 0.0f, 0.0f);
            echo.setTarget(target);
            level.addFreshEntity(echo);
            level.sendParticles(ParticleTypes.SOUL, echo.getX(), echo.getY() + 1.0, echo.getZ(), 30, 0.4, 1.0, 0.4, 0.05);
        }
        this.say("Echoes of " + GODS[r].title + " answer the Unmaker.");
    }

    /** Four black pillars rise round the arena and feed it. */
    private void raiseAnchors(ServerLevel level, Vec3 c) {
        BlockState anchor = ModBlocks.UNMAKING_ANCHOR.get().defaultBlockState();
        for (int i = 0; i < 4; i++) {
            double a = this.random.nextDouble() * Math.PI * 2.0;
            double r = 14.0 + this.random.nextDouble() * 6.0;
            BlockPos base = BlockPos.containing(c.x + Math.cos(a) * r, c.y, c.z + Math.sin(a) * r);
            if (level.getBlockState(base).isAir() && level.getBlockState(base.above()).isAir() && !level.getBlockState(base.below()).isAir()) {
                level.setBlock(base, anchor, 3);
                level.setBlock(base.above(), anchor, 3);
                this.anchors.add(base);
            }
        }
        if (!this.anchors.isEmpty()) {
            this.say("Unmaking Anchors tear up through the floor. While they stand, it mends. Break them.");
        }
    }

    private void tickAnchors(ServerLevel level) {
        BlockState anchor = ModBlocks.UNMAKING_ANCHOR.get().defaultBlockState();
        this.anchors.removeIf(p -> !level.getBlockState(p).is(anchor.getBlock()) && !level.getBlockState(p.above()).is(anchor.getBlock()));
        if (this.anchors.isEmpty() || this.tickCount % 20 != 0) {
            return;
        }
        this.heal(this.getMaxHealth() * 0.0025f * this.anchors.size());
        Vec3 heart = this.position().add(0, 9.0, 0);
        for (BlockPos p : this.anchors) {
            Vec3 from = Vec3.atCenterOf(p.above());
            for (int k = 1; k < 10; k++) {
                Vec3 at = from.lerp(heart, k / 10.0);
                level.sendParticles(ParticleTypes.WITCH, at.x, at.y, at.z, 1, 0, 0, 0, 0);
            }
        }
    }

    // ---- III. The Last Heart

    private void singularity(ServerLevel level, Vec3 c) {
        if (this.tickCount % 5 != 0) {
            return;
        }
        double strength = this.unmakeTicks > 0 ? 0.12 : 0.04;
        for (ServerPlayer p : players(level)) {
            Vec3 in = this.position().subtract(p.position()).multiply(1, 0, 1);
            if (in.lengthSqr() > 4.0) {
                in = in.normalize().scale(strength);
                p.push(in.x, 0.0, in.z);
                p.hurtMarked = true;
            }
        }
    }

    private void tickUnmaking(ServerLevel level, Vec3 c) {
        if (this.unmakeTicks > 0) {
            this.unmakeTicks--;
            level.sendParticles(ParticleTypes.PORTAL, getX(), getY() + 9.0, getZ(), 40, 6.0, 4.0, 6.0, 1.0);
            if (this.unmakeDamage >= this.getMaxHealth() * 0.04f) {
                this.unmakeTicks = 0;
                this.staggerTicks = 120;
                announce(level, "THE HEART FALTERS", "The Unmaking breaks. Strike now.");
                return;
            }
            if (this.tickCount % 20 == 0) {
                for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, this.getBoundingBox().inflate(56.0))) {
                    p.displayClientMessage(Component.literal("Strike the Last Heart  (" + this.unmakeTicks / 20 + ")")
                            .withStyle(ChatFormatting.DARK_PURPLE), true);
                }
            }
            if (this.unmakeTicks == 0) {
                unmakeWedge(level);
                for (ServerPlayer p : players(level)) {
                    p.hurt(this.damageSources().magic(), p.getMaxHealth() * 0.25f);
                }
            }
            return;
        }
        if (--this.unmakeTimer <= 0) {
            this.unmakeTimer = 360;
            this.unmakeTicks = 120;
            this.unmakeDamage = 0.0f;
            this.playSound(SoundEvents.END_PORTAL_SPAWN, 4.0f, 0.4f);
            announce(level, "THE UNMAKING", "Strike the Last Heart before the world gives way.");
        }
    }

    /** A wedge of the outer arena falls into the void (the pad and the nodes' plinths hold). */
    private void unmakeWedge(ServerLevel level) {
        if (this.arena == null || this.wedgesLost >= 6) {
            return;
        }
        this.wedgesLost++;
        double a0 = (this.random.nextInt(8) * 45 + 22.5 - 18) * Math.PI / 180.0;
        double a1 = a0 + 36 * Math.PI / 180.0;
        BlockPos c = this.arena;
        for (int dx = -27; dx <= 27; dx++) {
            for (int dz = -27; dz <= 27; dz++) {
                double d = Math.sqrt(dx * dx + dz * dz);
                double a = Math.atan2(dz, dx);
                if (a < 0) {
                    a += Math.PI * 2.0;
                }
                if (d <= 13.5 || d > 27.0 || a < a0 || a > a1) {
                    continue;
                }
                for (int dy = -8; dy <= 1; dy++) {
                    BlockPos p = c.offset(dx, dy, dz);
                    if (!level.getBlockState(p).isAir() && level.random.nextInt(4) != 0) {
                        level.destroyBlock(p, false);
                    }
                }
            }
        }
        this.say("A piece of the last world falls away into nothing.");
    }

    // ---- attacks

    @Override
    protected void castAbility(LivingEntity target) {
        if (this.staggerTicks > 0 || this.unmakeTicks > 0 || !(this.level() instanceof ServerLevel level)) {
            return;
        }
        this.casts++;
        switch (this.casts % 3) {
            case 0 -> {
                for (ServerPlayer p : players(level)) {
                    if (this.slamAt.size() < 6) {
                        this.slamAt.add(p.position());
                        this.slamTicks.add(30);
                    }
                }
                this.playSound(SoundEvents.WARDEN_SONIC_CHARGE, 3.0f, 0.5f);
            }
            case 1 -> voidLance(level, target);
            default -> collapse(level);
        }
    }

    private void tickSlams(ServerLevel level) {
        float damage = phase >= 3 ? 30.0f : 22.0f;
        for (int i = this.slamAt.size() - 1; i >= 0; i--) {
            Vec3 at = this.slamAt.get(i);
            int t = this.slamTicks.get(i) - 1;
            if (t > 0) {
                this.slamTicks.set(i, t);
                if (t % 3 == 0) {
                    for (int k = 0; k < 16; k++) {
                        double a = k * Math.PI / 8.0;
                        level.sendParticles(ParticleTypes.DRAGON_BREATH, at.x + Math.cos(a) * 3.5, at.y + 0.1, at.z + Math.sin(a) * 3.5, 1, 0, 0, 0, 0);
                    }
                }
                continue;
            }
            level.sendParticles(ParticleTypes.EXPLOSION, at.x, at.y + 0.5, at.z, 6, 1.5, 0.3, 1.5, 0.0);
            this.playSound(SoundEvents.GENERIC_EXPLODE, 2.0f, 0.6f);
            for (ServerPlayer p : players(level)) {
                if (p.position().distanceToSqr(at) < 3.5 * 3.5) {
                    p.hurt(this.damageSources().mobAttack(this), damage);
                    p.push(0.0, 0.9, 0.0);
                    p.hurtMarked = true;
                }
            }
            this.slamAt.remove(i);
            this.slamTicks.remove(i);
        }
    }

    private void voidLance(ServerLevel level, LivingEntity target) {
        Vec3 from = this.position().add(0, 9.0, 0);
        Vec3 to = target.position().add(0, 1.0, 0);
        for (int k = 0; k < 30; k++) {
            Vec3 at = from.lerp(to, k / 30.0);
            level.sendParticles(ParticleTypes.REVERSE_PORTAL, at.x, at.y, at.z, 2, 0.05, 0.05, 0.05, 0.0);
        }
        this.playSound(SoundEvents.BEACON_DEACTIVATE, 3.0f, 0.4f);
        if (this.hasLineOfSight(target)) {
            target.hurt(this.damageSources().indirectMagic(this, this), phase >= 3 ? 20.0f : 14.0f);
            target.addEffect(new MobEffectInstance(MobEffects.WITHER, 80, 1));
        }
    }

    private void collapse(ServerLevel level) {
        boolean pull = phase >= 2;
        for (ServerPlayer p : players(level)) {
            Vec3 d = this.position().subtract(p.position()).multiply(1, 0, 1).normalize().scale(pull ? 1.0 : -1.0);
            p.push(d.x, 0.35, d.z);
            p.hurtMarked = true;
            p.hurt(this.damageSources().mobAttack(this), 8.0f);
            p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 40, 0));
        }
        this.playSound(SoundEvents.WARDEN_SONIC_BOOM, 4.0f, 0.5f);
    }

    // ---- phases, damage, death

    @Override
    protected void onPhaseTwo() {
        if (this.level() instanceof ServerLevel level) {
            announce(level, "II - World Breaker", "Every realm becomes part of the fight.");
        }
    }

    @Override
    protected void onPhaseThree() {
        if (this.level() instanceof ServerLevel level) {
            announce(level, "III - The Last Heart", "The shell is gone. Only the heart is left.");
        }
    }

    @Override
    protected float incomingMultiplier() {
        if (this.staggerTicks > 0) {
            return 1.0f;
        }
        return phase >= 3 ? 0.6f : 0.25f;
    }

    @Override
    protected float capMultiplier() {
        return this.staggerTicks > 0 ? 2.5f : 1.0f;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (source.is(DamageTypeTags.IS_FALL) || source.is(DamageTypeTags.IS_LIGHTNING) || source.is(DamageTypes.FALLING_BLOCK)
                || source.is(DamageTypes.IN_WALL)) {
            return false;
        }
        float before = this.getHealth();
        boolean hit = super.hurt(source, amount);
        if (hit && this.unmakeTicks > 0) {
            this.unmakeDamage += before - this.getHealth();
        }
        return hit;
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        if (this.level() instanceof ServerLevel level) {
            if (this.borrowed != null) {
                setNode(level, this.borrowed, false);
            }
            for (BlockPos p : this.anchors) {
                level.removeBlock(p, false);
                level.removeBlock(p.above(), false);
            }
            if (this.arena != null) {
                ArenaBuilder.restoreLast(level, this.arena);
            }
            announce(level, "THE WORLDS ARE YOURS", "The Hand of Genesis waits where the heart was.");
        }
    }

    /** Three Fractured Genesis fall with it every time, beside the Hand of Genesis: the stuff Genesis Ingots are forged from. */
    @Override
    protected void dropCustomDeathLoot(DamageSource source, int looting, boolean recentlyHit) {
        super.dropCustomDeathLoot(source, looting, recentlyHit);
        Vec3 at = lootPosition();
        net.minecraft.world.entity.item.ItemEntity hearts = new net.minecraft.world.entity.item.ItemEntity(this.level(), at.x + 1.0, at.y + 0.5, at.z,
                new net.minecraft.world.item.ItemStack(ModItems.FRACTURED_GENESIS.get(), 3));
        hearts.setDefaultPickUpDelay();
        hearts.setGlowingTag(true);
        this.level().addFreshEntity(hearts);
    }

    @Override
    protected Vec3 lootPosition() {
        return this.arena != null ? Vec3.atBottomCenterOf(this.arena).add(0.0, 1.0, -2.0) : super.lootPosition();
    }
}
