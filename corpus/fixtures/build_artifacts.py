#!/usr/bin/env python3
"""Reproducibly synthesize five original, mono PCM16 audio fixtures."""
import argparse
import math
from pathlib import Path
import wave

import numpy as np

RATE = 48000
OUT = Path(__file__).resolve().parents[1] / "artifacts"


def save(name, samples):
    OUT.mkdir(parents=True, exist_ok=True)
    pcm = np.round(np.clip(samples, -1, 1) * 32767).astype("<i2")
    with wave.open(str(OUT / f"{name}.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(pcm.tobytes())


def time(seconds):
    return np.arange(round(seconds * RATE)) / RATE


def main(broken=False):
    rng = np.random.default_rng(20261012)
    t = time(.12)
    save("ui", .38 * np.sin(2 * np.pi * (700*t + 800*t*t)) * np.exp(-30*t))
    t = time(.32)
    noise = rng.standard_normal(len(t))
    save("impact", .40 * np.sin(2*np.pi*90*t) * np.exp(-16*t)
         + .23 * noise * np.exp(-65*t))
    t = time(.24)
    noise = rng.standard_normal(len(t))
    # A short broadband step, with a rounded onset and decay.
    save("movement", .24 * noise * (1-np.exp(-250*t)) * np.exp(-22*t))
    t = time(2)
    ambience = .15*np.sin(2*np.pi*12*t) + .09*np.sin(2*np.pi*36*t)
    if broken:
        ambience[-round(.02*RATE):] += .5
    save("ambience", ambience)
    t = time(2)
    save("stem", .23*np.sin(2*np.pi*220*t) + .11*np.sin(2*np.pi*330*t))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-failing", action="store_true")
    args = parser.parse_args()
    main(args.probe_failing)
