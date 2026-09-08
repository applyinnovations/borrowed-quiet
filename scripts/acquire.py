#!/usr/bin/env python3
"""Acquire and verify immutable Minecraft/Fabric inputs; never distribute game jars."""

import concurrent.futures
import hashlib
import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / ".runtime"


def get(url):
    with urllib.request.urlopen(url, timeout=90) as response:
        return response.read()


def acquire(item):
    target = CACHE / item["path"]
    algorithm = "sha256" if "sha256" in item else "sha1"
    expected = item.get(algorithm)
    if target.exists():
        data = target.read_bytes()
        if hashlib.new(algorithm, data).hexdigest() == expected:
            return {
                **item,
                "sha256": hashlib.sha256(data).hexdigest(),
                "size": len(data),
            }
    data = get(item["url"])
    if expected and hashlib.new(algorithm, data).hexdigest() != expected:
        raise ValueError("Hash mismatch: " + item["url"])
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".part")
    temporary.write_bytes(data)
    temporary.replace(target)
    return {**item, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}


def allowed(library):
    result = "rules" not in library
    for rule in library.get("rules", []):
        os_rule = rule.get("os", {})
        if os_rule.get("name", "linux") == "linux" and os_rule.get("arch", "x86_64") in (
            "x86_64",
            "amd64",
        ):
            result = rule["action"] == "allow"
    return result


def make_lock():
    version = json.loads(
        get(
            "https://piston-meta.mojang.com/v1/packages/3592ebc61c6b6c33bb8228fe5a9e90221df0be68/26.2.json"
        )
    )
    profile = json.loads(
        get("https://meta.fabricmc.net/v2/versions/loader/26.2/0.19.3/profile/json")
    )
    entries = [{"path": "libraries/minecraft-26.2.jar", **version["downloads"]["client"]}]
    for lib in version["libraries"]:
        if allowed(lib) and "artifact" in lib.get("downloads", {}):
            artifact = lib["downloads"]["artifact"]
            entries.append({**artifact, "path": "libraries/" + artifact["path"]})
    for lib in profile["libraries"]:
        group, name, number = lib["name"].split(":")
        path = f"{group.replace('.', '/')}/{name}/{number}/{name}-{number}.jar"
        entries.append(
            {
                "path": "libraries/" + path,
                "url": lib["url"] + path,
                **{k: lib[k] for k in ("sha256", "sha1") if k in lib},
            }
        )
    api = "0.152.0+26.2"
    entries.append(
        {
            "path": "mods/fabric-api.jar",
            "url": f"https://maven.fabricmc.net/net/fabricmc/fabric-api/fabric-api/{api}/fabric-api-{api}.jar",
        }
    )
    entries.append(
        {
            "path": "compilelibs/annotations.jar",
            "url": "https://repo.maven.apache.org/maven2/org/jetbrains/annotations/26.0.2/annotations-26.0.2.jar",
        }
    )
    for name, number in [
        ("fabric-client-gametest-api-v1", "5.1.0+db57954833"),
        ("fabric-gametest-api-v1", "4.0.21+4a7fa08133"),
    ]:
        entries.append(
            {
                "path": "testlibs/" + name + ".jar",
                "url": f"https://maven.fabricmc.net/net/fabricmc/fabric-api/{name}/{number}/{name}-{number}.jar",
            }
        )
    entries.append(
        {
            "path": "compilelibs/error-prone-annotations.jar",
            "url": "https://repo.maven.apache.org/maven2/com/google/errorprone/error_prone_annotations/2.38.0/error_prone_annotations-2.38.0.jar",
        }
    )
    entries.append({**version["assetIndex"], "path": "assets/indexes/32.json"})
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        locked = list(pool.map(acquire, entries))
    document = {
        "minecraft": "26.2",
        "java": 25,
        "loader": "0.19.3",
        "fabric_api": api,
        "asset_index": "32",
        "main_class": profile["mainClass"],
        "files": locked,
    }
    (ROOT / "deps").mkdir(exist_ok=True)
    (ROOT / "deps/runtime.json").write_text(json.dumps(document, indent=2) + "\n")
    print(f"Locked {len(locked)} files.")


def prepare():
    lock = json.loads((ROOT / "deps/runtime.json").read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        list(pool.map(acquire, lock["files"]))
        index = json.loads((CACHE / "assets/indexes/32.json").read_text())
        objects = [
            {
                "path": f"assets/objects/{v['hash'][:2]}/{v['hash']}",
                "url": f"https://resources.download.minecraft.net/{v['hash'][:2]}/{v['hash']}",
                "sha1": v["hash"],
            }
            for v in index["objects"].values()
        ]
        list(pool.map(acquire, objects))
    print(f"Verified {len(lock['files'])} files and {len(objects)} asset objects.")


if __name__ == "__main__":
    if sys.argv[1:] == ["--lock"]:
        make_lock()
    elif sys.argv[1:] == ["--prepare"]:
        prepare()
    else:
        raise SystemExit(
            "Use --lock for explicit acquisition, --prepare for verified runtime inputs."
        )
