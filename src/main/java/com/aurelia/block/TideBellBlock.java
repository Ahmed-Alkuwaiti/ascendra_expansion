package com.aurelia.block;

import com.aurelia.entity.Vorath;
import com.aurelia.world.Realm;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * A Tide Bell.
 *  In the Tidewrack Citadel: the portal ritual. Each bell has a voice (NOTE 0 to 4, its pedestal is NOTE + 1 steps tall).
 *  Ring them from the lowest voice to the highest, "as the tide rises". A wrong bell silences them all and the sea surges.
 *  In the Drowned Expanse: an arena bell. Ringing it drags Vorath to the surface, exposed, and the bell needs time to recover.
 */
public class TideBellBlock extends Block {
    public static final IntegerProperty NOTE = IntegerProperty.create("note", 0, 4);
    public static final BooleanProperty RUNG = BooleanProperty.create("rung");
    private static final VoxelShape SHAPE = Block.box(2.0, 0.0, 2.0, 14.0, 16.0, 14.0);
    private static final int GROUP_RANGE = 12;
    /** How long an arena bell stays silent after it has been rung, in ticks. */
    public static final int ARENA_COOLDOWN = 600;

    public TideBellBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(NOTE, 0).setValue(RUNG, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(NOTE, RUNG);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player,
                                 InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }
        ServerLevel serverLevel = (ServerLevel) level;
        if (Realm.of(level) == Realm.DROWNED) {
            ringInArena(serverLevel, pos, state, player);
        } else {
            ringInCitadel(serverLevel, pos, state, player);
        }
        return InteractionResult.CONSUME;
    }

    private void ringInArena(ServerLevel level, BlockPos pos, BlockState state, Player player) {
        if (state.getValue(RUNG)) {
            player.displayClientMessage(Component.literal("The bell is still shivering from the last time. Give it a moment."), true);
            return;
        }
        level.setBlock(pos, state.setValue(RUNG, true), 3);
        level.scheduleTick(pos, this, ARENA_COOLDOWN);
        level.playSound(null, pos, SoundEvents.BELL_BLOCK, SoundSource.BLOCKS, 3.0f, 0.6f);
        level.sendParticles(ParticleTypes.SPLASH, pos.getX() + 0.5, pos.getY() + 1.0, pos.getZ() + 0.5, 40, 1.2, 0.4, 1.2, 0.1);
        boolean pulled = false;
        for (Vorath vorath : level.getEntitiesOfClass(Vorath.class, new AABB(pos).inflate(64.0))) {
            pulled |= vorath.onBellRung(pos);
        }
        if (!pulled) {
            player.displayClientMessage(Component.literal("The bell's voice rolls out across the water. Nothing answers yet."), true);
        }
    }

    @Override
    public void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (state.getValue(RUNG) && Realm.of(level) == Realm.DROWNED) {
            level.setBlock(pos, state.setValue(RUNG, false), 3);
            level.playSound(null, pos, SoundEvents.BELL_RESONATE, SoundSource.BLOCKS, 1.5f, 1.2f);
        }
    }

    private void ringInCitadel(ServerLevel level, BlockPos pos, BlockState state, Player player) {
        if (state.getValue(RUNG)) {
            player.displayClientMessage(Component.literal("This bell has already sung. Find the next voice."), true);
            return;
        }
        List<BlockPos> group = new ArrayList<>();
        int rung = 0;
        for (BlockPos p : BlockPos.betweenClosed(pos.offset(-GROUP_RANGE, -4, -GROUP_RANGE), pos.offset(GROUP_RANGE, 4, GROUP_RANGE))) {
            BlockState s = level.getBlockState(p);
            if (s.is(this)) {
                group.add(p.immutable());
                if (s.getValue(RUNG)) {
                    rung++;
                }
            }
        }
        int note = state.getValue(NOTE);
        float pitch = 0.5f + note * 0.3f;
        if (note == rung) {
            level.setBlock(pos, state.setValue(RUNG, true), 3);
            level.playSound(null, pos, SoundEvents.BELL_BLOCK, SoundSource.BLOCKS, 2.0f, pitch);
            level.sendParticles(ParticleTypes.BUBBLE_POP, pos.getX() + 0.5, pos.getY() + 1.2, pos.getZ() + 0.5, 30, 0.4, 0.6, 0.4, 0.05);
            if (rung + 1 >= group.size()) {
                PuzzleLogic.check(level, pos, this, RUNG);
            } else {
                player.displayClientMessage(Component.literal("The bell sings and keeps singing. " + (rung + 1) + " of " + group.size() + "."), true);
            }
            return;
        }
        // Out of order: every bell falls silent and the sea surges.
        for (BlockPos p : group) {
            BlockState s = level.getBlockState(p);
            if (s.is(this) && s.getValue(RUNG)) {
                level.setBlock(p, s.setValue(RUNG, false), 3);
            }
        }
        level.playSound(null, pos, SoundEvents.BELL_RESONATE, SoundSource.BLOCKS, 2.0f, 0.5f);
        level.playSound(null, pos, SoundEvents.GENERIC_SPLASH, SoundSource.BLOCKS, 2.0f, 0.6f);
        for (Player p : level.getEntitiesOfClass(Player.class, new AABB(pos).inflate(10.0))) {
            p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 2));
            p.addEffect(new MobEffectInstance(MobEffects.DIG_SLOWDOWN, 200, 1));
            p.hurt(p.damageSources().drown(), 4.0f);
            level.sendParticles(ParticleTypes.SPLASH, p.getX(), p.getY() + 1.0, p.getZ(), 40, 0.6, 0.8, 0.6, 0.2);
        }
        player.displayClientMessage(Component.literal("The bells fall out of tune and the sea surges up. Begin again, as the tide rises."), true);
    }
}
