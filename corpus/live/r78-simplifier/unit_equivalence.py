#!/usr/bin/env python3
"""r78 SIMPLIFIER unit equivalence: the pure/dead-weight helpers, control vs
candidate, on synthetic inputs — no host audio state touched.

usage: unit_equivalence.py CONTROL.py CAND.py
"""
import importlib.util
import json
import sys
import tempfile
import wave
from hashlib import sha256
from pathlib import Path

import numpy as np


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ctl = load(sys.argv[1], "ctl")
    cand = load(sys.argv[2], "cand")
    out = {}

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # 1. the tag tone is byte-identical (the deleted `rate` default is
        #    the only value any call site ever passed)
        a, b = tmp / "a.wav", tmp / "b.wav"
        ctl._playback_r78_write_tone(a, 0.5)
        cand._playback_r78_write_tone(b, 0.5)
        out["tone_bytes_equal"] = sha256(a.read_bytes()).hexdigest() == \
            sha256(b.read_bytes()).hexdigest()
        out["tone_sha256"] = sha256(a.read_bytes()).hexdigest()
        # 2. the tone classifier is dict-identical on the same wav
        wa = ctl._playback_r78_tone_windows(a)
        wb = cand._playback_r78_tone_windows(b)
        out["tone_windows_equal"] = json.dumps(wa, sort_keys=True) == \
            json.dumps(wb, sort_keys=True)
        out["tone_windows_mine"] = wa["mine_windows"]
        # 3. an unsupported (mono) tap takes the same path
        mono = tmp / "mono.wav"
        with wave.open(str(mono), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(48000)
            w.writeframes(b"\0\0" * 4800)
        out["mono_tap_equal"] = json.dumps(ctl._playback_r78_tone_windows(mono),
                                           sort_keys=True) == \
            json.dumps(cand._playback_r78_tone_windows(mono), sort_keys=True)

    # 4. hw-params parser on the shapes the aplay legs emit
    texts = [
        'FORMAT: S16_LE S24_3LE\nCHANNELS: 2\nRATE: 48000\n',
        'HW Params of device "hw:0,0":\nFORMAT: S32_LE\nCHANNELS: [2 8]\n'
        'RATE: [48000 96000]\n',
        'CHANNELS: 2\nRATE: 48000 96000\n',
        '',
    ]
    out["hw_params_equal"] = all(
        ctl._playback_r78_hw_params(t) == cand._playback_r78_hw_params(t)
        for t in texts)

    # 5. the ratio-bucket helper on a grid
    grid = [0, 1, 1000, 22050 * 4, 44100 * 4, 48000 * 4, 96000 * 4, 1e9]
    out["nearest_equal"] = all(
        ctl._playback_r78_nearest(v, (22050, 44100, 48000, 96000), 0.25) ==
        cand._playback_r78_nearest(v, (22050, 44100, 48000, 96000), 0.25)
        for v in grid)

    # 6. the consumer/producer witnesses on synthetic edge sets, including
    #    the ambiguous, empty and one-sided cases
    links = [
        [("t:output_FL", "sinkA:playback_FL"),
         ("t:output_FR", "sinkA:playback_FR")],
        [("t:output_FL", "sinkA:playback_FL"),
         ("t:output_FR", "sinkB:playback_FR")],
        [],
        [("t:output_FL", "sinkA:playback_FL")],
        [("feed:output_FL", "t:input_FL"), ("feed:output_FR", "t:input_FR")],
    ]
    out["consumers_equal"] = all(
        ctl._playback_r78_consumers("t", L) ==
        cand._playback_r78_consumers("t", L) for L in links)
    out["producers_equal"] = all(
        ctl._playback_r78_producers("t", L) ==
        cand._playback_r78_producers("t", L) for L in links)

    # 7. the errclass tuple on the classes the aplay legs carry
    errs = ["Device or resource busy", "Unknown PCM pulse",
            "wrong extended format: BOGUS", "",
            "pw-play [options]", "failed to link ports: x"]
    out["errclass_equal"] = all(
        ctl._playback_r78_errclass(e) == cand._playback_r78_errclass(e)
        for e in errs)

    # 8. the pw-link adapter on a guaranteed-failing pair: rc is the verdict,
    #    err is the bounded echo (the fold unifies the bound at 100)
    bad = [("r78sim_no_such_out", "r78sim_no_such_in")]
    ra = ctl._playback_r78_pwlink_batch(bad, True)
    rb = cand._playback_r78_pwlink_batch(bad, True)
    out["pwlink_exit_equal"] = [r["exit"] for r in ra] == \
        [r["exit"] for r in rb]
    out["pwlink_err_len"] = [len(r["err"] or "") for r in ra], \
        [len(r["err"] or "") for r in rb]
    out["pwlink_err_prefix_equal"] = all(
        (x["err"] or "")[:80] == (y["err"] or "")[:80]
        for x, y in zip(ra, rb))

    bad_keys = [k for k, v in out.items()
                if k.endswith("_equal") and not v]
    print(json.dumps(out, indent=1))
    print("UNIT VERDICT:", "PASS" if not bad_keys else f"FAIL {bad_keys}")
    return 0 if not bad_keys else 1


if __name__ == "__main__":
    sys.exit(main())
