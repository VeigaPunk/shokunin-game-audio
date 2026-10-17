#!/usr/bin/env python3
"""r77 CRITIC — executable counterexamples against the r77 gate set.

Each battery drives a REAL r77 gate function from the committed fixture
(`corpus/fixtures/measure_audio.py` @ 65790f1) with synthetic leg cells
that satisfy EVERY other assertion, so the only deviation is the one
under test. No audio device is touched: the leg factories replace the
capture helpers; the only subprocesses are the entries' own cheap
enumeration calls (pactl list / arecord -l).

  A  arecord device-axis TERM legs: a cell that produced NO FILE passes.
  B  format axis: rate legs whose byte count is NOT rate-invariant pass.
  C  readers: a unit calibration that is 2x wrong passes.
  D  target-loss sha identity: absent == absent reads as a match.
"""
import importlib.util
import json
import signal as _sig
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
FIXTURE = ROOT / "corpus/fixtures/measure_audio.py"
spec = importlib.util.spec_from_file_location("ma_r77", FIXTURE)
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)

OUT = {}


def banner(t):
    print("\n" + "=" * 72 + f"\n{t}\n" + "=" * 72)


# ---------------------------------------------------------------- battery A
def battery_a():
    banner("A  arecord device-axis TERM legs with NO FILE AT ALL")
    real = ma._capture_r77_sever_cell

    def fake(argv, fname, sig, tmp, wait_s=ma.CAPTURE_R77_READER_WAIT_S):
        kill = sig == _sig.SIGKILL
        base = {"exit_code": -9 if kill else 1, "early_exit_code": None,
                "signal": "SIGKILL" if kill else "SIGTERM"}
        if fname.startswith("dev_") and not fname.startswith("devk_"):
            # THE COUNTEREXAMPLE: the TERM device leg wrote nothing at all.
            return {**base, "file": {"exists": False}}
        if fname.startswith("devk_"):
            return {**base, "file": {"exists": True, "bytes": 456044,
                                     "data_finalized": False,
                                     "data_declared_field": "other"}}
        label = fname[len("sev_"):].rsplit("_term", 1)[0].rsplit("_kill", 1)[0]
        want = {"d3": 576000, "d5": 960000, "d12": 2304000,
                "s300k": 1200000}.get(label)
        if want is None:            # unbounded
            if kill:
                return {**base, "file": {"exists": True, "bytes": 168044,
                                         "data_declared": 2147483648,
                                         "data_actual": 168000,
                                         "data_finalized": False,
                                         "data_declared_field":
                                             "placeholder_80000000"}}
            return {**base, "exit_code": 1, "error_class":
                    "aborted_by_signal",
                    "file": {"exists": True, "bytes": 168180,
                             "data_declared": 168136, "data_actual": 168136,
                             "data_finalized": True}}
        if kill:
            return {**base, "file": {"exists": True, "bytes": 72044,
                                     "data_declared": want,
                                     "data_actual": 72000,
                                     "data_finalized": False,
                                     "data_declared_field": "other"}}
        return {**base, "exit_code": 1, "error_class": "aborted_by_signal",
                "file": {"exists": True, "bytes": 72184,
                         "data_declared": 72140, "data_actual": 72140,
                         "data_finalized": True}}

    ma._capture_r77_sever_cell = fake
    try:
        entry = ma.capture_arecord_sever_r77_entry()
    finally:
        ma._capture_r77_sever_cell = real
    dev_term = [k for k in entry["legs"] if k.startswith("term_")]
    nofile = [k for k in dev_term
              if entry["legs"][k]["file"]["exists"] is False]
    print(f"device-axis TERM legs: {len(dev_term)}; "
          f"of those, file absent: {len(nofile)}")
    print(f"entry failures: {entry['failures']}")
    print(f"eintr_cells: {entry['eintr_cells']}  "
          f"scout_alsa_read_eintr_reproduced: "
          f"{entry['scout_alsa_read_eintr_reproduced']}")
    OUT["A"] = {"device_term_legs": len(dev_term),
                "no_file_legs": len(nofile), "failures": entry["failures"]}


# ---------------------------------------------------------------- battery B
def battery_b():
    banner("B  format axis: rate legs with a NON rate-invariant byte count")
    real = ma._capture_r77_file_leg
    fed = {}

    def fake(argv, fname, tmp, exact_bytes=False):
        if fname.startswith("ref_"):
            return {"exit_code": 1, "error_class": "usage_refusal",
                    "blocked": False, "file": {"exists": False}}
        fmt = {"tag": 1, "channels": 2, "rate": 48000, "bits": 16}
        for i, a in enumerate(argv):
            if a == "--rate":
                fmt["rate"] = int(argv[i + 1])
            elif a == "--channels":
                fmt["channels"] = int(argv[i + 1])
            elif a == "--format":
                v = argv[i + 1]
                if v in ("s24", "s32", "u8"):
                    fmt["bits"] = {"s24": 24, "s32": 32, "u8": 8}[v]
                elif v in ("f32", "f64"):
                    fmt["tag"], fmt["bits"] = 3, {"f32": 32, "f64": 64}[v]
        if fmt["channels"] == 6:
            fmt["tag"] = 65534
        nbytes = (19244 if fmt["rate"] == 48000 and fmt["bits"] == 16
                  and fmt["channels"] == 2 else 19244 + fmt["rate"] // 8)
        fed[f"{fmt['rate']}/{fmt['channels']}/{fmt['bits']}"] = nbytes
        return {"exit_code": 1, "error_class": None, "blocked": False,
                "file": {"exists": True, "bytes": nbytes,
                         "data_finalized": True, "fmt": fmt}}

    ma._capture_r77_file_leg = fake
    try:
        entry = ma.capture_format_axis_r77_entry()
    finally:
        ma._capture_r77_file_leg = real
    rate_legs = {k: fed.get(v, None) for k, v in
                 (("rate_8000", "8000/2/16"), ("rate_44100", "44100/2/16"),
                  ("rate_96000", "96000/2/16"),
                  ("rate_192000", "192000/2/16"))}
    print("byte counts fed, by rate leg:", json.dumps(rate_legs))
    print(f"entry failures: {entry['failures']}")
    OUT["B"] = {"bytes_by_rate_leg": rate_legs, "failures": entry["failures"]}


# ---------------------------------------------------------------- battery C
def battery_c():
    banner("C  readers: a UNIT CALIBRATION that is 2x wrong (soxi = samples)")
    real_cell = ma._capture_r77_sever_cell
    real_readers = ma._capture_r77_readers

    def readers_2x(path, insp):
        fb = 4
        honest = (insp.get("data_actual") or 0) // fb
        return {"honest_frames": honest, "declared_frames": honest,
                "frame_bytes": fb, "rate": 48000,
                "wave": {"value": honest, "verdict": "honest"},
                "ffprobe": {"value": honest, "verdict": "honest"},
                "soxi_s": {"value": 2 * honest, "verdict": "inflated"},
                "soxi_D": {"value": 2 * honest, "verdict": "inflated"},
                "sndfile": {"value": honest, "verdict": "honest"}}

    def fake_cell(argv, fname, sig, tmp,
                  wait_s=ma.CAPTURE_R77_READER_WAIT_S):
        kill = sig == _sig.SIGKILL
        arec = argv[0] == "arecord"
        bounded = arec and "-d" in argv
        fin = {"exists": True, "bytes": 479276, "data_finalized": not kill,
               "data_actual_zero": False, "data_declared": 479232,
               "data_actual": 479232, "data_declared_field": "finalized",
               "fmt": {"tag": 1, "channels": 2, "rate": 48000, "bits": 16}}
        if kill:
            fin["data_declared"] = 0
            fin["data_declared_field"] = "zero"
        cell = {"exit_code": -9 if kill else 1, "early_exit_code": None,
                "signal": "SIGKILL" if kill else "SIGTERM", "file": fin}
        if bounded:
            fin["data_declared"] = 12 * 48000 * 4
            fin["data_declared_field"] = "other"
            fin["data_actual"] = 456000
            fin["bytes"] = 456044
            if kill:
                cell["declared_bound_frames"] = 12 * 48000
        if arec and not bounded:
            fin["data_declared"] = 0x80000000
            fin["data_declared_field"] = "placeholder_80000000"
            fin["data_actual"] = 456000
            fin["bytes"] = 456044
            if kill:
                cell["declared_bound_frames"] = 0x80000000 // 4
        cell["readers"] = readers_2x(None, fin)
        return cell

    ma._capture_r77_sever_cell = fake_cell
    ma._capture_r77_readers = readers_2x
    try:
        entry = ma.capture_readers_r77_entry()
    finally:
        ma._capture_r77_sever_cell = real_cell
        ma._capture_r77_readers = real_readers
    cal = entry["unit_calibration"]
    answers = {r: cal["readers"][r]["value"] for r in
               ("wave", "ffprobe", "soxi_s", "soxi_D", "sndfile")}
    print(f"calibration expected_frames={cal['expected_frames']} "
          f"answers={json.dumps(answers)}")
    print(f"entry failures: {entry['failures']}")
    print(f"reader_honesty: {json.dumps(entry['reader_honesty'])}")
    OUT["C"] = {"expected_frames": cal["expected_frames"],
                "answers": answers, "failures": entry["failures"]}


# ---------------------------------------------------------------- battery D
def battery_d():
    banner("D  target-loss sha identity with BOTH files absent")
    a = ma._capture_r77_sha256(Path("/nonexistent-r77-critic-a.wav"))
    b = ma._capture_r77_sha256(Path("/nonexistent-r77-critic-b.wav"))
    print(f"_capture_r77_sha256(<absent a>) = {a!r}; "
          f"_capture_r77_sha256(<absent b>) = {b!r}")
    print(f"sha_match_control := (a == b) = {a == b!r}   <-- read as "
          f"'byte-identical'")
    OUT["D"] = {"a": a, "b": b, "sha_match_control": a == b}


if __name__ == "__main__":
    battery_a()
    battery_b()
    battery_c()
    battery_d()
    (ROOT / "corpus/live/r77-critic/gate-vacuity-batteries.json").write_text(
        json.dumps(OUT, indent=2, default=str) + "\n")
    print("\nwrote gate-vacuity-batteries.json")
