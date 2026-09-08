#!/usr/bin/env python3
"""Measured raw levels and complete derived listening clips; never a listening verdict."""

import argparse
import array
import hashlib
import json
import math
import pathlib
import re
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("input", type=pathlib.Path)
parser.add_argument("output", type=pathlib.Path)
parser.add_argument("--start", type=float, default=0)
parser.add_argument("--duration", type=float)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
selection = ["-ss", str(args.start), "-i", str(args.input)]
if args.duration is not None:
    selection += ["-t", str(args.duration)]
command = ["ffmpeg", "-nostdin", "-v", "error", *selection]
metadata = json.loads(
    subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_streams",
            "-of",
            "json",
            str(args.input),
        ]
    )
)
channel_count = metadata["streams"][0]["channels"]
assert channel_count in (1, 2), "Expected mono asset or stereo capture"
decoded = subprocess.check_output(command + ["-ar", "48000", "-f", "f32le", "-"])
samples = array.array("f", decoded)
channels = [samples[index::channel_count] for index in range(channel_count)]


def db(value):
    return 20 * math.log10(value) if value > 0 else None


def measure(values):
    return {
        "peak_dbfs": db(max(map(abs, values))),
        "rms_dbfs": db(math.sqrt(sum(x * x for x in values) / len(values))),
        "clipped_samples": sum(abs(x) >= 1 for x in values),
    }


loudness = subprocess.run(
    [
        "ffmpeg",
        "-nostdin",
        "-v",
        "info",
        "-f",
        "f32le",
        "-ar",
        "48000",
        "-ac",
        str(channel_count),
        "-i",
        "pipe:0",
        "-af",
        "apad=pad_dur=1,loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
        "-f",
        "null",
        "-",
    ],
    capture_output=True,
    input=decoded,
    check=True,
)
match = re.search(r'\{\s*"input_i".*?\}', loudness.stderr.decode(), re.S)
report = {
    "source": str(args.input),
    "source_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
    "start_seconds": args.start,
    "duration_seconds": len(samples) / (48000 * channel_count),
    "channels": [measure(values) for values in channels],
    "loudness": json.loads(match.group()) if match else None,
    "loudness_method": "Exact selected PCM followed by 1 second of digital silence, permitting the 400 ms R128 window for short one-shots; no adjacent scenario audio enters the measurement.",
    "interpretation": "Objective measurement only; separate complete audible inspection required.",
}
peak = max(map(abs, samples))
gain = min(100, 0.707 / peak) if peak else 1
report["listening_copy_gain_db"] = db(gain)
subprocess.run(
    command
    + [
        "-y",
        "-af",
        f"volume={gain}",
        "-ac",
        "1",
        "-ar",
        "16000",
        str(args.output / "listening.wav"),
    ],
    check=True,
)
(args.output / "measurement.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
