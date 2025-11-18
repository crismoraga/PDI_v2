#!/usr/bin/env python3
"""Generate a short demo MP4 by recording the screen for N seconds.

Note: Requires ffmpeg installed and available in PATH. On Windows,
ffmpeg should be built with gdigrab support (available in typical builds).

Usage:
    python tools/generate_demo_video.py --seconds 6
"""
import argparse
import platform
import shlex
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "ui" / "local_demo.mp4"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=int, default=6)
    args = parser.parse_args()

    sec = args.seconds
    if platform.system() == "Windows":
        # gdigrab captures primary monitor on Windows
        cmd = f"ffmpeg -y -f gdigrab -framerate 25 -t {sec} -i desktop -pix_fmt yuv420p {shlex.quote(str(OUT))}"
    else:
        # On Linux/Mac users can adapt; fallback: create MP4 from demo GIF
        cmd = f"ffmpeg -y -i assets/ui/demo_gif.gif -movflags faststart -pix_fmt yuv420p {shlex.quote(str(OUT))}"

    print("Running:", cmd)
    p = subprocess.run(cmd, shell=True)
    if p.returncode == 0:
        print("Generated demo video:", OUT)
    else:
        print("Failed to create demo video. Ensure ffmpeg is installed and try again.")


if __name__ == '__main__':
    main()
