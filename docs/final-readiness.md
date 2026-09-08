# Borrowed Quiet 1.0.0 — final readiness

Decision: ACCEPTED

The complete scope committed at `ec684c1` is implemented and accepted for Minecraft
Java 26.2 on the documented Linux x86-64 local single-player Survival environment.
The official 2026-09-08 release recheck still identifies 26.2 as stable; 26.3 is in
pre-release testing. No development phase, human playtest, AI service or additional
content delivery is needed to fulfill this scope.

Release jar SHA-256:

`2133042d444e80d3e072ea7b1354adc3dbdd1e6b72a1dada12f8b5081f228b87`

## Acceptance basis

All A1–A12 and F1–F4 requirements are linked to implementation, executed procedure,
result and SHA-256-bound evidence in [the acceptance matrix](../evidence/acceptance.json).
Sandboxed Nix checks cover formatting/static checks, compilation, 38,624,690 core
assertions, resources and deterministic original asset generation. Actual graphical
Minecraft tests cover the exact packaged jar, all three horror events, non-activation,
interruption, completion, cleanup, lifecycle/persistence, three ordinary-play seeds,
controls, malformed configuration, missing/incompatible dependencies and removal.
A separate harness-free player installation uses normal GUI world creation and
cheat-free controls, preserving a saved marker and inventory.

All six shipped sound assets and the original three-part visual geometry have
completed inspection records. Actual spatial playback, gain, subtitles, overlapping
voices, vanilla music interaction and cleanup were reviewed. Visual checks include
multiple angles, distances, lighting and motion, plus natural and endurance footage.
CUDA-assisted audio interpretation is explicitly fallible AI assessment; no fabricated
native hearing or human testimony is used.

The full clean workflow passed all 15 runtime labels, a 30-minute natural session
and two hours each of baseline/modded endurance. All predeclared performance and
retention gates passed. See [endurance review](endurance-review.md),
[experience assessment](experience-review.md), [audio](audio-review.md) and
[visual](visual-review.md). No unresolved known mod-caused crash, save corruption,
progression blocker, critical security issue, missing resource or uncontrolled
resource growth remains in the supported configuration.

## Provenance and honest validation sequence

The full runtime checkout was clean commit
`b762379f6d93567169f450747afb2a4216446224`, with fresh project state and independently
rebuilt package. Nix was 2.35.2 with sandboxing; all flake and external inputs were
pinned and verified. Lock SHA-256 is
`f5e5ca33ec6c271caf15946562b4de759447f272866249623b893e9d57e7d385`.
The later clean launcher regression at
`8acb07705bfdb03a9af6ac0a0747abbe1e41ed96` passed with the identical jar and harness.
Final review/export/documentation changes do not change any package input: source,
builder, dependency manifest and flake Git objects are compared to the tested commit
in [reproduction evidence](../evidence/reviews/reproduction.json). An independent
Nix `--rebuild` again produced the identical release checksum.

The initial clean `validate` invocation completed every runtime/performance check,
then correctly returned failure because the autonomous review dossier did not yet
exist. Its console is retained. It is **not** reported as an overall successful
invocation. Completed reviews and the exact-package acceptance gate finish that
readiness step separately. Release packaging requires a clean tree and passing gate;
the delivered source/evidence and Git bundle preserve this chronology. Archive commit
and archive checksums are recorded in the release manifest, distinct from the tested
implementation commit. No later documentation change is disguised as a new four-hour
game run.

## Boundaries and delivery

This is restrained, contextual ambient horror, not a chase campaign or a guarantee
of human fear. Repeated exposure can reveal its deliberately small vocabulary; rain
can mask quiet sound. The abstract form may read as a thin plank at some angles.
The renderer/performance claim is the tested Nix llvmpipe profile, not all hardware.
Multiplayer horror, hardcore, shaders, arbitrary other mods and custom resource packs
are not advertised. Nether/End and non-Survival/remote/published sessions are quiet
by design. These boundaries were scoped, not unfinished promised features.

Players need the jar, the documented Fabric Loader/API versions, Java and a legitimate
Minecraft installation—not Nix or any AI subscription. The source archive includes
editable original assets, tests, scripts, locks, provenance, documentation, the
acceptance matrix and Git history. The companion evidence archive supplies runtime
recordings and inspection/performance records referenced by that matrix. Extract
both archives together; their common directory is `borrowedquiet/`. The standalone
Git bundle also permits a clean clone. No Minecraft software, model weights,
credentials or saved worlds are distributed. `SHA256SUMS` identifies release files.

Reliable disabling/removal and spoiler-light controls are in the [player guide](../README.md).
There is no outstanding approval, creative question or post-delivery work dependency.
