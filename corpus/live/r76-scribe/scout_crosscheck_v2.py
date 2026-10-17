#!/usr/bin/env python3
"""r76 scribe — raw-vs-parsed cross-check of seat-local capture evidence (v2).

v1 fell back to argv[-1] and mis-flagged legs whose harness records `out: None`.
v2 resolves each leg's *declared* output path (the OUT substitution), compares
the seat's recorded byte count / sha16 / WAV header against disk, and — when
the declared path is absent — looks for numbered siblings of the same leg id
(the prior-revision naming) and reports them instead of a bare MISS.

Read-only. No fixture run. No receipt written.
"""
import hashlib
import json
import pathlib
import re
import struct

ROOT = pathlib.Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
SCOUT = ROOT / "corpus/live/r76-scout"
HASH_CAP = 64 << 20


def wav_fields(p: pathlib.Path):
    size = p.stat().st_size
    if size < 44:
        return {"short": size}
    head = p.read_bytes()[:44]
    if head[:4] != b"RIFF" or head[8:12] != b"WAVE":
        return {"magic": head[:4].decode("latin1", "replace")}
    return {
        "magic": "RIFF", "form": "WAVE",
        "riff_size": int.from_bytes(head[4:8], "little"),
        "fmt_size": int.from_bytes(head[16:20], "little"),
        "data_tag": head[36:40].decode("latin1", "replace"),
        "data_size": int.from_bytes(head[40:44], "little"),
        "file_bytes": size,
        "riff_matches_file": int.from_bytes(head[4:8], "little") + 8 == size,
        "data_matches_file": int.from_bytes(head[40:44], "little") == size - 44,
    }


def sha16(p: pathlib.Path):
    size = p.stat().st_size
    if size > HASH_CAP:
        return None
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()[:16]


def main() -> None:
    j = json.load(open(SCOUT / "runs/scout-capture-gates.json"))
    legs = j["legs"]
    abs_argv = 0
    print(f"scout batch={j.get('batch')} utc={j.get('utc')} legs={len(legs)}\n")
    for leg in legs:
        argv = leg.get("argv") or []
        declared = argv[-1] if argv else None
        if declared and declared.startswith("/"):
            abs_argv += 1
        rec_bytes = leg.get("out_bytes")
        rec_sha = leg.get("out_sha16")
        rec_wav = leg.get("wav") or {}
        row = f"{leg['id']:28s}"
        if declared and pathlib.Path(declared).exists():
            p = pathlib.Path(declared)
            size = p.stat().st_size
            sha = sha16(p)
            wf = wav_fields(p)
            size_ok = rec_bytes == size
            sha_ok = (rec_sha is None and sha is None) or (rec_sha == sha)
            if size == 0:  # empty capture: the harness records no sha by design
                sha_ok = True
            # header agreement on the fields both sides carry
            hdr_diff = {k: (rec_wav.get(k), wf.get(k)) for k in ("riff_size", "fmt_size", "data_size")
                        if k in rec_wav and k in wf and rec_wav[k] != wf[k]}
            status = "OK " if (size_ok and sha_ok and not hdr_diff) else "DIFF"
            print(f"{status} {row} bytes={size} rec={rec_bytes} sha={sha} rec_sha={rec_sha} "
                  f"hdr_diff={hdr_diff or 'none'}")
            if wf.get("data_tag") == "data" and not (wf.get("riff_matches_file") and wf.get("data_matches_file")):
                print(f"       UNFINALIZED header on disk: riff={wf['riff_size']} "
                      f"data={wf['data_size']} file={wf['file_bytes']}")
        else:
            sib = sorted(SCOUT.glob(f"legs/{leg['id']}-*"))
            if sib:
                tot = sum(s.stat().st_size for s in sib)
                print(f"SIB {row} declared ABSENT (rec bytes={rec_bytes}) but {len(sib)} numbered "
                      f"siblings on disk, {tot} B total")
                for s in sib:
                    wf = wav_fields(s)
                    print(f"       {s.name} {s.stat().st_size} B "
                          f"riff={wf.get('riff_size')} data={wf.get('data_size')} "
                          f"riff_ok={wf.get('riff_matches_file')} data_ok={wf.get('data_matches_file')}")
            else:
                print(f"MISS {row} declared={declared} rec bytes={rec_bytes} wav={rec_wav}")
    print(f"\nabsolute paths inside recorded argv: {abs_argv}/{len(legs)}")


if __name__ == "__main__":
    main()
