#!/usr/bin/env python3
"""Deterministic javac/ZIP packaging; called inside Nix with verified dependencies."""

import os
import pathlib
import subprocess
import sys
import tempfile
import zipfile

source, dependencies, output = map(pathlib.Path, sys.argv[1:])
temporary = tempfile.TemporaryDirectory(prefix=output.stem, dir=output.parent)
classes = pathlib.Path(temporary.name)
classpath = ":".join(str(p) for p in sorted(dependencies.rglob("*.jar")))
if os.environ.get("BQ_EXTRA_CLASSPATH"):
    classpath += ":" + os.environ["BQ_EXTRA_CLASSPATH"]
java = sorted(source.glob("java/**/*.java"))
result = subprocess.run(
    [
        "javac",
        "--release",
        "25",
        "-encoding",
        "UTF-8",
        "-Xlint:all",
        "-Werror",
        "-proc:none",
        "-cp",
        classpath,
        "-d",
        str(classes),
        *map(str, java),
    ],
    check=False,
)
if result.returncode:
    sys.exit(result.returncode)
with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for root in (classes, source / "resources"):
        for path in sorted(root.rglob("*")):
            if path.is_file():
                entry = zipfile.ZipInfo(str(path.relative_to(root)), (2026, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, path.read_bytes())
print(output)
temporary.cleanup()
