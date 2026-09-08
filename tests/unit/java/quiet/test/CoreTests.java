package quiet.test;

import quiet.ConfigStore;
import quiet.core.Director;
import quiet.core.Settings;

public final class CoreTests {
  private static long assertions;

  private static void check(boolean value, String message) {
    assertions++;
    if (!value) throw new AssertionError(message);
  }

  private static void reject(String json) {
    try {
      ConfigStore.parse(json);
      throw new AssertionError("Accepted malformed configuration: " + json);
    } catch (RuntimeException expected) {
      assertions++;
    }
  }

  public static void main(String[] arguments) throws java.io.IOException {
    for (var intensity : Director.Intensity.values()) {
      for (int seed = 0; seed < 64; seed++) {
        Director first = new Director(seed), second = new Director(seed);
        int pause = first.remaining();
        for (int tick = 0; tick < 400; tick++)
          check(first.tick(false, true, true, true, intensity) == null, "ineligible event");
        check(first.remaining() == pause, "paused countdown");
        Director.Kind previous = null;
        for (int tick = 0; tick < 100000; tick++) {
          boolean pace = tick % 131 < 70;
          boolean wall = tick % 197 < 100;
          boolean fold = tick % 67 == 0;
          var a = first.tick(true, pace, wall, fold, intensity);
          var b = second.tick(true, pace, wall, fold, intensity);
          check(a == b && first.remaining() == second.remaining(), "deterministic replay");
          check(first.remaining() >= 0 && first.remaining() <= 10800, "countdown bounds");
          if (a != null) {
            check(tick >= 2400, "warm-up");
            check(a != previous, "consecutive repetition");
            check(
                switch (a) {
                  case PACE -> pace;
                  case WALL -> wall;
                  case FOLD -> fold;
                },
                "context");
            check(first.remaining() >= 1800, "recovery floor");
            previous = a;
            first.started(a);
            second.started(b);
          }
        }
        first.interrupt();
        check(first.remaining() >= 1800, "interruption floor");
      }
    }
    Director empty = new Director(0);
    for (int tick = 0; tick < 100000; tick++)
      check(
          empty.tick(true, false, false, false, Director.Intensity.NORMAL) == null,
          "empty context");
    Director failedPlacement = new Director(1);
    failedPlacement.started(Director.Kind.PACE);
    for (int tick = 0; tick < 20000; tick++) {
      failedPlacement.tick(true, false, true, true, Director.Intensity.INTENSE);
      check(
          failedPlacement.previous() == Director.Kind.PACE,
          "failed placement must not erase actual previous episode");
    }
    for (int tick = 0; tick < 10000; tick++)
      check(
          failedPlacement.tick(true, true, false, false, Director.Intensity.INTENSE) == null,
          "failed alternate placements cannot permit consecutive actual repetition");
    check(ConfigStore.parse("{}").equals(Settings.DEFAULT), "defaults");
    check(
        !ConfigStore.parse("{\"enabled\":false,\"future\":17}").enabled(), "unknown key tolerance");
    for (String json :
        new String[] {
          "[]",
          "null",
          "{",
          "{\"enabled\":\"false\"}",
          "{\"volume\":-0.1}",
          "{\"volume\":1.1}",
          "{\"volume\":\"0.7\"}",
          "{\"intensity\":\"unsafe\"}",
          "{\"visuals\":null}",
          "{\"version\":2}"
        }) reject(json);
    try {
      new Settings(true, Director.Intensity.NORMAL, Double.NaN, true, false);
      throw new AssertionError("NaN");
    } catch (IllegalArgumentException expected) {
      assertions++;
    }
    configFiles();
    System.out.println(
        "PASS: "
            + assertions
            + " assertions across 19,200,000 seeded transitions and config cases.");
  }

  private static void configFiles() throws java.io.IOException {
    var directory = java.nio.file.Files.createTempDirectory("borrowedquiet-config-test-");
    var path = directory.resolve("borrowedquiet.json");
    var logger = org.slf4j.helpers.NOPLogger.NOP_LOGGER;
    try {
      java.nio.file.Files.writeString(path, "{broken");
      try (var store = new ConfigStore(path, logger)) {
        check(!store.read().enabled(), "malformed config fails disabled");
        for (int update = 0; update < 10000; update++)
          store.save(new Settings(update % 2 == 0, Director.Intensity.GENTLE, 0.2, false, true));
        store.save(Settings.DEFAULT);
      }
      check(
          ConfigStore.parse(java.nio.file.Files.readString(path)).equals(Settings.DEFAULT),
          "latest config retained after bounded queue stress");
      try (var files = java.nio.file.Files.list(directory)) {
        check(
            files.anyMatch(file -> file.getFileName().toString().contains(".invalid-")),
            "bad original preserved");
      }
      java.nio.file.Files.writeString(
          directory.resolve("borrowedquiet.json.tmp"), "interrupted write");
      try (var store = new ConfigStore(path, logger)) {
        check(store.read().equals(Settings.DEFAULT), "interrupted temporary write ignored");
      }
      java.nio.file.Files.writeString(path, "x".repeat(8193));
      try (var store = new ConfigStore(path, logger)) {
        check(!store.read().enabled(), "oversized config fails disabled");
      }
    } finally {
      try (var files = java.nio.file.Files.list(directory)) {
        for (var file : files.toList()) java.nio.file.Files.delete(file);
      }
      java.nio.file.Files.delete(directory);
    }
  }
}
