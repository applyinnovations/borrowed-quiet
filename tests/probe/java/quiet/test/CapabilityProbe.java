package quiet.test;

import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;

public final class CapabilityProbe implements FabricClientGameTest {
    @Override
    public void runTest(ClientGameTestContext context) {
        try (var world = context.worldBuilder().create()) {
            context.runOnClient(client -> {
                client.options.renderDistance().set(4);
                client.options.framerateLimit().set(30);
            });
            world.getClientLevel().waitForChunksRender();
            world.getServer().runCommand("gamemode survival @a");
            world.getServer().runCommand("time set day");
            context.takeScreenshot("capability-before");
            double before = context.computeOnClient(client -> client.player.getZ());
            context.getInput().lookAt(0, 0);
            context.getInput().holdKeyFor(options -> options.keyUp, 40);
            double after = context.computeOnClient(client -> client.player.getZ());
            if (Math.abs(after - before) < 1) throw new AssertionError("Movement failed");
            world.getServer().runCommand("execute at @a run playsound minecraft:block.amethyst_block.chime master @a ~2 ~ ~ 0.5 1");
            context.waitTicks(100);
            context.runOnClient(client -> System.out.println("CAPABILITY_AUDIO master="
                    + client.options.getSoundSourceVolume(net.minecraft.sounds.SoundSource.MASTER)
                    + " listener=" + client.getSoundManager().getListenerTransform()
                    + " player=" + client.player.position()));
            world.getServer().runCommand("execute at @a run playsound minecraft:entity.cow.ambient master @a ~ ~ ~ 1 1");
            context.waitTicks(80);
            world.getServer().runCommand("execute at @a run playsound minecraft:block.note_block.bell master @a ~ ~ ~ 1 1");
            context.waitTicks(80);
            context.takeScreenshot("capability-after");
            context.runOnClient(client -> System.out.println("CAPABILITY_METRICS fps=" + client.getFps()
                    + " frameNs=" + client.getFrameTimeNs() + " heap="
                    + (Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory())
                    + " tickNs=" + client.getSingleplayerServer().getAverageTickTimeNanos()));
            System.out.println("CAPABILITY_GAMEPLAY_PASS distance=" + Math.abs(after - before));
        }
    }
}
