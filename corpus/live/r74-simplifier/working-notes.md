# r74 simplifier working notes

- 15:19Z wave start; HEAD 1ba8103 (r73 report-last). r74 arm NOT landed.
- LSP device unavailable (re-verified): no pyright/pylsp/jedi-language-server/lsp
  binaries; pygls/jedi not importable; clangd C-family only; only MCP server
  `rea` is Ghidra-session-bound (binary_overview -> target_unavailable
  "No app is open"). => grep-literal fallback, NOT semantic proof.
- Scratch tree built (tree/corpus/fixtures + artifacts copy + live round-*
  symlinks; round-74 kept real). Normal battery rc=0.
- BASE retained behavior: scratch rerun of --probe-consumers-r73 vs committed
  20261014T151240011154Z-consumers-r73: 0 stable diffs / 1363 keys; only
  wall_s jitter (4.032->4.031, 6.004->6.003). Harness reproduces receipts.

## Pre-landing weight rulings (to check against the landed diff)

ARM A (--probe-lavfsweep-r74):
- A1 member authority: new member dict must ALIAS canonical members where shared
  (wav/aifc controls); new members only for iss/apc/acm/adx(+multi). No second
  copy of canonical paths.
- A2 timeout: reuse TRANSPORT_R71_ARM_TIMEOUT_S (15 s) — no new constant.
- A3 fifo writer protocol: reuse fifo_feed + fifo_writer_hold_s.
- A4 lavf parsing: mpv_leg already extracts the brief's exact field list
  (detected format / probe score / seek_failed / audio_track / playback
  reason) — reuse, don't write a second parser.
- A5 naming: --probe-lavfsweep-r74 / suffix -lavfsweep-r74; one mode branch,
  one suffix branch; family keys lavfsweep_*_r74_probe.
- A6 member generation (measured): ffmpeg n9.0.1 has NO iss/apc/acm muxers or
  encoders (adpcm_adx + pcm_s16be exist) -> hand-built deterministic headers
  for iss/apc/acm; fixed bytes, no timestamps -> byte-stable receipts.
- A7 secondary cells (iss_multi truncation-fork, mpv --start=N position fork)
  ride the same r74 flag/entry.

ARM B (pw-cat ops-2):
- B1 placement (measured): extending consumer_ops_entry mutates the r73 flag's
  receipt (sim: sha f6d5379a->8ac6ed72, 1 one-sided leaf, 0 shared-leaf
  changes). Parallel pwcat_ops2 key under the r74 flag keeps the r73 replay
  byte-identical (scratch rerun: 0/1363 stable diffs). Prefer parallel key.
- B2 kill-escalation rc cell: reuse the existing start_new_session+killpg
  SIGKILL pattern + /proc wchan capture; no second kill mechanism.
- B3 --target 0 negative cell: bounded timeout (reuse CONSUMER_R73_TIMEOUT_S),
  record rc/wall as negative; never gate.
- B4 -a/--raw name-axis-death cell: reuse pwcat_name_axis harness (same fifo +
  writer + identical .snd bytes), add raw-mode leg.
- B5 zero-sink private daemon: viability-conditional; record blockage if not
  cheap. Do not add a second daemon-viability authority (r73 C3 carries).
- B6 verdict granularity: normalized reason lines, never bare rc (r73 C6).
