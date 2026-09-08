#!/usr/bin/env python3
"""Bind the autonomous inspection dossier to the exact release; missing evidence fails closed."""

import hashlib
import json
import pathlib
import sys

jar = pathlib.Path(sys.argv[1])
path = pathlib.Path("evidence/acceptance.json")
if not path.exists():
    sys.exit("NOT ACCEPTED: autonomous acceptance dossier is absent")
dossier = json.loads(path.read_text())
assert dossier["package_sha256"] == hashlib.sha256(jar.read_bytes()).hexdigest(), (
    "Dossier/package mismatch"
)
assert dossier["decision"] == "ACCEPTED", "Autonomous acceptance incomplete"
for requirement in dossier["requirements"]:
    assert requirement["passed"] and requirement["evidence"], requirement["id"]
    for evidence in requirement["evidence"]:
        assert pathlib.Path(evidence).exists(), "Missing evidence: " + evidence
print("PASS: acceptance dossier bound to exact package")
