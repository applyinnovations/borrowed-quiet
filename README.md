# Minecraft horror mod project — blocked at preflight

This repository does **not** contain a finished mod or an installable release.
Implementation has not started because the required pre-implementation capability
gate has not passed: authorised Minecraft runtime access could not be established
from the available launcher state or browser connections.

The project brief prohibits new purchases, manual account setup, and human intervention.
The official trial requires Microsoft sign-in and is limited to approximately 100 minutes;
it does not establish the access required for multi-hour survival validation.
See [the preflight report](docs/preflight.md) for evidence and limits.

The files here preserve the autonomous feasibility work, not a substitute mod delivery:

- `flake.nix` and `flake.lock`: pinned Linux x86-64 prerequisite tools.
- `scripts/preflight`: host-interface and official-release diagnostics.
- `scripts/probe-capture`: isolated software OpenGL and audio-loopback capture probe.
- `scripts/probe-listening`: local audio-input model feasibility experiment.
- `docs/research-notes.md`: initial research with evidence categories and limitations.
- `evidence/preflight/`: recorded prerequisite results, explicitly distinct from game tests.

## Reproduce prerequisite checks

Host Nix tested: **2.35.2**, with `nix-command flakes` enabled and `sandbox = true`.
The development system evaluated here is `x86_64-linux`. Package versions are fixed by
the locked nixpkgs input. These tools do not establish a supported player platform.

```bash
nix flake check --no-update-lock-file
nix develop --no-update-lock-file --command ./scripts/preflight
nix develop --no-update-lock-file --command ./scripts/probe-capture
```

Capture uses its own Xvfb display and a temporary PulseAudio-compatible null sink;
it does not record a microphone or other applications. The host must supply a usable
PulseAudio/PipeWire socket. Software rendering uses pinned Mesa libraries. The initial
host OpenGL failure and its correction are recorded in the report.

The flake has no distributable `default` package. `scripts/test-runtime` and
`scripts/validate` have not been implemented. No fake release or passing placeholder
for these required deliverables is provided. Passing the prerequisite check means
only that its declared script lint and codec/toolchain tests passed.

## Audio-tool feasibility experiment

The flake separately pins public Qwen2.5-Omni model and projector files by repository
revision and SHA-256 for a local audio-understanding experiment using `llama.cpp`.
These are development evaluation inputs, not Minecraft dependencies or shipped assets.
They are approximately 7.3 GB combined. They are not downloaded by the prerequisite
check or regular development-shell startup.

The basic listening probe completed: the model identified the generated non-speech
tone, though it omitted the short fades from its description. This demonstrates a
limited audio-input route; it is not a completed asset or in-game listening review.

The [conversion's model card](https://huggingface.co/ggml-org/Qwen2.5-Omni-7B-GGUF/tree/89b785438c8901d4635e42f50480ba5985a1bbf1)
lists the Qwen research licence and links the upstream licence. The upstream 7B model's
current licence is Apache-2.0; this experiment makes no assumption that the conversion's
older metadata has been relicensed. Its use here is solely capability evaluation.
No model files are included in the repository, and no model outputs have been used as mod assets.

There is no release checksum, installation claim, experiential acceptance, human test
result, or final acceptance dossier. The original completion requirements remain unmet.
