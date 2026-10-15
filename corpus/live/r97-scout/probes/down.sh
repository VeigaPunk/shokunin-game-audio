#!/usr/bin/env bash
# r97-scout private instance teardown. Kills only this seat's pid files.
set -u
SEAT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN="$SEAT/run"
TARGETS="${1:-both}"
case "$TARGETS" in wp) LIST="wp";; core) LIST="core";; *) LIST="wp core";; esac
for n in $LIST; do
  f="$RUN/$n.pid"
  if [ -f "$f" ]; then
    p=$(cat "$f")
    if kill -0 "$p" 2>/dev/null; then
      kill -TERM -- "-$p" 2>/dev/null || kill -TERM "$p" 2>/dev/null
      for i in $(seq 1 20); do kill -0 "$p" 2>/dev/null || break; sleep 0.2; done
      kill -0 "$p" 2>/dev/null && { kill -KILL -- "-$p" 2>/dev/null || kill -KILL "$p" 2>/dev/null; sleep 0.3; }
      echo "$n stopped (was $p)"
    else
      echo "$n not running ($p)"
    fi
    rm -f "$f"
  fi
done
# sweep any stray child of this seat
if [ "${1:-both}" != "wp" ]; then
  pkill -f "$SEAT/conf/pw/r97s-pipewire.conf" 2>/dev/null && echo "swept stray core" || true
fi
exit 0
