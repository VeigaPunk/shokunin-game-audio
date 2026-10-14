#!/usr/bin/env python3
"""r72-reviewer: the 3-decoder verdict lattice, computed from committed sox
receipts + the committed r71 ffprobe receipt + the reviewer's own libsndfile
measurement. Emits per-arm acceptance cells and the member-level coverage
classes, so the wave-11 claim can be checked against numbers rather than
prose.

Acceptance per decoder:
  sox        exit_code == 0 and samples_read > 0
  ffmpeg     ffprobe_exit == 0 and ffmpeg_exit == 0
  libsndfile format_name is not None and read_frames > 0
"""
import json, sys

sys.path.insert(0, "corpus/live/r72-reviewer")
import lattice_extract as L  # noqa: E402

ARMS = L.ARMS
MEMBERS = list(L.MEMBER_MODES)


def sox_ok(a):
    return a["exit_code"] == 0 and (a["samples_read"] or 0) > 0


def ff_ok(a):
    return a["ffprobe_exit"] == 0 and a["ffmpeg_exit"] == 0


def sf_ok(a):
    return a["format_name"] is not None and (a["read_frames"] or 0) > 0


def main():
    sox, ff, sf = L.sox_rows(), L.ffmpeg_rows(), L.sndfile_rows()
    cells = {}
    for m in MEMBERS:
        for a in ARMS:
            cells[(m, a)] = {
                "sox": sox_ok(sox[m]["arms"][a]),
                "ffmpeg": ff_ok(ff[m]["arms"][a]),
                "sndfile": sf_ok(sf[m]["arms"][a]),
            }
    counts = {d: sum(1 for c in cells.values() if c[d]) for d in ("sox", "ffmpeg", "sndfile")}
    print(f"# accepted arm-cells (of {len(cells)}): {counts}")

    print("\n## per-arm acceptance cells")
    print("member\tarm\tsox\tffmpeg\tsndfile\tclass")
    for m in MEMBERS:
        for a in ARMS:
            c = cells[(m, a)]
            key = "".join(d[0] for d in ("sox", "ffmpeg", "sndfile") if c[d]) or "none"
            print(f"{m}\t{a}\t{int(c['sox'])}\t{int(c['ffmpeg'])}\t{int(c['sndfile'])}\t{key}")

    print("\n## member-level coverage class (arm-qualified)")
    for m in MEMBERS:
        arms = {d: [a for a in ARMS if cells[(m, a)][d]] for d in ("sox", "ffmpeg", "sndfile")}
        if all(arms[d] == list(ARMS) for d in arms):
            cls = "all-three/all-arms"
        elif any(arms.values()) and not any(arms["sox"]) and not any(arms["ffmpeg"]):
            cls = "sndfile-only"
        elif any(arms.values()) and not any(arms["sndfile"]) and not any(arms["ffmpeg"]):
            cls = "sox-only"
        elif not any(arms.values()):
            cls = "none-accept"
        else:
            cls = "mixed"
        print(f"{m}\t{cls}\t" + " ".join(f"{d}={arms[d]}" for d in ("sox", "ffmpeg", "sndfile")))

    print("\n## private cells per decoder (accepted by exactly one)")
    for d in ("sox", "ffmpeg", "sndfile"):
        priv = [(m, a) for (m, a) in cells if cells[(m, a)][d]
                and sum(cells[(m, a)].values()) == 1]
        print(f"{d}: {priv}")
    print("\n## pairs accepted by exactly two")
    for pair in (("sox", "ffmpeg"), ("sox", "sndfile"), ("ffmpeg", "sndfile")):
        sel = [(m, a) for (m, a) in cells
               if all(cells[(m, a)][d] for d in pair)
               and sum(cells[(m, a)].values()) == 2]
        print(f"{pair}: {sel}")
    print("\n## accepted by all three")
    print([(m, a) for (m, a) in cells if all(cells[(m, a)].values())])
    print("\n## rejected by all three")
    print([(m, a) for (m, a) in cells if not any(cells[(m, a)].values())])


if __name__ == "__main__":
    main()
