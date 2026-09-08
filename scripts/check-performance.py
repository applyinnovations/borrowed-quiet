#!/usr/bin/env python3
"""Compare predefined budgets; never convert a missing benchmark into a pass."""

import csv
import json
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])


def percentile(values, quantile):
    values = sorted(values)
    return values[min(len(values) - 1, int((len(values) - 1) * quantile))]


def condition(name):
    directory = root / ("endurance-" + name)
    with (directory / "game/metrics.csv").open() as file:
        rows = [{key: float(value) for key, value in row.items()} for row in csv.DictReader(file)]
    assert rows[-1]["seconds"] >= 7200, "Incomplete wall-time endurance"
    stable = [row for row in rows if row["seconds"] >= 120]
    log = (directory / "capture/game.log").read_text()
    heaps = [
        (float(t), int(h))
        for t, h in re.findall(r"POST_GC seconds=([\d.]+) heap=(\d+)", log)
        if float(t) >= 1800
    ]
    assert len(heaps) >= 60, "Missing post-GC retention evidence"
    return {
        "seconds": rows[-1]["seconds"],
        "samples": len(rows),
        "frame_p95_ns": percentile([row["frame_ns"] for row in stable], 0.95),
        "tick_p95_ns": percentile([row["tick_ns"] for row in stable], 0.95),
        "mod_p99_ns": percentile([row["mod_ns"] for row in stable], 0.99),
        "mod_max_ns": max(row["mod_ns"] for row in stable),
        "heap_growth": heaps[-1][1] - heaps[0][1],
        "max_sounds": max(row["sounds"] for row in rows),
        "max_entities": max(row["entities"] for row in rows),
        "max_trail": max(row["trail"] for row in rows),
    }


baseline, modded = condition("baseline"), condition("modded")
checks = {
    "mod_p99": modded["mod_p99_ns"] <= 500000,
    "mod_maximum": modded["mod_max_ns"] <= 5000000,
    "frames": modded["frame_p95_ns"] - baseline["frame_p95_ns"]
    <= max(3000000, baseline["frame_p95_ns"] * 0.2),
    "ticks": modded["tick_p95_ns"] - baseline["tick_p95_ns"] <= 1000000,
    "heap": modded["heap_growth"] - baseline["heap_growth"] <= 128 * 1024 * 1024,
    "resources": modded["max_sounds"] <= 2
    and modded["max_entities"] <= 3
    and modded["max_trail"] <= 32,
}
result = {"baseline": baseline, "modded": modded, "checks": checks, "passed": all(checks.values())}
(root / "performance.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if not result["passed"]:
    sys.exit("FAIL: performance budget; investigate and rerun affected validation")
