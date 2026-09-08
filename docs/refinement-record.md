# Internal refinement record

These are development findings, not release passes. Final acceptance must use the
affected checks rerun on the identified package and capture configuration.

| Finding | Resolution / evidence status |
|---|---|
| Original authorised runtime access unavailable | User authorised offline developer launch; actual graphical Minecraft capability was established before gameplay implementation. Historical preflight remains distinguishable. |
| Host GLX libraries failed the isolated renderer | Pinned Mesa/libGL/X11 libraries in the Nix shell; actual client launch and capture subsequently succeeded. |
| An early capture contained silence from the wrong sink | Private PulseAudio null sink plus own-process routing. Silent capture rejected, not treated as listening evidence. |
| Concurrent private audio servers contested the session bus | Each capture now owns a private D-Bus session using the pinned configuration file. No host audio or microphone is recorded. |
| First tread recipe had an overly tonal component | Replaced tread oscillators with seeded filtered noise; all derived sound inspections invalidated for those files. |
| Qwen2.5 listening descriptions inconsistently called varied clips a single beep | Rejected as sufficient audio acceptance; acquired a separately pinned Qwen3 audio-input model for a new calibrated review. No fabricated native hearing or human response. |
| Fold completion cut a sound tail | Geometry removal separated from final sound cleanup; finite voice lifetimes include low-pitch playback. Functional suite rerun on corrected package. |
| Blind visual reviewer found uncertain grounding and an abstract/possibly unfinished reading | Added a bounded base shadow and visible-ground line-of-sight placement. Natural-context review remains necessary; an isolated daylight showcase does not prove atmosphere. |
| Four camera views accidentally rotated the object along with the observer | Fixed the test to instantiate at a fixed orientation, then aim each camera separately. Earlier screenshots were not accepted as distinct model-angle coverage. |
| Input devices' independent timestamp resets displaced captured audio by roughly 1.5 seconds | Added FFmpeg `-isync 0`, retained actual device start timestamps, and reran presentation. Earlier recordings are marked unsynchronized experimental evidence. |
| Normal-world fixtures initially issued fill commands into unloaded chunks | Load fixture region first in spectator mode, then return to Survival for actual input/state assertions. Three seed runs passed. |
| Placement/young-crop aim used block centre instead of the actual surface | Corrected input ray targeting; real placement, growth, harvest and inventory checks passed. |
| Damage command used a multi-target selector for a single-entity argument | Corrected test command; damage/health interruption then passed. |
| Removal test assumed a world folder named `world` | Discover the single generated fixture directory; copied-save removal startup passed without the mod jar. |
| Claimed simulation distance 4 was below 26.2's accepted minimum | Recorded the technical correction to 5 for both benchmark conditions before endurance. No performance or duration criterion relaxed. |
| A failed placement could overwrite repetition history and allow two actual identical episodes | History now commits only after presentation successfully starts. Added 30,000 failure/repetition assertions; rerun affected functional and natural validation. |
| Natural work loop aimed before a preceding teleport reached the client | Wait for client ticks before the aim ray and assert the actual workpiece is mined every cycle. The preliminary recording is rejected as sustained mining evidence. |

The synchronization change follows the [FFmpeg input synchronization documentation](https://ffmpeg.org/ffmpeg.html):
the reference input's start time is used to preserve the difference between devices
that share a timestamp clock. Actual onsets and rendered subtitles still require
verification; specifying a flag alone is not a synchronization pass.
