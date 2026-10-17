#!/usr/bin/env python3
"""r82-simplifier fold: apply the ten proven deletions to a COPY of the
committed fixture (sha256 eb865760…). Each replacement must match exactly
once; the script aborts otherwise. Usage:
    python3 fold-r82-simplifier.py <base.py> <out.py>
Writes nothing else; prints a per-hunk APPLIED line.
"""
import sys

REPLACEMENTS = [
    # T1 — dead constant FFPW_R82_FFPLAY (0 Load refs; entry 8 uses the
    # literal "ffplay" in fbase and shutil.which("ffplay")).
    ('FFPW_R82_ANSI = re.compile(r"\\x1b\\[[0-9;]*[A-Za-z]")   '
     '# ffplay emits \\x1b[2K\nFFPW_R82_FFPLAY = "ffplay"\n',
     'FFPW_R82_ANSI = re.compile(r"\\x1b\\[[0-9;]*[A-Za-z]")   '
     '# ffplay emits \\x1b[2K\n'),
    # T2 — _ffpw_r82_last_node: `require_linked` never passed (22 call
    # sites) → the branch is dead; drop the param and the branch.
    ('def _ffpw_r82_last_node(leg, src="main", require_linked=False):\n'
     '    """The last sample\'s node leaf for `src` — the verdict surface."""\n'
     '    for s in reversed(leg.get("samples") or []):\n'
     '        for nd in (s.get("nodes") or []):\n'
     '            if src and nd.get("src") != src:\n'
     '                continue\n'
     '            if require_linked and not (nd.get("consumers") or\n'
     '                                       nd.get("producers")):\n'
     '                continue\n'
     '            return nd\n'
     '    return None\n',
     'def _ffpw_r82_last_node(leg, src="main"):\n'
     '    """The last sample\'s node leaf for `src` — the verdict surface."""\n'
     '    for s in reversed(leg.get("samples") or []):\n'
     '        for nd in (s.get("nodes") or []):\n'
     '            if src and nd.get("src") != src:\n'
     '                continue\n'
     '            return nd\n'
     '    return None\n'),
    # T3 — _ffpw_r82_shot: `env_extra` never passed (8 call sites) → the
    # env block never executes; drop param + block + env=env (env=None is
    # the Popen default anyway).
    ('def _ffpw_r82_shot(argv, env_extra=None, timeout_s=12.0):\n'
     '    """A read-only instant command (devices/sources/sinks/-h/ffprobe\n'
     '    listing) — subprocess timeout is the bound; no stream ever opens."""\n'
     '    env = None\n'
     '    if env_extra:\n'
     '        env = dict(os.environ)\n'
     '        for k, v in env_extra.items():\n'
     '            if v is None:\n'
     '                env.pop(k, None)\n'
     '            else:\n'
     '                env[k] = v\n'
     '    try:\n'
     '        proc = subprocess.run(argv, capture_output=True,\n'
     '                              timeout=timeout_s, env=env)\n',
     'def _ffpw_r82_shot(argv, timeout_s=12.0):\n'
     '    """A read-only instant command (devices/sources/sinks/-h/ffprobe\n'
     '    listing) — subprocess timeout is the bound; no stream ever opens."""\n'
     '    try:\n'
     '        proc = subprocess.run(argv, capture_output=True,\n'
     '                              timeout=timeout_s)\n'),
    # T4 — _landed_on: `taps` never passed (8 call sites) → the early
    # return is dead; drop the param and the guard.
    ('    def _landed_on(name, sink, want_target, taps=True):\n',
     '    def _landed_on(name, sink, want_target):\n'),
    ('        if not taps:\n'
     '            return\n'
     '        tdef = _tap_tone(leg, "tap_def")\n',
     '        tdef = _tap_tone(leg, "tap_def")\n'),
    # T5 — entry 6 artifact check: every leg in this entry omits
    # out_path → _ffpw_r82_leg stores "out": None → leg.get("out") or {}
    # is always {} → the condition can never be true.
    ('        out = leg.get("out") or {}\n'
     '        if out.get("exists") and (out.get("bytes") or 0) > 44:\n'
     '            failures.append(f"err {lname}: a refused leg must not "\n'
     '                            f"produce audio — {out}")\n',
     ''),
    # T6 — superseded predicate: any(rows.get(d) is None …) can only be
    # true after the per-device mismatch loop already appended a failure.
    ('    if any(rows.get(d) is None for d in want_flags):\n'
     '        failures.append("devices: a pinned audio device row is missing "\n'
     '                        f"entirely — {rows_seen[0]}")\n',
     ''),
    # T7 — dead store: d2's starred list is never recorded (d3/d4 record
    # leg["starred"]; the d2 receipt carries no `starred` key).
    ('    rows_pw, _star = _ffpw_r82_enum_rows(leg.get("out") or "")\n',
     '    rows_pw, _ = _ffpw_r82_enum_rows(leg.get("out") or "")\n'),
    # T8 — entry-2 _cap: `post` never passed (17 call sites) → the
    # `list(post or [])` argv slot is always empty; drop both.
    ('            def _cap(name, pre, src, post=None, env=None, wall=None,\n'
     '                     w=watch, tone=False):\n',
     '            def _cap(name, pre, src, env=None, wall=None,\n'
     '                     w=watch, tone=False):\n'),
    ('                    base + list(pre) + ["-i", src] + list(post or []) +\n'
     '                    ["-t", "2.0", "-c:a", "pcm_s16le", out],\n',
     '                    base + list(pre) + ["-i", src] +\n'
     '                    ["-t", "2.0", "-c:a", "pcm_s16le", out],\n'),
    # T10 — _ffpw_r82_kill_watch: sole call site is the t2 event
    # (2.0, "kill_watch", "pump") whose watch={"pump": pump} is a live
    # Popen → procs.get(arg) is never None; the `missing` leaf is dead
    # and `label` is used nowhere else.
    ('def _ffpw_r82_kill_watch(proc, label):\n'
     '    """Timed-event kill for a watch proc (the pump) — SIGKILL its pgid."""\n'
     '    if proc is None:\n'
     '        return {"missing": label}\n'
     '    if proc.poll() is not None:\n',
     'def _ffpw_r82_kill_watch(proc):\n'
     '    """Timed-event kill for a watch proc (the pump) — SIGKILL its pgid."""\n'
     '    if proc.poll() is not None:\n'),
    ('                    res = _ffpw_r82_kill_watch(procs.get(arg), arg)\n',
     '                    res = _ffpw_r82_kill_watch(procs.get(arg))\n'),
    # T11 — _ffpw_r82_tone_windows: all four call sites pass a non-empty
    # path → `if path is not None` / `if path` are always true.
    ('    path = Path(path) if path else None\n'
     '    insp = (_capture_wav_inspect(path) if path is not None\n'
     '            else {"exists": False})\n'
     '    pcm = (_playback_r78_pcm_array(path, insp) if path is not None\n'
     '           else None)\n',
     '    path = Path(path)\n'
     '    insp = _capture_wav_inspect(path)\n'
     '    pcm = _playback_r78_pcm_array(path, insp)\n'),
]

TAGS = ["T1", "T2", "T3", "T4a", "T4b", "T5", "T6", "T7", "T8a", "T8b",
        "T10a", "T10b", "T11"]


def main():
    base_path, out_path = sys.argv[1], sys.argv[2]
    text = open(base_path).read()
    assert len(TAGS) == len(REPLACEMENTS), "tag/replacement count mismatch"
    for tag, (old, new) in zip(TAGS, REPLACEMENTS):
        n = text.count(old)
        if n != 1:
            raise SystemExit(f"{tag}: pattern matched {n} times, expected 1")
        text = text.replace(old, new, 1)
        print(f"{tag}: APPLIED (1 match)")
    open(out_path, "w").write(text)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
