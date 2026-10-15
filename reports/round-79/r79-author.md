# R79 AUTHOR (audio) — the pw-loopback frontier, armed and run

Round 79. Repo `~/Projects/shokunin/audio-shokunin` @ HEAD
`a2616f732253ed90110ba16a223ec7d10224740c` (`r78 LOG: adjudicator
ADMIT-corr`). Host `plazir27`. Toolchain: PipeWire **1.6.8** (pw-loopback /
pw-cat / pw-record / pw-cli / pw-dump / pw-link), pactl **17.0-98-gb096**,
Python **3.14.7** (numpy 2.5.3), Linux **7.2.3-arch1-3**.

**Seat: AUTHOR. Tracked edits: exactly one file —
`corpus/fixtures/measure_audio.py` (+2737 / −3, sha256
`4ee754b3fa7dab6c…`).** The three rewritten lines are the prepend-only
wiring every prior round used: the one-mode exclusivity sum, the `mode`
ternary, the `suffix` ternary — every earlier flag's value is unchanged.
Receipts: `corpus/live/runs/20261015T072219089606Z-capture-r79/` and
`…T072746218296Z-capture-r79/` (both `failures: {}`, exit 0, 66 r79 legs
each), copied to `corpus/live/r79-author/` with sha256s. **No commit — the
tree is left dirty by design.**

---

## 0. Provenance — what this seat inherited, and the honest delta

The r79 arm's symbols (`--probe-capture-r79`, the `_loopback_r79_*` family,
eight entry functions, the argparse/mode/suffix wiring) were written by a
**previous author seat that died on a rate limit at 03:31 local, before it
ran or verified anything** — `corpus/fixtures/__pycache__` was still clean,
no `-capture-r79` receipt existed, and no `corpus/live/r79-author/`
directory existed. This seat read the inherited code, compiled it, ran it,
and found that **every one of the eight entries blocked vacuously** on its
first execution (`a probe null sink/monitor did not enumerate`). It then
repaired the arm and ran it to green. The repairs are listed here in full
because they are this seat's actual contribution; the measured laws that
follow are what the repaired arm produced.

| # | inherited defect (measured) | repair | evidence |
| --- | --- | --- | --- |
| 1 | every entry blocked: `_playback_r78_wait_source("<sink>.monitor")` can **never** succeed on this host — the graph's monitor ports are owned by the SINK node (`<sink>:monitor_FL/FR`), while the helper requires the port tag to equal the source name (`<sink>.monitor`) | r79-local `_loopback_r79_wait_monitor` (pactl source listing **and** the real port owner's monitor ports), r78 helper untouched | §2.1; `git show HEAD:` confirms the helper is committed r78 code |
| 2 | the pw-cat fallback leg played the tag tone into the **shared default sink** (the scout's own named contamination class) | `_loopback_r79_write_silence` + per-leg `feed_content`/`content_witness` | §7, §10 |
| 3 | the record entry ran its loopback through the **blocking** runner, so all four record legs spawned after it was reaped: `no target node available` (d2a/d2b), default-sink fallback (d2c), ENOENT on the D17 pin | `_loopback_r79_watch_sample` + a directly-spawned live loopback held for 16.7 s | §5 |
| 4 | the capture-side default-source arms failed on a host with no default source, with no named outcome | `_loopback_r79_default_source_probe`, `_loopback_r79_unnegotiated`, class `capture_default_source_unnegotiated` (per-leg correlate) | §3 |
| 5 | the matrix bands were mis-calibrated for the mono mix (they reject the measured `0.5·(L+R)`), and the strict tone classifier cannot see a mono mix | measured bands + a cross-leg half-gain ratio; mix legs pinned by the two-tone signature | §4 |
| 6 | `-C @SRC@` expected-producer never substituted → a passing leg reported a failure | substitute the token in the expectation | §3 |
| 7 | the pw-cat arm asserted the reported `Latency` param is invariant (r78's finding) | named verdict `latency_param_inert` / `latency_param_tracks_request`; the **prop** stays the hard assertion | §7 |
| 8 | the filter-chain conf.d legs matched node names by the leg's long name while the fragment publishes the short tag → healthy loaders read as empty; the parse warning was cut off by the tail window | match the fragment's short tag; keep a redacted `stderr_scan` | §8 |
| 9 | cosmetic: `if "r79" + … and <real check>` — an always-true operand | removed (behaviour identical) | — |

Nothing in the r76/r77/r78 families was relaxed or renamed: the diff is
prepend-only apart from the three wiring lines, and the r78 regression bar
is untouched (see §11 for the one r78-side defect this seat found and
deliberately did **not** "fix").

---

## 1. Declared move

`--probe-capture-r79`: eight entries, **66 legs**, over the pw-loopback
surface the scout measured on 2026-10-14 — shape and prop syntax, the `-C`
capture lattice, the `-P` playback lattice, the channel matrix, `pw-record
--target` against loopback nodes, hot-plug both directions, the pw-cat
`node.latency` vector, and the filter-chain module. Every leg carries the
r78 conventions now live: tap-witness bound/ran provenance, the spawn-time
`default.audio.sink`/`default.audio.source` metadata oracle, named
confounds (`default_reasserted`, `foreign-node`, …), pw-link port-readiness
gates on every fresh sink/source, stall envelopes, and `coverage_blocked`
surfacing. **Two formal runs** (B 07:22:19Z, C 07:27:46Z) on byte-identical
frozen code: `failures: {}`, exit 0, empty stderr, zero surviving nodes,
68/70 verdict fields identical between runs.

## 2. Headline — the eight entries

| # | entry | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | shape / props | **CONFIRMED** | one client, two nodes: `input.<n>` (Stream/Input/Audio, `input_FL/FR` + `monitor_FL/FR`), `output.<n>` (Stream/Output/Audio, `output_FL/FR`, **no** inputs); both carry the same `client.id` (104) and one `node.link-group`; zero links join the pair |
| 2 | `-C` capture lattice (12 legs) | **TWO ARMS, ONE CONDITIONAL** | `stream.capture.sink=true` + resolvable sink → that sink's **monitor** (`:monitor_*` ports); the prop with a garbage/source target → the **default sink monitor**; **without** the prop the fallback is the session **default source** — and on this host there is **no metadata/WirePlumber default source** (the `default.audio.source` key and the `wpctl` default marker are absent; a pactl-enumerable source can still exist — the two authorities differ), so those legs publish `input.<n>` **unnegotiated** (zero ports, `suspended`, zero links): `capture_default_source_unnegotiated` |
| 3 | `-P` playback lattice (10 legs) | **r78 LAW VERBATIM** | resolvable sink honored (two distinct probe sinks); **every** unresolvable/inapplicable form — garbage, a source name, `0`, the absent flag, a garbage `-o target.object` — lands the **current default sink** (SPDIF), rc −9 at bound, empty stderr; `-o target.object` beats `-P` with a silent-sink control; `-o node.autoconnect=false` publishes unlinked |
| 4 | channel matrix (4 legs) | **POSITION DRIVES THE MIX** | `-m '[ MONO ]'` / `-m MONO` → both channels carry both components at **2269.3** (exactly half the passthrough's **4538.6**, ratio **0.500**); `-c 1` with the default 2-entry position is **inert** (stereo passthrough, 4538.6/2.8 mirrored); port names stay `*_FL/*_FR` in all four legs |
| 5 | `pw-record --target` (4+1 legs) | **THREE ARMS + D17** | `output.<lb>` → the copied stream's own ports, tone carried (14/14 `mine` windows); `input.<lb>` **+ prop** → the capture node's `monitor_*` ports, tone carried; `input.<lb>` **without** the prop → default-source arm (unnegotiated here); the prop on `output.<lb>` → default sink monitor, silence; D17 manual `monitor_*` pins rc=0, tone carried |
| 6 | hot-plug (3 legs) | **FOLLOWS BOTH WAYS** | unload the playback target → re-link to the default sink; **load** the named target mid-route → re-link to it; unload the capture target → re-link to the **default sink monitor**; client alive throughout (rc −9 at bound), tone stops before every unload |
| 7 | pw-cat `node.latency` (13 legs) | **PROP VERBATIM; PARAM TRACKS THE REQUEST HERE** | `--latency 10ms` → `480/48000`, `--latency 256` → `256/48000`, `-P node.latency=1024/48000` → `1024/48000`; **prop beats flag** (`2048/48000`); `--latency 0` non-fatal argv error (no prop) while `-P node.latency=0` stores `0`; the reported `Latency` param takes **3 distinct values** that track the request → `latency_param_tracks_request` |
| 8 | filter-chain (7 conf.d + 5 pw-cli legs) | **CLIENT-SCOPED, PARSE-SOFT / RUNTIME-FATAL** | a good fragment publishes both chain nodes into the live session and they die with the loader; a syntax error is a **warning** (`conf_load() … error in config … Mismatched bracket`) with later fragments still loading; a bad label **with** `nofail` is silent, **without** it exits the loader **rc=254**; `unload-module @module:22` is refused (`unknown module`) and `quit` is the teardown; the DSP witness is `0.5·(L+R)` on FL with FR digital silence |

---

## 3. FRONTIER 2 — the `-C` capture lattice, and its condition

`-P` pinned to a probe-owned null sink on **every** leg (fail-closed); tone
only where the capture side is probe-owned. Twelve legs:

| leg | `-C` / props | producers of `input.<n>` | content | verdict |
| --- | --- | --- | --- | --- |
| b01 | `<ns_a>` + `stream.capture.sink=true` | `<ns_a>` (`:monitor_*` ports) | **tone** | honored |
| b02 | `<ns_a>`, no prop | *(none)* | — | `capture_default_source_unnegotiated` |
| b03 | `<ns_a>.monitor` | *(none)* | — | unnegotiated; `.monitor` never resolves (verbatim `target.object`) |
| b04 | real `Audio/Source` (Mic) | that source (`:capture_*` ports) | silence (host) | honored |
| b05 | `no_such_node_r79` | *(none)* | — | unnegotiated |
| b06 | `0` | *(none)* | — | `0` is not a don't-link idiom |
| b07 | `<ns_a>` + `stream.capture.sink=false` | *(none)* | — | false ≡ absent |
| b08 | real source **+ `target.object=<ns_a>` prop** | `<ns_a>` | **tone** | **prop beats flag** |
| b09 | `target.object=no_such_node_r79` + sink prop | **SPDIF** (default sink monitor) | silence | r78 fallback law on the capture side |
| b10 | sink + prop + `node.autoconnect=false` | *(none)* | — | honored, never links |
| b11 | `node.autoconnect=false`, no target | *(none)* | — | honored |
| b12 | real source + sink prop | **SPDIF** | silence | a source made "a sink" → default sink monitor |

Intent vs consumption is recorded per leg: b02/b03/b05/b07 keep the
requested name in `target.object` while producing from somewhere else
(`target_object_lies`), which is the r78 provenance trap on the capture
side — the lattice asserts that at least one such lie exists.

### 3.1 Correction to the scout — the fallback is **conditional**

The scout measured (2026-10-14) that `-C <unresolvable>` **without** the
sink prop lands the session **default source** (the DualSense mic) — an
ungated fallback pw-record does not have. This arm measures the *condition*
under which that happens, and this host no longer satisfies it:

* `pw-metadata -n default 0 default.audio.source` — **no key**;
  `wpctl status` marks **no source** with `*`.
* A plain `pw-record` with **no** `--target` dies
  `stream node <n> error: no target node available` /
  `remote error: … res:-2 (No such file or directory): no target node
  available` — the session manager has no source to hand out.
* Writing the key does **not** help: `pw-metadata … default.audio.source
  '{"name":"…Line__source"}'` reads back immediately, then WirePlumber
  **drops the key again mid-leg**; keeping that source **running** changes
  nothing (`exp-default-source-r79.json`, `exp-capture-ports-r79.json`).
* Consequently the loopback's capture stream publishes `input.<n>` with
  **zero ports** and state `suspended` and never links. The arm names this
  `capture_default_source_unnegotiated` and requires the observed shape
  (published, zero ports both ways, zero links) **plus** the per-leg
  correlate (`source_meta is None` at that leg, or the run-level probe
  class `no_target_node`). With a live default source the old strictness
  applies unchanged.
* The law is real, not retired: in run 3 (07:04Z) a **concurrent lane's**
  `r86ctl_src` was the live default source for legs b01–b04, and b02/b03
  **did** link to it — the fallback follows the *live* default, foreign or
  not. By b05 that source was gone and the same legs went unnegotiated.
  The authority flaps under multi-seat load, which is why the correlate is
  read per leg rather than once per entry.

---

## 4. FRONTIER 3 — the `-P` playback lattice (r78's law, verbatim)

| leg | `-P` / props | consumers of `output.<n>` | tap | verdict |
| --- | --- | --- | --- | --- |
| c01 | `<ns_b>` | `<ns_b>` | 40 `mine` | honored |
| c02 | `<ns_b2>` | `<ns_b2>` | 40 `mine` | honored |
| c03 | `no_such_sink_r79` | **SPDIF** | 0 | default sink |
| c04 | a real **source** name | **SPDIF** | 0 | default sink |
| c05 | `0` | **SPDIF** | 0 | `0` is not a don't-link idiom |
| c06 | *(absent)* | **SPDIF** | 0 | default sink |
| c07 | `<ns_b>` + `-o target.object=<ns_b2>` | `<ns_b2>` | 40 | **prop beats flag** — with a control tap on the flag sink: 0 `mine`, bound+ran |
| c08 | `<ns_b>` + `-o node.autoconnect=false` | *(none)* | 0 | honored, never links |
| c09 | `<ns_b>` + `-o stream.capture.sink=true` | `<ns_b>` | 40 | decoration on playback |
| c10 | `<ns_b>` + `-o target.object=no_such_sink_r79` | **SPDIF** | 0 | prop beats flag → fallback |

Ungated, rc −9 at bound, empty stderr: only topology and content separate
honored from fallback — exactly the r78 write-side law. The c07 control tap
is the round's one *negative* content pin (a tap that must carry nothing).

---

## 5. FRONTIER 4 — the channel matrix, calibrated

Tone L 1 kHz / R 1.5 kHz at amp 8192 played into `ns_a`, captured by the
loopback, played into `ns_b`, tapped and analysed per channel with the r78
Hann coherent-gain DTFT:

| leg | flags | props (`audio.channels` / `position`) | measured channels | verdict |
| --- | --- | --- | --- | --- |
| cm1 | `-c 1 -m '[ MONO ]'` | 1 / `[ MONO ]` | 2269.3 both, peak 8191 | **0.5·(L+R) mix** |
| cm2 | `-c 1` | 1 / `[ FL, FR ]` | ch0 4538.6/2.8, ch1 4.0/4538.6, peak 8192 | **inert** — stereo passthrough |
| cm3 | `-m '[ MONO ]'` | 2 / `[ MONO ]` | 2269.3 both | downmix |
| cm4 | `-m MONO` | 2 / `MONO` | 2269.3 both | same as bracketed |

The arm asserts the **absolute** signature *and* the cross-leg relation
`mix ≈ 0.5 × stereo` (measured ratio **0.500** on cm1/cm3/cm4 in both runs,
band 0.35–0.65) — so a band that is merely wide cannot pass a wrong mix.
The scout's own classifier values (4095.3 / 2047.6) sit inside the same
bands. Mix legs are content-pinned by this signature; the strict tone
classifier cannot see a mono mix (both channels carry both components), so
on those legs the tap only *forbids* our tag windows.

---

## 6. FRONTIER 5 — `pw-record --target` against loopback nodes

One live loopback (`-C <ns_a> -i stream.capture.sink=true -P <ns_b>`, held
16.7 s, route re-verified at 1.2 / 2.6 / 16.7 s), four bounded record legs
**during** it, then D17:

| leg | `--target` | prop | record stream's producers | content | verdict |
| --- | --- | --- | --- | --- | --- |
| d2a | `input.<lb>` | — | *(stream dies `no_target_node`)* | — | `capture_default_source_unnegotiated` |
| d2b | `output.<lb>` | — | `output.<lb>:output_*` | **14/14 tone** | honored |
| d2c | `input.<lb>` | `stream.capture.sink=true` | `input.<lb>:monitor_*` | **14/14 tone** | honored |
| d2d | `output.<lb>` | `stream.capture.sink=true` | **SPDIF** monitor | 0 | prop demotes the lookup to the sink domain |
| D17 | `0` | — | manual pins → `input.<lb>:monitor_*` | **14/14 tone** | pins rc=0 both |

D17 reproduces the scout's manual-pin leg exactly (both pins rc=0, tone
carried), which is also the proof that the loopback's `monitor_*` ports are
real data ports. d2a is the capture-side twin of §3.1: without the prop the
target is resolved in the **source** domain, `input.<lb>` is not a source,
and the fallback needs a default source that this session does not have.

---

## 7. FRONTIER 6 — hot-plug both ways

Tone stops **before** every unload (silence-before-loss), so a silent
re-link can never be mistaken for content:

| leg | event | before | after | client |
| --- | --- | --- | --- | --- |
| e1 | unload the playback target | `output.<lb>` → `<hp>` (tap 16 `mine`) | → **SPDIF** | **alive** (rc −9 at bound) |
| e2 | load the named target mid-route | `output.<lb>` → **SPDIF** | → **`<hp2>`** (tap 37 `mine`) | alive |
| e3 | unload the capture target | `input.<lb>` ← `<ns_a>` | ← **SPDIF monitor** (`:monitor_*` ports), playback side untouched | alive |

The client never exits and never logs; only topology and content move.

---

## 8. FRONTIER 7 — pw-cat `node.latency`, and what the param really is

| leg | request | measured `node.latency` | note |
| --- | --- | --- | --- |
| d01 | *(default)* | `4800/48000` | 100 ms default |
| d02 | `--latency 10ms` | `480/48000` | |
| d03 | `--latency 256` | `256/48000` | samples at the source rate |
| d04 | `-P node.latency=480` | `480` | literal, unvalidated |
| d05 | `-P node.latency=1024/48000` | `1024/48000` | |
| d06 | `--latency 5ms -P node.latency=2048/48000` | `2048/48000` | **prop beats flag** |
| d07 | `--latency 0` | *(absent)* | non-fatal argv error, stream still plays |
| d08 | `-P node.latency=0` | `0` | stored unvalidated |
| d09 | `--latency 500ms` | `24000/48000` | |
| d10 | `--latency 10ms -P node.force-latency=true` | `480/48000` + prop | no change to `node.latency` |
| d11 | `+ stream.capture.sink=true`, valid target | `4800/48000` | prop recorded on the node, target honored |
| d12 | `+ stream.capture.sink=true`, garbage target | `4800/48000` | **lands the default sink** — topology verdict, fed **digital silence** |
| d13 | `-P node.autoconnect=false` | `4800/48000` | never links, stalls to the bound |

**Correction to r78's "param is inert" reading.** The r78 author measured
the reported `Latency` param byte-identical across ten legs; on this host
it takes **three** distinct values that track the request (quantum 0.0 /
1.0 / 2.0, rate 0 / 0 / 512) — `latency_param_tracks_request`. Both are
named verdicts; the arm's hard assertion stays on the **prop**, which is
what the tool actually stores.

---

## 9. FRONTIER 8 — the filter-chain module

**conf.d path** (`PIPEWIRE_CONFIG_DIR` → `pipewire -c filter-chain.conf`,
scratch dirs, one fragment set per leg):

| leg | fragments | loader | chain node in session | stderr | verdict |
| --- | --- | --- | --- | --- | --- |
| f1 | good (builtin mixer) | alive | **yes** (`mix_input…_f1`) | — | published; DSP witness below; nodes gone after kill |
| f2 | one syntax error | **alive** | no | `conf_load() … error in config '<cfg>/10-bad.conf': Mismatched bracket` | **parse error is fail-soft** |
| f3 | good(10) + bad(20) | alive | **yes** | warning for the bad one | later fragments still load |
| f3b | bad(10) + good(20) | alive | **yes** | warning for the bad one | **per-fragment**: a bad one does not poison later ones |
| f4 | bad label + `nofail` | alive | no | *(empty)* | tolerated, silent |
| f5 | bad label, **no** `nofail` | **exits rc=254** | no | *(empty)* | **runtime graph error is fatal to the loader** |
| f6 | base only (control) | alive | no | — | control |

**pw-cli path** (one line per command): `load-module …` replies
`1 = @module:22` and publishes both nodes (client-scoped, gone on `quit`);
`unload-module @module:22` is **refused** (`Error: "unload-module: unknown
module '@module:22'"`) with the nodes still up — teardown is client exit,
and a scraped reply id is never fed to `destroy`; a bad label and malformed
args both refuse with `Could not load module` while the daemon stays alive.

**DSP witness** (identical for the conf.d and pw-cli paths): tone pinned
onto the chain's input ports → tap on the probe sink reads
`FL 4095.6 @1 kHz+1.5 kHz, FR 0.0, peak 8192` — the analytic mono
`0.5·(L+R)` on FL and **digital silence on FR**, because
`stream.dont-remix = true` forbids the upmix. Every fragment pins
`playback.props.target.object` to a probe-owned sink (the scout's second
contamination defect: never `node.passive`, never an implicit destination).

---

## 10. Guards, fail-closed rules, teardown

* **Fail-closed tone guard**: a tone-fed loopback leg is refused at spawn
  unless its effective playback target (`-o target.object` beating `-P`) is
  in the probe-owned set — the scout's harness defect armed permanently.
* **Silence where the destination is shared**: the pw-cat fallback leg
  (d12) is fed digital silence and declares
  `content_witness = declined_shared_default`; the fallback legs of the
  `-C`/`-P` lattices are never fed (topology + tap evidence only).
* **Port-readiness gates** on every fresh sink (`:playback_*` in-ports) and
  every monitor (`pactl` source listing **and** `<sink>:monitor_*` ports).
* **Tap provenance**: every sample records the tap's own producers, so a
  `mine` window only counts while the tap listens to the claimed node; a
  tap that never bound is a named confound, never a pass.
* **Stall envelopes**: `node.autoconnect=false` and the `-C`/`-P` stalls
  are bounded and killed (`killed_at_bound` is the expected shape for a
  persistent client; rc −9 is not a failure).
* **Teardown**: every probe sink is unloaded by the module id captured at
  **our** load (never a by-name lookup, never a foreign module); post-checks
  assert the sinks are gone and **no** `r79lb_`/`r79fc_` node survives
  (`own_nodes_after: []` in all eight entries, both runs). The loopback legs
  are tagged `r79lb_<pid>_<leg>` and the filter-chain nodes `r79fc_<pid>_*`.
* **Coverage honesty**: a blocked entry reports `blocked` +
  `coverage_blocked` with **zero** failures — the receipt never launders
  missing coverage as green. Both formal receipts contain no blocked entry.

## 11. The one r78-side defect found (reported, deliberately not "fixed")

`_playback_r78_wait_source("<sink>.monitor")` (committed r78 code, used by
`capture_unlinked_zeros_r78_probe` and `capture_parec_fix_r78_probe`)
requires the monitor's port tag to equal the source name; on this host the
monitor's ports are owned by the sink (`<sink>:monitor_FL/FR`) and no
`.monitor` node exists in `pw-link -o` at any point. Those two r78 arms
therefore return `monitor_source.enumerated: false` and **block** — visible
in the committed-fold receipts from 05:50:13Z onward (the 05:37:41Z receipt
still shows `True` from the pre-fold variant). The r79 baseline counted
those two blocked arms as "clean" because blocked entries carry no
failures; the class is `coverage_blocked`, not green.

This seat did **not** change the r78 helper: un-blocking it would relax an
inherited guard and change prior-row behaviour, which this round's
conventions forbid. The r79 arm uses its own corrected gate instead. The
finding is handed up as-is.

---

## 12. Contamination ledger

**This arm's tone never reaches the shared default sink.** Every tone-fed
leg is probe-owned by construction (the fail-closed guard), and the single
leg whose destination *is* the shared default sink (pw-cat d12) is fed
digital silence. The arm only *reads* the shared sink: monitor taps, and
the `-C`/record fallback legs that capture its monitor.

**Named, measured foreign event** (run A, 07:16Z): the `b09` leg — whose
capture side is the shared default sink monitor by design — tapped a
tag-shaped tone (1 kHz/1.5 kHz) at peaks **11997/8997**, above this arm's
8192 tag ceiling, while the leg had **never been fed**. A concurrent lane's
tone on the shared sink was being forwarded into a probe sink by the very
fallback the leg measures. **Fold correction (critic C3 / scribe F1):**
the `foreign_tone_on_shared_monitor` class is **named-but-unexecuted** —
it fired in the informal 07:16Z window and recurs in **no** formal
receipt; and the amplitude ceiling alone could never prove origin (our
own tone summed with a foreign tone reads above it). The gate is now an
ORIGIN witness: the excuse requires a producer on the leg's capture path
carrying none of this run's `r79lb_`/`r79fc_` tags, with the >8192 peak
kept as corroboration. No foreign producer → the tone is unexplained
contamination and FAILS. It did not recur in runs B/C. Other contention seen in the window: a concurrent lane's
`r86ctl_ns`/`r86ctl_src` null sink/source (transiently the session default
source, §3.1), one foreign `aplay` (the r78-era stale process), and the
game-dev lane's battery load. `host_is_quiet=false` is recorded on the
receipts; no sibling `measure_audio` probe was live at any formal-run
snapshot (`host-window.log`).

**Diagnostics' footprint**: `default.audio.source` was written once and
deleted again (pre/post state both "key absent", verified), and the default
source was held open ~10 s for one measurement; no other shared state was
touched.

## 13. Labrat dispatch (exactly one, read-only, advisory)

Hypothesis H1 — "is the measured surface *documented* shipped material or
undocumented behaviour?" — reported **PARTIAL**: `capture.props` /
`playback.props` pinning and `node.autoconnect` are documented by example
in `/usr/share/pipewire/filter-chain/*.conf` (11 fragments; the eq6 example
even uses `node.passive = true`, which is exactly the scout's second leak
mechanism), while `stream.capture.sink` appears in WirePlumber's
shipped material (`/usr/share/doc/wireplumber/NEWS.rst:1553`,
`/usr/share/wireplumber/scripts/lib/common-utils.lua:42`). **Scribe F2
correction (fold):** the earlier wording "and in **no** PipeWire config or
man page" is falsified — `stream.capture.sink` is named in the shipped
`libpipewire-module-protocol-simple(7)` man page (gzipped; the labrat's
"absent" was bounded by undecoded gzip). It remains absent from PipeWire's
own `*.conf` fragments. No measured claim here depends on this — the probe
made zero writes, spawned zero processes, and its output is advisory.

## 14. Confidence, and what this arm does not claim

* **High** (two independent runs, content + topology witnesses): §2 shape
  and prop syntax, §4 playback lattice, §5 matrix signature + half-gain
  ratio, §6 record arms and D17, §7 hot-plug all three legs, §8 the latency
  prop vector and prop-beats-flag, §9 conf.d/pw-cli failure split and the
  DSP witness.
* **High for the conditional, medium for the mechanism**: the
  `capture_default_source_unnegotiated` class is measured in four windows
  with four independent witnesses (metadata key absent, `wpctl` default
  marker absent, plain `pw-record` failing `no target node available`,
  write-the-key-and-run-it changing nothing) — but *why* WirePlumber holds
  no metadata default source on this host (device set, priority rules,
  the DualSense mic's removal; pactl can still enumerate sources — the
  scribe's "no default source" wording is hereby bound to the
  metadata/wpctl authority) is **not** established here.
* **Medium**: `latency_param_tracks_request` is one host/sink/version
  observation against r78's single-value reading; the arm records the set
  and names whichever holds.
* **Not claimed**: any perceived-quality claim; any claim about a real ALSA
  sink's latency behaviour (only null sinks and the SPDIF monitor were
  measured); no claim that the capture-side fallback is dead on other hosts
  or with other session managers; `-m` matrix syntax beyond the four forms;
  LADSPA/FFmpeg filter-chain node types (only `builtin`); `filter-chain.conf.d`
  merge order beyond "a bad fragment does not poison later ones".
* **Cosmetic wart, declared**: the capture lattice's `target_requested`
  leaf echoes the **raw** argv token where a leg used the `@SRC@`
  placeholder (the *verdict* uses the substituted name); left as-is rather
  than re-freezing a verified artifact.

## 15. Write scope, replay, and tree state

* **Tracked edits by this seat: one file** —
  `corpus/fixtures/measure_audio.py` (+2737/−3, sha256
  `4ee754b3fa7dab6c…`, `python3 -m py_compile` clean). `SHONEN.md` was
  already modified before this seat's first command (the r79 baseline
  reports the same) and is untouched here.
* **The `py_compile` cache was restored**: running the compile modified the
  tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`; it
  was `git checkout`-ed back to HEAD so the round's tracked diff is exactly
  the source edit. Re-running the compile re-creates it (a cache, not
  evidence — the compile-clean claim is reproducible from the frozen hash).
* **Untracked artifacts**: `corpus/live/r79-author/` (receipts, diagnostics,
  host snapshots, `RECEIPTS.md`) and this report. No commit, no push.
* **Replay**: `python3 corpus/fixtures/measure_audio.py --probe-capture-r79`
  from the repo root (writes its own receipt under `corpus/live/runs/` and
  prints `{"receipt": …, "failures": {}}`; exit 0 on a clean run). The two
  formal runs are reproducible with `corpus/live/r79-author/formal-runs.sh`.
