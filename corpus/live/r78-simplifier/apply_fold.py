#!/usr/bin/env python3
"""r78 SIMPLIFIER — applied deletion batch (scratch copy only).

Every replacement is asserted to apply exactly `n` times; the script prints a
unified diff. Target: the r78 arm's `corpus/fixtures/measure_audio.py`
(blob d21f5637… = HEAD d9aa6f9), r78 block only — no pre-r78 code path is
touched.

Batch (each item is receipt-neutral: it produces no leaf):
  S1  dead constants: PLAYBACK_R78_CAP_{TONE,FRAMES,UNLINK,RELINK}_S are
      referenced nowhere (the zeros entry carries its own literals).
  S2  dead parameters: _playback_r78_write_tone(rate=…) and
      _playback_r78_tone_windows(window_s=…) are never overridden — 10/10
      call sites each take the default, so the default is the only value.
  S3  vacuous guards in capture_unlinked_zeros_r78_entry: `len(seq) >= 7`
      (the event table fixes 7 size samples; the loop cannot break) and
      `len(seq_b) >= 2` (5 samples; and `not all([])` is False, so the
      conjunct is a no-op in both arms).
  S4  dead filter: every `legs` value is a dict (two write sites, both dicts).
  S5  duplicated pw-link adapter: the inline pwlink/pwlink_d loop in
      _playback_r78_run is the same adapter as _playback_r78_pwlink_batch;
      single-source it (err truncation unified at 100).
  S6  duplicated plugin legs: the aplay `plugin_default`/`plugin_pipewire`
      blocks are one leg table with one substituted word.
  S7  dead envelope: _playback_r78_link_map's `exit`/`error` fields are read
      by nobody (all three call sites take `.get("links", [])`).
  S8  dead bindings: four `cls, _line = _playback_r78_errclass(…)` unpacks
      whose second value is never read; the lattice table is iterated twice
      to rebuild a trace already carried per leg.
  S9  duplicated branch selector: the lattice resolver guard re-tests the
      exact complement of the two branches above it (and `str()` on a str).
"""
import difflib
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else \
    "/tmp/r78-simpl/cand/corpus/fixtures/measure_audio.py"

PATCH = []


def rep(old, new, n=1, why=""):
    PATCH.append((old, new, n, why))


# --- S1 ---------------------------------------------------------------------
rep("""PLAYBACK_R78_CARRIES_TONE_WINDOWS = 8  # 0.8 s of tag = content witness
PLAYBACK_R78_CAP_TONE_S = 6.0
PLAYBACK_R78_CAP_FRAMES_S = 4.8
PLAYBACK_R78_CAP_UNLINK_S = 1.6       # from the pw-record spawn
PLAYBACK_R78_CAP_RELINK_S = 3.2
PLAYBACK_R78_PAREC_POLL_S = 0.55""",
    """PLAYBACK_R78_CARRIES_TONE_WINDOWS = 8  # 0.8 s of tag = content witness
PLAYBACK_R78_PAREC_POLL_S = 0.55""",
    why="S1 four constants referenced nowhere")

# --- S2a --------------------------------------------------------------------
rep("""def _playback_r78_write_tone(path, seconds,
                             rate=PLAYBACK_R78_TONE_RATE):""",
    """def _playback_r78_write_tone(path, seconds):""",
    why="S2a dead parameter (never overridden)")
rep("""    n = int(rate * seconds)
    t = np.arange(n) / rate""",
    """    n = int(PLAYBACK_R78_TONE_RATE * seconds)
    t = np.arange(n) / PLAYBACK_R78_TONE_RATE""",
    why="S2a body uses the declared rate")
rep("""        w.setframerate(rate)""",
    """        w.setframerate(PLAYBACK_R78_TONE_RATE)""",
    why="S2a body uses the declared rate")

# --- S2b --------------------------------------------------------------------
rep("""def _playback_r78_tone_windows(path,
                               window_s=PLAYBACK_R78_TONE_WINDOW_S):""",
    """def _playback_r78_tone_windows(path):""",
    why="S2b dead parameter (never overridden)")
rep("""    win = max(64, int(rate * window_s))""",
    """    win = max(64, int(rate * PLAYBACK_R78_TONE_WINDOW_S))""",
    why="S2b body uses the declared window")
rep("""        at = round(i * window_s, 2)""",
    """        at = round(i * PLAYBACK_R78_TONE_WINDOW_S, 2)""",
    why="S2b body uses the declared window")
rep("""            cur = [at, at + window_s] if cur is None \\
                else [cur[0], at + window_s]""",
    """            cur = [at, at + PLAYBACK_R78_TONE_WINDOW_S] if cur is None \\
                else [cur[0], at + PLAYBACK_R78_TONE_WINDOW_S]""",
    why="S2b body uses the declared window")

# --- S3a --------------------------------------------------------------------
rep("""        seq = a.get("size_trace", [])
        # seq = [0.8, 1.3 | unlink@1.6 | 2.1, 2.6, 3.4 | relink@3.9 | 4.4,
        #        4.9] — pre-growth, frozen window, post-relink growth.
        if len(seq) >= 7:
            pre_grew = seq[1]["bytes"] > seq[0]["bytes"] + 80000
            froze = seq[4]["bytes"] - seq[2]["bytes"] < 8192
            resumed = seq[6]["bytes"] > seq[4]["bytes"] + 150000
            if not pre_grew:
                failures.append(f"zeros consumer_unlink: file was not "
                                f"growing before the unlink {seq}")
            if not froze:
                failures.append(f"zeros consumer_unlink: file kept "
                                f"growing during the unlink {seq} — "
                                "the class is a STARVING stream, not a "
                                "zero fill")
            if not resumed:
                failures.append(f"zeros consumer_unlink: file did not "
                                f"resume after the relink {seq}")""",
    """        seq = a.get("size_trace", [])
        # seq = [0.8, 1.3 | unlink@1.6 | 2.1, 2.6, 3.4 | relink@3.9 | 4.4,
        #        4.9] — pre-growth, frozen window, post-relink growth.
        pre_grew = seq[1]["bytes"] > seq[0]["bytes"] + 80000
        froze = seq[4]["bytes"] - seq[2]["bytes"] < 8192
        resumed = seq[6]["bytes"] > seq[4]["bytes"] + 150000
        if not pre_grew:
            failures.append(f"zeros consumer_unlink: file was not "
                            f"growing before the unlink {seq}")
        if not froze:
            failures.append(f"zeros consumer_unlink: file kept "
                            f"growing during the unlink {seq} — "
                            "the class is a STARVING stream, not a "
                            "zero fill")
        if not resumed:
            failures.append(f"zeros consumer_unlink: file did not "
                            f"resume after the relink {seq}")""",
    why="S3a vacuous guard (7 size samples, no break)")

# --- S3b --------------------------------------------------------------------
rep("""        if len(seq_b) >= 2 and not all(
                s2["bytes"] > s1["bytes"] + 50000
                for s1, s2 in zip(seq_b, seq_b[1:])):""",
    """        if not all(
                s2["bytes"] > s1["bytes"] + 50000
                for s1, s2 in zip(seq_b, seq_b[1:])):""",
    why="S3b vacuous guard (5 size samples; no-op on the empty arm)")

# --- S4 ---------------------------------------------------------------------
rep("""    if not any(l.get("target_object_lies") for l in legs.values()
               if isinstance(l, dict)):""",
    """    if not any(l.get("target_object_lies") for l in legs.values()):""",
    why="S4 dead filter (both legs write sites are dicts)")

# --- S5 ---------------------------------------------------------------------
rep("""        elif kind in ("pwlink_d", "pwlink"):
            rcs = []
            for a, b in arg:
                cmd = ["pw-link", a, b] if kind == "pwlink" \\
                    else ["pw-link", "-d", a, b]
                try:
                    p = subprocess.run(cmd, capture_output=True, timeout=10)
                    rcs.append({"out": a, "in": b, "exit": p.returncode,
                                "err": p.stderr.decode(
                                    errors="replace")[:100] or None})
                except (subprocess.TimeoutExpired, OSError) as exc:
                    rcs.append({"out": a, "in": b, "exit": None,
                                "err": str(exc)[:100]})
            fired.append({"at_s": at, "when_s": when, "kind": kind,
                          "links": rcs})""",
    """        elif kind in ("pwlink_d", "pwlink"):
            fired.append({"at_s": at, "when_s": when, "kind": kind,
                          "links": _playback_r78_pwlink_batch(
                              arg, kind == "pwlink_d")})""",
    why="S5 single-source the pw-link adapter")
rep('''    """Fire a batch of pw-link connects/disconnects -> per-pair rcs."""
    rcs = []
    for a, b in pairs:
        cmd = ["pw-link", "-d", a, b] if disconnect else ["pw-link", a, b]
        try:
            p = subprocess.run(cmd, capture_output=True, timeout=10)
            rcs.append({"out": a, "in": b, "exit": p.returncode,
                        "err": p.stderr.decode(
                            errors="replace")[:80] or None})
        except (subprocess.TimeoutExpired, OSError) as exc:
            rcs.append({"out": a, "in": b, "exit": None,
                        "err": str(exc)[:80]})
    return rcs''',
    '''    """Fire a batch of pw-link connects/disconnects -> per-pair rcs.
    The one adapter for both the event-fired links and the zeros legs; the
    stderr echo is bounded at 100 chars."""
    rcs = []
    for a, b in pairs:
        cmd = ["pw-link", "-d", a, b] if disconnect else ["pw-link", a, b]
        try:
            p = subprocess.run(cmd, capture_output=True, timeout=10)
            rcs.append({"out": a, "in": b, "exit": p.returncode,
                        "err": p.stderr.decode(
                            errors="replace")[:100] or None})
        except (subprocess.TimeoutExpired, OSError) as exc:
            rcs.append({"out": a, "in": b, "exit": None,
                        "err": str(exc)[:100]})
    return rcs''',
    why="S5 one adapter, one bound (the inline path's 100)")

# --- S6 ---------------------------------------------------------------------
rep("""        tapf2 = Path(tmp) / "tap_plugin.wav"
        tap2 = _playback_r78_tap(
            d0, tapf2, int(PLAYBACK_R78_TONE_RATE * 3.2),
            "r78aplay_plug_tap")
        time.sleep(PLAYBACK_R78_TAP_LEAD_S)
        legs["plugin_default"] = _playback_r78_aplay(
            ["aplay", "-D", "default", str(tone)])
        _capture_r77_reap(tap2, PLAYBACK_R78_TIMEOUT_S)
        legs["plugin_default"]["tap"] = {
            "target": d0, **_playback_r78_tone_windows(tapf2)}
        if legs["plugin_default"]["exit_code"] != 0 or \\
                not legs["plugin_default"]["tap"].get("carries_tone"):
            failures.append("aplay plugin: -D default must land the "
                            "tag tone on the current default sink")
        tapf3 = Path(tmp) / "tap_pipewire.wav"
        tap3 = _playback_r78_tap(
            d0, tapf3, int(PLAYBACK_R78_TONE_RATE * 3.2),
            "r78aplay_pw_tap")
        time.sleep(PLAYBACK_R78_TAP_LEAD_S)
        legs["plugin_pipewire"] = _playback_r78_aplay(
            ["aplay", "-D", "pipewire", str(tone)])
        _capture_r77_reap(tap3, PLAYBACK_R78_TIMEOUT_S)
        legs["plugin_pipewire"]["tap"] = {
            "target": d0, **_playback_r78_tone_windows(tapf3)}
        if legs["plugin_pipewire"]["exit_code"] != 0 or \\
                not legs["plugin_pipewire"]["tap"].get("carries_tone"):
            failures.append("aplay plugin: -D pipewire must land the "
                            "tag tone on the current default sink")""",
    """        for plug in ("default", "pipewire"):
            tapf = Path(tmp) / f"tap_{plug}.wav"
            tap = _playback_r78_tap(
                d0, tapf, int(PLAYBACK_R78_TONE_RATE * 3.2),
                f"r78aplay_{plug}_tap")
            time.sleep(PLAYBACK_R78_TAP_LEAD_S)
            legs["plugin_" + plug] = _playback_r78_aplay(
                ["aplay", "-D", plug, str(tone)])
            _capture_r77_reap(tap, PLAYBACK_R78_TIMEOUT_S)
            legs["plugin_" + plug]["tap"] = {
                "target": d0, **_playback_r78_tone_windows(tapf)}
            if legs["plugin_" + plug]["exit_code"] != 0 or \\
                    not legs["plugin_" + plug]["tap"].get("carries_tone"):
                failures.append(f"aplay plugin: -D {plug} must land the "
                                "tag tone on the current default sink")""",
    why="S6 one plugin leg table (same leaves, same failure text)")

# --- S7 ---------------------------------------------------------------------
rep('''def _playback_r78_link_map():
    """`pw-link -l` as an edge set [(out_port, in_port)]. The `|->` line
    under a producer's port and the `|<-` line under a consumer's port
    encode the SAME direction (producer -> consumer), so both forms fold
    into one directed edge set."""
    out = {"links": [], "exit": None}
    try:
        proc = subprocess.run(["pw-link", "-l"], capture_output=True,
                              timeout=10)
        out["exit"] = proc.returncode
        text = proc.stdout.decode(errors="replace")
    except (subprocess.TimeoutExpired, OSError) as exc:
        out["error"] = str(exc)[:120]
        return out
    port, links = None, []''',
    '''def _playback_r78_links():
    """`pw-link -l` as an edge set [(out_port, in_port)]. The `|->` line
    under a producer's port and the `|<-` line under a consumer's port
    encode the SAME direction (producer -> consumer), so both forms fold
    into one directed edge set. An unreadable table is the empty set —
    every caller consumes edges only."""
    try:
        proc = subprocess.run(["pw-link", "-l"], capture_output=True,
                              timeout=10)
        text = proc.stdout.decode(errors="replace")
    except (subprocess.TimeoutExpired, OSError):
        return []
    port, links = None, []''',
    why="S7 dead envelope fields (exit/error read by nobody)")
rep('''    out["links"] = sorted(set(links))
    return out''',
    '''    return sorted(set(links))''',
    why="S7 the edge list is the return value")
rep('''                **_playback_r78_consumers(
                    tag, _playback_r78_link_map().get("links", [])),''',
    '''                **_playback_r78_consumers(tag, _playback_r78_links()),''',
    why="S7 call site")
rep('''                        **_playback_r78_producers(
                            ctag_a, _playback_r78_link_map().get(
                                "links", []))})''',
    '''                        **_playback_r78_producers(
                            ctag_a, _playback_r78_links())})''',
    why="S7 call site")
rep('''                        **_playback_r78_producers(
                            ctag_b, _playback_r78_link_map().get(
                                "links", []))})''',
    '''                        **_playback_r78_producers(
                            ctag_b, _playback_r78_links())})''',
    why="S7 call site")

# --- S8a --------------------------------------------------------------------
rep("""        bcls, _bl = _playback_r78_errclass(
            legs["busy_under_witness"].get("stderr", ""))""",
    """        bcls = _playback_r78_errclass(
            legs["busy_under_witness"].get("stderr", ""))[0]""",
    why="S8a dead binding")
rep("""        rcls, _rl = _playback_r78_errclass(
            legs["refuse_bogus"].get("stderr", ""))""",
    """        rcls = _playback_r78_errclass(
            legs["refuse_bogus"].get("stderr", ""))[0]""",
    why="S8a dead binding")
rep("""        acls, _al = _playback_r78_errclass(
            legs["arecord_constrain"].get("stderr", ""))""",
    """        acls = _playback_r78_errclass(
            legs["arecord_constrain"].get("stderr", ""))[0]""",
    why="S8a dead binding")
rep("""        pcls, _pl = _playback_r78_errclass(
            legs["pulse_refuse"].get("stderr", ""))""",
    """        pcls = _playback_r78_errclass(
            legs["pulse_refuse"].get("stderr", ""))[0]""",
    why="S8a dead binding")

# --- S8b --------------------------------------------------------------------
rep('''    entry["default_sink_trace"] = [
        {"leg": n, "default_sink_at_leg": legs[n].get(
            "default_sink_at_leg")}
        for n, _r, _e in PLAYBACK_R78_LATTICE if n in legs]''',
    '''    entry["default_sink_trace"] = [
        {"leg": n, "default_sink_at_leg": leg.get("default_sink_at_leg")}
        for n, leg in legs.items()]''',
    why="S8b the trace restates a per-leg leaf (one table walk, not two)")

# --- S9 ---------------------------------------------------------------------
rep('''                else:
                    target = tg.get(resolver)
                if resolver is not None and \\
                        not str(resolver).startswith("literal:") and \\
                        not target:
                    legs[name] = {"blocked": f"no {resolver} enumerated "
                                             "on this host"}
                    continue''',
    '''                else:
                    target = tg.get(resolver)
                    if not target:
                        legs[name] = {"blocked": f"no {resolver} "
                                                 "enumerated on this "
                                                 "host"}
                        continue''',
    why="S9 fold the guard into the branch that selects it")


def main():
    src = open(PATH).read()
    new = src
    for i, (old, repl, n, why) in enumerate(PATCH, 1):
        got = new.count(old)
        assert got == n, (f"patch #{i} ({why}): expected {n} occurrences, "
                          f"found {got}")
        new = new.replace(old, repl)
    open(PATH, "w").write(new)
    diff = difflib.unified_diff(src.splitlines(True), new.splitlines(True),
                                "a/corpus/fixtures/measure_audio.py",
                                "b/corpus/fixtures/measure_audio.py")
    out = "".join(diff)
    open("/tmp/r78-simpl/fold.diff", "w").write(out)
    adds = sum(1 for l in out.splitlines() if l.startswith("+")
               and not l.startswith("+++"))
    dels = sum(1 for l in out.splitlines() if l.startswith("-")
               and not l.startswith("---"))
    print(f"# batch: {len(PATCH)} replacements, +{adds} / -{dels} lines")


if __name__ == "__main__":
    main()
