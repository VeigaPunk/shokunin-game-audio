#!/usr/bin/env python3
"""r77 SIMPLIFIER — applied deletion batch (scratch copy only).

Every replacement is asserted to apply exactly `n` times; the script prints a
unified diff. Target: /tmp/r77-simpl-cand/corpus/fixtures/measure_audio.py
(the r77 family only — no pre-r77 code path is touched).

Batch:
  S1  _capture_r77_file_leg: dead `exact_bytes` parameter + unreachable
      `or insp["bytes"] == 0` disjunct (both call sites pass True).
  S2  _capture_r77_lattice_cell: dead `sink` parameter + `elif sink: pass`.
  S3  _capture_r77_link_producers: drop the parallel `names` accumulator;
      `producers` is derived from the per-port map (one authority).
  S4  _capture_r77_reap: one bounded-wait-then-killpg adapter for the three
      inline copies (lattice cell, loss run, sever cell).
  S5  capture_target_loss_r77_entry: unreachable `if not bounded` guard.
  S6  _capture_r77_sink_names: enumerate SINKS, not sources — the check
      `CAPTURE_R77_NULL_SINK not in ...` could never fire (vacuously true).
  S7  dead internal leaves: _capture_r77_node_props `count`;
      _capture_r77_run's unread `link_baseline` return field.
  S8  duplicate-authority derivations: LOSS_BYTES from LOSS_FRAMES;
      split under/over from the data limit + one named margin;
      format baseline from FORMAT_FRAMES.
  S9  split undershoot: the `and` guard that silently skips the rotation check.
  S10 _capture_r77_loss_leaf: three-valued data_actual_zero (a missing data
      chunk is unknown, not "non-zero payload").
  S11 arecord sever entry: one device tuple / one `plug` computation.
"""
import difflib
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else \
    "/tmp/r77-simpl-cand/corpus/fixtures/measure_audio.py"

PATCH = []


def rep(old, new, n=1, why=""):
    PATCH.append((old, new, n, why))


# --- S1 ---------------------------------------------------------------------
rep("""def _capture_r77_file_leg(argv, fname, tmp, exact_bytes=False):
    \"\"\"One bounded file-writing leg under the r77 class set.\"\"\"""",
    """def _capture_r77_file_leg(argv, fname, tmp):
    \"\"\"One bounded file-writing leg under the r77 class set. Every leg here
    is exactly bounded (`-n <frames>`), so the byte count is a pinned leaf.\"\"\"""",
    why="S1 dead parameter")

rep("""    if insp.get("bytes") is not None and (exact_bytes or insp["bytes"] == 0):
        fin["bytes"] = insp["bytes"]""",
    """    if insp.get("bytes") is not None:
        fin["bytes"] = insp["bytes"]""",
    why="S1 unreachable disjunct")

rep("""                f"fmt_{name}.wav", tmp, exact_bytes=True)""",
    """                f"fmt_{name}.wav", tmp)""",
    why="S1 call site")

rep("""                f"ref_{name}.wav", tmp, exact_bytes=True)""",
    """                f"ref_{name}.wav", tmp)""",
    why="S1 call site")

# --- S2 ---------------------------------------------------------------------
rep("""def _capture_r77_lattice_cell(name, target, prop, tmp, member, sink):""",
    """def _capture_r77_lattice_cell(name, target, prop, tmp, member):""",
    why="S2 dead parameter")

rep("""    shown = " ".join(argv[:-1])
    if target:
        shown = shown.replace(target, "<target>")
    elif sink:
        pass
""",
    """    shown = " ".join(argv[:-1])
    if target:
        shown = shown.replace(target, "<target>")
""",
    why="S2 dead branch")

rep("""            legs[name] = _capture_r77_lattice_cell(
                name, target, prop, tmp, member, inv["default_sink"])""",
    """            legs[name] = _capture_r77_lattice_cell(name, target, prop, tmp,
                                                   member)""",
    why="S2 call site")

# --- S3 ---------------------------------------------------------------------
rep("""    names, per_port, port = [], {}, None
    for ln in text.splitlines():
        if not ln or not ln[0].isspace():
            # a new top-level entry: a port name, or a foreign node's name
            port = ln.strip() if ln.strip().startswith("pw-record:input_") \\
                else None
            continue
        if port and "|<-" in ln:
            names.append(ln.split("|<-", 1)[1].strip())
            per_port.setdefault(port, []).append(
                ln.split("|<-", 1)[1].strip())
    out["producers"] = sorted(set(names))
    out["per_port"] = {k: sorted(set(v)) for k, v in per_port.items()}""",
    """    per_port, port = {}, None
    for ln in text.splitlines():
        if not ln or not ln[0].isspace():
            # a new top-level entry: a port name, or a foreign node's name
            port = ln.strip() if ln.strip().startswith("pw-record:input_") \\
                else None
            continue
        if port and "|<-" in ln:
            per_port.setdefault(port, []).append(ln.split("|<-", 1)[1].strip())
    out["per_port"] = {k: sorted(set(v)) for k, v in per_port.items()}
    out["producers"] = sorted({p for v in out["per_port"].values() for p in v})""",
    why="S3 duplicate accumulator")

# --- S4 ---------------------------------------------------------------------
rep("""def _capture_r77_link_producers():""",
    """def _capture_r77_reap(proc, timeout_s=CAPTURE_R77_TIMEOUT_S):
    \"\"\"Bounded wait, then KILL the whole process group — one escalation
    policy for every r77 leg.\"\"\"
    try:
        proc.wait(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()


def _capture_r77_link_producers():""",
    why="S4 shared reap adapter")

rep("""    try:
        proc.wait(timeout=CAPTURE_R77_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
""",
    """    _capture_r77_reap(proc)
""",
    n=2, why="S4 inline copies (lattice cell + loss run)")

rep("""        try:
            proc.wait(timeout=CAPTURE_R77_KILL_WAIT_S)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
""",
    """        _capture_r77_reap(proc, CAPTURE_R77_KILL_WAIT_S)
""",
    why="S4 inline copy (sever cell)")

# --- S5 ---------------------------------------------------------------------
rep("""    bounded = entry.get("bounded")
    if not bounded:
        entry["failures"] = failures
        return entry
    for key in ("baseline", "fallback_control", "after_loss"):""",
    """    bounded = entry["bounded"]
    for key in ("baseline", "fallback_control", "after_loss"):""",
    why="S5 unreachable guard")

# --- S6 ---------------------------------------------------------------------
rep("""def _capture_r77_sink_names():
    try:
        proc = subprocess.run(["pactl", "list", "sources", "short"],
                              capture_output=True, timeout=10)""",
    """def _capture_r77_sink_names():
    \"\"\"SINK names. A `module-null-sink` creates the sink `X` and the monitor
    SOURCE `X.monitor`, so enumerating sources can never contain the bare sink
    name and the caller's `sink_gone` test would be vacuously true.\"\"\"
    try:
        proc = subprocess.run(["pactl", "list", "sinks", "short"],
                              capture_output=True, timeout=10)""",
    why="S6 vacuous check armed")

# --- S7 ---------------------------------------------------------------------
rep("""    out["count"] = len(out["nodes"])
    return out""",
    """    return out""",
    why="S7 dead leaf (node_props.count)")

rep("""            "samples": samples, "wall_s": round(time.monotonic() - t0, 2),
            "link_baseline": link_baseline,
            "stderr": proc.stderr.read().decode(errors="replace")}""",
    """            "samples": samples, "wall_s": round(time.monotonic() - t0, 2),
            # drained (bounded pipe), not recorded
            "stderr": proc.stderr.read().decode(errors="replace")}""",
    why="S7 unread return field")

# --- S8 ---------------------------------------------------------------------
rep("""CAPTURE_R77_LOSS_BYTES = 44 + 96000 * 4   # -n is a FRAME bound""",
    """CAPTURE_R77_LOSS_BYTES = 44 + CAPTURE_R77_LOSS_FRAMES * 4   # -n bound""",
    why="S8a one authority for the loss bound")

rep("""    for label, want in (("bound_d3_kill_early", 3 * 48000),
                        ("bound_d5_kill_early", 5 * 48000),
                        ("bound_d12_kill_early", 12 * 48000),
                        ("bound_d12_kill_late", 12 * 48000),
                        ("bound_s300k_kill", 300000)):""",
    """    fps = CAPTURE_R77_FRAMES_PER_SECOND
    for label, want in (("bound_d3_kill_early", 3 * fps),
                        ("bound_d5_kill_early", 5 * fps),
                        ("bound_d12_kill_early", 12 * fps),
                        ("bound_d12_kill_late", 12 * fps),
                        ("bound_s300k_kill", 300000)):""",
    why="S8d the -d bound uses the pinned rate, not a literal 48000")

rep("""    rate = fmt.get("rate") or 48000""",
    """    rate = fmt.get("rate") or CAPTURE_R77_FRAMES_PER_SECOND""",
    why="S8e reader rate fallback uses the pinned rate")

rep("""CAPTURE_R77_SPLIT_UNDER_FRAMES = 536870912 - 240000
CAPTURE_R77_SPLIT_OVER_FRAMES = 536870912 + 240000""",
    """CAPTURE_R77_SPLIT_LIMIT_FRAMES = CAPTURE_R77_SPLIT_DATA_LIMIT // 4
CAPTURE_R77_SPLIT_MARGIN_FRAMES = 240000   # 0.5 s at the pinned frame size
CAPTURE_R77_SPLIT_UNDER_FRAMES = \\
    CAPTURE_R77_SPLIT_LIMIT_FRAMES - CAPTURE_R77_SPLIT_MARGIN_FRAMES
CAPTURE_R77_SPLIT_OVER_FRAMES = \\
    CAPTURE_R77_SPLIT_LIMIT_FRAMES + CAPTURE_R77_SPLIT_MARGIN_FRAMES""",
    why="S8b frame limit has one authority")

rep("""                if name == "arecord_unbounded" and tag == "kill":
                    cells[key]["declared_bound_frames"] = \\
                        CAPTURE_R77_SPLIT_DATA_LIMIT // 4""",
    """                if name == "arecord_unbounded" and tag == "kill":
                    cells[key]["declared_bound_frames"] = \\
                        CAPTURE_R77_SPLIT_LIMIT_FRAMES""",
    why="S8b use the named limit")

rep("""    if legs.get("baseline", {}).get("file", {}).get("bytes") != 19244:
        failures.append("format baseline: expected the exact 44 + 4800 x 4 "
                        f"= 19244 B, got "
                        f"{legs.get('baseline', {}).get('file', {}).get('bytes')}")""",
    """    baseline_bytes = 44 + CAPTURE_R77_FORMAT_FRAMES * 4   # 2ch x s16
    if legs.get("baseline", {}).get("file", {}).get("bytes") != baseline_bytes:
        failures.append(f"format baseline: expected {baseline_bytes} B, got "
                        f"{legs.get('baseline', {}).get('file', {}).get('bytes')}")""",
    why="S8c baseline pin derived, not magic")

# --- S9 ---------------------------------------------------------------------
rep("""    if under.get("siblings") and list(under["siblings"]) != ["rot.wav"]:""",
    """    if list(under.get("siblings") or {}) != ["rot.wav"]:""",
    why="S9 the `and` guard silently skipped the check")

# --- S10 --------------------------------------------------------------------
rep("""            "data_finalized": insp.get("data_finalized"),
            "data_actual_zero": insp.get("data_actual") == 0,
            "data_declared_field": insp.get("data_declared_field"),""",
    """            "data_finalized": insp.get("data_finalized"),
            # a missing data chunk is UNKNOWN, not "non-zero payload".
            "data_actual_zero": (None if insp.get("data_actual") is None
                                 else insp.get("data_actual") == 0),
            "data_declared_field": insp.get("data_declared_field"),""",
    why="S10 three-valued leaf")

# --- S11 -------------------------------------------------------------------
rep("""    entry["frames_per_second"] = CAPTURE_R77_FRAMES_PER_SECOND
    legs = {}""",
    """    entry["frames_per_second"] = CAPTURE_R77_FRAMES_PER_SECOND
    plug = "plughw:" + hw0.split(":", 1)[1] if ":" in hw0 else None
    devices = tuple(d for d in (hw0, plug, "sysdefault") if d)
    legs = {}""",
    why="S11 one device list")

rep("""        plug = "plughw:" + hw0.split(":", 1)[1] if ":" in hw0 else None
        for dev in (hw0, plug, "sysdefault"):
            if not dev:
                continue
            tag = re.sub(r"\\W+", "_", dev)""",
    """        for dev in devices:
            tag = re.sub(r"\\W+", "_", dev)""",
    why="S11 sweep uses it")

rep("""    plug = "plughw:" + hw0.split(":", 1)[1] if ":" in hw0 else None
    dev_tags = [re.sub(r"\\W+", "_", d)
                for d in (hw0, plug, "sysdefault") if d]""",
    """    dev_tags = [re.sub(r"\\W+", "_", d) for d in devices]""",
    why="S11 coverage check uses the same list")


def main():
    src = open(PATH).read()
    out = src
    for old, new, n, why in PATCH:
        got = out.count(old)
        if got != n:
            print(f"FAILED [{why}]: pattern occurs {got}x, expected {n}x")
            print(old[:200])
            return 1
        out = out.replace(old, new)
    diff = difflib.unified_diff(src.splitlines(True), out.splitlines(True),
                               "measure_audio.py (HEAD 65790f1)",
                               "measure_audio.py (r77 simplifier batch)")
    d = "".join(diff)
    open(PATH + ".diff", "w").write(d)
    print(d)
    open(PATH, "w").write(out)
    added = sum(1 for l in d.splitlines() if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in d.splitlines() if l.startswith("-") and not l.startswith("---"))
    print(f"# batch: {len(PATCH)} replacements, +{added} / -{removed} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
