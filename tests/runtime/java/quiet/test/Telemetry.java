package quiet.test;

import java.io.IOException;
import java.io.PrintWriter;
import java.lang.reflect.Method;
import java.nio.file.Files;
import java.nio.file.Path;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.minecraft.client.Minecraft;

/** Test instrumentation only; same callback and buffered recording in both benchmark conditions. */
public final class Telemetry implements AutoCloseable {
  private final PrintWriter output;
  private final long started = System.nanoTime();
  private final Method diagnostic;
  private boolean enabled = true;
  private int ticks;

  public Telemetry(Path path) throws IOException, ReflectiveOperationException {
    output = new PrintWriter(Files.newBufferedWriter(path));
    Method method;
    try {
      method = Class.forName("quiet.BorrowedQuiet").getMethod("diagnostics");
    } catch (ClassNotFoundException absent) {
      method = null;
    }
    diagnostic = method;
    output.println("seconds,frame_ns,tick_ns,heap_bytes,mod_ns,sounds,entities,trail,episodes");
    ClientTickEvents.END_CLIENT_TICK.register(this::sample);
  }

  private void sample(Minecraft client) {
    if (!enabled || client.player == null || client.getSingleplayerServer() == null) return;
    try {
      long[] mod = diagnostic == null ? new long[5] : (long[]) diagnostic.invoke(null);
      if (mod[1] > 2 || mod[2] > 3 || mod[3] > 32) throw new AssertionError("Resource cap");
      output.printf(
          java.util.Locale.ROOT,
          "%.4f,%d,%d,%d,%d,%d,%d,%d,%d%n",
          (System.nanoTime() - started) / 1e9,
          client.getFrameTimeNs(),
          client.getSingleplayerServer().getAverageTickTimeNanos(),
          Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory(),
          mod[0],
          mod[1],
          mod[2],
          mod[3],
          mod[4]);
      if (++ticks % 100 == 0) output.flush();
    } catch (ReflectiveOperationException failure) {
      throw new IllegalStateException(failure);
    }
  }

  @Override
  public void close() {
    enabled = false;
    output.close();
  }

  public void check() {
    if (output.checkError()) throw new IllegalStateException("Telemetry write failed");
  }
}
