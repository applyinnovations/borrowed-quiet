#!/usr/bin/env python3
"""Local, authorised offline development launch; no accounts or credentials handled."""

import hashlib
import json
import os
import pathlib
import shutil
import sys

root = pathlib.Path(__file__).resolve().parent.parent
lock = json.loads((root / "deps/runtime.json").read_text())
cache = root / ".runtime"
game = pathlib.Path(sys.argv[1]).resolve()
game.mkdir(parents=True, exist_ok=True)
(game / "mods").mkdir(exist_ok=True)
cp = []
for item in lock["files"]:
    path = cache / item["path"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
        raise SystemExit("Unverified runtime input: " + item["path"])
    if item["path"].startswith("libraries/"):
        cp.append(str(path))
    elif item["path"].startswith(("mods/", "testlibs/")):
        shutil.copyfile(path, game / "mods" / path.name)
for mod in sys.argv[2:]:
    shutil.copyfile(mod, game / "mods" / pathlib.Path(mod).name)
options = game / "options.txt"
if not options.exists():
    options.write_text(
        "renderDistance:4\nsimulationDistance:4\nmaxFps:30\nguiScale:2\n"
        "pauseOnLostFocus:false\nsoundCategory_master:0.6\nsoundCategory_music:0.2\n"
    )
args = [
    "java",
    "-Xms1G",
    "-Xmx3G",
    "--enable-native-access=ALL-UNNAMED",
    "--sun-misc-unsafe-memory-access=allow",
    "-Dfabric.client.gametest",
    "-Dfabric.client.gametest.disableNetworkSynchronizer=true",
    "-Dminecraft.launcher.brand=quiet-nix-validation",
    "-cp",
    ":".join(cp),
    lock["main_class"],
    "--offlineDeveloperMode",
    "--username",
    "QuietTest",
    "--version",
    "26.2",
    "--gameDir",
    str(game),
    "--assetsDir",
    str(cache / "assets"),
    "--assetIndex",
    "32",
    "--accessToken",
    "0",
    "--width",
    "960",
    "--height",
    "540",
]
os.chdir(game)
os.execvp(args[0], args)
