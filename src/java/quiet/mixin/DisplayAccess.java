package quiet.mixin;

import com.mojang.math.Transformation;
import net.minecraft.world.entity.Display;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

@Mixin(value = Display.class, remap = false)
public interface DisplayAccess {
  @Invoker("setShadowRadius")
  void quietShadowRadius(float radius);

  @Invoker("setShadowStrength")
  void quietShadowStrength(float strength);

  @Invoker("setTransformation")
  void quietTransform(Transformation transformation);

  @Invoker("setTransformationInterpolationDuration")
  void quietDuration(int ticks);

  @Invoker("setTransformationInterpolationDelay")
  void quietDelay(int ticks);
}
