package quiet.test;

import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.core.BlockPos;
import net.minecraft.world.inventory.ContainerInput;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CropBlock;

/** Actual survival actions on an isolated fixture in a normally generated world. */
public final class OrdinaryTests {
  private OrdinaryTests() {}

  private static void select(ClientGameTestContext context, int slot) {
    context.runOnClient(client -> client.player.getInventory().setSelectedSlot(slot));
    context.waitTicks(4);
  }

  private static void aim(ClientGameTestContext context, double x, double y, double z) {
    var eye = context.computeOnClient(client -> client.player.getEyePosition());
    double dx = x - eye.x, dy = y - eye.y, dz = z - eye.z;
    context
        .getInput()
        .lookAt(
            (float) Math.toDegrees(-Math.atan2(dx, dz)),
            (float) Math.toDegrees(-Math.atan2(dy, Math.hypot(dx, dz))));
    context.waitTicks(3);
  }

  public static void run(ClientGameTestContext context, TestSingleplayerContext world) {
    world.getServer().runCommand("gamemode spectator @a");
    world.getServer().runCommand("tp @a 0.5 102 0.5 0 0");
    context.waitTicks(100);
    world.getClientLevel().waitForChunksRender();
    world.getServer().runCommand("fill -10 99 -10 10 99 10 stone");
    world.getServer().runCommand("fill -10 100 -10 10 105 10 air");
    world.getServer().runCommand("tp @a 0.5 100 0.5 0 0");
    world.getServer().runCommand("item replace entity @a hotbar.0 with iron_pickaxe");
    world.getServer().runCommand("setblock 0 100 3 stone");
    world.getServer().runCommand("gamemode survival @a");
    context.waitTicks(30);
    Harness.startBehind(context, "WALL");
    context.getInput().lookAt(new BlockPos(0, 100, 3));
    context.getInput().holdMouseFor(0, 50);
    context.waitTicks(8);
    if (!world
        .getServer()
        .computeOnServer(
            server -> server.overworld().getBlockState(new BlockPos(0, 100, 3)).isAir()))
      throw new AssertionError("Survival mining");
    System.out.println("ORDINARY_PASS mining");

    world.getServer().runCommand("item replace entity @a hotbar.1 with oak_planks 16");
    select(context, 1);
    aim(context, 0.5, 100.001, 3.5);
    context.getInput().pressMouse(1);
    context.waitTicks(10);
    if (!world
        .getServer()
        .computeOnServer(
            server ->
                server.overworld().getBlockState(new BlockPos(0, 100, 3)).is(Blocks.OAK_PLANKS)))
      throw new AssertionError("Survival placement");
    System.out.println("ORDINARY_PASS building");

    world.getServer().runCommand("setblock 3 99 0 farmland[moisture=7]");
    world.getServer().runCommand("setblock 4 99 0 water");
    world.getServer().runCommand("item replace entity @a hotbar.2 with wheat_seeds 16");
    select(context, 2);
    aim(context, 3.5, 99.938, 0.5);
    context.getInput().pressMouse(1);
    context.waitTicks(10);
    if (!world
        .getServer()
        .computeOnServer(
            server -> server.overworld().getBlockState(new BlockPos(3, 100, 0)).is(Blocks.WHEAT)))
      throw new AssertionError("Planting");
    world.getServer().runCommand("item replace entity @a hotbar.3 with bone_meal 16");
    select(context, 3);
    aim(context, 3.5, 100.03, 0.5);
    for (int i = 0; i < 8; i++) {
      context.getInput().pressMouse(1);
      context.waitTicks(4);
    }
    if (!world
        .getServer()
        .computeOnServer(
            server ->
                server.overworld().getBlockState(new BlockPos(3, 100, 0)).getValue(CropBlock.AGE)
                    == 7)) throw new AssertionError("Crop growth");
    context.getInput().holdMouseFor(0, 20);
    context.getInput().lookAt(-90, 0);
    context.getInput().holdKeyFor(options -> options.keyUp, 20);
    context.waitTicks(20);
    if (!context.computeOnClient(
        client -> client.player.getInventory().contains(stack -> stack.is(Items.WHEAT))))
      throw new AssertionError("Harvest pickup");
    System.out.println("ORDINARY_PASS farming");

    world.getServer().runCommand("tp @a 0.5 100 0.5 0 0");
    world.getServer().runCommand("item replace entity @a hotbar.4 with iron_sword");
    world.getServer().runCommand("summon husk 0.5 100 2.5 {NoAI:1b,Tags:[\"quiet_target\"]}");
    context.waitTicks(10);
    if (!world
        .getServer()
        .computeOnServer(
            server -> {
              for (var entity : server.overworld().getAllEntities())
                if (entity.getType() == net.minecraft.world.entity.EntityTypes.HUSK
                    && entity.getY() >= 99
                    && entity.isAlive()) return true;
              return false;
            })) throw new AssertionError("Combat target did not spawn");
    select(context, 4);
    context.getInput().lookAt(new BlockPos(0, 101, 2));
    for (int i = 0; i < 6; i++) {
      context.getInput().pressMouse(0);
      context.waitTicks(24);
    }
    boolean alive =
        world
            .getServer()
            .computeOnServer(
                server -> {
                  for (var entity : server.overworld().getAllEntities())
                    if (entity.getType() == net.minecraft.world.entity.EntityTypes.HUSK
                        && entity.getY() >= 99
                        && entity.isAlive()) return true;
                  return false;
                });
    if (alive) throw new AssertionError("Combat target survived");
    System.out.println("ORDINARY_PASS combat");

    world.getServer().runCommand("item replace entity @a hotbar.5 with oak_log");
    context.waitTicks(8);
    context.setScreen(
        () -> new InventoryScreen(net.minecraft.client.Minecraft.getInstance().player));
    context.waitTicks(4);
    context.runOnClient(
        client -> {
          client.gameMode.handleContainerInput(0, 41, 0, ContainerInput.PICKUP, client.player);
          client.gameMode.handleContainerInput(0, 1, 0, ContainerInput.PICKUP, client.player);
        });
    context.waitTicks(10);
    if (!context.computeOnClient(
        client -> client.player.inventoryMenu.getSlot(0).getItem().is(Items.OAK_PLANKS)))
      throw new AssertionError("Crafting recipe output");
    context.runOnClient(
        client ->
            client.gameMode.handleContainerInput(
                0, 0, 0, ContainerInput.QUICK_MOVE, client.player));
    context.waitTicks(10);
    if (!context.computeOnClient(
        client -> client.player.inventoryMenu.getSlot(1).getItem().isEmpty()))
      throw new AssertionError("Crafting consumption");
    context.setScreen(() -> null);
    System.out.println("ORDINARY_PASS crafting-progression");
    context.takeScreenshot("ordinary-fixture-complete");
    double before = context.computeOnClient(client -> client.player.getX());
    context.getInput().lookAt(90, 0);
    context.getInput().holdKeyFor(options -> options.keyUp, 25);
    double after = context.computeOnClient(client -> client.player.getX());
    if (Math.abs(after - before) < 2) throw new AssertionError("Exploration movement");
    System.out.println(
        "ORDINARY_PASS exploration seed=" + System.getProperty("borrowedquiet.test.seed"));
  }
}
