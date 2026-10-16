# r86-author — pw-cli / pw-dump / pw-metadata / pw-top / pw-jack control-plane ledger family

Author run of the Round 86 audio task (`--probe-pwctl-r86`). A new parallel,
insertion-only family in `corpus/fixtures/measure_audio.py` carrying only
boundary-surviving claims from `r86-scout.md` as corrected by `r86-boundary.md`.
Five entries; every arm measured live on this host before landing.

## Host / toolchain

- Host `plazir27`, kernel 7.2.3-arch1-3, loadavg ~50 during runs (foreign
  sibling churn recorded as contention census, never a verdict).
- PipeWire 1.6.8, WirePlumber 0.5.17, pactl/libpulse 17.0-98-gb096
  (protocol 35), python 3.14.7, numpy 2.5.3.
- `/usr/bin/pw-jack` is a POSIX shell wrapper; JACK shim lib present
  (`/usr/lib/libjack.so.0.3.1608`); no jackd/jack_* tools.
- `TMPDIR=/home/vgpnk/Projects/shokunin/tmp` for all runs (`/tmp` near quota).

## Implementation (`corpus/fixtures/measure_audio.py`)

+1761/-3 lines; insertion-only — one family block before `main()` plus
three wiring lines (add_argument, mutex sum, dispatch) and the mode/suffix
ternary heads. File hash `5ceba94019eaaa8f1db9ac18ea15023f7e4891e844defe86711f37873059b780`.

- Namespace `r86a_<pid>` for every owned object: null-sink
  `r86a_ns_<pid>`, monitor tap `r86a_tap_<pid>`, DSP stream
  `r86a_<pid>_dsp`, private restore key `r86arole<pid>` (never `music`).
- **Family lock at a fixed lane path** — `corpus/live/measure_audio-pwctl-r86.lock`
  (flock, holder pid/ns/role written as witness). This is the r84 3-seat
  consensus fold: r85's `$TMPDIR`-scoped lock lets cross-TMPDIR same-family
  runs race; this lock is identical for every seat regardless of TMPDIR.
- Name-verified teardown reusing the r85 unload protocol: unload only the
  module whose current `sink_name=` arg byte-matches our name at the verified
  index; then `sinks_gone` (strict pactl reader), `own_nodes_after`
  (`r86a_<pid>`-tagged survivors), `meta_keys_gone` (no `r86a_` key in the
  default store). Reader failures land in `coverage_blocked`, never pass
  vacuously.
- Crash-class legs (`pw-cli </dev/null`, `pw-top` TUI TERM/KILL) run with
  `RLIMIT_CORE=0` in the child — the assertion is measured, no coredump filed.
- No `set-default-*`, no subject-0 writes, no foreign object touched.

## Legs (all boundary-surviving; falsified rows recorded or dropped)

**`pwctl_addr_r86_probe`** — the addressing split + census surface:
`ls <serial>` resolves the node, `ls <id>` does not; `info <id>` resolves,
`info <serial>` → rc0 `unknown global` (same digits, two namespaces;
`enum-params`/`set-param`/`destroy` are id-family). Class census arms the
`id N, type …` row shape and the indistinguishable-empty law
(`ls Bogus` ≡ `ls node` ≡ `ls Session` → 0 bytes rc0). pw-dump surface:
`<id>`≡`<serial>` byte-identical single-object dumps; bad id → 0B rc0;
`-C never` → 0B rc0 (positional trap) vs `-Cnever` → full dump;
`-C=never` host-bimodal → **recorded only** (`armed: False`); self-Client
law armed (each invocation = exactly 1 fresh `pw-dump` client, serials
243277→243278 across two runs); `info <metadata-id>` → 0B rc0 silent-empty
on a live object; `-r <bogus>` → rc≠0 `failed to connect` (the one real
nonzero refusal); `info all`, `list-vars`, `list-remotes` rc0; own
monitor→playback self-loop: `pw-cli info <link-id>` census fields +
`pw-cli destroy <link-id>` removes it (witnessed via census).

**`pwctl_params_r86_probe`** — enum-params typed matrix + set-param refusals:
pod-dumped {Node: Props/PropInfo/EnumFormat; Port: EnumFormat/Latency/IO/
Meta; Device: Profile/EnumProfile/EnumRoute}; remote `res:-2 ENOENT`
{Node: IO/Meta/Profile; Port: Props; Device: Props}; local `not implemented`
{Client/Factory/Module/Link/Core}; numeric `3` ≡ `EnumFormat` byte-identical;
`Bogus`/`999`/`all` → `unknown param type`. Format rows: **Port** Format
armed pod-absent (unlinked port), **Node** Format armed rc-only —
negotiation-tracked (absent in scout/boundary spot-checks, exposed this run:
`has_pod: True`), the boundary's own correction. `d_route` recorded only.
set-param refusals: `garbage`→`None` echo, `{ }`→empty pod, unknown key
stripped on re-enum, wrong-type→`None` slot, EnumFormat→remote `res:-95`,
port Latency write→rc0 echo **+ local not-implemented** (echo is a local
print; boundary correction to "silently dropped"; `minQuantum` verified
unchanged `Float 0.000000`), bad id→`unknown global`, missing json→usage.

**`pwctl_dsp_r86_probe`** — set-param Props as live DSP (tap link-validated
before the player spawns, per the r85 fold). Windowed medians on the monitor
tap, run-2 realizations: solo 8192 → `channelVolumes 0.25` **2048.0**
(exact linear) → `0.5` **4096.0** → `mute` **0.0** → reset **8191.5** →
scalar `volume: 0.25` **8192.0** (display-dead: store reads `Float 0.25`
back via enum, pactl still 100%) → pactl `25%` **128.0** (exact cubic
0.015625×) → pactl `100%` **8192.0**. Scale-coupling arm: pactl reads ~63%
after `channelVolumes=0.25` (cube root). Envelopes not point values.

**`pwctl_meta_r86_probe`** — store laws: `pw-metadata -l` ≡ `pw-cli ls
Metadata` ≡ **9 stores**; pw-dump sees a strict subset **{31,34,36,39}**
(the census gap — mechanism unread, law armed as subset). Bare ≡ `-n
default` byte-equal; bogus store 0B rc0. Live subject: set-echo →
`update:` read-back, full-replace overwrite, `type:'Spa:String'` verbatim,
absent-key read = Found-only, `-d <s> <k>` delete echo + absent-delete same
no-op echo, `-d <s>` bare wipes subject (`delete properties: id:N`). Dead
subject 99997: echo prints, nothing persists — the echo-lies law.
`-m <subj>` filters rows (unbounded stream, kill-bounded; rows all carry
the subject id; `-m 0` → subject-0 rows only). Subject 0 **read-only
baseline** — defaults enumerated, never written (scout's `default.audio.*`
write arms deliberately not encoded).

**`pwctl_tools_r86_probe`** — process surfaces: `pw-top -b -n 2`/`-n 0`
clean rc0 tables; **batch + TERM rc0** vs **TUI + TERM → SIGABRT +
`loop.c:189 remove_from_poll`** (the narrowed H1 — curses-path teardown,
not pw-top per se); TUI + KILL → SIGKILL. pw-cli stdin trichotomy:
`/dev/null` → **SIGABRT** (scout's clean-EOF row falsified, boundary's
rc134 confirmed), pipe stdin → never exits (kill-bounded SIGKILL), `quit`
→ rc0. pw-jack shim: `-p 512`→`QUANTUM=512/48000`, `-s 44100 -p 256`→
`256/44100`, `-s` alone→unset, `-v`/`-vv`→`DEBUG=3`/`4`, preset 4→5,
`-r`→`REMOTE`, `-h`/no-args/`-Z`→rc0 (`-Z` prints illegal-option+usage),
bogus payload→rc 127 `exec: not found`. pw-link: create rc0, duplicate→
**rc255 File exists** (scout's rc0 falsified), bogus port→rc255, bare/
`-I`/`-v`→rc255, `-l`/`-l -I`→rc0 listing, `-d <port-id>`→rc255,
`-d <link-id>`→rc0 unlink, `-p` junk props silently accepted + link forms.

## Green runs (identical bytes, `5ceba940…`)

| run | receipt | sha256 | verdict |
|---|---|---|---|
| 1 | `corpus/live/runs/20261016T063006268243Z-pwctl-r86/measurements.json` | `1097d9f1…f515b` | `failures: {}` |
| 2 | `corpus/live/runs/20261016T063043717745Z-pwctl-r86/measurements.json` | `fe57c1cb…3920a` | `failures: {}` |

Both: all five entries `failures: []`, `coverage_blocked: []`, all unloads
`verified_index == captured` `recycled: False`, `sinks_gone` true,
`own_nodes_after: []`, `meta_keys_gone: true`. Post-run residue check:
0 `r86a_` modules / dump objects / metadata keys / processes; default sink
& source unchanged. (The earlier dev run `20261016T062922907396Z` failed
once on the pre-fix `n_format` pod-presence arm — that byte set was
corrected, not the green pair.)

## Files changed

- `corpus/fixtures/measure_audio.py` — +1761/-3 (family block ~L23730–L25500,
  wiring ~L25568/25576/25934–25964, mode/suffix ~L26615/26635). **Uncommitted.**
- `corpus/live/measure_audio-pwctl-r86.lock` — new fixed-path lock file
  (untracked artifact; `corpus/live/` is the receipts area).
- `corpus/live/runs/20261016T063006268243Z-pwctl-r86/` and
  `…T063043717745Z-pwctl-r86/` — green receipts.
- Pre-existing `__pycache__/measure_audio.cpython-314.pyc` delta left as-is
  (was dirty before this seat's session; regenerated artifact).

## Blockers / caveats

- None blocking. Two rows are intentionally record-only: `d_route` (silent
  vs dump both realized across seats) and `dump_color_eq` (bimodal
  0B-vs-rc255 across boots); `n_format` is armed rc-only since pod presence
  tracks WP negotiation timing — both realizations measured on this host.
- The single permitted labrat was dispatched on the `pw-cli </dev/null>`
  disagreement; its substrate had no exec capability → `UNTESTED`, zero side
  effects. The boundary's direct rc=134 evidence plus this seat's own
  SIGABRT runs carry the claim.
- Shared-default mutation arms (`.monitor` handling, `-d` on
  `default.audio.*`, authority of `default.audio.sink/.source`) remain
  unmeasured by design — the boundary left them untested and this family
  keeps them out; subject-0 is read-only here.
