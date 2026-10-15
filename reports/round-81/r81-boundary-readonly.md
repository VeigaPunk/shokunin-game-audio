# r81 BOUNDARY (read-only analysis pass) — receipt re-analysis of the r81 scout corpus

Seat: ufo-labrat (capability-blocked: read/grep/glob only — no exec, no
writes). This file is written by the orchestrator from the seat's reply
payload; no fresh legs were run. Everything below is re-analysis of
`corpus/live/r81-scout/` raw receipts — labeled accordingly.

## Verified findings from receipt re-analysis

- All 12 frozen reps (s5-loss t3/t4/t5/t6) show the byte-identical curve
  `0 → 65580 → 135212 → 204844 → flat` to the −9 wall-cap kill;
  `stderr_head=[]`, unload rc=0, `post_links=[]`. [O-receipt]
- Minus the 44-byte wav header: `65536 / 135168 / 204800` = 16/33/50 ×
  4096 B — the loss legs negotiated a **1024-frame** buffer. Freeze =
  exactly 50 whole delivered buffers (51200 frames ≈ 1.067 s delivered
  before the t=1.2 unload). Inter-sample deltas are 4096-quantized — **no
  partial-buffer flush exists**. [O-receipt]
- Contrast legs pin the quantum as leg-negotiated: `num-buffers=100`
  finalized at 819244 B (2048-frame buffers, c1/c2/c3/c5) vs 409644 B
  (1024-frame, c4/c7/c8); the t7 pw-record control grew through the
  unload in the same 4096-B quantum to 864300 B. [O-receipt]

## Falsified scout constant (critic must fold)

- The scout report's frozen-header constant `data field 0x7FFFF000` is
  **wrong on both fields**: receipts (s5-loss.json ~line 21470) measure
  `riff-size = 0x7FFF0024`, `data-size = 0x7FFF0000`. Any arm asserting
  `0x7FFFF000` will fail; pin `0x7FFF0024`/`0x7FFF0000`.

## Sharpened law [I]

`freeze bytes = delivered_buffers × per-leg-negotiated-buffer-bytes + 44`,
always unfinalized. "204844 = 44 + 51200×4" was arithmetically right but
the buffer-level truth is 50 × 1024-frame buffers; this quantifies r77's
"`num-buffers` is not a frame bound" note.

## Designed legs handed to the exec-capable r81-boundary-r2 seat

1. `on-disconnect` vs peer-stream exit (producer exits, sink alive);
   sharper variant: `pw-link -d`/`pw-cli destroy` of monitor→input links
   with `on-disconnect=error|eos`.
2. Capture-side precedence: `target-object` vs `stream-properties`
   target on `pipewiresrc`.
3. `PIPEWIRE_REMOTE=nonexistent` both elements; `PIPEWIRE_NODE` capture
   side; `PIPEWIRE_NODE` vs `target-object=` precedence.
4. `pulsesrc device=` variants: `*.monitor` real source name (expect rc=0
   + tone), bare sink name (expect rc=1), real source.
5. Freeze sweep: unload at t=0.7/2.0 + `num-buffers=20` EOS-before-loss
   control leg.
