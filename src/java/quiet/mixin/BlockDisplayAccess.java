package quiet.mixin;

import net.minecraft.world.entity.Display;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

@Mixin(value = Display.BlockDisplay.class, remap = false)
public interface BlockDisplayAccess {
  @Invoker("setBlockState")
  void quietBlock(BlockState state);
}
