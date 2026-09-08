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
Do not run CPU-intensive audio inference concurrently with performance comparisons.

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

## Instrumentation and interpretation

Forced triggers require `borrowedquiet.testing=true`; there are no ordinary player
test commands. Metrics/logs are enabled by testing or `borrowedquiet.diagnostics=true`.
`borrowedquiet.seed` reproduces only mod randomness, not vanilla ambient behaviour.
The benchmark samples the last frame duration and integrated-server average tick
counter each client tick with identical harness instrumentation in both conditions.
Post-GC retention samples use equal fixed workload intervals. Results apply to this
controlled software-rendered profile, not arbitrary hardware or mod packs.

Local audio-input model observations are fallible AI descriptions, cross-checked
against complete clips, known controls, measured timing, levels and channels.
Neither captions nor waveforms alone prove a human emotional response.
