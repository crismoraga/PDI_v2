"""Generate simple sounds for app events (capture, achievement).

This script synthesizes tiny WAV files (sine beeps) and saves them under assets/ui.
"""
from pathlib import Path
import math
import wave
import struct

OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "ui"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100


def synth_sine(filename: Path, freq: float, length_seconds: float = 0.25, volume: float = 0.3):
    n_samples = int(SAMPLE_RATE * length_seconds)
    with wave.open(str(filename), 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        for i in range(n_samples):
            sample = volume * math.sin(2 * math.pi * freq * (i / SAMPLE_RATE))
            # 16-bit signed
            w.writeframes(struct.pack('<h', int(sample * 32767)))


if __name__ == '__main__':
    synth_sine(OUT_DIR / 'capture.wav', 880.0, length_seconds=0.08)
    synth_sine(OUT_DIR / 'achievement.wav', 660.0, length_seconds=0.4)
    print('Generated sound assets in', OUT_DIR)
