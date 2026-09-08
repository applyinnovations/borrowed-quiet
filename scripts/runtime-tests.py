#!/usr/bin/env python3
"""Install the Nix-built package into fresh test instances and retain actual capture evidence."""

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import shutil
import subprocess

root = pathlib.Path(__file__).resolve().parent.parent
os.chdir(root)
parser = argparse.ArgumentParser()
parser.add_argument(
    "--suite",
    choices=[
        "all",
        "features",
        "ordinary",
        "lifecycle",
        "presentation",
        "persistence",
        "endurance",
        "natural",
    ],
    default="all",
)
parser.add_argument("--endurance", action="store_true")
parser.add_argument("--output", type=pathlib.Path)
args = parser.parse_args()
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
output = (args.output or root / ".runtime/validation" / stamp).resolve()
output.mkdir(parents=True, exist_ok=False)
subprocess.run(["python3", "scripts/acquire.py", "--prepare"], check=True)
subprocess.run(
    ["nix", "build", "--no-update-lock-file", ".#default", "-o", ".runtime/release"], check=True
)
subprocess.run(
    ["nix", "build", "--no-update-lock-file", ".#compile-deps", "-o", ".runtime/nix-deps"],
    check=True,
)
(root / "build").mkdir(exist_ok=True)
subprocess.run(
    [
        "python3",
        "scripts/build-java.py",
        "tests/runtime",
        ".runtime/nix-deps",
        "build/runtime-tests.jar",
    ],
    check=True,
)
package = (root / ".runtime/release/borrowedquiet-1.0.0.jar").resolve()
harness = root / "build/runtime-tests.jar"
report = {
    "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"])),
    "nix": subprocess.check_output(["nix", "--version"], text=True).strip(),
    "lock_sha256": hashlib.sha256((root / "flake.lock").read_bytes()).hexdigest(),
    "package_sha256": hashlib.sha256(package.read_bytes()).hexdigest(),
    "harness_sha256": hashlib.sha256(harness.read_bytes()).hexdigest(),
    "minecraft": "26.2",
    "started_utc": stamp,
    "runs": [],
    "result": "INCOMPLETE",
}


def save():
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")


def run(label, suite, seed="104729", baseline=False, seconds=0, dependency=None):
    directory = output / label
    if suite == "removal":
        shutil.copytree(output / "persistence-104729/game/saves", directory / "game/saves")
    env = dict(os.environ, BQ_TEST_SUITE=suite, BQ_TEST_SEED=seed, BQ_TEST_SECONDS=str(seconds))
    if dependency:
        env["BQ_DEPENDENCY_TEST"] = dependency
    command = [
        "python3",
        "scripts/runtime-session.py",
        str(directory / "capture"),
        str(seconds + 300 if seconds else 2100 if suite == "natural" else 600),
        "python3",
        "scripts/launch.py",
        str(directory / "game"),
        str(harness),
    ]
    if not baseline:
        command.append(str(package))
    result = subprocess.run(command, env=env, check=False)
    log = directory / "capture/game.log"
    content = log.read_text(errors="replace") if log.exists() else ""
    if dependency:
        passed = (
            result.returncode != 0
            and "borrowedquiet" in content.lower()
            and "requires" in content.lower()
        )
    else:
        marker = (
            "ENDURANCE_PASS"
            if seconds
            else {
                "ordinary": "ORDINARY_PASS exploration",
                "lifecycle": "LIFECYCLE_PASS sleep",
                "presentation": "LIFECYCLE_PASS fold-enclosed-mine",
                "features": "SCENARIO_PASS FOLD",
                "persistence": "PERSISTENCE_PASS",
                "removal": "REMOVAL_PASS",
                "natural": "NATURAL_PASS",
            }[suite]
        )
        passed = result.returncode == 0 and marker in content
    report["runs"].append(
        {
            "label": label,
            "suite": suite,
            "seed": seed,
            "seconds": seconds,
            "baseline": baseline,
            "returncode": result.returncode,
            "passed": passed,
        }
    )
    save()
    if not passed:
        raise SystemExit("FAIL: " + label + "; inspect " + str(directory))


save()
suites = (
    ["features", "ordinary", "lifecycle", "presentation", "persistence"]
    if args.suite == "all"
    else [args.suite]
)
for suite in suites:
    if suite == "endurance":
        continue
    for seed in ["104729", "821", "8675309"] if suite == "ordinary" else ["104729"]:
        run(suite + "-" + seed, suite, seed)
    if suite == "persistence":
        run("removal", "removal", baseline=True)
if args.suite == "all":
    run("missing-api", "features", dependency="missing-api")
    run("wrong-version", "features", dependency="wrong-version")
if args.endurance or args.suite == "endurance":
    if args.endurance:
        run("natural-104729", "natural")
    run("endurance-baseline", "features", baseline=True, seconds=7200)
    run("endurance-modded", "features", seconds=7200)
    subprocess.run(["python3", "scripts/check-performance.py", str(output)], check=True)
report["result"] = "RUNTIME_CHECKS_PASS"
save()
print(output / "report.json")
