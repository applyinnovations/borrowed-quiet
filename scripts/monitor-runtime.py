#!/usr/bin/env python3
"""Low-cost host/load evidence alongside the real-time runtime validation."""

import json
import os
import pathlib
import sys
import time

directory = pathlib.Path(sys.argv[1])
destination = pathlib.Path(sys.argv[2])
deadline = time.monotonic() + 7 * 3600
with destination.open("x") as output:
    while time.monotonic() < deadline:
        report_path = directory / "report.json"
        report = json.loads(report_path.read_text()) if report_path.exists() else {}
        captures = list(directory.glob("*/capture/game.log"))
        latest = max(captures, key=lambda file: file.stat().st_mtime) if captures else None
        metric = None
        if latest:
            metrics = latest.parent.parent / "game/metrics.csv"
            if metrics.exists() and metrics.stat().st_size:
                with metrics.open("rb") as stream:
                    stream.seek(max(0, metrics.stat().st_size - 2048))
                    lines = stream.read().decode().splitlines()
                    if lines:
                        metric = lines[-1]
        entry = {
            "unix": time.time(),
            "loadavg": os.getloadavg(),
            "cpu_counters": pathlib.Path("/proc/stat").read_text().splitlines()[0],
            "memory": [
                line
                for line in pathlib.Path("/proc/meminfo").read_text().splitlines()
                if line.startswith(("MemAvailable:", "SwapFree:"))
            ],
            "phase": latest.parent.parent.name if latest else "acquisition",
            "last_metric": metric,
            "completed_runs": len(report.get("runs", [])),
            "result": report.get("result", "INCOMPLETE"),
        }
        output.write(json.dumps(entry) + "\n")
        output.flush()
        print(entry["phase"], entry["completed_runs"], metric, flush=True)
        if entry["result"] == "RUNTIME_CHECKS_PASS" or any(
            not run["passed"] for run in report.get("runs", [])
        ):
            break
        time.sleep(30)
