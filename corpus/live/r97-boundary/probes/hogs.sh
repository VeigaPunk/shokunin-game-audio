#!/usr/bin/env bash
# r97-boundary load generator. Starts N of THIS seat's own CPU hogs, records
# their pids in run/hogs.pid, and can only kill those recorded pids (each kill
# is namespace-guarded: the pid's cmdline must mention the seat marker).
# NEVER touches foreign processes (the host already carries foreign `yes` hogs).
# Usage: hogs.sh start [N] | stop | count
set -u
SEAT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN="$SEAT/run"
PIDFILE="$RUN/hogs.pid"
mkdir -p "$RUN"

case "${1:-count}" in
  start)
    N="${2:-12}"
    : > "$PIDFILE"
    for i in $(seq 1 "$N"); do
      setsid bash -c "exec -a r97b_hog yes > /dev/null" &
      echo $! >> "$PIDFILE"
    done
    sleep 0.4
    echo "started $(wc -l < "$PIDFILE") r97b hogs; loadavg=$(cat /proc/loadavg)"
    ;;
  stop)
    if [ -f "$PIDFILE" ]; then
      for p in $(cat "$PIDFILE"); do
        cmd="$(tr '\0' ' ' < "/proc/$p/cmdline" 2>/dev/null || true)"
        case "$cmd" in
          *r97b_hog*) kill -KILL "$p" 2>/dev/null && echo "killed r97b hog $p" ;;
          *) [ -n "$cmd" ] && echo "REFUSED kill of pid $p (cmd=$cmd)" ;;
        esac
      done
      rm -f "$PIDFILE"
    fi
    echo "hogs stopped; loadavg=$(cat /proc/loadavg)"
    ;;
  count)
    n=0
    if [ -f "$PIDFILE" ]; then
      for p in $(cat "$PIDFILE"); do kill -0 "$p" 2>/dev/null && n=$((n+1)); done
    fi
    echo "$n"
    ;;
esac
