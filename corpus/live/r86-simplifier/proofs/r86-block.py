# r86: the PIPEWIRE CONTROL-PLANE lattice — pw-cli ls/info/enum-params/
#     set-param addressing + param exposure, the pw-dump census surface,
#     pw-metadata store laws, pw-top's batch/TUI signal split, the
#     pw-jack env shim and the pw-link rc lattice -- --probe-pwctl-r86.
#
# A NEW parallel ledger family; prior rows untouched; every r76-r85
# guard inherited (seat-owned r86a_<pid> names, the private
# r86arole<pid> restore key, name-verified module unloads by the
# module's OWN sink_name= arg, never set-default-*, bounded process
# groups, taps bounded by -n AND link-validated before the player
# spawns). The r84 F1 3-seat consensus is folded at authoring time:
# the family lock is a FIXED lane path under corpus/live/, never a
# $TMPDIR path — same-family runs exclude each other across seats with
# differing TMPDIRs. Surface facts are the r86 scout's THIS-HOST
# measurements (PipeWire 1.6.8, WirePlumber 0.5.17, pactl
# 17.0-98-gb096 protocol 35, python 3.14.7) as CORRECTED by the r86
# boundary — falsified rows are recorded or dropped, never armed:
#
#   ADDRESSING SPLIT (decisive): `pw-cli ls <N>` selects object.serial,
#     `pw-cli info <N>` selects object.id — same digits, two
#     namespaces. The id family is {info, enum-params, set-param,
#     destroy}; the serial family is {pactl verbs, `pw-cli ls`}.
#     `pw-dump <N>` accepts BOTH (id and serial resolve to the same
#     object row — no id<->serial collision exists in this id space).
#     Unknown/lowercase class names -> EMPTY stdout rc=0, identical to
#     a real empty class (`ls Bogus` == `ls node` == `ls Session`); the
#     ls row shape is `id N, type PipeWire:Interface:X/Y` (space) vs
#     info's `type: ...` (colon).
#
#   RC LAW + THE pw-link EXCEPTION: every measured pw-cli/pw-metadata/
#     pw-dump refusal is rc=0 — verdicts live in stderr text (local
#     `Error: "<verb>: ..."`, remote `remote 0: error id:N seq:S
#     res:-R`) or in output ABSENCE. pw-link refuses at rc=255 (the
#     scout's rc=0 row is falsified), its -I/-v/-m are MODIFIERS
#     (rc=255 without -l/-i/-o), `-p <json>` is silently ACCEPTED even
#     when the props are junk, and `-d` wants a LINK id (a port id ->
#     rc=255). `pw-cli -r <bogus>` -> rc=255 + `failed to connect:
#     Host is down` — a real nonzero refusal, unlike the rc0 family.
#
#   ENUM-PARAMS MATRIX (typed per object class): Node = {Props,
#     PropInfo, EnumFormat}; Port = {EnumFormat, Latency, IO, Meta};
#     Device = {Profile, EnumProfile, Route, EnumRoute};
#     Client/Factory/Link/Module/Core -> local `not implemented on
#     object`; an enum'd-but-unexposed param -> remote `res:-2 ENOENT`;
#     Format is absent PRE-negotiation (the refusal text is 3-valued
#     racy — silent / bind-race pair / res:-5 — so arms judge POD
#     PRESENCE ONLY); numeric `3` == `EnumFormat` byte-for-byte;
#     Bogus/999/all -> local `unknown param type`.
#
#   SET-PARAM WRITE SURFACE (own null-sink only): Props is LIVE DSP —
#     channelVolumes is LINEAR (0.25 -> peak x0.25 exactly) while
#     pactl's `%` is CUBIC (25% -> x0.015625) and the scalar `volume`
#     key is DISPLAY-DEAD (lands in the param store — enum reads Float
#     0.25 back — moves no audio, pactl still 100%). The param store
#     and the pulse volume are the same state on two scales (after
#     channelVolumes=0.25 pactl reads 63% = the cube root). Refusals:
#     `garbage` -> stdout `None` rc0; `{ }` -> empty pod echo rc0;
#     unknown keys STRIPPED (absent on re-enum); wrong-type value ->
#     None-typed slot; EnumFormat write -> rc0 echo + remote `res:-95
#     Operation not supported`; a PORT set-param -> rc0 + pod echo +
#     LOCAL `set-param not implemented ... type:...Port` (the echo is a
#     local print — the boundary's correction to `silently dropped`);
#     bad id -> `unknown global`; missing json -> usage text.
#
#   PW-DUMP SURFACE: <bad-id> -> 0 bytes rc0; `-C never` (two tokens)
#     -> 0 bytes rc0 (WHEN is eaten as the positional <id> — the
#     silent-empty trap); `-Cnever` -> the full dump; `-C=never` is
#     host-bimodal (0B on the boundary boot, rc=255 `Unknown color:
#     =never` here — RECORDED ONLY); each invocation adds ONE self
#     Client (application.name=pw-dump — volatile serial/pid props).
#     `BYTE-STABLE MODULO SELF` is FALSIFIED under a live graph
#     (canonical hashes take 3-4 distinct values with sibling churn) —
#     no hash arm is encoded. `pw-cli ls Metadata`/`pw-metadata -l`
#     agree on NINE stores where pw-dump sees a strict SUBSET (the
#     metadata census gap — the law is stable, the mechanism unread);
#     `pw-cli info <metadata-id>` -> 0 bytes rc0, a silent-empty on a
#     LIVE object.
#
#   PW-METADATA STORE LAWS: the `set property:` echo is a LOCAL print,
#     not an ack — a write persists only under a LIVE subject id (dead
#     subject 99997 echoes and never reads back); read -> `update:`
#     row; absent key -> the Found line only; overwrite is full
#     replace; a typed value persists verbatim (`type:'Spa:String'`);
#     `-d <subj> <key>` -> `delete property:` and deleting ABSENT is
#     the same echo no-op; `-d <subj>` bare -> `delete properties:
#     id:N` wipes every key under the subject; `-m <subj>` FILTERS rows
#     (an unbounded stream — bounded by kill). Subject 0 is READ-ONLY
#     in this family (the session defaults — never written, never
#     deleted; the scout's default.audio.* write arms are deliberately
#     not encoded — the wave spec's NEVER set-default-* covers the
#     door).
#
#   PROCESS SURFACES: `pw-top -b -n N` is headless-clean (rc0, plain
#     `S ID QUANT RATE ...` table; -n 0 -> one table); batch + TERM/INT
#     exits CLEAN (rc0) while the TUI path SIGABRTs on TERM/INT (the
#     loop.c:189 remove_from_poll assertion — the crash is the
#     curses-path teardown, not pw-top per se — the boundary's
#     narrowing of H1); `pw-cli </dev/null` hits the SAME assertion
#     (SIGABRT — the scout's clean-rc0-EOF row is falsified) while a
#     PIPE stdin never exits (streams registry events forever) and
#     `quit` is the only clean REPL exit; `pw-jack` exports
#     PIPEWIRE_QUANTUM from -p (rate defaults 48000; -s alone gates it
#     OFF), bumps PIPEWIRE_DEBUG per -v over any preset, exports -r
#     REMOTE, and `-h`/no-args/`-Z` all exit rc0 while a bogus payload
#     execs to rc=127; `pw-cli info <link-id>` is the live-format
#     census (endpoint ids + state + the negotiated Format pod).
#
# Rows assert rc + error class + pod presence/absence + graph targets
# + envelopes; volatile text (seq numbers, EIO phrasing, coredump
# timing) is recorded, never armed. Crash-class legs run with
# RLIMIT_CORE=0 — the assertion is measured, not dumped.

PWCTL_R86_PID = os.getpid()
PWCTL_R86_PREFIX = f"r86a_{PWCTL_R86_PID}"
PWCTL_R86_NS = f"r86a_ns_{PWCTL_R86_PID}"        # the probe null sink
PWCTL_R86_TAP = f"r86a_tap_{PWCTL_R86_PID}"      # monitor-tap node name
PWCTL_R86_ROLE = f"r86arole{PWCTL_R86_PID}"      # private restore key —
                                               # NEVER shared `music`
PWCTL_R86_BOGUS = "no_such_r86a"
PWCTL_R86_DEAD_SUBJECT = "99997"     # no live object — the echo lies
PWCTL_R86_META_KEY = "r86a_k"
PWCTL_R86_AMP = PLAYBACK_R78_TONE_AMP            # 8192
PWCTL_R86_LINK_WAIT_S = 5.0
PWCTL_R86_TAP_WAIT_S = 6.0
PWCTL_R86_STREAM_WAIT_S = 8.0
PWCTL_R86_TONE_S = 16.0          # one player covers both write passes
PWCTL_R86_SOLO_ENV = (0.85, 1.18)    # x8192 solo/reset/restore window
PWCTL_R86_CV25_ENV = (0.15, 0.35)    # linear 0.25x (exact: 2048)
PWCTL_R86_CV50_ENV = (0.40, 0.60)    # linear 0.5x  (exact: 4096)
PWCTL_R86_PA25_ENV = (0.008, 0.035)  # pactl cubic 25% -> x0.015625
PWCTL_R86_MUTE_MAX = 64              # post-mute peak cap
PWCTL_R86_CUBIC_PCT = (50, 80)       # pactl % after cv=0.25 (~63, =cbrt)


# r86-local error classes — family-local, checked before the r84 chain
# (never prepended into _CAPTURE_ERR_CLASSES). Order matters: the
# named remote-res classes precede the generic pwcli_remote catch-all;
# not_impl/unknown_global/unknown_param precede the usage shape.
_PWCTL_R86_ERR_CLASSES = (
    ("pwcli_unknown_global", r"unknown global '[^\n']*'"),
    ("pwcli_unknown_param", r"unknown param type: [^\n'\"]+"),
    ("pwcli_not_impl",
     r"(?:enum-params|set-param|info) not implemented on object \d+ "
     r"type:[^\n'\"]+"),
    ("pwcli_remote_enoent", r"res:-2 \(No such file or directory\)"),
    ("pwcli_remote_eio", r"res:-5 \(Input/output error\)"),
    ("pwcli_remote_notsup", r"res:-95 \(Operation not supported\)"),
    ("pwcli_remote", r"remote \d+: error id:\d+ seq:\d+ res:-\d+"),
    ("pwcli_connect_down", r"failed to connect: Host is down"),
    ("pwcli_usage", r"Error: \"[a-z-]+[^\"]*<[^\"]+>\""),
    ("pwcli_dump_color", r"Unknown color: [^\n]+"),
    ("pwlink_exists", r"failed to link ports: File exists"),
    ("pwlink_noent",
     r"failed to (?:un)?link ports: No such file or directory"),
    ("pwlink_usage",
     r"needs one or more of -l|PipeWire port and link manager|"
     r"missing output and input port names"),
    ("pw_loop_assert", r"remove_from_poll\(\)"),
    ("pwjack_exec", r"exec: [^\n]*: not found"),
)


def _pwctl_r86_errclass(text):
    """r86-local classes first, then the r84 pactl/alsa table and the
    shared pw table through it."""
    for name, pat in _PWCTL_R86_ERR_CLASSES:
        m = re.search(pat, text or "")
        if m:
            return name, m.group(0).strip()
    return _alsapw_r84_errclass(text or "")


def _pwctl_r86_no_core():
    """preexec: zero the core limit — crash-class legs measure the
    signal without filing a coredump."""
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def _pwctl_r86_run(argv, timeout_s, env=None, stdin_data=None,
                   nocore=False):
    """One bounded spawn -> rc/signal/stdout/stderr + r86 error class.
    `stdin_data` feeds a PIPE (None -> DEVNULL, which IS the pw-cli
    </dev/null arm); `nocore` zeroes RLIMIT_CORE for the SIGABRT legs.
    killed_at_bound separates a harness kill from an app refusal.
    stdout is preview-truncated like the r85 runner but the measured
    verdicts read the computed fields (bytes/lines/has_pod), never the
    preview."""
    rec = {"argv": " ".join(str(a) for a in argv)}
    try:
        proc = subprocess.Popen(
            argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=(subprocess.PIPE if stdin_data is not None
                   else subprocess.DEVNULL),
            env=env, start_new_session=True,
            preexec_fn=_pwctl_r86_no_core if nocore else None)
    except OSError as exc:
        rec["spawn_error"] = str(exc)[:160]
        return rec
    t0 = time.monotonic()
    killed = False
    try:
        out, err = proc.communicate(input=stdin_data,
                                    timeout=timeout_s)
    except subprocess.TimeoutExpired:
        killed = True
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = proc.communicate()
    errt = err.decode(errors="replace")
    outt = out.decode(errors="replace")
    cls, hit = _pwctl_r86_errclass(errt)
    rec.update({"exit_code": proc.returncode,
                "signal": (signal.Signals(-proc.returncode).name
                           if (proc.returncode or 0) < 0 else None),
                "killed_at_bound": killed,
                "wall_s": round(time.monotonic() - t0, 3),
                "stdout_bytes": len(outt),
                "stdout_lines": len(outt.strip().splitlines()),
                "has_pod": "Object:" in outt,
                "stdout_head": outt.strip().splitlines()[:3],
                "stdout": outt[:700],
                "stderr_head": errt.strip().splitlines()[:3],
                "stderr": errt[:900],
                "error_class": cls, "error_hit": hit})
    return rec


def _pwctl_r86_sigleg(argv, sig, at_s, bound_s, label):
    """Spawn argv, deliver `sig` to the process group at `at_s`, wait to
    `bound_s` — the signal-discipline leg shape (pw-top/pw-cli crash
    classes). RLIMIT_CORE is always zeroed: the assertion is measured,
    never dumped."""
    rec = {"argv": " ".join(str(a) for a in argv), "sent": label,
           "at_s": at_s}
    try:
        proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.DEVNULL,
                                start_new_session=True,
                                preexec_fn=_pwctl_r86_no_core)
    except OSError as exc:
        rec["spawn_error"] = str(exc)[:160]
        return rec
    t0 = time.monotonic()
    time.sleep(at_s)
    sent = proc.poll() is None
    if sent:
        try:
            os.killpg(proc.pid, sig)
        except ProcessLookupError:
            sent = False
    rec["signal_delivered"] = sent
    killed = False
    try:
        out, err = proc.communicate(
            timeout=max(0.2, bound_s - (time.monotonic() - t0)))
    except subprocess.TimeoutExpired:
        killed = True
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = proc.communicate()
    errt = err.decode(errors="replace")
    outt = out.decode(errors="replace")
    cls, hit = _pwctl_r86_errclass(errt)
    rec.update({"exit_code": proc.returncode,
                "signal": (signal.Signals(-proc.returncode).name
                           if (proc.returncode or 0) < 0 else None),
                "killed_at_bound": killed,
                "wall_s": round(time.monotonic() - t0, 3),
                "stdout_bytes": len(outt),
                "stdout_lines": len(outt.strip().splitlines()),
                "stdout_head": outt.strip().splitlines()[:3],
                "stderr_head": errt.strip().splitlines()[:3],
                "stderr": errt[:900],
                "loop_assert": "remove_from_poll" in errt,
                "error_class": cls, "error_hit": hit})
    return rec


def _pwctl_r86_pwcli(*args, timeout_s=10.0):
    return _pwctl_r86_run(["pw-cli", *[str(a) for a in args]],
                          timeout_s)


def _pwctl_r86_meta(*args, timeout_s=10.0):
    return _pwctl_r86_run(["pw-metadata", *[str(a) for a in args]],
                          timeout_s)


def _pwctl_r86_graph():
    return _pactlmon_r85_graph()


def _pwctl_r86_node(g, name):
    return _pactlmon_r85_node(g, name)


def _pwctl_r86_links():
    """pw-dump Link objects resolved to `node:port` name pairs, WITH
    the link's object.id — the destroy/info legs need the id, the
    census needs the shape. None on reader failure."""
    try:
        proc = subprocess.run(["pw-dump"], capture_output=True,
                              timeout=15)
        dump = json.loads(proc.stdout or b"[]")
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return None
    nodes = {o["id"]: (o.get("info") or {}).get("props", {})
             .get("node.name") for o in dump
             if str(o.get("type", "")).endswith("Node")}
    ports = {o["id"]: (o.get("info") or {}).get("props", {})
             .get("port.name") for o in dump
             if str(o.get("type", "")).endswith("Port")}
    out = []
    for o in dump:
        if not str(o.get("type", "")).endswith("Link"):
            continue
        info = o.get("info") or {}
        out.append({"id": o["id"], "state": info.get("state"),
                    "out": f"{nodes.get(info.get('output-node-id'))}:"
                           f"{ports.get(info.get('output-port-id'))}",
                    "in": f"{nodes.get(info.get('input-node-id'))}:"
                          f"{ports.get(info.get('input-port-id'))}"})
    return out


def _pwctl_r86_own_links(sink=PWCTL_R86_NS):
    """Live link leaves with one endpoint on `sink` (our monitor->
    playback self-loops and the DSP player's links)."""
    links = _pwctl_r86_links()
    if links is None:
        return None
    return [l for l in links
            if (l["out"] or "").startswith(sink + ":")
            or (l["in"] or "").startswith(sink + ":")]


def _pwctl_r86_meta_ids():
    """`pw-metadata -l` -> {store_name: id} from the `Found "<n>"
    metadata <id>` rows — the store census (None on reader failure)."""
    try:
        proc = subprocess.run(["pw-metadata", "-l"],
                              capture_output=True, timeout=10)
    except (subprocess.TimeoutExpired, OSError):
        return None
    out = {}
    for m in re.finditer(r'Found "([^"]+)" metadata (\d+)',
                         proc.stdout.decode(errors="replace")):
        out[m.group(1)] = int(m.group(2))
    return out


def _pwctl_r86_ls_ids(cls):
    """`pw-cli ls <cls>` -> the object.id list behind the `id N, type`
    rows (None on reader failure)."""
    try:
        proc = subprocess.run(["pw-cli", "ls", cls],
                              capture_output=True, timeout=10)
    except (subprocess.TimeoutExpired, OSError):
        return None
    return [int(m.group(1)) for m in re.finditer(
        r"\bid (\d+),\s*type PipeWire:Interface:",
        proc.stdout.decode(errors="replace"))]


def _pwctl_r86_dump_ids(cls):
    """pw-dump -> the object.id list of class `cls` (None on reader
    failure) — one half of the metadata census-gap arm."""
    try:
        proc = subprocess.run(["pw-dump"], capture_output=True,
                              timeout=15)
        dump = json.loads(proc.stdout or b"[]")
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return None
    return [o["id"] for o in dump
            if str(o.get("type", "")).endswith(cls)]


def _pwctl_r86_update_rows(text):
    """The `update: id:N ...` rows of a pw-metadata read/monitor."""
    return [ln for ln in (text or "").splitlines()
            if ln.lstrip().startswith("update:")]


def _pwctl_r86_family_lock():
    """Same-family exclusion at a FIXED lane path — the r84 F1 3-seat
    consensus fix: a $TMPDIR-scoped lock lets two same-family runs on
    different TMPDIRs race and cross-credit node names, so this lock
    lives under corpus/live/ (outside $TMPDIR entirely). A second
    --probe-pwctl-r86 waits HERE (the r82 convention)."""
    path = ROOT / "live" / "measure_audio-pwctl-r86.lock"
    try:
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    except OSError:
        return None
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        os.ftruncate(fd, 0)
        os.write(fd, f"pid={PWCTL_R86_PID} ns={PWCTL_R86_NS} "
                     f"role={PWCTL_R86_ROLE}\n".encode())
    except OSError:
        pass
    return fd


def _pwctl_r86_entry_head(probe):
    """Shared entry preamble: contention census, oracle, inventory,
    loadavg, and the foreign-r86a census (a crashed sibling's residue
    is a witness, never a verdict — this pid's own namespace is the
    only teardown target)."""
    inv = _capture_inventory()
    names = _playback_r78_node_names() or []
    return {"probe": probe,
            "contention": _playback_r78_foreign_clients(),
            "oracle_at_start": _loopback_r79_oracle(),
            "foreign_r86a_nodes": sorted(
                n for n in names if "r86a_" in n
                and f"_{PWCTL_R86_PID}" not in n),
            "inventory": {"default_sink": inv["default_sink"],
                          "default_source": inv["default_source"],
                          "sources_count": len(inv["sources"]),
                          "monitors_count": len(inv["monitors"]),
                          "alsa_capture_devices":
                          inv["alsa_capture_devices"]},
            "loadavg": _alsapw_r84_loadavg()}


def _pwctl_r86_teardown(entry, failures, loads, meta_subject=False):
    """Every own module unloaded by the name-verified index (each load
    record carries its OWN field name — sink_name), then the
    witnesses: sinks gone from pactl, no r86a_<pid>-tagged node
    survives, and (when the entry wrote metadata) no r86a_ key remains
    in the default store."""
    for tag, leaf in (loads or {}).items():
        leaf = leaf or {}
        entry.setdefault("unloads", {})[tag] = \
            _pactlmon_r85_unload_own(
                leaf.get("module_id"),
                leaf.get("field", "sink_name"),
                leaf.get("value", tag))
    sinks_now = _capture_r77_sink_names_strict()
    if sinks_now is None:
        entry["sinks_gone"] = "reader_error"
        entry.setdefault("coverage_blocked", []).append(
            "teardown: pactl sink reader failed — sinks_gone "
            "unmeasured")
    else:
        gone = {nm: nm not in sinks_now for nm in (loads or {})}
        entry["sinks_gone"] = gone
        if not all(gone.values()):
            failures.append(
                "teardown: probe sinks survived unload: "
                f"{[n for n, g in gone.items() if not g]}")
    names = _playback_r78_node_names()
    if names is None:
        entry["own_nodes_after"] = "reader_error"
        entry.setdefault("coverage_blocked", []).append(
            "teardown: node reader failed — own_nodes_after "
            "unmeasured")
    else:
        rest = sorted(n for n in names
                      if f"r86a_{PWCTL_R86_PID}" in n
                      or n in (loads or {}))
        entry["own_nodes_after"] = rest
        if rest:
            failures.append(
                f"teardown: r86a-tagged nodes survived: {rest}")
    if meta_subject:
        try:
            proc = subprocess.run(["pw-metadata", "-n", "default"],
                                  capture_output=True, timeout=10)
            leftover = [ln.strip()[:160] for ln in
                        proc.stdout.decode(
                            errors="replace").splitlines()
                        if "r86a_" in ln]
        except (subprocess.TimeoutExpired, OSError):
            leftover = None
        if leftover is None:
            entry["meta_keys_gone"] = "reader_error"
            entry.setdefault("coverage_blocked", []).append(
                "teardown: pw-metadata reader failed — meta_keys_gone "
                "unmeasured")
        else:
            entry["meta_keys_gone"] = not leftover
            if leftover:
                failures.append(
                    f"teardown: r86a metadata keys survived: "
                    f"{leftover}")


def _pwctl_r86_block(entry, failures, msg, loads=None):
    """The named coverage block: record it, unload anything loaded."""
    entry["blocked"] = msg
    entry.setdefault("coverage_blocked", []).append(msg)
    for tag, leaf in (loads or {}).items():
        leaf = leaf or {}
        entry.setdefault("unloads", {})[tag] = \
            _pactlmon_r85_unload_own(
                leaf.get("module_id"),
                leaf.get("field", "sink_name"),
                leaf.get("value", tag))
    entry["failures"] = failures
    return entry


def _pwctl_r86_load_ns():
    """Load + gate the family's null sink; the load record carries its
    own field/value for the name-verified unload."""
    leaf = _pwcat_r83_ns_load(PWCTL_R86_NS)
    leaf["field"] = "sink_name"
    leaf["value"] = PWCTL_R86_NS
    return leaf


def _pwctl_r86_node_ports(g, nid):
    """The port leaves of node `nid` — {port_name: port_id}."""
    return {p.get("name"): pid for pid, p in
            (g.get("ports") or {}).items()
            if str(p.get("node_id")) == str(nid)}


def pwctl_addr_r86_entry():
    """The pw-cli ls/info addressing split + class census + the pw-dump
    surface (id|serial resolution, bad-id zero-bytes, the -C
    positional trap, the self-Client law) + the info-all and
    remote-refusal rows + pw-cli destroy as an id-family write."""
    failures, legs = [], {}
    entry = _pwctl_r86_entry_head(
        "r86a pw-cli/pw-dump addressing + census lattice")
    tools = {t: shutil.which(t) for t in
             ("pw-cli", "pw-dump", "pw-metadata", "pw-link", "pactl")}
    entry["tools"] = tools
    if not all(tools.values()):
        return _pwctl_r86_block(
            entry, failures,
            f"missing tools: {[t for t, p in tools.items() if not p]}")
    loads = {}
    try:
        loads[PWCTL_R86_NS] = _pwctl_r86_load_ns()
        if loads[PWCTL_R86_NS].get("module_id") is None:
            return _pwctl_r86_block(
                entry, failures, "probe null sink never enumerated",
                loads)
        g0 = _pwctl_r86_graph()
        na = _pwctl_r86_node(g0, PWCTL_R86_NS) or {}
        nid = na.get("node_id")
        ser = str(na.get("object_serial"))
        entry["ns_leaf"] = {"node_id": nid, "object_serial": ser,
                            "media_class": na.get("media_class")}
        if nid is None or ser in (None, "None"):
            return _pwctl_r86_block(
                entry, failures,
                "probe sink id/serial never resolved", loads)
        # ---------------- the addressing split ----------------
        legs["ls_serial"] = _pwctl_r86_pwcli("ls", ser)
        legs["ls_id"] = _pwctl_r86_pwcli("ls", nid)
        legs["info_id"] = _pwctl_r86_pwcli("info", nid)
        legs["info_serial"] = _pwctl_r86_pwcli("info", ser)
        legs["enum_serial"] = _pwctl_r86_pwcli(
            "enum-params", ser, "Props")
        legs["info_bogus"] = _pwctl_r86_pwcli("info", "bogus")
        # ---------------- class census ----------------
        for cls in ("Node", "Port", "Link", "Metadata", "Client",
                    "Bogus", "node", "Session", "SecurityContext"):
            legs[f"ls_{cls}"] = _pwctl_r86_pwcli("ls", cls)
        # ---------------- pw-dump surface ----------------
        legs["dump_id"] = _pwctl_r86_run(["pw-dump", str(nid)], 15.0)
        legs["dump_serial"] = _pwctl_r86_run(["pw-dump", ser], 15.0)
        legs["dump_badid"] = _pwctl_r86_run(["pw-dump", "99999"], 15.0)
        legs["dump_bogus"] = _pwctl_r86_run(["pw-dump", "bogus"], 15.0)
        legs["dump_color_sep"] = _pwctl_r86_run(
            ["pw-dump", "-C", "never"], 15.0)
        legs["dump_color_join"] = _pwctl_r86_run(
            ["pw-dump", "-Cnever"], 15.0)
        # host-bimodal (0B on the boundary boot, rc=255 `Unknown
        # color: =never` on this one) — RECORDED ONLY, never armed
        legs["dump_color_eq"] = _pwctl_r86_run(
            ["pw-dump", "-C=never"], 15.0)
        legs["info_all"] = _pwctl_r86_pwcli("info", "all",
                                           timeout_s=25.0)
        legs["list_vars"] = _pwctl_r86_pwcli("list-vars")
        legs["list_remotes"] = _pwctl_r86_pwcli("list-remotes")
        legs["remote_down"] = _pwctl_r86_run(
            ["pw-cli", "-r", f"{PWCTL_R86_PREFIX}_nope", "ls", "Node"],
            12.0)
        mids = _pwctl_r86_meta_ids()
        entry["meta_store_ids"] = mids
        if mids:
            legs["meta_info_empty"] = _pwctl_r86_pwcli(
                "info", sorted(mids.values())[0])
        # ---------------- the self-Client law ----------------
        # full dumps are parsed, not previewed — two invocations, each
        # must carry exactly its own fresh pw-dump Client row.
        self_serials = []
        for rep in (1, 2):
            try:
                proc = subprocess.run(["pw-dump"], capture_output=True,
                                      timeout=20)
                dump = json.loads(proc.stdout or b"[]")
                selfs = [o for o in dump if (o.get("info") or {})
                         .get("props", {}).get("application.name")
                         == "pw-dump"]
                legs[f"dump_full{rep}"] = {
                    "exit_code": proc.returncode,
                    "objects": len(dump),
                    "self_clients": len(selfs),
                    "self_serials": sorted(
                        str((o.get("info") or {}).get("props", {})
                            .get("object.serial")) for o in selfs)}
                self_serials.append({s for s in
                                     legs[f"dump_full{rep}"]
                                     ["self_serials"]})
            except (subprocess.TimeoutExpired, OSError, ValueError) \
                    as exc:
                legs[f"dump_full{rep}"] = {"reader_error":
                                           type(exc).__name__}
                self_serials.append(set())
        # ------------- pw-cli destroy: the id-family write -------------
        legs["mk_self_loop"] = _pwctl_r86_run(
            ["pw-link", f"{PWCTL_R86_NS}:monitor_FL",
             f"{PWCTL_R86_NS}:playback_FL"], 10.0)
        time.sleep(0.4)
        own = [l for l in (_pwctl_r86_own_links() or [])
               if l["out"] == f"{PWCTL_R86_NS}:monitor_FL"
               and l["in"] == f"{PWCTL_R86_NS}:playback_FL"]
        legs["self_loop_census"] = {"links": own}
        if own:
            lid = own[0]["id"]
            legs["info_link"] = _pwctl_r86_pwcli("info", lid)
            legs["destroy_link"] = _pwctl_r86_pwcli("destroy", lid)
            time.sleep(0.4)
            rest = [l["id"] for l in (_pwctl_r86_own_links() or [])
                    if l["id"] == lid]
            legs["destroy_census"] = {"link_id": lid,
                                      "surviving": rest}
    finally:
        _pwctl_r86_teardown(entry, failures, loads)
    # ---------------- verdicts ----------------
    l = legs["ls_serial"]
    if l.get("exit_code") != 0 or \
            f'object.serial = "{ser}"' not in (l.get("stdout") or "") \
            or f"id {nid}," not in (l.get("stdout") or ""):
        failures.append(
            f"ls_serial: rc={l.get('exit_code')} — ls <serial> did "
            "not resolve the node")
    l = legs["ls_id"]
    if l.get("exit_code") != 0 or \
            f'object.serial = "{ser}"' in (l.get("stdout") or ""):
        failures.append(
            f"ls_id: rc={l.get('exit_code')} — ls <id> resolved the "
            "node (serial namespace violated)")
    l = legs["info_id"]
    if l.get("exit_code") != 0 or \
            f"id: {nid}" not in (l.get("stdout") or ""):
        failures.append(
            f"info_id: rc={l.get('exit_code')} — info <id> did not "
            "resolve the node")
    l = legs["info_serial"]
    if l.get("exit_code") != 0 or \
            l.get("error_class") != "pwcli_unknown_global":
        failures.append(
            f"info_serial: rc={l.get('exit_code')} class="
            f"{l.get('error_class')} — the rc-0 unknown-global shape "
            "fails")
    l = legs["enum_serial"]
    if l.get("exit_code") != 0 or \
            l.get("error_class") != "pwcli_unknown_global":
        failures.append(
            f"enum_serial: rc={l.get('exit_code')} class="
            f"{l.get('error_class')} — enum-params <serial> is not "
            "the id-family refusal")
    l = legs["info_bogus"]
    if l.get("exit_code") != 0 or \
            l.get("error_class") != "pwcli_unknown_global":
        failures.append(
            f"info_bogus: rc={l.get('exit_code')} class="
            f"{l.get('error_class')}")
    for cls in ("Node", "Port", "Metadata", "Client"):
        l = legs[f"ls_{cls}"]
        rows = re.findall(r"\bid (\d+),\s*type "
                          r"PipeWire:Interface:(\w+)/",
                          l.get("stdout") or "")
        legs[f"ls_{cls}"]["typed_rows"] = len(rows)
        if l.get("exit_code") != 0 or not rows or \
                any(t != cls for _, t in rows):
            failures.append(
                f"ls_{cls}: rc={l.get('exit_code')} rows={len(rows)} "
                "— the class census shape fails")
    for cls in ("Bogus", "node", "Session"):
        l = legs[f"ls_{cls}"]
        if l.get("exit_code") != 0 or l.get("stdout_bytes") != 0:
            failures.append(
                f"ls_{cls}: rc={l.get('exit_code')} bytes="
                f"{l.get('stdout_bytes')} — the "
                "indistinguishable-empty law fails")
    for nm in ("dump_id", "dump_serial"):
        l = legs[nm]
        if l.get("exit_code") != 0 or l.get("stdout_bytes") == 0 \
                or f'"id": {nid}' not in (l.get("stdout") or ""):
            failures.append(
                f"{nm}: rc={l.get('exit_code')} bytes="
                f"{l.get('stdout_bytes')} — pw-dump <id|serial> did "
                "not resolve the node")
    if legs["dump_id"].get("stdout") != legs["dump_serial"].get(
            "stdout"):
        failures.append(
            "dump_id vs dump_serial: different bytes — <id> and "
            "<serial> resolved differently")
    for nm in ("dump_badid", "dump_bogus", "dump_color_sep"):
        l = legs[nm]
        if l.get("exit_code") != 0 or l.get("stdout_bytes") != 0:
            failures.append(
                f"{nm}: rc={l.get('exit_code')} bytes="
                f"{l.get('stdout_bytes')} — the silent-empty refusal "
                "fails")
    l = legs["dump_color_join"]
    if l.get("exit_code") != 0 or l.get("stdout_bytes") < 1000:
        failures.append(
            f"dump_color_join: rc={l.get('exit_code')} bytes="
            f"{l.get('stdout_bytes')} — joined -Cnever did not dump")
    legs["dump_color_eq"]["armed"] = False   # bimodal — data only
    for rep in (1, 2):
        l = legs[f"dump_full{rep}"]
        if l.get("exit_code") != 0 or l.get("self_clients", 0) < 1:
            failures.append(
                f"dump_full{rep}: rc={l.get('exit_code')} selfs="
                f"{l.get('self_clients')} — the self-Client law fails")
    l = legs["info_all"]
    if l.get("exit_code") != 0 or l.get("stdout_bytes") < 10000:
        failures.append(
            f"info_all: rc={l.get('exit_code')} bytes="
            f"{l.get('stdout_bytes')}")
    for nm in ("list_vars", "list_remotes"):
        l = legs[nm]
        if l.get("exit_code") != 0 or l.get("stdout_bytes") == 0:
            failures.append(
                f"{nm}: rc={l.get('exit_code')} bytes="
                f"{l.get('stdout_bytes')}")
    l = legs["remote_down"]
    if l.get("exit_code") == 0 or \
            "failed to connect" not in ((l.get("stderr") or "") +
                                        (l.get("stdout") or "")):
        failures.append(
            f"remote_down: rc={l.get('exit_code')} — the bogus-remote "
            "refusal is not a real nonzero")
    if "meta_info_empty" in legs:
        l = legs["meta_info_empty"]
        if l.get("exit_code") != 0 or l.get("stdout_bytes") != 0:
            failures.append(
                f"meta_info_empty: rc={l.get('exit_code')} bytes="
                f"{l.get('stdout_bytes')} — info on a live Metadata "
                "object is not silent-empty")
    l = legs["mk_self_loop"]
    if l.get("exit_code") != 0 or not legs["self_loop_census"]["links"]:
        failures.append(
            f"mk_self_loop: rc={l.get('exit_code')} — the self-loop "
            "never formed")
    if "info_link" in legs:
        l = legs["info_link"]
        ok = all(k in (l.get("stdout") or "") for k in
                 ("output-node-id", "input-node-id", "state"))
        legs["info_link"]["format_pod"] = l.get("has_pod")
        if l.get("exit_code") != 0 or not ok:
            failures.append(
                f"info_link: rc={l.get('exit_code')} — the live-link "
                "census fields are absent")
    if "destroy_link" in legs:
        l = legs["destroy_link"]
        if l.get("exit_code") != 0 or \
                legs["destroy_census"]["surviving"]:
            failures.append(
                f"destroy_link: rc={l.get('exit_code')} surviving="
                f"{legs['destroy_census']['surviving']} — pw-cli "
                "destroy did not remove the link")
    entry["legs"] = legs
    entry["failures"] = failures
    return entry


def pwctl_params_r86_entry():
    """The enum-params exposure matrix (Node/Port/Device dump sets,
    the not-implemented classes, remote ENOENT, the pre-negotiation
    Format absence, name==number equivalence) + the set-param
    write-refusal lattice (None echo, empty pod, stripped keys,
    wrong-type slot, remote -95, port not-implemented, bad id,
    usage)."""
    failures, legs = [], {}
    entry = _pwctl_r86_entry_head(
        "r86a enum-params matrix + set-param write-refusal lattice")
    tools = {t: shutil.which(t) for t in
             ("pw-cli", "pw-dump", "pw-link", "pactl")}
    entry["tools"] = tools
    if not all(tools.values()):
        return _pwctl_r86_block(
            entry, failures,
            f"missing tools: {[t for t, p in tools.items() if not p]}")
    loads = {}
    try:
        loads[PWCTL_R86_NS] = _pwctl_r86_load_ns()
        if loads[PWCTL_R86_NS].get("module_id") is None:
            return _pwctl_r86_block(
                entry, failures, "probe null sink never enumerated",
                loads)
        g0 = _pwctl_r86_graph()
        na = _pwctl_r86_node(g0, PWCTL_R86_NS) or {}
        nid = na.get("node_id")
        ports = _pwctl_r86_node_ports(g0, nid)
        port0 = ports.get("playback_FL")
        dev = (_pwctl_r86_dump_ids("Device") or [None])[0]
        cli = (_pwctl_r86_dump_ids("Client") or [None])[0]
        fac = (_pwctl_r86_dump_ids("Factory") or [None])[0]
        mod = (_pwctl_r86_dump_ids("Module") or [None])[0]
        entry["subjects"] = {"node": nid, "port": port0,
                             "device": dev, "client": cli,
                             "factory": fac, "module": mod}
        if nid is None or port0 is None or dev is None:
            return _pwctl_r86_block(
                entry, failures,
                "probe node/port/device subjects never resolved",
                loads)
        # a self-loop gives the Link-class row a live subject
        legs["mk_self_loop"] = _pwctl_r86_run(
            ["pw-link", f"{PWCTL_R86_NS}:monitor_FR",
             f"{PWCTL_R86_NS}:playback_FR"], 10.0)
        time.sleep(0.4)
        own = [l for l in (_pwctl_r86_own_links() or [])
               if l["out"] == f"{PWCTL_R86_NS}:monitor_FR"]
        lid = own[0]["id"] if own else None
        entry["subjects"]["link"] = lid

        def enu(obj, param):
            return _pwctl_r86_pwcli("enum-params", obj, param)

        def setp(obj, param, *js):
            return _pwctl_r86_pwcli("set-param", obj, param, *js)

        # ---------------- Node row ----------------
        legs["n_props"] = enu(nid, "Props")
        legs["n_propinfo"] = enu(nid, "PropInfo")
        legs["n_enumformat"] = enu(nid, "EnumFormat")
        legs["n_num3"] = enu(nid, "3")
        legs["n_format"] = enu(nid, "Format")
        legs["n_latency"] = enu(nid, "Latency")
        legs["n_proclat"] = enu(nid, "ProcessLatency")
        legs["n_io"] = enu(nid, "IO")
        legs["n_meta"] = enu(nid, "Meta")
        legs["n_profile"] = enu(nid, "Profile")
        legs["n_bogus"] = enu(nid, "Bogus")
        legs["n_999"] = enu(nid, "999")
        legs["n_all"] = enu(nid, "all")
        legs["enum_badobj"] = enu("99999", "Props")
        # ---------------- Port row ----------------
        legs["p_enumformat"] = enu(port0, "EnumFormat")
        legs["p_latency"] = enu(port0, "Latency")
        legs["p_io"] = enu(port0, "IO")
        legs["p_meta"] = enu(port0, "Meta")
        legs["p_props"] = enu(port0, "Props")
        legs["p_format"] = enu(port0, "Format")
        # ---------------- Device row ----------------
        legs["d_profile"] = enu(dev, "Profile")
        legs["d_enumprofile"] = enu(dev, "EnumProfile")
        legs["d_enumroute"] = enu(dev, "EnumRoute")
        legs["d_route"] = enu(dev, "Route")      # silent-vs-dump —
                                               # recorded, not armed
        legs["d_props"] = enu(dev, "Props")
        # ---------------- not-implemented classes ----------------
        for nm, obj in (("c_props", cli), ("f_props", fac),
                        ("m_props", mod), ("l_props", lid)):
            if obj is not None:
                legs[nm] = enu(obj, "Props")
        legs["core_setparam"] = setp("0", "Latency", "{ }")
        # ---------------- set-param write lattice ----------------
        legs["sp_garbage"] = setp(nid, "Props", "garbage")
        legs["sp_empty"] = setp(nid, "Props", "{ }")
        legs["sp_zzz"] = setp(nid, "Props", "{ zzz.r86a: 7 }")
        legs["re_zzz"] = enu(nid, "Props")
        legs["sp_voltype"] = setp(nid, "Props", '{ volume: "high" }')
        legs["re_vol"] = enu(nid, "Props")
        legs["sp_enumf"] = setp(nid, "EnumFormat",
                                "{ mediaType: 1, mediaSubtype: 1 }")
        legs["sp_port_lat"] = setp(port0, "Latency",
                                 "{ minQuantum: 2.0 }")
        legs["re_port_lat"] = enu(port0, "Latency")
        legs["sp_badid"] = setp("99999", "Props", "{ }")
        legs["sp_nojson"] = setp(nid, "Props")
        legs["sp_bogusp"] = setp(nid, "Bogus", "{ }")
    finally:
        _pwctl_r86_teardown(entry, failures, loads)
    # ---------------- verdicts ----------------
    for nm in ("n_props", "n_propinfo", "n_enumformat",
               "p_enumformat", "p_latency", "p_io", "p_meta",
               "d_profile", "d_enumprofile", "d_enumroute"):
        l = legs[nm]
        if l.get("exit_code") != 0 or not l.get("has_pod"):
            failures.append(
                f"{nm}: rc={l.get('exit_code')} pod="
                f"{l.get('has_pod')} — the exposure-matrix dump is "
                "absent")
    for nm in ("p_format", "n_latency", "n_proclat"):
        l = legs[nm]
        if l.get("exit_code") != 0 or l.get("has_pod"):
            failures.append(
                f"{nm}: rc={l.get('exit_code')} pod="
                f"{l.get('has_pod')} — the pod-absence law fails "
                "(refusal TEXT is racy, judged on presence only)")
    # Node Format is the state-dependent row: absent before
    # negotiation, exposed after WP negotiates it (measured BOTH ways
    # on this host — the boundary's presence-tracks-negotiation law) —
    # only the rc0 family is armed, the pod is recorded.
    l = legs["n_format"]
    if l.get("exit_code") != 0:
        failures.append(
            f"n_format: rc={l.get('exit_code')} — the rc-0 family "
            "fails (pod presence is negotiation-tracked, recorded)")
    legs["n_format"]["armed"] = "rc_only"
    for nm in ("n_io", "n_meta", "n_profile", "p_props", "d_props"):
        l = legs[nm]
        if l.get("exit_code") != 0 or \
                l.get("error_class") != "pwcli_remote_enoent":
            failures.append(
                f"{nm}: rc={l.get('exit_code')} class="
                f"{l.get('error_class')} — the remote-ENOENT refusal "
                "fails")
    legs["d_route"]["armed"] = False   # realization — data only
    if legs["n_num3"].get("stdout") != legs["n_enumformat"].get(
            "stdout"):
        failures.append(
            "n_num3: numeric 3 != EnumFormat — the name==number law "
            "fails")
    for nm in ("n_bogus", "n_999", "n_all", "sp_bogusp"):
        l = legs[nm]
        if l.get("exit_code") != 0 or \
                l.get("error_class") != "pwcli_unknown_param":
            failures.append(
                f"{nm}: rc={l.get('exit_code')} class="
                f"{l.get('error_class')} — the unknown-param-type "
                "refusal fails")
    l = legs["enum_badobj"]
    if l.get("exit_code") != 0 or \
            l.get("error_class") != "pwcli_unknown_global":
        failures.append(
            f"enum_badobj: rc={l.get('exit_code')} class="
            f"{l.get('error_class')}")
    for nm in ("c_props", "f_props", "m_props", "l_props",
               "core_setparam"):
        l = legs.get(nm)
        if l is None:
            continue
        if l.get("exit_code") != 0 or \
                l.get("error_class") != "pwcli_not_impl":
            failures.append(
                f"{nm}: rc={l.get('exit_code')} class="
                f"{l.get('error_class')} — the not-implemented "
                "refusal fails")
    l = legs["sp_garbage"]
    if l.get("exit_code") != 0 or \
            (l.get("stdout") or "").strip() != "None":
        failures.append(
            f"sp_garbage: rc={l.get('exit_code')} out="
            f"{(l.get('stdout') or '').strip()[:40]!r} — the None "
            "parse-echo fails")
    l = legs["sp_empty"]
    if l.get("exit_code") != 0 or not l.get("has_pod"):
        failures.append(
            f"sp_empty: rc={l.get('exit_code')} — the empty-pod echo "
            "fails")
    if legs["sp_zzz"].get("exit_code") != 0 or \
            "zzz" in (legs["re_zzz"].get("stdout") or ""):
        failures.append(
            "sp_zzz: unknown key was stored — the stripped-keys law "
            "fails")
    l = legs["sp_voltype"]
    if l.get("exit_code") != 0 or "None" not in (l.get("stdout") or ""):
        failures.append(
            f"sp_voltype: rc={l.get('exit_code')} — the wrong-type "
            "None-slot echo fails")
    l = legs["sp_enumf"]
    if l.get("exit_code") != 0 or \
            l.get("error_class") != "pwcli_remote_notsup":
        failures.append(
            f"sp_enumf: rc={l.get('exit_code')} class="
            f"{l.get('error_class')} — the readonly-write remote "
            "refusal fails")
    l = legs["sp_port_lat"]
    if l.get("exit_code") != 0 or \
            l.get("error_class") != "pwcli_not_impl" or \
            "type:PipeWire:Interface:Port" not in (l.get("stderr")
                                                   or ""):
        failures.append(
            f"sp_port_lat: rc={l.get('exit_code')} class="
            f"{l.get('error_class')} — the port-write echo-lie shape "
            "fails")
    if not re.search(r"minQuantum[\s\S]{0,140}?Float 0\.000000",
                     legs["re_port_lat"].get("stdout") or ""):
        failures.append(
            "re_port_lat: minQuantum moved — the port write was NOT "
            "dropped")
    l = legs["sp_badid"]
    if l.get("exit_code") != 0 or \
            l.get("error_class") != "pwcli_unknown_global":
        failures.append(
            f"sp_badid: rc={l.get('exit_code')} class="
            f"{l.get('error_class')}")
    l = legs["sp_nojson"]
    if l.get("exit_code") != 0 or \
            l.get("error_class") != "pwcli_usage":
        failures.append(
            f"sp_nojson: rc={l.get('exit_code')} class="
            f"{l.get('error_class')} — the usage refusal fails")
    entry["legs"] = legs
    entry["failures"] = failures
    return entry


def pwctl_dsp_r86_entry():
    """set-param Props as LIVE DSP on the probe-owned null-sink — the
    three-way same-number split: channelVolumes LINEAR (x0.25/x0.5
    measured exactly), pactl % CUBIC (25% -> x0.015625), the scalar
    `volume` key DISPLAY-DEAD (param store moves, audio doesn't), plus
    the mute leg, the reversible-write restore leg, and the
    store<->pulse scale coupling (pactl reads the cube root back).
    Tap protocol per the r85 fold: the monitor tap is link-validated
    BEFORE the player spawns and every amplitude arm carries the
    same-run solo reference."""
    failures, legs = [], {}
    entry = _pwctl_r86_entry_head(
        "r86a set-param live-DSP / dead-key / cubic-contrast lattice")
    tools = {t: shutil.which(t) for t in
             ("pw-cli", "pw-dump", "pw-play", "pw-record", "pactl")}
    entry["tools"] = tools
    if not all(tools.values()):
        return _pwctl_r86_block(
            entry, failures,
            f"missing tools: {[t for t, p in tools.items() if not p]}")
    loads = {}
    try:
        loads[PWCTL_R86_NS] = _pwctl_r86_load_ns()
        if loads[PWCTL_R86_NS].get("module_id") is None:
            return _pwctl_r86_block(
                entry, failures, "probe null sink never enumerated",
                loads)
        g0 = _pwctl_r86_graph()
        na = _pwctl_r86_node(g0, PWCTL_R86_NS) or {}
        nid = na.get("node_id")
        if nid is None:
            return _pwctl_r86_block(
                entry, failures, "probe node id never resolved", loads)
        with tempfile.TemporaryDirectory(prefix="r86a-dsp-") as tmp:
            tone = Path(tmp) / "r86a_tone.wav"
            _playback_r78_write_tone(tone, PWCTL_R86_TONE_S)
            tapf = Path(tmp) / "dsp_tap.wav"
            tap = _playback_r78_tap(
                PWCTL_R86_NS, tapf,
                int(48000 * (PWCTL_R86_TONE_S + 1.0)),
                PWCTL_R86_TAP)
            t0 = time.monotonic()
            edges, waited = _pactlmon_r85_wait_tap_link(
                PWCTL_R86_NS, PWCTL_R86_TAP)
            legs["tap_link"] = {"edges": edges, "wait_s": waited}
            if not edges:
                if tap.poll() is None:
                    _alsapw_r84_killpg(tap)
                    tap.wait()
                return _pwctl_r86_block(
                    entry, failures,
                    "monitor tap never linked — dsp arms skipped",
                    loads)
            tag = f"{PWCTL_R86_PREFIX}_dsp"
            player = _pactlmon_r85_play(tag, PWCTL_R86_NS, tone,
                                        role=PWCTL_R86_ROLE)
            leaf, waited = _alsapw_r84_wait_attached(
                tag, timeout_s=PWCTL_R86_STREAM_WAIT_S)
            legs["player_attach"] = {
                "stream_index": (leaf or {}).get("index"),
                "sink": (leaf or {}).get("sink"),
                "wait_s": waited}

            def mark():
                return time.monotonic() - t0

            def sleep_to(at):
                left = at - mark()
                if left > 0:
                    time.sleep(left)

            def setp(param, js):
                rec = _pwctl_r86_run(
                    ["pw-cli", "set-param", str(nid), param, js], 10.0)
                rec["done_at_s"] = round(mark(), 3)
                return rec

            def pactl(*a):
                rec = _pwctl_r86_run(
                    ["pactl", *[str(x) for x in a]], 8.0)
                rec["done_at_s"] = round(mark(), 3)
                return rec

            writes = {}
            attached = leaf is not None and leaf.get("sink") not in (
                None, 4294967295)
            if attached:
                # pass A — solo ref -> linear cv25 -> cv50 -> mute
                sleep_to(mark() + 0.8)
                solo_lo, solo_hi = mark(), None
                sleep_to(solo_lo + 0.6)
                solo_hi = mark()
                writes["w_cv25"] = setp(
                    "Props", "{ channelVolumes: [0.25, 0.25] }")
                legs["pactl_after_cv25"] = pactl(
                    "get-sink-volume", PWCTL_R86_NS)
                sleep_to(writes["w_cv25"]["done_at_s"] + 1.1)
                writes["w_cv50"] = setp(
                    "Props", "{ channelVolumes: [0.5, 0.5] }")
                legs["pactl_after_cv50"] = pactl(
                    "get-sink-volume", PWCTL_R86_NS)
                sleep_to(writes["w_cv50"]["done_at_s"] + 1.1)
                writes["w_mute"] = setp("Props", "{ mute: true }")
                sleep_to(writes["w_mute"]["done_at_s"] + 1.1)
                # the reversible-write restore leg
                writes["w_reset"] = setp(
                    "Props",
                    "{ mute: false, channelVolumes: [1.0, 1.0] }")
                sleep_to(writes["w_reset"]["done_at_s"] + 1.1)
                # pass B — dead scalar key -> pactl cubic -> restore
                writes["w_dead"] = setp("Props", "{ volume: 0.25 }")
                legs["pactl_after_dead"] = pactl(
                    "get-sink-volume", PWCTL_R86_NS)
                legs["enum_after_dead"] = _pwctl_r86_pwcli(
                    "enum-params", nid, "Props")
                sleep_to(writes["w_dead"]["done_at_s"] + 1.1)
                writes["w_pa25"] = pactl(
                    "set-sink-volume", PWCTL_R86_NS, "25%")
                legs["pactl_read_25"] = pactl(
                    "get-sink-volume", PWCTL_R86_NS)
                sleep_to(writes["w_pa25"]["done_at_s"] + 1.1)
                writes["w_pa100"] = pactl(
                    "set-sink-volume", PWCTL_R86_NS, "100%")
                legs["pactl_read_100"] = pactl(
                    "get-sink-volume", PWCTL_R86_NS)
                sleep_to(writes["w_pa100"]["done_at_s"] + 1.0)
            legs["writes"] = writes
            legs["player_alive_at_end"] = player.poll() is None
            if player.poll() is None:
                _alsapw_r84_killpg(player, signal.SIGTERM)
            try:
                player.wait(timeout=3.0)
            except subprocess.TimeoutExpired:
                _alsapw_r84_killpg(player)
                player.wait()
            if tap.poll() is None:
                _alsapw_r84_killpg(tap, signal.SIGTERM)
            try:
                tap.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                _alsapw_r84_killpg(tap)
                tap.wait()
            legs["tap_exit"] = tap.returncode
            legs["player_exit"] = player.returncode
            legs["tap_stderr_tail"] = _capture_tail(
                tap.stderr.read().decode(errors="replace"), str(tapf))
            # -------- post-analysis: windowed medians per region ----
            series = _alsapw_r84_amp_series(tapf, 0.1)
            legs["tap_windows"] = len(series)
            legs["tap_peak_all"] = max(
                (a for _, a in series), default=None)

            def med(lo_t, hi_t):
                return _alsapw_r84_amp_med(series, lo_t, hi_t)

            if attached:
                regs = {"solo": (solo_lo, solo_hi)}
                for key, gap in (("cv25", "w_cv25"),
                                 ("cv50", "w_cv50"),
                                 ("mute", "w_mute"),
                                 ("reset", "w_reset"),
                                 ("dead", "w_dead"),
                                 ("pa25", "w_pa25"),
                                 ("pa100", "w_pa100")):
                    w = writes[gap]["done_at_s"]
                    regs[key] = (w + 0.35, w + 0.95)
                meds = {k: med(*r) for k, r in regs.items()}
                legs["regions"] = {k: {"t": [round(r[0], 2),
                                           round(r[1], 2)],
                                       "median_peak": meds[k]}
                                   for k, r in regs.items()}
    finally:
        _pwctl_r86_teardown(entry, failures, loads)
    # ---------------- verdicts ----------------
    if not legs["tap_link"]["edges"]:
        failures.append("tap_link: the monitor tap never validated")
    if not (legs.get("player_attach") or {}).get("sink"):
        entry.setdefault("coverage_blocked", []).append(
            "player never attached — dsp arms skipped")
    else:
        regs = legs.get("regions") or {}
        solo = (regs.get("solo") or {}).get("median_peak")

        def region(name, lo, hi):
            v = (regs.get(name) or {}).get("median_peak")
            if v is None or not (lo <= v <= hi):
                failures.append(
                    f"{name}: median_peak={v} outside "
                    f"[{lo},{hi}] — the DSP law fails")

        if solo is None or not (PWCTL_R86_SOLO_ENV[0] * PWCTL_R86_AMP
                                <= solo <=
                                PWCTL_R86_SOLO_ENV[1] * PWCTL_R86_AMP):
            failures.append(
                f"solo: median_peak={solo} outside the x8192 "
                f"{PWCTL_R86_SOLO_ENV} envelope — the tap/solo "
                "reference fails")
        else:
            region("cv25", PWCTL_R86_CV25_ENV[0] * PWCTL_R86_AMP,
                     PWCTL_R86_CV25_ENV[1] * PWCTL_R86_AMP)
            region("cv50", PWCTL_R86_CV50_ENV[0] * PWCTL_R86_AMP,
                     PWCTL_R86_CV50_ENV[1] * PWCTL_R86_AMP)
            mv = (regs.get("mute") or {}).get("median_peak")
            if mv is None or mv > PWCTL_R86_MUTE_MAX:
                failures.append(
                    f"mute: median_peak={mv} > {PWCTL_R86_MUTE_MAX} "
                    "— mute is not live DSP")
            region("reset",
                   PWCTL_R86_SOLO_ENV[0] * PWCTL_R86_AMP,
                   PWCTL_R86_SOLO_ENV[1] * PWCTL_R86_AMP)
            region("dead",
                   PWCTL_R86_SOLO_ENV[0] * PWCTL_R86_AMP,
                   PWCTL_R86_SOLO_ENV[1] * PWCTL_R86_AMP)
            region("pa25",
                   PWCTL_R86_PA25_ENV[0] * PWCTL_R86_AMP,
                   PWCTL_R86_PA25_ENV[1] * PWCTL_R86_AMP)
            region("pa100",
                   PWCTL_R86_SOLO_ENV[0] * PWCTL_R86_AMP,
                   PWCTL_R86_SOLO_ENV[1] * PWCTL_R86_AMP)
        # -------- the store<->pulse scale coupling --------
        def vol_pct(rec):
            m = re.search(r"(\d+)\s*%",
                          (rec or {}).get("stdout") or "")
            return int(m.group(1)) if m else None
        p25 = vol_pct(legs.get("pactl_after_cv25"))
        if p25 is None or not (PWCTL_R86_CUBIC_PCT[0] <= p25 <=
                               PWCTL_R86_CUBIC_PCT[1]):
            failures.append(
                f"pactl_after_cv25: {p25}% outside "
                f"{PWCTL_R86_CUBIC_PCT} — the cube-root read-back "
                "fails")
        pdead = vol_pct(legs.get("pactl_after_dead"))
        if pdead != 100:
            failures.append(
                f"pactl_after_dead: {pdead}% != 100 — the dead "
                "scalar key moved the pulse volume")
        dead = (legs.get("enum_after_dead") or {}).get("stdout") or ""
        if not re.search(r"Props:volume[\s\S]{0,120}?Float 0\.25",
                         dead):
            failures.append(
                "enum_after_dead: the param store does not read "
                "Float 0.25 back — the dead-key landing fails")
        if vol_pct(legs.get("pactl_read_25")) != 25:
            failures.append(
                f"pactl_read_25: {vol_pct(legs.get('pactl_read_25'))}"
                "% != 25")
        if vol_pct(legs.get("pactl_read_100")) != 100:
            failures.append(
                f"pactl_read_100: "
                f"{vol_pct(legs.get('pactl_read_100'))}% != 100 — "
                "the volume restore failed")
        for nm, want_rc0 in (("w_cv25", 0), ("w_cv50", 0),
                             ("w_mute", 0), ("w_reset", 0),
                             ("w_dead", 0)):
            l = (legs.get("writes") or {}).get(nm) or {}
            if l.get("exit_code") != want_rc0:
                failures.append(
                    f"{nm}: rc={l.get('exit_code')} — the set-param "
                    "write refused")
    entry["legs"] = legs
    entry["failures"] = failures
    return entry


def pwctl_meta_r86_entry():
    """The pw-metadata store lattice — the -l/ls/dump census gap, the
    local-echo-vs-persist split (live subject persists, dead 99997
    drops), full-replace overwrite, verbatim type persist, absent-key
    silence, -d key/subject semantics, the -m subject filter, and a
    READ-ONLY subject-0 baseline (session defaults are never
    written)."""
    failures, legs = [], {}
    entry = _pwctl_r86_entry_head(
        "r86a pw-metadata store laws + census gap")
    tools = {t: shutil.which(t) for t in
             ("pw-metadata", "pw-cli", "pw-dump", "pactl")}
    entry["tools"] = tools
    if not all(tools.values()):
        return _pwctl_r86_block(
            entry, failures,
            f"missing tools: {[t for t, p in tools.items() if not p]}")
    loads = {}
    try:
        loads[PWCTL_R86_NS] = _pwctl_r86_load_ns()
        if loads[PWCTL_R86_NS].get("module_id") is None:
            return _pwctl_r86_block(
                entry, failures, "probe null sink never enumerated",
                loads)
        g0 = _pwctl_r86_graph()
        na = _pwctl_r86_node(g0, PWCTL_R86_NS) or {}
        nid = na.get("node_id")
        if nid is None:
            return _pwctl_r86_block(
                entry, failures, "probe node id never resolved", loads)
        # ---------------- store census ----------------
        legs["meta_list"] = _pwctl_r86_meta("-l")
        legs["meta_bare"] = _pwctl_r86_meta()
        legs["meta_default"] = _pwctl_r86_meta("-n", "default")
        legs["meta_bogus"] = _pwctl_r86_meta(
            "-n", f"{PWCTL_R86_PREFIX}_nope")
        ls_ids = _pwctl_r86_ls_ids("Metadata")
        dump_ids = _pwctl_r86_dump_ids("Metadata")
        entry["meta_census"] = {
            "store_ids": sorted((legs["meta_list"].get("stdout") or "")
                                and [int(m.group(2)) for m in
                                     re.finditer(
                                         r'Found "([^"]+)" metadata '
                                         r'(\d+)',
                                         legs["meta_list"]["stdout"])]
                                or []),
            "ls_ids": sorted(ls_ids or []),
            "dump_ids": sorted(dump_ids or [])}
        # ---------------- live-subject cycle ----------------
        K = PWCTL_R86_META_KEY
        legs["m_write"] = _pwctl_r86_meta("-n", "default", nid, K,
                                        "v1")
        legs["m_read"] = _pwctl_r86_meta("-n", "default", nid, K)
        legs["m_over"] = _pwctl_r86_meta("-n", "default", nid, K, "v2")
        legs["m_read2"] = _pwctl_r86_meta("-n", "default", nid, K)
        legs["m_typed"] = _pwctl_r86_meta("-n", "default", nid,
                                        f"{K}2", "v3", "Spa:String")
        legs["m_read3"] = _pwctl_r86_meta("-n", "default", nid,
                                        f"{K}2")
        legs["m_absent"] = _pwctl_r86_meta("-n", "default", nid,
                                         f"{K}_nope")
        legs["m_del"] = _pwctl_r86_meta("-n", "default", "-d", nid, K)
        legs["m_read4"] = _pwctl_r86_meta("-n", "default", nid, K)
        legs["m_delabsent"] = _pwctl_r86_meta("-n", "default", "-d",
                                            nid, f"{K}_nope")
        legs["m_dead_w"] = _pwctl_r86_meta(
            "-n", "default", PWCTL_R86_DEAD_SUBJECT, K, "v")
        legs["m_dead_r"] = _pwctl_r86_meta(
            "-n", "default", PWCTL_R86_DEAD_SUBJECT, K)
        legs["m_wipe"] = _pwctl_r86_meta("-n", "default", "-d", nid)
        legs["m_read5"] = _pwctl_r86_meta("-n", "default", nid)
        # ---------------- the -m subject filter ----------------
        _pwctl_r86_meta("-n", "default", nid, f"{K}_f", "fv")
        legs["m_filter"] = _pwctl_r86_meta("-n", "default", "-m", nid,
                                         timeout_s=1.4)
        legs["m_filter0"] = _pwctl_r86_meta("-n", "default", "-m", "0",
                                          timeout_s=1.4)
        _pwctl_r86_meta("-n", "default", "-d", nid)
        # ---------------- subject-0 baseline (READ-ONLY) ----------------
        legs["subj0_read"] = _pwctl_r86_meta("-n", "default", "0")
    finally:
        _pwctl_r86_teardown(entry, failures, loads, meta_subject=True)
    # ---------------- verdicts ----------------
    l = legs["meta_list"]
    if l.get("exit_code") != 0 or \
            not re.search(r'Found "[^"]+" metadata \d+',
                          l.get("stdout") or ""):
        failures.append(
            f"meta_list: rc={l.get('exit_code')} — the store census "
            "fails")
    if legs["meta_bare"].get("stdout") != \
            legs["meta_default"].get("stdout") or \
            legs["meta_bare"].get("exit_code") != 0:
        failures.append(
            "meta_bare: bare != -n default — the default-store "
            "alias fails")
    l = legs["meta_bogus"]
    if l.get("exit_code") != 0 or l.get("stdout_bytes") != 0:
        failures.append(
            f"meta_bogus: rc={l.get('exit_code')} bytes="
            f"{l.get('stdout_bytes')} — the bogus-store silent-empty "
            "fails")
    cen = entry["meta_census"]
    if cen["store_ids"] and cen["ls_ids"]:
        if cen["store_ids"] != cen["ls_ids"]:
            failures.append(
                f"meta_census: -l {cen['store_ids']} != ls "
                f"{cen['ls_ids']} — the two censuses disagree")
        if not (set(cen["dump_ids"]) < set(cen["ls_ids"])):
            failures.append(
                f"meta_census: dump {cen['dump_ids']} is not a "
                f"strict subset of ls {cen['ls_ids']} — the census "
                "gap fails")
    l = legs["m_write"]
    if l.get("exit_code") != 0 or \
            f"set property: id:{nid}" not in (l.get("stdout") or ""):
        failures.append(
            f"m_write: rc={l.get('exit_code')} — the set echo fails")
    l = legs["m_read"]
    rows = _pwctl_r86_update_rows(l.get("stdout"))
    if not any(f"id:{nid}" in r and f"key:'{PWCTL_R86_META_KEY}'" in r
               and "value:'v1'" in r for r in rows):
        failures.append("m_read: the live-subject read-back fails")
    l = legs["m_read2"]
    rows = _pwctl_r86_update_rows(l.get("stdout"))
    if not any("value:'v2'" in r for r in rows) or \
            any("value:'v1'" in r for r in rows):
        failures.append("m_read2: overwrite is not a full replace")
    l = legs["m_read3"]
    rows = _pwctl_r86_update_rows(l.get("stdout"))
    if not any("type:'Spa:String'" in r for r in rows):
        failures.append(
            "m_read3: the typed value did not persist verbatim")
    l = legs["m_absent"]
    if _pwctl_r86_update_rows(l.get("stdout")) or \
            l.get("exit_code") != 0:
        failures.append(
            "m_absent: absent-key read is not Found-only silent")
    l = legs["m_del"]
    if l.get("exit_code") != 0 or "delete property:" not in \
            (l.get("stdout") or ""):
        failures.append("m_del: the delete echo fails")
    if _pwctl_r86_update_rows(legs["m_read4"].get("stdout")):
        failures.append("m_read4: the key survived delete")
    l = legs["m_delabsent"]
    if l.get("exit_code") != 0 or "delete property:" not in \
            (l.get("stdout") or ""):
        failures.append(
            "m_delabsent: deleting an absent key is not the same "
            "echo no-op")
    if "set property:" not in (legs["m_dead_w"].get("stdout") or ""):
        failures.append("m_dead_w: the dead-subject echo fails")
    if _pwctl_r86_update_rows(legs["m_dead_r"].get("stdout")):
        failures.append(
            "m_dead_r: the dead-subject write persisted — the "
            "echo-lies law fails")
    l = legs["m_wipe"]
    if f"delete properties: id:{nid}" not in (l.get("stdout") or ""):
        failures.append("m_wipe: the subject-wipe echo fails")
    if _pwctl_r86_update_rows(legs["m_read5"].get("stdout")):
        failures.append(
            "m_read5: keys survived the subject wipe")
    l = legs["m_filter"]
    rows = _pwctl_r86_update_rows(l.get("stdout"))
    if not l.get("killed_at_bound") or not rows or \
            not all(f"id:{nid}" in r for r in rows):
        failures.append(
            f"m_filter: killed={l.get('killed_at_bound')} rows={rows}"
            " — the -m subject filter fails")
    l = legs["m_filter0"]
    rows0 = _pwctl_r86_update_rows(l.get("stdout"))
    if not l.get("killed_at_bound") or not rows0 or \
            not all("id:0" in r for r in rows0):
        failures.append(
            f"m_filter0: killed={l.get('killed_at_bound')} "
            f"rows={len(rows0)} — the -m 0 filter fails")
    l = legs["subj0_read"]
    if l.get("exit_code") != 0 or \
            'Found "default"' not in (l.get("stdout") or ""):
        failures.append(
            f"subj0_read: rc={l.get('exit_code')} — the read-only "
            "subject-0 baseline fails")
    legs["subj0_keys"] = sorted(set(re.findall(
        r"key:'([^']+)'", l.get("stdout") or "")))
    entry["legs"] = legs
    entry["failures"] = failures
    return entry


def pwctl_tools_r86_entry():
    """The process-surface lattice — pw-top batch-vs-TUI signal split
    (batch TERM is clean; the TUI path aborts with the loop.c:189
    assertion), the pw-cli stdin trichotomy (/dev/null aborts, pipe
    never exits, quit exits), the pw-jack env-shim lattice, and the
    pw-link rc=255 refusal family on the probe's own ports."""
    failures, legs = [], {}
    entry = _pwctl_r86_entry_head(
        "r86a pw-top/pw-jack/pw-link/pw-cli process lattice")
    tools = {t: shutil.which(t) for t in
             ("pw-top", "pw-jack", "pw-link", "pw-cli", "pw-dump",
              "pactl")}
    entry["tools"] = tools
    if not all(tools.values()):
        return _pwctl_r86_block(
            entry, failures,
            f"missing tools: {[t for t, p in tools.items() if not p]}")
    loads = {}
    try:
        loads[PWCTL_R86_NS] = _pwctl_r86_load_ns()
        if loads[PWCTL_R86_NS].get("module_id") is None:
            return _pwctl_r86_block(
                entry, failures, "probe null sink never enumerated",
                loads)
        g0 = _pwctl_r86_graph()
        na = _pwctl_r86_node(g0, PWCTL_R86_NS) or {}
        nid = na.get("node_id")
        ports = _pwctl_r86_node_ports(g0, nid)
        port0 = ports.get("playback_FL")
        entry["subjects"] = {"node": nid, "port": port0}
        # ---------------- pw-top ----------------
        legs["top_batch"] = _pwctl_r86_run(
            ["pw-top", "-b", "-n", "2"], 15.0)
        legs["top_batch0"] = _pwctl_r86_run(
            ["pw-top", "-b", "-n", "0"], 15.0)
        legs["top_batch_term"] = _pwctl_r86_sigleg(
            ["pw-top", "-b", "-n", "100000"], signal.SIGTERM, 1.0,
            6.0, "TERM@1.0")
        legs["top_tui_term"] = _pwctl_r86_sigleg(
            ["pw-top"], signal.SIGTERM, 1.4, 7.0, "TERM@1.4")
        legs["top_tui_kill"] = _pwctl_r86_sigleg(
            ["pw-top"], signal.SIGKILL, 1.2, 6.0, "KILL@1.2")
        # ---------------- pw-cli stdin trichotomy ----------------
        legs["cli_devnull"] = _pwctl_r86_run(
            ["pw-cli"], 7.0, nocore=True)
        legs["cli_quit"] = _pwctl_r86_run(
            ["pw-cli"], 10.0, stdin_data=b"quit\n")
        legs["cli_pipe"] = _pwctl_r86_run(
            ["pw-cli"], 4.0, stdin_data=b"ls\n")
        # ---------------- pw-jack env shim ----------------
        def jack(*args, env=None):
            return _pwctl_r86_run(
                ["pw-jack", *args, "sh", "-c",
                 'echo Q=${PIPEWIRE_QUANTUM-unset} '
                 'D=${PIPEWIRE_DEBUG-unset} R=${PIPEWIRE_REMOTE-unset}'],
                10.0, env=env)
        legs["jack_p"] = jack("-p", "512")
        legs["jack_sp"] = jack("-s", "44100", "-p", "256")
        legs["jack_s_only"] = jack("-s", "44100")
        legs["jack_v"] = jack("-v")
        legs["jack_vv"] = jack("-v", "-v")
        e4 = dict(os.environ); e4["PIPEWIRE_DEBUG"] = "4"
        legs["jack_v_preset"] = jack("-v", env=e4)
        legs["jack_r"] = jack("-r", f"{PWCTL_R86_PREFIX}_remote")
        legs["jack_help"] = _pwctl_r86_run(["pw-jack", "-h"], 10.0)
        legs["jack_noargs"] = _pwctl_r86_run(["pw-jack"], 10.0)
        legs["jack_badopt"] = _pwctl_r86_run(["pw-jack", "-Z"], 10.0)
        legs["jack_bogus"] = _pwctl_r86_run(
            ["pw-jack", f"{PWCTL_R86_PREFIX}_nocmd"], 10.0)
        # ---------------- pw-link rc lattice (own ports) ----------------
        legs["lk_create"] = _pwctl_r86_run(
            ["pw-link", f"{PWCTL_R86_NS}:monitor_FL",
             f"{PWCTL_R86_NS}:playback_FL"], 10.0)
        time.sleep(0.4)
        legs["lk_dup"] = _pwctl_r86_run(
            ["pw-link", f"{PWCTL_R86_NS}:monitor_FL",
             f"{PWCTL_R86_NS}:playback_FL"], 10.0)
        legs["lk_bogus"] = _pwctl_r86_run(
            ["pw-link", f"{PWCTL_R86_NS}:monitor_FL",
             f"{PWCTL_R86_BOGUS}:playback_FL"], 10.0)
        legs["lk_usage"] = _pwctl_r86_run(["pw-link"], 10.0)
        legs["lk_I_alone"] = _pwctl_r86_run(["pw-link", "-I"], 10.0)
        legs["lk_v_alone"] = _pwctl_r86_run(["pw-link", "-v"], 10.0)
        legs["lk_list"] = _pwctl_r86_run(["pw-link", "-l"], 10.0)
        legs["lk_list_I"] = _pwctl_r86_run(["pw-link", "-l", "-I"], 10.0)
        own = [l for l in (_pwctl_r86_own_links() or [])
               if l["out"] == f"{PWCTL_R86_NS}:monitor_FL"
               and l["in"] == f"{PWCTL_R86_NS}:playback_FL"]
        legs["lk_census"] = {"links": own}
        lid = own[0]["id"] if own else None
        if lid is not None:
            legs["lk_d_port"] = _pwctl_r86_run(
                ["pw-link", "-d", str(port0)], 10.0)
            legs["lk_d_link"] = _pwctl_r86_run(
                ["pw-link", "-d", str(lid)], 10.0)
            time.sleep(0.4)
            legs["lk_after_unlink"] = {"links": _pwctl_r86_own_links()}
        # -p accepts a junk props payload silently — the link forms
        legs["lk_junkprops"] = _pwctl_r86_run(
            ["pw-link", "-p", '{ "zzz_r86a": 1 }',
             f"{PWCTL_R86_NS}:monitor_FR",
             f"{PWCTL_R86_NS}:playback_FR"], 10.0)
        time.sleep(0.4)
        fr = [l for l in (_pwctl_r86_own_links() or [])
              if l["out"] == f"{PWCTL_R86_NS}:monitor_FR"]
        legs["lk_junkprops_census"] = {"links": fr}
        if fr:
            legs["lk_junkprops_unlink"] = _pwctl_r86_run(
                ["pw-link", "-d", str(fr[0]["id"])], 10.0)
    finally:
        _pwctl_r86_teardown(entry, failures, loads)
    # ---------------- verdicts ----------------
    l = legs["top_batch"]
    if l.get("exit_code") != 0 or "FORMAT" not in (l.get("stdout")
                                                 or "") \
            or "NAME" not in (l.get("stdout") or ""):
        failures.append(
            f"top_batch: rc={l.get('exit_code')} — the headless "
            "table fails")
    l = legs["top_batch0"]
    if l.get("exit_code") != 0 or l.get("stdout_lines", 0) < 1:
        failures.append(
            f"top_batch0: rc={l.get('exit_code')} lines="
            f"{l.get('stdout_lines')}")
    l = legs["top_batch_term"]
    if l.get("exit_code") != 0 or l.get("signal") or \
            l.get("loop_assert"):
        failures.append(
            f"top_batch_term: rc={l.get('exit_code')} sig="
            f"{l.get('signal')} assert={l.get('loop_assert')} — "
            "batch TERM is not clean (the narrowed law)")
    l = legs["top_tui_term"]
    if l.get("signal") != "SIGABRT" or not l.get("loop_assert"):
        failures.append(
            f"top_tui_term: sig={l.get('signal')} assert="
            f"{l.get('loop_assert')} — the TUI-path abort class "
            "fails")
    l = legs["top_tui_kill"]
    if l.get("signal") != "SIGKILL" or l.get("loop_assert"):
        failures.append(
            f"top_tui_kill: sig={l.get('signal')} assert="
            f"{l.get('loop_assert')}")
    l = legs["cli_devnull"]
    if l.get("signal") != "SIGABRT" or \
            "remove_from_poll" not in (l.get("stderr") or ""):
        failures.append(
            f"cli_devnull: sig={l.get('signal')} — the /dev/null "
            "abort class fails")
    l = legs["cli_quit"]
    if l.get("exit_code") != 0 or l.get("killed_at_bound"):
        failures.append(
            f"cli_quit: rc={l.get('exit_code')} killed="
            f"{l.get('killed_at_bound')} — quit is not the clean "
            "exit")
    l = legs["cli_pipe"]
    if not l.get("killed_at_bound") or l.get("signal") != "SIGKILL":
        failures.append(
            f"cli_pipe: killed={l.get('killed_at_bound')} sig="
            f"{l.get('signal')} — the pipe-stdin hang fails")

    def jack_env(name, want):
        l = legs[name]
        got = dict(m for m in re.findall(
            r"([QDR])=(\S+)", (l.get("stdout") or "")))
        legs[name]["env"] = got
        if l.get("exit_code") != 0 or any(
                got.get(k) != v for k, v in want.items()):
            failures.append(
                f"{name}: rc={l.get('exit_code')} env={got} != "
                f"{want} — the pw-jack shim law fails")

    jack_env("jack_p", {"Q": "512/48000"})
    jack_env("jack_sp", {"Q": "256/44100"})
    jack_env("jack_s_only", {"Q": "unset"})
    jack_env("jack_v", {"D": "3"})
    jack_env("jack_vv", {"D": "4"})
    jack_env("jack_v_preset", {"D": "5"})
    jack_env("jack_r", {"R": f"{PWCTL_R86_PREFIX}_remote"})
    for nm in ("jack_help", "jack_noargs", "jack_badopt"):
        l = legs[nm]
        if l.get("exit_code") != 0:
            failures.append(
                f"{nm}: rc={l.get('exit_code')} — pw-jack rc0 "
                "surface fails")
    if "illegal option" not in (legs["jack_badopt"].get("stderr")
                              or "") or \
            "run JACK applications" not in \
            (legs["jack_badopt"].get("stdout") or ""):
        failures.append(
            "jack_badopt: the -Z usage/illegal-option shape fails")
    l = legs["jack_bogus"]
    if l.get("exit_code") != 127 or \
            l.get("error_class") != "pwjack_exec":
        failures.append(
            f"jack_bogus: rc={l.get('exit_code')} class="
            f"{l.get('error_class')} — the exec-127 law fails")
    # ---------------- pw-link ----------------
    if legs["lk_create"].get("exit_code") != 0 or \
            not legs["lk_census"]["links"]:
        failures.append(
            f"lk_create: rc={legs['lk_create'].get('exit_code')} — "
            "the own-port link never formed")
    l = legs["lk_dup"]
    if l.get("exit_code") != 255 or \
            l.get("error_class") != "pwlink_exists":
        failures.append(
            f"lk_dup: rc={l.get('exit_code')} class="
            f"{l.get('error_class')} — the rc=255 File-exists "
            "refusal fails (the scout's rc=0 row stays falsified)")
    l = legs["lk_bogus"]
    if l.get("exit_code") != 255 or \
            l.get("error_class") != "pwlink_noent":
        failures.append(
            f"lk_bogus: rc={l.get('exit_code')} class="
            f"{l.get('error_class')}")
    for nm in ("lk_usage", "lk_I_alone", "lk_v_alone"):
        l = legs[nm]
        if l.get("exit_code") != 255:
            failures.append(
                f"{nm}: rc={l.get('exit_code')} — the modifier/usage "
                "refusal fails")
    for nm in ("lk_list", "lk_list_I"):
        l = legs[nm]
        if l.get("exit_code") != 0 or PWCTL_R86_NS not in \
                (l.get("stdout") or ""):
            failures.append(
                f"{nm}: rc={l.get('exit_code')} — the list mode "
                "fails")
    if "lk_d_port" in legs:
        l = legs["lk_d_port"]
        if l.get("exit_code") != 255:
            failures.append(
                f"lk_d_port: rc={l.get('exit_code')} — unlink wants "
                "a link id")
        l = legs["lk_d_link"]
        if l.get("exit_code") != 0 or \
                legs["lk_after_unlink"]["links"]:
            failures.append(
                f"lk_d_link: rc={l.get('exit_code')} — unlink by "
                "link id failed")
    l = legs["lk_junkprops"]
    if l.get("exit_code") != 0 or \
            not legs["lk_junkprops_census"]["links"]:
        failures.append(
            f"lk_junkprops: rc={l.get('exit_code')} — the silent "
            "props-accept law fails")
    entry["legs"] = legs
    entry["failures"] = failures
    return entry


