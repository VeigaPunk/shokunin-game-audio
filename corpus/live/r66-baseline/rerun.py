#!/usr/bin/env python3
"""r66 baseline: frozen before-state replay of the lane's 96-command ledger.

Runs the exact MODES list from r65-author/run_ledger.py (verbatim order: the
prior 92 + the four r65 preempt modes at positions 2-5) against the
git-archive HEAD (30e5e32) extraction at ./frozen, NOT the live worktree.
The frozen tree was extracted with all corpus/live/r*-baseline members and
any node_modules excluded (archive-manifest.txt / archive-excluded.txt).
measure_audio.py is __file__-anchored (ROOT=parents[1]=frozen/corpus), so all
fixture inputs, probe wavs, and receipt writes resolve inside the frozen
tree; the canonical repo's corpus/live/runs/ is untouched by this replay.

Per-row ledger: ledger-r66-baseline.tsv  (idx \t exit \t receipt \t failsum)
Per-command captures: out/{NN}.stdout / out/{NN}.stderr
Run-dir census: runs-before.txt / runs-after.txt / runs-new.txt
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TREE = HERE / "frozen"
MEASURE = TREE / "corpus" / "fixtures" / "measure_audio.py"
TSV = HERE / "ledger-r66-baseline.tsv"
OUT = HERE / "out"
RUNS = TREE / "corpus" / "live" / "runs"

# verbatim copy of MODES from corpus/live/r65-author/run_ledger.py (HEAD 30e5e32)
MODES = [
    "",                                            # 01 normal
    "--probe-ui-preempt-act-r65",                  # 02 NEW  (uncollided control == r63 pair_route_84)
    "--probe-ui-preempt-gsrt-r65",                 # 03 NEW  (gsrt preempts act)
    "--probe-ui-preempt-hcom-r65",                 # 04 NEW  (hcom preempts act)
    "--probe-ui-preempt-both-r65",                 # 05 NEW  (gsrt preempts hcom+act)
    "--probe-ui-extensible-valid-8-r64",
    "--probe-ui-extensible-valid-9-r64",
    "--probe-ui-extensible-valid-24-r64",
    "--probe-ui-extensible-valid-25-r64",
    "--probe-ui-extensible-valid-56-r64",
    "--probe-ui-extensible-valid-57-r64",
    "--probe-ui-route-act-84-r63",
    "--probe-ui-route-act-00-r63",
    "--probe-ui-extensible-valid-24-r62",
    "--probe-ui-extensible-valid-32-r62",
    "--probe-ui-extensible-valid-17-r61",
    "--probe-ui-extensible-valid-16-r61",
    "--probe-ui-extensible-valid-0-r60",
    "--probe-ui-extensible-valid-16-r60",
    "--probe-ui-extensible-valid-13-r59",
    "--probe-ui-extensible-valid-16-r59",
    "--probe-ui-extensible-valid-14-r58",
    "--probe-ui-extensible-valid-16-r58",
    "--probe-ui-extensible-valid-15",
    "--probe-ui-extensible-valid-16",
    "--probe-ui-extensible-mask-zero",
    "--probe-ui-extensible-mask-center",
    "--probe-ui-extensible-pcm16",
    "--probe-ui-standard-pcm16-r55",
    "--probe-ui-pcm32",
    "--probe-ui-pcm16-r54",
    "--probe-ui-float32",
    "--probe-ui-pcm16-r53",
    "--probe-ui-pcm8",
    "--probe-ui-pcm16-r52",
    "--probe-ui-pcm24",
    "--probe-ui-pcm16",
    "--probe-ui-channel-stereo",
    "--probe-ui-channel-mono",
    "--probe-ui-rate-48001",
    "--probe-ui-rate-48000-r49",
    "--probe-ui-rate-47999",
    "--probe-ui-rate-48000",
    "--probe-ui-upper-centroid-below",
    "--probe-ui-upper-centroid-above",
    "--probe-ui-absolute-centroid-below",
    "--probe-ui-absolute-centroid-above",
    "--probe-ui-lower-tolerance-5713",
    "--probe-ui-lower-tolerance-5711",
    "--probe-ui-tolerance-5807",
    "--probe-ui-tolerance-5809",
    "--probe-ui-crest-46",
    "--probe-ui-crest-47",
    "--probe-ui-peak-31129",
    "--probe-ui-peak-31130",
    "--probe-outer-slope-32",
    "--probe-outer-slope-33",
    "--probe-outer-endpoint-983",
    "--probe-outer-endpoint-984",
    "--probe-ambience-orientation-forward",
    "--probe-ambience-orientation-reverse",
    "--probe-ambience-centroid-above",
    "--probe-ambience-centroid-below",
    "--probe-ui-mixed-pass",
    "--probe-ui-joint-below",
    "--probe-ui-orientation-forward",
    "--probe-ui-orientation-reverse",
    "--probe-ui-lower-centroid-below",
    "--probe-ui-lower-centroid-above",
    "--probe-ui-centroid-below",
    "--probe-ui-centroid-above",
    "--probe-ui-duration-below",
    "--probe-ui-duration-at",
    "--probe-ui-clone",
    "--probe-layer-third-join-edge-pass",
    "--probe-layer-third-join-edge-fail",
    "--probe-layer-third-join",
    "--probe-layer-third-slope-edge-pass",
    "--probe-layer-third-slope-edge-fail",
    "--probe-layer-third-slope",
    "--probe-layer-alt-reverse",
    "--probe-layer-alt-slope",
    "--probe-layer-alt-join",
    "--probe-layer-alt-flat",
    "--probe-layer-slope",
    "--probe-layer-join",
    "--probe-flat",
    "--probe-layer-flat",
    "--probe-slope",
    "--probe-failing",
    "--probe-invalid",
    "", "", "", "", "",                            # 5 trailing normals
]
assert len(MODES) == 96, len(MODES)


def census(tag):
    names = sorted(p.name for p in RUNS.iterdir() if p.is_dir()) if RUNS.is_dir() else []
    (HERE / f"runs-{tag}.txt").write_text("\n".join(names) + ("\n" if names else ""))
    return set(names)


def main():
    before = census("before")
    OUT.mkdir(exist_ok=True)
    rows = []
    with TSV.open("w") as fh:
        for i, flag in enumerate(MODES, 1):
            cmd = ["python3", str(MEASURE)] + ([flag] if flag else [])
            proc = subprocess.run(cmd, capture_output=True, text=True, cwd=TREE)
            (OUT / f"{i:02d}.stdout").write_text(proc.stdout)
            (OUT / f"{i:02d}.stderr").write_text(proc.stderr)
            receipt = "-"
            failsum = "none"
            try:
                payload = json.loads(proc.stdout.strip().splitlines()[-1])
                receipt = payload.get("receipt", "-")
                fails = payload.get("failures", {})
                if fails:
                    failsum = "; ".join(f"{k}: {'; '.join(v) if isinstance(v, list) else v}"
                                        for k, v in fails.items())
            except Exception:
                failsum = "UNPARSED:" + proc.stdout.strip()[-120:] + " | " + proc.stderr.strip()[-120:]
            fh.write(f"{i:02d}\t{proc.returncode}\t{receipt}\t{failsum}\n")
            fh.flush()
            rows.append((i, proc.returncode, receipt, failsum))
            print(f"{i:02d} exit={proc.returncode} {flag or 'normal'}", file=sys.stderr)
    after = census("after")
    new = sorted(after - before)
    (HERE / "runs-new.txt").write_text("\n".join(new) + ("\n" if new else ""))
    print(f"runs: before={len(before)} after={len(after)} new={len(new)}", file=sys.stderr)


if __name__ == "__main__":
    main()
