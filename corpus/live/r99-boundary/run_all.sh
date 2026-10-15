#!/usr/bin/env bash
# r99-boundary single repro path.
#   ./run_all.sh quiet   -> quiet-ish pass (0 own hogs) + LAN arms
#   ./run_all.sh load    -> load pass (14 own hogs held) + LAN arms
#   ./run_all.sh analyze -> verdicts + manifest
# Discipline: r99b_* namespace only, own PIDs only, private core + private WP.
set -u
SEAT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SEAT"
case "${1:-all}" in
  quiet)
    python3 probes/r99b_census.py
    python3 probes/r99b_driver.py cells --pass quiet
    python3 probes/r99b_driver.py lan  --pass quiet
    ;;
  load)
    python3 probes/r99b_loadrun.py --n 14 --warmup 60
    ;;
  analyze)
    python3 probes/r99b_analyze.py
    python3 probes/r99b_manifest.py
    sha256sum -c manifest.sha256 | tail -1
    ;;
  all)
    "$0" quiet && "$0" load && "$0" analyze
    ;;
  *) echo "usage: $0 {quiet|load|analyze|all}"; exit 2;;
esac
