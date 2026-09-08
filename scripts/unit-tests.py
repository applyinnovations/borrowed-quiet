#!/usr/bin/env python3
"""Run pure director/config tests without launching Minecraft or contacting a network."""

import pathlib
import subprocess
import sys

dependencies, mod, tests = map(pathlib.Path, sys.argv[1:])
classpath = ":".join(map(str, [mod, tests, *sorted(dependencies.rglob("*.jar"))]))
subprocess.run(["java", "-ea", "-cp", classpath, "quiet.test.CoreTests"], check=True)
