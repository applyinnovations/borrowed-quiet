package quiet.test;

import java.nio.file.Files;
import java.nio.file.Path;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.world.TestWorldSave;
import net.fabricmc.fabric.impl.client.gametest.world.TestWorldSaveImpl;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;

public final class PersistenceTests {
  private PersistenceTests() {}

  public static void run(ClientGameTestContext context, boolean removal) {
    TestWorldSave saved;
    Path game = context.computeOnClient(client -> client.gameDirectory.toPath());
    if (removal) {
      try (var directories = Files.list(game.resolve("saves"))) {
        var worlds = directories.filter(Files::isDirectory).toList();
        if (worlds.size() != 1) throw new AssertionError("Expected one isolated saved fixture");
        saved = new TestWorldSaveImpl(context, worlds.getFirst());
      } catch (java.io.IOException failure) {
        throw new java.io.UncheckedIOException(failure);
      }
    } else {
      try (var world = context.worldBuilder().create()) {
        saved = world.getWorldSave();
        world.getServer().runCommand("gamemode survival @a");
        world.getServer().runCommand("setblock 2 -60 2 gold_block");
        world.getServer().runCommand("item replace entity @a hotbar.8 with diamond 3");
        context.waitTicks(30);
        Harness.startBehind(context, "FOLD");
        if (world
            .getServer()
            .computeOnServer(
                server -> {
                  for (var entity : server.overworld().getAllEntities())
                    if (entity instanceof net.minecraft.world.entity.Display) return true;
                  return false;
                })) throw new AssertionError("Client display leaked into integrated server");
        Harness.command(context, "off");
        context.waitTicks(30);
      }
      try {
        String settings = Files.readString(game.resolve("config/borrowedquiet.json"));
        if (!settings.contains("\"enabled\":false"))
          throw new AssertionError("Settings did not persist");
      } catch (java.io.IOException failure) {
        throw new java.io.UncheckedIOException(failure);
      }
    }
    try (var world = saved.open()) {
      context.waitTicks(30);
      if (!world
          .getServer()
          .computeOnServer(
              server ->
                  server.overworld().getBlockState(new BlockPos(2, -60, 2)).is(Blocks.GOLD_BLOCK)))
        throw new AssertionError("Saved marker changed");
      if (!context.computeOnClient(
          client ->
              client.player.getInventory().getItem(8).is(Items.DIAMOND)
                  && client.player.getInventory().getItem(8).getCount() == 3))
        throw new AssertionError("Saved inventory changed");
      if (!removal) Harness.quiet(context, "save-reopen-disabled");
      else {
        try {
          Class.forName("quiet.BorrowedQuiet");
          throw new AssertionError("Mod still installed in removal test");
        } catch (ClassNotFoundException expected) {
          System.out.println("REMOVAL_PASS preserved blocks and inventory");
        }
      }
      context.takeScreenshot(removal ? "removed-world" : "reopened-world");
    }
    System.out.println("PERSISTENCE_PASS saved=" + saved.getSaveDirectory());
  }
}
