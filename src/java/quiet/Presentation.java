package quiet;

import com.mojang.math.Transformation;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Display;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import quiet.mixin.BlockDisplayAccess;
import quiet.mixin.DisplayAccess;

/** Owns only local, non-colliding presentation; no server entity or block writes. */
public final class Presentation {
  private record Voice(SimpleSoundInstance sound, int expires) {}

  private final List<Voice> voices = new ArrayList<>(2);
  private final List<Display.BlockDisplay> folds = new ArrayList<>(3);
  private ClientLevel foldLevel;
  private int clock;
  private int nextId = -1700000000;

  public void tick(Minecraft client) {
    clock++;
    voices.removeIf(
        voice -> {
          if (clock >= voice.expires()) {
            client.getSoundManager().stop(voice.sound());
            return true;
          }
          return false;
        });
  }

  public void sound(Minecraft client, String name, Vec3 at, double volume, float pitch) {
    if (volume <= 0 || voices.size() >= 2) return;
    var sound =
        new SimpleSoundInstance(
            SoundEvent.createVariableRangeEvent(
                Identifier.fromNamespaceAndPath("borrowedquiet", name)),
            SoundSource.AMBIENT,
            (float) Math.min(0.6, volume),
            pitch,
            RandomSource.create(0),
            at.x,
            at.y,
            at.z);
    client.getSoundManager().play(sound);
    int duration =
        switch (name) {
          case "scrape" -> 38;
          case "fold" -> 30;
          default -> 12;
        };
    voices.add(new Voice(sound, clock + duration));
  }

  public boolean showFold(Minecraft client, Vec3 at, float yaw) {
    if (!folds.isEmpty()) return false;
    foldLevel = client.level;
    for (int part = 0; part < 3; part++) {
      int id = nextId++;
      if (foldLevel.getEntity(id) != null) {
        clear(client);
        return false;
      }
      var display = new Display.BlockDisplay(EntityTypes.BLOCK_DISPLAY, foldLevel);
      display.setId(id);
      display.noPhysics = true;
      display.setPos(at.x, at.y, at.z);
      display.setYRot(yaw);
      ((BlockDisplayAccess) display).quietBlock(Blocks.CONCRETE.black().defaultBlockState());
      ((DisplayAccess) display).quietTransform(transform(part, 1));
      if (part == 0) {
        ((DisplayAccess) display).quietShadowRadius(0.4f);
        ((DisplayAccess) display).quietShadowStrength(0.65f);
      }
      foldLevel.addEntity(display);
      folds.add(display);
    }
    return true;
  }

  private static Transformation transform(int part, float width) {
    float[] x = {-0.21f, 0.13f, -0.12f};
    float[] y = {0, 0.83f, 1.75f};
    float[] lean = {-0.24f, 0.36f, -0.31f};
    return new Transformation(
        new Vector3f(x[part] * width, y[part], 0),
        new Quaternionf().rotateZ(lean[part] * width),
        new Vector3f(0.32f * width, 1.1f, 0.14f * width),
        new Quaternionf());
  }

  public void contract() {
    for (int part = 0; part < folds.size(); part++) {
      DisplayAccess access = (DisplayAccess) folds.get(part);
      access.quietDuration(18);
      access.quietDelay(0);
      access.quietTransform(transform(part, 0.025f));
    }
  }

  public void clear(Minecraft client) {
    for (Voice voice : voices) client.getSoundManager().stop(voice.sound());
    voices.clear();
    hideFold();
  }

  public void hideFold() {
    for (var fold : folds) {
      if (foldLevel != null && foldLevel.getEntity(fold.getId()) == fold)
        foldLevel.removeEntity(fold.getId(), Entity.RemovalReason.DISCARDED);
    }
    folds.clear();
    foldLevel = null;
  }

  public int sounds() {
    return voices.size();
  }

  public int entities() {
    return folds.size();
  }
}
