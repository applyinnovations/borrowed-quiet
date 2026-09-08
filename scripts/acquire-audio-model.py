#!/usr/bin/env python3
"""Optional parallel acquisition of the exact flake-pinned review model; verify before store import."""

import concurrent.futures
import hashlib
import pathlib
import shutil
import urllib.request

name = "Qwen3-Omni-30B-A3B-Instruct-Q4_K_M.gguf"
url = (
    "https://huggingface.co/ggml-org/Qwen3-Omni-30B-A3B-Instruct-GGUF/resolve/6e35a28f4a19b18730f8949b0c579c6429649ab8/"
    + name
)
expected = "d9e2876556e7873e02c0359f832432ee2d67ab7dd0cee3efe0f77fd7a1f4dd85"
size = 18557053952
chunk = 64 * 1024 * 1024
directory = pathlib.Path(".runtime/audio-acquisition")
directory.mkdir(parents=True, exist_ok=True)


def acquire(index):
    first, last = index * chunk, min(size, (index + 1) * chunk) - 1
    path = directory / f"part-{index:04d}"
    # A resumed part is only a candidate: the complete immutable SHA-256 below is mandatory.
    if path.exists() and path.stat().st_size == last - first + 1:
        return path
    request = urllib.request.Request(url, headers={"Range": f"bytes={first}-{last}"})
    with urllib.request.urlopen(request, timeout=120) as response, path.open("wb") as output:
        assert response.status == 206
        assert response.headers["Content-Range"] == f"bytes {first}-{last}/{size}"
        shutil.copyfileobj(response, output, 1024 * 1024)
    assert path.stat().st_size == last - first + 1
    return path


paths = []
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    futures = {pool.submit(acquire, index): index for index in range((size + chunk - 1) // chunk)}
    for future in concurrent.futures.as_completed(futures):
        paths.append(future.result())
        if len(paths) % 8 == 0:
            print(
                f"Acquired {sum(path.stat().st_size for path in paths) / 1e9:.2f} / {size / 1e9:.2f} GB",
                flush=True,
            )
target = directory / name
digest = hashlib.sha256()
with target.open("wb") as output:
    for path in sorted(paths):
        with path.open("rb") as source:
            while data := source.read(1024 * 1024):
                digest.update(data)
                output.write(data)
assert target.stat().st_size == size and digest.hexdigest() == expected, "Model integrity failure"
print("VERIFIED", expected, target, flush=True)
