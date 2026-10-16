#!/usr/bin/env bash
# r87 simplifier — end-to-end reproduction of every seat artifact.
# Read-only against the repo: re-pins the base, re-folds, re-proves.
# Aborts if the shipped fixture no longer matches the d1e687b9 pin
# (the fold is anchored to that blob).  Scratch writes go to $TMPDIR
# (default ~/Projects/shokunin/tmp).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEAT="$(dirname "$HERE")"
REPO="$(cd "$HERE/../../../.." && pwd)"
PIN="be31da679be229074690dc5157edcc122612560594baa8ba62a9b5ce26dd9516"
export TMPDIR="${TMPDIR:-$HOME/Projects/shokunin/tmp}"
mkdir -p "$TMPDIR"

cd "$REPO"
echo "== 1. pin the d1e687b9 blob"
got=$(sha256sum corpus/fixtures/measure_audio.py | cut -d' ' -f1)
if [ "$got" != "$PIN" ]; then
    echo "ABORT: shipped fixture sha256 $got != pin $PIN" >&2
    exit 1
fi
cp corpus/fixtures/measure_audio.py "$HERE/base-measure_audio.py"
git show d1e687b9 -- corpus/fixtures/measure_audio.py > "$HERE/r87-diff.patch"
sha256sum "$HERE/base-measure_audio.py" corpus/fixtures/measure_audio.py \
    > "$HERE/sha256.txt"
echo "   pin ok: $PIN"

echo "== 2. fold (12 exact-match edits, region-scoped)"
python3 "$HERE/fold-r87-simplifier.py" "$HERE/base-measure_audio.py" \
    "$HERE/folded/measure_audio.py" | tee "$HERE/fold-apply.txt"

echo "== 3. compile + parse the folded copy"
{ python3 -m py_compile "$HERE/folded/measure_audio.py" && echo "py_compile OK"
  python3 - "$HERE/folded/measure_audio.py" <<'EOF'
import ast, pathlib, sys
src = pathlib.Path(sys.argv[1]).read_text()
ast.parse(src)
print("ast.parse OK")
print("lines", len(src.splitlines()))
EOF
} | tee "$HERE/pycompile.txt"

echo "== 4. patch: generate, git apply --check, patch -p1 round-trip"
diff -u --label a/corpus/fixtures/measure_audio.py \
     --label b/corpus/fixtures/measure_audio.py \
     "$HERE/base-measure_audio.py" "$HERE/folded/measure_audio.py" \
     > "$SEAT/r87-simplifier.patch" || true
{ git apply --check "$SEAT/r87-simplifier.patch" && echo "git apply --check CLEAN"
  git apply --numstat "$SEAT/r87-simplifier.patch"
  sha256sum "$SEAT/r87-simplifier.patch"
} | tee "$HERE/patch-check.txt"
rm -rf "$TMPDIR/r87simp-rt"
mkdir -p "$TMPDIR/r87simp-rt/corpus/fixtures"
cp "$HERE/base-measure_audio.py" "$TMPDIR/r87simp-rt/corpus/fixtures/measure_audio.py"
( cd "$TMPDIR/r87simp-rt" && \
  patch -p1 --no-backup-if-mismatch < "$SEAT/r87-simplifier.patch" >/dev/null && \
  cmp corpus/fixtures/measure_audio.py "$HERE/folded/measure_audio.py" && \
  echo "patch -p1 round-trip BYTE-IDENTICAL" && \
  sha256sum corpus/fixtures/measure_audio.py ) | tee "$HERE/patch-check-rt.txt"

echo "== 5. static proofs"
python3 "$HERE/static-proofs.py" | tee "$HERE/static-proofs.txt"

echo "== 6. executed differentials"
python3 "$HERE/differential.py" | tee "$HERE/differential.txt"

echo "== 7. receipt census (both pinned green runs)"
python3 "$HERE/receipt-census.py" | tee "$HERE/receipt-census.txt"

echo "== 8. fixed-path lock proof (cross-TMPDIR)"
python3 "$HERE/lock-proof.py" | tee "$HERE/lock-proof.txt"

echo "== 9. CLI wiring (help flag + probe mutex)"
{ echo "== folded --help | grep pwbind"
  python3 "$HERE/folded/measure_audio.py" --help 2>&1 | grep -n 'pwbind'
  echo "== folded mutex (two probe flags)"
  python3 "$HERE/folded/measure_audio.py" --probe-pwbind-r87 --probe-pwctl-r86 >/dev/null 2>&1 || echo "rc=$?"
  echo "== base mutex (two probe flags)"
  python3 "$HERE/base-measure_audio.py" --probe-pwbind-r87 --probe-pwctl-r86 >/dev/null 2>&1 || echo "rc=$?"
} | tee "$HERE/cli-check.txt"

echo "== 10. censuses (legs / symbols / findings)"
python3 - "$REPO" "$HERE" <<'EOF' | tee "$HERE/legcensus.txt"
import json, pathlib, re, sys
repo, here = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
for run in ("20261016T070036115509Z-pwbind-r87",
            "20261016T070305393338Z-pwbind-r87"):
    j = json.loads((repo / "corpus/live/runs" / run /
                    "measurements.json").read_text())
    print("==", run)
    tot = 0
    for e in ("pwbind_modes_r87_probe", "pwbind_target_r87_probe",
              "pwbind_cli_r87_probe", "pwbind_midi_r87_probe"):
        n = len(j["measurements"][e]["legs"])
        print(f"  {e:26s} legs={n}")
        tot += n
    print("  TOTAL leg keys:", tot)
src = (here / "base-measure_audio.py").read_text().splitlines()
lo = next(i for i, l in enumerate(src)
          if l.startswith("# r87: the DEVICE-BINDING lattice"))
hi = next(i for i, l in enumerate(src)
          if l.startswith("    if args.probe_pactlmon_r85:"))
region = src[lo:hi]
print("region lines:", len(region),
      "fns:", len([l for l in region if re.match(r"def (pwbind_\w+_r87_entry|_pwbind_r87_\w+)", l)]),
      "consts:", len([l for l in region if re.match(r"PWBIND_R87_\w+ =", l)]))
print("r87 region line span:", lo + 1, hi)
EOF
python3 "$HERE/findings-evidence.py" | tee "$HERE/findings-evidence.txt"

echo "== 11. manifest (must be the LAST write: hashes every seat file)"
python3 "$HERE/make-manifest.py"
echo "ALL GREEN"
