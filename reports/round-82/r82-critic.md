# r82 CRITIC — adversarial review of the landed r82 family (aa03c347)

Host `plazir27`, 2026-10-15 17:30–17:55Z (-03). Seat: CRITIC (leaf).
Reviewed the committed `--probe-ffmpeg-r82` family (fixture block
`measure_audio.py:14176`–`16311`, +2 170 lines, 8 entries/76 legs) against
`reports/round-82/r82-{scout,boundary,baseline,author}.md` and the four
committed receipts. All criticism is of the *pinning choices and gate
coverage*, not of the measurements themselves — the underlying scout and
boundary work is strong and the receipts are honest.

**Probe environment:** loadavg ~90 on 32 cores during all probes (r83a
sibling lane live with its own null sinks and pw-record taps; the family
replay itself ran in a quieter audio-graph window). Seat namespace
`r82c_*`. **No tracked writes, no commits, no `set-default-*`.**
Evidence: `corpus/live/r82-critic/` (MANIFEST.md + raw outputs) and the
untracked replay receipt
`corpus/live/runs/20261015T203551336204Z-ffmpeg-r82/measurements.json`.

## Verdict

**ADMIT-with-findings.** The family reproduces cleanly — my own replay on
the committed code under load ≈90 returned `{"failures": {}}`, 76 legs,
all armed pins held (c3 3× eio_251, a5 params_251, a6=44100, p7
device_flag, star_vs_pactl agree, max sample gap 0.209 s). The receipts
are internally consistent (independent depth-2 probe verified 4×76 legs,
zero failures, envelope leaves in-envelope). **But two verdict-bearing
legs can green without exercising their claim** (F1, F2), the content
witness is forgeable by named sibling classes (F3), and the inherited
name-verified unload is a substring predicate that can select and kill a
foreign module (F4 — proven live). None of these fired in the committed
runs; all are latent, and F1/F2/F3-collision are cheap to fix.

## Findings, ranked

### F1 — `a2_hw_free_pwheld` deterministically tests a weaker premise than the claim (claim-fidelity error, plus ungated holder)

The scout's measured cell was capture `hw:0,0` **while PW held the same
subdevice's playback direction** via the `Speaker__sink` (api.alsa.path
`hw:Audio,0` — the same PCM as `hw:0,0`). The fixture instead takes
`sorted(sinks_on_card)[0]` — alphabetically
`…HiFi__Headphones__sink`, which is `hw:Audio,1` — a **different
subdevice**. All four committed receipts and my replay record
`holder_consumers=[Headphones__sink]`. Different-subdevice concurrency is
the trivial ALSA case; the same-subdevice opposite-direction split (the
actual claim — "independent per direction") is never exercised.
Compounding it: `holder_consumers` is *recorded but never gated*
(`measure_audio.py:16122–16123`), so even the weaker premise can pass
vacuously if the holder's stream never linked (e.g., sink suspended,
routed elsewhere). Secondary defect: `r82-author.md` §6 asserts the holder
ran "on `…Speaker__sink`" — the report misquotes its own committed
receipts (all show Headphones). **Fix shape:** select the sink whose
`aplay_device` equals `hw:{card},{cap_dev_device}` (Speaker here), fall
back to a named `coverage_blocked` when none maps, and gate
`holder_consumers == [that sink]`.

### F2 — `t2_cap_*` cannot see the failure class it claims to exclude (sustained-zeros blind spot)

The capture-loss legs gate: rc=0, a pre-unload `producers==[ns]` sample,
re-link `producers==[default]` ≤0.8 s, `post_sizes[-1] > post_sizes[0]`,
riff finalized. **No content gate at any point.** The r85 family's own
`unlinked_sustained_zeros` class — file growing at rate with zeros —
satisfies every one of these gates. `cap_tone` (`mine_windows`,
`mine_spans`) is recorded into the leg but *never asserted*. This is not
hypothetical: committed `final3` `t2_cap_r2` shows `mine_spans
[[0.2,1.1]]` — **zero tag-tone windows after the 1.202 s unload** (the
pump re-linked to the default at ~1.4 s and ran to 2.0 s, so the tone was
present on the captured monitor but absent from the wav classification) —
and the leg is green. The verdict "keeps growing + still receiving our
tone" reduces to "flushed ≥1 chunk post-unlink". (Also note the growth
check's granularity: ffmpeg flushes at 256 KiB — the first bytes appear
~1.3–1.6 s in; pre-unlink growth is never observed at all.)
**Fix shape:** require ≥1 `mine` window strictly post-unlink (the data is
already recorded), mirroring the t1 `post_mine` gate.

### F3 — the tag-tone witness is unauthenticated: same-family reruns and a quantified r78 collision

`FFPW_R82_TONE_L_HZ=1210.0`/`R_HZ=1780.0` are **constants**, and nothing
excludes a concurrent `--probe-ffmpeg-r82` run (no flock anywhere in the
harness). Two overlapping runs share the default-sink monitor and produce
indistinguishable tags: proven — a foreign-named pump playing the r82
pair into `r82c_tgt` reads `carries_tone=True`, 20/20 mine windows. Both
directions are poisoned: p1/p4/p5/p8 get forged corroboration, p0/p6/p12
get false "LEAKED" reds.

Sharper still: the author's defense ("a pair DISTINCT from the r78
1k/1.5k tag") predates the r78 constants actually being **pid-keyed**:
`PLAYBACK_R78_TONE_L_HZ = 997 + (pid%4)*211`, `R = L+503`. An r78-family
run with `pid % 4 == 1` emits **(1208, 1711)** — inside r82's ±6%
windows (|1210−1208|=2 ≤ 72.6; |1780−1711|=69 ≤ 106.8). Classifier run on
synthesized wavs: **(1208,1711) → mine 10/10**; the other three pid
classes → 0. So one-in-four concurrent r78-family runs can forge `mine` on
the shared default sink — and r78/r79-family legs demonstrably do put tag
tones on the shared default in this lane's history (r78 `pactl` default
legs, r85b churn). **Fix shape:** derive the pair from the pid like r78
does (but in a disjoint band — e.g., 3–4 kHz), or widen the mine gate to
require pid-correlated structure (amplitude modulation pattern, per-run
dither seed is already there but unused by the classifier).

### F4 — `_gst_r81_unload_own`'s "name-verified" index is a substring match — proven to select and kill a foreign module (inherited helper, still live)

`_gst_r81_sink_module_index` tests `"module-null-sink" in ln and
f"sink_name={sink_name}" in ln` — substring containment. Demonstrated
live in my namespace: with only `r82c_a2` loaded (index 536870921), the
lookup for **`r82c_a` (absent)** returned 536870921 and
`_gst_r81_unload_own(None, "r82c_a")` fired — `exit_code 0`, the `r82c_a2`
module destroyed. The `skipped:not_listed` safety never engages because
the substring matched. In this family the queried name is
`r82ff_ns_<pid>`: any foreign `r82ff_ns_<pid><suffix>` — e.g., a
same-family sibling whose pid merely *extends* ours (`1234` vs `12345`),
or a foreign lane reusing the prefix — would be selected and unloaded by
our loss legs/teardown, and conversely their teardown can kill ours. The
boundary lane's own teardown already once unloaded a stale index; this
shows the guard's ownership proof is weaker than claimed. (Residual
TOCTOU between the re-read and the unload call is separate and smaller.)
**Fix shape:** anchor the match — `f"sink_name={sink_name}"` followed by
tab/whitespace/end, or parse the `sink_name=` field to equality.

### F5 — ambient env non-hermeticity: `PULSE_SINK`/`PIPEWIRE_PROPS`/`PULSE_SOURCE` leak into legs and taps

`_ffpw_r82_leg`/`_ffpw_r82_pump`/`_ffpw_r82_tap` spawn with `env=None`
unless the leg itself sets `env_extra` — the process inherits the
operator's whole environment. Proven: `PULSE_SINK=r82c_tgt ffmpeg -f
pulse` (no `-device`) → `target.object=r82c_tgt`, `consumers=[r82c_tgt]`;
control → `target.object=None`, consumers=[SPDIF]. Exposed legs:
`p8_no_device`, `p11_env_target` (both assert "no target / default
routing"), plus ambient `PIPEWIRE_PROPS`/`PULSE_SOURCE` on every leg
without `env_extra`. The f0/f1 ffplay legs DO strip
`SDL_AUDIODRIVER`/`PULSE_SINK` — the hygiene pattern exists but coverage
is partial. On a host with exported audio env (redirected desktop
sessions), p8/p11 produce false reds **and** push a real stream onto an
unintended sink. **Fix shape:** scrub `PULSE_SINK`/`PULSE_SOURCE`/
`PIPEWIRE_PROPS`/`SDL_AUDIODRIVER` in the leg runner's default env, as
f0/f1 already do explicitly.

### F6 — "leg-time default" is actually entry-start default — stale-compare reds + undeclared contamination on a foreign sink

`default`/`defsrc` come from `_ffpw_r82_entry_head` (pactl at entry
construction) and are reused across every leg of a 30–60 s entry — the
t1/t2 rep loop "re-reads" `default` but `_ffpw_r82_default_sink` returns
the frozen inventory value. Under default churn (the r85b/r78_def_sink
class this lane sees routinely), every `_landed_on`/`@DEFAULT_*@`/
re-link comparison runs against the stale name → fail-closed reds (the
author's own runs hit this class in the *r79* rows). The worse direction:
when the live default has moved to a **foreign-owned** sink, our fallback
legs still inject the bounded tag tone into *that* sink — contamination
of a foreign object, beyond the declared `contamination` leaf (which
discloses the *shared* default, not "whatever the default is now").
**Fix shape:** re-read `pactl info` per leg for the compare value (keep
the entry-head value recorded alongside), or record `leg_time_default`
explicitly and gate on it.

### F7 — envelope arms: c3 admits crash-as-hang; a5's failure arm can hold green indefinitely

- **c3**: `elif killed == "wallcap" or (rc is not None and rc < 0)` —
  **any** negative rc (SIGSEGV −11, SIGABRT −6, a bytecap kill) records
  `hang_killed` and stays green. A crash during `default` connect is a
  different failure class than a hang — the arm silently absorbs it.
  Narrow the arm to `killed == "wallcap"` (and keep `wall_s` sanity).
  Assessment of admission risk: the arm itself is honest (realizations
  recorded), 0/18 measured realizations, and it can only relax one leg —
  keep it, tighten the predicate.
- **a5**: `{plugin_rc0, params_251}` is a *closed* envelope with both
  arms gated — good. Residual risk is coverage starvation, not false
  pass: while the host's pipewire-alsa capture stays broken (still
  rc=251/`arecord -D default` rc=1 as of this review — my `a5probe.err`),
  `params_251` realizes forever and the actual claim (env `node.name`
  landing on the plugin path) is never exercised while the family reads
  green. Acceptable as designed; flag it in scorecards as "armed but
  unexercised" so it isn't read as coverage.

### F8 — silent leg drops + no leg census

`c5` names its skip (`coverage_blocked`); **`c9_real_source` and
`p2_src_name` vanish silently** when no default source exists — no
`coverage_blocked`, no count check. The family's "76 legs" headline is
host-state-dependent (74 without a default source) and nothing in the
fixture asserts the census. Minor honesty gap; the labrat probe confirms
all four committed receipts did run 76.

### F9 — teardown audit misses untagged node names

`own_nodes_after` matches `r82ff_<pid>`/`r82ffx_<pid>`/ns only. Legs that
don't pass `-name` produce nodes named `Lavf63.1.101`, and ffplay
produces `ffplay` — an orphaned process of ours (the scout's own
`r82ff_ffpump` orphan class) wearing a *default* name would evade the
audit entirely. Process-group kills make it rare; the check exists to
catch exactly that tail.

### F10 — census blind spot: `ffplay`/`ffprobe` uncounted

`_playback_r78_foreign_clients` counts `ffmpeg` but not `ffplay`/`ffprobe`
comms — a foreign ffplay storm is invisible to `host_is_quiet`. Recorded
not gated, so this only weakens post-hoc attribution. Minor.

### F11 — cooperative bounds inside the event loop (latent, not realized here)

`_ffpw_r82_sample` runs `pw-dump` with `timeout=15` **inside** the leg
loop that owns timed events and the wallcap — a wedged dump delays the
unload event (and the kill) by up to its timeout. Not realized: measured
pw-dump 25–46 ms under load ≈90, max sample gap 0.209 s. Keep as a noted
fragility; a nonblocking dump (or threading it off the loop) would
harden the timed-event semantics.

### F12 — dead gate: the e-legs' "refusal must not produce audio" check never fires

`e1`–`e6` pass the wav path positionally but never pass `out_path`, so
`leg["out"]` is `None` → the `out.get("exists") and bytes>44` guard at
`measure_audio.py:15969–15972` is unreachable for all six legs (contrast
the capture `_refusal` which does get `out`). Harmless today — these
failures happen before header write — but it's an armed-looking check
that isn't armed.

### F13 — stderr-pipe starvation can mislabel a flood as `hang_killed`

Legs run `stderr=PIPE` drained only at exit; `-loglevel warning` keeps it
theoretical, but a warning-flood would block ffmpeg mid-leg → wallcap →
recorded as the c3 hang arm. Cheap hardening: drain stderr in the loop or
`stderr` to a bounded file like the taps.

## What survived the attack (worth saying)

- The **link-table verdicts are sound**: `consumers`/`producers` are
  object-id joins keyed by client pid — the core claims (fallback
  routing, re-link targets, producers=[ns]) cannot be forged by foreign
  audio; the tone is corroboration, which is why F3 poisons
  corroboration but not the link claims themselves.
- The **refusal classes held under load**: `-i default` EIO rc=251 at
  0.087–0.114 s ×4 under loadavg ~90; the `.monitor` permissive hole
  reproduced (rc=0 silent fallback).
- **p7/p11** are honest recorded envelopes; **star_vs_pactl** correctly
  recorded-not-gated; `d0` rep-stability check present.
- The unload *event* recording (`verified_index`/`captured`/`recycled`)
  is genuinely good practice — F4 is about the predicate's strength, not
  the discipline.
- The mid-battery `ci6` dead-code edit between run shas is documented
  and inert.
- Independent depth-2 read-only probe (ufo-labrat): all 4 committed
  receipts fingerprint-verified — 8 entries, 76 legs each, zero
  failures, envelope leaves in-envelope; flagged pw-record rc=1 exits
  (bounded-exit quirk, consistent), one transient empty-nodes sample in
  run1 `t2_cap_r1`, and `not_listed` teardown skips — all benign.

## Probe summary (all under live load ≈90, `r82c_*` namespace)

| probe | result |
| --- | --- |
| Full `--probe-ffmpeg-r82` replay on committed tree | green, `failures:{}`, 76 legs, ~2.5 min |
| `-i default` EIO ×4 | rc=251, 0.087–0.114 s (c3 arm still eio_251) |
| `.monitor` bogus-name fallback | rc=0, silent (hole live) |
| Unload-index substring (`r82c_a` vs `r82c_a2`) | returned foreign index, **fired a real unload on the wrong module** |
| Ambient `PULSE_SINK` on no-`-device` playback | target.object + consumers steered to env sink |
| Foreign-node same-tag tap | `mine` 20/20 — witness unauthenticated |
| r78 pid%4==1 pair (1208/1711) vs r82 classifier | `mine` 10/10 — collision proven |
| `ffmpeg -f alsa -i default` / `arecord -D default` | rc=251 / rc=1 — a5 `params_251` still the live state |
| Module/node/process residue | zero `r82c_*` modules, zero tagged nodes, tracked tree clean |

## Remaining risks / blockers

- F1 needs the Speaker↔device map selection fix to actually exercise the
  claimed split; until then the a2 row's green is overstated.
- F2/F3 are one-line/one-constant fixes; both are corroboration-layer
  issues — the ledger's link-level claims remain trustworthy.
- F4 is inherited from `_gst_r81_*`; fixing it here fixes every family
  using it (r81 family included) — worth a shared-helper patch, not a
  local one.
- `sustained_zeros`-class regression in ffmpeg's capture path would pass
  today's t2 unwitnessed (F2) — the one behavioral regression I'd want
  covered before this family is called load-bearing.
- Nothing blocks the ledger standing; no seat-blocking defect found.

Report ends. No tracked edits, no commits, no pushes; seat objects
`r82c_*` fully torn down.
