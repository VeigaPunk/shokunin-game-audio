#!/usr/bin/env python3
"""Reproducibly synthesize five original, mono PCM16 audio fixtures."""
import argparse
import math
from pathlib import Path
import wave

import numpy as np

RATE = 48000
OUT = Path(__file__).resolve().parents[1] / "artifacts"


def save(name, samples, directory=OUT):
    directory.mkdir(parents=True, exist_ok=True)
    pcm = np.round(np.clip(samples, -1, 1) * 32767).astype("<i2")
    with wave.open(str(directory / f"{name}.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(pcm.tobytes())


def time(seconds):
    return np.arange(round(seconds * RATE)) / RATE


def build_invalid_probes():
    import struct

    out = OUT.parent / "live" / "round-6"
    out.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out / "short_sections.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        frames = (int(.2 * 32767 * math.sin(2*math.pi*180*i/RATE)) for i in range(3*RATE))
        wav.writeframes(b"".join(struct.pack("<h", sample) for sample in frames))
    (out / "corrupt.wav").write_bytes(bytes.fromhex("524946460000000057415645666d7420"))
    with wave.open(str(out / "wrong_format.wav"), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        frames = bytearray()
        for i in range(44100 * 4):
            t = i / 44100
            frames.extend(struct.pack("<hh", round(.30 * math.sin(2*math.pi*440*t)*32767),
                                      round(.25 * math.sin(2*math.pi*660*t)*32767)))
        wav.writeframes(frames)
    odd = OUT.parent / "live" / "round-7"
    odd.mkdir(parents=True, exist_ok=True)
    with wave.open(str(odd / "odd_sections.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(b"".join(struct.pack("<h", round(.2 * 32767 * math.sin(2*math.pi*180*i/RATE)))
                                 for i in range(101)))


def main(broken=False, slope_probe=False, flat_probe=False):
    if slope_probe:
        t_probe = time(1)
        probe = .30 * np.sin(2*np.pi*220*t_probe)
        probe[0], probe[1], probe[-2], probe[-1] = 0., .45, .02, 0.
        save("slope_probe", probe, OUT.parent / "live" / "round-3")
    rng = np.random.default_rng(20261012)
    t = time(.12)
    save("ui", .38 * np.sin(2 * np.pi * (700*t + 800*t*t)) * np.exp(-30*t))
    t = time(.16)
    save("ui_alt", .32 * np.sin(2 * np.pi * (1200*t + 1200*t*t)) * np.exp(-18*t))
    t = time(.32)
    noise = rng.standard_normal(len(t))
    save("impact", .40 * np.sin(2*np.pi*90*t) * np.exp(-16*t)
         + .23 * noise * np.exp(-65*t))
    save("impact_alt", .55*np.sin(2*np.pi*95*t)*np.exp(-14*t)
         + .25*np.sin(2*np.pi*340*t)*np.exp(-35*t)
         + .12*np.sin(2*np.pi*900*t)*np.exp(-50*t))
    t = time(.24)
    noise = rng.standard_normal(len(t))
    # A short broadband step, with a rounded onset and decay.
    save("movement", .24 * noise * (1-np.exp(-250*t)) * np.exp(-22*t))
    t = time(.36)
    noise_alt = np.random.default_rng(20261013).standard_normal(len(t))
    save("movement_alt", .30 * noise_alt * (1-np.exp(-180*t)) * np.exp(-15*t))
    t = time(2)
    ambience = .15*np.sin(2*np.pi*12*t) + .09*np.sin(2*np.pi*36*t)
    if broken:
        ambience[-round(.02*RATE):] += .5
    save("ambience", ambience)
    save("ambience_alt", .15*np.sin(2*np.pi*20*t) + .09*np.sin(2*np.pi*60*t)
         + .06*np.sin(2*np.pi*100*t))
    t = time(2)
    save("stem", .23*np.sin(2*np.pi*220*t) + .11*np.sin(2*np.pi*330*t))
    t = time(4)
    common = .08*np.sin(2*np.pi*220*t) + .04*np.sin(2*np.pi*330*t)
    save("stem_sections", common + np.where(t < 2, .012, .060)*np.sin(2*np.pi*30*t))
    if flat_probe:
        save("flat30_probe", common + .036*np.sin(2*np.pi*30*t),
             OUT.parent / "live" / "round-4")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-failing", action="store_true")
    parser.add_argument("--probe-slope", action="store_true")
    parser.add_argument("--probe-flat", action="store_true")
    parser.add_argument("--probe-invalid", action="store_true")
    args = parser.parse_args()
    if args.probe_invalid:
        build_invalid_probes()
    else:
        main(args.probe_failing, args.probe_slope, args.probe_flat)
