# r98-scout source provenance

Fetched over the network from the PipeWire GitLab at tag `1.6.8` (the version
installed on this host), 2026-10-15 ~20:3xZ. These are `[I]` sources (not
present on disk as package sources).

## Version match

| package | installed |
| --- | --- |
| pipewire | `1:1.6.8-1` |
| libpipewire-0.3 (pkg-config) | 1.6.8 |
| wireplumber | `0.5.17-1` |
| gcc | `16.2.1+r23+gd564253eb6c8-1` |

## Fetched files

| file | URL | sha256 | lines |
| --- | --- | --- | --- |
| `stream.c` | `https://gitlab.freedesktop.org/pipewire/pipewire/-/raw/1.6.8/src/pipewire/stream.c` | `3699792e732ec7a2…` (full in `SOURCES.sha256`) | 2793 |
| `stream.h` | `…/1.6.8/src/pipewire/stream.h` | `1ad58710f7487680…` | 708 |
| `impl-node.c` | `…/1.6.8/src/pipewire/impl-node.c` | `e193b599c362376d…` | 3019 |
| `audioadapter.c` | `…/1.6.8/spa/plugins/audioconvert/audioadapter.c` | `8ab982349c42321d…` | 2276 |
| `adapter.c`, `audioconvert-adapter.c`, `impl-node-rt.c` | wrong paths under `src/pipewire/` and `spa/plugins/audioconvert/` | each `17ce38b6dab5dc0b…` | **88 — GitLab 404 HTML pages, not C source.** Kept as artifacts of the wrong paths; the real adapter file is `spa/plugins/audioconvert/audioadapter.c` (the r98 labrat caught this corruption). |

## Used anchors (verbatim)

- `stream.c:449-477` — `update_requested()`/`call_process()`: process is
  suppressed while no free buffer exists; `requested` is set from
  `rate_match->size`.
- `stream.c:693-700` — `rate_size = rate_match->size` (fallback = quantum).
- `stream.c:1230,1257` — `node_id = SPA_ID_INVALID` at new; set when the node
  global is bound.
- `stream.c:2087-2098` — AUTOCONNECT/EXCLUSIVE/DONT_RECONNECT only-if-absent
  prop projection; non-RT → `node.loop.class=main` + `node.async=true`.
- `stream.c:2121-2123` — `media.class %s does not expect %s stream direction`
  (warning only; the native crash path is downstream).
- `stream.c:2753-2772` — `pw_stream_trigger_process()` returns the RT target
  trigger's value (observed rc 1).
- `stream.c:2776-2782` — `pw_stream_set_rate()` → `-ENOTSUP` when
  `rate_match == NULL`.
- `impl-node.c:1550-1555` — `pw_impl_node_trigger()` → `t->trigger(t, nsec)`.
