# r91-scout source provenance

All upstream files fetched **over the network** from the PipeWire GitLab at tag
`1.6.8` (the version installed on this host), 2026-10-15 ~17:0xZ. These are
`[I]` sources (not present on disk); the on-host Lua policy tree is `[O]`.

## Version match

| package | installed |
| --- | --- |
| pipewire | `1:1.6.8-1` |
| gst-plugin-pipewire | `1:1.6.8-1` (the GStreamer plugin ships inside the PipeWire tree) |
| libwireplumber | `0.5.17-1` |
| gstreamer | `1.28.6-3` |

Network reachability check: `curl -sI https://gitlab.freedesktop.org` → `302`.

Binary cross-checks (installed artifacts):
`strings /usr/lib/gstreamer-1.0/libgstpipewire.so` contains
`keepalive-time`, `resend-last`, `stream-properties`, `target-object`,
`autoconnect`; `strings /usr/bin/pw-cat` contains `target.object` and does
**not** contain `node.dont-reconnect` (consistent with pw-cat never setting the
flag; the key lives in libpipewire, not in the client).

## Fetched files

| file | URL | sha256 |
| --- | --- | --- |
| `gstpipewiresrc.c` | `https://gitlab.freedesktop.org/pipewire/pipewire/-/raw/1.6.8/src/gst/gstpipewiresrc.c` | `0e2248a9051b46cffe597fcb0a82e88b06d228e7ef8cf115e44ff43328e6e186` |
| `gstpipewiresink.c` | `…/1.6.8/src/gst/gstpipewiresink.c` | `8659aa72b5e265e77aa8bed24716c3f9aaadfb8a5e37cb4b384ff612b4e80b11` |
| `pw-cat.c` | `…/1.6.8/src/tools/pw-cat.c` | `0b8d05ce84149e8f9e3e0bdc7122d9bfd864119546081d0388ce355b76aba2ce` |
| `stream.c` | `…/1.6.8/src/pipewire/stream.c` | `3699792e732ec7a212045c532289db9b677241500cb5d4653cce20e569b43b55` |

## Key anchors

- `gstpipewiresrc.c:1207-1211` — capture `pw_stream_connect` flags:
  `PW_STREAM_FLAG_DONT_RECONNECT | PW_STREAM_FLAG_ASYNC` (+ AUTOCONNECT if
  `autoconnect`). **Unconditional** on the capture element.
- `gstpipewiresrc.c:48` `DEFAULT_KEEPALIVE_TIME 0`; `:1633-1642` with keepalive
  0 the create loop calls `pw_thread_loop_wait` (no timeout, no error).
- `gstpipewiresrc.c:1179-1195` — `target-object=` → `PW_KEY_TARGET_OBJECT` plus
  `PW_KEY_NODE_TARGET` when the value is a name.
- `gstpipewiresink.c:908-916` — sink flags: `ASYNC | EARLY_PROCESS` (+
  AUTOCONNECT, DRIVER, ALLOC_BUFFERS) — **no** DONT_RECONNECT.
- `pw-cat.c:2141-2151` — `flags = 0; … |= PW_STREAM_FLAG_AUTOCONNECT`.
- `stream.c:2091-2093` — `DONT_RECONNECT` → prop set **only if absent**, which
  is why a user-supplied `node.dont-reconnect=false` survives (measured).

## On-host WirePlumber Lua policy (`[O]`, installed by libwireplumber 0.5.17)

Shas in `WP-LUA.sha256`; anchors:
- `linking/prepare-link.lua:27` (`reconnect = not parseBool(node.dont-reconnect)`),
  `:65` (`"... dont-reconnect, not moving"`), `:71-76` (target dropped when
  `not reconnect and was_handled`).
- `linking/find-defined-target.lua:38-79` (target lookup + direction filter),
  `:116` (`dont-fallback` branch).
- `lib/common-utils.lua:37-48` (`getTargetDirection`, incl. the
  `stream.capture.sink` gate), `:52-62` (`getDefaultNode`).
- `lib/linking-utils.lua:257-267` (`isMonitor`/`canLink` same-direction rule).
