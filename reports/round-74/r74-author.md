# R74 author — lavf no-seek demuxer sweep + pw-cat ops-2

Round: 74. Wave: `shokunin-train-20261101-w13`. Base commit `1ba8103`.
Host `plazir27` (measured 2026-10-14 ~15:30 UTC): mpv **v0.41.0** /
libavformat **63.1.101**, ffmpeg **n9.0.1**, pw-cat (libpipewire
**1.6.8**), PipeWire daemon live (`pipewire` pid 1905, `pipewire-pulse`
2290, `pactl` proto 35, default sink present).

## Landed changes

`corpus/fixtures/measure_audio.py` (**+544/−3**; the 3 changed lines are
the mutex-sum, `mode`, and `suffix` chains — each preserves the prior
expression verbatim and adds only the r74 clause, the same edit r73 made
to join the flag set):

- `LAVF_R74_MEMBERS` + `build_lavf_r74_members()` — byte-deterministic
  member generation under `corpus/live/round-74/` (self-sufficient on a
  fresh tree; a generation failure degrades to a recorded per-member
  blockage, never a fabricated member). Header layouts taken from the
  n9.0.1 demuxer sources (iss.c/apc.c/acm.c). Member generation lives in
  the probe path itself (brief scope: implement in measure_audio.py)
  rather than build_artifacts.py — the r69 convention would put it
  there; noted as a deliberate scope choice, not an oversight.
- `mpv_extent_leg(transport, path, data, hold_s, extra_opts)` — mpv leg
  with `--ao=pcm --ao-pcm-file=<scratch>`: the decoded stream lands in a
  scratch wav and `pcm_out_bytes`/`pcm_out_duration_s` (ffprobe) is the
  PCM-extent pin for the head-truncation and position wound shapes,
  where the fork is in HOW MUCH audio plays, not the verdict signature.
  `ao=pcm` needs no device (the r73 `ao=null` pin guards the
  pipewire/dead-runtime class only). Log field set mirrors `mpv_leg`.
- `lavf_transport_entry(member, path)` — mpv-only 4-transport entry
  (same leg + verdict-group machinery as `consumer_transport_entry`;
  signature `(exit_code, lavf_detected, seek_failed)`, never bare rc).
  `predicted` names the claim cell; failures pin deviations BOTH ways —
  an absent predicted fork and an invariant-member fork are both
  measured falsifications.
- `lavf_startpos_entry(path)` — `mpv --start=2` extent cell on the r73
  4.0 s wav pacer.
- `pwcat_ops2_entry()` — ops-2 as a PARALLEL key
  (`consumer_pwcat_ops2_r74_probe`), leaving the r73 ops entry untouched:
  (a) `fifo_no_writer_escalation` — blocked in `wait_for_partner`,
      SIGTERM ignored ≥1.0 s, `killpg` SIGKILL -> `exit_code -9`;
  (b) `target0_unlinked_stream` — `timeout -s TERM 4` -> `exit_code 124`
      (TERM-TERMINABLE hang, the negative twin of (a)'s TERM immunity);
  (c) `pwcat_raw_name_axis` — `pw-cat -p --raw` on the identical
      extsuffix .snd bytes through `axis.{snd,wav,bin}` fifos;
  (d) `zero_sink_daemon` — private `pipewire` under a scratch
      `PIPEWIRE_RUNTIME_DIR`/`XDG_RUNTIME_DIR`, `pw-dump` Audio/Sink
      census, `pw-cat -p` bounded at 6 s then `killpg` SIGKILL; daemon
      terminated in `finally`. Recorded as a blockage cell when the
      private socket never appears or `pipewire` cannot be spawned.
- Flag `--probe-lavfsweep-r74` wired through argparse, the mutex sum,
  and the `mode`/`suffix` chains (`probe-lavfsweep-r74` /
  `-lavfsweep-r74`).

## New members (`corpus/live/round-74/`, generated deterministically each run)

| member | bytes | sha256 | construction |
|---|---|---|---|
| `lavf_iss.iss` | 552 | `4fbc2ca5…` | hand-built: `"IMA_ADPCM_Sound"` + 9 ASCII tokens, 2×256 B packets |
| `lavf_iss_multi.iss` | 131118 | `85a518c8…` | same header, 256×512 B packets (exceeds the probe window) |
| `lavf_apc.apc` | 5152 | `684d2794…` | hand-built: `"CRYO_APC"+"1.20"` + u32 fields + 5120 B payload |
| `lavf_acm.acm` | 2394 | `5afaa65a…` | hand-built: BE magic `0x97280301` in the 14-B extradata + 20×119 B zero frames (subformat `0x7700` -> level 0/rows 0x77; interplayacm decodes to silence) |
| `lavf_adx.adx` | 12474 | `3831ef47…` | `ffmpeg -f lavfi -i sine=440:44100:0.5 -ac 1 -c:a adpcm_adx` |
| `lavf_aifc.aifc` | 44154 | `23aa8a65…` | same synth, `-c:a pcm_s16be` (aiff muxer) |

(Regeneration verified byte-identical — sha256 above are stable across
two builds.) Controls from existing tracked members: `dec_act`
(round-66, wav). The brief's "aifc already on corpus" held only for
frontier/reviewer scratch, not a tracked member — aifc is generated as
`lavf_aifc` so the invariant control is a real member, not a scratch
dependency.

## Measured (committed receipt `runs/20261014T153027827786Z-lavfsweep-r74`, `failures: {}`)

ARM A — the source-derived 4-clause rule held on every member:

| member | prediction | file | stdin_pipe | redirected_fd | fifo_path | outcome |
|---|---|---|---|---|---|---|
| `lavf_iss` | fork | **rc2** EPERM, iss@100 | rc0 | **rc2** EPERM | rc0 | FORK (rc2 wound — same shape as r73 dec_hcom) |
| `lavf_apc` | fork | **rc2** EPERM, apc@100 | rc0 | **rc2** EPERM | rc0 | FORK (rc2 wound) |
| `lavf_acm` | fork | rc0 + EPERM, acm@66 | rc0 | rc0 + EPERM | rc0 | FORK — **ENOSYS-class wound**: seek_failed EPERM on seekable arms yet rc=0 (fork lands on the `seek_failed` field, not rc) |
| `lavf_iss_multi` | fork | rc0 + EPERM, iss@100 | rc0 | rc0 + EPERM | rc0 | FORK + head-truncation (below) |
| `lavf_adx` | invariant | rc0 (refresh-seek OK) | rc0 | rc0 | rc0 | INVARIANT — GENERIC_INDEX index-seek rescue, adx@75 |
| `lavf_aifc` | invariant | rc0 | rc0 | rc0 | rc0 | INVARIANT — aiff's own read_seek, aiff probe |
| `dec_act` | invariant | rc0 | rc0 | rc0 | rc0 | INVARIANT — wav read_seek + pcm seek hack |

Secondary cells:

- **Head-truncation (wound-shape corollary)** — `lavf_iss_multi`: file
  arm `refresh seek` -> `Seek failed (Operation not permitted)` ->
  `seek done` -> continues from queued packets -> `success (reason 0)`.
  Extent pin (ao=pcm): file **516196 B / 5.851791 s** vs fifo
  **520260 B / 5.897868 s** — the seekable arm drops 4064 B of head PCM
  (the packets consumed inside the probe window). rc0-with-truncation,
  NOT rc2 — corollary CONFIRMED.
- **Position fork** — `mpv --start=2` on `stem_sections.wav` (4.0 s):
  {file, redirected_fd} seek to 2.0 -> **2.0 s** output
  (192068 B) vs {stdin_pipe, fifo_path} `Cannot seek` -> play from 0 ->
  **4.0 s** (384068 B). CONFIRMED exactly.

ARM B — `consumer_pwcat_ops2_r74_probe` (all pins hit):

- `fifo_no_writer_escalation`: `blocked=true`, `wchan=wait_for_partner`,
  `sigterm_immune=true` (ignored ≥1.0 s), `killpg` SIGKILL ->
  `exit_code=-9`. The missing kill-escalation rc cell is now pinned.
- `target0_unlinked_stream`: `timeout -s TERM 4 pw-cat -p --target 0`
  -> `exit_code=124`, `wall_s=4.002`, `term_terminable=true` —
  the hang is real but TERM-TERMINABLE, cleanly separated from the
  open-block's SIGTERM immunity. Matches r73-boundary's class.
- `pwcat_raw_name_axis`: identical extsuffix .snd bytes through
  `--raw` -> `rc=0` on ALL THREE fifo names ({snd,wav,bin} — ops-1's
  decode-layer fork {0,1,1} collapses). The name axis dies without the
  libsndfile decode layer. CONFIRMED.
- `zero_sink_daemon`: private pipewire socket up in ~0.4 s,
  `audio_sink_count=0` (pw-dump census), `pw-cat -p` hung the full
  6.0 s -> `killpg` SIGKILL, `exit_code=-9`, daemon terminated cleanly.
  Zero-sink is a hang class, not an error — CONFIRMED (cheap enough to
  include).

## Claim outcome

The xconnector 4-clause fork rule is CONFIRMED on this corpus, this
host, this toolchain: all three predicted-fork demuxers fork on the
seekable bit, all three predicted-invariant controls hold, and both
wound shapes are measured (rc2 when probing drains the stream;
rc=0+EPERM with truncated head when packets survive behind the probe
window — acm shows the second shape at small size because its raw-packet
reads queue data ahead of the failed refresh seek). Two new members
document each shape inside ONE demuxer (iss small vs iss_multi).

## Known bounds / risks

- The acm member is a decode-to-silence recipe (subformat 0x7700, zero
  frames): the interplayacm decoder accepts it, but it is not a real
  game asset — the fork evidence is the demuxer-level `seek_failed`
  signature, which is what the receipt keys on.
- `pcm_out_bytes`/`pcm_out_duration_s` are deterministic decoded output
  (516196/520260 B reproduced twice: scratch + committed run); the
  4064 B head-truncation delta should be stable, but it is a
  packet-granular quantity — treat the delta's exact value as
  member+build pinned, the SIGN (`truncated`) as the semantic pin.
- `target0_unlinked_stream.wall_s` and `zero_sink_daemon` waits are
  wall-clock leaves (jitter); semantic pins are `exit_code=124`,
  `term_terminable`, `blocked`, `sigterm_immune`, `exit_code=-9`.
- Zero-sink cell spawns a private `pipewire` — teardown is in `finally`
  and the live session daemon (pid 1905) is never touched; the cell
  degrades to a recorded blockage if the private daemon cannot spawn.
- The sweep is viability-conditional on the same gates as r73 (mpv +
  lavf for ARM A; live PipeWire daemon for ARM B); member generation
  additionally needs `ffmpeg -f lavfi` for adx/aifc only.
- Reviewer cross-check already exists: `corpus/live/r74-reviewer/`
  independently generated iss/apc/acm members and measured the same
  fork/invariant outcomes before this arm ran — agreement across two
  independent generators strengthens the mechanism attribution.

**Seat stop.** Files changed: `corpus/fixtures/measure_audio.py` only
(+544/−3). New untracked members: `corpus/live/round-74/` (6 files).
Receipt: `corpus/live/runs/20261014T153027827786Z-lavfsweep-r74/`.
Prior rows byte-identical (re-verified: this run's
`transport_dec_act_r67_probe` is byte-identical to all 44 default-hold
committed receipts; 2 prior receipts differ only in the recorded
`fifo_writer_hold_s` env override). No git mutation, no commits.
