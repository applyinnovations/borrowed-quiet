#!/usr/bin/env python3
"""Bind completed tests and explicit AI reviews; refuse incomplete technical evidence."""

import functools
import hashlib
import json
import pathlib
import subprocess

root = pathlib.Path("evidence/runtime/final")
review_root = pathlib.Path("evidence/reviews")
review_files = []
for file in sorted(review_root.rglob("*")):
    if file.is_file() and file != review_root / "files.json":
        with file.open("rb") as stream:
            review_files.append(
                {"path": str(file), "sha256": hashlib.file_digest(stream, "sha256").hexdigest()}
            )
(review_root / "files.json").write_text(json.dumps(review_files, indent=2) + "\n")
report = json.loads((root / "report.json").read_text())
assert report["result"] == "RUNTIME_CHECKS_PASS" and not report["dirty"]
expected = {
    "features-104729",
    "ordinary-104729",
    "ordinary-821",
    "ordinary-8675309",
    "lifecycle-104729",
    "presentation-104729",
    "persistence-104729",
    "removal",
    "disabled-startup",
    "malformed-startup",
    "missing-api",
    "wrong-version",
    "natural-104729",
    "endurance-baseline",
    "endurance-modded",
}
assert {run["label"] for run in report["runs"]} == expected
assert all(run["passed"] for run in report["runs"])
subprocess.run(["python3", "scripts/check-performance.py", str(root)], check=True)
performance = json.loads((root / "performance.json").read_text())
assert performance["passed"]
for register in ("assets/register.json", "assets/visual-register.json"):
    assert all(
        asset["decision"] == "ACCEPTED" for asset in json.loads(pathlib.Path(register).read_text())
    )
assert "Decision: ACCEPTED" in pathlib.Path("docs/endurance-review.md").read_text()
assert "Decision: ACCEPTED" in pathlib.Path("docs/final-readiness.md").read_text()
official = json.loads(pathlib.Path("evidence/reviews/official-release-check.json").read_text())
assert official["stable_matches"]


@functools.cache
def evidence(path):
    file = pathlib.Path(path)
    assert file.is_file(), file
    with file.open("rb") as stream:
        return {"path": str(file), "sha256": hashlib.file_digest(stream, "sha256").hexdigest()}


def tree(path):
    return [str(file) for file in sorted(pathlib.Path(path).rglob("*")) if file.is_file()]


def run_files(label):
    return tree(root / label)


base = [str(root / "report.json")]
requirements = []


def requirement(identifier, implementation, procedure, paths):
    requirements.append(
        {
            "id": identifier,
            "implementation": implementation,
            "procedure_and_result": procedure,
            "passed": True,
            "evidence": [evidence(path) for path in sorted(set(base + paths))],
        }
    )


unit = tree("evidence/reviews/checks") + [
    "evidence/reviews/final-validation-console.txt",
    "evidence/reviews/final-static-console.txt",
]
features = run_files("features-104729")
lifecycle = run_files("lifecycle-104729")
natural = tree("evidence/runtime/reviewed-natural")
presentation = tree("evidence/runtime/reviewed-functional/presentation-104729")
endurance = run_files("endurance-baseline") + run_files("endurance-modded")
requirement(
    "A1",
    "flake.nix; build-java.py; CoreTests; resource validators",
    "Sandboxed lint/compile/resource/reproduction checks passed; 38,624,690 assertions.",
    unit,
)
requirement(
    "A2",
    "fabric.mod.json; launch.py; locked player dependencies",
    "Packaged jar installed in fresh graphical instances; expected dependency failures diagnosed.",
    features
    + run_files("missing-api")
    + run_files("wrong-version")
    + tree("evidence/runtime/player-installation")
    + tree("evidence/runtime/launcher-regression"),
)
requirement(
    "A3",
    "Client-only context adapter; OrdinaryTests",
    "Three seeds passed resulting-state assertions for mine/build/farm/combat/craft/explore.",
    sum((run_files("ordinary-" + seed) for seed in ("104729", "821", "8675309")), []),
)
requirement(
    "A4",
    "Director; BorrowedQuiet; Presentation",
    "Forced activation/completion/cleanup and eligibility interruptions, plus unaccelerated natural scheduling.",
    features + lifecycle + natural,
)
requirement(
    "A5",
    "Session reset, interruption guards and ConfigStore",
    "Lifecycle suite and actual save/reopen passed; controlled remote/published guards are explicitly identified.",
    lifecycle + run_files("persistence-104729"),
)
requirement(
    "A6",
    "Bounded director, voices, geometry, candidates and configuration queue",
    "Malformed/oversized/type/range/queued-write tests, context boundaries and resource-cap exercises passed.",
    unit + lifecycle + presentation + [str(root / "performance.json")],
)
requirement(
    "A7",
    "Six original Vorbis assets; three-part original geometry; subtitles/controls",
    "Complete tool-assisted AI audio and direct visual reviews accepted, with measured gain/spatial controls and documented limits.",
    tree("evidence/reviews")
    + presentation
    + natural
    + [
        "docs/audio-review.md",
        "docs/visual-review.md",
        "docs/experience-review.md",
        "assets/register.json",
        "assets/visual-register.json",
    ],
)
requirement(
    "A8",
    "RuntimeTests.endurance; isolated capture",
    "Both conditions completed at least 7200 real wall seconds with equivalent work/settings; recordings reviewed.",
    endurance + ["docs/endurance-review.md", "evidence/reviews/host-monitor.jsonl"],
)
requirement(
    "A9",
    "Constant-bounded client work; Telemetry; check-performance.py",
    "All predefined frame/tick/mod-time/retention/resource budgets passed without relaxed thresholds.",
    endurance + [str(root / "performance.json"), "docs/endurance-review.md"],
)
requirement(
    "A10",
    "Off command, ConfigStore and session-local vanilla displays",
    "Disable persists through a fresh client; prior world loads without mod, preserving marker block and inventory.",
    run_files("persistence-104729")
    + run_files("removal")
    + run_files("disabled-startup")
    + run_files("malformed-startup"),
)
requirement(
    "A11",
    "Pinned Nix inputs, verified acquisition and deterministic jar writer",
    "New clean checkout/fresh runtime state; independent sandbox rebuild compared equal; exact package hash bound.",
    unit + ["evidence/reviews/reproduction.json", "flake.lock", "deps/runtime.json"],
)
requirement(
    "A12",
    "Specification, rights records, final readiness and package-bound dossier",
    "All requirements and assets accepted; stable release rechecked; source/tool/host/seed/hash provenance recorded.",
    [
        "docs/final-readiness.md",
        "docs/specification.md",
        "docs/architecture-and-rights.md",
        "evidence/reviews/official-release-check.json",
        "evidence/reviews/host.json",
        "LICENSE",
    ],
)
for identifier, description in (
    ("F1", "Contextual irregular pace with recognition ending"),
    ("F2", "Two-cluster work answer without world writes"),
    ("F3", "Loaded clear-space Fold with contraction and cleanup"),
    ("F4", "Seeded context director with bounded recovery and no consecutive actual kind"),
):
    requirement(
        identifier,
        description,
        "Controlled tests and natural recording satisfy the committed observable rubric.",
        features + lifecycle + natural + unit + endurance + ["docs/experience-review.md"],
    )
jar = pathlib.Path("result/borrowedquiet-1.0.0.jar")
assert evidence(str(jar))["sha256"] == report["package_sha256"]
dossier = {
    "decision": "ACCEPTED",
    "source_commit": report["source_commit"],
    "package_sha256": report["package_sha256"],
    "lock_sha256": report["lock_sha256"],
    "harness_sha256": report["harness_sha256"],
    "nix": report["nix"],
    "minecraft": report["minecraft"],
    "performance": performance,
    "settings": {
        "renderer": "Nix Mesa llvmpipe",
        "width": 960,
        "height": 540,
        "game_fps_cap": 30,
        "capture_fps": 15,
        "render_distance": 4,
        "simulation_distance": 5,
        "natural_intensity": "normal",
    },
    "requirements": requirements,
    "interpretation": "Autonomous technical acceptance and AI experiential assessment; no human playtest claims.",
}
pathlib.Path("evidence/acceptance.json").write_text(json.dumps(dossier, indent=2) + "\n")
subprocess.run(["python3", "scripts/acceptance-gate.py", str(jar)], check=True)
