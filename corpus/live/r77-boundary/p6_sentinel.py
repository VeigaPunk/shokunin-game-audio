"""r77 BOUNDARY probe 6 — the split sentinel: does the rotation counter ever stop?

The labrat seat was BLOCKED (no exec on that substrate), so this seat runs the
probe itself. Method: the `-m/--max-file-time` rotation path reaches the same
filename generator as the 2 GiB `0x80000000` split without writing 2 GiB per
file (a `-D null` leg free-runs, so 130 s of 8 kHz mono audio is ~2 MB).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import struct
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r77b_lib import (  # noqa: E402
    SCRATCH,
    save_receipt,
    sh,
    size_watchdog,
    spawn,
    reap,
    tmpfs_free_gb,
    wipe_scratch,
)

ROT = SCRATCH / "rot"
SPLIT = SCRATCH / "split"


def wav_fields(p):
    """(riff_magic, riff_size_field, form, data_declared, bytes)."""
    raw = Path(p).read_bytes()[:4096]
    if len(raw) < 44:
        return None
    magic = raw[:4].decode("latin1")
    rsz = struct.unpack_from("<I", raw, 4)[0]
    form = raw[8:12].decode("latin1")
    # walk to data
    pos, dsz = 12, None
    while pos + 8 <= len(raw):
        cid = raw[pos : pos + 4]
        csz = struct.unpack_from("<I", raw, pos + 4)[0]
        if cid == b"data":
            dsz = csz
            break
        pos += 8 + csz + (csz & 1)
    return {"riff_magic": magic, "riff_size_field": rsz, "form": form, "data_declared": dsz}


def main():
    wipe_scratch()
    rec = {"probe": "r77-boundary/p6-sentinel", "t0": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    ROT.mkdir(parents=True, exist_ok=True)
    SPLIT.mkdir(parents=True, exist_ok=True)

    # 1. template evidence from the binary
    s = sh(["bash", "-lc", "strings /usr/bin/arecord | grep -nE '%s-0|%02i|max-file' "], timeout=15)
    rec["strings"] = {"lines": s["out"].strip().splitlines()[:20], "rc": s["rc"]}

    # 2. counter behaviour under -m rotation (cheap: -D null free-runs)
    cmd = ["timeout", "40", "arecord", "-D", "null", "-f", "S16_LE", "-c", "1", "-r", "8000",
           "-t", "wav", "-m", "1", "-d", "130", str(ROT / "rot.wav")]
    t0 = time.monotonic()
    p = spawn(cmd)
    r = reap(p, timeout=45)
    rec["rotation_run"] = {"cmd": " ".join(cmd), "rc": r["rc"], "err": r["err"].strip()[:300],
                           "wall_s": round(time.monotonic() - t0, 3)}
    files = sorted(ROT.glob("*"))
    names = [f.name for f in files]
    rec["rotation_files"] = {
        "count": len(names),
        "names_head": names[:6],
        "names_tail": names[-6:],
        "base_name_exists": (ROT / "rot.wav").exists(),
        "total_bytes": sum(f.stat().st_size for f in files),
        "sizes_head": [f.stat().st_size for f in files[:3]],
        "sizes_tail": [f.stat().st_size for f in files[-3:]],
        "unique_sizes": sorted({f.stat().st_size for f in files}),
        "widened_past_99": any(re.search(r"-1\d\d\.wav$", n) for n in names),
        "name_at_99": [n for n in names if re.search(r"-9[89]\.wav$", n)],
        "name_at_100": [n for n in names if re.search(r"-10[01]\.wav$", n)],
    }
    for probe_name in ("rot-01.wav", "rot-09.wav", "rot-99.wav", "rot-100.wav"):
        f = ROT / probe_name
        if f.exists():
            rec["rotation_files"][f"header_{probe_name}"] = wav_fields(f)

    # 3. re-run into the SAME directory: does the counter restart (clobber) or resume?
    before = set(ROT.glob("*"))
    cmd2 = ["timeout", "20", "arecord", "-D", "null", "-f", "S16_LE", "-c", "1", "-r", "8000",
            "-t", "wav", "-m", "1", "-d", "3", str(ROT / "rot.wav")]
    p2 = spawn(cmd2)
    r2 = reap(p2, timeout=25)
    after = sorted(ROT.glob("*"))
    rec["rerun_same_dir"] = {
        "rc": r2["rc"], "err": r2["err"].strip()[:300],
        "count_before": len(before), "count_after": len(after),
        "new_names": [f.name for f in after if f not in before],
        "clobbered": (ROT / "rot-01.wav").exists(),
        "rot01_mtime": (ROT / "rot-01.wav").stat().st_mtime if (ROT / "rot-01.wav").exists() else None,
    }

    # 4. the 2 GiB split template: one bounded, watchdog-capped leg
    free = tmpfs_free_gb()
    rec["split_run"] = {"free_gb_before": free, "attempted": False}
    if free >= 6.0:
        stop = __import__("threading").Event()
        wd = size_watchdog(lambda: [str(p) for p in SPLIT.glob("*")], 1_500_000_000, stop, interval=0.02)
        cmd3 = ["timeout", "0.8", "arecord", "-D", "null", "-f", "cd", "-t", "wav", str(SPLIT / "split.wav")]
        p3 = spawn(cmd3)
        r3 = reap(p3, timeout=20)
        stop.set()
        wd.join(timeout=2)
        names3 = sorted(f.name for f in SPLIT.glob("*"))
        rec["split_run"].update(
            attempted=True, rc=r3["rc"], err=r3["err"].strip()[:200], names=names3[:12],
            count=len(names3), base_exists=(SPLIT / "split.wav").exists(),
            head_name=names3[0] if names3 else None,
            head_size=(SPLIT / names3[0]).stat().st_size if names3 else None,
            head_header=wav_fields(SPLIT / names3[0]) if names3 else None,
            free_gb_after=tmpfs_free_gb(),
            watchdog_note="truncates all but the newest rotation file; peak tmpfs use ~2.1 GB",
        )
        shutil.rmtree(SPLIT, ignore_errors=True)
    else:
        rec["split_run"]["skipped"] = f"only {free} GB free on tmpfs"

    rec["pw_record_structural"] = {
        "rotation_flags": sh(["bash", "-lc", "pw-record --help 2>&1 | grep -icE 'max-file|rotate|split'"],
                             timeout=10)["out"].strip(),
        "rf64_container_listed": "rf64" in sh(["pw-record", "--list-containers"], timeout=10)["out"],
        "rename_template_in_binary": sh(["bash", "-lc", "strings /usr/bin/pw-record | grep -cE '%s-[0-9][0-9]'"],
                                        timeout=10)["out"].strip(),
        "libsndfile_linked": sh(["bash", "-lc", "ldd /usr/bin/pw-record | grep -c libsndfile"], timeout=10)["out"].strip(),
    }

    save_receipt("probe-p6-sentinel.json", rec)
    print("strings:", rec["strings"]["lines"])
    print("rotation run:", json.dumps(rec["rotation_run"]))
    rf = rec["rotation_files"]
    print("rotation files:", json.dumps({k: v for k, v in rf.items() if k != "unique_sizes"}))
    print("  unique sizes:", rf["unique_sizes"][:6], "n_unique:", len(rf["unique_sizes"]))
    for k, v in rf.items():
        if k.startswith("header_"):
            print(" ", k, v)
    print("rerun same dir:", json.dumps(rec["rerun_same_dir"]))
    print("split run:", json.dumps(rec["split_run"]))
    print("pw-record structural:", json.dumps(rec["pw_record_structural"]))


if __name__ == "__main__":
    main()
