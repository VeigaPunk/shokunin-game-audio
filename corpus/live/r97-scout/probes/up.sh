#!/usr/bin/env bash
# r97-scout private instance bring-up: private PipeWire core + private WirePlumber.
# NEVER touches the shared daemons: separate runtime dir => separate socket.
# Usage: up.sh [core|wp]   (default: both)
set -u
SEAT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN="$SEAT/run"
mkdir -p "$RUN"
export PIPEWIRE_RUNTIME_DIR="$RUN"
export XDG_RUNTIME_DIR="$RUN"
export XDG_CONFIG_HOME="$SEAT/conf/xdg-config"
export XDG_STATE_HOME="$SEAT/conf/xdg-state"
export XDG_DATA_HOME="$SEAT/conf/xdg-data"
## NOTE (measured r97s L1): WIREPLUMBER_CONFIG_DIR *replaces* the config search path;
## a dir without wireplumber.conf yields "no modules loaded from context.modules" and rc 1.
## Private arming therefore uses a private XDG_CONFIG_HOME (variant C).
export R97_WP_CONFIG_DIR=""
export WIREPLUMBER_DEBUG="${WIREPLUMBER_DEBUG:-2}"
export PIPEWIRE_DEBUG="${PIPEWIRE_DEBUG:-2}"
mkdir -p "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d" "$XDG_STATE_HOME" "$XDG_DATA_HOME"

start_core() {
  if [ -f "$RUN/core.pid" ] && kill -0 "$(cat "$RUN/core.pid")" 2>/dev/null; then
    echo "core already up pid=$(cat "$RUN/core.pid")"; return 0
  fi
  setsid pipewire -c "$SEAT/conf/pw/r97s-pipewire.conf" \
      >"$SEAT/runs/core.log" 2>&1 &
  echo $! > "$RUN/core.pid"
  for i in $(seq 1 40); do
    [ -S "$RUN/pipewire-0" ] && { echo "core up pid=$(cat "$RUN/core.pid") sock=$RUN/pipewire-0"; return 0; }
    sleep 0.25
  done
  echo "CORE FAILED TO COME UP"; tail -20 "$SEAT/runs/core.log"; return 1
}

start_wp() {
  if [ -f "$RUN/wp.pid" ] && kill -0 "$(cat "$RUN/wp.pid")" 2>/dev/null; then
    echo "wp already up pid=$(cat "$RUN/wp.pid")"; return 0
  fi
  setsid wireplumber -c wireplumber.conf -p "${R97_PROFILE:-main}" \
      >"$SEAT/runs/wp.log" 2>&1 &
  echo $! > "$RUN/wp.pid"
  for i in $(seq 1 60); do
    if wpctl status >/dev/null 2>&1; then
      echo "wp up pid=$(cat "$RUN/wp.pid") profile=${R97_PROFILE:-main}"; return 0
    fi
    sleep 0.25
  done
  echo "WP FAILED TO COME UP"; tail -30 "$SEAT/runs/wp.log"; return 1
}

case "${1:-both}" in
  core) start_core ;;
  wp)   start_wp ;;
  both) start_core && start_wp ;;
esac
