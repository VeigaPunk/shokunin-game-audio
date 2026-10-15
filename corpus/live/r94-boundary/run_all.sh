#!/usr/bin/env bash
# r94-boundary — sequential passes.  Writes only under corpus/live/r94-boundary/.
#
# Order matters: both "quiet-ish" measurements are taken before any own hog is
# started, so the quiet baseline is not contaminated by this seat's own hogs.
# R94B_SETTLE lets the 1-min loadavg decay after a previous run of this script.
set -euo pipefail
cd "$(dirname "$0")"
export LC_ALL=C
SETTLE=${R94B_SETTLE:-90}

echo "== prep (stimulus + cross-seat output sha smoke) =="
R94B_PASS=quiet R94B_HOGS=0 python3 probes/r94b_driver.py prep

echo "== settle ${SETTLE}s so the 1-min loadavg reflects only foreign load =="
sleep "${SETTLE}"
echo "  loadavg at quiet start: $(cat /proc/loadavg)"

echo "== quiet-ish pass: own hogs = 0 (foreign load recorded, not controlled) =="
R94B_PASS=quiet R94B_HOGS=0 python3 probes/r94b_driver.py all

echo "== focused claim probe, quiet (r94-scout §1.5 '-v rejects at -130 dB') =="
R94B_PASS=quiet R94B_HOGS=0 python3 probes/r94b_r5_probe.py

echo "== load pass: own hogs = 16 held across witness/laws/axes/conc (90 s warmup) =="
R94B_PASS=load R94B_HOGS=16 R94B_HOG_WARMUP=90 python3 probes/r94b_driver.py all

echo "== focused claim probe, under load =="
R94B_PASS=load R94B_HOGS=16 R94B_HOG_WARMUP=90 python3 probes/r94b_r5_probe.py

echo "== census =="
R94B_PASS=final R94B_HOGS=0 python3 probes/r94b_driver.py census

echo "done"
