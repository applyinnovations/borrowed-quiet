# Development and evidence reproduction

Supported host: Linux x86-64; Nix **2.35.2**, with `nix-command flakes` enabled and
`sandbox = true`. Nix is the declared host bootstrap boundary. Build, asset,
runtime, capture, lint and inspection tools come from the committed flake.

The reference host has an AMD Ryzen 9 5900X and 32 GiB RAM. Validation uses pinned
software Mesa, not the physical GPU: private Xvfb, 960×540, 30 FPS game cap, 15 FPS
recording, render distance 4, simulation distance 5. Private D-Bus and PulseAudio
null-sink sessions isolate recording from other applications. No desktop display,
microphone or host audio service is needed. Linux processes, temporary storage,
Unix sockets, network for acquisition and a writable checkout are required.
Do not run audio inference concurrently with performance comparisons.

Audio inspection uses the flake's CUDA-enabled llama.cpp, built for NVIDIA compute
capability 12.0 (reference host: RTX 5080, 16 GiB). The separate CUDA nixpkgs import
enables unfree CUDA toolkit dependencies without changing the Minecraft build or
Mesa test profile. `scripts/cuda-driver-env` exposes only host NVIDIA driver
libraries through a private temporary symlink directory on non-NixOS hosts, or
uses `/run/opengl-driver/lib` on NixOS. It never adds all of `/usr/lib` to Nix's
library search path. The host kernel driver and `/dev/nvidia*` are explicit host
interfaces; CUDA toolkit and inference binaries remain pinned by Nix.

`scripts/probe-listening` and `scripts/listen-batch.py` require CUDA0 and request
automatic weight offload, GPU audio projection and 6144 MiB VRAM headroom.
The model is larger than available VRAM, so some CPU work is expected. They fail
if CUDA is unavailable instead of silently reverting to CPU-only inference.
The CUDA build is exposed as `nix build --no-update-lock-file .#audio-review-engine`.
Audio models and CUDA are inspection tools only, never player dependencies.
On the reference host (driver 610.57.04), the calibrated fit puts all 49 layer
graphs on CUDA with some MoE expert weights retained on CPU. A 3072 MiB margin
failed during cuBLAS workspace allocation; 6144 MiB passes the recorded audio
calibration. GPU audio projection is separately confirmed in the engine log.

## Locked inputs

`flake.lock` fixes nixpkgs. `deps/runtime.json` fixes application/test jars and
official Minecraft metadata by URL, size and digest; assets follow the pinned
official content-addressed index. Minecraft downloads are local test inputs,
**not distributable artifacts**. Audio models/projectors are pinned independently
by repository revision and SHA-256 in `flake.nix`; they are not game dependencies.
No credentials belong in this repository, the Nix store or launch arguments.
Authorised offline developer mode is used solely for isolated validation, not as
a player installation method.

```sh
nix develop --no-update-lock-file --command python3 scripts/acquire.py --prepare
nix build --no-update-lock-file .#default
```

Acquisition is explicit and hash-verified; package builds are network-disabled
derivations. `acquire.py --lock` deliberately updates dependencies and is never
part of validation. Direct Java 25 compilation uses 26.2's unobfuscated API, all
javac warnings as errors, and no Gradle/Loom resolution. Sorted jar entries, fixed
timestamps and stable permissions avoid machine-specific output.

## Validation interface

`nix flake check --no-update-lock-file` runs sandboxed compilation, deterministic
transition and configuration tests, resource/hash/codec checks, shell/Python lint,
Java formatting and flake formatting. Test classes never enter the player jar.

`nix develop --no-update-lock-file --command ./scripts/test-runtime` installs the
Nix package into fresh graphical instances and separately executes Fabric client
GameTests. It retains recordings, screenshots, logs and a package-bound report in
`.runtime/validation/<UTC timestamp>`. The default suites cover forced features,
three normal-world seeds, lifecycle, presentation, persistence/removal and
dependency failures. Fixture commands prepare isolated worlds; ordinary actions
use actual survival input and resulting-state assertions.

Remote/published exclusion tests set the relevant client/server context fields
temporarily and exercise the actual mod callback, then restore them in `finally`.
They do not open a LAN socket or claim tested multiplayer gameplay. No multiplayer
horror mode is supported. Falling is likewise covered by a controlled context
boundary in addition to actual water, lava, death, sleep and dimension transitions.

`--suite natural` records 30 unaccelerated minutes without mod triggers or timing
edits. `--suite endurance` runs two hours baseline then two hours modded using
equivalent work and settings, followed by strict budget comparison. Other suite
names select focused checks. `--output <new-directory>` selects a unique report
destination; an existing destination is rejected.

`nix develop --no-update-lock-file --command ./scripts/validate` requires a clean
checkout, runs sandboxed checks, builds and independently rebuilds the package,
runs runtime/endurance validation and checks the autonomous acceptance dossier.
Missing, incomplete or mismatched evidence fails; test success alone does not
manufacture a release decision. Final reproduction uses a separate clean checkout
and fresh runtime state. Never use personal game directories or worlds for tests.

Generated caches and evidence are isolated under ignored `.runtime` and `build`.
They are not package build inputs. Player dependencies must be acquired from their
publishers; the delivered mod contains neither Minecraft nor Fabric API.

The release separates the small source archive from the large evidence archive.
Both extract under `borrowedquiet/`; extract both to inspect the hash-bound dossier.
The source archive also contains `history.git.bundle`, preserving the committed
pre-implementation specification and subsequent refinements without local Git
configuration or credentials. For clean-checkout reproduction, run
`git clone history.git.bundle ../borrowedquiet-clean` from the extracted source,
then use the Nix workflow there. Copy the extracted `evidence/runtime` and
`evidence/reviews` into that clone to verify the delivered dossier; fresh runtime
tests create separate `.runtime` state. Players need only the mod jar and declared
dependencies, not either archive or the bundle.

## Instrumentation and interpretation

Forced triggers require `borrowedquiet.testing=true`; there are no ordinary player
test commands. Metrics/logs are enabled by testing or `borrowedquiet.diagnostics=true`.
For the separate harness-free installation inspection, `BQ_PLAYER_MODE=1` makes
`scripts/launch.py` omit test libraries and all mod testing/seed JVM properties;
only the specified release jar and Fabric API are installed. The agent used the
isolated display recorded in session metadata, actual GUI screenshots and paced
`xdotool` input to load/create worlds, verify controls with cheats off, save and quit.
This is still the authorised developer launch, not player entitlement instructions.
`borrowedquiet.seed` reproduces only mod randomness, not vanilla ambient behaviour.
The benchmark samples the last frame duration and integrated-server average tick
counter each client tick with identical harness instrumentation in both conditions.
Post-GC retention samples use equal fixed workload intervals. Results apply to this
controlled software-rendered profile, not arbitrary hardware or mod packs.

Local audio-input model observations are fallible AI descriptions, cross-checked
against complete clips, known controls, measured timing, levels and channels.
Neither captions nor waveforms alone prove a human emotional response.
