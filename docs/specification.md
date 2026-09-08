# Borrowed Quiet — complete delivery specification

Scope set 8 September 2026, before gameplay implementation. Version 1.0.0 is the
complete work described here, not a framework for later content. Acceptance is
strictly separate from specification: a requirement below is not a claim of a pass.

## Creative direction

**The world has learned when you stop.** Ordinary work leaves an acoustic impression
that something unseen tries to finish. The player is neither a chosen hero nor
trapped in a campaign. The mine, the farm and the unfinished house remain the point
of playing. An occasional impossible fold in familiar space gives the sounds a
possible author, without explaining it. No lore collectibles, compulsory objectives,
new dimension, combat monster, sanity meter or ending are part of this work.

The identity is dry, close-grained and restrained: dull footfalls, hollow answers,
a fibrous scrape, a narrow charcoal shape without a face. No speech, copyrighted
character references, flashing lights, camera seizure, visual noise overlay, music
replacement or deliberately broken-looking UI. Daylight is not absolute safety,
but ordinary environmental light and music are never suppressed.

## Supported environment

- Minecraft Java **26.2 stable**, Fabric Loader **0.19.3**, Fabric API
  **0.152.0+26.2**, Java **25**. Recheck official stable release at acceptance.
- Validated player and development platform: **Linux x86-64**, OpenGL, English
  (`en_us`). Other languages fall back to English. No untested platform claim.
- Ordinary local single-player Survival, all four difficulties. Existing and new
  vanilla worlds. Overworld events; Nether and End remain quiet recovery spaces.
- Creative, spectator, death screens, LAN-published worlds and remote servers:
  experience is inert, with deliberate cleanup. Multiplayer horror, hardcore,
  shaders, third-party resource packs and other gameplay mods are not advertised.
- Client-only mod: no server installation, networking protocol, server mutation or
  save migration. Vanilla world data remains removable without conversion.

## Complete content and systems

| ID | System | Behaviour and experiential function | Observable acceptance |
|---|---|---|---|
| F1 | Borrowed Pace | After sustained walking ends, 3–6 irregular footfalls continue along a nearby remembered trail. Looking towards the source cuts the imitation short. | Movement context required naturally; finite delayed sounds behind the player; turn response and cleanup visible in event log and stereo recording. |
| F2 | The Other Wall | Recent mining or block use is answered by two short clusters of taps from nearby solid space, sometimes displaced sideways. | Work context required naturally; bounded nearby loaded-position query; audible pause between clusters; no world block changes. |
| F3 | The Fold | Infrequently, an off-axis, angular charcoal fold stands in nearby clear space. Noticing or approaching it contracts it into a line, then nothing; a scrape links it to the earlier sound grammar. | Valid ground and loaded space; directly inspect multiple angles, daylight, darkness and collapse; no hitbox obstruction, damage, persistent entity or missing-texture appearance. |
| F4 | Director | One episode at a time. Context and seeded randomness choose opportunities, with no consecutive identical episode. A missed opportunity becomes quiet, not punishment. | Deterministic replay; eligibility, timing bounds, diversity and resource invariants tested across at least 100,000 generated transitions. |

Episode duration is at most **18 seconds**. New-world/session warm-up is **120 seconds**
of eligible play. Recovery after any episode is at least **90 seconds**. Normal
intervals are **150–300 seconds**; Gentle **300–540**; Intense **90–180**. Time stops
in pause/menu/ineligible states. No escalation without bound, no penalty for ignoring
an event, and no encounter summons or pursuit outside the bounded episode.

Interrupt on menus, disable, world change, remote/published session, death, sleep,
low health (five hearts or less), recent damage, substantial falling, or immersion
in fluid. Interruption stops all owned sounds and removes all owned presentation
objects by the next client tick. Resume only after recovery. Resource reload has
the same presentation cleanup. No promised effect is allowed to survive disabling.

## Controls, configuration and lifecycle

Client command `/borrowedquiet` provides help, status, on/off, intensity, volume
(0–1), visuals on/off and reduced-motion on/off. It needs no cheats or server
permission. Default: enabled, Normal, volume 0.7, visuals enabled, reduced motion
disabled. Reduced motion removes the fold immediately on recognition rather than
animating contraction. Vanilla subtitles label every custom sound and preserve
direction indicators. Vanilla master and ambient volume continue to apply.

Configuration is a versioned, bounded JSON file in the game's `config` directory.
Validate types/ranges, tolerate unknown keys for compatibility, preserve malformed
input rather than silently destroy it, disable the experience on malformed input,
and report one useful diagnostic. Write only
this mod's file, atomically off the game thread through a bounded queue. No player
volume settings, external files, accounts or credentials are read or changed.

Director and episodes are **session-local**, not saved entities or world data.
Reopening deliberately begins a new warm-up; switching worlds clears history.
Configuration persists. A diagnostic seed property reproduces randomness in the
test environment. Forced triggers require an explicit JVM testing property and are
not registered as ordinary player commands. Developer metrics are opt-in and bounded.

## Architecture and hard bounds

Separate pure deterministic director, configuration IO, Minecraft context adapter,
sound presentation, and fold presentation. Fabric client events bind these modules.
The fold uses at most **three client-local vanilla display objects** and original
geometry; no Minecraft texture is redistributed. Presentation ids are local and
objects never enter the integrated server. Maintain at most **32 trail positions**,
**two active owned sounds**, one episode and one pending configuration snapshot.

No network requests at runtime. No blocking game-thread IO, scheduled unbounded
tasks, chunk loading, world scans, block writes or repeated log spam. Candidate
search per event is at most **24 nearby positions**, with fixed local support/clearance
checks and at most **16 short raycasts**. Tick cost is constant between events.

## Assets and rights

Six original mono 48 kHz OGG Vorbis one-shots: two treads, two taps, scrape and fold.
Editable deterministic synthesis source plus lossless masters are project assets;
runtime package contains only final OGG files and resource declarations. No loop
seams because no looping sound is used. Original geometry is editable source.
Original source/assets use MIT; third-party build/test inputs retain their licences
and are not included in the distributable mod. Player dependencies are declared,
not silently bundled. No Minecraft client, server or extracted vanilla assets ship.

Every final asset has a register entry with creator, source, date, licence,
modifications, SHA-256, use, full inspection evidence and decision. Reinspect any
presentation change. Audio: inspect the complete sound using the local audio-input
model, rejecting silent/invalid input before inference and reporting model limits;
measure duration, peak, RMS/integrated loudness and clipping separately. Individual
decoded peaks **≤ −12 dBFS**, no clipped samples, runtime per-source gain **≤ 0.6**,
maximum two simultaneous sources. Inspect recorded stereo left/right, near/far,
overlap, vanilla music, subtitles, all volume/visual controls and interruption.

## Nix and reproducibility

Nix **2.35.2**, experimental features `nix-command flakes`, sandbox enabled. Pin
nixpkgs through committed flake.lock. Pin each non-flake Java dependency URL, version,
size and SHA-256 in `deps/runtime.json`; verify downloads before use. Minecraft
assets are addressed by the pinned official asset index and verified SHA-1 objects.
Acquisition is explicit and separate from network-disabled builds.

Use Java 25 `javac` against the unobfuscated 26.2 API, without Gradle or Loom.
There is no Gradle dependency resolution, so Gradle verification metadata is not
applicable. Deterministic sorted jar entries, fixed timestamps and no embedded
machine paths. `packages.x86_64-linux.default` builds the installable jar.
`checks` execute compilation, lint, pure tests and resource checks in the sandbox.
`devShells.x86_64-linux.default` controls runtime, audio model, capture and inspection.

Required interfaces are Linux process/filesystem support and Nix daemon/network for
acquisition. Graphical tests use their own Xvfb display, pinned software Mesa and
private PulseAudio server with a null sink: no desktop or microphone recording.
Existing user authorisation permits the offline development client. No credential
or licence token is put in the repository or store. Players need no Nix or AI model.

Required non-interactive commands:

```sh
nix flake check --no-update-lock-file
nix build --no-update-lock-file .#default
nix develop --no-update-lock-file --command ./scripts/test-runtime
nix develop --no-update-lock-file --command ./scripts/validate
```

## Acceptance plan (all required before delivery)

| ID | Gate | Required evidence |
|---|---|---|
| A1 | Build | Formatting, shell/Python static analysis, javac all warnings as errors, ≥100,000 core transitions, metadata/sound decoding/resource references, no development test classes in release. |
| A2 | Installation | Actual `nix build` jar copied into fresh Minecraft game directory with only declared player dependencies plus separately identified test harness. Startup, absent/incompatible dependency diagnostics. |
| A3 | Ordinary play | Seeds 104729, 821 and 8675309; fresh terrain and established structure/farm/mine fixture; automated input mining, placing, planting/harvesting, exploration, combat, and crafting/progression. Verify resulting state, not command completion alone. |
| A4 | Feature coverage | Each F1–F3: activation, natural non-activation, interruption, completion, repeat, cleanup. Forced cases plus natural scheduling with no time compression. |
| A5 | Lifecycle | Save/quit/reopen, death/respawn, bed sleep, dimension changes, unloading, pause, configuration changes, resource reload, new/established world, creative/spectator and remote/published inert behaviour. |
| A6 | Robustness | Malformed/oversized/out-of-range configuration, unsafe contexts, interrupted IO/effects, resource-limit stress. No save damage, crash or uncontrolled accumulation. |
| A7 | Presentation | All shipped visual/sound assets and derived presentation directly inspected; real captured gameplay, complete audio, stereo position/attenuation, worst-case overlap/music, subtitle and control behaviour. |
| A8 | Endurance | **Two hours baseline and two hours modded**, actual wall time, equivalent seed/settings/workload, no accelerated clock; interval metrics and recordings, snapshots and logs. |
| A9 | Performance | Mod tick p99 ≤0.5 ms and ordinary maximum ≤5 ms after warm-up; frame p95 overhead ≤max(3 ms,20% baseline); integrated-server tick p95 overhead ≤1 ms. Post-GC heap growth over final 90 min no more than 128 MiB above baseline growth. Owned resource bounds always hold. |
| A10 | Removal | Disable cleans by next tick, persists across restart; removing jar loads a previously played save with unchanged blocks/inventory and no required custom registry entries. |
| A11 | Reproduction | Final validation starts in clean checkout/fresh project state; two independent builds with fresh build directories have identical jar hashes, with differences investigated. Locked acquisition only. |
| A12 | Acceptance | Requirement/evidence matrix complete; source commit, tool/host versions, lock hash, seeds/settings, package checksum, final stable-release recheck, rights review and zero unresolved acceptance-blocking defects. |

Endurance frame/tick comparisons use the same capped 960×540, render-distance 4,
simulation-distance 5, 30 FPS software-rendered profile. Technical correction after
the first runtime test: 26.2's validated minimum simulation distance is 5, not 4;
both benchmark conditions use 5. No performance budget is relaxed. A baseline includes Loader,
API and test harness but no horror jar. Record environmental interference; an invalid
comparison must be rerun, not excused by changing budgets. Store intervals and summaries
rather than unbounded in-memory telemetry. Mod packaging budget: **2 MiB**.

## Autonomous experience rubric

Review natural and forced recordings in a separate critical pass. Where available,
give a separate reviewing agent clips without event explanations. Every conclusion
must cite timecodes plus observable sounds/images or event timing. Required: work
remains possible; cue is perceptible in representative contexts; response has a
coherent relation to prior work; silence/recovery visibly outlasts episodes; repetition
does not become identical back-to-back playback; looking/continuing work retain agency;
fold reads as intentional impossible geometry rather than missing texture or broken
entity. Revise failures before acceptance. Fear, paranoia and enjoyment predictions
are **AI assessments**, never measured human responses or fabricated testimony.

Deliver jar and checksum, complete editable source, Nix/tooling/dependency records,
installation/configuration/content/troubleshooting/removal guides, research rationale,
asset register/licences and acceptance dossier with actual runtime audiovisual and
performance evidence. No promised feature may be left disabled or deferred.
