#!/usr/bin/env python3
"""Prepare complete, traceable runtime excerpts and level-control comparisons."""

import hashlib
import json
import pathlib
import subprocess

root = pathlib.Path(".runtime/final-listening-inputs")
root.mkdir(exist_ok=False)
presentation = pathlib.Path(".runtime/clean-final/audio-analysis-final")
records = []


def extract(source, name, start, duration, gain=1, channel=None):
    destination = root / (name + ".wav")
    filters = [f"volume={gain}"]
    if channel is not None:
        filters.append(f"pan=mono|c0=c{channel}")
    subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-ss",
            str(start),
            "-i",
            str(source),
            "-t",
            str(duration),
            "-vn",
            "-af",
            ",".join(filters),
            "-ac",
            "1",
            "-ar",
            "16000",
            str(destination),
        ],
        check=True,
    )
    records.append(
        {
            "file": str(destination),
            "source": str(source),
            "start": start,
            "duration": duration,
            "gain": gain,
            "channel": channel,
            "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        }
    )


for index in (0, 1, 2, 3, 5, 6, 7, 8, 9, 10):
    directory = next(presentation.glob(f"{index:02d}-*"))
    measurement = json.loads((directory / "measurement.json").read_text())
    extract(
        pathlib.Path(measurement["source"]),
        directory.name,
        measurement["start_seconds"],
        measurement["duration_seconds"],
        10,
    )
    if index in (0, 1):
        for channel in (0, 1):
            extract(
                pathlib.Path(measurement["source"]),
                directory.name + f"-ear-{channel}",
                measurement["start_seconds"],
                measurement["duration_seconds"],
                10,
                channel,
            )

measurement = json.loads((presentation / "11-maximum-overlap/measurement.json").read_text())
for gain in (1, 4):
    extract(
        pathlib.Path(measurement["source"]),
        f"overlap-gain-{gain}",
        measurement["start_seconds"],
        measurement["duration_seconds"],
        gain,
    )

source = pathlib.Path(".runtime/natural-2/natural-104729/capture/session.mkv")
for index, (start, duration) in enumerate(
    ((157, 24), (445, 22), (618, 18), (887, 25), (1194, 24), (1434, 25), (1639, 22), (1814, 25))
):
    extract(source, f"natural-{index}", start, duration, 4)
(root / "manifest.json").write_text(json.dumps(records, indent=2) + "\n")
