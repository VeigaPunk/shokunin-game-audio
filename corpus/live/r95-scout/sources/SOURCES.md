# r95 scout — upstream sources read (PipeWire 1.6.8 tag)

Fetched read-only from gitlab.freedesktop.org (network reachable; same method as r91).
These are the *version-matched* sources of the installed pipewire-jack 1:1.6.8-1
(libjack.so.0.3.1608; binary strings carry `../pipewire/pipewire-jack/src/...`
build paths, cross-checked below).

| local file | upstream path @ tag 1.6.8 | used for |
| --- | --- | --- |
| pipewire-jack.c | pipewire-jack/src/pipewire-jack.c | open/activate, port register, naming, get_ports, connect, buffer-size/sample-rate, xrun callback, transport, freewheel, rt-prio |
| metadata.c | pipewire-jack/src/metadata.c | jack metadata -> PW metadata object write path |
| statistics.c | pipewire-jack/src/statistics.c | jack_get_{xrun,max}_delayed_usecs unit handling |
| uuid.c | pipewire-jack/src/uuid.c | uuid generate/parse/unparse/index |
| common.c, transport.c | pipewire-jack/src/{common,transport}.c | auxiliary |
| private.h | src/pipewire/private.h | pw_node_activation field docs (xrun_delay/max_delay units) |

On-disk (installed) anchors: /usr/share/pipewire/jack.conf, /usr/bin/pw-jack,
/usr/share/man/man1/pw-jack.1.gz, /usr/include/jack/*.h, /usr/lib/libjack.so.0.3.1608.

Binary cross-check: `strings /usr/lib/libjack.so.0.3.1608` contains
`../pipewire/pipewire-jack/src/pipewire-jack.c`, `.../metadata.c`,
`jack.global-buffer-size`, `clock.force-quantum`, `clock.force-rate`.
