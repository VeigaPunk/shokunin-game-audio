#!/usr/bin/env python3
"""r76 scribe — raw capture-header audit v3 (chunk-walking; read-only).

v2 assumed the data chunk sits at offset 36, which is false for lavf-written
WAVs (ffmpeg emits LIST/INFO before data). v3 walks the chunk table properly:

    RIFF <size> WAVE ( <id> <size> <body...> )*

and reports, per file:
  * declared RIFF size vs file size
  * the chunk sequence (id/size/offset)
  * the data chunk's declared size vs the bytes actually after its header
  * a `finalized` verdict = riff_size+8 == filesize AND data_declared == tail bytes

That is the raw side of the raw-vs-parsed audit: a consumer killed mid-capture
leaves a header whose declared sizes disagree with the file, so any parsed
duration derived from the header contradicts the byte count.

No fixture run. No receipt written. Read-only.
"""
import hashlib
import pathlib
import struct
import sys

TSV = [
    "path", "bytes", "sha16", "riff_declared_file", "riff_ok", "chunks",
    "data_declared", "data_tail_bytes", "data_ok", "finalized", "dur_s_at_declared",
]


def audit(p: pathlib.Path) -> dict:
    size = p.stat().st_size
    row = {"path": str(p), "bytes": size, "sha16": None}
    if size == 0:
        row.update(kind="EMPTY", sha16=hashlib.sha256(b"").hexdigest()[:16])
        return row
    with p.open("rb") as fh:
        head = fh.read(12)
        if head[:4] != b"RIFF" or head[8:12] != b"WAVE":
            row.update(kind="NON-WAV", sha16=_sha(p))
            return row
        riff_size = struct.unpack("<I", head[4:8])[0]
        chunks = []
        off = 12
        data_decl = None
        data_off = None
        fmt = None
        fh.seek(off)
        while True:
            ch = fh.read(8)
            if len(ch) < 8:
                break
            cid = ch[:4].decode("latin1", "replace")
            csize = struct.unpack("<I", ch[4:8])[0]
            body_off = off + 8
            chunks.append(f"{cid}:{csize}@{off}")
            if cid == "fmt " and data_decl is None:
                body = fh.read(min(csize, 16))
                if len(body) >= 16:
                    afmt, nch, rate = struct.unpack("<HHI", body[:8])
                    bits = struct.unpack("<H", body[14:16])[0]
                    fmt = {"afmt": afmt, "ch": nch, "rate": rate, "bits": bits}
                fh.seek(body_off + csize + (csize & 1))
            elif cid == "data":
                data_decl = csize
                data_off = body_off
                break
            else:
                fh.seek(body_off + csize + (csize & 1))
            off = body_off + csize + (csize & 1)
    row.update(
        kind="WAVE", sha16=_sha(p), riff_declared_file=riff_size + 8,
        riff_ok=(riff_size + 8 == size), chunks="|".join(chunks) or "(none)",
        data_declared=data_decl,
        data_tail_bytes=(size - data_off) if data_off is not None else None,
        data_ok=(data_decl is not None and data_decl == size - data_off),
        finalized=(riff_size + 8 == size and data_decl is not None and data_decl == size - data_off),
        fmt=fmt,
    )
    if fmt and fmt["rate"] and fmt["ch"] and fmt["bits"] and data_decl is not None:
        row["dur_s_at_declared"] = round(data_decl / (fmt["rate"] * fmt["ch"] * fmt["bits"] // 8), 6)
    return row


def _sha(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()[:16]


def main() -> None:
    rows = []
    for root in sys.argv[1:]:
        rp = pathlib.Path(root)
        files = sorted(rp.rglob("*")) if rp.is_dir() else [rp]
        for f in files:
            if f.is_file():
                rows.append(audit(f))
    print("\t".join(TSV))
    for r in rows:
        print("\t".join(str(r.get(k, "-")) for k in TSV))
    print(f"# {len(rows)} artifacts", file=sys.stderr)


if __name__ == "__main__":
    main()
