#!/usr/bin/env python3
"""r77-baseline post-replay integrity checks.
 (a) the env's probed members/artifacts are still byte-equal to their frozen
     b0b5d4d blobs (the replay must not have mutated its own inputs);
 (b) the env receipt census (one receipt per ledger row, zero extras);
 (c) the committed ledger-r71.tsv blob is unchanged vs the frozen commit.
Writes post-replay-fixture-check.txt + receipt-shas.txt.
"""
import subprocess
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ENV = HERE / "measure-env" / "corpus"
FROZEN = "b0b5d4d5c8bfd3356fb6c761cae7f40d0978d588"
CHECK = [
    "artifacts/stem_sections.wav",
    "artifacts/stem_layer.wav",
    "artifacts/stem_layer_alt.wav",
    "artifacts/stem_layer_third.wav",
    "artifacts/ambience.wav",
    "artifacts/ambience_alt.wav",
    "artifacts/movement.wav",
    "artifacts/impact.wav",
    "artifacts/ui.wav",
    "artifacts/ui_alt.wav",
]


def git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True).stdout


def main():
    out = [f"frozen {FROZEN}"]
    n_eq = 0
    for rel in CHECK:
        p = ENV / rel
        got = sha256(p.read_bytes()).hexdigest() if p.is_file() else "MISSING"
        want = sha256(git("show", f"{FROZEN}:corpus/{rel}")).hexdigest()
        ok = got == want
        n_eq += ok
        out.append(f"{'EQUAL' if ok else 'DIFF'} {rel} {got}")
    out.append(f"post-replay fixture check: {n_eq}/{len(CHECK)} EQUAL")
    Path(HERE / "post-replay-fixture-check.txt").write_text("\n".join(out) + "\n")

    rows = []
    for line in (HERE / "ledger-r77-baseline.tsv").read_text().splitlines():
        p = line.split("\t")
        rp = Path(p[2])
        s = sha256(rp.read_bytes()).hexdigest() if rp.is_file() else "MISSING"
        rows.append(f"{s}  {p[2]}")
    Path(HERE / "receipt-shas.txt").write_text("\n".join(rows) + "\n")
    env_receipts = sorted((ENV / "live" / "runs").glob("*/measurements.json"))
    out.append(f"env receipts on disk={len(env_receipts)} ledger rows="
               f"{len(rows)}")

    lr = "corpus/live/r70-author/ledger-r71.tsv"
    blob_now = git("rev-parse", f"HEAD:{lr}").decode().strip()
    blob_frozen = git("rev-parse", f"{FROZEN}:{lr}").decode().strip()
    body = git("show", f"{FROZEN}:{lr}")
    out.append(f"ledger-r71.tsv blob frozen={blob_frozen} HEAD={blob_now} "
               f"sha256={sha256(body).hexdigest()}")
    Path(HERE / "post-replay-fixture-check.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
