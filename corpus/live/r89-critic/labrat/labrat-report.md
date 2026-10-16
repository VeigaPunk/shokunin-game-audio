# r89 critic — frozen probeParent labrat dispatch (exactly one)

Seat: `ufo-labrat` agent `4d05f9e0`, dispatched once by the frozen
`probeParent` (this seat) with a bounded, read-only, falsifiable
hypothesis. No second spawn. The child reported no `exec` tool (file
inspection only, exactly the r88 precedent), and it did the work with
`read`/`grep` — so this is a real independent witness, not a
`STILL NO EXEC` return.

## Hypothesis

"Every numeric value cited as measured in
`reports/round-89/r89-author.md` matches the corresponding value
recorded in the two committed green receipts."

## Child's verdict

**FALSIFIED** — 8 distinct numeric discrepancies, several against both
receipts. The child's own table (verbatim, condensed to the mismatches;
run A = `20261016T074733533774Z`, run B = `20261016T074816877001Z`):

| claim | report | run A | run B |
|---|---|---|---|
| total legs | 47 | **52** | **52** |
| xw legs | 8 | **9** | **9** |
| `g_term`/`g_int` infos | 47 | **46** | **46** |
| `g_two` wall | 0.071 s | **0.081** | 0.071 |
| `o_int` bytes | 32347 | **32362** | **32340** |
| `o_default` `profiler.log` bytes | 4320 | **4314** | **4312** |
| `o_dash` `-` bytes | 6468 | **6472** | 6468 |
| `x_conc` bytes | 6471 | **6503** | 6471 |
| `x_top` row / medians | 1.6/0.6 µs, 2.55/1.40 µs | **2.3/0.9, 4.09/2.22** | 1.6/0.6, 2.55/1.40 |

The child also noted that the report's own per-entry counts sum to 51,
not 47. Cleanup: no files modified, no scratch created, no processes
spawned.

## Dispatcher's independent agreement

This seat's own census (`census.json`) and report-vs-receipt comparison
found the same eight discrepancies without sight of the child's table
(leg totals 52 in both receipts; `g_term.n_info == 46` in both;
`o_int` 32362/32340; `o_default` 4314/4312; `o_dash` 6472/6468;
`x_conc` 6503/6471; `x_top` 2.3/0.9+4.09/2.22 vs 1.6/0.6+2.55/1.40;
`g_two` 0.081/0.071). Two independent seats, same counterexamples.

## Note

The child was **not** used to probe the host (no exec) and did not run
the fixture — no graph object was touched by the child.
