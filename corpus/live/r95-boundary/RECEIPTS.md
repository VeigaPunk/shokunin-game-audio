# r95-boundary receipts index — JACK↔PipeWire laws re-attacked (pipewire-jack 1.6.8)

Host plazir27, window **2026-10-15 20:52–21:09Z** (17:52–18:09 local, UTC−3). Repo
`~/Projects/shokunin/audio-shokunin` @ entry HEAD `51a98e54` (unchanged; **zero tracked
writes, nothing committed**). Seat namespace `r95b_*`. All receipts untracked, written by
`probes/r95bdriver.py` (own bounded runner, own synth, own Goertzel; never imports
`corpus/fixtures/measure_audio.py`). `manifest.sha256` pins every file (59 verified OK;
its own line carries the empty-file hash, scout convention).

Conditions: `q_*` = no own hogs (foreign load only, load1 62.9→80.8 — **never a quiet
host**); `h_*` = 14 own CPU hogs (`r95b_hog_00..13`), load1 74.8→108.8. Every rep is a
fresh process. Sweeps kill only tracked PIDs/modules + namespace-verified `r95b` strays.

| receipt | stage | legs / reps | what it pins |
| --- | --- | --- | --- |
| `q_env.json` / `h_env.json` | env | 1 static | toolchain, libjack sha, **217 declared functions / 51 absent** (218/52 loose regex catches the type `jack_port_t`), settings metadata, defaults, residue rows |
| `{q,h}_shape.json` | shape | 3 reps | PW citizen shape, port alias triple, flag mapping, monitor API local-only, census (Q 48–51, H 35–44 ports; foreign ports present), latency 0/0, 0 links |
| `{q,h}_xconnect.json` | xconnect | 3 arms × 3 reps | rendered rc 0 / native rc 22 / fill-alias rc 0 with link presence |
| `{q,h}_liveness.json` | liveness | 2 arms × 3 reps | driver-present cb 76; **no-driver cb 76 too** (falsifies "idle with no driver") |
| `{q,h}_bytepath.json` | bytepath | 3+3 reps | JACK→PW peak 0.5 but **3 distinct window shapes** (frames 174080/175104); PW→JACK peak 0.499969482, mag² 323955146.781 |
| `{q,h}_quantum.json` | quantum | 4 arms × 3 reps | per-client force-quantum 2048, live 512 + callback, cross-client 2048, `PIPEWIRE_QUANTUM` 256/512/2048, **rate 44100/96000 land**, `pw-jack -p512` ≡ `-p 512`, order_neg rc 2 |
| `{q,h}_global.json` | global | 2 reps each | `clock.force-quantum` 512 during/past exit, restored to 0, only that key moved (timestamps in receipt) |
| `{q,h}_xrun.json` | xrun | 3 reps × (control + 150 ms×4 + 60 ms×2 stalls) | control `xrun_cbs=0` 6/6 (scout saw 1); stalls 8–29 cycles → 0 callbacks; delayed ≤ 0.0 |
| `{q,h}_latency.json` | latency | 3 reps | 0/0 default → `[100,200]`/`[10,20]`, total 150, recompute 0 |
| `{q,h}_rtprio.json` | rtprio | 3+3 reps | plain values garbage; **stack-poison 0xAA→`aaaaaaa4/aaaaaaa9`, 0xBB→`bbbbbbb5/bbbbbbba` 6/6** |
| `{q,h}_transport.json` | transport | 3 reps | start→Rolling frame advancing, stop→Stopped, locate/reposition rc 0 inert |
| `{q,h}_metadata.json` | metadata | 3 reps | `default` metadata row keyed by registry id, round-trip, removed on exit, stale read after remove |
| `{q,h}_nameproj.json` | nameproj | 5 arms + duplicate × 3 | description mismatch → status 4; description==name → 0; nick/name overrides → 0; duplicate → status 4 |
| `{q,h}_flags.json` | flags | 4+2 arms × 2 reps | `-P` order-insensitive (pw-play/pw-record), `pw-link` reversed rc 255, `pactl` arg order-insensitive |
| `{q,h}_defaultnode.json` | defaultnode | 5 arms × 2 reps | `PULSE_SINK` honored by paplay, **ignored by pw-play**; `--target` honored; defaults churned by siblings |
| `{q,h}_bufsize1.json` | bufsize1 | 2 reps | no global opt-in: `set_buffer_size(1)` → `node.force-quantum="1"`, effective 4 |
| `{q,h}_driverid.json` | driverid | 3 / 2 reps | no seat sink: scheduling driver = **Dummy-Driver** (node.driver=true, prio 200000), cb>0 |
| `{q,h}_corner.json` | corner | 3 / 2 reps | sink with description==node.name (space-form props): the "native" string resolves rc 0 |
| `{q,h}_sibling.json` | sibling | 2 reps | foreign-seat census before/during/after; armed cells hold with siblings present |
| `parse_artifact.json` | parse_artifact | 2 arms | F4: comma-form `sink_properties` is one string prop + row persists; space-form is boolean `False` + no row |
| `{q,h}_verify.json` | verify | 1 | exit census: force-quantum 0, rate 48000, 0 modules/procs/nodes; 13 `stream-properties` rows (4 scout + 9 this seat) |

Raw runs: `runs/q_battery.log`, `runs/h_battery.log`, `runs/q_axes.log`, `runs/h_axes.log`,
`runs/{q,h}_summary_extract.json` (analyzer output).

Reproduce:

```
cd corpus/live/r95-boundary/probes
gcc -O2 -Wall -Wextra -o r95bjack r95bjack.c -ljack -lm
python3 r95bdriver.py all --cond q --reps 3
python3 r95bdriver.py driverid corner --cond q --reps 3
python3 r95bdriver.py global flags defaultnode bufsize1 driverid sibling verify --cond q --reps 2
python3 r95bdriver.py all --cond h --reps 3
python3 r95bdriver.py global flags defaultnode bufsize1 driverid corner sibling verify --cond h --reps 2
python3 r95banalyze.py q   # and h
```
