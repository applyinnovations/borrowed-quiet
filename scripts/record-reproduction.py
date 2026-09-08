#!/usr/bin/env python3
"""Record actual independent rebuild and unchanged package-input provenance."""

import hashlib
import json
import pathlib
import subprocess

output = pathlib.Path("evidence/reviews")
report = json.loads(pathlib.Path("evidence/runtime/final/report.json").read_text())
assert report["result"] == "RUNTIME_CHECKS_PASS" and not report["dirty"]
assert not subprocess.check_output(["git", "status", "--porcelain"])
nix = subprocess.check_output(["nix", "--version"], text=True).strip()
assert nix == "nix (Nix) 2.35.2", "Use the documented Nix 2.35.2 bootstrap"
sandbox = subprocess.check_output(["nix", "config", "show", "sandbox"], text=True).strip()
assert sandbox == "true", "Sandboxed builds are required"
inputs = ("src", "scripts/build-java.py", "deps/runtime.json", "flake.nix", "flake.lock")
trees = {}
for path in inputs:
    tested = subprocess.check_output(
        ["git", "rev-parse", report["source_commit"] + ":" + path], text=True
    ).strip()
    current = subprocess.check_output(["git", "rev-parse", "HEAD:" + path], text=True).strip()
    assert tested == current, "Changed package input requires affected validation: " + path
    trees[path] = current
jar = pathlib.Path("result/borrowedquiet-1.0.0.jar")
with (output / "independent-rebuild-console.txt").open("w") as log:
    subprocess.run(
        ["nix", "build", "--no-update-lock-file", ".#default"], stdout=log, stderr=log, check=True
    )
    before = hashlib.sha256(jar.read_bytes()).hexdigest()
    subprocess.run(
        ["nix", "build", "--no-update-lock-file", "--rebuild", ".#default"],
        stdout=log,
        stderr=log,
        check=True,
    )
after = hashlib.sha256(jar.read_bytes()).hexdigest()
assert before == after == report["package_sha256"]
record = {
    "decision": "REPRODUCTION_PASS",
    "nix": nix,
    "sandbox": sandbox,
    "tested_clean_checkout_commit": report["source_commit"],
    "verification_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    "package_input_git_objects": trees,
    "lock_sha256": hashlib.sha256(pathlib.Path("flake.lock").read_bytes()).hexdigest(),
    "before_sha256": before,
    "independent_rebuild_sha256": after,
    "fresh_state": "The full runtime workflow began in a new --no-hardlinks Git clone with no project runtime state, verified 82 acquired files and 5057 asset objects, and independently rebuilt in fresh Nix sandbox build directories.",
    "supplemental_rebuild": "This command independently rebuilt the unchanged package inputs again using Nix --rebuild; Nix also compared the rebuilt output to the existing output.",
    "acceptance_sequence": "The initial clean validate invocation completed all runtime/performance checks, then correctly refused acceptance because the review dossier did not yet exist. Final review and the exact-package acceptance gate complete that readiness step separately; the initial refusal is preserved, not represented as an overall successful invocation.",
}
(output / "reproduction.json").write_text(json.dumps(record, indent=2) + "\n")
print("REPRODUCTION_PASS", after)
