#!/usr/bin/env python3
"""Package the accepted jar and complete source/evidence without game dependencies."""

import hashlib
import json
import pathlib
import shutil
import subprocess
import zipfile

root = pathlib.Path(__file__).resolve().parent.parent
jar = root / "result/borrowedquiet-1.0.0.jar"
assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=root)
subprocess.run(["python3", "scripts/acceptance-gate.py", str(jar)], cwd=root, check=True)
output = root / "dist"
output.mkdir(exist_ok=False)
shutil.copyfile(jar, output / jar.name)
tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
files = {root / name for name in tracked if name}
for directory in (root / "evidence/runtime", root / "evidence/reviews"):
    files.update(file for file in directory.rglob("*") if file.is_file())
archive_path = output / "borrowedquiet-1.0.0-complete-project.zip"
with zipfile.ZipFile(
    archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
) as archive:
    for file in sorted(files):
        relative = file.relative_to(root)
        assert not any(
            part in {".git", "saves", "mods", "libraries", "objects"} for part in relative.parts
        )
        assert file.suffix not in {".gguf", ".jar"}, relative
        info = zipfile.ZipInfo("borrowedquiet/" + str(relative), (2026, 1, 1, 0, 0, 0))
        info.external_attr = (0o100755 if file.stat().st_mode & 0o111 else 0o100644) << 16
        info.compress_type = (
            zipfile.ZIP_STORED if file.suffix in {".mkv", ".ogg", ".png"} else zipfile.ZIP_DEFLATED
        )
        with file.open("rb") as source, archive.open(info, "w", force_zip64=True) as target:
            shutil.copyfileobj(source, target)
checksums = []
for file in (output / jar.name, archive_path):
    with file.open("rb") as stream:
        checksums.append(hashlib.file_digest(stream, "sha256").hexdigest() + "  " + file.name)
(output / "SHA256SUMS").write_text("\n".join(checksums) + "\n")
(output / "release.json").write_text(
    json.dumps(
        {
            "archive_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True
            ).strip(),
            "tested_source_commit": json.loads((root / "evidence/acceptance.json").read_text())[
                "source_commit"
            ],
            "files": checksums,
        },
        indent=2,
    )
    + "\n"
)
with zipfile.ZipFile(archive_path) as archive:
    assert archive.testzip() is None, "Archive integrity"
print("PACKAGED", output)
