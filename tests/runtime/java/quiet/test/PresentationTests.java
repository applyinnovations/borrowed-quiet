package quiet.test;

import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundSource;

public final class PresentationTests {
  private PresentationTests() {}

  private static void sound(ClientGameTestContext context, String name, double x, double z) {
    context.runOnClient(
        client -> {
          try {
            Class.forName("quiet.BorrowedQuiet")
                .getMethod("testSound", String.class, double.class, double.class, double.class)
                .invoke(null, name, x, -58.5, z);
          } catch (ReflectiveOperationException failure) {
            throw new IllegalStateException(failure);
          }
        });
  }

  private static void mark(String label) {
    System.out.println("AV_MARK " + System.currentTimeMillis() + " " + label);
  }

  public static void run(ClientGameTestContext context, TestSingleplayerContext world) {
    Harness.command(context, "volume 1");
    context.runOnClient(
        client -> client.options.getSoundSourceOptionInstance(SoundSource.MUSIC).set(0.0));
    context.getInput().lookAt(0, 0);
    for (double[] point :
        new double[][] {{6.5, 0.5}, {-5.5, 0.5}, {0.5, 3.5}, {0.5, 14.5}, {0.5, 30.5}}) {
      mark("position " + point[0] + " " + point[1]);
      sound(context, "scrape", point[0], point[1]);
      context.waitTicks(65);
    }
    for (String name : new String[] {"tread1", "tread2", "tap1", "tap2", "scrape", "fold"}) {
      mark("asset " + name);
      for (int pulse = 0; pulse < 4; pulse++) {
        sound(context, name, 0.5, 4.5);
        context.waitTicks(40);
      }
      context.waitTicks(20);
    }
    mark("maximum-overlap");
    sound(context, "scrape", 0.5, 0.5);
    sound(context, "fold", 0.5, 0.5);
    sound(context, "tap1", 0.5, 0.5);
    context.waitTicks(60);
    Harness.command(context, "volume 0");
    mark("mod-muted");
    sound(context, "scrape", 0.5, 0.5);
    context.waitTicks(60);
    Harness.quiet(context, "mod-volume-zero");
    Harness.command(context, "volume 1");
    context.runOnClient(
        client -> client.options.getSoundSourceOptionInstance(SoundSource.AMBIENT).set(0.0));
    mark("ambient-muted");
    sound(context, "scrape", 0.5, 0.5);
    context.waitTicks(60);
    context.runOnClient(
        client -> client.options.getSoundSourceOptionInstance(SoundSource.AMBIENT).set(1.0));
    context.runOnClient(
        client -> client.options.getSoundSourceOptionInstance(SoundSource.MASTER).set(0.0));
    mark("master-muted");
    sound(context, "scrape", 0.5, 0.5);
    context.waitTicks(60);
    context.runOnClient(
        client -> {
          client.options.getSoundSourceOptionInstance(SoundSource.MASTER).set(1.0);
          client.options.getSoundSourceOptionInstance(SoundSource.MUSIC).set(1.0);
        });
    mark("music-overlap");
    world
        .getServer()
        .runCommand("execute at @a run playsound minecraft:music.game music @a ~ ~ ~ 1 1");
    sound(context, "scrape", 0.5, 1.5);
    sound(context, "fold", 1.5, 0.5);
    context.waitTicks(200);
    world.getServer().runCommand("stopsound @a music");
    context.runOnClient(
        client -> client.options.getSoundSourceOptionInstance(SoundSource.MASTER).set(0.6));
    for (String lighting : new String[] {"day", "night"}) {
      world.getServer().runCommand("time set " + (lighting.equals("day") ? "6000" : "18000"));
      world.getServer().runCommand("setblock 3 -60 8 torch");
      for (int angle = 0; angle < 4; angle++) {
        double theta = angle * Math.PI / 2;
        double x = 0.5 + Math.sin(theta) * 7, z = 8.5 - Math.cos(theta) * 7;
        world.getServer().runCommand("tp @a " + x + " -60 " + z);
        context.waitTicks(10);
        context.getInput().lookAt(0, 0);
        mark("fold " + lighting + " angle=" + angle);
        context.runOnClient(
            client -> {
              if (!Harness.trigger("FOLD", 0.5, -60, 8.5)) throw new AssertionError("Fold view");
            });
        context.getInput().lookAt(new BlockPos(0, -59, 8));
        context.waitTicks(15);
        context.takeScreenshot("fold-" + lighting + "-" + angle);
        context.waitTicks(60);
        Harness.quiet(context, "fold-view-" + lighting + "-" + angle);
      }
    }
  }
}
