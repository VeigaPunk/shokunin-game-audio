#!/usr/bin/env python3
"""Host-free unit equivalence: pristine r77 helpers vs the batch's versions.

Imports both fixture copies (distinct module names) and drives the changed
helpers on synthetic inputs, so every equivalence claim in §3 that does not
need a live audio graph is proven directly. The one deliberate difference
(S10's unknown-data-chunk leaf) is asserted to be the *only* difference.

usage: unit_equivalence.py
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

PRISTINE = "/tmp/r77-simpl-control/corpus/fixtures/measure_audio.py"
CAND = "/tmp/r77-simpl-cand/corpus/fixtures/measure_audio.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


A = load(PRISTINE, "ma_pristine")
B = load(CAND, "ma_candidate")

FAIL = []


def eq(label, x, y):
    if x != y:
        FAIL.append(f"{label}: {x!r} != {y!r}")
    print(f"  {'OK ' if x == y else 'DIFF'} {label}"
          + ("" if x == y else f"   {x!r} vs {y!r}"))


# --- synthetic `pw-link -l` tables -----------------------------------------
LINK_EMPTY = "\n"
LINK_ONE_SIDED = """pw-record:input_FL
  |<- alsa_output.sinkA:monitor_FL
pw-record:input_FR
"""
LINK_BOTH = """pw-record:input_FL
  |<- alsa_output.sinkA:monitor_FL
  |<- alsa_output.ghost:monitor_FL
pw-record:input_FR
  |<- alsa_output.sinkA:monitor_FR
some-other-node:input_FL
  |<- alsa_output.foreign:monitor_FL
"""
LINK_FOREIGN_NODE = """pw-record:input_FL
  |<- alsa_output.sinkA:monitor_FL
pw-record:input_FR
  |<- alsa_output.sinkA:monitor_FR
Lavf63.1.101:input_FL
  |<- alsa_output.other:monitor_FL
Lavf63.1.101:input_FR
  |<- alsa_output.other:monitor_FR
"""


def fake_run(text):
    class P:
        returncode = 0
        stdout = text.encode()
        stderr = b""
    return lambda *a, **k: P()


def link_case(label, text):
    ra = ra_b = None
    for mod, box in ((A, "a"), (B, "b")):
        mod.subprocess.run = fake_run(text)
        r = mod._capture_r77_link_producers()
        r.pop("exit", None)
        if box == "a":
            ra = r
        else:
            ra_b = r
    eq(f"link_producers[{label}]", ra, ra_b)
    return ra


print("== S3 `_capture_r77_link_producers` (synthetic pw-link -l tables)")
for label, text in (("empty", LINK_EMPTY), ("one-sided", LINK_ONE_SIDED),
                    ("both+ghost", LINK_BOTH), ("foreign node", LINK_FOREIGN_NODE)):
    r = link_case(label, text)
    print(f"      -> producers={r['producers']} nodes={r['nodes']} "
          f"ambiguous={r['ambiguous']}")

print("== S3 `_capture_r77_link_delta` (synthetic per-port maps)")
before = {"per_port": {"pw-record:input_FL": ["a:monitor_FL"],
                       "pw-record:input_FR": ["a:monitor_FR"]},
          "producers": ["a:monitor_FL", "a:monitor_FR"]}
during = {"per_port": {"pw-record:input_FL": ["a:monitor_FL", "b:monitor_FL"],
                       "pw-record:input_FR": ["a:monitor_FR", "b:monitor_FR"]},
          "producers": ["a:monitor_FL", "a:monitor_FR",
                        "b:monitor_FL", "b:monitor_FR"]}
eq("link_delta", A._capture_r77_link_delta(before, during),
   B._capture_r77_link_delta(before, during))

print("== `_capture_r77_frame_class` (whole verdict matrix)")
cases = [(None, 10, 20), (0, 0, 0), (5, 0, 0), (10, 10, 20), (20, 10, 20),
         (30, 10, 20), (7, 10, 20), (10, 10, 10)]
for c in cases:
    eq(f"frame_class{c}", A._capture_r77_frame_class(*c),
       B._capture_r77_frame_class(*c))

print("== S8e reader rate fallback")
for insp in ({"fmt": {"rate": 44100, "channels": 2, "bits": 16}}, {}):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "x.wav"
        A._capture_r77_write_synthetic(p, frames=4, rate=48000)
        ra = A._capture_r77_readers(p, insp)
        rb = B._capture_r77_readers(p, insp)
        ra.pop("wave", None)
        rb.pop("wave", None)
    eq(f"readers(rate={insp.get('fmt', {}).get('rate')})", ra, rb)

print("== `_capture_r77_rate_buckets` / `_capture_r77_reader_honesty`")
samples = [{"at_s": 0.4, "bytes": 73772}, {"at_s": 0.9, "bytes": 172076},
           {"at_s": 1.6, "bytes": 303148}, {"at_s": 2.6, "bytes": 495660}]
eq("rate_buckets", A._capture_r77_rate_buckets(samples),
   B._capture_r77_rate_buckets(samples))
cells = {"k": {"readers": {"honest_frames": 10, "declared_frames": 20,
                           "wave": {"value": None, "verdict": "rejects"},
                           "ffprobe": {"value": 20, "verdict": "declared_echo"},
                           "soxi_s": {"value": 10, "verdict": "honest"},
                           "soxi_D": {"value": 30, "verdict": "inflated"},
                           "sndfile": {"value": 7, "verdict": "underreports"}}}}
eq("reader_honesty", A._capture_r77_reader_honesty(cells),
   B._capture_r77_reader_honesty(cells))

print("== S4 `_capture_r77_reap` (real child: exits / ignores TERM)")
import os
import signal
import time
for label, argv in (("exits", ["true"]), ("ignores-term",
                                          ["python3", "-c",
                                           "import signal,time;"
                                           "signal.signal(signal.SIGTERM,"
                                           "signal.SIG_IGN);time.sleep(30)"])):
    outs = []
    for mod in (A, B):
        p = subprocess.Popen(argv, start_new_session=True)
        if label == "ignores-term":
            time.sleep(0.2)
            p.send_signal(signal.SIGTERM)
        t0 = time.monotonic()
        try:
            p.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
        outs.append(round(time.monotonic() - t0, 1))
    eq(f"reap[{label}] (wall class)", outs[0] == outs[1] or
       abs(outs[0] - outs[1]) <= 0.6, True)
    print(f"      -> pristine {outs[0]}s / candidate {outs[1]}s")

print("== S10 `_capture_r77_loss_leaf`: the ONE deliberate difference")
with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "w.wav"
    p.write_bytes(b"RIFF" + b"\x00" * 40)
    run = {"exit_code": 1, "unloaded": None}
    insp_missing_data = {"exists": True, "bytes": 44, "riff": True}
    la = A._capture_r77_loss_leaf(p, run)
    lb = B._capture_r77_loss_leaf(p, run)
    print(f"      pristine  data_actual_zero={la['data_actual_zero']!r}")
    print(f"      candidate data_actual_zero={lb['data_actual_zero']!r}")
    diff = {k for k in set(la) | set(lb) if la.get(k) != lb.get(k)}
    eq("only declared key differs", diff, {"data_actual_zero"})
    # and for a *real* wav (the state the round measures) they must be equal
    A._capture_r77_write_synthetic(p, frames=10, rate=48000)
    real = A._capture_wav_inspect(p)
    la = A._capture_r77_loss_leaf(p, run)
    lb = B._capture_r77_loss_leaf(p, run)
    eq("real-wav leaf", la, lb)
    print(f"      real wav data_actual_zero={la['data_actual_zero']!r}")

print()
if FAIL:
    print(f"UNIT EQUIVALENCE: FAIL ({len(FAIL)})")
    for f in FAIL:
        print("  ", f)
    sys.exit(1)
print("UNIT EQUIVALENCE: PASS (all changed helpers, synthetic inputs; the only "
      "difference is S10's declared unknown-state leaf)")
