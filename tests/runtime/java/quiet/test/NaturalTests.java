package quiet.test;

import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.levelgen.Heightmap;

/** Unaccelerated ordinary-work recording. No mod triggers, seed changes or cooldown edits. */
public final class NaturalTests {
  private NaturalTests() {}

  public static void run(ClientGameTestContext context, TestSingleplayerContext world) {
    world.getServer().runCommand("gamemode spectator @a");
    world.getServer().runCommand("tp @a 0.5 150 0.5");
    context.waitTicks(100);
    world.getClientLevel().waitForChunksRender();
    int ground =
        world
            .getServer()
            .computeOnServer(
                server ->
                    server.overworld().getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, 0, 0));
    world
        .getServer()
        .runCommand("fill -16 " + (ground - 1) + " -16 16 " + (ground - 1) + " 16 grass_block");
    world.getServer().runCommand("fill -16 " + ground + " -16 16 " + (ground + 5) + " 16 air");
    world.getServer().runCommand("fill -9 " + ground + " -5 -9 " + (ground + 3) + " 5 oak_planks");
    world.getServer().runCommand("fill -9 " + ground + " -5 -3 " + (ground + 3) + " -5 oak_planks");
    world.getServer().runCommand("fill -9 " + ground + " 5 -3 " + (ground + 3) + " 5 oak_planks");
    world
        .getServer()
        .runCommand("fill -9 " + (ground + 4) + " -5 -3 " + (ground + 4) + " 5 oak_slab");
    world.getServer().runCommand("setblock -6 " + ground + " 0 crafting_table");
    for (int x : new int[] {-12, 0, 12})
      for (int z : new int[] {-12, 0, 12})
        world.getServer().runCommand("setblock " + x + " " + ground + " " + z + " torch");
    world.getServer().runCommand("fill 6 " + ground + " -6 6 " + (ground + 3) + " 6 stone");
    world.getServer().runCommand("difficulty peaceful");
    world.getServer().runCommand("time set 10000");
    world.getServer().runCommand("gamemode survival @a");
    world.getServer().runCommand("tp @a 0.5 " + ground + " 0.5 0 0");
    world.getServer().runCommand("item replace entity @a hotbar.0 with iron_pickaxe");
    context.waitTicks(30);
    long start = System.nanoTime();
    int cycles = 0;
    while (System.nanoTime() - start < 1800_000_000_000L) {
      // Restore the finite test workpiece, then mine it using real survival input.
      world.getServer().runCommand("setblock 3 " + ground + " 0 stone");
      context.waitTicks(10); // Receive the preceding server teleport before computing the aim ray.
      context.getInput().lookAt(new BlockPos(3, ground, 0));
      context.getInput().holdMouseFor(0, 55);
      if (!world
          .getServer()
          .computeOnServer(
              server -> server.overworld().getBlockState(new BlockPos(3, ground, 0)).isAir()))
        throw new AssertionError("Natural workpiece was not mined");
      context.waitTicks(100);
      for (int direction = 0; direction < 4; direction++) {
        context.getInput().lookAt(direction * 90, 0);
        context.getInput().holdKeyFor(options -> options.keyUp, 45);
        context.waitTicks(70);
        context.getInput().lookAt(direction * 90 + 160, 0);
        context.waitTicks(50);
      }
      if (++cycles % 5 == 0) context.takeScreenshot("natural-work-" + cycles);
      // Re-establish the work station after bounded input drift, without resetting mod state.
      world.getServer().runCommand("tp @a 0.5 " + ground + " 0.5 0 0");
      if (cycles % 15 == 0)
        world.getServer().runCommand("item replace entity @a hotbar.0 with iron_pickaxe");
    }
    System.out.println("NATURAL_PASS elapsed_ns=" + (System.nanoTime() - start));
  }
}
