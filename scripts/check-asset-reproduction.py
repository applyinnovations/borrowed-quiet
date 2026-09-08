#!/usr/bin/env python3
"""Regenerate every original master and encoded sound in fresh state and compare bytes."""

import json
import pathlib
import subprocess
import sys
import tempfile

root = pathlib.Path(sys.argv[1])
with tempfile.TemporaryDirectory(prefix="borrowedquiet-asset-reproduction-") as temporary:
    subprocess.run([sys.executable, str(root / "assets/synthesize.py"), temporary], check=True)
    for asset in json.loads((root / "assets/register.json").read_text()):
        for key in ("original", "file"):
            path = asset[key]
            assert (root / path).read_bytes() == (pathlib.Path(temporary) / path).read_bytes(), path
        print("PASS: independently regenerated master and OGG", asset["id"])
