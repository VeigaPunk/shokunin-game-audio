# Labrat report (relayed verbatim) — r90 verifier, single permitted probe

Seat: `ufo-labrat`, depth-2, read-only, dispatched once by the frozen
`probeParent` (r90 verifier). Substrate limitation disclosed by the labrat: no
exec surface — read/grep/glob only; zero writes, zero spawned processes, zero
audio-state changes.

---

**Hypothesis:** The WirePlumber `stream-properties` store has no deletion path
reachable from the r90 toolset; every `r90a_*` row is permanent residue.

**Expected observation (named before probing):** ≥100 `r90a_` keys in the live
store; `state-stream.lua` writes but never nils keys; `wpctl`/`pactl`/`pw-cli`/
`pw-dump` expose no store-delete verb.

## Observed

**1. Row census** — `/home/vgpnk/.local/state/wireplumber/stream-properties`:
**220 lines contain `r90a_`**. Examples (lines 6795–6805):

- `Output/Audio:application.name:r90a_2962524n140522_c={"volume":0.5, "channelMap":["FL","FR"], …}`
- `Output/Audio:application.name:r90a_2962524n140522_t={…"target":"r90a_ns2_2962524"}`
- `Output/Audio:application.name:r90a_2962524n140522_z={…"target":"r90a_ns4_2962524"}`

Naming is `r90a_<pid>n<nonce>_<tag>`; sink objects are `r90a_ns{2..4}_<pid>`
(fixture: `measure_audio.py:35590–35600`).

**2. Store implementation (installed, WP 0.5.17):**

- `/usr/share/wireplumber/scripts/node/state-stream.lua` — the only owner of
  `stream-properties`. Writes at `saveStreamProps` (line 451;
  `state_table[key] = Json…` at 457, `state:save_after_timeout` at 458), called
  from lines 255, 321, 389. **No `state_table[key] = nil`, no `state:clear()`,
  no deletion hook anywhere in the file.** `toggleState` (489–517) only nils the
  in-memory handle; it never erases keys.
- `/usr/include/wireplumber-0.5/wp/state.h:37` — `void wp_state_clear (WpState
  *self)` exists in the C API. **But a grep of all 73 installed lua scripts
  finds zero callers of `state:clear`.**
- Deletion *does* exist — for a different store:
  `/usr/share/wireplumber/scripts/default-nodes/state-default-nodes.lua:172`
  `state_table [key] = nil`, triggered by `wpctl clear-default` against the
  `default-nodes` state file.

**3. r90 fixture toolset** (`measure_audio.py` r90 block, ~35556–37711):
`pactl` (list/load/unload/set-*), `pw-cli` (enum-params, set-param, destroy),
`pw-dump`, `pw-link`, `pw-play`, `wpctl settings` (35807). Teardown
(`_wpstate_r90_teardown`, 36109–36165) reaps players, name-verified
`pactl unload-module`, `pw-cli destroy` of residual nodes — then only
**censuses** the store (`store_at_exit`, 36863). It never attempts row removal;
line 34108–34115 confirms rows are reported as residue, verbatim
"stream-properties rows left by this seat".

**4. `wpctl` verb surface** (`/usr/share/bash-completion/completions/wpctl:9-11`):
`status get-volume inspect set-default set-volume set-mute set-profile
set-route clear-default settings set-log-level list reset`. `clear-default`
deletes `default-nodes` keys only; `settings`/`reset` touch config/settings, not
stream-properties. `pactl`/`pw-cli`/`pw-dump`/`pw-link` have no state-store verb
at all (rows appear only as a side effect of WirePlumber observing stream
`Props` param changes — `node-params-changed` hook, state-stream.lua:180–259).

## Counterexample command that deletes a stream-properties row

**None found.** The closest reachable deletion is `wpctl clear-default <id>` —
but it nils keys in the `default-nodes` store (state-default-nodes.lua:172), not
`stream-properties`.

## Conclusion

**CONFIRMED**, with one refinement: the hypothesis's mechanism clause is
slightly too strong — WirePlumber's `WpState` API does support deletion
(`wp_state_clear`, state.h:37; `state_table[key]=nil` idiom,
state-default-nodes.lua:172) — but that path is wired only to
`default-nodes`/`settings` stores. For `stream-properties` specifically,
state-stream.lua contains no deletion code and no fixture tool can invoke one.
All 220 `r90a_` rows are permanent until operator-side file editing (or
`wp_state_clear` via a custom script/client).

**Cleanup status:** zero writes, zero spawned processes, zero audio-state
changes; read/grep/glob only (no exec surface, disclosed per method).
