#!/usr/bin/env python3
"""r68 baseline: frozen before-state replay of the lane's 112-command ledger.

Runs the exact MODES list from r67-author/run_ledger.py (verbatim order: the
prior 102 + the ten r67 transport modes at positions 02-11) against the
git-archive HEAD (bd5e1fe) extraction at ./frozen, NOT the live worktree.
The frozen tree was extracted with all corpus/live/r*-baseline members and
any node_modules excluded (archive-manifest.txt / archive-excluded.txt).
measure_audio.py is __file__-anchored (ROOT=parents[1]=frozen/corpus), so all
fixture inputs (live/round-65|66 pair_*.wav included) and receipt writes
resolve inside the frozen tree; the canonical repo's corpus/live/runs/ is
untouched by this replay. MODES equality with the committed run_ledger.py is
assert-checked at startup (import of the frozen copy).

Per-row ledger: ledger-r68-baseline.tsv  (idx \t exit \t receipt \t failsum)
Per-command captures: out/{NN}.{stdout,stderr} (NN = 01..112, zero-padded 2)
Run-dir census: runs-before.txt / runs-after.txt / runs-new.txt
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TREE = HERE / "frozen"
MEASURE = TREE / "corpus" / "fixtures" / "measure_audio.py"
RUN_LEDGER = TREE / "corpus" / "live" / "r67-author" / "run_ledger.py"
TSV = HERE / "ledger-r68-baseline.tsv"
OUT = HERE / "out"
RUNS = TREE / "corpus" / "live" / "runs"

# verbatim copy of MODES from corpus/live/r67-author/run_ledger.py (HEAD bd5e1fe)
MODES = [
    "",                                            # 01 normal
    "--probe-transport-preempt-act-r67",           # 02 NEW  (act: file decode | redir EOF | pipe+fifo au-magic)
    "--probe-transport-preempt-gsrt-r67",          # 03 NEW  (gsrt: seekable EOF | nonseekable invalid-format)
    "--probe-transport-preempt-hcom-r67",          # 04 NEW  (hcom: invariant bad-compression-type)
    "--probe-transport-preempt-both-r67",          # 05 NEW  (gsrt-first-match: same fork as preempt-gsrt)
    "--probe-transport-dec-hcom-r67",              # 06 NEW  (hcom: invariant decode 9 — the control)
    "--probe-transport-dec-act-r67",               # 07 NEW  (act: file decode 278 | redir EOF | pipe+fifo au-magic)
    "--probe-transport-lengate-gsrt-24-r67",       # 08 NEW  (wav: invariant fmt-fail)
    "--probe-transport-lengate-gsrt-25-r67",       # 09 NEW  (gsrt: seekable EOF | nonseekable missing-name)
    "--probe-transport-lengate-hcom-131-r67",      # 10 NEW  (wav: invariant decode 43)
    "--probe-transport-lengate-hcom-132-r67",      # 11 NEW  (hcom: invariant premature-EOF)
    "--probe-ui-dec-hcom-r66",
    "--probe-ui-dec-act-r66",
    "--probe-ui-lengate-gsrt-24-r66",
    "--probe-ui-lengate-gsrt-25-r66",
    "--probe-ui-lengate-hcom-131-r66",
    "--probe-ui-lengate-hcom-132-r66",
    "--probe-ui-preempt-act-r65",
    "--probe-ui-preempt-gsrt-r65",
    "--probe-ui-preempt-hcom-r65",
    "--probe-ui-preempt-both-r65",
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
assert len(MODES) == 112, len(MODES)

# verify verbatim against the committed r67 runner inside the frozen tree
_spec = importlib.util.spec_from_file_location("run_ledger_r67", RUN_LEDGER)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
assert _mod.MODES == MODES, "MODES drift vs frozen r67-author/run_ledger.py"


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
            print(f"{i:03d} exit={proc.returncode} {flag or 'normal'}", file=sys.stderr)
    after = census("after")
    new = sorted(after - before)
    (HERE / "runs-new.txt").write_text("\n".join(new) + ("\n" if new else ""))
    print(f"runs: before={len(before)} after={len(after)} new={len(new)}", file=sys.stderr)


if __name__ == "__main__":
    main()
