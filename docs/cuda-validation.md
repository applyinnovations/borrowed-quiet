# CUDA audio-inspection validation — 8 September 2026

The CUDA setup follows the separate CUDA-enabled nixpkgs import and narrow host
driver bridge used in the locally inspected Kinesis Labs flake. This repository
contains its own implementation; it does not depend on that checkout.

- Nix 2.35.2; existing nixpkgs lock unchanged.
- llama.cpp 0.4.0, build 10809, commit 5266f24; CUDA 12.9.86; target sm_120a.
- Engine output: `/nix/store/snfb34pgjwkdzdsjc9ymd156h9hwkp1d-llama-cpp-0.4.0`.
- NVIDIA GeForce RTX 5080, 15877 MiB reported, host driver 610.57.04.
- Pinned Qwen3 Omni Q4_K_M and bf16 projector from the flake; no model changes.

The first run detected CUDA but exhausted VRAM during cuBLAS workspace allocation
with a 3072 MiB fit margin. This failed run is retained as
`.runtime/qwen3-cuda-calibration.txt`, not counted as a pass. The final commands
reserve 6144 MiB. The successful calibration reports 49/49 layer graphs offloaded,
37 expert-overflow layers, 5175.63 MiB of GPU model buffers, a 768 MiB GPU KV cache,
and CUDA audio projection. This is mixed CPU/GPU inference, not a claim that all
model weights fit on the GPU.

The four-pulse, 9.051-second recorded calibration completed successfully and
identified four separated percussive events. It reports 23.66 generated tokens/s.
The subsequent eight-input server batch completed without an inference error:
six complete isolated assets and the maximum-overlap and music-overlap clips.
Batch generation ranged from 17.30 to 19.76 tokens/s. These are observed timings,
not a controlled hardware benchmark or evidence of human listening responses.

Evidence retained locally:

| Record | SHA-256 |
| --- | --- |
| `.runtime/qwen3-cuda-calibration-2.txt` | `f5519a6f231383876818e5968abf0afc7d41cda613dfcb48efda2b5c4f2313ce` |
| `.runtime/cuda-device-verification.txt` | `35637d95c0831ca1674c7cda7c9703feb1fc6130b36b58ffc417dd300949f6a7` |
| `.runtime/listening-cuda-1/server.log` | `1ded5e58b4b9cd96e78955df9a533d7bf1cfd5a8f562228815b476408a816918` |
| `.runtime/cuda-final-checks.log` | `ce0289e08b0badeb07dcb1442cead29807fa325702bdbc923a2b8cab7257ae94` |

All three flake checks pass. The mod derivation and release-candidate jar remain
unchanged. This validates the inspection backend only: audio acceptance still
requires critical review of the captions against the recordings and measurements.
In particular, the overlap caption describes harsh distortion despite no measured
digital clipping; that perception must be investigated, not marked passed simply
because inference succeeded. Overall mod acceptance and endurance remain pending.
