#!/usr/bin/env python3
"""Recheck authoritative release metadata and fingerprint reviewed policy pages."""

import datetime
import hashlib
import json
import pathlib
import subprocess
import sys

urls = {
    "manifest": "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json",
    "release": "https://www.minecraft.net/en-us/article/minecraft-java-edition-26-2",
    "eula": "https://www.minecraft.net/en-us/eula",
    "usage": "https://www.minecraft.net/en-us/usage-guidelines",
}
records = {}
for name, url in urls.items():
    data = subprocess.check_output(
        [
            "curl",
            "--fail",
            "--location",
            "--silent",
            "--show-error",
            "--max-time",
            "30",
            "--retry",
            "2",
            "--user-agent",
            "Mozilla/5.0",
            url,
        ]
    )
    if name == "release":
        assert b"26.2" in data and b"Minecraft" in data
    if name == "eula":
        assert b"Mods" in data and b"distribute" in data
    if name == "usage":
        assert b"modded version" in data.lower() and b"screenshots" in data.lower()
    records[name] = {"url": url, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    if name == "manifest":
        metadata = json.loads(data)
        records[name]["latest"] = metadata["latest"]
        assert metadata["latest"]["release"] == "26.2", (
            "Stable release changed: update and revalidate"
        )
        stable = next(item for item in metadata["versions"] if item["id"] == "26.2")
        assert stable["type"] == "release"
        records[name]["stable"] = stable
record = {
    "checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "sources": records,
    "stable_matches": True,
    "rights_interpretation": "See docs/architecture-and-rights.md; fingerprints alone are not legal review.",
}
pathlib.Path(sys.argv[1]).write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
