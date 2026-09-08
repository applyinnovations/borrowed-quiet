package quiet;

import static net.fabricmc.fabric.api.client.command.v2.ClientCommands.argument;
import static net.fabricmc.fabric.api.client.command.v2.ClientCommands.literal;

import com.mojang.brigadier.arguments.BoolArgumentType;
import com.mojang.brigadier.arguments.DoubleArgumentType;
import java.util.ArrayDeque;
import java.util.Locale;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.command.v2.ClientCommandRegistrationCallback;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientLifecycleEvents;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import quiet.core.Director;
import quiet.core.Settings;

public final class BorrowedQuiet implements ClientModInitializer {
  private static final Logger LOG = LoggerFactory.getLogger("Borrowed Quiet");
  private static final boolean TESTING = Boolean.getBoolean("borrowedquiet.testing");
  private static final boolean DIAGNOSTICS =
      TESTING || Boolean.getBoolean("borrowedquiet.diagnostics");
  private static BorrowedQuiet instance;
  private final Presentation presentation = new Presentation();
  private final ArrayDeque<Vec3> trail = new ArrayDeque<>(32);
  private ConfigStore store;
  private Settings settings;
  private Director director;
  private ClientLevel world;
  private Vec3 lastPosition;
  private Vec3 source;
  private Vec3 paceStep = Vec3.ZERO;
  private Director.Kind active;
  private int age, collapse, pulse, nextPulse, pulses, walked, stopped, work, ticks;
  private int damageGrace;
  private long measuredNanos;
  private long episodes;

  @Override
  public void onInitializeClient() {
    instance = this;
    store =
        new ConfigStore(
            FabricLoader.getInstance().getConfigDir().resolve("borrowedquiet.json"), LOG);
    settings = store.read();
    ClientTickEvents.END_CLIENT_TICK.register(this::tick);
    ClientLifecycleEvents.CLIENT_STOPPING.register(client -> store.close());
    commands();
    LOG.info("Borrowed Quiet 1.0.0: local survival only. Controls: /borrowedquiet");
  }

  private void commands() {
    ClientCommandRegistrationCallback.EVENT.register(
        (dispatcher, registry) -> {
          var command =
              literal("borrowedquiet")
                  .executes(
                      context -> {
                        context
                            .getSource()
                            .sendFeedback(
                                Component.literal(
                                    "Borrowed Quiet: /borrowedquiet on | off | status | gentle |"
                                        + " normal | intense | volume <0–1> | visuals <true/false>"
                                        + " | reducedmotion <true/false>. Vanilla Ambient volume"
                                        + " and subtitles apply."));
                        return 1;
                      });
          command.then(
              literal("status")
                  .executes(
                      context -> {
                        context
                            .getSource()
                            .sendFeedback(
                                Component.literal(
                                    "Borrowed Quiet: "
                                        + settings
                                        + ". Local Overworld survival only. "
                                        + (active == null ? "Quiet." : "An episode is active.")));
                        return 1;
                      }));
          for (boolean enabled : new boolean[] {true, false})
            command.then(
                literal(enabled ? "on" : "off")
                    .executes(
                        context ->
                            change(
                                new Settings(
                                    enabled,
                                    settings.intensity(),
                                    settings.volume(),
                                    settings.visuals(),
                                    settings.reducedMotion()))));
          for (var intensity : Director.Intensity.values())
            command.then(
                literal(intensity.name().toLowerCase(Locale.ROOT))
                    .executes(
                        context ->
                            change(
                                new Settings(
                                    settings.enabled(),
                                    intensity,
                                    settings.volume(),
                                    settings.visuals(),
                                    settings.reducedMotion()))));
          command.then(
              literal("volume")
                  .then(
                      argument("value", DoubleArgumentType.doubleArg(0, 1))
                          .executes(
                              context ->
                                  change(
                                      new Settings(
                                          settings.enabled(),
                                          settings.intensity(),
                                          DoubleArgumentType.getDouble(context, "value"),
                                          settings.visuals(),
                                          settings.reducedMotion())))));
          command.then(
              literal("visuals")
                  .then(
                      argument("value", BoolArgumentType.bool())
                          .executes(
                              context ->
                                  change(
                                      new Settings(
                                          settings.enabled(),
                                          settings.intensity(),
                                          settings.volume(),
                                          BoolArgumentType.getBool(context, "value"),
                                          settings.reducedMotion())))));
          command.then(
              literal("reducedmotion")
                  .then(
                      argument("value", BoolArgumentType.bool())
                          .executes(
                              context ->
                                  change(
                                      new Settings(
                                          settings.enabled(),
                                          settings.intensity(),
                                          settings.volume(),
                                          settings.visuals(),
                                          BoolArgumentType.getBool(context, "value"))))));
          dispatcher.register(command);
        });
  }

  private int change(Settings value) {
    settings = value;
    clear(Minecraft.getInstance(), "configuration");
    store.save(settings);
    if (Minecraft.getInstance().player != null)
      Minecraft.getInstance()
          .player
          .sendSystemMessage(Component.literal("Borrowed Quiet: settings updated. " + settings));
    return 1;
  }

  private boolean safe(Minecraft client) {
    return settings.enabled()
        && client.player != null
        && client.level != null
        && client.level.dimension() == Level.OVERWORLD
        && client.getSingleplayerServer() != null
        && !client.getSingleplayerServer().isPublished()
        && client.gameMode != null
        && client.gameMode.getPlayerMode() == GameType.SURVIVAL
        && client.gui.screen() == null
        && client.gui.overlay() == null
        && !client.isPaused()
        && client.player.isAlive()
        && !client.player.isSleeping()
        && client.player.getHealth() > 10
        && client.player.hurtTime == 0
        && client.player.fallDistance < 3
        && !client.player.isInWater()
        && !client.player.isInLava()
        && damageGrace == 0;
  }

  private void tick(Minecraft client) {
    long started = System.nanoTime();
    try {
      advance(client);
    } finally {
      measuredNanos = System.nanoTime() - started;
    }
  }

  private void advance(Minecraft client) {
    if (world != client.level) {
      clear(client, "world-change");
      world = client.level;
      director = new Director(Long.getLong("borrowedquiet.seed", System.nanoTime()));
      trail.clear();
      lastPosition = null;
      walked = stopped = work = damageGrace = 0;
    }
    if (client.player != null && client.player.hurtTime > 0) damageGrace = 200;
    else if (damageGrace > 0) damageGrace--;
    if (!safe(client)) {
      clear(client, "unsafe-or-menu");
      walked = stopped = work = 0;
      lastPosition = null;
      return;
    }
    ticks++;
    presentation.tick(client);
    Vec3 position = client.player.position();
    boolean moving = lastPosition != null && position.distanceToSqr(lastPosition) > 0.008;
    if (moving) {
      walked = Math.min(200, walked + 1);
      stopped = 0;
    } else stopped = Math.min(200, stopped + 1);
    if (stopped > 100) walked = 0;
    if (ticks % 5 == 0 && moving) {
      if (trail.size() == 32) trail.removeFirst();
      trail.addLast(position);
    }
    lastPosition = position;
    if ((client.options.keyAttack.isDown() || client.options.keyUse.isDown())
        && client.hitResult != null
        && client.hitResult.getType() == HitResult.Type.BLOCK) work = 160;
    else if (work > 0) work--;
    if (active != null) {
      episode(client);
      return;
    }
    var choice =
        director.tick(
            true,
            walked >= 35 && stopped >= 8 && stopped <= 80,
            work > 0,
            settings.visuals() && ticks % 3 == 0,
            settings.intensity());
    if (choice != null) start(client, choice, null);
  }

  private Vec3 chooseSource(Minecraft client, Director.Kind kind) {
    if (kind == Director.Kind.PACE) {
      for (Vec3 point : trail) {
        double distance = point.distanceTo(client.player.position());
        if (distance >= 4 && distance <= 10 && loaded(client, BlockPos.containing(point)))
          return point;
      }
      return null;
    }
    Vec3 eye = client.player.getEyePosition();
    if (kind == Director.Kind.WALL) {
      for (int candidate = 0; candidate < 8; candidate++) {
        double angle = Math.toRadians(client.player.getYRot() + 70 + director.randomInt(220));
        Vec3 target = eye.add(-Math.sin(angle) * 8, -0.4, Math.cos(angle) * 8);
        if (!loaded(client, BlockPos.containing(target))) continue;
        var hit =
            client.level.clip(
                new ClipContext(
                    eye,
                    target,
                    ClipContext.Block.COLLIDER,
                    ClipContext.Fluid.NONE,
                    client.player));
        if (hit.getType() == HitResult.Type.BLOCK && hit.getLocation().distanceTo(eye) >= 3)
          return hit.getLocation();
      }
      return null;
    }
    int sightChecks = 0;
    for (int candidate = 0; candidate < 24 && sightChecks < 16; candidate++) {
      double angle = Math.toRadians(client.player.getYRot() + 70 + director.randomInt(221));
      double distance = 6 + director.randomInt(9);
      BlockPos base =
          BlockPos.containing(
              client
                  .player
                  .position()
                  .add(
                      -Math.sin(angle) * distance,
                      (candidate % 4) - 2,
                      Math.cos(angle) * distance));
      if (!loaded(client, base)
          || !client
              .level
              .getBlockState(base.below())
              .isCollisionShapeFullBlock(client.level, base.below())) continue;
      if (client.level.getBlockState(base).isAir()
          && client.level.getBlockState(base.above()).isAir()
          && client.level.getBlockState(base.above(2)).isAir()) {
        sightChecks++;
        Vec3 position = Vec3.atBottomCenterOf(base);
        if (client
                .level
                .clip(
                    new ClipContext(
                        eye,
                        position.add(0, 1.4, 0),
                        ClipContext.Block.COLLIDER,
                        ClipContext.Fluid.NONE,
                        client.player))
                .getType()
            == HitResult.Type.MISS) return position;
      }
    }
    return null;
  }

  private boolean start(Minecraft client, Director.Kind kind, Vec3 override) {
    source = override == null ? chooseSource(client, kind) : override;
    if (source == null) {
      trace("miss", kind.toString());
      return false;
    }
    if (kind == Director.Kind.FOLD
        && (!settings.visuals()
            || !presentation.showFold(client, source, client.player.getYRot() + 20))) return false;
    active = kind;
    director.started(kind);
    age = 0;
    collapse = 0;
    pulse = 0;
    nextPulse = 12 + director.randomInt(18);
    pulses = kind == Director.Kind.PACE ? 3 + director.randomInt(4) : 5;
    Vec3 toPlayer = client.player.position().subtract(source);
    paceStep =
        toPlayer.normalize().scale(Math.min(0.6, Math.max(0, toPlayer.length() - 3) / pulses));
    episodes++;
    trace("start", kind + " at " + source);
    return true;
  }

  private static boolean loaded(Minecraft client, BlockPos position) {
    return client.level.getChunkSource().hasChunk(position.getX() >> 4, position.getZ() >> 4);
  }

  private boolean noticed(Minecraft client) {
    Vec3 towards = source.add(0, 1.3, 0).subtract(client.player.getEyePosition());
    return towards.lengthSqr() < 9 || client.player.getLookAngle().dot(towards.normalize()) > 0.96;
  }

  private void episode(Minecraft client) {
    age++;
    if (source.distanceToSqr(client.player.position()) > 900 || age >= 360) {
      clear(client, "complete");
      return;
    }
    if (active == Director.Kind.FOLD) {
      if (age == 18) sound(client, "scrape", source, 0.5f);
      if (collapse == 0 && age > 20 && (noticed(client) || age > 190)) {
        if (settings.reducedMotion()) {
          clear(client, "noticed-reduced-motion");
          return;
        }
        collapse = age;
        presentation.contract();
        sound(client, "fold", source, 0.5f);
        trace("contract", source.toString());
      }
      if (collapse > 0 && age - collapse >= 20) presentation.hideFold();
      if (collapse > 0 && age - collapse >= 45) clear(client, "fold-complete");
      return;
    }
    if (active == Director.Kind.PACE && age > 24 && noticed(client)) {
      clear(client, "noticed");
      return;
    }
    if (age == nextPulse && pulse < pulses) {
      String name = (active == Director.Kind.PACE ? "tread" : "tap") + (1 + director.randomInt(2));
      Vec3 at = source;
      if (active == Director.Kind.WALL && pulse >= 3) at = source.add(0.7, 0, -0.4);
      sound(client, name, at, 0.48f);
      pulse++;
      if (active == Director.Kind.PACE) source = source.add(paceStep);
      nextPulse =
          age + (active == Director.Kind.WALL && pulse == 3 ? 65 : 12 + director.randomInt(12));
    }
    if (pulse == pulses && age > nextPulse + 35) clear(client, "complete");
  }

  private void sound(Minecraft client, String name, Vec3 at, float gain) {
    presentation.sound(
        client, name, at, gain * settings.volume(), 0.92f + director.randomInt(17) / 100f);
    trace("sound", name + " at " + at);
  }

  private void clear(Minecraft client, String reason) {
    if (active != null) {
      trace("end", active + " " + reason + " age=" + age);
      if (director != null) director.recover(settings.intensity());
    }
    presentation.clear(client);
    active = null;
  }

  private void trace(String action, String message) {
    if (DIAGNOSTICS) LOG.info("BQ tick={} {} {}", ticks, action, message);
  }

  public static long[] diagnostics() {
    if (!DIAGNOSTICS || instance == null) return new long[0];
    var mod = instance;
    return new long[] {
      mod.measuredNanos,
      mod.presentation.sounds(),
      mod.presentation.entities(),
      mod.trail.size(),
      mod.episodes,
      mod.active == null ? -1 : mod.active.ordinal(),
      mod.director == null ? 2400 : mod.director.remaining()
    };
  }

  public static boolean testTrigger(String kind, double x, double y, double z) {
    if (!TESTING) throw new SecurityException("Test controls require borrowedquiet.testing");
    var client = Minecraft.getInstance();
    if (instance == null || !instance.safe(client)) return false;
    instance.clear(client, "test-trigger");
    return instance.start(client, Director.Kind.valueOf(kind), new Vec3(x, y, z));
  }

  public static void testSound(String name, double x, double y, double z) {
    if (!TESTING) throw new SecurityException("Test controls require borrowedquiet.testing");
    if (!java.util.Set.of("tread1", "tread2", "tap1", "tap2", "scrape", "fold").contains(name))
      throw new IllegalArgumentException("Unknown sound");
    if (instance != null && instance.safe(Minecraft.getInstance()))
      instance.sound(Minecraft.getInstance(), name, new Vec3(x, y, z), 0.6f);
  }
}
