#!/usr/bin/env python3
"""Validate every shipped resource, decoded audio limit, jar boundary and asset hash."""

import array
import hashlib
import json
import math
import pathlib
import subprocess
import sys
import zipfile

root = pathlib.Path(sys.argv[1])
jar = pathlib.Path(sys.argv[2])
register = json.loads((root / "assets/register.json").read_text())
sound_root = root / "src/resources/assets/borrowedquiet"
sounds = json.loads((sound_root / "sounds.json").read_text())
language = json.loads((sound_root / "lang/en_us.json").read_text())
assert set(sounds) == {asset["id"] for asset in register}
for asset in register:
    path = root / asset["file"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == asset["sha256"], path
    probe = json.loads(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(path)]
        )
    )
    stream = probe["streams"][0]
    assert (
        stream["channels"] == 1
        and stream["codec_name"] == "vorbis"
        and stream["sample_rate"] == "48000"
    )
    pcm = array.array(
        "f",
        subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-"]),
    )
    assert all(math.isfinite(x) for x in pcm)
    peak = max(map(abs, pcm))
    assert 0 < peak <= 10 ** (-12 / 20), (path, peak)
    assert sounds[asset["id"]]["subtitle"] in language
    print(
        asset["id"],
        "PASS peak_dbfs=",
        20 * math.log10(peak),
        "seconds=",
        len(pcm) / 48000,
    )
with zipfile.ZipFile(jar) as archive:
    names = archive.namelist()
    assert not any(
        name.startswith(("net/minecraft/", "quiet/test/")) or name.endswith(".wav")
        for name in names
    )
    assert "fabric.mod.json" in names and jar.stat().st_size <= 2 * 1024 * 1024
print("PASS: resources, decoded peaks, metadata, package boundaries and size")
