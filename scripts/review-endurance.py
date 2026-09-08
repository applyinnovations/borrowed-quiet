#!/usr/bin/env python3
"""Prepare measured, timecoded endurance evidence; never manufacture an AI verdict."""

import argparse
import csv
import datetime
import hashlib
import json
import pathlib
import re
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("runtime", type=pathlib.Path)
parser.add_argument("output", type=pathlib.Path)
args = parser.parse_args()
report = json.loads((args.runtime / "report.json").read_text())
assert report["result"] == "RUNTIME_CHECKS_PASS", "Complete runtime checks first"
args.output.mkdir(parents=True, exist_ok=False)
summary = {}
clips = []


def command(arguments, log=None):
    result = subprocess.run(arguments, capture_output=True, check=True)
    if log:
        log.write_bytes(result.stderr)
    return result.stdout


for name in ("baseline", "modded"):
    directory = args.runtime / ("endurance-" + name)
    output = args.output / name
    output.mkdir()
    capture = directory / "capture"
    video = capture / "session.mkv"
    start = json.loads((capture / "session-start.json").read_text())["recording_start_unix"]
    with (directory / "game/metrics.csv").open() as stream:
        rows = [{key: float(value) for key, value in row.items()} for row in csv.DictReader(stream)]
    assert rows[-1]["seconds"] >= 7200
    events = []
    warnings = []
    day = datetime.datetime.fromtimestamp(start).date()
    for line in (capture / "game.log").read_text().splitlines():
        clock = re.match(r"\[(\d\d:\d\d:\d\d)\]", line)
        if not clock:
            continue
        wall = datetime.datetime.combine(day, datetime.time.fromisoformat(clock[1])).timestamp()
        if wall < start - 43200:
            wall += 86400
        seconds = wall - start
        event = re.search(r"BQ tick=(\d+) (start|end) (PACE|WALL|FOLD) (.+)", line)
        if event:
            events.append(
                {
                    "video_seconds": seconds,
                    "tick": int(event[1]),
                    "action": event[2],
                    "kind": event[3],
                    "detail": event[4],
                }
            )
        if "/WARN]" in line or "/ERROR]" in line:
            warnings.append({"video_seconds": seconds, "line": line})
    summary[name] = {
        "seconds": rows[-1]["seconds"],
        "maximum_sample_gap_seconds": max(
            b["seconds"] - a["seconds"] for a, b in zip(rows, rows[1:])
        ),
        "maximum_recorded_frame_ms": max(row["frame_ns"] for row in rows) / 1e6,
        "warnings": warnings,
        "events": events,
        "time_mapping": "Log timestamps have one-second resolution; offset uses capture metadata and the recorded host timezone.",
    }
    command(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-xerror",
            "-threads",
            "2",
            "-i",
            str(video),
            "-map",
            "0",
            "-f",
            "null",
            "-",
        ],
        output / "decode.log",
    )
    summary[name]["complete_decode"] = "PASS"
    command(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "info",
            "-i",
            str(video),
            "-vn",
            "-af",
            "astats=metadata=0:reset=0",
            "-f",
            "null",
            "-",
        ],
        output / "audio-statistics.log",
    )
    command(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-threads",
            "2",
            "-i",
            str(video),
            "-vf",
            "fps=1/60,scale=320:180,tile=4x6",
            "-fps_mode",
            "vfr",
            str(output / "overview-%02d.png"),
        ],
        output / "overview.log",
    )
    summary[name]["overview_method"] = (
        "One frame per minute, 4x6 tiles; overview only, not frame-accurate event timing. Native checkpoint screenshots and targeted excerpts supplement it."
    )
    if name == "baseline":
        near = [row for row in rows if 5600 <= row["seconds"] <= 5625]
        summary[name]["timing_warning_window"] = {
            "metric_seconds": [5600, 5625],
            "samples": len(near),
            "maximum_sample_gap_seconds": max(
                b["seconds"] - a["seconds"] for a, b in zip(near, near[1:])
            ),
            "maximum_frame_ms": max(row["frame_ns"] for row in near) / 1e6,
            "maximum_server_average_tick_ms": max(row["tick_ns"] for row in near) / 1e6,
        }
        selections = [(120, 20, "ordinary-early"), (7100, 20, "ordinary-late")]
    else:
        starts = [event for event in events if event["action"] == "start"]
        selections = []
        for kind in ("PACE", "WALL", "FOLD"):
            matching = [event for event in starts if event["kind"] == kind]
            assert matching, kind
            for exposure, event in (("first", matching[0]), ("last", matching[-1])):
                ending = next(
                    item
                    for item in events
                    if item["action"] == "end"
                    and item["tick"] > event["tick"]
                    and item["kind"] == kind
                )
                selections.append(
                    (
                        max(0, event["video_seconds"] - 3),
                        ending["video_seconds"] - event["video_seconds"] + 7,
                        kind.lower() + "-" + exposure,
                    )
                )
    for seconds, duration, label in selections:
        clip = output / (label + ".wav")
        command(
            [
                "ffmpeg",
                "-nostdin",
                "-v",
                "error",
                "-ss",
                str(seconds),
                "-i",
                str(video),
                "-t",
                str(duration),
                "-vn",
                "-af",
                "volume=4",
                "-ac",
                "1",
                "-ar",
                "16000",
                str(clip),
            ]
        )
        clips.append(
            {
                "file": str(clip),
                "source": str(video),
                "start": seconds,
                "duration": duration,
                "gain": 4,
                "sha256": hashlib.sha256(clip.read_bytes()).hexdigest(),
            }
        )
        command(
            [
                "ffmpeg",
                "-nostdin",
                "-v",
                "error",
                "-ss",
                str(seconds),
                "-i",
                str(video),
                "-t",
                str(duration),
                "-vf",
                "fps=2,scale=320:180,tile=4x6",
                "-fps_mode",
                "vfr",
                str(output / (label + "-%02d.png")),
            ]
        )
(args.output / "inspection-inputs.json").write_text(
    json.dumps({"measurements": summary, "clips": clips}, indent=2) + "\n"
)
print(args.output / "inspection-inputs.json")
