# r72-scout — libsndfile 1.2.2 transport matrix + 3-decoder verdict lattice

Seat: scout (leaf). Wave: `shokunin-train-20261101-w11`. Lane: audio. Repo: `audio-shokunin`.
Scope: this report + `corpus/live/r72-scout/` (scratch) only. No fixture edits (author seat owns the tracked change).

Decoder under test: **libsndfile 1.2.2-4** (`/usr/lib/libsndfile.so.1` →
`libsndfile.so.1.0.37`; `sf_version_string()` = `libsndfile-1.2.2`; CLI:
`/usr/bin/sndfile-info`, `/usr/bin/sndfile-convert`). Member set: the canonical
9 of `TRANSPORT_R71_MEMBERS` (`measure_audio.py:556`), transports
`{file, stdin_pipe, redirected_fd, fifo_path}` with the r67/r70 fifo protocol
(one-shot write + writer lingers; `fifo_feed`/`reap_fifo_orphans` reused from
the fixture).

Tooling note (seat rule): no LSP server answered in this session — the MCP
surface exposes only the `rea` RE toolset, no `definition`/`references`
device. Symbol tracing below is therefore textual (`read`/`grep` on
`corpus/fixtures/measure_audio.py`, cited by line); no semantic claims are
made from grep output alone.

## Headline

Measured the full 9-member × 4-transport libsndfile matrix in the r71
ffprobe-arm shape (ctypes `sf_open`/`sf_open_fd` detection + `sf_readf_short`
decode, one bounded child process per leg, 15 s arm timeout). Verdicts:

- **transport fork: exactly one member.** `extsuffix_snd` forks on the
  **name axis**: `{file, fifo_path}` open `RAW (header-less)/U-Law` (500
  frames read), `{stdin_pipe, redirected_fd}` → `Format not recognised.` —
  the same `{named}/{anonymous}` partition as sox's sndr gate, reproduced
  here at the API boundary (`sf_open(path)` vs `sf_open_fd(0)`). All other 8
  members are transport-invariant, including unseekable pipes.
- **unique tier confirmed transport-invariant**: `txw_piperefuse` →
  `File contains data in an unimplemented format.` on **all 4 arms**
  (magic recognized, no TXW reader in this build) — distinct from
  `Format not recognised.` for true no-match bytes.
- `dec_act`/`dec_hcom` decode as **WAV (Microsoft)/Signed 16 bit PCM, 278
  frames on all 4 arms** (libsndfile labels the hcom- and act-polyglots WAV;
  no HCOM/ACT reader involved).
- **Claim test** (verbatim wave claim: “sox-only: txw-seekable/.f32-named;
  sndfile-only: .snd-named; ffmpeg superset on detect”):
  1. *sox-only* — **CONFIRMED exactly** (4 cells, see lattice).
  2. *sndfile-only: .snd-named* — **FALSIFIED as an exclusive class**: sox
     also accepts both `.snd`-named cells (`sndr`, 504 samples). The measured
     class is `{sox, sndfile}-accept / ffmpeg-reject`; the *mechanism*
     (post-sniff extension fallback) and the ffmpeg divergence are
     sndfile-specific, the acceptance is not.
  3. *ffmpeg superset on detect* — **FALSIFIED**: ffmpeg’s detect set (8
     cells) is a strict **subset** of both sndfile’s (10) and sox’s (14).
     Measured nesting: **ffmpeg ⊂ sndfile ⊂ sox** (detect cells); no
     coverage-superset reading holds (nor a format-label superset: ffmpeg
     `{wav,hcom}`, sndfile `{WAV/PCM16, RAW|ULAW}`, sox
     `{act,hcom,txw,sndr}`).
- Cross-checks: run1 ≡ run2 byte-identical (same sha256, full receipt);
  **36/36 cells equal** to the frontier seat’s independent harness
  (`frontier-sndfile/runs/sndfile-matrix.json`); **72/72** sox+ffmpeg rows
  equal to the frontier’s receipt extraction.
- Discrepancy flagged for the author: `fa-sndfile.md`’s table says
  `.f32` sox decode **75**; the committed receipts (all 8 runs of
  `probe-transport-extsuffix-f32-r69`, byte-stable) say **128** samples
  (512 B / 4 B f32; r69 adjudicator/author/verifier all recorded 128). Use 128.

## The measured libsndfile matrix (this seat)

Format labels are the `sf_command` major/subtype names. “REJ” = open fails
`Format not recognised.`; “REFUSED” = open fails
`File contains data in an unimplemented format.`.

| member (`corpus/live/…`) | file | stdin_pipe | redirected_fd | fifo_path | fork | sndfile-info file / fifo (exit 0 always) | sndfile-convert (file) |
|---|---|---|---|---|---|---|---|
| `dec_act` `round-66/pair_dec_act.wav` | WAV/PCM16 278 fr | = | = | = | no | `0x00010002` / `0x00010002` (Frames 278) | exit 0 |
| `dec_hcom` `round-66/pair_dec_hcom.wav` | WAV/PCM16 278 fr | = | = | = | no | `0x00010002` / `0x00010002` (278) | exit 0 |
| `posttable_nomatch` `round-68/posttable_nomatch.wav` | REJ | = | = | = | no | `Format not recognised.` / same | exit 1 |
| `txw_piperefuse` `round-68/txw_piperefuse.wav` | REFUSED | = | = | = | no | unimplemented / unimplemented | exit 1 |
| `extsuffix_wav` `round-69/extsuffix_nomatch.wav` | REJ | = | = | = | no | `Format not recognised.` / same | exit 1 |
| `extsuffix_bin` `…/extsuffix_nomatch.bin` | REJ | = | = | = | no | same | exit 1 |
| `extsuffix_txw` `…/extsuffix_nomatch.txw` | REJ | = | = | = | no | same | exit 1 |
| `extsuffix_f32` `…/extsuffix_nomatch.f32` | REJ | = | = | = | no | same | exit 1 |
| `extsuffix_snd` `…/extsuffix_nomatch.snd` | RAW\|ULAW 500 fr | REJ | REJ | RAW\|ULAW 500 fr | **YES** | `0x00040010` (Frames 512) / `0x00040010` (**Frames unknown**) | exit 0 |

Per-arm numbers for the fork member: `.snd` file arm `format=0x40010`,
`frames=512`, 8 kHz mono, `sf_seekable=true`, `read_frames=500`; `.snd` fifo
arm identical except `frames=9223372036854775807` (INT64_MAX, length unknown)
and `sf_seekable=false`; anonymous arms `sf_strerror(NULL)` =
`Format not recognised.`. `sf_format_check` was true on all 10 opened arms.

## The 3-decoder verdict lattice (36 cells)

Sources: sox = latest-per-mode committed receipts (`extract_baselines.py`
records the exact receipt dir per member); ffmpeg = r71 receipt
`20261014T142028085688Z-ffprobe-transport-r71/measurements.json` (ffprobe
entries byte-identical to the earlier `141033` run — measured); sndfile =
`runs/sndfile-matrix-run1.json`. Accept predicates: sox `exit==0 &
samples≠None`, ffmpeg `ffmpeg_exit==0`, sndfile `opened & read_frames>0`.

**Accept classes** (`lattice.json` `classes`):

| class | n | cells |
|---|---|---|
| sox + ffmpeg + sndfile | 5 | `dec_act/file`, `dec_hcom/{file,stdin_pipe,redirected_fd,fifo_path}` |
| ffmpeg + sndfile | 3 | `dec_act/{stdin_pipe,redirected_fd,fifo_path}` (sox’s act→ffmpeg bridge can’t reopen pipes) |
| sox + sndfile | 2 | `extsuffix_snd/{file,fifo_path}` |
| **sox only** | 4 | `txw_piperefuse/{file,redirected_fd}`, `extsuffix_f32/{file,fifo_path}` |
| **ffmpeg only** | 0 | — |
| **sndfile only** | 0 | — |
| none | 22 | posttable×4, extsuffix_wav×4, extsuffix_bin×4, extsuffix_txw×4, extsuffix_f32/{stdin_pipe,redirected_fd}, extsuffix_snd/{stdin_pipe,redirected_fd}, txw_piperefuse/{stdin_pipe,fifo_path} |

`sndfile_refused` (third tier, not an accept) marks 4 more cells:
`txw_piperefuse` on all 4 transports — 2 of them sit inside “sox only”
(seekable arms, where sox decodes 64), 2 inside “none” (pipe arms, where sox
also fails).

**Detect cells** (sox `sox_detected_format≠None`; ffmpeg `ffprobe_format≠None`;
sndfile `opened`): sox 14 = `dec_act`×4 + `dec_hcom`×4 + `txw`×4 +
`snd/{file,fifo_path}`; sndfile 10 = `dec_act`×4 + `dec_hcom`×4 +
`snd/{file,fifo_path}`; ffmpeg 8 = `dec_act`×4 + `dec_hcom`×4. Nesting
**ffmpeg ⊂ sndfile ⊂ sox** (both inclusions strict). Note `extsuffix_f32`
named arms are sox *accept-not-detect* (route `none`, no detected format,
decode 128); `.snd` named arms are sndfile accept-and-detect (open).

**Claim checks** (`lattice.json` `checks`): `sox_only_matches_claim=true`;
`sndfile_only_cells=[]`, `sndfile_only_matches_claim=false`; `.snd`-named is
in `sndfile_named_cells_ffmpeg_rejects` **and**
`sndfile_named_cells_sox_accepts_too`; `ffmpeg_only_accept_cells=[]`;
`ffmpeg_detect_is_superset_of={sox:false, sndfile:false}`,
`ffmpeg_detect_subset_of={sox:true, sndfile:true}`.

Mechanism note: the `.snd` fork partitions on the **name**, not seekability —
`fifo_path` is unseekable yet opens; the two anonymous arms fail. sox reaches
the same cells via its ext-gated sndr CHECK row, sndfile via the post-sniff
extension fallback, ffmpeg has no name axis at all.

## Handoff for `--probe-sndfile-transport-r72` (author seat)

Insertion anchors in `corpus/fixtures/measure_audio.py` (HEAD `c079aba`; this
file unmodified in the working tree — `grep sndfile` is empty):

- `:556` `TRANSPORT_R71_MEMBERS` — reuse directly (the canonical 9); no new member map needed.
- `:567` `TRANSPORT_R71_ARM_TIMEOUT_S = 15` — reuse as the arm bound.
- `:570` `ffprobe_leg` / `:666` `ffmpeg_transport_matrix` / `:687` `ffprobe_transport_entry` — the shape to mirror (per-arm leg → matrix → verdict groups + fork pin).
- `:881` argparse flag; `:883` the `sum([...]) > 1` one-mode guard; `:1091` the r71 dispatch block; `:1558` mode chain; `:1578` suffix chain. New receipt key: `f"sndfile_{member}_r72_probe"`; mode `probe-sndfile-transport-r72`; suffix `-sndfile-transport-r72`.

Leg ingredients (ctypes is stdlib — no new dependency): `SFM_READ=0x10`;
`SF_INFO` `{frames:i64, samplerate, channels, format, sections, seekable}`;
`sf_open(path)` / `sf_open_fd(fd)`; `sf_readf_short` → decode count;
`sf_strerror(NULL)` for open failure, `sf_error_str(snd)` after read;
`sf_format_check`; `sf_command` `SFC_GET_FORMAT_MAJOR_COUNT=0x1030` /
`MAJOR=0x1031` / `SUBTYPE_COUNT=0x1032` / `SUBTYPE=0x1033` for the
`WAV (Microsoft)/Signed 16 bit PCM`-style labels. Arm mapping: `file` →
`sf_open(path)`; `stdin_pipe` → `sf_open_fd(0)` with member bytes piped;
`redirected_fd` → `sf_open_fd(0)` with a **fresh** fd on the member file
(r71’s fresh-fd-per-subprocess fix); `fifo_path` → `sf_open(fifo)` with the
existing `fifo_feed` one-shot+linger writer and `reap_fifo_orphans`.

Two working leg shapes, both measured-adjacent: (a) **child process per leg**
(this seat: `sndfile_leg.py`; gives a real 15 s timeout and fresh fds by
construction; matrix wall time ≈ 19 s for 9×4 + CLI legs); (b) **in-process**
(frontier seat: `frontier-sndfile/probe_sndfile.py`; identical verdicts on
all 36 of these member×transport cells). Pick (a) if the receipt should carry
the r71-style `blocked: no verdict within 15 s` error shape.

Receipt fields per arm: `sndfile_format`, `sndfile_format_hex`,
`sndfile_format_check`, `sndfile_frames`, `sndfile_samplerate`,
`sndfile_channels`, `sndfile_seekable`, `sndfile_read_frames`,
`sndfile_error`, plus `named`/`seekable` from `TRANSPORT_R67_ARMS`. Group
signatures: decode groups key on `(format, read_frames, normalized error)`,
detect groups on `(format, normalized error)`; normalize `"No Error."` → null.
**Do not key on `SF_INFO.frames`** — on the `.snd` fifo it is INT64_MAX and
on the file 512 while the decode verdict is 500 on both; `read_frames` is the
verdict, `frames` is a length estimate.

CLI gotchas if `sndfile-info` is used for the detection leg: it **exits 0 on
every verdict** (measured 9/9 members incl. rejects); reasons live in stdout
(`Format not recognised.` / `File contains data in an unimplemented format.`);
the `Error :` line embeds the concrete input path → replace with `<input>`
for byte-stable receipts (r71 convention); on a fifo its `Frames` line prints
`unknown` for `.snd` (not a decode count). `sndfile-convert` does propagate
exit codes (0 on convert, 1 on reject — measured).

## Evidence / commands (exact)

```sh
cd ~/Projects/shokunin/audio-shokunin
python3 corpus/live/r72-scout/sndfile_leg.py path corpus/live/round-68/txw_piperefuse.wav   # exit 0; error "File contains data in an unimplemented format."
python3 corpus/live/r72-scout/sndfile_matrix.py run1   # exit 0, 18.6 s wall
python3 corpus/live/r72-scout/sndfile_matrix.py run2   # exit 0
python3 corpus/live/r72-scout/extract_baselines.py     # exit 0
python3 corpus/live/r72-scout/lattice.py               # exit 0
python3 corpus/live/r72-scout/crosscheck.py            # exit 0
```

Artifacts (all under `corpus/live/r72-scout/`):
`runs/sndfile-matrix-run1.json` ≡ `run2` (sha256 `1c4fb4bf600aec36…` — full
receipts byte-identical), `logs/info-*.txt` (18 raw `sndfile-info` outputs),
`extract_baselines.py` + `prior-verdicts.json|tsv` (sox receipts + r71
ffprobe, latest per mode; e.g. sox `txw` receipt
`20261014T142032229685Z-…`, `.snd` `20261014T142030162830Z-…`),
`lattice.py` + `lattice.json|tsv`, `crosscheck.py` + `crosscheck.json`,
`sndfile_leg.py`, `sndfile_matrix.py`.

Cross-checks: 36/36 sndfile cells equal to
`frontier-sndfile/runs/sndfile-matrix.json` (member key `posttable` ≡
`posttable_nomatch`); 72/72 sox+ffmpeg rows equal to
`frontier-sndfile/runs/prior-verdicts.tsv`; the 9 member entries are
byte-stable across the newest-vs-previous receipt of every mode (stable from
14:06 onward; the only historic dec-act diffs are 12:22–12:40-era runs,
pre-dating the r71 path-normalization correction). Re-extracting baselines
after newer receipts landed mid-session (incl. dec-act
`20261014T142154016476Z`) leaves `lattice.json` byte-identical (sha256
`feda12cbea068204…`); no timeouts, no fifo orphans, zero fixture/receipt
writes by this seat.

## Confidence & remaining unknowns

Confidence: **high** for the 36 measured cells and the lattice (two
independent harnesses agree 36/36; two runs byte-identical; baselines
cross-checked 72/72 against an independent extraction).

Unresolved:
- The wave claim’s “ffmpeg superset on detect” holds under no coverage
  reading measured here; if the intent was “ffmpeg content-probes where
  sox/sndfile need a name” (mechanism), that part is true but is not a
  superset of cells or labels — flagged for the adjudicator.
- In-process vs child-process leg equivalence is established for verdicts
  (36/36 agree) but not for the timeout path (no arm blocked in either run).
- `.snd` extension-fallback case sensitivity (`.SND`) untested in this
  corpus; frontier left it open too.
- No pure-FSSD TXW/HCOM member exists; the REFUSED tier is measured on the
  LM8953 polyglot only.
- The `.snd` decode-count gap (sndfile 500 vs sox 504 vs `frames` 512) is
  recorded, not explained — out of scope here; do not “fix” it in the receipt.
