# Preflight verdict

**Verdict: BLOCKED BEFORE IMPLEMENTATION. No mod release exists.**

The brief requires proof of build, Minecraft execution, gameplay control, audiovisual
capture/inspection, automated checks, and performance collection before implementation.
It also prohibits obtaining missing access through new purchases, manual account setup,
or human intervention. The capability gate was therefore treated as a prerequisite,
not as an acceptance condition to waive later.

## Results on 8 September 2026

| Capability | Result | Evidence and limit |
|---|---|---|
| Current stable release | Verified: Java 26.2 | Official release page and Mojang version manifest; latest test release was 26.3-pre-2. `evidence/preflight/release.json`. |
| Nix availability | Verified: 2.35.2 | Daemon responded; flakes enabled; sandbox reported true. Host tool output in `host.txt`. |
| Pinned tool environment | Verified | `flake.lock` pins nixpkgs; Java 25.0.4.1, FFmpeg 9.0.1, llama.cpp 0.4.0 build 10809. |
| Sandboxed prerequisite tests | Passed | Script lint, Java major version, mono OGG Vorbis encode, metadata check and decode. These are not mod compilation or tests. |
| Host display/audio services | Reachable | X11 metadata and PulseAudio-compatible server queries succeeded. |
| Software OpenGL | Verified after correction | Initial host and Xvfb probes failed to find a GLX visual. Explicit pinned Mesa/libglvnd library paths and software Mesa selection produced OpenGL 4.6 with llvmpipe. |
| Isolated video/audio capture | Verified at probe level | Actual OpenGL gear window captured with FFV1 video; probe tone played through a dedicated null sink and captured to WAV. No Minecraft was running. |
| Direct image inspection | Probe inspected | Captured frame shows red, green and blue gears against black, without a missing-texture pattern. This is not inspection of a mod asset. |
| Native audio perception | Unavailable in this conversation | Emitting a WAV through the audio helper produced an audio attachment omitted from inspectable model input. No claim of hearing it is made. |
| Local audio-model fallback | Basic probe succeeded; not full acceptance | Pinned model consumed the complete 3-second probe and described a high-pitched electronic beep with no intelligible speech. Its description omitted the short fades. See `audio-review.txt`; complex sound, stereo spatial judgment and game playback remain unvalidated. |
| Authorised Minecraft client access | Not established — blocking | Standard launcher directories and tested Flatpak locations absent; no matching running launcher/client process. Browser access tool reported `No browser is available`. This does not assert that the user does not own Minecraft. |
| Minecraft startup/gameplay control | Not run | No clean packaged-mod installation, client launch, integrated server, or automated gameplay evidence exists. |
| Performance/endurance | Not run | Hardware information and a gears probe do not establish Minecraft performance or multi-hour stability. |

## Access alternatives considered

Checked only relevant application locations: `.minecraft`, `.local/share/PrismLauncher`,
`.local/share/multimc`, `.local/share/ATLauncher`, `.config/PrismLauncher`, and the
PrismLauncher/Minecraft Flatpak locations. No account files were read or copied;
credentials were not requested, logged, placed in the repository, or placed in the Nix store.

An attempt to use an existing browser connection for the Minecraft profile page failed
because the computer-use tool reported that no browser was available. No sign-in was attempted.

Fabric's development launch workflow was also considered. A development client can
operate without an authenticated online session; this is distinct from establishing
an existing authorised game licence. The report does not claim that authentication
is technically necessary for every development launch.

The [official free-trial page](https://www.minecraft.net/en-us/free-trial) documents
Microsoft sign-in and approximately 100 minutes of play. This is not a replacement
for the required unrestricted multi-hour survival tests. A publicly downloadable jar
does not establish the required authorisation. An open-source Minecraft-like game
would not satisfy the Minecraft Java Edition target. No account-creation or purchase
workflow was initiated.

## Scope and acceptance status

No complete scope specification was committed, no gameplay implementation was started,
and no production assets were selected. Initial research is preserved separately and
explicitly marked incomplete. The project does not claim to have reached the stage
at which a final acceptance decision on a release package could be made.

All mod-specific commitments in the brief remain **unimplemented/unverified**:
creative specification, finished gameplay and assets, dependency acquisition and build
verification, package output, runtime/validation scripts, ordinary-play/lifecycle and
robustness tests, accessibility/controls, in-game audiovisual review, endurance and
performance comparisons, clean reproduction, installation/removal, provenance records,
and the requirement-to-release-evidence matrix. None is relabelled as a scope exclusion.

No human approval, playtesting request, or creative question is part of this verdict.
This is a report of an unmet external capability prerequisite, not final delivery.
