# r95-foldfix receipts — implementation sha per receipt

Seat: **foldfix-author**, lane `~/Projects/shokunin/audio-shokunin`, HEAD
`6fcff79280193fcf54ccc98adb3a193ed3575eaa` (the r95 author commit `ffeb5155`
is its ancestor; both carry the same pre-fold `measure_audio.py` blob
`dca4dc9b…`). **No commit.** Host `plazir27`.

The run tree is `tree/` = `git archive HEAD` extracted at 09:30:35Z plus the
fold patch applied to `corpus/fixtures/measure_audio.py` (`fold.patch`, the
lane's working-tree diff). The implementation sha of
`corpus/fixtures/measure_audio.py` in the tree was set explicitly before each
run and is recorded below; `r95jack.c` is untouched
(`55d4d4111bd8d46be743d0425a40dc8d938d15e071ce37f460db70de0df997be`, frozen
fixture source).

| receipt | implementation sha (`measure_audio.py`) | revision | entries | legs | measured | failures |
| --- | --- | --- | --- | --- | --- | --- |
| `before-frozen-measurements.json` | `dca4dc9b…` (HEAD, no fold) | frozen committed bytes | 22 | 24 | key absent | 1 (`d_metadata: stale after remove`) |
| `intermediate-run-legsbug-measurements.json` | `46ef4b8f…` | fold rev 1 | 23 | **0** | mixed | 0 |
| `intermediate-run-pre-f1census-measurements.json` | `540b918e…` | fold rev 2 | 23 | 24 | all true | 0 |
| `after-run2-measurements.json` | `740d9ce3…` (final) | fold rev 3 | 23 | 24 | all true | 0 |
| `after-run3-measurements.json` | `740d9ce3…` (final) | fold rev 3 | 23 | 24 | all true | 0 |
| `after-run4-measurements.json` | `740d9ce3…` (final) | fold rev 3 | 23 | 24 | all true | 0 |

The two intermediate receipts are kept as the catches that produced the next
revision:

- **legsbug**: `_jack_r95_finish` did not receive the local `legs` dict, so
  every entry shipped `legs: {}` while `measured: true` — i.e. the fold's own
  C1 discriminator was live and *did* say "ran", but the leg payload was
  missing. Caught by reading the receipt, fixed by passing `legs` and adding
  `legs_measured`.
- **pre-f1census**: the F1 subject census read `p.get("port_id")` from
  `_jack_r95_graph()` port entries, which do not carry that key (only
  `_jack_r95_port()` adds it), so `own_subjects` collapsed to the node id and
  our own `r95a/portkey` row was filed as *foreign*. Caught by reading the
  receipt's `foreign_r95a_rows_while_running`, fixed by keying on the port
  dict's own global id; the final revision adds an armed completeness check
  (both own keys must be attributable to our subjects).

`manifest.sha256` covers every receipt in this directory.
