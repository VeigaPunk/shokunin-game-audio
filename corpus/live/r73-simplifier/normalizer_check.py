#!/usr/bin/env python3
"""Apply the fixture's existing _tail normalizers (measure_audio.py:647-653)
verbatim to (a) a frontier pw-cat stderr line and (b) a frontier mpv log line,
to test whether the landed normalizer is sufficient for the r73 consumer arms.
"""
import re

def _tail(err):
    lines = err.strip().splitlines()
    if not lines:
        return None
    t = re.sub(r"`[^']*'", "`<input>'", lines[-1])
    t = re.sub(r" @ 0x[0-9a-fA-F]+", "", t)   # ASLR module tags
    return t[-160:]

samples = {
    "pwcat-file-txw": 'sndfile: failed to open audio file "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/round-68/txw_piperefuse.wav": File contains data in an unimplemented format.',
    "pwcat-nodaemon": "error: pw_context_connect() failed: Host is down",
    "mpv-lavf-seek": "[   0.006][v][lavf] Seek failed (Operation not permitted)",
    "mpv-lavf-found": "[   0.006][v][lavf] Found 'hcom' at score=100 size=600.",
    "mpv-exit-err": "[   0.008][i][cplayer] Exiting... (Errors when loading file)",
}
for name, s in samples.items():
    print(f"{name}: raw={s!r}")
    print(f"{name}: _tail={_tail(s)!r}")
    # the r71 convention also does a literal .replace(probe_arg, '<input>') when
    # probe_arg is known; test whether the _tail step alone leaves the path in.
    print(f"{name}: path-survives={('/home/' in (_tail(s) or ''))}, ts-survives={bool(re.search(r'\[\s*\d+\.\d+\]', _tail(s) or ''))}")
    print()
