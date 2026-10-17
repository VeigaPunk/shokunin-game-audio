#!/usr/bin/env python3
"""r74-baseline replay: the current 123-command battery, serially, against the
env materialization (measure-env/corpus — 657 tracked files proven byte-equal
to frozen HEAD 1ba8103 via env-proofs.txt). MODE order = worktree
corpus/live/r73-author/run_ledger.py MODES verbatim (the freshest encoding of
the full committed probe surface: r72's 122 + --probe-consumers-r73 at pos 2).
Writes ledger-r74-baseline.tsv: idx \t exit \t receipt_path \t failure_summary;
per-command captures to out/{01..123}.{stdout,stderr}.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEASURE = str(HERE / "measure-env" / "corpus" / "fixtures" / "measure_audio.py")
TSV = HERE / "ledger-r74-baseline.tsv"
OUT = HERE / "out"

# corpus/live/r73-author/run_ledger.py MODES verbatim (asserted 123 there).
MODES = [
    "",                                            # 01 normal
    "--probe-consumers-r73",                       # 02 (consumer class: pw-cat + mpv 4-transport matrix, 9 members + ops)
    "--probe-sndfile-transport-r72",               # 03
    "--probe-ffprobe-transport-r71",               # 04
    "--probe-fifo-hold-ladder-r70",                # 05
    "--probe-transport-extsuffix-wav-r69",         # 06
    "--probe-transport-extsuffix-bin-r69",         # 07
    "--probe-transport-extsuffix-txw-r69",         # 08
    "--probe-transport-extsuffix-f32-r69",         # 09
    "--probe-transport-extsuffix-snd-r69",         # 10
    "--probe-transport-posttable-nomatch-r68",
    "--probe-transport-txw-piperefuse-r68",
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
assert len(MODES) == 123, len(MODES)


def main():
    with TSV.open("w") as fh:
        for i, flag in enumerate(MODES, 1):
            cmd = ["python3", MEASURE] + ([flag] if flag else [])
            proc = subprocess.run(cmd, capture_output=True, text=True)
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
            failsum = " ".join(failsum.splitlines())
            fh.write(f"{i:02d}\t{proc.returncode}\t{receipt}\t{failsum}\n")
            fh.flush()
            print(f"{i:03d} exit={proc.returncode} {flag or 'normal'}", file=sys.stderr)


if __name__ == "__main__":
    main()
