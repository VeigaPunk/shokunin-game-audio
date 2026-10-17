#!/usr/bin/env python3
"""r76 scribe — raw-vs-parsed cross-check of seat-local capture receipts.

Reads the seat-local JSON evidence written by the r76 scout and boundary
seats and re-measures the capture files it references *from disk*:

  * recorded byte count      vs stat().st_size
  * recorded sha256/sha16    vs a fresh hash  (files > HASH_CAP are size-only)
  * recorded WAV header      vs an independent in-place parse

No fixture run, no canonical receipt written. Read-only.
"""
import hashlib
import json
import pathlib
import struct
import sys

ROOT = pathlib.Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
HASH_CAP = 64 << 20  # don't hash > 64 MiB (the 2 GiB arecord captures)


def parse_wav(p: pathlib.Path):
    size = p.stat().st_size
    if size < 44:
        return None
    head = p.read_bytes()[:64]
    if head[:4] != b"RIFF" or head[8:12] != b"WAVE":
        return None
    riff_size = struct.unpack("<I", head[4:8])[0]
    fmt_size = struct.unpack("<I", head[16:20])[0]
    data_tag = head[36:40].decode("latin1")
    data_size = struct.unpack("<I", head[40:44])[0]
    return {
        "riff_size": riff_size,
        "fmt_size": fmt_size,
        "data_tag": data_tag,
        "data_size": data_size,
        "file_bytes": size,
        "data_actual": size - 44,
        "riff_matches": riff_size + 8 == size,
        "data_matches": data_size == size - 44,
    }


def digest(p: pathlib.Path):
    size = p.stat().st_size
    if size > HASH_CAP:
        return None, size
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest(), size


def check(path_str, rec_bytes=None, rec_sha=None, rec_wav=None, label=""):
    p = pathlib.Path(path_str)
    if not p.is_absolute():
        p = ROOT / path_str
    row = {"label": label, "path": str(p)}
    if not p.exists():
        row["status"] = "MISSING-ON-DISK"
        return row
    sha, size = digest(p)
    row["size_on_disk"] = size
    row["size_match"] = (rec_bytes is None) or (rec_bytes == size)
    row["sha_on_disk"] = sha[:16] if sha else f"<skipped:{size}B>"
    if rec_sha:
        if sha:
            row["sha_match"] = sha.startswith(rec_sha[:16]) or sha == rec_sha
        else:
            row["sha_match"] = "size-only"
    wav = parse_wav(p)
    row["wav_on_disk"] = wav
    if rec_wav and wav:
        diffs = {k: (rec_wav.get(k), wav.get(k)) for k in rec_wav if k in wav and rec_wav[k] != wav[k]}
        row["wav_field_diffs"] = diffs or "none"
    return row


def main() -> None:
    rows = []
    scout = ROOT / "corpus/live/r76-scout/runs/scout-capture-gates.json"
    if scout.exists():
        j = json.load(open(scout))
        for leg in j.get("legs", []):
            out = leg.get("out") or (leg.get("argv") or [None])[-1]
            if not out:
                continue
            rows.append(check(out, leg.get("out_bytes"), leg.get("out_sha16"), leg.get("wav"), leg.get("id", "")))
    for bpath in sorted((ROOT / "corpus/live/r76-boundary/runs").glob("*/measurements.json")):
        j = json.load(open(bpath))
        if not isinstance(j, list):
            continue
        for cell in j:
            out = cell.get("out")
            if not out:
                continue
            rows.append(check(out, None, cell.get("sha256"), cell.get("riff"), f"{bpath.parent.name}/{cell.get('cell')}"))
    ok = sum(1 for r in rows if r.get("status") != "MISSING-ON-DISK" and r.get("size_match") and r.get("sha_match", True) is not False)
    print(f"{len(rows)} referenced captures; {ok} size+sha agree\n")
    for r in rows:
        flag = "OK "
        if r.get("status") == "MISSING-ON-DISK":
            flag = "MISS"
        elif not r.get("size_match") or r.get("sha_match") is False or r.get("wav_field_diffs") not in (None, "none"):
            flag = "DIFF"
        print(f"{flag} {r['label'][:44]:44s} {r['path'].split('/')[-1][:34]:34s} "
              f"disk={r.get('size_on_disk')} rec_match={r.get('size_match')} sha_match={r.get('sha_match')} "
              f"wavdiff={r.get('wav_field_diffs')}")
        if r.get("wav_on_disk"):
            w = r["wav_on_disk"]
            if not (w["riff_matches"] and w["data_matches"]):
                print(f"      on-disk header UNFINALIZED: riff_size={w['riff_size']} "
                      f"(file {w['file_bytes']}) data_size={w['data_size']} data_actual={w['data_actual']}")


if __name__ == "__main__":
    main()
