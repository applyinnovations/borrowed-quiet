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
required = {f"A{number}" for number in range(1, 13)} | {f"F{number}" for number in range(1, 5)}
assert {entry["id"] for entry in dossier["requirements"]} == required, (
    "Incomplete requirement matrix"
)
assert (
    dossier["lock_sha256"] == hashlib.sha256(pathlib.Path("flake.lock").read_bytes()).hexdigest()
), "Lock mismatch"
assert dossier["package_sha256"] == hashlib.sha256(jar.read_bytes()).hexdigest(), (
    "Dossier/package mismatch"
)
assert dossier["decision"] == "ACCEPTED", "Autonomous acceptance incomplete"
for requirement in dossier["requirements"]:
    assert requirement["passed"] and requirement["evidence"], requirement["id"]
    for evidence in requirement["evidence"]:
        file = pathlib.Path(evidence["path"])
        assert file.is_file(), "Missing evidence: " + str(file)
        with file.open("rb") as stream:
            assert hashlib.file_digest(stream, "sha256").hexdigest() == evidence["sha256"], file
for register in ("assets/register.json", "assets/visual-register.json"):
    for asset in json.loads(pathlib.Path(register).read_text()):
        assert asset["decision"] == "ACCEPTED" and asset["inspection"], asset["id"]
        assert (
            hashlib.sha256(pathlib.Path(asset["file"]).read_bytes()).hexdigest() == asset["sha256"]
        ), asset["id"]
print("PASS: acceptance dossier bound to exact package")
