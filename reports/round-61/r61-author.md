# R61 author — extensible wValidBitsPerSample 17 vs 16 (valid bits > container depth)

host: devin (prior rounds ran on prime-agent)
Clean-before HEAD: `cd62e6d` (R60 final commit "Audio round 60: final malformed valid0 report").

## Scoped move derived from the LOG

R57–R60 walked `wValidBitsPerSample` **downward** against control 16: valid15
(divisible-2 payload), valid14 (divisible-4), valid13 (divisible-8), and malformed
valid0 — all locally accepted and decoded as PCM16 on this host. The remaining
unprobed boundary of that one header field is **above** the 16-bit container
depth: `wValidBitsPerSample=17` declares more valid bits than the container
holds — an impossible/malformed declaration. R61 probes exactly that: a matched
5760-frame mono 48 kHz `WAVE_FORMAT_EXTENSIBLE` PCM-subtype pair (fmt size 40,
cbSize 22, mask `0x4`, 16-bit container, identical signed16 payload) differing
only in `wValidBitsPerSample` **17 vs 16**. This is a deliberately malformed
header case, not a conforming positive vector. Falsifiable question: do
ffprobe/SoX/unchanged project measurer reject it before a receipt, reclassify the
stream, or pass the existing UI gates. Actual observed outcome is recorded below
without preclaim; no predicate/threshold/canonical17/prior-mode change was made.

## What ran (exact commands, exit codes, receipts)

All commands from repo root `/home/vgpnk/Projects/prymeagnt/audio`:

1. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-17-r61` → **exit 1**, receipt
   `.shokunin/audio/corpus/live/runs/20261013T164943766168Z-ui-extensible-valid-17-r61/measurements.json`.
   Sole failing entry `ui_extensible_valid_17_r61_probe`:
   `format: expected PCM16`, `duration: outside ±1 ms`,
   `level: clipping headroom or near silence`, `spectrum: centroid outside fixture band`.
   All 17 canonical measurements and all distinctness/family/section records in that receipt carry no failures.
2. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16-r61` → **exit 0**, receipt
   `.shokunin/audio/corpus/live/runs/20261013T165003992146Z-ui-extensible-valid-16-r61/measurements.json`, zero failures.
3. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` → **exit 0**, receipt
   `.shokunin/audio/corpus/live/runs/20261013T165005333529Z-normal/measurements.json`;
   parsed JSON **exactly equal** to R60 normal `20261013T132816640667Z-normal`.
4. Prior-mode spot check `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-0-r60` → **exit 0**, receipt
   `20261013T165033697535Z-ui-extensible-valid-0-r60/measurements.json`; regenerated
   round-60 pair SHAs `5ab169fc3f43b29c0bb17cc86e6b76fb424e590b7d788a503a002501c8a2f394` /
   `d7f08d659b608e003e5ef2aaccf325dae3bd4e961caeaa450bd933c406b4cc46` match R60 recorded values exactly (deterministic rebuild, prior mode intact).
5. `python3 -m py_compile` both fixture scripts → exit 0; `git diff --check` → exit 0.

## Byte-exact evidence

Integrated builder output `corpus/live/round-61/pair_valid_{17,16}.wav`, each 11,588 bytes:

| file | SHA-256 | wValidBitsPerSample |
|---|---|---:|
| `pair_valid_17.wav` | `15cadf242eff13ede3ff25b992f4410ec89a76a9814e2afad346b4052eb63fe4` | 17 |
| `pair_valid_16.wav` | `2c5e244fb19bed5f6abdaa605ae503dd6685f88cb440de93a4cd313959591d00` | 16 |

Byte comparison: **only file offset 38 differs** (0x11 vs 0x10). Both parse as
RIFF/WAVE fmt40, tag `0xfffe`, mono, 48000 Hz, byte rate 96000, block align 2,
container bits 16, cbSize 22, mask `0x4`, PCM subtype GUID
`0100000000001000800000aa00389b71`, data 11,520 bytes; identical payload SHA-256
`7ebc75f1e6f7af3533113826b7cdbfe61813d7ca6c55d53fefc00a4cd5b10cc2`
(5,760 signed16 values `round(8191*(.28*sin(2π·1050·i/48000)+.10*sin(2π·1750·i/48000)))`).

Independent tool observations on this host (ffprobe n9.0.1, SoX_ng v14.8.0.1 — SoX uses its ffmpeg backend here):

- ffprobe `pair_valid_17.wav` exit 0: `codec_name=pcm_s24le`, `sample_fmt=s32`,
  `bits_per_sample=24`, `bits_per_raw_sample=24`, 48000 Hz mono, **duration 0.08 s**.
  ffprobe reclassifies the stream as 24-bit when valid bits exceeds 16; the
  11,520-byte payload is then read as ~3,840 24-bit frames.
- ffprobe `pair_valid_16.wav` exit 0: `pcm_s16le`, `s16`, 16 bits, 0.12 s.
- `sox --i pair_valid_17.wav` exit 0 reports container-level "16-bit Signed Integer PCM",
  yet the actual SoX f32 decode produced **3,839 samples** (valid16: 5,760);
  decoded vectors are **not equal** (different length). SoX f32 file SHAs:
  valid17 `3cda59787933bc3057c7db939382a05a247fc56f2f0f726325d6fe4ce51e707c`,
  valid16 `407e8c22c48ae31952ab5ad117681c7e54148d8f6cebcd435033ac751b6f9a97`
  (artifacts kept at `corpus/live/round-61/valid{17,16}.f32`).
- Runner probe measurements: valid17 → duration `.08`, `pcm_s24le`/24, peak
  `.992279052734375`, RMS `-7.797933085328953` dBFS, centroid `12180.625368025178` Hz,
  bandwidth `7171.544640451181` Hz, 4 failures (garbage 24-bit reinterpretation of
  the 16-bit payload, expected consequences); valid16 → duration `.12`,
  `pcm_s16le`/16, peak `.088226318359375`, RMS `-25.58802390050348` dBFS, centroid
  `1250.916113037482` Hz, bandwidth `585.4256545144334` Hz, clean.

## Source diff (additive only)

- `corpus/fixtures/build_artifacts.py` (+19/−1): new deterministic
  `build_ui_extensible_valid17_probe()` writing `live/round-61/pair_valid_{17,16}.wav`;
  two new argparse flags `--probe-ui-extensible-valid-17-r61` /
  `--probe-ui-extensible-valid-16-r61`; one new dispatch branch placed before the
  R60 branch.
- `corpus/fixtures/measure_audio.py` (+12/−4 per `git diff --stat`: 31+/5− total):
  two argparse flags, two entries in the mutual-exclusion sum, two forwarded
  builder flags, one measurement block (`live/round-61/pair_valid_{17,16}.wav`,
  names `ui_extensible_valid_{17,16}_r61_probe`), `mode`/`suffix` chain heads.
- `format_failures()`, `SPECS`, all thresholds, canonical 17 artifacts, and all
  prior probe modes unchanged. Only files under `.shokunin/audio/` were touched;
  nothing was committed.

## Per-axis claim (author evidence only; verdict is for verifier + adjudicator)

- **depth — claimed locally improved**: first locally *rejected*
  extensible-valid-bits case. All four prior perturbations (15/14/13/0) passed;
  valid17 exposes that this host's ffmpeg-derived path acts on the field — it
  rounds the declared container up to 24 bits, so the unchanged format predicate
  indirectly catches the malformed declaration (`format: expected PCM16`) plus
  three cascade failures from the mis-decoded stream. Directional asymmetry of
  reader behavior is now evidenced: below/within-range declarations are ignored,
  above-range alters the decoded stream.
- **coverage — claimed locally improved**: two new opt-in modes and a new
  perturbation region of byte 38 (value > container depth); canonical 17 and
  all prior modes preserved (normal receipt JSON identical to R60; R60 mode
  re-run clean with identical regenerated WAV SHAs).
- **calibration — claimed locally improved**: the probe class now includes an
  expected-exit-1 *with receipt* extensible-header case, calibrating what
  "malformed" means on this host — valid0 (ignored field, passed) vs valid17
  (field consumed, rejected). Exit-1-with-receipt is a gate validation outcome,
  not a decoder crash (ffprobe/SoX both exited 0).
- **harmed**: none demonstrated in scoped evidence. No threshold, predicate,
  canonical fixture, or prior receipt was altered; no prior-mode regression
  observed (one prior mode spot-checked clean plus the byte-identical rebuild).

## Conditional replay shape (for the non-author verifier)

Both new modes produce receipts, so the R60-style conditional applies: an
82-command serial replay = the R60 80-command ledger plus these two modes,
expected **43 exit 0 / 39 exit 1** (38 prior expected validation exit-1 plus the
valid17 expected exit-1). This is the ledger shape implied by convention, not a
verdict.

## UNKNOWNs

- Whether ffmpeg's 17→24-bit container rounding is spec-mandated, an ffmpeg
  heuristic, or version-specific; no WAV specification was consulted and no other
  decoder/host tested. `bits_per_raw_sample=24` is ffprobe's own report.
- Why the SoX ffmpeg-backend decode yields 3,839 samples rather than the
  arithmetically expected 3,840 (11,520/3); the one-frame difference is
  unexplained host behavior.
- Whether any valid-bits value >16 but representable in ffmpeg's rounding table
  (e.g. 24, 32) behaves identically; only 17 was probed.
- Whether SoX's `--i` "16-bit" report vs its ffmpeg-backend 24-bit decode is a
  display quirk or a real internal inconsistency on this host.
- No claim about standards conformance, universal extensible-WAV handling,
  valid-bit metadata enforcement in general, other masks/GUIDs/fmt sizes,
  precision/fidelity, audibility, quality, production, rights, engine,
  publishing, or promotion. `wValidBitsPerSample=17` remains a malformed
  declaration, not a positive format case.
