#!/usr/bin/env bash
# r97-boundary private instance teardown. Kills ONLY this seat's pid files
# (namespace guard: the pid must belong to a process whose cmdline mentions this
# seat dir, else the kill is refused). No namespace-blind sweeps.
set -u
SEAT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN="$SEAT/run"
TARGETS="${1:-both}"
case "$TARGETS" in wp) LIST="wp";; core) LIST="core";; *) LIST="wp core";; esac

guarded_kill() {  # $1 = pid, $2 = signal
  local pid="$1" sig="$2"
  local cmd env
  cmd="$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null || true)"
  env="$(tr '\0' '\n' < "/proc/$pid/environ" 2>/dev/null || true)"
  case "$cmd" in
    *"$SEAT"*) return 0 ;;   # own process (cmdline carries the seat path)
  esac
  # `wireplumber -c wireplumber.conf -p main` has no seat path in its cmdline;
  # its seat identity lives in the environment (XDG_CONFIG_HOME/STATE_HOME).
  case "$env" in
    *"$SEAT"*) return 0 ;;   # own process (env carries the seat path)
  esac
  echo "REFUSED kill of foreign pid $pid (cmd=$cmd)"; return 1
}

for n in $LIST; do
  f="$RUN/$n.pid"
  if [ -f "$f" ]; then
    p=$(cat "$f")
    if kill -0 "$p" 2>/dev/null; then
      if guarded_kill "$p" TERM; then
        kill -TERM -- "-$p" 2>/dev/null || kill -TERM "$p" 2>/dev/null
        for i in $(seq 1 25); do kill -0 "$p" 2>/dev/null || break; sleep 0.2; done
        if kill -0 "$p" 2>/dev/null; then
          kill -KILL -- "-$p" 2>/dev/null || kill -KILL "$p" 2>/dev/null; sleep 0.3
        fi
        echo "$n stopped (was $p)"
      fi
    else
      echo "$n not running ($p)"
    fi
    rm -f "$f"
  fi
done
exit 0
