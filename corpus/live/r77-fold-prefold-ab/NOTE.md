# r77 fold pre-fold A/B receipt

`20261014T211929650838Z-capture-r76` — the r76 probe run at PRE-FOLD HEAD
(`65790f1`) via `git worktree add /tmp/audio-prefold HEAD`, copied into the
ledger after the r78 scribe found the A/B artifact absent from the audited
record (finding 5.1). Its failure set — `parec_no_device` +
`arecord -D default`/`-D pipewire` — matches the post-fold r76 runs,
establishing those as host-topology drift (DualSense default source + freed
PCM paths), not a fold regression. The post-fold-only roundtrip-witness
failure matches the named contention false-alarm class (nonzero content,
level-far only).
