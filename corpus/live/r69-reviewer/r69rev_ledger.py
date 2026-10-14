#!/usr/bin/env python3
"""r69 reviewer replay of the committed r68 ledger (114 rows).

Independent copy of the r68 MODES order (the order itself is under test),
invoking the committed corpus/fixtures/measure_audio.py from the lane
worktree root (~/Projects/prymeagnt/audio) so .shokunin/audio resolves
through the symlink into the canonical repo — same contract run_ledger.py used.

Writes ledger-r69rev.tsv: idx \t exit \t receipt_path \t failure_summary
"""
import json
import subprocess
import sys
from pathlib import Path

MEASURE = ".shokunin/audio/corpus/fixtures/measure_audio.py"
TSV = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r69-reviewer/ledger-r69rev.tsv")

# r68 ledger order: r67's 112 verbatim + 2 new r68 modes inserted newest-first
# at positions 2-3. Copied from committed corpus/live/r68-author/run_ledger.py.
MODES = [
    "",                                            # 01 normal
    "--probe-transport-posttable-nomatch-r68",     # 02 r68
    "--probe-transport-txw-piperefuse-r68",        # 03 r68
    "--probe-transport-preempt-act-r67",
    "--probe-transport-preempt-gsrt-r67",
    "--probe-transport-preempt-hcom-r67",
    "--probe-transport-preempt-both-r67",
    "--probe-transport-dec-hcom-r67",
    "--probe-transport-dec-act-r67",
    "--probe-transport-lengate-gsrt-24-r67",
    "--probe-transport-lengate-gsrt-25-r67",
    "--probe-transport-lengate-hcom-131-r67",
    "--probe-transport-lengate-hcom-132-r67",
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
assert len(MODES) == 114, len(MODES)


def main():
    with TSV.open("w") as fh:
        for i, flag in enumerate(MODES, 1):
            cmd = ["python3", MEASURE] + ([flag] if flag else [])
            proc = subprocess.run(cmd, capture_output=True, text=True)
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
            failsum = " ".join(failsum.splitlines())
            fh.write(f"{i:02d}\t{proc.returncode}\t{receipt}\t{failsum}\n")
            fh.flush()
            print(f"{i:03d} exit={proc.returncode} {flag or 'normal'}", file=sys.stderr)


if __name__ == "__main__":
    main()
