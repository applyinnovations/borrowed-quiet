#!/usr/bin/env python3
"""Original deterministic material foley. No samples, trained model or third-party assets."""

import array
import hashlib
import json
import math
import pathlib
import random
import subprocess
import sys
import wave

root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
masters = root / "assets/masters"
sounds = root / "src/resources/assets/borrowedquiet/sounds"
masters.mkdir(parents=True, exist_ok=True)
sounds.mkdir(parents=True, exist_ok=True)
rate = 48000
register = []
for index, (name, duration) in enumerate(
    [
        ("tread1", 0.46),
        ("tread2", 0.51),
        ("tap1", 0.38),
        ("tap2", 0.42),
        ("scrape", 1.58),
        ("fold", 1.16),
    ]
):
    rng = random.Random(104729 + index)
    values = []
    low = 0.0
    deep = 0.0
    for frame in range(int(duration * rate)):
        t = frame / rate
        noise = rng.uniform(-1, 1)
        low = 0.86 * low + 0.14 * noise
        deep = 0.97 * deep + 0.03 * noise
        envelope = min(1, t / 0.009) * min(1, (duration - t) / 0.045)
        if name.startswith("tread"):
            body = deep * math.exp(-20 * t)
            gravel = low * (math.exp(-15 * t) + 0.5 * math.exp(-420 * (t - 0.12) ** 2))
            value = envelope * (2.6 * body + 0.9 * gravel + 0.03 * noise * math.exp(-18 * t))
        elif name.startswith("tap"):
            value = envelope * (
                0.8 * low * math.exp(-27 * t)
                + sum(
                    math.sin(2 * math.pi * frequency * t) * gain * math.exp(-decay * t)
                    for frequency, gain, decay in [
                        (189 + index * 11, 0.4, 19),
                        (527 + index * 19, 0.19, 24),
                        (1171, 0.07, 35),
                    ]
                )
            )
        elif name == "scrape":
            grain = max(0, math.sin(t * 31 + math.sin(t * 5)))
            value = envelope * math.sin(math.pi * t / duration) ** 1.2 * low * (0.3 + 0.7 * grain)
        else:
            value = (
                envelope
                * math.sin(math.pi * t / duration) ** 1.5
                * (
                    low * (0.5 + 0.25 * math.sin(57 * t))
                    + 0.08 * math.sin(2 * math.pi * (110 * t - 18 * t * t))
                )
            )
        values.append(value)
    # Headroom before Vorbis reconstruction; final decoded peaks are checked separately.
    scale = 10 ** (-14 / 20) / max(map(abs, values))
    samples = array.array("h", (round(x * scale * 32767) for x in values))
    if sys.byteorder != "little":
        samples.byteswap()
    master = masters / (name + ".wav")
    with wave.open(str(master), "wb") as wav:
        wav.setparams((1, 2, rate, len(samples), "NONE", "not compressed"))
        wav.writeframes(samples.tobytes())
    output = sounds / (name + ".ogg")
    subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-y",
            "-v",
            "error",
            "-i",
            str(master),
            "-map_metadata",
            "-1",
            "-fflags",
            "+bitexact",
            "-flags:a",
            "+bitexact",
            "-c:a",
            "libvorbis",
            "-q:a",
            "5",
            str(output),
        ],
        check=True,
    )
    register.append(
        {
            "id": name,
            "creator": "Borrowed Quiet project",
            "source": "assets/synthesize.py",
            "license": "MIT",
            "acquired": "2026-09-08",
            "original": str(master.relative_to(root)),
            "modifications": "Original seeded synthesis, peak headroom, Vorbis encoding",
            "file": str(output.relative_to(root)),
            "seconds": duration,
            "channels": 1,
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "inspection": "PENDING",
            "decision": "NOT ACCEPTED",
        }
    )
(root / "assets/register.json").write_text(json.dumps(register, indent=2) + "\n")
