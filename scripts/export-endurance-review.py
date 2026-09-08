#!/usr/bin/env python3
"""Export reviewed endurance material while excluding reconstructed gameplay audio."""

import pathlib
import shutil

destination = pathlib.Path("evidence/reviews/endurance")
destination.mkdir(parents=True, exist_ok=False)
groups = {
    "capture-review": pathlib.Path(".runtime/endurance-review-final"),
    "listening": pathlib.Path(".runtime/endurance-listening-final"),
    "listening-followup": pathlib.Path(".runtime/endurance-listening-followup"),
}
for name, source in groups.items():
    for file in sorted(source.rglob("*")):
        if file.is_file() and file.suffix in {".json", ".txt", ".log", ".png"}:
            target = destination / name / file.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, target)
(destination / "independent-review.md").write_text(
    pathlib.Path(".runtime/endurance-independent-review.md")
    .read_text()
    .replace("endurance-review-final/", "capture-review/")
)
for source, name in (
    (".runtime/final-validation-console.txt", "final-validation-console.txt"),
    (".runtime/final-host-monitor.jsonl", "host-monitor.jsonl"),
    (".runtime/final-static-console.txt", "final-static-console.txt"),
):
    shutil.copyfile(source, destination.parent / name)
print("ENDURANCE_REVIEW_EXPORTED", destination)
