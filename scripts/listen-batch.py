#!/usr/bin/env python3
"""Complete audio-input reviews through a temporary loopback-only pinned model server."""

import argparse
import base64
import hashlib
import json
import pathlib
import secrets
import socket
import subprocess
import time
import urllib.error
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("output", type=pathlib.Path)
parser.add_argument("audio", type=pathlib.Path, nargs="+")
parser.add_argument("--allow-silent-controls", action="store_true")
parser.add_argument(
    "--compact",
    action="store_true",
    help="Request a bounded complete paragraph for follow-up review",
)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=False)
devices = subprocess.check_output(["llama-server", "--list-devices"], text=True)
if "CUDA0" not in devices:
    raise RuntimeError("CUDA0 is required for audio review; no silent CPU fallback")
(args.output / "devices.txt").write_text(devices)
engine_version = subprocess.check_output(
    ["llama-server", "--version"], text=True, stderr=subprocess.STDOUT
)
(args.output / "engine-version.txt").write_text(engine_version)


def package(name):
    return subprocess.check_output(
        ["nix", "build", "--no-update-lock-file", "--no-link", "--print-out-paths", ".#" + name],
        text=True,
    ).strip()


model = package("audio-review-model-v3")
projector = package("audio-review-projector-v3")
with socket.socket() as selection:
    selection.bind(("127.0.0.1", 0))
    port = selection.getsockname()[1]
token = secrets.token_hex(24)
address = f"http://127.0.0.1:{port}"
prompt = (
    "Listen to the entire clip from beginning to end. Describe its audible sequence, texture, "
    "attack and decay, pauses or repetitions, and any distortion or intelligible speech. "
    "Distinguish what you hear from uncertain guesses about its source."
)
if args.compact:
    prompt += " Use one compact paragraph of at most 120 words, no headings, covering the whole sequence and any artefacts."
with (args.output / "server.log").open("w") as log:
    server = subprocess.Popen(
        [
            "llama-server",
            "-m",
            model,
            "--mmproj",
            projector,
            "--jinja",
            "--device",
            "CUDA0",
            "-ngl",
            "auto",
            "--fit",
            "on",
            "--fit-target",
            "6144",
            "--mmproj-offload",
            "--verbosity",
            "4",
            "-t",
            "8",
            "-c",
            "8192",
            "-np",
            "1",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--api-key",
            token,
        ],
        stdout=log,
        stderr=log,
    )
    try:
        deadline = time.monotonic() + 600
        while True:
            if server.poll() is not None:
                raise RuntimeError("Audio model server stopped; inspect server.log")
            try:
                with urllib.request.urlopen(address + "/health", timeout=2) as response:
                    if response.status == 200:
                        break
            except OSError, urllib.error.HTTPError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("Audio model startup") from None
                time.sleep(1)
        for index, path in enumerate(args.audio):
            measurement = subprocess.run(
                ["python3", "scripts/audio-measure.py", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if measurement.returncode:
                try:
                    measured = json.loads(measurement.stdout)
                except json.JSONDecodeError:
                    measured = {}
                if args.allow_silent_controls and measured.get("peak_sample", 3) <= 2:
                    (args.output / f"{index:02d}-silence-control.json").write_text(
                        json.dumps(
                            {
                                "file": str(path),
                                "measurement": measured,
                                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                "interpretation": "Measured digital silence control; no model inference or audible-content claim.",
                            },
                            indent=2,
                        )
                        + "\n"
                    )
                    print("SILENCE_CONTROL", path, flush=True)
                    continue
                raise ValueError(
                    "Silent/invalid input requires a separate control record: " + str(path)
                )
            data = path.read_bytes()
            payload = {
                "model": "local-audio-review",
                "temperature": 0,
                "seed": 1,
                "max_tokens": 512 if args.compact else 256,
                "cache_prompt": False,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_audio",
                                "input_audio": {
                                    "data": base64.b64encode(data).decode(),
                                    "format": "wav",
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            }
            request = urllib.request.Request(
                address + "/v1/chat/completions",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json", "Authorization": "Bearer " + token},
            )
            with urllib.request.urlopen(request, timeout=300) as response:
                result = json.load(response)
            record = {
                "file": str(path),
                "sha256": hashlib.sha256(data).hexdigest(),
                "prompt": prompt,
                "model": model,
                "projector": projector,
                "engine_version": engine_version,
                "backend": "CUDA0; automatic weight offload with 6144 MiB headroom; GPU multimodal projector; CPU expert overflow permitted",
                "measurement": json.loads(measurement.stdout),
                "response": result,
                "interpretation": "Fallible local AI audio-input observation, not human listening testimony or automatic acceptance.",
            }
            (args.output / f"{index:02d}-review.json").write_text(
                json.dumps(record, indent=2) + "\n"
            )
            print(path, result["choices"][0]["message"], flush=True)
    finally:
        server.terminate()
        try:
            server.wait(timeout=15)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
