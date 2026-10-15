#!/usr/bin/env python3
"""r78-baseline prior-row stability vs the two prior canonical sets.

Prior set A = the r77-baseline Phase-1 ledger (corpus/live/r77-baseline/
ledger-r77-baseline.tsv, 126 rows) — the freshest full-battery receipt set.
The r78 battery is that ordering verbatim with --probe-capture-r77 inserted at
position 02, so the mapping is INDEX-EXACT: r78 row i+1 == r77 row i for
i in 1..126. Both row level (exit, failure summary) and receipt level are
compared on that mapping.

Prior set B = the r76-baseline ledger (corpus/live/r76-baseline/
ledger-r76-baseline.tsv, 125 rows), mode-keyed (as r77's prior_compare did).

Leaf-walk classification of every non-byte-equal pair:
  EQUAL-MOD-PATHS     every differing leaf is corpus/-anchored with equal
                      post-anchor suffix (env infix is the only delta)
  DECLARED-ENV        differing leaves confined to the named environmental set
                      (host topology change: DualSense became the default
                      source, so the r76 capture gate's parec/parecord
                      no-device legs and the arecord plugin legs no longer
                      produce the pre-change verdict)
  DECLARED-DRIFT      differing leaves confined to the declared host-drift
                      leaves (pw_capture_ports inventory, aplay stderr_tail
                      scrub window, hw-contention device legs)
  JITTER-LEAVES       differing leaves confined to the declared wall-clock
                      jitter key set
  STRUCTURE-DIFF      key sets differ
  UNDECLARED-DIFF     same structure, non-path non-jitter non-declared leaf
Writes prior-rows-stable.txt + prior-receipt-compare.tsv +
prior76-receipt-compare.tsv.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PRIOR_A = REPO / "corpus" / "live" / "r77-baseline" / "ledger-r77-baseline.tsv"
PRIOR_B = REPO / "corpus" / "live" / "r76-baseline" / "ledger-r76-baseline.tsv"
FRESH = HERE / "ledger-r78-baseline.tsv"
INFIX_A = "corpus/live/r77-baseline/measure-env/corpus/"
INFIX_B = "corpus/live/r76-baseline/measure-env/corpus/"
INFIX_F = "corpus/live/r78-baseline/measure-env/corpus/"
JITTER_KEYS = {"wall_s", "wchan", "waited_s", "delivery_window_s",
               "playback_paced", "starved_ok"}

# named environmental set — host topology change: the DualSense wireless
# controller became the default SOURCE (was: USB Audio Line source). The r76
# capture gate's device legs that encode the pre-change verdict:
#   parec_no_device / parecord_no_device  (no -d -> now resolves a default)
#   arecord_default / arecord_pipewire / arecord_unknown_pcm
ENV = [
    # (i) the no-device gate legs: a default source now resolves
    re.compile(r"gate\.parec_no_device"),
    re.compile(r"gate\.parecord_no_device"),
    # (ii) the plugin routes the new default source unblocks
    re.compile(r"gate\.arecord_(default|pipewire)"),
    re.compile(r"device_axis[^.]*\.legs\.(default|pipewire)\b"),
    # (iii) enumeration gains the DualSense source/sink/monitor/card
    re.compile(r"inventory\.(sources|monitors|default_source|pw_capture_ports|"
               r"alsa_capture_devices|alsa_plugins|sinks)"),
    re.compile(r"device_census\.playback_devices"),
    re.compile(r"viability"),
    # (iv) legs whose target now resolves to the DualSense default source
    re.compile(r"\.argv$"),
    re.compile(r"DualSense|Direct__Direct__"),
]
# declared contention classes (multi-seat probes on the shared audio stack)
CONTENTION = [
    re.compile(r"device_axis[^.]*\.legs\.(hw_first|hw_first_mono|plughw_first|sysdefault)"),
    re.compile(r"cells\.arecord_(term|kill)\.(device|argv)"),
    re.compile(r"arecord_contention"),
    re.compile(r"roundtrip.*content_witness"),
    re.compile(r"legs\.ffmpeg_alsa_t"),
    re.compile(r"gate\.ffmpeg_(alsa|pulse)_default"),
    re.compile(r"gate\.pwrecord_(auto_target|monitor_alias)"),
]
DECLARED = [
    re.compile(r"pw_capture_ports"),
    re.compile(r"stderr_tail"),
    re.compile(r"device_axis[^.]*\.legs\.sysdefault"),
    re.compile(r"legs\.ffmpeg_alsa_t"),
    re.compile(r"cells\.arecord_(term|kill)\.device"),
]


def mode_of(receipt_path):
    d = Path(receipt_path).parent.name
    return re.sub(r"^\d{8}T\d+Z-?", "", d) or "?"


def read_ledger(path):
    rows = []
    for line in path.read_text().splitlines():
        p = line.split("\t")
        if len(p) >= 4:
            rows.append({"idx": int(p[0]), "exit": p[1], "receipt": p[2],
                         "failsum": p[3], "mode": mode_of(p[2])})
    return rows


def leaves(obj, prefix=""):
    if isinstance(obj, dict):
        for k in sorted(obj):
            yield from leaves(obj[k], f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, f"{prefix}[{i}]")
    else:
        yield prefix, obj


def anchored_tail(v):
    if isinstance(v, str) and "corpus/" in v:
        return v.rsplit("corpus/", 1)[1]
    return None


def classify(fresh_bytes, prior_bytes, label, prior_infix):
    if fresh_bytes == prior_bytes:
        return f"EQUAL\t{label}", []
    try:
        f = json.loads(fresh_bytes)
        p = json.loads(prior_bytes)
    except Exception:
        return f"UNPARSEABLE\t{label}", []
    fk = dict(leaves(f))
    pk = dict(leaves(p))
    if set(fk) != set(pk):
        only_f = sorted(set(fk) - set(pk))
        only_p = sorted(set(pk) - set(fk))
        # ENV-STRUCTURE: a structural change confined to the named environmental
        # leaf set (the plugin routes now land real files where the pre-change
        # verdict was a named error) is the environmental class, not drift.
        def bucket(k):
            if re.search(r"\.failures\[\d+\]$", k):
                return "failures"
            for name, rxs in (("env", ENV), ("drift", DECLARED),
                              ("contention", CONTENTION)):
                if any(rx.search(k) for rx in rxs):
                    return name
            return "other"

        buckets = [bucket(k) for k in only_f + only_p]
        if "other" not in buckets:
            counts = {b: buckets.count(b) for b in set(buckets)}
            ftexts = [json.dumps(fk.get(k, pk.get(k)))[:120]
                      for k in only_f + only_p if bucket(k) == "failures"]
            return (f"ENV-STRUCTURE\t{label}\tonly-fresh={len(only_f)} "
                    f"only-prior={len(only_p)}\tbuckets={counts}\t"
                    f"failure-leaves={ftexts[:4]}\t"
                    f"sample={[k.split('.', 1)[1] for k in (only_f + only_p)][:6]}"), []
        others = [k for k, b in zip(only_f + only_p, buckets) if b == "other"]
        return (f"STRUCTURE-DIFF\t{label}\tonly-fresh={only_f[:5]}\t"
                f"only-prior={only_p[:5]}\tunclassified={others[:5]}"), []
    pathdiff, jitter, env, drift, cont, content = [], [], [], [], [], []
    for k in fk:
        if fk[k] == pk[k]:
            continue
        if isinstance(fk[k], str) and prior_infix in pk[k] \
                and fk[k].replace(INFIX_F, prior_infix) == pk[k]:
            pathdiff.append(k)
            continue
        fa, ca = anchored_tail(fk[k]), anchored_tail(pk[k])
        if fa is not None and ca is not None and fa == ca \
                and (INFIX_F in str(fk[k]) or prior_infix in str(pk[k])):
            pathdiff.append(k)
        elif any(rx.search(k) for rx in ENV):
            env.append(k)
        elif any(rx.search(k) for rx in DECLARED):
            drift.append(k)
        elif any(rx.search(k) for rx in CONTENTION):
            cont.append(k)
        elif k.split(".")[-1].split("[")[0] in JITTER_KEYS:
            jitter.append(k)
        else:
            content.append(k)
    if content:
        return (f"UNDECLARED-DIFF\t{label}\tkeys={content[:8]}\t"
                f"env={len(env)}\tdeclared_drift={len(drift)}\t"
                f"contention={len(cont)}\tjitter={len(jitter)}\t"
                f"path_embedded={len(pathdiff)}"), content
    if env:
        return (f"DECLARED-ENV\t{label}\tleaves={env[:10]}\t"
                f"declared_drift={len(drift)}\tcontention={len(cont)}\t"
                f"jitter={len(jitter)}\tpath_embedded={len(pathdiff)}"), []
    if drift or cont:
        return (f"DECLARED-DRIFT\t{label}\tleaves={(drift + cont)[:8]}\t"
                f"jitter={len(jitter)}\tpath_embedded={len(pathdiff)}"), []
    if jitter:
        return (f"JITTER-LEAVES\t{label}\tjitter={jitter[:8]}\t"
                f"path_embedded={len(pathdiff)}"), []
    return (f"EQUAL-MOD-PATHS\t{label}\tpath_embedded={len(pathdiff)}\t"
            f"keys={pathdiff[:6]}"), []


def compare_index_exact(prior, fresh):
    """Index-exact mapping: row 01 == row 01 (normal); row i+1 of the r78
    ledger == row i of the r77 ledger for i >= 2 (capture-r77 inserted at 02)."""
    lines, rlines = [], []
    row_cls = defaultdict(int)
    cls_count = defaultdict(int)
    undeclared = []
    by_idx = {r["idx"]: r for r in fresh}

    def target_idx(i):
        return i if i == 1 else i + 1

    for p in prior:
        f = by_idx.get(target_idx(p["idx"]))
        if f is None:
            row_cls["NO-FRESH-ROW"] += 1
            lines.append(f"NO-FRESH-ROW\tprior-{p['idx']:02d}\t{p['mode']}")
            continue
        if f["exit"] == p["exit"] and f["failsum"] == p["failsum"]:
            row_cls["ROW-STABLE"] += 1
        else:
            cls = "ROW-EXIT-ONLY" if f["exit"] == p["exit"] else "ROW-NO-MATCH"
            row_cls[cls] += 1
            lines.append(f"{cls}\tprior-{p['idx']:02d}->fresh-{f['idx']:02d}"
                         f"\t{p['mode']}\tprior_exit={p['exit']}"
                         f" fresh_exit={f['exit']}\n"
                         f"    prior_failsum='{p['failsum'][:200]}'\n"
                         f"    fresh_failsum='{f['failsum'][:200]}'")
        pp, fp = Path(p["receipt"]), Path(f["receipt"])
        if not pp.is_file():
            rlines.append(f"PRIOR-MISSING\tprior-{p['idx']:02d}\t{p['mode']}")
            cls_count["PRIOR-MISSING"] += 1
            continue
        cls, content = classify(fp.read_bytes(), pp.read_bytes(),
                                f"prior-{p['idx']:02d}->fresh-{f['idx']:02d}"
                                f"\t{p['mode']}", INFIX_A)
        cls_count[cls.split("\t")[0]] += 1
        rlines.append(cls)
        if content:
            undeclared.append(f"prior-{p['idx']:02d} {p['mode']}: {content[:8]}")
    lines.append(f"row-level (index-exact: row 01<->01, row N+1 vs r77 row N "
                 f"for N>=2): {dict(row_cls)}")
    lines.append(f"receipt-level counts: {dict(cls_count)}")
    return lines, rlines, cls_count, undeclared


def compare_mode_keyed(prior, fresh):
    lines, rlines = [], []
    row_cls = defaultdict(int)
    cls_count = defaultdict(int)
    undeclared = []
    fresh_by_mode = defaultdict(list)
    for r in fresh:
        fresh_by_mode[r["mode"]].append(r)
    for p in prior:
        cands = fresh_by_mode.get(p["mode"], [])
        if not cands:
            row_cls["NO-FRESH-ROW"] += 1
            lines.append(f"NO-FRESH-ROW\tprior-{p['idx']:02d}\t{p['mode']}")
            continue
        exact = [f for f in cands
                 if f["exit"] == p["exit"] and f["failsum"] == p["failsum"]]
        if exact:
            row_cls["ROW-STABLE"] += 1
        else:
            cls = ("ROW-EXIT-ONLY"
                   if any(f["exit"] == p["exit"] for f in cands)
                   else "ROW-NO-MATCH")
            row_cls[cls] += 1
            lines.append(f"{cls}\tprior-{p['idx']:02d}\t{p['mode']}\t"
                         f"prior_exit={p['exit']} fresh_exit={cands[0]['exit']}"
                         f"\n    prior_failsum='{p['failsum'][:200]}'"
                         f"\n    fresh_failsum='{cands[0]['failsum'][:200]}'")
        pp = Path(p["receipt"])
        if not pp.is_file():
            rlines.append(f"PRIOR-MISSING\tprior-{p['idx']:02d}\t{p['mode']}")
            cls_count["PRIOR-MISSING"] += 1
            continue
        # prefer a fresh row with the same exit, then same failsum
        best = sorted(cands, key=lambda f: (f["exit"] != p["exit"],
                                            f["failsum"] != p["failsum"]))[0]
        cls, content = classify(Path(best["receipt"]).read_bytes(),
                                pp.read_bytes(),
                                f"prior-{p['idx']:02d}\t{p['mode']}", INFIX_B)
        cls_count[cls.split("\t")[0]] += 1
        rlines.append(cls)
        if content:
            undeclared.append(f"prior-{p['idx']:02d} {p['mode']}: {content[:8]}")
    lines.append(f"row-level (mode-keyed vs r76 ledger): {dict(row_cls)}")
    lines.append(f"receipt-level counts: {dict(cls_count)}")
    return lines, rlines, cls_count, undeclared


def main():
    prior_a = read_ledger(PRIOR_A)
    prior_b = read_ledger(PRIOR_B)
    fresh = read_ledger(FRESH)
    out = [f"prior A (r77-baseline Phase-1): {len(prior_a)} rows",
           f"prior B (r76-baseline): {len(prior_b)} rows",
           f"fresh (r78-baseline): {len(fresh)} rows",
           "=== (a) index-exact vs r77-baseline Phase-1 (r78 row N+1 == r77 row N) ==="]
    a_lines, a_rec, a_cls, a_und = compare_index_exact(prior_a, fresh)
    out += a_lines
    out.append("=== (b) mode-keyed vs r76-baseline canonical ===")
    b_lines, b_rec, b_cls, b_und = compare_mode_keyed(prior_b, fresh)
    out += b_lines
    (HERE / "prior-rows-stable.txt").write_text("\n".join(out) + "\n")
    (HERE / "prior-receipt-compare.tsv").write_text("\n".join(a_rec) + "\n")
    (HERE / "prior76-receipt-compare.tsv").write_text("\n".join(b_rec) + "\n")
    if a_und:
        (HERE / "prior-undeclared-diffs.txt").write_text("\n".join(a_und) + "\n")
    print("\n".join(out))
    print(f"\n(a) receipt-level: {dict(a_cls)}")
    print(f"(b) receipt-level: {dict(b_cls)}")


if __name__ == "__main__":
    main()
