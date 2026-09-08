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
player_mode = os.environ.get("BQ_PLAYER_MODE") == "1"
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
        if player_mode and item["path"].startswith("testlibs/"):
            continue
        if (
            os.environ.get("BQ_DEPENDENCY_TEST") == "missing-api"
            and item["path"] == "mods/fabric-api.jar"
        ):
            continue
        shutil.copyfile(path, game / "mods" / path.name)
for mod in sys.argv[2:]:
    shutil.copyfile(mod, game / "mods" / pathlib.Path(mod).name)
options = game / "options.txt"
if not options.exists():
    options.write_text(
        "version:4903\nmaxAnisotropyBit:2\ntextureFiltering:0\n"
        "renderDistance:4\nsimulationDistance:5\nmaxFps:30\nguiScale:2\n"
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
    "-Dfabric.noGui=true",
    "-Dborrowedquiet.testing=true",
    "-Dborrowedquiet.seed=104729",
    "-Dborrowedquiet.test.seconds=" + os.environ.get("BQ_TEST_SECONDS", "0"),
    "-Dborrowedquiet.test.suite=" + os.environ.get("BQ_TEST_SUITE", "features"),
    "-Dborrowedquiet.test.seed=" + os.environ.get("BQ_TEST_SEED", "104729"),
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
if os.environ.get("BQ_DEPENDENCY_TEST") == "wrong-version":
    args.insert(1, "-Dfabric.gameVersion=26.1")
if player_mode:
    args = [
        arg
        for arg in args
        if not arg.startswith(("-Dfabric.client.gametest", "-Dfabric.noGui", "-Dborrowedquiet."))
    ]
os.chdir(game)
os.execvp(args[0], args)
