#!/usr/bin/env python3
"""Export completed inspection records, not standalone extracted vanilla audio."""

import hashlib
import json
import pathlib
import shutil

destination = pathlib.Path("evidence/reviews")
destination.mkdir(parents=True, exist_ok=False)
groups = {
    "asset-measurements": pathlib.Path(".runtime/asset-analysis-final"),
    "presentation-measurements": pathlib.Path(".runtime/clean-final/audio-analysis-final"),
    "isolated-and-overlap": pathlib.Path(".runtime/listening-cuda-1"),
    "context-listening": pathlib.Path(".runtime/final-listening-review-2"),
    "blind-visual": pathlib.Path(".runtime/blind-review-final"),
}
for name, source in groups.items():
    for file in source.rglob("*"):
        if file.is_file() and file.suffix in {".json", ".txt", ".log", ".png"}:
            target = destination / name / file.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, target)
for source, name in (
    (".runtime/final-listening-inputs/manifest.json", "excerpt-manifest.json"),
    (".runtime/qwen3-cuda-calibration-2.txt", "calibration.txt"),
    (".runtime/cuda-device-verification.txt", "cuda-device.txt"),
):
    shutil.copyfile(source, destination / name)
files = []
for file in sorted(destination.rglob("*")):
    if file.is_file():
        with file.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        files.append({"path": str(file), "sha256": digest})
(destination / "files.json").write_text(json.dumps(files, indent=2) + "\n")
print("REVIEW_EXPORT", len(files))
