#!/usr/bin/env python3
"""Record the separately observed harness-free UI installation after graceful exit."""

import hashlib
import json
import pathlib

root = pathlib.Path(".runtime/player-installation")
log = (root / "capture/game.log").read_text()
mods = sorted((root / "game/mods").glob("*.jar"))
assert {file.name for file in mods} == {"fabric-api.jar", "borrowedquiet-1.0.0.jar"}
assert "- fabric-client-gametest-api-v1" not in log
assert "Borrowed Quiet 1.0.0: local survival only" in log
assert "time query daytime<--[HERE]" in log
assert "Settings[enabled=false" in log
assert "Stopping!" in log and "All dimensions are saved" in log
assert not json.loads((root / "game/config/borrowedquiet.json").read_text())["enabled"]
screens = root / "game/screenshots"
screens.mkdir(exist_ok=True)
for name in (
    "startup",
    "menu-ready",
    "world-loaded",
    "normal-status",
    "create-world",
    "world-options",
    "plain-world",
    "cheats-disabled-control-2",
    "saved-title",
):
    source = root / (name + ".png")
    assert source.exists()
    (screens / source.name).write_bytes(source.read_bytes())
report = {
    "result": "PLAYER_INSTALLATION_PASS",
    "method": "AI observed actual UI screenshots and drove the isolated client using Nix xdotool; no GameTest harness or testing JVM properties.",
    "seed": "104729",
    "fresh_world": "Plain Installation",
    "mode": "Survival",
    "difficulty": "Normal",
    "allow_commands": False,
    "observations": [
        "Prepared save retained gold marker and three diamonds",
        "Fresh default world loaded without test data packs",
        "Vanilla time command denied; mod off command accepted",
        "Settings persisted and world saved through normal UI",
        "Client quit normally with process exit code 0",
    ],
    "mods": [
        {"name": file.name, "sha256": hashlib.sha256(file.read_bytes()).hexdigest()}
        for file in mods
    ],
    "launcher_sha256": hashlib.sha256(pathlib.Path("scripts/launch.py").read_bytes()).hexdigest(),
    "capture_script_sha256": hashlib.sha256(
        pathlib.Path("scripts/runtime-session.py").read_bytes()
    ).hexdigest(),
    "limits": "Supplemental installation check, not a performance comparison. Initial setup uses vanilla graphics defaults (16/12 distances). A mistimed input opened the vanilla Friends screen; the agent recovered and repeated the command with paced input. No account or network interaction was performed.",
}
(root / "report.json").write_text(json.dumps(report, indent=2) + "\n")
print(report["result"])
