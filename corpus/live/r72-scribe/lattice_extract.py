#!/usr/bin/env python3
"""r72-scribe: read-only extraction + provenance audit for the 3-decoder lattice.

Sources (all pre-existing artifacts; nothing is re-measured here):
  1. corpus/live/frontier-sndfile/runs/prior-verdicts.tsv
     (frontier seat's sox+ffmpeg per-arm extract; every row is re-checked
      against the committed receipt named in its own `receipt` column)
  2. corpus/live/frontier-sndfile/runs/sndfile-matrix.json
     (frontier libsndfile 13-member x 4-arm ctypes matrix)
  3. corpus/live/r72-reviewer/sndfile-matrix.json
     (reviewer seat's independent libsndfile matrix, 9 members x 4 arms;
      cross-check only, sibling scratch)

Writes (into corpus/live/r72-scribe/ only):
  lattice-verified.tsv, checks.txt
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # audio-shokunin/
OUT = Path(__file__).resolve().parent
RUNS = ROOT / "corpus/live/runs"
ARMS = ("file", "stdin_pipe", "redirected_fd", "fifo_path")
CANONICAL = [
    "dec_act", "dec_hcom", "posttable", "txw_piperefuse",
    "extsuffix_wav", "extsuffix_bin", "extsuffix_txw", "extsuffix_f32",
    "extsuffix_snd",
]

checks = []


def log(line):
    checks.append(line)


def sf_accept(entry):
    return bool(entry.get("read_frames"))


# ---- 1. prior-verdicts.tsv rows vs the committed receipts they cite ----
rows = list(csv.DictReader(open(ROOT / "corpus/live/frontier-sndfile/runs/prior-verdicts.tsv"),
                           delimiter="\t"))
log(f"prior-verdicts.tsv rows: {len(rows)}")
rec_cache = {}
mismatch = 0
for row in rows:
    rid = row["receipt"]
    if rid not in rec_cache:
        rec_cache[rid] = json.load(open(RUNS / rid / "measurements.json"))["measurements"]
    m = rec_cache[rid]
    if row["decoder"] == "sox":
        def pmatch(v):
            pm = v.get("pair_member") or ""
            return pm == row["member"] or pm == row["member"] + "_nomatch" or row["member"] in pm
        hit = next(v for k, v in m.items() if isinstance(v, dict) and pmatch(v))
        axis = hit["transport_axis"][row["arm"]]
        got = (axis.get("sox_detected_format"), axis.get("exit_code"),
               axis.get("samples_read"), axis.get("error"))
        exp = (None if row["detected"] == "None" else row["detected"], int(row["exit"]),
               None if row["samples"] == "None" else int(row["samples"]),
               None if row["error"] == "None" else row["error"])
    else:
        hit = next(v for k, v in m.items()
                   if isinstance(v, dict) and k.endswith("_r71_probe")
                   and (v.get("pair_member") == row["member"]
                        or v.get("pair_member") == row["member"] + "_nomatch"
                        or row["member"] in (v.get("pair_member") or "")))
        axis = hit["transport_axis"][row["arm"]]
        got = (axis.get("ffprobe_format"), axis.get("ffmpeg_exit"), axis.get("ffmpeg_error"))
        exp = (None if row["detected"] == "None" else row["detected"], int(row["exit"]),
               None if row["error"] == "None" else row["error"])
    if got != exp:
        mismatch += 1
        log(f"MISMATCH {row['member']} {row['decoder']} {row['arm']}: tsv={exp} receipt={got}")
log(f"prior-verdicts rows verified against cited receipts: {len(rows)-mismatch}/{len(rows)} (mismatches={mismatch})")

# ---- 2. sndfile matrix: frontier vs reviewer (9 canonical members) ----
fmat = json.load(open(ROOT / "corpus/live/frontier-sndfile/runs/sndfile-matrix.json"))
rmat = json.load(open(ROOT / "corpus/live/r72-reviewer/sndfile-matrix.json"))["members"]
sf_diffs = 0
for mem in CANONICAL:
    for arm in ARMS:
        fa = fmat[mem]["arms"][arm]
        ra = rmat[mem]["arms"][arm]
        fv = (f"READ{fa.get('read_frames')}" if fa.get("read_frames") else f"REJ:{fa.get('error')}",
              fa.get("format_name"))
        rv = (f"READ{ra.get('read_frames')}" if ra.get("read_frames") else f"REJ:{ra.get('error')}",
              ra.get("format_name"))
        if fv != rv:
            sf_diffs += 1
            log(f"SNDFILE DIFF {mem} {arm}: frontier={fv} reviewer={rv}")
log(f"libsndfile frontier-vs-reviewer cells: {len(CANONICAL)*4 - sf_diffs}/{len(CANONICAL)*4} identical (diffs={sf_diffs})")

# ---- 3. build verified lattice ----
by = {}
for row in rows:
    by.setdefault(row["member"], {}).setdefault(row["arm"], {})[row["decoder"]] = row
lattice = []
for mem in CANONICAL:
    for arm in ARMS:
        s = by[mem][arm]["sox"]
        f = by[mem][arm]["ffmpeg"]
        sf = fmat[mem]["arms"][arm]
        lattice.append({
            "member": mem, "arm": arm,
            "sox": ("det=%s exit=%s samples=%s err=%s" % (
                s["detected"], s["exit"], s["samples"], s["error"])),
            "ffmpeg": ("fmt=%s dec_exit=%s err=%s" % (
                f["detected"], f["exit"], f["error"])),
            "sndfile": ("%s read=%s err=%s" % (
                sf.get("format_name"), sf.get("read_frames"), sf.get("error"))),
            "sox_accept": int(s["exit"] == "0" and s["samples"] != "None"),
            "ffmpeg_accept": int(f["exit"] == "0"),
            "sndfile_accept": int(sf_accept(sf)),
        })
with open(OUT / "lattice-verified.tsv", "w") as fh:
    fh.write("member\tarm\tsox\tffmpeg\tsndfile\tsox_accept\tffmpeg_accept\tsndfile_accept\n")
    for r in lattice:
        fh.write("\t".join(str(r[k]) for k in
                           ("member", "arm", "sox", "ffmpeg", "sndfile",
                            "sox_accept", "ffmpeg_accept", "sndfile_accept")) + "\n")

# ---- 4. acceptance classes over the 36 cells ----
sox_only, sf_only, ff_only, all3, none3 = [], [], [], [], []
for r in lattice:
    a = (r["sox_accept"], r["ffmpeg_accept"], r["sndfile_accept"])
    tag = f"{r['member']}/{r['arm']}"
    if a == (1, 0, 0):
        sox_only.append(tag)
    elif a == (0, 0, 1):
        sf_only.append(tag)
    elif a == (0, 1, 0):
        ff_only.append(tag)
    elif a == (1, 1, 1):
        all3.append(tag)
    elif a == (0, 0, 0):
        none3.append(tag)
    else:
        log(f"OTHER accept-pattern {tag}: sox={a[0]} ffmpeg={a[1]} sndfile={a[2]}")
log("sox-only cells: " + (", ".join(sox_only) or "none"))
log("sndfile-only cells: " + (", ".join(sf_only) or "none"))
log("ffmpeg-only cells: " + (", ".join(ff_only) or "none"))
log("all-three cells: " + ", ".join(all3))
log("all-reject cells: " + ", ".join(none3))

(OUT / "checks.txt").write_text("\n".join(checks) + "\n")
print("\n".join(checks))
sys.exit(0 if mismatch == 0 and sf_diffs == 0 else 1)
