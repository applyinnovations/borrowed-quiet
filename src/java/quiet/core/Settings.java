package quiet.core;

public record Settings(
    boolean enabled,
    Director.Intensity intensity,
    double volume,
    boolean visuals,
    boolean reducedMotion) {
  public static final Settings DEFAULT =
      new Settings(true, Director.Intensity.NORMAL, 0.7, true, false);

  public Settings {
    if (intensity == null || !Double.isFinite(volume) || volume < 0 || volume > 1)
      throw new IllegalArgumentException("Invalid Borrowed Quiet settings");
  }
}
