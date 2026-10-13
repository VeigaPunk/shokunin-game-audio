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


def build_width_probes():
    out = OUT.parent / "live" / "round-22"
    out.mkdir(parents=True, exist_ok=True)
    samples = .2 * np.sin(2 * np.pi * 440 * time(4))
    save("native16_probe", samples, out)
    pcm24 = np.round(np.clip(samples, -1, 1) * 8388607).astype(np.int32)
    packed = np.stack((pcm24 & 255, (pcm24 >> 8) & 255, (pcm24 >> 16) & 255), axis=1).astype(np.uint8)
    with wave.open(str(out / "native24_probe.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(3)
        wav.setframerate(RATE)
        wav.writeframes(packed.tobytes())


def build_rate_channel_probes():
    out = OUT.parent / "live" / "round-25"
    out.mkdir(parents=True, exist_ok=True)
    for name, rate, channels in (("stereo48_probe", 48000, 2), ("mono441_probe", 44100, 1)):
        t = np.arange(4 * rate) / rate
        pcm = np.round(.2 * np.sin(2 * np.pi * 440 * t) * 32767).astype("<i2")
        if channels == 2:
            pcm = np.repeat(pcm[:, None], 2, axis=1)
        with wave.open(str(out / (name + ".wav")), "wb") as wav:
            wav.setnchannels(channels)
            wav.setsampwidth(2)
            wav.setframerate(rate)
            wav.writeframes(pcm.tobytes())


def build_ui_clone_probe():
    out = OUT.parent / "live" / "round-26"
    t = time(.12)
    samples = .30 * np.sin(2 * np.pi * 700 * t) * np.exp(-20 * t)
    for name in ("ui_clone", "ui_clone_alt"):
        save(name, samples, out)


def build_ui_duration_probe(frames, label):
    out = OUT.parent / "live" / "round-27"
    for name, count in ((f"ui_duration_{label}", 5760), (f"ui_duration_{label}_alt", frames)):
        t = np.arange(count) / RATE
        save(name, .38 * np.sin(2 * np.pi * (700*t + 800*t*t)) * np.exp(-30*t), out)


def build_ui_centroid_probe(multiplier, label):
    out = OUT.parent / "live" / "round-28"
    t = time(.12)
    for name, k in ((f"ui_centroid_{label}", 1.0),
                    (f"ui_centroid_{label}_alt", multiplier)):
        save(name, .38 * np.sin(2 * np.pi * (700*k*t + 800*k*t*t)) * np.exp(-30*t), out)


def build_ui_lower_centroid_probe(multiplier, label):
    out = OUT.parent / "live" / "round-29"
    t = time(.12)
    for name, k in ((f"ui_lower_centroid_{label}", 1.0),
                    (f"ui_lower_centroid_{label}_alt", multiplier)):
        save(name, .38 * np.sin(2 * np.pi * k * (700*t + 800*t*t)) * np.exp(-30*t), out)


def build_ui_orientation_probe(reverse):
    out = OUT.parent / "live" / "round-30"
    label = "reverse" if reverse else "forward"
    t = time(.12)
    for name, k in ((f"ui_orientation_{label}", .95 if reverse else 1.0),
                    (f"ui_orientation_{label}_alt", 1.0 if reverse else .95)):
        save(name, .38 * np.sin(2 * np.pi * k * (700*t + 800*t*t)) * np.exp(-30*t), out)


def build_ui_joint_below_probe():
    out = OUT.parent / "live" / "round-31"
    for name, count, k in (("ui_joint_below", 5760, 1.0),
                           ("ui_joint_below_alt", 6719, .88)):
        t = np.arange(count) / RATE
        save(name, .38 * np.sin(2 * np.pi * k * (700*t + 800*t*t)) * np.exp(-30*t), out)


def build_ui_mixed_pass_probe():
    out = OUT.parent / "live" / "round-32"
    for name, count, k in (("ui_mixed_pass", 5760, 1.0),
                           ("ui_mixed_pass_alt", 6719, 1.14)):
        t = np.arange(count) / RATE
        save(name, .38 * np.sin(2 * np.pi * k * (700*t + 800*t*t)) * np.exp(-30*t), out)


def build_ui_rate_probe():
    out = OUT.parent / "live" / "round-48"
    out.mkdir(parents=True, exist_ok=True)
    n = np.arange(5760)
    t = n / RATE
    samples = .28 * np.sin(2*np.pi*1000*t) * np.hanning(len(n))
    pcm = np.rint(np.clip(samples, -1, 1) * 32767).astype("<i2")
    for rate in (47999, 48000):
        with wave.open(str(out / f"ui-{rate}.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(rate)
            wav.writeframes(pcm.tobytes())


def build_ui_upper_centroid_probe():
    out = OUT.parent / "live" / "round-47"
    out.mkdir(parents=True, exist_ok=True)
    n = np.arange(5760)
    t = n / RATE
    for label, frequency in (("below", 3983), ("above", 3984)):
        samples = .28 * np.sin(2*np.pi*frequency*t) * np.hanning(len(n))
        save(f"upper-{label}", samples, out)


def build_ui_absolute_centroid_probe():
    out = OUT.parent / "live" / "round-46"
    out.mkdir(parents=True, exist_ok=True)
    n = np.arange(5760)
    t = n / RATE
    for label, frequency in (("below", 225), ("above", 226)):
        samples = .28 * np.sin(2*np.pi*frequency*t) * np.hanning(len(n))
        save(f"centroid-{label}", samples, out)


def build_ui_lower_tolerance_probe():
    out = OUT.parent / "live" / "round-45"
    out.mkdir(parents=True, exist_ok=True)
    for frames in (5713, 5711):
        t = np.arange(frames) / RATE
        samples = .28 * np.sin(2*np.pi*(700*t + 700*t*t)) * np.exp(-5*t)
        save(f"duration-{frames}", samples, out)


def build_ui_tolerance_probe():
    out = OUT.parent / "live" / "round-44"
    out.mkdir(parents=True, exist_ok=True)
    for frames in (5807, 5809):
        t = np.arange(frames) / RATE
        samples = .28 * np.sin(2*np.pi*(700*t + 700*t*t)) * np.exp(-5*t)
        save(f"duration-{frames}", samples, out)


def build_ui_crest_probe():
    out = OUT.parent / "live" / "round-43"
    n = np.arange(5760)
    out.mkdir(parents=True, exist_ok=True)
    for counts in (46, 47):
        pcm = np.rint(counts * np.cos(2*np.pi*1000*n/RATE)).astype("<i2")
        with wave.open(str(out / f"crest-{counts}.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(pcm.tobytes())


def build_ui_peak_probe():
    out = OUT.parent / "live" / "round-42"
    n = np.arange(5760)
    out.mkdir(parents=True, exist_ok=True)
    for counts in (31129, 31130):
        pcm = np.rint(counts * np.cos(2*np.pi*1000*n/RATE)).astype("<i2")
        with wave.open(str(out / f"ui-peak-{counts}.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(pcm.tobytes())


def build_outer_slope_probe():
    out = OUT.parent / "live" / "round-41"
    n = np.arange(96000)
    pcm = np.rint(.15 * np.sin(2*np.pi*120*n/96000) * 32768).astype("<i2")
    out.mkdir(parents=True, exist_ok=True)
    for counts in (32, 33):
        probe = pcm.copy()
        probe[1] = 38 - counts
        with wave.open(str(out / f"slope-{counts}.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(probe.tobytes())


def build_outer_endpoint_probe():
    out = OUT.parent / "live" / "round-40"
    n = np.arange(96000)
    t = n / RATE
    base = .7 + .04*np.cos(2*np.pi*30*t)
    for counts in (983, 984):
        correction = counts/32768 - (base[-1] - base[0])
        pcm = np.rint((base + np.linspace(0, correction, len(n))) * 32768).astype("<i2")
        out.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out / f"endpoint_{counts}.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(pcm.tobytes())


def build_ambience_orientation_probe():
    out = OUT.parent / "live" / "round-39"
    t = time(2.0)
    for name, frequency in (("orientation_low", 108), ("orientation_high", 114)):
        save(name, .22*np.sin(2*np.pi*frequency*t), out)


def build_ambience_centroid_above_probe():
    out = OUT.parent / "live" / "round-38"
    t = time(2.0)
    for name, frequency in (("ambience_above", 65), ("ambience_above_alt", 75)):
        save(name, .22*np.sin(2*np.pi*frequency*t), out)


def build_ambience_centroid_below_probe():
    out = OUT.parent / "live" / "round-37"
    t = time(2.0)
    for name, frequency in (("ambience_probe", 60), ("ambience_probe_alt", 64)):
        save(name, .22*np.sin(2*np.pi*frequency*t), out)


def main(broken=False, slope_probe=False, flat_probe=False, layer_flat_probe=False, join_probe=False, layer_slope_probe=False, layer_alt_flat_probe=False, layer_alt_join_probe=False, layer_alt_slope_probe=False, layer_alt_reverse_probe=False, layer_third_slope_probe=False, layer_third_slope_edge_pass=False, layer_third_slope_edge_fail=False, layer_third_join_probe=False, layer_third_join_edge_pass=False, layer_third_join_edge_fail=False):
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
    t = time(.20)
    save("ui_third", .38 * np.sin(2 * np.pi * (700*t + 800*t*t)) * np.exp(-30*t))
    t = time(.32)
    noise = rng.standard_normal(len(t))
    save("impact", .40 * np.sin(2*np.pi*90*t) * np.exp(-16*t)
         + .23 * noise * np.exp(-65*t))
    save("impact_alt", .55*np.sin(2*np.pi*95*t)*np.exp(-14*t)
         + .25*np.sin(2*np.pi*340*t)*np.exp(-35*t)
         + .12*np.sin(2*np.pi*900*t)*np.exp(-50*t))
    t = time(.40)
    impact_noise = np.random.default_rng(3401).standard_normal(len(t))
    save("impact_third", .38*np.sin(2*np.pi*2200*t)*np.exp(-11*t)
         + .045*impact_noise*np.exp(-80*t))
    t = time(.24)
    noise = rng.standard_normal(len(t))
    # A short broadband step, with a rounded onset and decay.
    save("movement", .24 * noise * (1-np.exp(-250*t)) * np.exp(-22*t))
    t = time(.36)
    noise_alt = np.random.default_rng(20261013).standard_normal(len(t))
    save("movement_alt", .30 * noise_alt * (1-np.exp(-180*t)) * np.exp(-15*t))
    t = time(.30)
    movement_rng = np.random.default_rng(3501)
    movement_env = np.sin(np.pi*np.minimum(t/.012, 1)/2)**2 * np.exp(-t/.20)
    movement_third = .52*movement_env*np.sin(2*np.pi*1800*t)
    movement_attack = np.zeros(len(t))
    attack_count = round(.012*RATE)
    movement_attack[:attack_count] = movement_rng.normal(0, .07, attack_count) * np.exp(-np.arange(attack_count)/(RATE*.003))
    movement_third += movement_attack
    movement_third *= np.minimum(np.arange(len(t))/(RATE*.002), 1)
    save("movement_third", np.clip(movement_third, -.9, .9))
    t = time(2)
    ambience = .15*np.sin(2*np.pi*12*t) + .09*np.sin(2*np.pi*36*t)
    if broken:
        ambience[-round(.02*RATE):] += .5
    save("ambience", ambience)
    save("ambience_alt", .15*np.sin(2*np.pi*20*t) + .09*np.sin(2*np.pi*60*t)
         + .06*np.sin(2*np.pi*100*t))
    save("ambience_third", .20*np.sin(2*np.pi*90*t) + .025*np.sin(2*np.pi*130*t))
    t = time(2)
    save("stem", .23*np.sin(2*np.pi*220*t) + .11*np.sin(2*np.pi*330*t))
    t = time(4)
    common = .08*np.sin(2*np.pi*220*t) + .04*np.sin(2*np.pi*330*t)
    save("stem_sections", common + np.where(t < 2, .012, .060)*np.sin(2*np.pi*30*t))
    save("stem_layer", np.where(t < 2, .012, .060)*np.sin(2*np.pi*120*t))
    save("stem_layer_alt", np.where(t < 2, .015, .050)*np.sin(2*np.pi*180*t))
    save("stem_layer_third", np.where(t < 2, .015, .050)*np.sin(2*np.pi*200*t))
    if layer_third_slope_probe:
        with wave.open(str(OUT / "stem_layer_third.wav"), "rb") as wav:
            frames = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").copy()
        frames[96001] += 8
        out = OUT.parent / "live" / "round-18"
        out.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out / "slope200_probe.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(frames.tobytes())
    for enabled, offset, filename in ((layer_third_slope_edge_pass, 2, "edgepass_probe.wav"),
                                      (layer_third_slope_edge_fail, 3, "edgefail_probe.wav")):
        if enabled:
            with wave.open(str(OUT / "stem_layer_third.wav"), "rb") as wav:
                frames = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").copy()
            frames[96001] += offset
            out = OUT.parent / "live" / "round-19"
            out.mkdir(parents=True, exist_ok=True)
            with wave.open(str(out / filename), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(RATE)
                wav.writeframes(frames.tobytes())
    if layer_third_join_probe:
        # Canonical-copy two-sample step at 200 Hz throws the full-signal centroid
        # above the existing 2000 Hz band (measured 2195.8 Hz). Same pattern as the
        # 180 Hz join: keep the stepped 200 Hz layer and add the original 220/330 Hz
        # bed, then edit only the two join frames. Not a canonical rewrite.
        base = (np.where(t < 2, .015, .050)*np.sin(2*np.pi*200*t)
                + .08*np.sin(2*np.pi*220*t) + .04*np.sin(2*np.pi*330*t))
        frames = np.round(np.clip(base, -1, 1)*32767).astype("<i2")
        # s[95999] is -145; gap counts = target-(-145). .03*32768 = 983.04,
        # so target >= 839. 839 is the smallest integer that crosses .03 FS
        # while the preserved left step keeps side-slope at 0.
        frames[96000] = 839
        frames[96001] = frames[96000] + frames[95999] - frames[95998]
        out = OUT.parent / "live" / "round-20"
        out.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out / "join200_probe.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(frames.tobytes())
    for enabled, gap_counts, name in ((layer_third_join_edge_pass, 983, "join200_edgepass_probe"),
                                      (layer_third_join_edge_fail, 984, "join200_edgefail_probe")):
        if enabled:
            base = (np.where(t < 2, .015, .050)*np.sin(2*np.pi*200*t)
                    + .08*np.sin(2*np.pi*220*t) + .04*np.sin(2*np.pi*330*t))
            frames = np.round(np.clip(base, -1, 1)*32767).astype("<i2")
            frames[96000] = frames[95999] + gap_counts
            frames[96001] = frames[96000] + frames[95999] - frames[95998]
            out = OUT.parent / "live" / "round-21"
            out.mkdir(parents=True, exist_ok=True)
            with wave.open(str(out / (name + ".wav")), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(RATE)
                wav.writeframes(frames.tobytes())
    if layer_alt_reverse_probe:
        save("reverse180_probe", np.where(t < 2, .050, .015)*np.sin(2*np.pi*180*t),
             OUT.parent / "live" / "round-16")
    if layer_alt_slope_probe:
        with wave.open(str(OUT / "stem_layer_alt.wav"), "rb") as wav:
            frames = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").copy()
        frames[96001] += round(.0004*32767)
        out = OUT.parent / "live" / "round-15"
        out.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out / "slope180_probe.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(frames.tobytes())
    if layer_alt_join_probe:
        base = (np.where(t < 2, .015, .050)*np.sin(2*np.pi*180*t)
                + .08*np.sin(2*np.pi*220*t) + .04*np.sin(2*np.pi*330*t))
        frames = np.round(np.clip(base, -1, 1)*32767).astype("<i2")
        frames[96000] = round(.040*32767)
        frames[96001] = frames[96000] + frames[95999] - frames[95998]
        out = OUT.parent / "live" / "round-14"
        out.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out / "join180_probe.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(frames.tobytes())
    if join_probe:
        with wave.open(str(OUT / "stem_layer.wav"), "rb") as wav:
            source = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").astype(np.float64) / 32767
        frames = np.round(np.clip(source + .03*np.sin(2*np.pi*60*t), -1, 1)*32767).astype("<i2")
        frames[96000] = round(.0305*32767)
        out = OUT.parent / "live" / "round-10"
        out.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out / "join_probe.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(frames.tobytes())
    if layer_slope_probe:
        with wave.open(str(OUT / "stem_layer.wav"), "rb") as wav:
            samples = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").copy()
        samples[96001] = round(samples[96001] + .0004*32767)
        out = OUT.parent / "live" / "round-11"
        out.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out / "slope_probe.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(samples.tobytes())
    if layer_alt_flat_probe:
        save("flat180_probe", .036*np.sin(2*np.pi*180*t),
             OUT.parent / "live" / "round-13")
    if layer_flat_probe:
        save("flat120_probe", .036*np.sin(2*np.pi*120*t),
             OUT.parent / "live" / "round-8")
    if flat_probe:
        save("flat30_probe", common + .036*np.sin(2*np.pi*30*t),
             OUT.parent / "live" / "round-4")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-failing", action="store_true")
    parser.add_argument("--probe-slope", action="store_true")
    parser.add_argument("--probe-flat", action="store_true")
    parser.add_argument("--probe-layer-flat", action="store_true")
    parser.add_argument("--probe-layer-join", action="store_true")
    parser.add_argument("--probe-layer-slope", action="store_true")
    parser.add_argument("--probe-layer-alt-flat", action="store_true")
    parser.add_argument("--probe-layer-alt-join", action="store_true")
    parser.add_argument("--probe-layer-alt-slope", action="store_true")
    parser.add_argument("--probe-layer-alt-reverse", action="store_true")
    parser.add_argument("--probe-layer-third-slope", action="store_true")
    parser.add_argument("--probe-layer-third-slope-edge-pass", action="store_true")
    parser.add_argument("--probe-layer-third-slope-edge-fail", action="store_true")
    parser.add_argument("--probe-layer-third-join", action="store_true")
    parser.add_argument("--probe-layer-third-join-edge-pass", action="store_true")
    parser.add_argument("--probe-layer-third-join-edge-fail", action="store_true")
    parser.add_argument("--probe-invalid", action="store_true")
    parser.add_argument("--probe-ui-clone", action="store_true")
    parser.add_argument("--probe-ui-duration-below", action="store_true")
    parser.add_argument("--probe-ui-duration-at", action="store_true")
    parser.add_argument("--probe-ui-centroid-below", action="store_true")
    parser.add_argument("--probe-ui-centroid-above", action="store_true")
    parser.add_argument("--probe-ui-lower-centroid-below", action="store_true")
    parser.add_argument("--probe-ui-lower-centroid-above", action="store_true")
    parser.add_argument("--probe-ui-orientation-forward", action="store_true")
    parser.add_argument("--probe-ui-orientation-reverse", action="store_true")
    parser.add_argument("--probe-ui-joint-below", action="store_true")
    parser.add_argument("--probe-ui-mixed-pass", action="store_true")
    parser.add_argument("--probe-ambience-centroid-below", action="store_true")
    parser.add_argument("--probe-ambience-centroid-above", action="store_true")
    parser.add_argument("--probe-ambience-orientation-forward", action="store_true")
    parser.add_argument("--probe-ambience-orientation-reverse", action="store_true")
    parser.add_argument("--probe-outer-endpoint-983", action="store_true")
    parser.add_argument("--probe-outer-endpoint-984", action="store_true")
    parser.add_argument("--probe-outer-slope-32", action="store_true")
    parser.add_argument("--probe-outer-slope-33", action="store_true")
    parser.add_argument("--probe-ui-peak-31129", action="store_true")
    parser.add_argument("--probe-ui-peak-31130", action="store_true")
    parser.add_argument("--probe-ui-crest-46", action="store_true")
    parser.add_argument("--probe-ui-crest-47", action="store_true")
    parser.add_argument("--probe-ui-tolerance-5807", action="store_true")
    parser.add_argument("--probe-ui-tolerance-5809", action="store_true")
    parser.add_argument("--probe-ui-lower-tolerance-5713", action="store_true")
    parser.add_argument("--probe-ui-lower-tolerance-5711", action="store_true")
    parser.add_argument("--probe-ui-absolute-centroid-below", action="store_true")
    parser.add_argument("--probe-ui-absolute-centroid-above", action="store_true")
    parser.add_argument("--probe-ui-upper-centroid-below", action="store_true")
    parser.add_argument("--probe-ui-upper-centroid-above", action="store_true")
    parser.add_argument("--probe-ui-rate-47999", action="store_true")
    parser.add_argument("--probe-ui-rate-48000", action="store_true")
    args = parser.parse_args()
    if args.probe_ui_rate_47999 or args.probe_ui_rate_48000:
        main()
        build_ui_rate_probe()
    elif args.probe_ui_upper_centroid_below or args.probe_ui_upper_centroid_above:
        main()
        build_ui_upper_centroid_probe()
    elif args.probe_ui_absolute_centroid_below or args.probe_ui_absolute_centroid_above:
        main()
        build_ui_absolute_centroid_probe()
    elif args.probe_ui_lower_tolerance_5713 or args.probe_ui_lower_tolerance_5711:
        main()
        build_ui_lower_tolerance_probe()
    elif args.probe_ui_tolerance_5807 or args.probe_ui_tolerance_5809:
        main()
        build_ui_tolerance_probe()
    elif args.probe_ui_crest_46 or args.probe_ui_crest_47:
        main()
        build_ui_crest_probe()
    elif args.probe_ui_peak_31129 or args.probe_ui_peak_31130:
        main()
        build_ui_peak_probe()
    elif args.probe_outer_slope_32 or args.probe_outer_slope_33:
        main()
        build_outer_slope_probe()
    elif args.probe_outer_endpoint_983 or args.probe_outer_endpoint_984:
        main()
        build_outer_endpoint_probe()
    elif args.probe_ambience_orientation_forward or args.probe_ambience_orientation_reverse:
        main()
        build_ambience_orientation_probe()
    elif args.probe_ambience_centroid_above:
        main()
        build_ambience_centroid_above_probe()
    elif args.probe_ambience_centroid_below:
        main()
        build_ambience_centroid_below_probe()
    elif args.probe_ui_mixed_pass:
        main()
        build_ui_mixed_pass_probe()
    elif args.probe_ui_joint_below:
        main()
        build_ui_joint_below_probe()
    elif args.probe_ui_orientation_forward or args.probe_ui_orientation_reverse:
        main()
        build_ui_orientation_probe(args.probe_ui_orientation_reverse)
    elif args.probe_ui_lower_centroid_below or args.probe_ui_lower_centroid_above:
        main()
        build_ui_lower_centroid_probe(.95 if args.probe_ui_lower_centroid_below else .94,
                                      "below" if args.probe_ui_lower_centroid_below else "above")
    elif args.probe_ui_centroid_below or args.probe_ui_centroid_above:
        main()
        build_ui_centroid_probe(1.11 if args.probe_ui_centroid_below else 1.10,
                                "below" if args.probe_ui_centroid_below else "above")
    elif args.probe_ui_duration_below or args.probe_ui_duration_at:
        main()
        build_ui_duration_probe(6719 if args.probe_ui_duration_below else 6720,
                                "below" if args.probe_ui_duration_below else "at")
    elif args.probe_ui_clone:
        main()
        build_ui_clone_probe()
    elif args.probe_invalid:
        build_invalid_probes()
        build_width_probes()
        build_rate_channel_probes()
    else:
        main(args.probe_failing, args.probe_slope, args.probe_flat, args.probe_layer_flat, args.probe_layer_join, args.probe_layer_slope, args.probe_layer_alt_flat, args.probe_layer_alt_join, args.probe_layer_alt_slope, args.probe_layer_alt_reverse, args.probe_layer_third_slope, args.probe_layer_third_slope_edge_pass, args.probe_layer_third_slope_edge_fail, args.probe_layer_third_join, args.probe_layer_third_join_edge_pass, args.probe_layer_third_join_edge_fail)
