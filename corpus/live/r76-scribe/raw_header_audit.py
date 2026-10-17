#!/usr/bin/env python3
"""r76 scribe — raw-capture header audit (read-only, no fixture, no receipt).

For every capture artifact under the given roots: parse the RIFF/WAVE header
in place and compare the DECLARED chunk sizes against the bytes actually on
disk. This is the raw side of a raw-vs-parsed audit: a consumer that dies
mid-capture can leave a header whose declared sizes disagree with the file
length (stale/placeholder header) — a parsed field derived from the header
would then disagree with the byte count.

Non-WAV files are reported by size + magic only.
"""
import hashlib
import pathlib
import struct
import sys

ROOTS = sys.argv[1:]


def sha16(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:16]


def audit(path: pathlib.Path) -> dict:
    size = path.stat().st_size
    row = {"path": str(path), "bytes": size, "sha256_16": None, "kind": None}
    if size == 0:
        row["kind"] = "EMPTY"
        row["sha256_16"] = sha16(b"")
        return row
    head = path.read_bytes()[:64]
    row["sha256_16"] = sha16(path.read_bytes()) if size <= 4 << 20 else sha16(head) + "(head-only)"
    if head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        row["kind"] = "WAVE"
        riff_size = struct.unpack("<I", head[4:8])[0]  # file size - 8
        row["riff_declared_file_bytes"] = riff_size + 8
        # walk chunks in the first 64 bytes (fmt is 16-18B, data header at 36)
        fmt = None
        data_decl = None
        off = 12
        raw = path.read_bytes()
        while off + 8 <= len(raw):
            cid = raw[off:off + 4]
            csize = struct.unpack("<I", raw[off + 4:off + 8])[0]
            if cid == b"fmt ":
                body = raw[off + 8:off + 8 + min(csize, 16)]
                if len(body) >= 16:
                    afmt, nch, rate = struct.unpack("<HHI", body[:8])
                    bits = struct.unpack("<H", body[14:16])[0]
                    fmt = {"afmt": afmt, "ch": nch, "rate": rate, "bits": bits}
            elif cid == b"data":
                data_decl = csize
                break
            off += 8 + csize + (csize & 1)
        row["fmt"] = fmt
        row["data_declared"] = data_decl
        row["data_actual"] = size - off - 8 if data_decl is not None else None
        if data_decl is not None:
            row["data_delta"] = row["data_actual"] - data_decl
        if fmt and fmt.get("rate"):
            dur = (row["data_actual"] or 0) / (fmt["rate"] * fmt["ch"] * fmt["bits"] // 8)
            row["actual_duration_s"] = round(dur, 6)
        row["header_finalized"] = (
            data_decl is not None
            and row["data_actual"] == data_decl
            and riff_size + 8 == size
        )
        row["riff_size_matches_file"] = (riff_size + 8 == size)
    else:
        row["kind"] = "RAW/OTHER"
        row["magic_hex"] = head[:8].hex()
    return row


def main() -> None:
    rows = []
    for root in ROOTS:
        p = pathlib.Path(root)
        files = sorted(p.rglob("*")) if p.is_dir() else [p]
        for f in files:
            if f.is_file():
                rows.append(audit(f))
    print(f"{'file':52s} {'bytes':>9s} {'decl':>9s} {'delta':>7s} {'dur_s':>8s} {'finalized':>9s} sha16")
    for r in rows:
        decl = r.get("data_declared")
        delta = r.get("data_delta")
        print(
            f"{r['path']:52s} {r['bytes']:9d} "
            f"{(decl if decl is not None else '-'):>9} "
            f"{(delta if delta is not None else '-'):>7} "
            f"{(r.get('actual_duration_s', '-')):>8} "
            f"{str(r.get('header_finalized', '-')):>9} {r['sha256_16']}"
        )
    print(f"\n{len(rows)} artifacts audited")


if __name__ == "__main__":
    main()
