package quiet.test;

import java.lang.reflect.Method;
import java.nio.file.Path;
import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.sounds.SoundSource;

/** Test-only jar; never embedded in the player package. */
public final class RuntimeTests implements FabricClientGameTest {
  @Override
  public void runTest(ClientGameTestContext context) {
    try {
      runChecked(context);
    } catch (ReflectiveOperationException failure) {
      throw new IllegalStateException(failure);
    }
  }

  private void runChecked(ClientGameTestContext context) throws ReflectiveOperationException {
    String suite = System.getProperty("borrowedquiet.test.suite", "features");
    if (suite.equals("persistence") || suite.equals("removal")) {
      PersistenceTests.run(context, suite.equals("removal"));
      return;
    }
    try (var world =
        context
            .worldBuilder()
            .setUseConsistentSettings(!suite.equals("ordinary") && !suite.equals("natural"))
            .adjustSettings(
                settings ->
                    settings.setSeed(System.getProperty("borrowedquiet.test.seed", "104729")))
            .create()) {
      context.runOnClient(
          client -> {
            client.options.renderDistance().set(4);
            client.options.framerateLimit().set(30);
            client.options.showSubtitles().set(true);
            client.options.getSoundSourceOptionInstance(SoundSource.MUSIC).set(0.2);
          });
      world.getClientLevel().waitForChunksRender();
      world.getServer().runCommand("gamemode survival @a");
      world.getServer().runCommand("time set day");
      if (suite.equals("natural")) {
        NaturalTests.run(context, world);
        return;
      }
      if (System.getProperty("borrowedquiet.test.suite", "features").equals("ordinary")) {
        OrdinaryTests.run(context, world);
        return;
      }
      world.getServer().runCommand("tp @a 0.5 -60 0.5 0 0");
      context.waitTicks(30);
      if (System.getProperty("borrowedquiet.test.suite", "features").equals("presentation")) {
        PresentationTests.run(context, world);
        return;
      }
      if (System.getProperty("borrowedquiet.test.suite", "features").equals("lifecycle")) {
        LifecycleTests.run(context, world);
        return;
      }
      if (Integer.getInteger("borrowedquiet.test.seconds", 0) > 0) {
        endurance(context, world);
        return;
      }
      for (String kind : new String[] {"PACE", "WALL", "FOLD"}) {
        context.getInput().lookAt(0, 0);
        context.runOnClient(
            client -> {
              Method trigger =
                  Class.forName("quiet.BorrowedQuiet")
                      .getMethod(
                          "testTrigger", String.class, double.class, double.class, double.class);
              boolean started =
                  (boolean)
                      trigger.invoke(null, kind, 0.5, -60.0, kind.equals("FOLD") ? 9.5 : -5.5);
              if (!started) throw new AssertionError("Failed to start " + kind);
            });
        System.out.println("SCENARIO_START " + kind);
        context.waitTicks(kind.equals("FOLD") ? 15 : 140);
        context.takeScreenshot(kind.toLowerCase() + "-visible");
        context.waitTicks(240);
        context.runOnClient(
            client -> {
              long[] state =
                  (long[])
                      Class.forName("quiet.BorrowedQuiet").getMethod("diagnostics").invoke(null);
              if (state[1] != 0 || state[2] != 0 || state[5] != -1)
                throw new AssertionError("Leaked " + kind);
            });
        System.out.println("SCENARIO_PASS " + kind);
      }
    }
  }

  private void endurance(ClientGameTestContext context, TestSingleplayerContext world)
      throws ReflectiveOperationException {
    long duration = Integer.getInteger("borrowedquiet.test.seconds", 0) * 1_000_000_000L;
    long started = System.nanoTime();
    Path metrics =
        context.computeOnClient(client -> client.gameDirectory.toPath().resolve("metrics.csv"));
    world.getServer().runCommand("difficulty peaceful");
    world.getServer().runCommand("fill -8 -60 -8 8 -57 -8 stone");
    world.getServer().runCommand("fill -8 -60 8 8 -57 8 stone");
    world.getServer().runCommand("fill -8 -60 -8 -8 -57 8 stone");
    world.getServer().runCommand("fill 8 -60 -8 8 -57 8 stone");
    world.getServer().runCommand("item replace entity @a hotbar.0 with iron_pickaxe");
    try (Telemetry telemetry = new Telemetry(metrics)) {
      int cycle = 0;
      while (System.nanoTime() - started < duration) {
        world.getServer().runCommand("tp @a 0.5 -60 0.5 0 0");
        world.getServer().runCommand("setblock 0 -60 3 stone");
        context.waitTicks(10);
        context.getInput().lookAt(new net.minecraft.core.BlockPos(0, -60, 3));
        context.getInput().holdMouseFor(0, 50);
        context.waitTicks(40);
        for (int direction = 0; direction < 4; direction++) {
          context.getInput().lookAt(direction * 90, 0);
          context.getInput().holdKeyFor(options -> options.keyUp, 40);
          context.waitTicks(100);
        }
        if (++cycle % 2 == 0)
          context.runOnClient(
              client -> {
                System.gc();
                System.out.println(
                    "POST_GC seconds="
                        + (System.nanoTime() - started) / 1e9
                        + " heap="
                        + (Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()));
              });
        if (cycle % 20 == 0)
          world.getServer().runCommand("item replace entity @a hotbar.0 with iron_pickaxe");
        if (cycle % 20 == 0) context.takeScreenshot("endurance-" + cycle);
      }
      System.out.println("ENDURANCE_PASS elapsed_ns=" + (System.nanoTime() - started));
      telemetry.check();
    } catch (java.io.IOException failure) {
      throw new java.io.UncheckedIOException(failure);
    }
  }
}
