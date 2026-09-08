# Architecture, safety and rights

`Director` is a pure deterministic SplitMix64 state machine: bounded quiet periods,
context eligibility and no consecutive identical kind. A missed placement is not
an accumulated event debt. State is session-local; reopening resets warm-up.

`BorrowedQuiet` adapts client context/input, retaining at most 32 trail positions.
Ground search checks at most 24 loaded candidates and 16 short sight rays; wall
selection uses eight rays. The mod has no server tick callback, custom packet,
chunk request, world write, damage or pathfinding.

`Presentation` owns two sound instances and three client-local vanilla block
displays at most. Displays have no collision; negative local ids are checked
before insertion and removal verifies object identity. They never reach the server
or save. The original charcoal geometry references vanilla concrete at runtime;
no Minecraft texture is redistributed. Normal recognition contracts over 18 ticks,
then geometry disappears while the finite sound tail finishes. Reduced motion
skips contraction. Any interruption stops sound and geometry together.

`ConfigStore` reads only its bounded JSON and writes only that file and recoverable
sibling files. A single background writer and one-slot coalescing queue bound
pending work. Atomic replacement avoids partial overwrites; unsupported replacement
reports failure. Malformed input is preserved and disables the experience.
Shutdown waits at most two seconds, outside active gameplay. Resource reload,
unsafe contexts, settings and world changes explicitly clear presentation.
Minecraft's volume controls remain authoritative. No AI model, analytics,
external service, private-file inspection or account access exists at runtime.

## Provenance and distribution

Source, six synthesized sounds, lossless masters, geometry and documentation are
original project work under [MIT](../LICENSE). Fixed-seed synthesis code is the
editable sound original. There are no commissioned, borrowed-character or
uncertain-provenance game assets. Every sound is mapped in the asset register;
geometry also requires direct rendered-inspection evidence before acceptance.

The player jar contains original classes, loader/mixin metadata, English subtitles,
sound declarations, six OGGs and the project licence. No Minecraft classes,
textures/music, client/server jar, test harness, model weights or Fabric API are
included. Dependencies retain their upstream licences and are obtained from their
publishers. No blanket project licence overrides those terms.

Minecraft belongs to Mojang/Microsoft. Local runtime downloads and generated worlds
are validation inputs. Gameplay recordings are inspection evidence, not playable
Minecraft software. The [EULA](https://www.minecraft.net/en-us/eula) and
[usage guidelines](https://www.minecraft.net/en-us/usage-guidelines) govern external
publication. This project is independent and not endorsed.

Acceptance review on 8 September 2026: distribute this original mod free, not a
modified Minecraft client/server; require genuine player installations; provide no
external ownership checks, paid unlocks or play-to-earn features. Inspection footage
is free to view and is not sold or used to advertise an unrelated product. Minecraft
is a descriptive compatibility reference, not the dominant product name or copied
logo. The final release check fingerprints the current EULA/usage pages and verifies
the official manifest's stable version. This is a project compliance assessment,
not a claim of Mojang approval or professional legal advice.

Nix, Fabric, Java, FFmpeg, llama.cpp and other tools retain upstream terms, available
with their pinned packages. Audio-input models are development inspection tools,
not shipped assets. Initial model-conversion licence distinctions and rejected
listening experiments are preserved in preflight/research records. Generated
descriptions are AI assessments, never performer recordings or human testimony.
No third-party CC BY game asset is shipped and no required external asset credit
is silently omitted.
