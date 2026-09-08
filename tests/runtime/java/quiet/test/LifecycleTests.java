package quiet.test;

import java.util.concurrent.CompletableFuture;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.client.gui.screens.PauseScreen;
import net.minecraft.world.level.Level;

public final class LifecycleTests {
  private LifecycleTests() {}

  public static void run(ClientGameTestContext context, TestSingleplayerContext world) {
    for (String kind : new String[] {"PACE", "WALL", "FOLD"}) {
      Harness.startBehind(context, kind);
      Harness.command(context, "off");
      Harness.quiet(context, kind + "-disabled");
      context.runOnClient(
          client -> {
            if (Harness.trigger(kind, 0.5, -60, -6))
              throw new AssertionError("Disabled activation");
          });
      Harness.command(context, "on");
      Harness.startBehind(context, kind);
      context.setScreen(() -> new PauseScreen(true));
      context.waitTicks(4);
      Harness.quiet(context, kind + "-pause");
      context.setScreen(() -> null);
      context.waitTicks(4);
      for (String mode : new String[] {"creative", "spectator"}) {
        Harness.startBehind(context, kind);
        world.getServer().runCommand("gamemode " + mode + " @a");
        context.waitTicks(8);
        Harness.quiet(context, kind + "-" + mode);
        context.runOnClient(
            client -> {
              if (Harness.trigger(kind, 0.5, -60, -6))
                throw new AssertionError("Non-survival activation");
            });
        world.getServer().runCommand("gamemode survival @a");
        context.waitTicks(8);
      }
      Harness.startBehind(context, kind);
      CompletableFuture<Void> reload =
          context.computeOnClient(client -> client.reloadResourcePacks());
      context.waitFor(client -> reload.isDone(), 1200);
      Harness.quiet(context, kind + "-resource-reload");
      context.waitFor(client -> client.gui.overlay() == null, 1200);
      context.waitTicks(30);
    }
    for (String dimension : new String[] {"the_nether", "the_end"}) {
      Harness.startBehind(context, "FOLD");
      world.getServer().runCommand("execute in minecraft:" + dimension + " run tp @a 0 90 0");
      context.waitFor(
          client -> client.level != null && client.level.dimension() != Level.OVERWORLD, 1200);
      context.waitTicks(2);
      Harness.quiet(context, dimension);
      world.getServer().runCommand("execute in minecraft:overworld run tp @a 0.5 -60 0.5");
      context.waitFor(
          client -> client.level != null && client.level.dimension() == Level.OVERWORLD, 1200);
      context.waitTicks(30);
    }
    Harness.startBehind(context, "PACE");
    world.getServer().runCommand("kill @a");
    context.waitTicks(30);
    Harness.quiet(context, "death");
    context.clickScreenButton("Respawn");
    context.waitFor(
        client -> client.player != null && client.player.isAlive() && client.gui.screen() == null,
        1200);
    context.waitTicks(220);
    Harness.startBehind(context, "WALL");
    world.getServer().runCommand("tp @a 512 -60 512");
    context.waitTicks(30);
    Harness.quiet(context, "distance-unloading");
    world.getServer().runCommand("tp @a 0.5 -60 0.5");
    context.waitTicks(30);
    Harness.command(context, "visuals false");
    context.runOnClient(
        client -> {
          if (Harness.trigger("FOLD", 0.5, -60, 6)) throw new AssertionError("Visuals disabled");
        });
    Harness.command(context, "visuals true");
    Harness.command(context, "reducedmotion true");
    context.runOnClient(
        client -> {
          if (!Harness.trigger("FOLD", 0.5, -60, 6)) throw new AssertionError("Reduced mode");
        });
    context.getInput().lookAt(0, 0);
    context.waitTicks(25);
    Harness.quiet(context, "reduced-motion");
    Harness.command(context, "reducedmotion false");
    for (String intensity : new String[] {"gentle", "normal", "intense"}) {
      Harness.command(context, intensity);
      Harness.startBehind(context, "PACE");
      Harness.command(context, "off");
      Harness.quiet(context, "intensity-" + intensity);
      Harness.command(context, "on");
    }
    Harness.command(context, "normal");
    for (String difficulty : new String[] {"peaceful", "easy", "normal", "hard"}) {
      world.getServer().runCommand("difficulty " + difficulty);
      Harness.startBehind(context, "WALL");
      Harness.command(context, "off");
      Harness.quiet(context, "difficulty-" + difficulty);
      Harness.command(context, "on");
    }
    Harness.startBehind(context, "WALL");
    world.getServer().runCommand("execute as @a run damage @s 11 minecraft:generic");
    context.waitTicks(4);
    Harness.quiet(context, "damage-low-health");
    world.getServer().runCommand("effect give @a instant_health 1 5 true");
    context.waitTicks(220);
    for (String fluid : new String[] {"water", "lava"}) {
      world.getServer().runCommand("effect give @a fire_resistance 20 0 true");
      Harness.startBehind(context, "FOLD");
      world.getServer().runCommand("setblock 0 -60 0 " + fluid);
      context.waitTicks(8);
      Harness.quiet(context, fluid);
      world.getServer().runCommand("fill -2 -60 -2 2 -60 2 air");
      world.getServer().runCommand("tp @a 0.5 -60 0.5");
      world
          .getServer()
          .runOnServer(
              server -> server.getPlayerList().getPlayers().forEach(player -> player.clearFire()));
      context.waitTicks(220);
    }
    world.getServer().runCommand("time set night");
    world.getServer().runCommand("setblock 0 -60 2 red_bed[part=foot,facing=south]");
    world.getServer().runCommand("setblock 0 -60 3 red_bed[part=head,facing=south]");
    Harness.startBehind(context, "WALL");
    context.getInput().lookAt(new net.minecraft.core.BlockPos(0, -60, 2));
    context.getInput().pressMouse(1);
    context.waitFor(client -> client.player.isSleeping(), 100);
    context.waitTicks(2);
    Harness.quiet(context, "sleep");
    context.waitFor(client -> !client.player.isSleeping(), 300);
    context.waitTicks(10);
    for (String boundary : new String[] {"published", "remote", "falling"}) {
      Harness.startBehind(context, "FOLD");
      context.runOnClient(
          client -> {
            try {
              var type = Class.forName("quiet.BorrowedQuiet");
              var instanceField = type.getDeclaredField("instance");
              instanceField.setAccessible(true);
              var advance = type.getDeclaredMethod("advance", net.minecraft.client.Minecraft.class);
              advance.setAccessible(true);
              var server = client.getSingleplayerServer();
              if (boundary.equals("published")) {
                var port = server.getClass().getDeclaredField("multiplayerScope");
                port.setAccessible(true);
                Object prior = port.get(server);
                try {
                  port.set(server, net.minecraft.server.MinecraftServer.MultiplayerScope.LAN);
                  advance.invoke(instanceField.get(null), client);
                  if (Harness.trigger("FOLD", 0.5, -60, 6))
                    throw new AssertionError("Published guard");
                } finally {
                  port.set(server, prior);
                }
              } else if (boundary.equals("remote")) {
                var field = client.getClass().getDeclaredField("singleplayerServer");
                field.setAccessible(true);
                try {
                  field.set(client, null);
                  advance.invoke(instanceField.get(null), client);
                  if (Harness.trigger("FOLD", 0.5, -60, 6))
                    throw new AssertionError("Remote guard");
                } finally {
                  field.set(client, server);
                }
              } else {
                var prior = client.player.fallDistance;
                try {
                  client.player.fallDistance = 4;
                  advance.invoke(instanceField.get(null), client);
                  if (Harness.trigger("FOLD", 0.5, -60, 6))
                    throw new AssertionError("Falling guard");
                } finally {
                  client.player.fallDistance = prior;
                }
              }
            } catch (ReflectiveOperationException failure) {
              throw new IllegalStateException(failure);
            }
          });
      Harness.quiet(context, "controlled-" + boundary + "-guard");
    }
    Harness.command(context, "off");
  }
}
