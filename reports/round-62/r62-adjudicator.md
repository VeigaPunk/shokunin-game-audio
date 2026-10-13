# R62 Sol independent per-axis adjudication — SoX 3,839 decode-length mechanism

**Verdict: ADMIT the bounded R62 depth move.** Depth **improved locally**; coverage **improved locally**; calibration **improved locally**. No scoped axis is harmed. This verdict accepts a local mechanism explanation for one observed host behavior (SoX_ng decoding `pair_valid_17.wav` to 3,839 f32 samples), **not** standards conformance, decoder-correctness, or any claim about other tools/hosts.

Pinned work adjudicated: `cbe763e` (clean-before `1c52c7d`). Worktree clean otherwise; HEAD is the pinned commit on `main`.

## The declared claim (as briefed)

One **depth** move: resolve r61's retained UNKNOWN — why does SoX_ng v14.8.0.1 decode `corpus/live/round-61/pair_valid_17.wav` to 3,839 f32 samples (15,356 B) while `pair_valid_16.wav` yields 5,760 (23,040 B), and why SoX reports the file "16-bit" while decoding 24-bit. Establish the mechanism or record a bounded UNKNOWN.

## Mechanism as established by this round (five independent seat derivations, all convergent)

1. **SoX autodetect ordering**: `formats.c` probes `CHECK(act, "RIFF"@0, 0x84@256)` *before* the `wav` check; payload byte at file offset 256 is `0x84`, so both r61 files sniff as `act`; `act` open fails and the fallback chain reaches the `(ffmpeg)` pseudo-handler. With byte 256 → 0x00 (or file ≤256 B, or a chunk between fmt/data), SoX detects `wav` and the native reader **fatally rejects** `number of valid bits exceeds the number of bits per sample` (exit 2; inside `measure()`'s `check=True` that is a receiptless crash — a fixture fragility disclosed by scout/simplifier).
2. **ffmpeg reclassification**: `parse_waveformatex` treats nonzero `wValidBitsPerSample` as coded-sample width, ceil-mapped `(17+7)>>3=3` → `pcm_s24le` (3-byte). Codec map verified by critic sweep: 1–8→u8, 9–16→s16le, 17–24→s24le, 25–32→s32le, ≥33→unknown.
3. **Packetization**: `ff_pcm_default_packet_size` → `block_align·2^⌊log2(bitrate/80/ba)⌋` on the *reclassified* bitrate → max_size 8,192 B → packets `8192 + 3328` (confirmed via `-show_packets`).
4. **Per-packet floor**: the pcm_s24le decoder emits `floor(pkt/3)` and rejects each packet's mod-3 tail (`Invalid PCM packet size 2`/`size 1`) → `2730 + 1109 = 3839`. Total loss = 3 payload bytes = 1 frame. `duration_ts=3840` is nominal metadata division `(11520×8)/24`, not a decode bound. SoX's `--i` "16-bit" is a display artifact of the AU intermediary's encoding tag — answers r61's second residual UNKNOWN.

Eliminated hypotheses (each falsified by a constructed control): header-declared duration (`duration_ts=3840` ≠ 3839), valid-bits arithmetic directly (`v17_c32`=7,678 under a different reclassified bitrate), whole-file floor / EOF-loss / count-trim (critic achieved 3,839 *without* valid17 — `pcm16_n7678`, `pcm24_n11517`, `ext24_v24_n11517` — and non-3,839 *with* valid17 — `n11522`→3840, `ba3`→3840, `ext24_v17`→3840), `-max_size` sweeps (5000→3838, 6000→3840, 7000→3839) and 4 held-out constructions all predicted exactly.

## Evidence audited (this adjudicator's own runs, not report-trust)

- Fresh runner re-runs: `--probe-ui-extensible-valid-24-r62` → **exit 1**, receipt `20261013T232318649694Z`, failing entry with the four named failures (format/duration/level/spectrum); `--probe-ui-extensible-valid-32-r62` → **exit 1**, receipt `20261013T232319799401Z`, two failures (format/duration). Both as claimed.
- `ffprobe` on the r62 pair: valid24 → `pcm_s24le`/24/`0.080000`; valid32 → `pcm_s32le`/32/`0.060000`; `cmp -l` shows the pair differs **only at byte 38** (0x18 vs 0x20).
- `sox -t ffmpeg` decode byte counts re-derived: valid24 → 15,356 B = **3,839**; valid32 → 11,520 B = **2,880**; valid17 → 3,839; valid16 → 5,760. All four match the author/verifier values.
- `git show --stat cbe763e`: fixture diffs `build_artifacts.py` +28/−1, `measure_audio.py` +13/−4 — additive-only (removed lines are chain-head rewrites per convention); `format_failures`/`SPECS`/thresholds/canonical17/all prior modes untouched. Receipts + reports + seat scratch committed; disclosed `.pyc` regeneration is lane-convention churn.
- Non-author verifier `r62-verifier.md`: all **84 commands replayed serially**, 43 exit0 / 41 exit1, **84/84 exits match** the author's ledger and **84/84 receipts byte-identical** to committed counterparts; discernment spot-checks both directions (ffmpeg direct = 3,839 — SoX adds nothing; byte-256 flip → native fatal rejection). One disclosed incident (accidental `xxd` overwrite of `pair_valid_32.wav`) was detected by the verifier's own anomaly check and restored byte-exact — evidence-quality note, not a defect; `git status` clean.
- Frozen baseline `r62-baseline`: standalone `git archive` replay of the 82-command ledger → identical 43/39 shape, **81/82 receipts byte-identical** (sole divergence = resolved-absolute-path string inside `--probe-invalid`'s captured ffprobe stderr — pre-dates this round; both baseline and reviewer hit it identically).
- Seat reports r62-{scout,boundary,critic,reviewer,simplifier,scribe} all landed and mutually corroborate; five derivations of the same arithmetic from different entry points (source-trace, variant sweep, prediction matrix).

## Discrepancies and evidence-quality notes (none gate-affecting)

- **Dangling historical commit pins** (reviewer, carry-over from r61 extraction): `cd62e6d`, `1b35faaa`, `4894d07` cited in r61 records do not resolve in the canonical repo (r61 ran pre-extraction in the prymeagnt origin repo; canonical equivalents `0a300b4`/`04b4bd4`); blob SHAs verified identical so content is faithful — pointer defect only. LOG's r61 retro-declaration also pinned `4894d07` as clean-before where `cd62e6d` (→`0a300b4`) was correct. Corrected as an append-only LOG note this round.
- **Fixture fragility disclosed**: the r61 pair's decodability through SoX rests on payload byte 256 == `0x84`; the SHA-pinned committed payload makes this deterministic, but it is a content-collision, not designed behavior — flagged for future fixture authors, no action taken on the committed artifacts.
- Author's discarded wrong-cwd ledger attempt (84× exit 2, zero receipts) and corrected stale-count reads are setup noise, disclosed and excluded from evidence.
- Verifier's `__pycache__` observation: two `.pyc` binaries churned — lane convention commits them; retained.

## Per-axis judgment

| Axis | Judgment | Basis and limit |
|---|---|---|
| Depth | **Improved locally** | A retained UNKNOWN became a fully attributed mechanism with a predictive model (28/28 author predictions + independent held-out constructions). Depth = mechanism resolution, bounded to this host's tool versions. |
| Coverage | **Improved locally** | Second impossible-header family landed (`pair_valid_{24,32}.wav` + two opt-in modes); designated ledger extends 82→84 fresh commands; prior 82 preserved verbatim (81/82 byte-identical, one path-string). |
| Calibration | **Improved locally** | The gate's behavior on *more* impossible-valid-bits values is now measured (24 → 4-failure rejection, 32 → 2-failure rejection, both exit 1 with receipt); the earlier "malformed ⇒ gate rejects" shape is refined — rejection rides ffprobe's reclassification, not the field itself. |

## Learning trends

- **Expansion**: improved — new header-value region (24/32) + a mechanism-level model, both previously absent.
- **Quality**: improved — five convergent derivations, predictive falsifications in both directions, honest incident disclosure.
- **Discernment**: improved — admitted cases (r62 pair decode/rejection) and rejected cases (byte-256-flip fatal, wrong-hypothesis arms) both externally spot-checked by the named verifier.

## Bounded limits

Host SoX_ng v14.8.0.1 + ffmpeg n9.0.1 + Python 3.14 only; ACT collision is payload-content-dependent; packetizer constants swept on a grid, not exhaustively; no claim about non-ffmpeg SoX builds, other ffmpeg versions, audibility/fidelity, standards conformance, or production behavior. The `act`→`au`→`ffmpeg` fallback ordering and au's sniff trigger remain partially code-uncorroborated (error strings observed; bounded UNKNOWN retained).

## Reopen conditions

Reopen if: the 84-command ledger fails to reproduce the 43/41 exit shape; any committed receipt fails byte-comparison on a fresh run; byte-256 content of the committed pair_valid_17.wav changes (would re-route SoX natively and change r61/r62 evidence semantics); or the committed pair differs at any byte other than offset 38.

This adjudicator made no commits, pushes, spawns, or file writes other than this report and the two disclosed append-only receipts `20261013T232318649694Z`/`20261013T232319799401Z`.
