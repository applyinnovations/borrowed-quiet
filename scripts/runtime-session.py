#!/usr/bin/env python3
"""Run a bounded isolated graphical session, recording only its screen and audio sink."""

import json
import os
import pathlib
import signal
import subprocess
import sys
import tempfile
import threading
import time

if os.environ.get("BQ_PRIVATE_BUS") != "1":
    os.execvpe(
        "dbus-run-session",
        [
            "dbus-run-session",
            "--config-file=" + os.environ["BQ_DBUS_CONFIG"],
            "--",
            sys.executable,
            __file__,
            *sys.argv[1:],
        ],
        dict(os.environ, BQ_PRIVATE_BUS="1"),
    )

directory = pathlib.Path(sys.argv[1]).resolve()
directory.mkdir(parents=True, exist_ok=True)
seconds = int(sys.argv[2])
command = sys.argv[3:]
processes = []
sink_id = None
recorder = None
finished = threading.Event()
audio_state = tempfile.TemporaryDirectory(prefix="borrowedquiet-audio-")
env = dict(
    os.environ,
    LIBGL_ALWAYS_SOFTWARE="1",
    __GLX_VENDOR_LIBRARY_NAME="mesa",
    ALSOFT_DRIVERS="pulse",
)
try:
    read_fd, write_fd = os.pipe()
    with (directory / "display.log").open("w") as log:
        display = subprocess.Popen(
            [
                "Xvfb",
                "-displayfd",
                str(write_fd),
                "-screen",
                "0",
                "960x540x24",
                "-nolisten",
                "tcp",
            ],
            pass_fds=(write_fd,),
            stdout=log,
            stderr=log,
            env=env,
        )
    processes.append(display)
    os.close(write_fd)
    with os.fdopen(read_fd) as output:
        env["DISPLAY"] = ":" + output.readline().strip()
    sink = "quiet_test_" + str(os.getpid())
    env["PULSE_SERVER"] = "unix:" + audio_state.name + "/native"
    with (directory / "audio-server.log").open("w") as log:
        pulse = subprocess.Popen(
            [
                "pulseaudio",
                "-n",
                "--daemonize=no",
                "--use-pid-file=no",
                "--exit-idle-time=-1",
                "--load=module-native-protocol-unix socket="
                + audio_state.name
                + "/native auth-anonymous=1",
                "--load=module-null-sink sink_name=" + sink + " rate=48000 channels=2",
                "--log-target=stderr",
            ],
            stdout=log,
            stderr=log,
            env=env,
        )
    processes.append(pulse)
    for _ in range(100):
        if pathlib.Path(audio_state.name, "native").exists():
            break
        if pulse.poll() is not None:
            raise RuntimeError("Private audio server failed; see audio-server.log")
        time.sleep(0.05)
    env["PULSE_SINK"] = sink
    (directory / "session-start.json").write_text(
        json.dumps(
            {
                "recording_start_unix": time.time(),
                "width": 960,
                "height": 540,
                "capture_fps": 15,
                "renderer": "Nix Mesa llvmpipe",
                "audio": "private PulseAudio stereo null sink",
            },
            indent=2,
        )
        + "\n"
    )
    with (directory / "capture.log").open("w") as log:
        recorder = subprocess.Popen(
            [
                "ffmpeg",
                "-y",
                "-v",
                "warning",
                "-f",
                "x11grab",
                "-video_size",
                "960x540",
                "-framerate",
                "15",
                "-i",
                env["DISPLAY"],
                "-f",
                "pulse",
                "-i",
                sink + ".monitor",
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-crf",
                "24",
                "-c:a",
                "flac",
                str(directory / "session.mkv"),
            ],
            stdin=subprocess.PIPE,
            stdout=log,
            stderr=log,
            env=env,
        )
    time.sleep(1)
    with (directory / "game.log").open("w") as log:
        game = subprocess.Popen(command, env=env, stdout=log, stderr=log)
        processes.append(game)

        def route_audio():
            routed = set()
            while not finished.wait(0.25):
                query = subprocess.run(
                    ["pactl", "-f", "json", "list", "sink-inputs"],
                    capture_output=True,
                    text=True,
                    check=False,
                    env=env,
                )
                if query.returncode:
                    continue
                for stream in json.loads(query.stdout):
                    if str(stream.get("properties", {}).get("application.process.id")) == str(
                        game.pid
                    ):
                        identity = stream["index"]
                        if identity not in routed:
                            moved = subprocess.run(
                                ["pactl", "move-sink-input", str(identity), sink],
                                capture_output=True,
                                check=False,
                                env=env,
                            )
                            if moved.returncode:
                                continue  # OpenAL may replace its startup stream between queries.
                            volume = subprocess.run(
                                [
                                    "pactl",
                                    "set-sink-input-volume",
                                    str(identity),
                                    "100%",
                                ],
                                capture_output=True,
                                check=False,
                                env=env,
                            )
                            if volume.returncode:
                                continue
                            routed.add(identity)
                            with (directory / "audio-routing.log").open("a") as routing:
                                routing.write(
                                    json.dumps(
                                        {
                                            "process": game.pid,
                                            "stream": identity,
                                            "prior_volume": stream.get("volume"),
                                            "set_volume_percent": 100,
                                        }
                                    )
                                    + "\n"
                                )

        router = threading.Thread(target=route_audio, daemon=True)
        router.start()
        result = game.wait(timeout=seconds)
        finished.set()
        router.join(timeout=5)
    if result:
        raise SystemExit(result)
finally:
    finished.set()
    if recorder is not None and recorder.poll() is None:
        recorder.communicate(b"q", timeout=20)
    for process in reversed(processes):
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    if sink_id is not None:
        subprocess.run(["pactl", "unload-module", sink_id], check=True)
    audio_state.cleanup()
