# Endurance, performance and repeat-exposure review

Decision: ACCEPTED

This is an autonomous technical review and AI experiential assessment, not a human
playtest. The full recordings were decoded and measured; visual review was sampled,
not frame-by-frame inspection of four hours. Audio inspection used the calibrated,
pinned Qwen3 Omni audio-input model with CUDA, not a claim of native assistant hearing.

## Conditions and results

The clean checkout `b762379f6d93567169f450747afb2a4216446224` ran the packaged mod
through the complete validation workflow. Both endurance conditions used the same
seed, fixture, actual movement/mining work loop and capture settings. The baseline
omitted Borrowed Quiet, retaining the same loader/API/test infrastructure. Neither
condition ran concurrent audio inference or another Minecraft client.

Host: Ryzen 9 5900X, 32 GiB RAM, Linux x86-64; Minecraft 26.2, Fabric Loader 0.19.3,
Fabric API 0.152.0+26.2, Java 25.0.4.1. Nix Mesa llvmpipe rendered an isolated
960×540 Xvfb display, with a 30 FPS game cap, 15 FPS capture, render distance 4,
simulation distance 5, and private PulseAudio loopback. The RTX 5080 was used for
separate CUDA audio inspection, not Minecraft rendering. Host details and the
continuous host monitor accompany the evidence.

| Measurement | Baseline | Modded |
| --- | ---: | ---: |
| Last elapsed telemetry, seconds | 7229.9217 | 7229.6069 |
| Samples | 144,560 | 144,560 |
| Frame-time p95 | 6.624272 ms | 6.817117 ms |
| Sampled server tick-time p95 | 0.513955 ms | 0.476058 ms |
| Post-GC retained heap growth | −1,636,184 bytes | −2,216,112 bytes |
| Maximum mod sounds / displays / trail | 0 / 0 / 0 | 1 / 3 / 32 |

Mod p99 work was 0.004518 ms and maximum 2.969385 ms, passing the predeclared
0.5 ms / 5 ms limits. Frame overhead was 0.192845 ms, below the larger-of-3-ms-or-20%
budget. Tick-time p95 decreased by 0.037897 ms, below the +1 ms budget. Differential
retained growth was −579,928 bytes, below +128 MiB. Warm-up exclusion and the final
90-minute post-GC retention comparison follow the committed performance checker.
The natural run's one-voice maximum does not substitute for the separate controlled
two-voice worst-case presentation test. All resource caps and all performance gates
passed without relaxed thresholds. These are this host/profile's measurements,
not GPU-renderer or arbitrary mod-pack guarantees.

The runtime report contains 15 passing run labels: all controlled functional,
ordinary-play, lifecycle, presentation, persistence, removal/configuration and
dependency diagnostics, a 1817.503727209-second natural run, and both multi-hour
conditions. See [report](../evidence/runtime/final/report.json) and
[performance](../evidence/runtime/final/performance.json).

## Sustained work and pacing

Both recordings show continued mining through the final minute. Direct checkpoint
inspection covered each 20-item increment through 200 cobblestone in each condition.
The independent reviewer inspected all twelve one-frame-per-minute overview sheets,
early/late native frames and finer late sequences. At video 02:00:00 both conditions
show 218 collected cobblestone; 02:00:12–02:00:20 shows another swing, break, single
drop and collection to 219. Health/hunger remain full, textures and HUD coherent,
and no growing floor litter or persistent mod geometry is visible. This demonstrates
the bounded endurance work loop; the separate three-seed suite supplies broader
mining, building, farming, crafting, combat and exploration assertions.

The modded log contains 29 naturally scheduled completed episodes: 11 Pace, 10 Wall,
8 Fold. No actual consecutive kind repeats. Tick-derived episode lengths are
1.35–11.8 seconds, totaling 211.35 seconds. Between completed episodes and the next
start, quiet spans 151.2–473.05 seconds. Recovery settings select opportunities, not
a deadline guaranteeing an encounter: context or unsuccessful placement can extend
silence beyond the nominal 150–300-second Normal recovery range.

At 01:31:24–01:31:26 the scrape subtitle precedes a narrow dark form. The native
01:31:28.500 frame shows its ground shadow; a five-frame-per-second sequence shows
contraction/disappearance, followed by mining at 01:31:35–01:31:37. The last Fold,
01:52:52.917–01:53:04.917, also clears while ordinary work proceeds. The final Wall
at 01:42:05.917–01:42:14.917 accompanies collected work and directional subtitles;
the last Pace at 01:57:50.917–01:57:51.917 is brief rather than accumulating.

The bright repeated enclosure is intentionally useful for equivalent-work endurance
but weak for atmospheric variety. The separately reviewed natural shoreline and rain
session supplies contrasting presentation. The independent reviewer was independent
of event logs/source/performance for this pass, but had prior visual familiarity:
this is repeat-exposure review, not a second fresh blind test. The narrow form remains
anatomically ambiguous; sampled footage shows intentional finite motion rather than
a stuck artifact. Familiarity and rain masking remain genuine creative limits, not
promises of endless novelty or guaranteed notice.

## Complete capture and audio inspection

Both full MKV files passed FFmpeg decoding with `-xerror`. Full-capture audio peaks
were −13.084021 dBFS baseline and −12.564267 dBFS modded; RMS values were −49.829959
and −50.582801 dBFS. Neither reaches digital full scale. Original capture is stereo
48 kHz FLAC. All eight complete selected review clips (baseline early/late and first/
last occurrence of each mod kind, including context and tails) were inspected through
the CUDA audio-input model. The 16 kHz mono +12.041 dB inspection copies contain zero
clipped samples. The manifest gives exact extraction spans and original hashes.

The first baseline caption hit its output limit; a compact follow-up consumed the
same complete material and finished normally. Descriptions support separated dry
impacts/rustles and finite granular sound bursts, with music present in the baseline
follow-up. Several captions make dubious beep/buzz source guesses; the follow-up
also contradicts itself about repetition. Those guesses are not accepted as literal
sound-source or repetition facts. Texture judgments are combined with complete
original-asset review, timed playback logs, quantitative measurements and the prior
spatial/music/overlap controls. No human reactions or flawless model hearing are
claimed. See [audio review](audio-review.md) for all six original assets and mixing
limits; no vanilla audio extraction is shipped as a mod asset.

## Investigated warnings

The baseline alone logged a 2000 ms/40-tick scheduler warning at capture
01:33:47.552 near a scheduled GC checkpoint. The corresponding telemetry window
(elapsed 5600–5625 seconds) contains 499 samples, a maximum 0.1277-second sample gap,
14.357153 ms maximum frame and 0.443685 ms maximum sampled average server tick.
Full-run maximum gaps were 0.1975 seconds baseline and 0.1802 seconds modded;
maximum recorded frames were 56.560298 and 59.405473 ms. There is no corresponding
two-second freeze in these samples. Accumulated scheduler drift at repeated GC
checkpoints is a plausible inference, not a proven cause. Work continued, no warning
recurred, and the modded run had no equivalent warning. The full warning and host
trace are retained; neither condition or threshold was discarded to obtain a pass.

The test-harness anisotropy warning is traced to Fabric's test option initialization,
not mod rendering. Offline developer services-public-key warnings are specific to
authorized developer launch; players use their legitimate normal installation.

## Evidence map

- [Independent visual review](../evidence/reviews/endurance/independent-review.md)
- [Capture, episode and clip manifest](../evidence/reviews/endurance/capture-review/inspection-inputs.json)
- Full recordings/logs/metrics: `evidence/runtime/final/endurance-{baseline,modded}/`
- Complete audio-input records: `evidence/reviews/endurance/listening/` and `listening-followup/`
- Full capture decode/audio measurements and sampled images: `evidence/reviews/endurance/capture-review/`
- [Host monitor](../evidence/reviews/host-monitor.jsonl)

The dossier hashes these materials. Endurance supports stability, bounded resources,
finite interruptions and recovery. Predicted dread/enjoyment remains an AI design
assessment grounded in those observations, never a measured human outcome.
