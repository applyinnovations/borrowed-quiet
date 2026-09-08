#!/usr/bin/env python3
"""Export only owned recordings/reports, never game software, assets, accounts or saves."""

import argparse
import hashlib
import json
import pathlib
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("input", type=pathlib.Path)
parser.add_argument("output", type=pathlib.Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=False)
records = []
for file in sorted(args.input.rglob("*")):
    if not file.is_file():
        continue
    relative = file.relative_to(args.input)
    keep = (
        relative.name in {"report.json", "performance.json", "metrics.csv"}
        or "screenshots" in relative.parts
        and file.suffix == ".png"
        or "capture" in relative.parts
        and relative.name
        in {
            "session.mkv",
            "session-start.json",
            "game.log",
            "capture.log",
            "audio-routing.log",
            "audio-server.log",
            "display.log",
        }
    )
    if not keep:
        continue
    target = args.output / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(file, target)
    with target.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    records.append({"path": str(relative), "bytes": target.stat().st_size, "sha256": digest})
(args.output / "files.json").write_text(json.dumps(records, indent=2) + "\n")
print(f"Exported {len(records)} evidence files, excluding all Minecraft software and saves.")
