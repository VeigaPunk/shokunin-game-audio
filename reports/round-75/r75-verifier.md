# R75 verifier — independent replay of the committed consumer-breadth-2 arm

Round: 75. Wave: `shokunin-train-20261101-w14`. Seat: verifier (LEAF — no
subagents, no git mutation). Repo `/home/vgpnk/Projects/shokunin/audio-shokunin`.
Replayed on committed tree at HEAD **`db46fba`** == the author commit
(`git log`: `db46fba` on top of `6f905c3`; nothing after it). Fixture blob
`30eac683a94c3434274b56c4773b84ce577a3ac4` == `HEAD:corpus/fixtures/
measure_audio.py`. Note: this blob is **not** the scribe-audited revision B
(`b0153958c28d`, snapshotted 16:45:27Z) — a further filter-hardening edit
landed between the scribe's last snapshot and the commit (16:52:07Z). All
evidence below is on the committed blob.

Host gates re-measured this session: `pacat 17.0-98-gb096` / libpulse 17.0.0,
`aplay 1.2.16`, `ffplay n9.0.1`, `pactl info` → `Server Name: PulseAudio (on
PipeWire 1.6.8)`, `Default Sink: …USB_Audio-00.HiFi__SPDIF__sink` — matches
the author's claimed environment leaf-for-leaf.

## Method / receipts

The fixture has **no `--runs` flag** — receipt output is hardcoded to
`corpus/live/runs/<stamp>-consumers2-r75/` (`measure_audio.py:3803`). Per the
r74-verifier convention I ran the mode twice on the committed tree and copied
both fresh receipts into this seat's scope.

| run | command | exit | receipt |
|---|---|---|---|
| 1 | `python3 corpus/fixtures/measure_audio.py --probe-consumers2-r75` | 0 | `runs/20261014T165717676332Z-consumers2-r75/` → `corpus/live/r75-verifier/runs/…/` |
| 2 | same | 0 | `runs/20261014T165821738609Z-consumers2-r75/` → `corpus/live/r75-verifier/runs/…/` |

Each run ~54 s wall. Stdout captures `corpus/live/r75-verifier/
run{1,2}.stdout.json` (`{"failures": {}}` both); stderr logs 0 bytes both.

**What was byte-compared** (naming it per the F24 caveat): the dispatch asked
for verdict groups + verdict fields byte-compared, excluding `stderr_tail`
leaves. I did strictly more — **full-receipt `sha256sum` + `cmp`-equivalent
byte compare, all leaves including every `stderr_tail`** — plus a parsed
leaf-level diff to confirm zero structural deltas. Under the committed blob
the exclusion proved unnecessary: no leaf of any kind differed.

## Result: byte-level

- **run1 ≡ run2 ≡ all three author receipts**: sha256
  `0829a5986bb6ca70c5c9b06b50bf661e9c8dbbe7cddefac5b16e860e2c2a76d4`, 99159
  bytes, on `…T164819343934Z`, `…T164913129596Z`, `…T165017429491Z` (author),
  `…T165717676332Z`, `…T165821738609Z` (mine). **5/5 consecutive committed-blob
  receipts byte-identical** — determinism claim reproduced, not merely
  field-stable. `failures: {}` in every entry; mode `probe-consumers2-r75`;
  29 measurement keys.
- **Prior rows byte-identical**: parsed compare of the author's cited receipt
  vs the committed r73 receipt `20261014T145502288182Z-consumers-r73` — all 17
  shared base rows (`ui`,`ui_alt`,`ui_third`,`impact`×3,`movement`×3,
  `ambience`×3,`stem`,`stem_sections`,`stem_layer`×3) and all 7 non-mode
  top-level sections (`thresholds`, `distinctness`, `ui_/impact_/movement_/
  ambience_family_comparisons`, `sections`) serialize identically. Zero diffs.
  (Author claimed "6 meta sections"; the identical non-mode set is actually 7
  keys — stronger than stated.) Since my receipts are byte-identical to the
  author's, the same holds for my runs.
- **Insertion-only**: `git show db46fba` on the fixture deletes exactly 3
  lines — the mutex `sum([...])` line, the `mode` chain, the `suffix` chain —
  each re-emitted verbatim plus the r75 clause (`measure_audio.py:3025`,
  `:3782`, `:3802`); +936 additions, matching the report's +936/−3. No prior
  probe-row code touched; no receipts tracked.
- **`paplay -` fact spot-check**: `paplay - < /dev/null` → `open(): No such
  file or directory`, rc=1 — the literal-filename claim verified on this host.
  `strings /usr/bin/paplay | grep -c sf_open_fd` → 1 (the fd-entry claim).

## F21/F24 status under the committed blob (honest bound)

The scribe's F21 stands as a code-read fact: `_PACAT_RACY_TAIL`
(`measure_audio.py:2014-2017`) keeps the `Time:.*Latency:` alternative
`$`-anchored, and I re-verified on the committed regex that
`Time: 0.000 sec; Latency: 34750 usec.` → **not matched** (while
`Draining connection to server.`, `Playback stream drained.`,
`Connected to device … (index: N)`, `Stream started.` are all matched).
What changed vs the scribe's post-fix family: with every *competitor* line
filtered, the unfiltered `Time:` line deterministically occupies the tail on
successful paplay legs — and it did in all 5 committed-blob receipts. The
drifted receipts the scribe measured (16:41–16:46Z, shas `876c810c`,
`db4b827a`, `a3047c8a`, `3b91594b`) were produced by **pre-commit revisions**
(blob `b0153958c28d` ≠ committed `30eac683a94c`) and are no longer in `runs/`
(only the three canonical + my two remain). Two latent surfaces remain worth
recording, not as defects but as bounds: (a) the surviving `Latency: 34750
usec.` value is coupled to this host's USB sink parameters — a different host
could byte-diverge on that leaf; (b) `fifo_no_writer` tails go through
`_consumer2_tail` without the `_FFPLAY_STATUS_TAIL`/`ALSA lib` prefilters
(`:2381`), so ffplay's `nan` progress fragment lands there — stable 5/5 here,
timing-dependent in principle.

## Per-claim adjudication (all verified on my run receipts, byte-equal to author's)

### (a) 27/27 verdict groups transport-invariant — AGREE

Exactly the author's table, reproduced verbatim on all 5 receipts: dec_act +
dec_hcom → paplay `[0,'s16le 1ch 8000Hz',None]` / aplay `[0,'WAVE',None]` /
ffplay `[0,'wav'|'hcom',0,False]`; all 5 extsuffix + posttable_nomatch +
txw_piperefuse → paplay `[1,None,'Failed to open audio file.']` / aplay
`[0,'raw data',None]` / ffplay `[0,None,0,True]`. `transport_fork: false`
×27, zero fork-failure rows. Distinct detect strings on dec_hcom (`hcom`)
confirm the signature reads lavf detection, not a constant.

### (b) paplay .snd name axis dead / sf_open_fd name-blind — AGREE

`paplay_name_axis`: all 7 legs (`file:`/`fifo:` × {snd,wav,bin} + rfd) rc=1
`'Failed to open audio file.'` on identical `extsuffix_nomatch.snd` bytes —
the r73 pw-cat `.snd` fork does not transfer. `raw_bypass` rc=0 on the same
bytes (decode-layer skip). Reproduced.

### (c) aplay name axis invariant-accept — AGREE

`aplay_name_axis`: `axis.{snd,wav,bin}` fifos → `[0,'raw data', spec
u8/8000/mono]` ×3 — polarity-inverted vs paplay, as claimed.

### (d) ffplay carries no mpv-style refresh-seek fork — AGREE

All 9 members × 4 arms: `avio_seeks: 0` including the seekable file arm
(`Statistics: 600 bytes read, 0 seeks` tails on dec_act/dec_hcom). The hcom
inverted-seek fork is an mpv-ism, not a lavf property — confirmed by a second
lavf consumer. `ffplay_duration` carries the residual seekable-bit evidence
(`00:00:04.00` file vs `N/A` stdin on the startpos cell) outside the verdict
signature, as described.

### (e) ffplay rc is never the verdict — AGREE

`ffplay_invalid: true` with `exit_code: 0` on all 7 reject members × 4 arms
and on `fifo_empty_writer` (rc=0, `Invalid data found`). The verdict rides on
detect+seek+invalid fields exactly as claimed.

### (f) paplay ops — AGREE

`daemon_live` pactl rc=0 (server name + SPDIF sink recorded);
`daemon_gate_dead` rc=1 `wall_s: 0.001` tail `pa_context_connect() failed:
Connection refused`; `gate_ordering_dead_fifo` + `fifo_no_writer` both
`blocked, wchan wait_for_partner, sigterm_immune false, exit_code -15` with
**no** connection-error tail — input-first ordering confirmed (opposite of
pw-cat's gate-first); `fifo_empty_writer` rc=1.

### (g) aplay ops — AGREE

`device_census` = 12 playback devices across 3 cards; `plugin_census`
{null, pipewire, default} all present; `device_axis` on dec_act: null/
default/pipewire rc=0 WAVE, `hw_first` (hw:0,0 = USB Audio) rc=1
`aplay: set_params:1404: Channels count non available` — the kernel-device
format-coupled rejection, host-coupled as disclosed; `fifo_no_writer`
blocked, `sigterm_immune: true` (TERM caught: `Aborted by signal
Terminated...`, still stuck) → SIGKILL → **-9**; `fifo_empty_writer` rc=1
`read_header:2973: read error`.

### (h) ffplay ops — AGREE

`sdl_driver_axis` {dummy,pulse,alsa} all rc=0 wav on this host (dummy is the
pinned sink; pulse/alsa gates recorded per leg); `fifo_no_writer` blocked,
wchan `hrtimer_nanosleep` (read-thread open block), `sigterm_immune: false`,
graceful **exit 123** — the third kill class; `ffplay_startpos` = the path
fork: file `seeks:2, 641580 B, duration 00:00:04.00` vs stdin
`could_not_seek, seeks:0, 384044 B, N/A`, both rc=0 — fork in the seek PATH,
not extent, as claimed; `fifo_empty_writer` rc=0 invalid.

### (i) kill-class triplet — AGREE

Reproduced exactly: paplay `wait_for_partner`/TERM-kills/**-15**, aplay
`wait_for_partner`/TERM-caught-still-stuck/**-9**, ffplay
`hrtimer_nanosleep`/TERM-graceful/**123** (pw-cat r73/r74 = TERM-immune/-9 —
three distinct classes on the identical writerless-fifo cell).

### (j) commit/package hygiene — AGREE

Commit `db46fba` touches only `corpus/fixtures/measure_audio.py` (+936/−3)
and `reports/round-75/r75-author.md`; the author's `corpus/live/r75-author/`
is empty (its artifacts were the fixture + receipts, consistent with the
recovery-dispatch note); no receipts committed. My runs dirtied no tracked
file (`git status --porcelain` non-`??` set is empty).

## Verdict

**AGREE on all claim items (a–j).** The committed arm replays byte-for-byte:
my two independent runs and the author's three receipts share one sha256
(`0829a5986b…`) — a stronger result than the F24-scoped field compare the
dispatch anticipated, under a fixture revision later than the one the scribe
audited. The verdict layer is transport-invariant 27/27 with zero forks, all
three ops surfaces pin their declared gates and kill classes, prior rows are
byte-identical to the committed r73 receipt, and the diff is insertion-only.
Carried caveat: byte-stability of the `stderr_tail` leaves relies on this
host's stable pacat latency parameter and kill-phase timing (F21's
mis-anchored `Time:` alternative is still in the committed regex) — the
verdict-carrying fields are the durable surface.
