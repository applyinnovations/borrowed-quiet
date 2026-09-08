# Complete audio inspection

All six shipped OGG files were decoded and passed in their entirety to the pinned
Qwen3 Omni audio-input model. Complete in-game excerpts were then reviewed,
including four repetitions of every asset, left/right and near/far placements,
maximum two-voice overlap, vanilla music, and eight naturally scheduled episodes.
The agent inspected the returned acoustic descriptions critically alongside the
actual PCM measurements, event logs, subtitle frames and sound lifetime code.
This is tool-assisted AI listening, **not native human hearing or human playtesting**.

The model is fallible: it sometimes guesses physical recording equipment, counts
four test pulses as eight, or infers a tone where the source has already ended.
Those claims are not accepted as facts. Pulse counts/timing come from the recorded
signal and runtime log; clipping comes from decoded samples, not an adjective.
The four-pulse calibration correctly identifies separated dry percussion. Earlier
Qwen2.5 descriptions were rejected; the complete Qwen3 CUDA inputs, hashes, prompts,
responses and engine logs are retained in the review evidence.

## Isolated assets

| Asset | Decoded seconds | Peak dBFS | RMS dBFS | Padded LUFS | Critical acoustic assessment |
| --- | ---: | ---: | ---: | ---: | --- |
| tread1 | 0.4573 | -13.915 | -34.333 | -35.69 | Dry initial crack with a lower thud and very short granular decay; suitable as an ambiguous continued footfall. |
| tread2 | 0.5293 | -14.553 | -34.513 | -34.80 | Similar crack/thump family with a different body/decay; no voiced syllable or recognizable borrowed sample. |
| tap1 | 0.3773 | -13.998 | -32.211 | -33.15 | Woody, compact, pitched impact; a clearer knock than the granular treads. |
| tap2 | 0.4173 | -14.106 | -32.092 | -32.55 | Brighter hollow impact, brief ringing coloration, short decay; coherent variation rather than a new sound family. |
| scrape | 1.5800 | -13.955 | -33.851 | -31.95 | Abrasive/fibrous granular rustling, sometimes interpreted as tearing paper or a mechanism; the source remains ambiguous. |
| fold | 1.1600 | -14.941 | -30.605 | -29.87 | Dense dry crackling with a low body; connects the contraction to the material sound vocabulary. |

Every file is original seeded synthesis, mono 48 kHz Vorbis, with zero clipped
samples and a decoded peak below -12 dBFS. The measurement tool feeds the exact
selected PCM plus one second of silence into R128 analysis so the shortest tap
can fill its 400 ms window. These LUFS values describe that explicitly padded
measurement, not a long musical programme. Full reports retain exact values.
There are no speech recordings or loops. Smooth source envelopes and bounded tails
avoid a loop seam; silence between repeated playback is intentional. Byte-identical
regeneration of masters and Vorbis files is separately tested in the Nix sandbox.
The register's `master_seconds` describes the editable source duration; final
decoded durations (including codec trimming/padding differences) are measured above
and in each linked measurement record.

**All six assets accepted** for the declared restrained, dry material identity.
They are stylized foley, not claimed natural field recordings. No intelligible
speech, accidental voiced content, missing decoder resource or unexplained clipping
was found. The model's precise source guesses are not evidence of those objects.

## Recorded presentation and controls

The final clean presentation recording is 02:39.400. Its `AV_MARK` timestamps map
to captured device timestamps, after the synchronization correction. The five
position scenarios occupy approximately 00:13–00:30; six four-pulse tests follow,
then overlap and controls. Exact excerpt starts/durations are in the measurement
records, not rounded timecodes used for navigation here.

Opposite side sources invert the active stereo channel. Complete separate-ear
copies use the same +20 dB inspection gain; the opposite channels are digital
silence and are recorded as silence controls without generating model captions.
The audio model consumes mono, so stereo localization is assessed using these
separate-ear reviews plus original channel measurements and directional subtitles,
not a false claim that the model binaurally heard the original stereo field.
The 3 m sound measures roughly -52 dBFS RMS versus roughly -68 dBFS at 14 m;
30 m is silent. Mod, Ambient and Master zero-volume cases are silent. Runtime
assertions confirm no retained voices after the corresponding cleanup.

At 01:27.566, three requests exercise the two-voice cap at the listener. The
3.201-second original excerpt peaks at **-29.035 dBFS**, RMS -48.010 dBFS per
channel, zero clipping. A peak-normalized listening copy amplified this by
26.023 dB; its caption described harsh distortion. This was investigated, not
discarded silently. Reviews of the same complete excerpt at original level and
at +12.041 dB instead describe a dry crack/thump and short rustle, without
significant distortion. The discrepancy is gain-sensitive interpretation of a
granular transient, not digital overload in the delivered mix. No mix increase
was made to force perceptibility. The original and both comparisons are traceable
through hashes and the excerpt manifest.

The music-overlap review identifies the brief percussive foreground sound followed
by unbroken soft piano. The measured original mix has no clipping. The mod neither
ducks/replaces music nor changes player volume settings. All source gains are
bounded by 0.6, with at most two owned voices, including the worst-case test.

## Natural context and repetition

Complete excerpts cover events near 02:42, 07:30, 10:23, 14:52, 19:59, 23:59,
27:24 and 30:19 in the 31-minute natural recording, with work before/after each.
The early Fold excerpt contains vanilla piano and distinct papery rustling;
the quiet work excerpts contain separate impacts, scraping and pauses. The dense
visual sequence at 14:54–15:02 aligns scraping/subtitles, the shoreline form and
return to mining. Later rain-dominated excerpts mask some subtle sounds; the
reviewer sometimes hears mainly rain. This is a documented presentation boundary,
not a reason to override environmental volume or claim every event was heard.
Directional subtitles remain available, and missed opportunities carry no penalty.

The natural log records eight episodes with all three kinds and no consecutive
identical kind. Multi-minute recovery greatly exceeds the 4–12 second observed
episodes. Forced four-pulse playback is deliberately repetitive for inspection,
not the delivered scheduler. The two tread/tap variants, irregular timing, turn
response and contextual placement resist identical replay; familiarity with the
small sound vocabulary remains possible and is not disguised as infinite content.

Evidence: `evidence/reviews/asset-measurements`, `presentation-measurements`,
`isolated-and-overlap`, `context-listening`, and the hash-bound original gameplay
recordings in the final dossier. Standalone extracted vanilla music/audio is not
distributed; the preparation script and original video permit reconstruction.

The final two-hour repeat-exposure captures add complete first/last excerpts of
all three event kinds and early/late baseline context. Their measurements,
CUDA observations, critical interpretation and timecodes are recorded in
[the endurance review](endurance-review.md). One verbose baseline music caption
hit its output limit; a compact follow-up reviewed the complete same input and
finished normally. Neither the truncated caption nor uncertain electronic-source
guesses are treated as complete factual descriptions.
