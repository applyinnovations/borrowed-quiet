#!/usr/bin/env python3
"""Decode complete audio, measure samples, and reject silence before inference."""

import array
import json
import math
import subprocess
import sys

raw = subprocess.check_output(
    [
        "ffmpeg",
        "-nostdin",
        "-v",
        "error",
        "-i",
        sys.argv[1],
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-f",
        "s16le",
        "-",
    ]
)
samples = array.array("h", raw)
if sys.byteorder != "little":
    samples.byteswap()
peak = max(map(abs, samples), default=0)
rms = math.sqrt(sum(x * x for x in samples) / max(1, len(samples)))
print(
    json.dumps(
        {
            "seconds": len(samples) / 16000,
            "peak_sample": peak,
            "peak_dbfs": 20 * math.log10(peak / 32768) if peak else None,
            "rms_dbfs": 20 * math.log10(rms / 32768) if rms else None,
            "clipped_samples": sum(abs(x) >= 32767 for x in samples),
        }
    )
)
if peak <= 2:
    sys.exit("REJECTED: silent input; no perceptual inference permitted.")
