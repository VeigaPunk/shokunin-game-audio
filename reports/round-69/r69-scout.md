# r69 scout — extension-suffix sweep: predicted partition measured (claim tracks TRUE); the `.snd` arm is content-contracted to zero-prefix bytes; dead-row census = 125/130

Seat: scout (leaf). Lane: audio. Repo: `audio-shokunin` worktree at
`~/Projects/prymeagnt/audio` (`.shokunin/audio` → `~/Projects/shokunin/audio-shokunin`).
Host: `SoX_ng v14.8.0.1` `/usr/bin/sox` (USING_FFMPEG + HAVE_SNDFILE +
HAVE_SF_FORMAT_MPC2K + HAVE_MAGIC — `sds`/`mpc2k`/`act` all in `sox --help`;
ldd shows libsndfile+libmagic). Source: upstream `sox_ng/src/formats.c` at
`/tmp/sox_ng_src/sox_ng/src/` — same tree the r64/r68 rounds verified
byte-identical to `corpus/live/r64-reviewer/r64rev-formats.c`.
Evidence: `corpus/live/r69-scout/` — `probes/` (16 members, 2 contents),
`run_matrix.sh` → `runs/matrix-r69.tsv` (12 members × 4 arms = 48 legs),
`runs/check-row-census.tsv` (131 CHECK rows, per-row fired status),
`logs/*.stderr` (48 leg captures + 4 conjunct probes).

## Headline for the author — the declared claim is predicted TRUE, with one binding content contract

Declared claim: *the named arm splits into ≥3 distinct verdict groups by
extension alone on identical no-match bytes, and the `.snd` member is the
first tracked member where DETECTION (not just decode) forks on transport
name.*

Measured on the scratch matrix (`runs/matrix-r69.tsv`, identical 300 zero
bytes sha256 `d13d4a8b…` under 8 names): **the named arm splits into seven
distinct verdict outcomes** — wav-reader `RIFF header not found`,
`no handler for file extension 'bin'`, txw-reader `invalid filetype ID…`
(file) / `input must be a file, not a pipe` (fifo), f32 **decode 75 samples
exit 0**, sndr-detected `invalid rate value`, au-reader `can't find
Sun/NeXT/DEC identifier`, raw-reader `sample rate is zero or negative`.
≥3 is met with margin.

And `nm_zeros.snd` gives `sox_detected_format=sndr` on {file,fifo_path} vs
`null` on {stdin_pipe,redirected_fd} — a DETECTION fork on transport name,
the first for a tracked member (r67's 10 members + r68's 2 are all
detection-invariant; verified per-arm in their receipts).

**Binding contract on shared content**: the ext-gated row is
`CHECK(sndr, 7,1,"", 0,2,"\0")` — it fires only when `ext=="snd"`
(case-insensitive) AND `data[0]==0 && data[1]==0 && data[7]==0`. The
five members must share bytes with **zeros at offsets {0,1,7}**; 300 zero
bytes is the minimal such content and is what I measured. The tracked r68
member `posttable_nomatch.wav` starts `"ufo-r68 post-tab…"` (bytes 0,1,7 all
nonzero, sha `6373923f…`) — renaming *it* `.snd` yields the au-dispatch
verdict (`can't find Sun/NeXT/DEC identifier`, measured on `nm_riffx.snd`),
falsifying the sndr clause. Do not reuse r68 bytes for this family.

## 1. Ext-gated CHECK rows vs pure post-table dispatch — exactly one runtime gate

`auto_detect_format` (formats.c:66-271) holds **131 CHECK invocations**
(lines 78-248), of which **130 compile in this build** (the `adx` row at
formats.c:165 sits inside `#if 0`). Distinct return types: 78.
("~97 rows" in the brief undercounts — exact enumeration in
`runs/check-row-census.tsv`.)

All compile-time guards: `#if USING_FFMPEG` (act:93 + the whole
ffmpeg-bridge block 143-245), `#if HAVE_SNDFILE` (sds:137), `#if
HAVE_SF_FORMAT_MPC2K` (mpc2k:139). **Exactly ONE row is gated at runtime by
the input's extension**: formats.c:247-248 —

```
if (ext && !strcasecmp(ext, "snd"))
CHECK(sndr  , 7, 1, ""     , 0,  2, "\0")
```

`ext` is `lsx_find_file_extension(path)` passed at formats.c:911 — NULL for
`-` inputs, the basename suffix for named arms (fifo paths included, and
`|<cmd> x.snd` spellings — the extension is parsed off the pipe string).
Conjunct probes (`logs/` + legs): `nm_z01.snd` (bytes 0,1 zero; byte 7 =
0x41) → NOT sndr → au dispatch; `nm_z0.snd`/`nm_z1.snd` (one of bytes 0/1
nonzero) → NOT sndr → au dispatch; `nm_zeros.SND` (uppercase) → **sndr
detected** (strcasecmp). All three content conjuncts and the
case-insensitive ext gate are individually load-bearing.

Post-miss dispatch (formats.c:920-933, unchanged since r68): `io_type==pipe`
(`|` spelling only) → assume-`sox`; no ext → `can't determine type`;
ext unknown → `no handler for file extension`; ext known →
`sox_find_format(ext, true)` = names[] lookup → reader verdict. Extension →
handler for the members in play:

| suffix | handler (names[] site) | zero-bytes verdict (named arms) |
|---|---|---|
| `.wav` | wav (wav.c:2147 `{wav,wavpcm,amb}`) | `RIFF header not found` |
| `.bin`/`.xyz` | none | `no handler for file extension '<e>'` (path-free) |
| `.txw` | txw (tx16w.c:404) | file: `invalid filetype ID in input file header, != LM8953`; fifo: `input must be a file, not a pipe` (seek gate tx16w.c:90) |
| `.f32` | f4 raw (f4-fmt.c:21 `RAW_FORMAT1(f4,"f32",32,0,FLOAT)` → names `{f4,f32}`) | **decode 75 samples, exit 0** — no header, no seek needed |
| `.snd` | au (au.c:221 `{au,snd}`) — *but* the ext-gated CHECK(sndr) preempts when bytes 0,1,7 are zero | zeros → detected `sndr` → `invalid rate value` (sounder.c:13-31: type field 0 → rate field 0 fails); nonzero-at-gates → `can't find Sun/NeXT/DEC identifier` |
| `.sndr` | sndr (sounder.c:45 `{"sndr"}`) | ext dispatch direct to sndr reader — `invalid header` on RIFF content (measured `nm_riffx.sndr`) |
| `.au` | au (au.c:221) | `can't find Sun/NeXT/DEC identifier` |
| `.raw` | raw (raw-fmt.c:26) | `sample rate is zero or negative` (lsx_rawstart rate check) |

## 2. Predicted partition table — measured on identical zero bytes (sha `d13d4a8b…`), 4-arm set

Signature = (`sox_detected_format`, `sox_route`, exit, samples, error-post-`':`):

| member | file | stdin_pipe | redirected_fd | fifo_path | groups |
|---|---|---|---|---|---|
| `*.wav` | (null,none,2,–,`RIFF header not found`) | (null,none,2,–,can't-determine `-'`) | same as pipe | = file | **2** |
| `*.bin` | (null,none,2,–,`no handler for file extension 'bin'`) | can't-determine | same | = file | **2** |
| `*.txw` | (null,none,2,–,`invalid filetype ID in input file header, != LM8953`) | can't-determine | same | (null,none,2,–,`input must be a file, not a pipe`) | **3** |
| `*.f32` | (null,none,**0**,**75**,null) | can't-determine | same | = file | **2** |
| `*.snd` | (**sndr**,native,2,–,`invalid rate value`) | can't-determine | same | = file | **2** |
| `*.au` (extra) | `can't find Sun/NeXT/DEC identifier` | can't-determine | same | = file | 2 |
| `*.raw` (extra) | `sample rate is zero or negative` | can't-determine | same | = file | 2 |
| `*.xyz` (extra) | `no handler for file extension 'xyz'` | can't-determine | same | = file | 2 |
| `noext` (hazard) | `can't determine type of file '<abs path>'` | can't-determine | same | `no handler for file extension 'nm_zeros_noext'` (mktemp --suffix added a dot) | 2 |

Rows marked "extra" are coverage confirmations of the same classes
(reader-verdict / no-handler are families, not singletons) — not needed as
members. All 48 legs + stderr in `runs/matrix-r69.tsv`, `logs/`.

**Detection-fork column**: every member except `*.snd` has
`sox_detected_format` identical on all 4 arms (null, or — for the r68
txw-style content — its type). `*.snd` alone yields
`sndr`{file,fifo} vs `null`{pipe,redir}: **DETECTION itself forks on the
name** — the first tracked member with that property.

**f32 is also a new verdict class**: the first member whose
extension-dispatched reader *succeeds* on named arms (75 samples, exit 0,
`sox_route` stays `"none"` since detection was null — the receipt's group
signature still separates it).

Receipt-safety notes for the author (verified against the current code):
all five declared member names carry extensions → `transport_error`/
`stderr_tail` stay path-free (`RIFF header not found`,
`no handler for file extension 'bin'`, `invalid filetype ID in input file
header, != LM8953`, `input must be a file, not a pipe`,
`invalid rate value`, none). A no-extension member would embed the mkdtemp
nonce in `error` — the r68-documented hazard; `noext` leg above confirms the
file-arm string carries the absolute path. Member names must keep their
declared suffixes.

## 3. Committed-receipt census — 5 of 130 compiled CHECK rows have EVER first-matched

Receipt inventory: **4670 committed** `corpus/live/runs/*/measurements.json`
(`git ls-files corpus/live/runs | wc -l` = 4670). Canonical ledger = 114
rows in `corpus/live/r68-author/ledger-r68.tsv`, columns
`pos ⇒ exit ⇒ receipt path ⇒ failures-summary` (row 01 = `-normal`, then the
r68 pair, then 10 r67 transport rows, then r63-r66 autodetect family, then
the pre-autodetect depth/channel/rate/probe rows).

Detection-bearing rows: **29 of 114** carry `sox_detected_format != null`
(row 02, posttable-nomatch, carries the field explicitly `null` — the only
no-match row). Scanning every committed receipt for the field gives exactly
five detected types + null:

| detected | CHECK row | ledger rows carrying it | first-match row(s) |
|---|---|---|---|
| `act` | formats.c:93 (RIFF@0 + 0x84@256) | 11 (route_84, all six r64 valids, preempt_act, dec_act) | act |
| `gsrt` | :81 ("ring.bin"@16, len≥25) | 6 (preempt_gsrt, preempt_both, lengate_25, +arm rows) | gsrt |
| `hcom` | :90 (FSSD@65 + HCOM@128, len≥132) | 6 (preempt_hcom, dec_hcom, lengate_132, +arm rows) | hcom |
| `wav` | :95 (RIFF+WAVE) | 5 (route_00, lengate_gsrt_24, lengate_hcom_131 + arm rows) | wav-RIFF |
| `txw` | :86 ("LM8953"@0) | 1 (txw_piperefuse) | txw |

wav's sibling rows :96 (RIFX) and :97 (RF64) are **dead-verified**: every
tracked member starts `RIFF` or `LM8953`/ASCII (hex survey of all
`round-5[5-9],6[0-8]` members); no committed member carries RIFX/RF64
bytes, so those rows can never have fired.

**Census result** (`runs/check-row-census.tsv`, per-row):
131 invocations → 130 compiled rows → **5 ever first-match** (gsrt:81,
txw:86, hcom:90, act:93, wav:95) → **125 compiled rows dead**
(96.2% coverage gap), 1 never-compiled (adx:165 `#if 0`). The ext-gated
**sndr:248 is dead today** — no tracked member is named `*.snd`. Landing the
r69 `.snd` member makes it the 6th ever-fired row and the first whose match
is name-conditional.

## 4. Minimal member set + insertion map

The partition classes and the smallest set covering them (all identical
300-zero bytes, sha `d13d4a8b…`):

| class | member | named-arm outcome | groups | new? |
|---|---|---|---|---|
| ext→reader verdict, seek-indifferent | `extgate.wav` | `RIFF header not found` | 2 | class already tracked via r68 `.wav` — still needed for the identical-bytes claim |
| ext→no-handler | `extgate.bin` | `no handler for file extension 'bin'` | 2 | new member |
| ext→seek-gated reader | `extgate.txw` | file `invalid filetype ID…` / fifo `input must be a file, not a pipe` | **3** | new member (first 3-group member; file≠fifo inside the named arm) |
| ext→reader decode success | `extgate.f32` | decode 75, exit 0 | 2 | new class (first successful extension-dispatch) |
| ext-gated CHECK → detection+reader | `extgate.snd` | `sndr` detected → `invalid rate value` | 2 | **new class** (first detection fork) |

Five members, one shared content: `bytes(300)` written to five names —
`corpus/live/round-69/extgate.{wav,bin,txw,f32,snd}` (any basename works;
the suffix is the axis). All anonymous-`{stdin_pipe,redirected_fd}` arms
read `can't determine type of  \`-'`; all receipts path-free.

Predicted ledger: **114 → 119 rows**, all five new rows **exit 1** (fork
pinned in `failures`), ledger exits 49/65 → **49/70**; additive-only →
prior-114 byte-identical. Members sha `d13d4a8b…` each.

Insertion map (mirrors r68 exactly; line numbers from HEAD `7b8d423`):

- `corpus/fixtures/measure_audio.py`: `TRANSPORT_R69_MEMBERS` dict after
  `TRANSPORT_R68_MEMBERS` (~L207); five flags
  `--probe-transport-extgate-{wav,bin,txw,f32,snd}-r69` after L428;
  `sum()` +5 (L430); forward flags newest-first at the head of the
  build-command list (~L443); member-select block newest-first **before**
  the r68 block (L618); `mode`/`suffix` chain heads (~L1052/~L1072). Reuse
  `transport_matrix`/`transport_entry` unchanged — the fifo name carries
  the member's own basename, so the `.snd` ext gate fires on `fifo_path`
  too (measured).
- `corpus/fixtures/build_artifacts.py`: `build_ui_extgate_r69_probe()`
  writing `bytes(300)` ×5 (same literal-write pattern as
  `build_ui_posttable_r68_probe` L192); flags + dispatch next to the r68
  pair (~L1002-1008).

Caveats handed forward:

- `.snd` detection also fires on `|cmd` spellings (ext parsed off the pipe
  string) — outside the 4-arm set; footnote only.
- `stderr_tail` scrubs ` \`[^']*' `→` \`<input>' ` — covers the fifo path in
  FAIL lines; `error` uses post-`':` verdict — all five members' errors are
  path-free (measured). No code change needed.
- `.SND`/`.Snd` names work identically (strcasecmp) — keep `.snd`.

## Unresolved / limits

- `lsx_find_file_extension` on `-` returns NULL by construction; other
  builds could differ — within-host determinism only (SoX_ng 14.8.0.1).
- `.snd` fifo leg relies on the ext gate seeing the fifo basename — measured
  true here; the reader's `invalid rate value` is seek-indifferent
  (sounder.c reads the 8-B header inline).
- The census counts **first-match** only; shadowed rows that would match
  under a different ordering aren't distinguishable from committed
  receipts (detection records only the winner).
- No claim beyond local fixture behavior on this host/toolchain; no
  fidelity/conformance claim.

Artifacts: `corpus/live/r69-scout/{probes/ (16 members), run_matrix.sh,
runs/matrix-r69.tsv (48 legs), runs/check-row-census.tsv (131 rows),
logs/ (48 matrix + 4 conjunct-leg stderrs), runs/probe-shas.txt}`.
