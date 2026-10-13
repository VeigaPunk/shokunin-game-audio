# Round 62 — simplifier: minimal-design critique of the SoX-decode-length mechanism hunt

Seat: **simplifier** (leaf, report-only — no tracked edits). Host: devin. Worktree
`~/Projects/prymeagnt/audio`; `.shokunin/audio/` → `~/Projects/shokunin/audio-shokunin`.
Brief: critique the author's landed r62 diff when it appears, else the r61 additions;
judge smallest discriminating fixture pair, probe-mode wiring, cheaper controls;
name anything deletable without losing the falsification.

**Landing status at write time**: no tracked diff — `git status` shows 0 modified
files; `corpus/fixtures/` unchanged (3 scripts + `__pycache__`). The author's work is
still untracked scratch (`corpus/live/r62-author/scratch/`: `build_variants.py`,
23 variant WAVs in `wav/`, `sweep_packets.py` + `sweep/` packet map, `bisect/` byte
bisection). I therefore critique (a) the landed r61 additions and (b) the r62
approach as visible in scratch. Independent verification ran in
`corpus/live/r62-simplifier/` (my `scratch/` and `runs/` only).

## TL;DR verdict

- The r61 pair **is** the smallest discriminating pair for its claim — one byte
  (offset 38), one identical 11,520-byte payload. Its wiring is the established
  minimal pattern. **Nothing in the landed r61 diff is deletable** — every added
  symbol is referenced by the admitted 82-command ledger.
- The r62 mechanism is fully pinnable by **~4 single-field scratch variants + one
  zero-fixture `ffprobe -show_packets`**, not a new tracked probe-mode family.
  The minimal landing for a *mechanism-explanation* round is **zero new probe
  modes** — the r61 pair is already the committed regression surface. If the
  author's scratch matrix were landed as modes, ~19 of 23 variants would be
  deletable without losing falsification.
- **Hidden load-bearing byte found** (new, independently reproduced): SoX's route
  to the 3,839 decode depends on **file byte 256 = `0x84`** — SoX_ng's autodetect
  ranks `act` (an ffmpeg pseudo-handler alias) ahead of `wav` when that byte
  matches. Flip it to `0x00` on the byte-identical-header file and `sox` exits 2 —
  and `measure_audio.measure()` then raises `CalledProcessError` (`command()`,
  `check=True`): the r61 runner would have produced **no receipt at all**, not an
  exit-1 receipt. The committed payload fixes byte 256 deterministically, so r61
  evidence remains reproducible — but it is an undocumented fragility of the
  fixture design, not just decoder trivia.

## The mechanism, confirmed independently (needed to judge "smallest")

Chain for `pair_valid_17.wav` on this host (SoX_ng 14.8.0.1, ffmpeg/ffprobe n9.0.1):

1. SoX autodetect → `act` → ffmpeg handler pipes `ffmpeg -i <f> -f au -`; SoX's
   `--i` "16-bit" describes the **AU intermediary** (s16be), not the wav.
2. `ff_get_wav_header`/`parse_waveformatex`: `bits_per_coded_sample :=
   wValidBitsPerSample` (17); `ff_get_pcm_codec_id(17)` → `(17+7)>>3 = 3` →
   `pcm_s24le` (valid-bits *replaces* container bits — a heuristic, not a spec rule).
3. `wavdec` packets: `max_size = block_align · 2^⌊log2(bitrate/80/block_align)⌋`,
   bitrate from the **codec** (24·48000·1) → ba2 → 8,192 B → `8192 + 3328`.
4. `pcmdec`: per-packet `buf_size -= buf_size % 3` → 2730 + 1109 = **3,839**;
   the 2 B + 1 B tails are rejected (`Invalid PCM packet`) — the one-frame gap is
   exactly 3 dropped payload bytes at packet boundaries.
5. ffprobe `duration = data_size·8/(ch·codec_bits) = 3840 → 0.080 s` — byte-count
   metadata, not a decode count.

My independent reproduction (commands → observed; all under
`corpus/live/r62-simplifier/scratch/`):

| experiment | observed | eliminates |
|---|---|---|
| `ffmpeg -i pair_valid_17.wav -f f32le -acodec pcm_f32le -` | 15,356 B = 3,839 | SoX adds nothing; loss is inside ffmpeg decode |
| `sox -t ffmpeg sweep_11520.wav` (my zero-payload, byte-identical header) | 15,356 B | header alone is sufficient for the ffmpeg decode path |
| data-size sweep @ba2 (`sweep_{3,30,4095,4096,8192,8196,11520,11521,12288,16386,24576}`) | 1,10,1365,1365,2730,2731,3839,3839,4095,5460,8190 | whole-stream floor, fixed −1, duration-driven models all die |
| `ffprobe -show_packets` on those files | `8192 3328` / `8192 8192 2` / `8192 8192 8192` … | packet boundaries are exactly 8,192-byte multiples; Σfloor(pkt/3) predicts every count |
| `align6_11520.wav` (ba2→ba6, all else identical) | **3,840** | one-field flip erases the loss: cap 4096·…→`6·2048=12,288` ≥ data → single packet, no boundary |
| `align4_/align1_11520.wav` | 3,839 | ba∤3 keeps boundaries mid-sample |
| `native24_{11520,12288}.wav` (true 24-bit container, ba3) | 3,840 / 4,096 | genuine s24 decode unaffected |
| `byte256_00.wav` (pair with byte 256 `0x84`→`0x00`) | `sox` **exit 2**, `formats: can't open input file … number of valid bits exceeds the number of bits per sample`; `ffmpeg` direct still 3,839 | proves the SoX-side fork is one byte of payload |
| `zeropay_84.wav` (zero payload + `0x84` at 256) | `sox` → 15,356 B = 3,839 | reproduces the r61 phenomenon on arbitrary payload |

Cross-checked against the author's scratch variants (decoded read-only —
`r62-author/scratch/wav/*.wav`): ba∈{1..8} sweep, v∈{20,24,25,32,33,64},
d-sizes {8190,8194,8196,11521,11522}, declared-size lies, `fact`, true-pcm24,
`v17_c32`. Every observed count matches `block_align·2^k` packetization +
per-packet floor: `ba5` → packets `10240+1280` → 3413+426 = 3,839 (cap is
`5·2048=10,240`, not "round 8192 down" — the bitrate-scaled formula is required);
`v25`→`pcm_s32le`, one 11,520 packet, 2,880 samples, zero loss; `v33`→codec
unknown → 0 samples; `v64`→`pcm_s64le` → 1,440; `v17_c32`→`pcm_s24le` (valid-bits
drives codec even inside a legal 32-bit container) → `8192+8192+6656` →
2730+2730+2218 = 7,678; `declared_short` → single 5,766 B packet → 1,922 —
declared size governs extent, `fact` ignored. All agree with the boundary seat's
source-cited chain (`r62-boundary.md`), which additionally fetched the n9.0.1
sources (`riffdec.c`, `wavdec.c`, `pcm.c`, `pcmdec.c`, `decode.c`).

## r61 additions — audit for deletability

Diff (r61 work commit, per `git diff 0a300b4..04b4bd4` as audited by the
reviewer): `build_artifacts.py` +18/−1, `measure_audio.py` +13/−4.

- **Fixture pair**: `build_ui_extensible_valid17_probe()` emits the 11,588-byte
  pair differing only at offset 38. One-field pair, byte-exact SHAs recorded,
  payload SHA-pinned — this is already the smallest discriminating shape for the
  "valid-bits > container" claim. Nothing deletable.
- **Builder wiring**: two `add_argument` + one dispatch branch — minimal for the
  file's existing convention.
- **Measurer wiring**: two flags + two sum entries + two forwarded flags + one
  `measure(name, SPECS["ui"], path)` block + `mode`/`suffix` chain heads — the
  established per-round pattern; no dead paths introduced.
- **Not deletable despite redundancy appearance**: `…-valid-16-r61` looks
  redundant with r57–r60's four other valid16 modes, but each controls a
  *different payload* (different generators) and each is a ledger-referenced
  replay command — removing it breaks prior-command reproducibility, which is
  the ledger's no-harm surface.
- **Accretion note (flag, don't act)**: the mutual-exclusion `sum([…])` list and
  the `mode`/`suffix` ternary chains grow ~2 entries per round (now ~80 flags).
  A table-driven `(flag → name, path)` map would collapse them — but the giant
  ternary IS the current convention, touching it rewrites every prior mode's
  dispatch and gains nothing on a depth-axis round. Recorded as a future
  consolidation candidate only.

## r62 approach — minimality assessment

**Is the smallest discriminating fixture pair used?** For the *mechanism* claim
the minimal pinning set is:

1. `ffprobe -show_packets pair_valid_17.wav` → `[8192, 3328]` — **zero new
   fixtures**; combined with the known 3,839 count it exhibits the boundary
   arithmetic directly (ffprobe's own per-packet durations are already floored:
   2730 + 1109).
2. One block_align flip to a multiple of 3 (`ba3` or `ba6`) → 3,840 — one changed
   field erases the loss ⇒ boundary-driven.
3. One reclassification to a width dividing the packet (`v25` → s32 → 2,880,
   single packet) ⇒ loss is width-modular arithmetic, not a malformation penalty.
4. `declared_short` → 1,922 ⇒ declared data size governs extent (kills the
   "header duration field" hypothesis cleanly).
5. (SoX half) one-byte edit `byte256→0x00` ⇒ `sox` exit 2 ⇒ handler-route
   dependence — the cheapest possible control, applied to the existing file.

= **4 tiny variants + 1 command**. The author's 23-variant matrix is a superset;
as scratch exploration that is fine (cheap, parallel, untracked), and several
"redundant" cells are defensible corroboration (`ba5` specifically *needed* the
full packet formula to predict, which is what makes it diagnostic). But if any
of it lands as tracked fixtures/probe modes, the following are deletable without
losing falsification:

- `v20`, `v24`, `v32`: same codec-map claim as v17/v25. `v24` alone brackets the
  s24→s32 boundary against `v25`; keep at most one of the {v20,v24,v32} triple.
- `pcm24_true`: duplicates `ba3`'s falsification ("multiple-of-3 units → no
  loss") while changing two fields (tag 0x0001 *and* container width) — weaker
  as a control and redundant as evidence.
- `d8190`/`d8194`/`d11521`/`d11522`: only one discriminating data-size is needed
  (e.g. `d11521` → predicted 3,839 vs naive floor 3,840, or `d8193`-style tail);
  the rest are corroboration.
- `fact5760`: a one-line "fact chunk ignored" fact — worth a sentence in the
  mechanism note, not a fixture.
- `ba{1,4,5,8}`: keep **one** non-multiple-of-3 (say `ba5`, since its 10,240 cap
  is the case that falsifies the naive "round to block_align" rule).

**Is the probe-mode wiring minimal?** There is nothing to wire. This round's
deliverable is an *explanation*, not a new gate fixture: the r61 probe modes
already replay the pair. Landing new `--probe-*` modes for decoder-internals
variants would (a) freeze an ffmpeg-version-specific packetization rule into
expected receipts, (b) add weight the falsification doesn't need. The
proportionate landing is a `corpus/knowledge/` note recording the mechanism plus
the byte-256 dependency, or nothing tracked at all.

**Cheaper controls**: `sox -t ffmpeg` / direct `ffmpeg` replace any SoX-path
fixture need for the decode side — deterministic, bypasses the detection
lottery. For the SoX side, the byte-256 single-byte edit is the minimal
discriminating control (reproduced above).

## Caveats for whoever writes variant fixtures later

- Any future wav fixture relying on the SoX→ffmpeg route must keep **file offset
  256 = `0x84`** (requires ≥ 189 payload bytes) or force `-t ffmpeg` — otherwise
  `sox` takes the native wav handler and hard-fails `valid>bits`. My zero/random/
  ramp-payload files with byte-identical headers all failed `sox` open while
  decoding fine via ffmpeg — the r61 "SoX decode" is payload-dependent.
- `measure()`'s `sox` call uses `check=True`: a native-path flip converts
  "exit-1 with receipt" into "runner crash, no receipt" — the recorded r61
  outcome shape depends on this byte.

## Housekeeping disclosure

While verifying the `measure()` crash claim I imported the tracked
`measure_audio.py` once; Python rewrote the tracked
`corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`. I restored it
byte-exactly with `git show HEAD:<path> > <path>` (no `checkout`/`commit` —
leaf rule honored); `git status` now shows 0 modified tracked files. Scratch
and this report are the only writes, both inside my assigned scope.

## Scope notes

All findings are host-specific (SoX_ng 14.8.0.1 + ffmpeg n9.0.1 on this machine);
no claim about other versions, spec conformance, rights, quality, or production.
No commits, no pushes, no subagents, no sibling-lane writes. One report file +
scratch under `corpus/live/r62-simplifier/`.
