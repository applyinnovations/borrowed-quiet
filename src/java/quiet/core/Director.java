package quiet.core;

/** Pure bounded scheduling. One call is one eligible 20 Hz client tick. */
public final class Director {
  public enum Kind {
    PACE,
    WALL,
    FOLD
  }

  public enum Intensity {
    GENTLE(6000, 10800),
    NORMAL(3000, 6000),
    INTENSE(1800, 3600);
    final int minimum;
    final int maximum;

    Intensity(int minimum, int maximum) {
      this.minimum = minimum;
      this.maximum = maximum;
    }
  }

  private long random;
  private int remaining = 2400;
  private Kind previous;
  private long opportunities;

  public Director(long seed) {
    random = seed;
  }

  public int randomInt(int bound) {
    if (bound <= 0) throw new IllegalArgumentException("Positive bound required");
    random += 0x9e3779b97f4a7c15L;
    long value = random;
    value = (value ^ (value >>> 30)) * 0xbf58476d1ce4e5b9L;
    value = (value ^ (value >>> 27)) * 0x94d049bb133111ebL;
    return (int) Long.remainderUnsigned(value ^ (value >>> 31), bound);
  }

  public Kind tick(
      boolean eligible, boolean pace, boolean wall, boolean fold, Intensity intensity) {
    if (!eligible) return null;
    if (remaining > 0) {
      remaining--;
      return null;
    }
    opportunities++;
    Kind[] kinds = Kind.values();
    int offset = randomInt(kinds.length);
    for (int i = 0; i < kinds.length; i++) {
      Kind kind = kinds[(offset + i) % kinds.length];
      boolean available =
          switch (kind) {
            case PACE -> pace;
            case WALL -> wall;
            case FOLD -> fold;
          };
      if (kind != previous && available) {
        recover(intensity);
        return kind;
      }
    }
    remaining = 100 + randomInt(101); // Missed opportunity, never a forced punishment.
    return null;
  }

  public void recover(Intensity intensity) {
    remaining = intensity.minimum + randomInt(intensity.maximum - intensity.minimum + 1);
  }

  /** Placement can fail; only an actually presented episode changes repetition history. */
  public void started(Kind kind) {
    previous = java.util.Objects.requireNonNull(kind);
  }

  public void interrupt() {
    remaining = Math.max(remaining, 1800);
  }

  public int remaining() {
    return remaining;
  }

  public Kind previous() {
    return previous;
  }

  public long opportunities() {
    return opportunities;
  }
}
