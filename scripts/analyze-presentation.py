#!/usr/bin/env python3
"""Map actual capture to clocked in-game marks and measure each complete scenario."""

import json
import pathlib
import re
import subprocess
import sys

capture = pathlib.Path(sys.argv[1])
output = pathlib.Path(sys.argv[2])
output.mkdir(parents=True, exist_ok=True)
start = json.loads((capture / "session-start.json").read_text())["recording_start_unix"]
marks = [
    (int(ms) / 1000 - start, label)
    for ms, label in re.findall(r"AV_MARK (\d+) (.+)", (capture / "game.log").read_text())
]
report = []
for index, (seconds, label) in enumerate(marks):
    if label.startswith("fold "):
        continue
    end = marks[index + 1][0] if index + 1 < len(marks) else seconds + 3
    directory = output / (f"{index:02d}-" + re.sub(r"[^a-zA-Z0-9]+", "-", label))
    subprocess.run(
        [
            "python3",
            "scripts/analyze-audio.py",
            str(capture / "session.mkv"),
            str(directory),
            "--start",
            str(max(0, seconds - 0.1)),
            "--duration",
            str(end - seconds),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    report.append(
        {
            "label": label,
            "start_seconds": seconds,
            "measurement": str(directory / "measurement.json"),
            "listening_copy": str(directory / "listening.wav"),
        }
    )
(output / "index.json").write_text(json.dumps(report, indent=2) + "\n")
print(output / "index.json")
