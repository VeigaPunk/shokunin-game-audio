#!/usr/bin/env bash
# r81-baseline env/toolchain + host-state census at freeze time.
set -u
cd /home/vgpnk/Projects/shokunin/audio-shokunin
OUT=corpus/live/r81-baseline
{
  echo "host: $(hostname)"
  echo "kernel: $(uname -r)"
  echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "HEAD: $(git rev-parse HEAD)"
  echo "HEAD_subject: $(git log --oneline -1)"
  echo "fixture_sha256: $(sha256sum corpus/fixtures/measure_audio.py | cut -d' ' -f1)"
  echo "fixture_bytes: $(stat -c %s corpus/fixtures/measure_audio.py)"
  echo "fixture_git_blob: $(git rev-parse HEAD:corpus/fixtures/measure_audio.py)"
  echo "fixture_dirty_vs_HEAD: '$(git status --porcelain -- corpus/fixtures/measure_audio.py)'"
  echo "---"
  python3 -c 'import sys,numpy;print("Python",sys.version.split()[0],"(numpy",numpy.__version__+")")'
  sox --version 2>&1 | head -1
  ffmpeg -version 2>&1 | head -1
  ffprobe -version 2>&1 | head -1
  pipewire --version 2>&1 | head -1
  pactl --version 2>&1 | head -1
  pw-record --version 2>&1 | head -1
  arecord --version 2>&1 | head -1
  aplay --version 2>&1 | head -1
  mpv --version 2>&1 | head -1
  ldconfig -p 2>/dev/null | grep -E 'libsndfile\.so|libjack\.so' | head -4
  echo "--- default sink/source ---"
  pactl info 2>/dev/null | grep -E "Server Version|Default (Sink|Source)"
  echo "--- foreign null sinks/sources (contention census) ---"
  pactl list short sinks 2>/dev/null | grep -v "alsa_output\|alsa_input" || echo "(none)"
  pactl list short sources 2>/dev/null | grep -v "alsa_output\|alsa_input" || echo "(none)"
  echo "--- foreign probe processes ---"
  pgrep -af "measure_audio|pw-cat|pw-play|pw-record|pw-loopback|parec|r79lb_|r80|r81|gst_r81" | grep -v pgrep || echo "(none)"
  echo "--- load ---"
  uptime
  echo "--- pw-cli ---"
  pw-cli info 0 2>&1 | head -3
} > "$OUT/env.txt" 2>&1
cat "$OUT/env.txt"
