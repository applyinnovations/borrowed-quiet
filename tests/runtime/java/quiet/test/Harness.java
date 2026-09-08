package quiet.test;

import net.fabricmc.fabric.api.client.command.v2.ClientCommands;
import net.fabricmc.fabric.api.client.command.v2.FabricClientCommandSource;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;

public final class Harness {
  private Harness() {}

  public static long[] state() {
    try {
      return (long[]) Class.forName("quiet.BorrowedQuiet").getMethod("diagnostics").invoke(null);
    } catch (ReflectiveOperationException failure) {
      throw new IllegalStateException(failure);
    }
  }

  public static boolean trigger(String kind, double x, double y, double z) {
    try {
      return (boolean)
          Class.forName("quiet.BorrowedQuiet")
              .getMethod("testTrigger", String.class, double.class, double.class, double.class)
              .invoke(null, kind, x, y, z);
    } catch (ReflectiveOperationException failure) {
      throw new IllegalStateException(failure);
    }
  }

  public static void command(ClientGameTestContext context, String command) {
    context.runOnClient(
        client -> {
          try {
            ClientCommands.getActiveDispatcher()
                .execute(
                    "borrowedquiet " + command,
                    (FabricClientCommandSource) client.getConnection().getSuggestionsProvider());
          } catch (com.mojang.brigadier.exceptions.CommandSyntaxException failure) {
            throw new IllegalStateException(failure);
          }
        });
    context.waitTicks(4);
  }

  public static void quiet(ClientGameTestContext context, String reason) {
    context.runOnClient(
        client -> {
          long[] state = state();
          if (state[1] != 0 || state[2] != 0 || state[5] != -1)
            throw new AssertionError("Cleanup: " + reason);
        });
    System.out.println("LIFECYCLE_PASS " + reason);
  }

  public static void startBehind(ClientGameTestContext context, String kind) {
    context.runOnClient(
        client -> {
          var point = client.player.position().subtract(client.player.getLookAngle().scale(6));
          if (!trigger(kind, point.x, client.player.getY(), point.z))
            throw new AssertionError(
                "Trigger "
                    + kind
                    + " screen="
                    + client.gui.screen()
                    + " overlay="
                    + client.gui.overlay()
                    + " paused="
                    + client.isPaused()
                    + " health="
                    + client.player.getHealth()
                    + " mode="
                    + client.gameMode.getPlayerMode());
        });
    context.waitTicks(2);
  }
}
