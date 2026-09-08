package quiet;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import quiet.core.Director;
import quiet.core.Settings;

/** Only the mod's configuration is read/written, never player options or world data. */
public final class ConfigStore implements AutoCloseable {
  private final Path path;
  private final Logger log;
  private final ThreadPoolExecutor writer;
  private volatile boolean invalid;

  public ConfigStore(Path path, Logger log) {
    this.path = path;
    this.log = log;
    writer =
        new ThreadPoolExecutor(
            1,
            1,
            0,
            TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(1),
            runnable -> {
              Thread thread = new Thread(runnable, "Borrowed Quiet config");
              thread.setDaemon(true);
              return thread;
            },
            new ThreadPoolExecutor.DiscardOldestPolicy());
  }

  public Settings read() {
    if (!Files.exists(path)) return Settings.DEFAULT;
    try {
      if (Files.size(path) > 8192) throw new IOException("Configuration exceeds 8 KiB");
      return parse(Files.readString(path));
    } catch (RuntimeException | IOException failure) {
      invalid = true;
      log.warn(
          "Borrowed Quiet: invalid configuration preserved; experience disabled. {}",
          failure.getMessage());
      return new Settings(
          false, Settings.DEFAULT.intensity(), Settings.DEFAULT.volume(), true, false);
    }
  }

  public static Settings parse(String text) {
    JsonObject object = JsonParser.parseString(text).getAsJsonObject();
    if (number(object, "version", 1) != 1)
      throw new IllegalArgumentException("Unsupported configuration version");
    Settings defaults = Settings.DEFAULT;
    return new Settings(
        bool(object, "enabled", defaults.enabled()),
        object.has("intensity")
            ? Director.Intensity.valueOf(
                string(object, "intensity").toUpperCase(java.util.Locale.ROOT))
            : defaults.intensity(),
        number(object, "volume", defaults.volume()),
        bool(object, "visuals", defaults.visuals()),
        bool(object, "reducedMotion", defaults.reducedMotion()));
  }

  private static boolean bool(JsonObject object, String key, boolean fallback) {
    if (!object.has(key)) return fallback;
    if (!object.get(key).isJsonPrimitive() || !object.getAsJsonPrimitive(key).isBoolean())
      throw new IllegalArgumentException(key + " must be boolean");
    return object.get(key).getAsBoolean();
  }

  private static double number(JsonObject object, String key, double fallback) {
    if (!object.has(key)) return fallback;
    if (!object.get(key).isJsonPrimitive() || !object.getAsJsonPrimitive(key).isNumber())
      throw new IllegalArgumentException(key + " must be numeric");
    return object.get(key).getAsDouble();
  }

  private static String string(JsonObject object, String key) {
    if (!object.get(key).isJsonPrimitive() || !object.getAsJsonPrimitive(key).isString())
      throw new IllegalArgumentException(key + " must be a string");
    return object.get(key).getAsString();
  }

  public void save(Settings settings) {
    writer.execute(
        () -> {
          Path temporary = path.resolveSibling(path.getFileName() + ".tmp");
          try {
            Files.createDirectories(path.getParent());
            if (invalid && Files.exists(path)) {
              Files.move(
                  path,
                  path.resolveSibling(
                      path.getFileName() + ".invalid-" + System.currentTimeMillis()));
              invalid = false;
            }
            JsonObject object = new JsonObject();
            object.addProperty("version", 1);
            object.addProperty("enabled", settings.enabled());
            object.addProperty(
                "intensity", settings.intensity().name().toLowerCase(java.util.Locale.ROOT));
            object.addProperty("volume", settings.volume());
            object.addProperty("visuals", settings.visuals());
            object.addProperty("reducedMotion", settings.reducedMotion());
            Files.writeString(temporary, object + "\n");
            Files.move(
                temporary,
                path,
                StandardCopyOption.ATOMIC_MOVE,
                StandardCopyOption.REPLACE_EXISTING);
          } catch (IOException failure) {
            log.warn("Borrowed Quiet settings could not be saved: {}", failure.getMessage());
          }
        });
  }

  @Override
  public void close() {
    writer.shutdown();
    try {
      if (!writer.awaitTermination(2, TimeUnit.SECONDS))
        log.warn(
            "Borrowed Quiet: settings writer did not finish before shutdown; previous file remains"
                + " recoverable.");
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
    }
  }
}
