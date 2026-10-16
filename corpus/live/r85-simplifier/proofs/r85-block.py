# r85: the pactl short-name/serial addressing lattice + the monitor-stream
#     (N-streams-one-sink mixing + capture-side monitor/source surface)
#     leg lattice -- --probe-pactlmon-r85.
#
# A NEW parallel ledger family; prior rows untouched; every r76-r84 guard
# inherited (seat-owned r85a_*_<pid> names, name-verified module unloads —
# by the module's OWN sink_name=/source_name= arg, never a bare index and
# never a name substring; never set-default-*; bounded process groups;
# taps bounded by -n and link-validated; tag tones fail-closed to
# probe-owned sinks — the only shared-sink landings are the aplay SILENCE
# fallback legs and the prop-form default-monitor capture arms, both
# measured surfaces, recorded). Surface facts are the r85 scout's
# THIS-HOST measurements (PipeWire 1.6.8, pactl 17.0-98-gb096 protocol 35,
# libsndfile 1.2.2 — the sndfile suite itself is OUT of this family's
# scope: the move is the pactl/monstreams lattice) as CORRECTED by the
# r85 boundary:
#
#   PACTL VERB-ARG CLASSES (own sinks only, read verbs + move): a pactl
#     number is the object.serial, never the object.id (`No such
#     entity`); verbs are typed — @DEFAULT_SINK@ resolves as a sink arg
#     and @DEFAULT_SOURCE@/@DEFAULT_MONITOR@ as source args only;
#     <name>.monitor is a SOURCE arg; `""` is a different refusal
#     (`Operation failed: Invalid argument`); `0` resolves to the LIVE
#     default (the boundary's resolution of the scout's ambiguous row —
#     measured here by comparing its volume row with @DEFAULT_SINK@'s in
#     the same run); leading/trailing spaces, `+`, `.0`, `x` suffix and
#     `0x<hex>` of a real serial all parse; a `_`-grouped serial refuses.
#     The `0<digits>` leading-zero row is RECORDED ONLY — the boundary
#     measured rc=0 on one pass and rc=1 on another (octal-parse
#     hypothesis unproven) so no arm asserts it. Serials are monotonic
#     (unload+reload never reuses); the module INDEX is recycled
#     immediately — recorded, never armed (host-impl detail).
#
#   NAME/SERIAL COLLISION (boundary supplement): a sink literally NAMED
#     with another sink's serial does not shadow pactl's numeric arg —
#     `move-sink-input <stream> <digits>` lands on the serial holder. On
#     the pw-cat side the same digits resolve as a NAME first (a sink —
#     unusable as a noprop capture target): the record forms no monitor
#     link (stall or refusal — host-state realization, recorded).
#
#   --target CAPTURE LATTICE (boundary-corrected): noprop, a source
#     NAME / source SERIAL / source OBJECT.ID all bind the source's
#     capture_* ports (the scout's object.id stall is falsified); a sink
#     SERIAL noprop bypasses the prop gate and links the sink's
#     monitor_*; a sink NAME noprop NEVER links monitor_* (realizations:
#     arbitrary-source bind on the boundary host, outright
#     `no target node available` refusal on this authoring pass — the
#     arm asserts only the never-monitor invariant, realization
#     recorded); -P stream.capture.sink=true makes a sink name link its
#     own monitor_* and makes a SOURCE name resolve on the DEFAULT
#     sink's monitor (never touches the named source).
#
#   TARGET LOSS, folded falsification 15: a pw-record bound to a
#     remap-source whose module dies mid-record has its links destroyed
#     and NEVER re-created; the stream stays alive; the file carries NO
#     NEW CONTENT after the loss — the froze-vs-growing-zeros switch is
#     bimodal host state (the boundary froze 6/6, the scout grew zeros)
#     so the artifact shape is RECORDED ONLY. The prop form
#     (stream.capture.sink=true) re-links to the DEFAULT sink's monitor
#     instead (r80/r81 law, re-confirmed).
#
#   Audio/Source NULL-SINK self-destruct (confirmed+widened): a
#     module-null-sink with media.class=Audio/Source survives idle
#     (>=3.5 s window armed), dies on a CLIENT BIND (pw-record and parec
#     armed <=1.5 s; module death precedes node death), never dies on a
#     manual pw-link, and is never touched by the prop form (which
#     captures the default monitor). No late-bind: an absent-name
#     --target stall is NOT re-armed by a conforming source appearing
#     mid-stall (boundary 3/3 quiet + 3/3 load).
#
#   MIXING on one sink (monitor-tap laws): N streams share the sink's
#     TWO playback_* port objects (4 links -> 2 ports); the mix is an
#     exact linear sum — each tone keeps full amplitude with ZERO
#     channel bleed; the same file twice sums coherently to 2x (pinned
#     as an envelope — quantum alignment held 6/6 on the boundary but is
#     load-slip-capable, so the inverse leg is CLASSIFIED not armed);
#     a sum over full scale hard-clips at the s16 tap (peak 32767 +
#     rail fraction envelope + clip products — the phase-dependent
#     amplitudes are never pinned). TAP PROTOCOL (the boundary's NEW
#     HAZARD folded): the monitor tap is link-validated BEFORE any
#     player starts and every amplitude arm carries the solo reference
#     in the same run — an unvalidated tap read 0 or exactly 1/8 in the
#     boundary's vacuous first battery; bare amplitude never arms here.
#
#   aplay -D pipewire ENV (3 new boundary laws): PIPEWIRE_NODE=<sink>
#     and PIPEWIRE_PROPS='{ target.object=<sink> }' both publish
#     target.object and link the named sink; on a conflict the PROPS
#     target.object wins; a numeric serial inside props resolves; a
#     BOGUS PIPEWIRE_NODE publishes the bogus target.object but silently
#     falls back to the live default (measured with a SILENCE file —
#     no tag tone ever lands on the shared sink from this family).
#
# Rows assert rc + error class + graph targets + envelopes. The family
# lock serializes same-family runs — two concurrent pactlmon runs would
# cross-credit taps and contest the collision/cycle sinks. Every spawned
# stream carries the PRIVATE media.role r85arole<pid> — never the shared
# `music` restore key (r84's contamination lesson).

PACTLMON_R85_PID = os.getpid()
PACTLMON_R85_PREFIX = f"r85a_{PACTLMON_R85_PID}"
PACTLMON_R85_NS = f"r85a_ns_{PACTLMON_R85_PID}"      # addressing sink A
PACTLMON_R85_NS2 = f"r85a_ns2_{PACTLMON_R85_PID}"    # move/collision sink B
PACTLMON_R85_MIX = f"r85a_mix_{PACTLMON_R85_PID}"    # the mixing sink
PACTLMON_R85_TONE = f"r85a_tone_{PACTLMON_R85_PID}"  # capture-carrier sink
PACTLMON_R85_VSRC = f"r85a_vsrc_{PACTLMON_R85_PID}"  # remap-source (loss)
PACTLMON_R85_SD = f"r85a_sd_{PACTLMON_R85_PID}"      # Audio/Source trap
PACTLMON_R85_LATE = f"r85a_late_{PACTLMON_R85_PID}"  # late-bind name
PACTLMON_R85_CYC = f"r85a_cyc_{PACTLMON_R85_PID}"    # serial-cycle sink
PACTLMON_R85_ROLE = f"r85arole{PACTLMON_R85_PID}"    # private restore key —
                                                    # NEVER shared `music`
PACTLMON_R85_BOGUS = "no_such_r85a"
PACTLMON_R85_STREAM_WAIT_S = 8.0
PACTLMON_R85_LINK_WAIT_S = 5.0
PACTLMON_R85_TAP_WAIT_S = 6.0
PACTLMON_R85_FEED_S = 30.0       # feed tone seconds (outlives the entry)
PACTLMON_R85_AMP = PLAYBACK_R78_TONE_AMP            # 8192
PACTLMON_R85_F3 = 2711.0         # stream-B freqs — clear of the pid-offset
PACTLMON_R85_F4 = 3214.0         # A pair (L<=1630, R<=2133) + harmonics
PACTLMON_R85_SOLO_ENV = (0.85, 1.18)    # x8192 solo/ref amplitude window
PACTLMON_R85_BLEED_MAX = 0.05           # cross-channel spectral bleed cap
PACTLMON_R85_DUP_ENV = (1.80, 2.20)     # the coherent 2x-sum envelope
PACTLMON_R85_CLIP_AMP = 24576           # 0.75 FS per stream
PACTLMON_R85_RAIL_ENV = (0.08, 0.60)    # clipped-frame fraction envelope
PACTLMON_R85_SPUR_MIN = 300.0           # clip-product floor
PACTLMON_R85_FLUSH_BOUND = 16384        # post-loss in-flight flush cap
                                        # (8 quanta; measured 2048)


# r85-local error classes — family-local, checked before the r84 chain
# (never prepended into _CAPTURE_ERR_CLASSES; pa_invalid_arg is the
# empty-string pactl refusal, pwcli_unknown_global is pw-cli's rc-0
# lie shape).
_PACTLMON_R85_ERR_CLASSES = (
    ("pa_invalid_arg", r"Operation failed: Invalid argument"),
    ("pwcli_unknown_global", r"unknown global '[^\n]*'"),
)


def _pactlmon_r85_errclass(text):
    """r85-local classes first, then the r84 pactl/alsa table and the
    shared pw table through it."""
    for name, pat in _PACTLMON_R85_ERR_CLASSES:
        m = re.search(pat, text or "")
        if m:
            return name, m.group(0).strip()
    return _alsapw_r84_errclass(text or "")


def _pactlmon_r85_loadavg():
    return _alsapw_r84_loadavg()


def _pactlmon_r85_run(argv, timeout_s, env=None):
    """One bounded spawn -> rc/signal/std(out|err) + r85 error class.
    killed_at_bound separates a harness kill from an app refusal."""
    shown = " ".join(str(a) for a in argv)
    rec = {"argv": shown}
    try:
        proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.DEVNULL,
                                env=env, start_new_session=True)
    except OSError as exc:
        rec["spawn_error"] = str(exc)[:160]
        return rec
    t0 = time.monotonic()
    killed = False
    try:
        out, err = proc.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        killed = True
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = proc.communicate()
    errt = err.decode(errors="replace")
    outt = out.decode(errors="replace")
    cls, hit = _pactlmon_r85_errclass(errt)
    rec.update({"exit_code": proc.returncode,
                "signal": (signal.Signals(-proc.returncode).name
                           if (proc.returncode or 0) < 0 else None),
                "killed_at_bound": killed,
                "wall_s": round(time.monotonic() - t0, 3),
                "stdout_head": outt.strip().splitlines()[:3],
                "stdout": outt[:700],
                "stderr_head": errt.strip().splitlines()[:3],
                "stderr": errt[:900],
                "error_class": cls, "error_hit": hit})
    return rec


def _pactlmon_r85_pactl(*args, timeout_s=8.0):
    return _pactlmon_r85_run(["pactl", *[str(a) for a in args]],
                             timeout_s)


def _pactlmon_r85_graph():
    """pw-dump -> {nodes, ports, links}. r85 keeps object.id +
    object.serial + media.class + target.object — the addressing surface
    under test (the r84 graph drops the serial set)."""
    try:
        proc = subprocess.run(["pw-dump"], capture_output=True,
                              timeout=15)
        dump = json.loads(proc.stdout or b"[]")
    except (subprocess.TimeoutExpired, OSError, ValueError) as exc:
        return {"error": type(exc).__name__}
    nodes, ports, links = {}, {}, []
    for o in dump:
        t = str(o.get("type", ""))
        info = o.get("info") or {}
        props = info.get("props") or {}
        if t.endswith("Node"):
            nodes[o["id"]] = {
                "name": props.get("node.name"),
                "state": info.get("state"),
                "media_class": props.get("media.class"),
                "object_serial": props.get("object.serial"),
                "object_id": props.get("object.id"),
                "target_object": props.get("target.object"),
                "node_latency": props.get("node.latency")}
        elif t.endswith("Port"):
            ports[o["id"]] = {
                "node_id": (info.get("node-id")
                            or props.get("node.id")),
                "name": props.get("port.name"),
                "direction": (info.get("direction")
                              or props.get("port.direction"))}
        elif t.endswith("Link"):
            links.append({"out_node": info.get("output-node-id"),
                          "out_port": info.get("output-port-id"),
                          "in_node": info.get("input-node-id"),
                          "in_port": info.get("input-port-id"),
                          "state": info.get("state")})
    return {"nodes": nodes, "ports": ports, "links": links}


def _pactlmon_r85_node(g, name):
    """The node leaf whose node.name is exactly `name` (None absent) —
    carries object.id + object.serial."""
    for nid, n in (g.get("nodes") or {}).items():
        if n.get("name") == name:
            return {"node_id": nid, **n}
    return None


def _pactlmon_r85_edges(g):
    """Directed edges as name:port pairs — the link-shape witness."""
    out = []
    nodes, ports = g.get("nodes", {}), g.get("ports", {})
    for l in g.get("links", []):
        op = ports.get(l["out_port"]) or {}
        ip = ports.get(l["in_port"]) or {}
        on = (nodes.get(l["out_node"]) or {}).get("name")
        inn = (nodes.get(l["in_node"]) or {}).get("name")
        out.append({"out": f"{on}:{op.get('name')}",
                    "in": f"{inn}:{ip.get('name')}",
                    "out_node": on, "in_node": inn,
                    "out_port_name": op.get("name"),
                    "in_port_name": ip.get("name"),
                    "state": l.get("state")})
    return sorted(out, key=lambda e: (str(e["out"]), str(e["in"])))


def _pactlmon_r85_edges_in(g, in_node_name):
    """Edges landing on <name>:input_* — a capture stream's bindings."""
    return [e for e in _pactlmon_r85_edges(g)
            if e.get("in_node") == in_node_name]


def _pactlmon_r85_edges_out(g, out_node_name):
    return [e for e in _pactlmon_r85_edges(g)
            if e.get("out_node") == out_node_name]


def _pactlmon_r85_module_index(field, value):
    """`pactl list modules short` -> the index whose ARG STRING carries
    `field=value` as an exact field (the module's OWN declared name —
    sink_name= for null sinks, source_name= for remap sources). The
    r85-scout mod_index() grep covered sink_name only and its
    remap-source unloads never fired (the s3d vacuity); this reader
    takes the field name explicitly so a source module is found by its
    source_name= line. Exact equality — a foreign r85a_* prefix must
    never answer."""
    try:
        proc = subprocess.run(["pactl", "list", "modules", "short"],
                              capture_output=True, timeout=10)
    except (subprocess.TimeoutExpired, OSError):
        return None
    for ln in proc.stdout.decode(errors="replace").splitlines():
        f = ln.split("\t")
        if not (f and f[0].strip().isdigit()):
            continue
        m = re.search(re.escape(field) + r"=(\S+)", ln)
        if m and m.group(1).strip("\"'") == value:
            return int(f[0].strip())
    return None


def _pactlmon_r85_unload_own(module_id, field, value):
    """Unload by the NAME-VERIFIED index only: re-read the module table
    immediately before firing and require the index whose args carry OUR
    `field=value`; a captured id is never fired (index recycling is
    measured, immediate, on this host — firing a stale id would kill a
    foreign module). `field` is `sink_name` or `source_name` — the
    caller names the module's own arg."""
    idx = _pactlmon_r85_module_index(field, value)
    res = {"verified_index": idx, "captured": module_id,
           "field": field, "value": value}
    if idx is None:
        res["skipped"] = "not_listed"
        return res
    res["recycled"] = (module_id is not None and idx != module_id)
    try:
        proc = subprocess.run(["pactl", "unload-module", str(idx)],
                              capture_output=True, timeout=15)
        res["exit_code"] = proc.returncode
        res["stderr_tail"] = proc.stderr.decode(
            errors="replace").strip()[:120] or None
    except (subprocess.TimeoutExpired, OSError) as exc:
        res["exit_code"] = None
        res["error"] = str(exc)[:120]
    return res


def _pactlmon_r85_remap_load(master_monitor, source_name):
    """Load module-remap-source master=<master_monitor>
    source_name=<source_name>; gate on the pactl source listing AND the
    node's own capture ports — the instrument behind the loss and
    target-lattice legs (a real deletable Audio/Source, unlike the
    media.class=Audio/Source null-sink trap). On a partial enumeration
    the module is removed through the source_name-verified unload."""
    leaf = {"field": "source_name", "value": source_name,
            "master": master_monitor}
    try:
        proc = subprocess.run(
            ["pactl", "load-module", "module-remap-source",
             f"master={master_monitor}",
             f"source_name={source_name}"],
            capture_output=True, timeout=15)
        mid = proc.stdout.decode(errors="replace").strip()
        leaf["module_id"] = int(mid) if mid.isdigit() else None
        leaf["rc"] = proc.returncode
        leaf["error"] = proc.stderr.decode(
            errors="replace")[:160] or None
    except (subprocess.TimeoutExpired, OSError) as exc:
        leaf.update({"module_id": None, "rc": None,
                     "error": str(exc)[:160]})
        return leaf
    if leaf.get("module_id") is None:
        return leaf
    t0 = time.monotonic()
    seen = ports = False
    while time.monotonic() - t0 < PACTLMON_R85_LINK_WAIT_S:
        seen = source_name in (_playback_r78_source_names() or [])
        ports = bool(_playback_r78_output_ports(source_name))
        if seen and ports:
            break
        time.sleep(0.1)
    leaf["source_seen"] = seen
    leaf["capture_ports"] = ports
    leaf["waited_s"] = round(time.monotonic() - t0, 3)
    if not (seen and ports):
        leaf["error"] = "source/capture ports never enumerated — " \
                        "unloaded"
        _pactlmon_r85_unload_own(leaf["module_id"], "source_name",
                                 source_name)
        leaf["module_id"] = None
    return leaf


def _pactlmon_r85_sd_load(name):
    """Load `module-null-sink sink_name=<name> media.class=Audio/Source`
    — the self-destruct trap node. It is a SOURCE (never appears in
    `list sinks`, so _pwcat_r83_ns_load's sink gate cannot see it) with
    a single capture_* port; gate on the pactl source listing + the
    port witness. On a partial enumeration the module is removed
    through the sink_name-verified unload (its args carry sink_name= —
    media.class is a separate arg)."""
    leaf = {"field": "sink_name", "value": name,
            "media_class": "Audio/Source"}
    try:
        proc = subprocess.run(
            ["pactl", "load-module", "module-null-sink",
             "sink_name=" + name, "media.class=Audio/Source"],
            capture_output=True, timeout=15)
        mid = proc.stdout.decode(errors="replace").strip()
        leaf["module_id"] = int(mid) if mid.isdigit() else None
        leaf["rc"] = proc.returncode
        leaf["error"] = proc.stderr.decode(
            errors="replace")[:160] or None
    except (subprocess.TimeoutExpired, OSError) as exc:
        leaf.update({"module_id": None, "rc": None,
                     "error": str(exc)[:160]})
        return leaf
    if leaf.get("module_id") is None:
        return leaf
    t0 = time.monotonic()
    seen = ports = False
    while time.monotonic() - t0 < PACTLMON_R85_LINK_WAIT_S:
        seen = name in (_playback_r78_source_names() or [])
        ports = bool(_playback_r78_output_ports(name))
        if seen and ports:
            break
        time.sleep(0.1)
    leaf["source_seen"] = seen
    leaf["capture_ports"] = ports
    leaf["waited_s"] = round(time.monotonic() - t0, 3)
    if not (seen and ports):
        leaf["error"] = "Audio/Source never enumerated — unloaded"
        _pactlmon_r85_unload_own(leaf["module_id"], "sink_name",
                                 name)
        leaf["module_id"] = None
    return leaf


def _pactlmon_r85_play(tag, target, tone, role=None):
    """pw-play the tag tone into `target` (probe-owned names only — the
    fail-closed convention). Tagged by node.name AND application.name;
    role defaults to the family's private restore key."""
    argv = ["pw-play", "-P", f"node.name={tag}",
            "-P", f"application.name={tag}",
            "-P", f"media.role={role or PACTLMON_R85_ROLE}",
            "--target", target, str(tone)]
    return subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            stdin=subprocess.DEVNULL,
                            start_new_session=True)


def _pactlmon_r85_tone(path, seconds, lhz, rhz, amp=PACTLMON_R85_AMP,
                       invert_both=False):
    """Stereo s16 48 kHz tone: L=lhz / R=rhz at `amp`; invert_both flips
    both channels (the phase-inverted duplicate for the cancellation
    realization leg)."""
    n = int(48000 * seconds)
    t = np.arange(n) / 48000
    sgn = -1.0 if invert_both else 1.0
    left = (sgn * amp * np.sin(2 * np.pi * lhz * t)).astype("<i2")
    right = (sgn * amp * np.sin(2 * np.pi * rhz * t)).astype("<i2")
    pcm = np.empty(n * 2, dtype="<i2")
    pcm[0::2], pcm[1::2] = left, right
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(pcm.tobytes())


def _pactlmon_r85_killpg(proc, sig=signal.SIGKILL):
    _alsapw_r84_killpg(proc, sig)


def _pactlmon_r85_wait_node(name, timeout_s=PACTLMON_R85_LINK_WAIT_S):
    """Poll pw-dump until node.name == `name` exists."""
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout_s:
        g = _pactlmon_r85_graph()
        if _pactlmon_r85_node(g, name):
            return True, round(time.monotonic() - t0, 3)
        time.sleep(0.12)
    return False, round(time.monotonic() - t0, 3)


def _pactlmon_r85_wait_tap_link(sink, tap_tag,
                                timeout_s=PACTLMON_R85_TAP_WAIT_S):
    """The boundary's mandated tap validation: poll the graph until the
    monitor tap's links `<sink>:monitor_* -> <tap_tag>:input_*` exist —
    an unvalidated tap is the r85b silence/1-of-8 hazard. Returns
    (edges, waited_s)."""
    t0 = time.monotonic()
    last = []
    while time.monotonic() - t0 < timeout_s:
        g = _pactlmon_r85_graph()
        last = _pactlmon_r85_edges_in(g, tap_tag)
        if last and all(
                (e.get("out_port_name") or "").startswith("monitor_")
                for e in last):
            return last, round(time.monotonic() - t0, 3)
        time.sleep(0.12)
    return last, round(time.monotonic() - t0, 3)


def _pactlmon_r85_amps(path, freqs, win_s=0.25, skip_s=0.35):
    """Per-window spectral census of a tap wav: frame-peak, clipped-FRAME
    fraction (any channel |x|>=32767), and the Hann-DTFT amplitude of
    each `freqs` tag on each channel — the linear-sum/zero-bleed/clip
    witness."""
    insp, pcm = _alsapw_r84_pcm(path)
    out = {"exists": insp.get("exists"), "bytes": insp.get("bytes"),
           "freqs": {k: v for k, v in freqs.items()}, "windows": []}
    if pcm is None:
        out["unsupported"] = "no s16 stereo data chunk"
        return out
    rate = (insp.get("fmt") or {}).get("rate") or 48000
    n = int(rate * win_s)
    for i in range(int(rate * skip_s), len(pcm) - n + 1, n):
        seg = pcm[i:i + n].astype(np.int32)
        rail = int((((np.abs(seg[:, 0]) >= 32767) |
                     (np.abs(seg[:, 1]) >= 32767))).sum())
        row = {"at_s": round(i / rate, 2),
               "peak": int(np.abs(seg).max()),
               "rail_frames": rail,
               "rail_frac": round(rail / len(seg), 4)}
        for tag, f in freqs.items():
            row[f"l_{tag}"] = round(
                _pwcat_r83_amp_at(seg[:, 0], rate, f), 1)
            row[f"r_{tag}"] = round(
                _pwcat_r83_amp_at(seg[:, 1], rate, f), 1)
        out["windows"].append(row)
    return out


def _pactlmon_r85_med(windows, key, lo=None, hi=None):
    """Median of `key` across settled windows (optionally [lo,hi] s)."""
    vals = [w[key] for w in windows if key in w and
            (lo is None or w["at_s"] >= lo) and
            (hi is None or w["at_s"] <= hi)]
    return float(np.median(vals)) if vals else None


def _pactlmon_r85_tapped_mix(name, ctx, players, dur_s=4.6,
                             settle_s=0.5):
    """Monitor tap on ctx['mix'] FIRST, link-validated (the §2.1 hazard
    protocol), then the players [(offset_s, tone_path)] into the same
    sink; SIGTERM the tap + SIGKILL players at dur_s. Returns the leg:
    tap links + the spectral windows."""
    tag = f"{PACTLMON_R85_PREFIX}_{name}"
    tapf = Path(ctx["tmp"]) / f"{name}_tap.wav"
    frames = int(48000 * (dur_s + 1.2))
    tap = _playback_r78_tap(ctx["mix"], tapf, frames, f"{tag}_tap")
    t0 = time.monotonic()
    edges, waited = _pactlmon_r85_wait_tap_link(ctx["mix"],
                                              f"{tag}_tap")
    leg = {"name": name, "tag": tag, "tap_link": edges,
           "tap_link_wait_s": waited, "tap_target": ctx["mix"],
           "dur_s": dur_s}
    procs = []
    for off, tone in players:
        left = off - (time.monotonic() - t0)
        if left > 0:
            time.sleep(left)
        procs.append(_pactlmon_r85_play(
            f"{tag}_p{len(procs)}", ctx["mix"], tone))
    time.sleep(settle_s)
    g = _pactlmon_r85_graph()
    leg["mix_edges"] = [e for e in _pactlmon_r85_edges_in(g, ctx["mix"])
                        if (e.get("in_port_name") or "")
                        .startswith("playback_")]
    left = dur_s - (time.monotonic() - t0)
    if left > 0:
        time.sleep(left)
    if tap.poll() is None:
        _pactlmon_r85_killpg(tap, signal.SIGTERM)
    try:
        tap.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        _pactlmon_r85_killpg(tap)
        tap.wait()
    for p in procs:
        if p.poll() is None:
            _pactlmon_r85_killpg(p)
        p.wait()
    leg["tap_exit"] = tap.returncode
    leg["player_exits"] = [p.returncode for p in procs]
    leg["tap_stderr_tail"] = _capture_tail(
        tap.stderr.read().decode(errors="replace"), str(tapf))
    return leg, tapf


def _pactlmon_r85_cap_leg(name, ctx, target, prop=False, dur_s=4.6,
                          loss_at=None, loss_field=None, loss_value=None,
                          late_at=None, late_master=None, late_name=None,
                          link_samples=(0.8,), out_name=None):
    """One tagged pw-record with timed link/file witnesses, an optional
    name-verified module unload at `loss_at`, and an optional
    mid-stall remap-source load at `late_at` (the late-bind leg). Links
    are the record stream's input edges; `realization` names the loss
    shape WITHOUT arming it (the froze-vs-zeros switch is bimodal)."""
    tag = f"{PACTLMON_R85_PREFIX}_{name}"
    out = Path(ctx["tmp"]) / (out_name or f"{name}.wav")
    argv = ["pw-record", "-P", f"node.name={tag}"]
    if prop:
        argv += ["-P", "stream.capture.sink=true"]
    argv += ["--target", str(target), "--rate", "48000",
             "--channels", "2", "--format", "s16", str(out)]
    try:
        proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.DEVNULL,
                                start_new_session=True)
    except OSError as exc:
        return {"name": name, "argv": " ".join(argv),
                "spawn_error": str(exc)[:160]}
    t0 = time.monotonic()
    leg = {"name": name, "tag": tag, "argv": " ".join(argv),
           "target": str(target), "prop": prop}
    events = sorted([(s, "sample") for s in link_samples] +
                    ([(loss_at, "unload")] if loss_at is not None
                     else []) +
                    ([(late_at, "late_load")] if late_at is not None
                     else []))
    size_at_loss = None
    samples = []
    for at, kind in events:
        left = at - (time.monotonic() - t0)
        if left > 0:
            time.sleep(left)
        if kind == "sample":
            g = _pactlmon_r85_graph()
            samples.append(
                {"at_s": round(time.monotonic() - t0, 2),
                 "links": _pactlmon_r85_edges_in(g, tag),
                 "size": out.stat().st_size if out.exists() else None,
                 "node_alive": _pactlmon_r85_node(g, tag) is not None})
        elif kind == "late_load":
            leg["late_load"] = _pactlmon_r85_remap_load(
                late_master, late_name)
            leg["late_load"]["at_s"] = round(
                time.monotonic() - t0, 3)
        else:
            size_at_loss = (out.stat().st_size if out.exists()
                            else None)
            leg["unloaded"] = _pactlmon_r85_unload_own(
                None, loss_field, loss_value)
            leg["unloaded"]["at_s"] = round(time.monotonic() - t0, 3)
    left = dur_s - (time.monotonic() - t0)
    if left > 0:
        time.sleep(left)
    leg["alive_at_end"] = proc.poll() is None
    if proc.poll() is None:
        _pactlmon_r85_killpg(proc, signal.SIGTERM)
    try:
        proc.wait(timeout=4.0)
    except subprocess.TimeoutExpired:
        _pactlmon_r85_killpg(proc)
        proc.wait()
        leg["sigkill"] = True
    err = proc.stderr.read().decode(errors="replace")
    cls, hit = _pactlmon_r85_errclass(err)
    leg.update({"samples": samples, "size_at_loss": size_at_loss,
                "exit_code": proc.returncode,
                "signal": (signal.Signals(-proc.returncode).name
                           if (proc.returncode or 0) < 0 else None),
                "stderr_tail": _capture_tail(err, str(out)),
                "error_class": cls, "file": str(out)})
    return leg


def _pactlmon_r85_post_stats(path, loss_size):
    """The falsification-15-safe verdict on a post-loss capture: bytes
    appended after `loss_size` must be ABSENT (froze realization) or
    ALL-ZERO (grew-with-zeros); a nonzero post-loss sample is new
    content. `realization` names the shape — recorded, never armed."""
    insp, pcm = _alsapw_r84_pcm(path)
    out = {"exists": insp.get("exists"), "bytes": insp.get("bytes"),
           "loss_bytes": loss_size}
    if pcm is None:
        out["unsupported"] = "no s16 stereo data chunk"
        return out
    data_off = 44
    for c in insp.get("chunks") or []:
        if c["id"] == "data":
            data_off = c["offset"] + 8
    loss_frame = None
    if loss_size is not None and loss_size > data_off:
        loss_frame = (loss_size - data_off) // 4
    if loss_frame is None or loss_frame >= len(pcm):
        out.update({"post_frames": 0, "post_peak": 0,
                    "post_nonzero": 0, "realization": "froze"})
        return out
    post = pcm[int(loss_frame):].astype(np.int32)
    peak = int(np.abs(post).max()) if len(post) else 0
    nz = int(np.any(post != 0, axis=1).sum())
    out.update({"post_frames": int(len(post)), "post_peak": peak,
                "post_nonzero": nz,
                "realization": ("grew_zeros" if peak == 0 else
                                "grew_content")})
    return out


def _pactlmon_r85_sd_leg(name, ctx, sd, client_argv, dur_s=2.6):
    """Audio/Source self-destruct witness: `client_argv` spawns against
    the loaded `sd` null-sink; module + source absence are polled on a
    ~60 ms grid; the file stays a 44-B stub when no link forms."""
    tag = f"{PACTLMON_R85_PREFIX}_{name}"
    argv = [a if a != "<SD>" else sd for a in client_argv]
    argv = [a if a != "<TAG>" else tag for a in argv]
    leg = {"name": name, "tag": tag, "argv": " ".join(argv)}
    try:
        proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.DEVNULL,
                                start_new_session=True)
    except OSError as exc:
        leg["spawn_error"] = str(exc)[:160]
        return leg
    t0 = time.monotonic()
    grid, mod_dead = [], None
    src_dead = None
    while time.monotonic() - t0 < dur_s:
        mod_alive = _pactlmon_r85_module_index("sink_name", sd) \
            is not None
        src_alive = sd in (_playback_r78_source_names() or [])
        grid.append({"at_s": round(time.monotonic() - t0, 2),
                     "module": bool(mod_alive), "source": src_alive})
        if mod_dead is None and not mod_alive:
            mod_dead = grid[-1]["at_s"]
        if src_dead is None and not src_alive:
            src_dead = grid[-1]["at_s"]
        time.sleep(0.06)
    leg["grid"] = grid
    leg["module_dead_at_s"] = mod_dead
    leg["source_dead_at_s"] = src_dead
    g = _pactlmon_r85_graph()
    leg["links"] = _pactlmon_r85_edges_in(g, tag)
    leg["alive_at_end"] = proc.poll() is None
    if proc.poll() is None:
        _pactlmon_r85_killpg(proc, signal.SIGTERM)
    try:
        proc.wait(timeout=4.0)
    except subprocess.TimeoutExpired:
        _pactlmon_r85_killpg(proc)
        proc.wait()
    err = proc.stderr.read().decode(errors="replace")
    cls, hit = _pactlmon_r85_errclass(err)
    leg.update({"exit_code": proc.returncode,
                "signal": (signal.Signals(-proc.returncode).name
                           if (proc.returncode or 0) < 0 else None),
                "stderr_tail": _capture_tail(err, tag),
                "error_class": cls})
    return leg


def _pactlmon_r85_family_lock():
    """Same-family exclusion — two concurrent pactlmon runs would
    cross-credit monitor taps and contest the collision/cycle sinks, so
    a second --probe-pactlmon-r85 waits HERE (the r82 convention)."""
    path = Path(tempfile.gettempdir()) / \
        "measure_audio-pactlmon-r85.lock"
    try:
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    except OSError:
        return None
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        os.ftruncate(fd, 0)
        os.write(fd, f"pid={PACTLMON_R85_PID} ns={PACTLMON_R85_NS} "
                     f"role={PACTLMON_R85_ROLE}\n".encode())
    except OSError:
        pass
    return fd


def _pactlmon_r85_entry_head(probe):
    """Shared entry preamble: contention census, oracle, inventory."""
    inv = _capture_inventory()
    return {"probe": probe,
            "contention": _playback_r78_foreign_clients(),
            "oracle_at_start": _loopback_r79_oracle(),
            "inventory": {"default_sink": inv["default_sink"],
                          "default_source": inv["default_source"],
                          "sources_count": len(inv["sources"]),
                          "monitors_count": len(inv["monitors"]),
                          "alsa_capture_devices":
                          inv["alsa_capture_devices"]},
            "loadavg": _pactlmon_r85_loadavg()}


def _pactlmon_r85_teardown(entry, failures, loads):
    """Every own module unloaded by the name-verified index (each load
    record carries its OWN field name — sink_name or source_name), then
    the witnesses: sinks gone from pactl, sources gone from pactl, and
    no r85a_<pid>-tagged node survives."""
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
        sink_names = [t for t, l in (loads or {}).items()
                      if (l or {}).get("field", "sink_name") ==
                      "sink_name"]
        gone = {nm: nm not in sinks_now for nm in sink_names}
        entry["sinks_gone"] = gone
        if not all(gone.values()):
            failures.append(
                "teardown: probe sinks survived unload: "
                f"{[n for n, g in gone.items() if not g]}")
    srcs_now = _playback_r78_source_names()
    if srcs_now is None:
        entry["sources_gone"] = "reader_error"
        entry.setdefault("coverage_blocked", []).append(
            "teardown: pactl source reader failed — sources_gone "
            "unmeasured")
    else:
        src_names = [t for t, l in (loads or {}).items()
                     if (l or {}).get("field") == "source_name"]
        sgone = {nm: nm not in srcs_now for nm in src_names}
        entry["sources_gone"] = sgone
        if not all(sgone.values()):
            failures.append(
                "teardown: probe sources survived unload: "
                f"{[n for n, g in sgone.items() if not g]}")
    names = _playback_r78_node_names()
    if names is None:
        entry["own_nodes_after"] = "reader_error"
        entry.setdefault("coverage_blocked", []).append(
            "teardown: node reader failed — own_nodes_after "
            "unmeasured")
    else:
        rest = sorted(n for n in names
                      if PACTLMON_R85_PREFIX in n
                      or n in (loads or {}))
        entry["own_nodes_after"] = rest
        if rest:
            failures.append(
                f"teardown: r85a-tagged nodes survived: {rest}")


def _pactlmon_r85_block(entry, failures, msg, loads=None):
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


def _pactlmon_r85_vol_pct(rec):
    """First front-* `N%` on a pactl volume row's stdout."""
    m = re.search(r"(\d+)\s*%", (rec or {}).get("stdout") or "")
    return int(m.group(1)) if m else None


def pactlmon_addr_r85_entry():
    """The pactl/pw-cli verb-arg equivalence lattice on two probe-owned
    sinks — serial-vs-id classes, typed @DEFAULT_* args, the `0`=live-
    default resolution, numeric parse edges (leading-zero row recorded,
    never armed), move-sink-input name/serial/bogus, the name/serial
    collision law, and serial monotonicity vs module-index recycle."""
    failures, legs = [], {}
    entry = _pactlmon_r85_entry_head(
        "r85a pactl/pw-cli addressing lattice + collision + serial "
        "monotonicity")
    tools = {t: shutil.which(t) for t in
             ("pactl", "pw-cli", "pw-dump", "pw-play", "pw-record")}
    entry["tools"] = tools
    if not all(tools.values()):
        return _pactlmon_r85_block(
            entry, failures,
            f"missing tools: {[t for t, p in tools.items() if not p]}")
    loads = {}
    try:
        loads[PACTLMON_R85_NS] = _pwcat_r83_ns_load(PACTLMON_R85_NS)
        loads[PACTLMON_R85_NS2] = _pwcat_r83_ns_load(PACTLMON_R85_NS2)
        loads[PACTLMON_R85_NS]["field"] = "sink_name"
        loads[PACTLMON_R85_NS]["value"] = PACTLMON_R85_NS
        loads[PACTLMON_R85_NS2]["field"] = "sink_name"
        loads[PACTLMON_R85_NS2]["value"] = PACTLMON_R85_NS2
        if loads[PACTLMON_R85_NS].get("module_id") is None or \
                loads[PACTLMON_R85_NS2].get("module_id") is None:
            return _pactlmon_r85_block(
                entry, failures, "probe null sinks never enumerated",
                loads)
        g0 = _pactlmon_r85_graph()
        na = _pactlmon_r85_node(g0, PACTLMON_R85_NS) or {}
        nb = _pactlmon_r85_node(g0, PACTLMON_R85_NS2) or {}
        ser_a, oid_a = na.get("object_serial"), na.get("node_id")
        ser_b = nb.get("object_serial")
        entry["ns_props"] = {"object_serial": ser_a,
                             "object_id_prop": na.get("object_id"),
                             "node_id": na.get("node_id"),
                             "media_class": na.get("media_class")}
        entry["ns2_serial"] = ser_b
        def_sink = _alsapw_r84_default("sink")
        def_src = _alsapw_r84_default("source")
        entry["defaults"] = {"sink": def_sink, "source": def_src}
        ns_idx = (_alsapw_r84_sink_leaf(PACTLMON_R85_NS) or {}).get(
            "index")
        ns2_idx = (_alsapw_r84_sink_leaf(PACTLMON_R85_NS2) or {}).get(
            "index")
        entry["sink_index"] = {"ns": ns_idx, "ns2": ns2_idx}
        if ser_a is None or ser_b is None or ns_idx is None:
            return _pactlmon_r85_block(
                entry, failures,
                "probe sink serials/indices never resolved", loads)
        with tempfile.TemporaryDirectory(prefix="r85a-addr-") as tmp:
            tone = Path(tmp) / "r85a_tag.wav"
            _playback_r78_write_tone(tone, 6.0)
            ctx = {"tmp": tmp, "tone": tone, "ns": PACTLMON_R85_NS,
                   "ns2": PACTLMON_R85_NS2}
            try:
                # -------- get-sink-volume equivalence class --------
                def gsv(arg, label):
                    return _pactlmon_r85_pactl(
                        "get-sink-volume", arg)
                legs["g_name"] = gsv(PACTLMON_R85_NS, "name")
                legs["g_serial"] = gsv(str(ser_a), "serial")
                legs["g_objid"] = gsv(str(oid_a), "object.id")
                legs["g_defsink"] = gsv("@DEFAULT_SINK@", "defsink")
                legs["g_defsrc"] = gsv("@DEFAULT_SOURCE@", "defsrc")
                legs["g_defmon"] = gsv("@DEFAULT_MONITOR@", "defmon")
                legs["g_monitor_as_sink"] = gsv(
                    f"{PACTLMON_R85_NS}.monitor", "monitor_as_sink")
                legs["g_bogus"] = gsv(PACTLMON_R85_BOGUS, "bogus")
                legs["g_huge"] = gsv("99999999", "huge")
                legs["g_neg"] = gsv("-1", "neg")
                legs["g_empty"] = gsv("", "empty")
                legs["g_zero"] = gsv("0", "zero")
                legs["g_leadspace"] = gsv(f" {ser_a}", "leadspace")
                legs["g_plus"] = gsv(f"+{ser_a}", "plus")
                legs["g_float"] = gsv(f"{ser_a}.0", "float")
                legs["g_xsuf"] = gsv(f"{ser_a}x", "xsuf")
                legs["g_hex"] = gsv(f"0x{ser_a:X}", "hex")
                s = str(ser_a)
                legs["g_uscr"] = gsv(f"{s[:-3]}_{s[-3:]}", "uscr")
                # boundary-bimodal row — RECORDED ONLY, never armed
                legs["g_lead0"] = gsv(f"0{s}", "lead0")
                legs["g_defsinkX"] = gsv("@DEFAULT_SINK@X", "defsinkX")
                # -------- get-source-volume equivalence class --------
                def gsvo(arg):
                    return _pactlmon_r85_pactl(
                        "get-source-volume", arg)
                legs["s_monitor_name"] = gsvo(
                    f"{PACTLMON_R85_NS}.monitor")
                legs["s_sink_serial"] = gsvo(str(ser_a))
                legs["s_defmon"] = gsvo("@DEFAULT_MONITOR@")
                legs["s_defsrc"] = gsvo("@DEFAULT_SOURCE@")
                legs["s_sinkname"] = gsvo(PACTLMON_R85_NS)
                legs["s_defsink"] = gsvo("@DEFAULT_SINK@")
                legs["s_bogus"] = gsvo(PACTLMON_R85_BOGUS)
                legs["s_zero"] = gsvo("0")
                # -------- pw-cli namespace inversion --------
                legs["pwcli_id"] = _pactlmon_r85_run(
                    ["pw-cli", "info", str(oid_a)], 10.0)
                legs["pwcli_serial"] = _pactlmon_r85_run(
                    ["pw-cli", "info", str(ser_a)], 10.0)
                # -------- move-sink-input name/serial/bogus --------
                tag = f"{PACTLMON_R85_PREFIX}_mv"
                pa = _pactlmon_r85_play(tag, PACTLMON_R85_NS, tone)
                ia, wa = _alsapw_r84_wait_attached(tag)
                legs["mv_spawn"] = {"tag": tag, "stream": ia,
                                    "wait_s": wa}
                if ia is not None:
                    w1 = _pactlmon_r85_pactl(
                        "move-sink-input", ia["index"],
                        PACTLMON_R85_NS2)
                    after1 = _alsapw_r84_wait_moved(tag, ia["sink"])
                    legs["mv_name"] = {"pactl": w1, "after": after1}
                    cur = (after1 or {}).get("sink")
                    w2 = _pactlmon_r85_pactl(
                        "move-sink-input", ia["index"], str(ser_a))
                    after2 = _alsapw_r84_wait_moved(tag, cur)
                    legs["mv_serial"] = {"pactl": w2, "after": after2}
                    cur = (after2 or {}).get("sink")
                    w3 = _pactlmon_r85_pactl(
                        "move-sink-input", ia["index"],
                        PACTLMON_R85_BOGUS)
                    after3 = _alsapw_r84_wait_moved(tag, cur,
                                                    timeout_s=1.2)
                    legs["mv_bogus"] = {"pactl": w3, "after": after3}
                    # -------- name/serial collision (boundary) --------
                    # a sink literally NAMED <ser_a> — pactl's numeric
                    # arg still means object.serial, never node.name.
                    digits = str(ser_a)
                    dup = _pwcat_r83_ns_load(digits)
                    loads[digits] = dict(dup, field="sink_name",
                                         value=digits)
                    legs["cdup_load"] = {"module_id": dup.get(
                        "module_id"), "named": digits}
                    if dup.get("module_id") is not None:
                        w4 = _pactlmon_r85_pactl(
                            "move-sink-input", ia["index"], digits)
                        after4 = _alsapw_r84_wait_moved(
                            tag, (after3 or {}).get("sink"))
                        legs["cdup_move"] = {"pactl": w4,
                                             "after": after4}
                        # pw-cat side: the digits resolve as a NAME
                        # first — a sink, unusable noprop; never a
                        # monitor link (stall/refusal recorded).
                        cl = _pactlmon_r85_cap_leg(
                            "cdup_cap", ctx, digits, dur_s=2.6,
                            link_samples=(1.0, 2.0))
                        legs["cdup_cap"] = cl
                    _pactlmon_r85_killpg(pa)
                    pa.wait()
                # -------- serial monotonicity vs index recycle --------
                serials, mods = [], []
                for rep in range(3):
                    leaf = _pwcat_r83_ns_load(PACTLMON_R85_CYC)
                    mid = leaf.get("module_id")
                    gg = _pactlmon_r85_graph()
                    nn = _pactlmon_r85_node(gg, PACTLMON_R85_CYC) or {}
                    serials.append(nn.get("object_serial"))
                    mods.append(mid)
                    legs[f"cyc_{rep}"] = {"module_id": mid,
                                          "serial": nn.get(
                                              "object_serial")}
                    _pactlmon_r85_unload_own(
                        mid, "sink_name", PACTLMON_R85_CYC)
                entry["serial_cycles"] = {"serials": serials,
                                          "module_indices": mods}
            finally:
                entry["legs"] = legs
            # ---------------- verdicts ----------------
            def noent(name):
                l = legs[name]
                if l.get("exit_code") != 1 or \
                        l.get("error_class") != "pa_get_info_noent":
                    failures.append(
                        f"{name}: rc={l.get('exit_code')} class="
                        f"{l.get('error_class')} — the "
                        "not-a-sink-arg refusal fails")
            for nm in ("g_name", "g_serial", "g_defsink",
                       "g_leadspace", "g_plus", "g_float", "g_xsuf",
                       "g_hex"):
                l = legs[nm]
                if l.get("exit_code") != 0 or \
                        "Volume:" not in (l.get("stdout") or ""):
                    failures.append(
                        f"{nm}: rc={l.get('exit_code')} — the "
                        "sink-arg resolution fails")
            if _pactlmon_r85_vol_pct(legs["g_serial"]) != \
                    _pactlmon_r85_vol_pct(legs["g_name"]):
                failures.append(
                    "g_serial: serial row != name row — the "
                    "serial-is-the-number law fails")
            for nm in ("g_objid", "g_defsrc", "g_defmon",
                       "g_monitor_as_sink", "g_bogus", "g_huge",
                       "g_neg", "g_uscr", "g_defsinkX"):
                noent(nm)
            l = legs["g_empty"]
            if l.get("exit_code") != 1 or \
                    l.get("error_class") != "pa_invalid_arg":
                failures.append(
                    f"g_empty: rc={l.get('exit_code')} class="
                    f"{l.get('error_class')} — the Invalid-argument "
                    "class fails")
            l = legs["g_zero"]
            if l.get("exit_code") != 0 or \
                    _pactlmon_r85_vol_pct(l) != _pactlmon_r85_vol_pct(
                        legs["g_defsink"]):
                failures.append(
                    f"g_zero: rc={l.get('exit_code')} pct="
                    f"{_pactlmon_r85_vol_pct(l)} — the 0=live-default "
                    "arm fails")
            legs["g_lead0"]["armed"] = False   # bimodal — data only
            for nm in ("s_monitor_name", "s_sink_serial", "s_defmon",
                       "s_defsrc", "s_zero"):
                l = legs[nm]
                if l.get("exit_code") != 0 or \
                        "Volume:" not in (l.get("stdout") or ""):
                    failures.append(
                        f"{nm}: rc={l.get('exit_code')} — the "
                        "source-arg resolution fails")
            if _pactlmon_r85_vol_pct(legs["s_sink_serial"]) != \
                    _pactlmon_r85_vol_pct(legs["s_monitor_name"]):
                failures.append(
                    "s_sink_serial: monitor source did not share "
                    "the sink's serial")
            for nm in ("s_sinkname", "s_defsink", "s_bogus"):
                l = legs[nm]
                if l.get("exit_code") != 1 or \
                        l.get("error_class") != "pa_get_info_noent":
                    failures.append(
                        f"{nm}: rc={l.get('exit_code')} class="
                        f"{l.get('error_class')} — source-verb sink "
                        "refusal fails")
            l = legs["pwcli_id"]
            if l.get("exit_code") != 0 or str(oid_a) not in \
                    (l.get("stdout") or ""):
                failures.append(
                    f"pwcli_id: rc={l.get('exit_code')} — object.id "
                    "did not resolve on pw-cli")
            l = legs["pwcli_serial"]
            blob = (l.get("stderr") or "") + (l.get("stdout") or "")
            if l.get("exit_code") != 0 or \
                    "unknown global" not in blob:
                failures.append(
                    f"pwcli_serial: rc={l.get('exit_code')} — the "
                    "rc-0 unknown-global shape fails")
            if ia is not None:
                ns2_idx = entry["sink_index"]["ns2"]
                ns_idx = entry["sink_index"]["ns"]
                a1 = (legs.get("mv_name") or {}).get("after") or {}
                if (legs["mv_name"]["pactl"].get("exit_code") != 0
                        or a1.get("sink") != ns2_idx):
                    failures.append(
                        f"mv_name: sink={(a1 or {}).get('sink')} != "
                        f"ns2 {ns2_idx} — move-by-name fails")
                a2 = (legs.get("mv_serial") or {}).get("after") or {}
                if (legs["mv_serial"]["pactl"].get("exit_code") != 0
                        or a2.get("sink") != ns_idx):
                    failures.append(
                        f"mv_serial: sink={(a2 or {}).get('sink')} "
                        f"!= ns {ns_idx} — move-by-serial fails")
                l3 = legs.get("mv_bogus") or {}
                if l3.get("pactl", {}).get("exit_code") == 0 or \
                        (l3.get("after") or {}).get("sink") != \
                        (a2 or {}).get("sink"):
                    failures.append(
                        "mv_bogus: bogus move did not refuse-and-"
                        "stay")
                cm = legs.get("cdup_move")
                if cm is not None:
                    a4 = cm.get("after") or {}
                    if cm["pactl"].get("exit_code") != 0 or \
                            a4.get("sink") != ns_idx:
                        failures.append(
                            f"cdup_move: sink={(a4 or {}).get('sink')}"
                            f" != serial-holder ns {ns_idx} — the "
                            "collision law fails")
                cl = legs.get("cdup_cap") or {}
                cl_links = [e for s in cl.get("samples", [])
                            for e in s.get("links", [])]
                mon = [e for e in cl_links
                       if (e.get("out_port_name") or "")
                       .startswith("monitor_")]
                # BOTH resolution orders were measured: the boundary's
                # host resolved the digits as a NAME first (the sink —
                # never a monitor link); this authoring host resolves
                # them as the SERIAL (the t_sinkserial noprop monitor
                # bypass). The surviving invariant: any monitor link
                # must land on the SERIAL HOLDER's monitor — the
                # digits never resolve a foreign target.
                if mon and all(e.get("out_node") == PACTLMON_R85_NS
                               for e in mon):
                    cl["realization"] = "serial_monitor_bypass"
                elif mon:
                    cl["realization"] = "foreign_monitor"
                elif cl_links:
                    cl["realization"] = "name_shadow_bound"
                elif cl.get("exit_code") == 1 and \
                        not cl.get("alive_at_end"):
                    cl["realization"] = "refused"
                elif cl.get("alive_at_end"):
                    cl["realization"] = "stalled"
                else:
                    cl["realization"] = "other"
                if cl["realization"] in ("foreign_monitor", "other"):
                    failures.append(
                        f"cdup_cap: monitor-links={len(mon)} "
                        f"realization={cl['realization']} — the "
                        "digits-resolution lattice fails")
            sers = [s for s in
                    entry["serial_cycles"]["serials"] if s is not None]
            if len(serials) != 3 or len(serials) != len(set(serials)) \
                    or serials != sorted(serials):
                failures.append(
                    f"cyc: serials={serials} — serial monotonicity "
                    "(never recycled) fails")
    finally:
        _pactlmon_r85_teardown(entry, failures, loads)
    entry["failures"] = failures
    return entry


def pactlmon_mix_r85_entry():
    """N streams on one probe-owned sink — the monitor-tap linear-sum
    laws with the boundary's NEW-HAZARD protocol folded in: the tap is
    link-validated BEFORE any player starts and the solo reference is
    measured inside the same entry (a bare amplitude arm can read 0 or
    exactly 1/8 on this host)."""
    failures, legs = [], {}
    entry = _pactlmon_r85_entry_head(
        "r85a N-streams-one-sink mixing — link-validated taps + solo "
        "reference")
    tools = {t: shutil.which(t) for t in
             ("pw-play", "pw-record", "pw-dump", "pactl")}
    entry["tools"] = tools
    if not all(tools.values()):
        return _pactlmon_r85_block(
            entry, failures,
            f"missing tools: {[t for t, p in tools.items() if not p]}")
    loads = {}
    try:
        loads[PACTLMON_R85_MIX] = _pwcat_r83_ns_load(PACTLMON_R85_MIX)
        loads[PACTLMON_R85_MIX]["field"] = "sink_name"
        loads[PACTLMON_R85_MIX]["value"] = PACTLMON_R85_MIX
        if loads[PACTLMON_R85_MIX].get("module_id") is None:
            return _pactlmon_r85_block(
                entry, failures, "probe mix sink never enumerated",
                loads)
        lhz, rhz = (PLAYBACK_R78_TONE_L_HZ, PLAYBACK_R78_TONE_R_HZ)
        f3, f4 = PACTLMON_R85_F3, PACTLMON_R85_F4
        freqs = {"a": lhz, "b": rhz, "c": f3, "d": f4}
        with tempfile.TemporaryDirectory(prefix="r85a-mix-") as tmp:
            ta = Path(tmp) / "r85a_tagA.wav"
            tb = Path(tmp) / "r85a_tagB.wav"
            tinv = Path(tmp) / "r85a_tagInv.wav"
            th1 = Path(tmp) / "r85a_hot1.wav"
            th3 = Path(tmp) / "r85a_hot3.wav"
            _pactlmon_r85_tone(ta, 6.5, lhz, rhz)
            _pactlmon_r85_tone(tb, 6.5, f3, f4)
            _pactlmon_r85_tone(tinv, 6.5, lhz, lhz, invert_both=True)
            tmono = Path(tmp) / "r85a_tagMono.wav"
            _pactlmon_r85_tone(tmono, 6.5, lhz, lhz)
            _pactlmon_r85_tone(th1, 6.5, lhz, lhz,
                               amp=PACTLMON_R85_CLIP_AMP)
            _pactlmon_r85_tone(th3, 6.5, f3, f3,
                               amp=PACTLMON_R85_CLIP_AMP)
            ctx = {"tmp": tmp, "mix": PACTLMON_R85_MIX}
            try:
                # the §2.1 protocol: tap-link validation is inside
                # _pactlmon_r85_tapped_mix; `solo` IS the same-run
                # amplitude reference every other leg is judged
                # against.
                legs["solo"], solo_f = _pactlmon_r85_tapped_mix(
                    "solo", ctx, [(0.25, ta)], dur_s=4.2)
                legs["mix2"], mix2_f = _pactlmon_r85_tapped_mix(
                    "mix2", ctx, [(0.25, ta), (0.35, tb)], dur_s=4.6)
                # the same file twice: the coherent-2x sum requires
                # sample-aligned starts — a realization the boundary
                # measured 6/6 but which slips under negotiation-
                # quantum jitter (this authoring pass measured 0.76x
                # and ~0 on two realizations). Spawn back-to-back,
                # record the ratio, arm only the LINEAR bound — the
                # sum of two equal-amp coherent waves can never
                # exceed 2x.
                legs["mixdup"], dup_f = _pactlmon_r85_tapped_mix(
                    "mixdup", ctx, [(0.25, ta), (0.25, ta)],
                    dur_s=4.6)
                legs["mixdelay"], dly_f = _pactlmon_r85_tapped_mix(
                    "mixdelay", ctx, [(0.25, ta), (0.75, ta)],
                    dur_s=5.0)
                legs["mixinv"], inv_f = _pactlmon_r85_tapped_mix(
                    "mixinv", ctx, [(0.25, tmono), (0.35, tinv)],
                    dur_s=4.6)
                legs["mixclip"], clip_f = _pactlmon_r85_tapped_mix(
                    "mixclip", ctx, [(0.25, th1), (0.35, th3)],
                    dur_s=4.6)
            finally:
                entry["legs"] = legs
            # ---------------- verdicts ----------------
            lo, hi = PACTLMON_R85_SOLO_ENV
            amp = PACTLMON_R85_AMP
            def tap_ok(nm):
                l = legs[nm]
                edges = l.get("tap_link") or []
                if not edges:
                    failures.append(
                        f"{nm}: tap never linked — the arm is "
                        "unvalidated (r85b silence hazard)")
                    return False
                if not all((e.get("out_port_name") or "")
                           .startswith("monitor_") for e in edges):
                    failures.append(
                        f"{nm}: tap links land on non-monitor "
                        f"ports: {edges}")
                    return False
                return True
            for nm in ("solo", "mix2", "mixdup", "mixdelay",
                       "mixinv", "mixclip"):
                tap_ok(nm)
            # solo reference — full-amp both channels, zero bleed
            sa = _pactlmon_r85_amps(solo_f, freqs)
            legs["solo"]["amps"] = sa
            sw = sa.get("windows") or []
            la = _pactlmon_r85_med(sw, "l_a")
            rb = _pactlmon_r85_med(sw, "r_b")
            ra = _pactlmon_r85_med(sw, "r_a")
            lb = _pactlmon_r85_med(sw, "l_b")
            legs["solo"]["ref"] = {"l_a": la, "r_b": rb,
                                   "r_a_bleed": ra, "l_b_bleed": lb}
            if la is None or not (lo * amp <= la <= hi * amp) or \
                    rb is None or not (lo * amp <= rb <= hi * amp):
                failures.append(
                    f"solo: l_a={la} r_b={rb} — the solo reference "
                    f"is outside {PACTLMON_R85_SOLO_ENV}*8192 "
                    "(tap-gain hazard would poison every mix leg)")
            else:
                legs["solo_ref_ok"] = True
            if (ra or 0) > PACTLMON_R85_BLEED_MAX * amp or \
                    (lb or 0) > PACTLMON_R85_BLEED_MAX * amp:
                failures.append(
                    f"solo: bleed r_a={ra} l_b={lb} — the zero-bleed "
                    "arm fails at the reference")
            ref = None
            if la and rb:
                ref = min(la, rb)
            # mix2 — both tones full amplitude, zero bleed
            ma = _pactlmon_r85_amps(mix2_f, freqs)
            legs["mix2"]["amps"] = ma
            mw = ma.get("windows") or []
            for k in ("l_a", "r_b", "l_c", "r_d"):
                v = _pactlmon_r85_med(mw, k)
                legs["mix2"].setdefault("meds", {})[k] = v
                if ref and (v is None or
                            not (lo * ref <= v <= hi * ref)):
                    failures.append(
                        f"mix2: {k}={v} — the full-amplitude "
                        "preservation arm fails")
            for k in ("r_a", "l_b", "r_c", "l_d"):
                v = _pactlmon_r85_med(mw, k) or 0
                legs["mix2"].setdefault("bleed", {})[k] = v
                if ref and v > PACTLMON_R85_BLEED_MAX * ref:
                    failures.append(
                        f"mix2: bleed {k}={v} — zero-bleed fails")
            # topology: the players' links land on exactly the two
            # playback_* port objects (4 links -> 2 ports)
            ports_seen = {e.get("in") for e in
                          legs["mix2"].get("mix_edges") or []}
            outs_seen = {e.get("out") for e in
                         legs["mix2"].get("mix_edges") or []}
            if len(legs["mix2"].get("mix_edges") or []) != 4 or \
                    len(ports_seen) != 2 or \
                    not all(":playback_" in p for p in ports_seen):
                failures.append(
                    f"mix2 topology: edges="
                    f"{legs['mix2'].get('mix_edges')} — the "
                    "4-links-to-2-ports law fails")
            if len(outs_seen) < 4:
                failures.append(
                    f"mix2 topology: producer ports={outs_seen} — "
                    "expected 4 distinct stream output ports")
            # mixdup — the coherent-2x sum is a REALIZATION (phase-
            # aligned starts are quantum-boundary luck): the ratio is
            # classified, and the ARM is the linear bound — the sum
            # can never exceed 2.05x a single stream, and the mix
            # introduces no energy away from the tone frequencies
            # (mix2 already arms zero bleed).
            da = _pactlmon_r85_amps(dup_f, {"a": lhz, "b": rhz})
            legs["mixdup"]["amps"] = da
            dw = da.get("windows") or []
            dv = _pactlmon_r85_med(dw, "l_a")
            legs["mixdup"]["l_a_med"] = dv
            drat = (dv / ref) if ref and dv is not None else None
            legs["mixdup"]["dup_ratio"] = drat
            legs["mixdup"]["realization"] = (
                "coherent_2x" if drat is not None and
                PACTLMON_R85_DUP_ENV[0] <= drat <=
                PACTLMON_R85_DUP_ENV[1] else
                "cancelled" if drat is not None and drat < 0.12 else
                "partial" if drat is not None else "unmeasured")
            if drat is None or drat > 2.05:
                failures.append(
                    f"mixdup: ratio={drat} — the linear-sum bound "
                    "(<=2.05x) fails")
            # mixdelay — +0.5s duplicate: same bound on the overlap
            # windows (the phase relation is arbitrary by design).
            da = _pactlmon_r85_amps(dly_f, {"a": lhz})
            legs["mixdelay"]["amps"] = da
            dw = [w for w in (da.get("windows") or [])
                  if w["at_s"] >= 1.2]
            dv = _pactlmon_r85_med(dw, "l_a")
            legs["mixdelay"]["l_a_med_late"] = dv
            drat = (dv / ref) if ref and dv is not None else None
            legs["mixdelay"]["delay_ratio"] = drat
            legs["mixdelay"]["realization"] = (
                "coherent_2x" if drat is not None and
                PACTLMON_R85_DUP_ENV[0] <= drat <=
                PACTLMON_R85_DUP_ENV[1] else
                "cancelled" if drat is not None and drat < 0.12 else
                "partial" if drat is not None else "unmeasured")
            if drat is None or drat > 2.05:
                failures.append(
                    f"mixdelay: late ratio={drat} — the linear-sum "
                    "bound fails")
            # mixinv — cancellation is a REALIZATION (load-slip-
            # capable), classified never armed: residual must stay
            # below 2.05x ref (anything else is not a phase pair)
            ia_ = _pactlmon_r85_amps(inv_f, {"a": lhz})
            legs["mixinv"]["amps"] = ia_
            iw = ia_.get("windows") or []
            iv = _pactlmon_r85_med(iw, "l_a")
            ratio = (iv / ref) if ref and iv is not None else None
            legs["mixinv"]["residual_ratio"] = ratio
            legs["mixinv"]["realization"] = (
                "cancelled" if (ratio is not None and ratio < 0.12)
                else "slipped" if ratio is not None else "unmeasured")
            if ratio is None or ratio > 2.05:
                failures.append(
                    f"mixinv: residual={ratio} — not a coherent-pair "
                    "realization")
            # mixclip — hard clip at the s16 tap
            ca = _pactlmon_r85_amps(
                clip_f, {"a": lhz, "c": f3,
                         "h1": 3 * lhz, "h3": 3 * f3,
                         "i1": abs(2 * f3 - lhz)})
            legs["mixclip"]["amps"] = ca
            cw = ca.get("windows") or []
            pk = _pactlmon_r85_med(cw, "peak")
            rail = _pactlmon_r85_med(cw, "rail_frac")
            spur = max(_pactlmon_r85_med(cw, "l_h1") or 0,
                       _pactlmon_r85_med(cw, "r_h1") or 0,
                       _pactlmon_r85_med(cw, "l_h3") or 0,
                       _pactlmon_r85_med(cw, "r_h3") or 0,
                       _pactlmon_r85_med(cw, "l_i1") or 0,
                       _pactlmon_r85_med(cw, "r_i1") or 0)
            legs["mixclip"]["clip"] = {"peak_med": pk,
                                       "rail_frac_med": rail,
                                       "spur_max": spur}
            rlo, rhi = PACTLMON_R85_RAIL_ENV
            if pk is None or pk < 32767:
                failures.append(
                    f"mixclip: peak={pk} below the s16 rail — the "
                    "hard-clip arm fails")
            if rail is None or not (rlo <= rail <= rhi):
                failures.append(
                    f"mixclip: rail_frac={rail} outside "
                    f"{PACTLMON_R85_RAIL_ENV} — the clip-fraction "
                    "envelope fails")
            if spur < PACTLMON_R85_SPUR_MIN:
                failures.append(
                    f"mixclip: spur={spur} < {PACTLMON_R85_SPUR_MIN} "
                    "— the clip-product arm fails")
    finally:
        _pactlmon_r85_teardown(entry, failures, loads)
    entry["failures"] = failures
    return entry


def pactlmon_aplayenv_r85_entry():
    """aplay -D pipewire env targeting — PIPEWIRE_NODE / PIPEWIRE_PROPS
    target.object, the props-win conflict law, serial-in-props
    resolution, and the bogus-name silent fallback (SILENCE files only
    on the shared default — no tag tone ever lands there)."""
    failures, legs = [], {}
    entry = _pactlmon_r85_entry_head(
        "r85a aplay -D pipewire env targeting lattice")
    tools = {t: shutil.which(t) for t in
             ("aplay", "pw-dump", "pactl")}
    entry["tools"] = tools
    if not all(tools.values()):
        return _pactlmon_r85_block(
            entry, failures,
            f"missing tools: {[t for t, p in tools.items() if not p]}")
    loads = {}
    try:
        loads[PACTLMON_R85_NS] = _pwcat_r83_ns_load(PACTLMON_R85_NS)
        loads[PACTLMON_R85_NS2] = _pwcat_r83_ns_load(PACTLMON_R85_NS2)
        loads[PACTLMON_R85_NS]["field"] = "sink_name"
        loads[PACTLMON_R85_NS]["value"] = PACTLMON_R85_NS
        loads[PACTLMON_R85_NS2]["field"] = "sink_name"
        loads[PACTLMON_R85_NS2]["value"] = PACTLMON_R85_NS2
        if loads[PACTLMON_R85_NS].get("module_id") is None or \
                loads[PACTLMON_R85_NS2].get("module_id") is None:
            return _pactlmon_r85_block(
                entry, failures, "probe null sinks never enumerated",
                loads)
        gg = _pactlmon_r85_graph()
        na = _pactlmon_r85_node(gg, PACTLMON_R85_NS) or {}
        ser_a = na.get("object_serial")
        entry["ns_serial"] = ser_a
        if ser_a is None:
            return _pactlmon_r85_block(
                entry, failures, "probe sink serial never resolved",
                loads)
        base_env = dict(os.environ)
        for k in list(base_env):
            if k.startswith("PIPEWIRE_"):
                base_env.pop(k)
        with tempfile.TemporaryDirectory(prefix="r85a-env-") as tmp:
            tone = Path(tmp) / "r85a_tag.wav"
            _playback_r78_write_tone(tone, 3.0)
            silence = Path(tmp) / "r85a_silence.wav"
            _pactlmon_r85_tone(silence, 3.0, 20.0, 20.0, amp=0)
            ctx = {"tmp": tmp, "tone": tone, "sil": silence,
                   "redact": (str(tmp),)}
            try:
                legs["env_node"] = _alsapw_r84_aplay_leg(
                    "pipewire", ctx, tone_key="tone", env={
                        **base_env,
                        "PIPEWIRE_NODE": PACTLMON_R85_NS})
                legs["env_props"] = _alsapw_r84_aplay_leg(
                    "pipewire", ctx, tone_key="tone", env={
                        **base_env,
                        "PIPEWIRE_PROPS":
                            "{ target.object=" + PACTLMON_R85_NS +
                            " }"})
                legs["env_conflict"] = _alsapw_r84_aplay_leg(
                    "pipewire", ctx, tone_key="tone", env={
                        **base_env,
                        "PIPEWIRE_NODE": PACTLMON_R85_NS2,
                        "PIPEWIRE_PROPS":
                            "{ target.object=" + PACTLMON_R85_NS +
                            " }"})
                legs["env_serial"] = _alsapw_r84_aplay_leg(
                    "pipewire", ctx, tone_key="tone", env={
                        **base_env,
                        "PIPEWIRE_PROPS":
                            "{ target.object=" + str(ser_a) + " }"})
                # the two default-sink legs — SILENCE only, recorded
                legs["env_bogus"] = _alsapw_r84_aplay_leg(
                    "pipewire", ctx, tone_key="sil", env={
                        **base_env,
                        "PIPEWIRE_NODE": PACTLMON_R85_BOGUS})
                legs["env_none"] = _alsapw_r84_aplay_leg(
                    "pipewire", ctx, tone_key="sil", env=base_env)
            finally:
                entry["legs"] = legs
            # ---------------- verdicts ----------------
            def_bound = entry["inventory"]["default_sink"]
            def to_sink(nm, want_obj, want_consumer=None):
                """target.object publishes as an INT in pw-dump — both
                sides str()-normalized; the expected consumer (a sink
                NAME) may differ from the published target (a serial)."""
                l = legs[nm]
                wc = want_consumer or want_obj
                hits = [c for c in (l.get("nodes_mid") or [])
                        if str((c.get("props") or {})
                        .get("target.object")) == str(want_obj)]
                l["target_candidates"] = hits
                if not hits:
                    failures.append(
                        f"{nm}: no node carried target.object="
                        f"{want_obj} — the env landing arm fails")
                    return
                if not any(str(wc) in (c.get("consumers") or [])
                           for c in hits):
                    failures.append(
                        f"{nm}: candidates consumers="
                        f"{[c.get('consumers') for c in hits]} — "
                        f"the link to {wc} fails")
            to_sink("env_node", PACTLMON_R85_NS)
            to_sink("env_props", PACTLMON_R85_NS)
            to_sink("env_conflict", PACTLMON_R85_NS)
            # the props-win discriminator: nothing may land on ns2
            lc = legs["env_conflict"]
            if any(PACTLMON_R85_NS2 in (c.get("consumers") or [])
                   for c in (lc.get("nodes_mid") or [])):
                failures.append(
                    "env_conflict: a link landed on the NODE= sink "
                    "— the props-win law fails")
            to_sink("env_serial", ser_a, PACTLMON_R85_NS)
            # bogus + none -> silent fallback to the live default
            for nm, want_prop in (("env_bogus", PACTLMON_R85_BOGUS),
                                  ("env_none", None)):
                l = legs[nm]
                cands = l.get("nodes_mid") or []
                if want_prop is not None:
                    hits = [c for c in cands
                            if str((c.get("props") or {})
                            .get("target.object")) == str(want_prop)]
                    l["target_candidates"] = hits
                    if not hits:
                        failures.append(
                            f"{nm}: no node carried the bogus "
                            "target.object — the publish arm fails")
                        continue
                pool = cands if want_prop is None else hits
                if def_bound and not any(
                        def_bound in (c.get("consumers") or [])
                        for c in pool):
                    failures.append(
                        f"{nm}: consumers="
                        f"{[c.get('consumers') for c in pool]} — the "
                        "silent default fallback fails")
    finally:
        _pactlmon_r85_teardown(entry, failures, loads)
    entry["failures"] = failures
    return entry


def pactlmon_capture_r85_entry():
    """The capture-side monitor/source surface — the boundary-corrected
    --target lattice, the folded loss law (links die, never re-form,
    alive, no new content; the froze-vs-zeros shape recorded only), the
    prop-form default-monitor fallback, the Audio/Source self-destruct
    ladder (idle / pw-record / parec / prop / manual-link), and the
    no-late-bind leg."""
    failures, legs = [], {}
    entry = _pactlmon_r85_entry_head(
        "r85a capture-side target lattice + loss + self-destruct + "
        "late-bind")
    tools = {t: shutil.which(t) for t in
             ("pw-record", "parec", "pw-play", "pw-dump", "pw-link",
              "pactl")}
    entry["tools"] = tools
    if not all(tools.values()):
        return _pactlmon_r85_block(
            entry, failures,
            f"missing tools: {[t for t, p in tools.items() if not p]}")
    loads = {}
    feeder = None
    try:
        loads[PACTLMON_R85_TONE] = _pwcat_r83_ns_load(
            PACTLMON_R85_TONE)
        loads[PACTLMON_R85_NS2] = _pwcat_r83_ns_load(PACTLMON_R85_NS2)
        loads[PACTLMON_R85_TONE]["field"] = "sink_name"
        loads[PACTLMON_R85_TONE]["value"] = PACTLMON_R85_TONE
        loads[PACTLMON_R85_NS2]["field"] = "sink_name"
        loads[PACTLMON_R85_NS2]["value"] = PACTLMON_R85_NS2
        if loads[PACTLMON_R85_TONE].get("module_id") is None or \
                loads[PACTLMON_R85_NS2].get("module_id") is None:
            return _pactlmon_r85_block(
                entry, failures, "probe sinks never enumerated",
                loads)
        with tempfile.TemporaryDirectory(prefix="r85a-cap-") as tmp:
            tone = Path(tmp) / "r85a_tag.wav"
            _playback_r78_write_tone(tone, PACTLMON_R85_FEED_S)
            ctx = {"tmp": tmp, "tone": tone,
                   "ns": PACTLMON_R85_NS2,
                   "tone_sink": PACTLMON_R85_TONE}
            # the feeder — a tagged pw-play into the tone sink for the
            # whole entry (the remap source's master carries it)
            feeder = _pactlmon_r85_play(
                f"{PACTLMON_R85_PREFIX}_feed", PACTLMON_R85_TONE,
                tone)
            loads[PACTLMON_R85_VSRC] = _pactlmon_r85_remap_load(
                f"{PACTLMON_R85_TONE}.monitor", PACTLMON_R85_VSRC)
            try:
                gg = _pactlmon_r85_graph()
                vs = _pactlmon_r85_node(gg, PACTLMON_R85_VSRC) or {}
                ns2n = _pactlmon_r85_node(gg, PACTLMON_R85_NS2) or {}
                vser, vid = vs.get("object_serial"), vs.get(
                    "node_id")
                ser2 = ns2n.get("object_serial")
                entry["vsrc"] = {"serial": vser, "node_id": vid,
                                 "media_class": vs.get(
                                     "media_class")}
                entry["ns2_serial"] = ser2
                if vs.get("media_class") and \
                        loads[PACTLMON_R85_VSRC].get(
                            "module_id") is None:
                    entry.setdefault(
                        "coverage_blocked", []).append(
                        "remap source never enumerated — "
                        "vsrc-target legs skipped")
                # -------- the baseline: the vsrc carries tone ----
                legs["cap_baseline"] = _pactlmon_r85_cap_leg(
                    "cap_baseline", ctx, PACTLMON_R85_VSRC,
                    dur_s=2.2, link_samples=(0.8, 1.6))
                # -------- --target lattice FIRST — the loss legs  --------
                # kill the sources, so every source-target form runs
                # while `vsrc` is still alive (the serial/id forms were
                # the boundary's corrections — scout had the object.id
                # leg wrong).
                legs["t_srcname"] = _pactlmon_r85_cap_leg(
                    "t_srcname", ctx, PACTLMON_R85_VSRC,
                    dur_s=2.4, link_samples=(0.9, 1.9))
                legs["t_srcserial"] = _pactlmon_r85_cap_leg(
                    "t_srcserial", ctx, vser, dur_s=2.4,
                    link_samples=(0.9, 1.9))
                legs["t_srcid"] = _pactlmon_r85_cap_leg(
                    "t_srcid", ctx, vid, dur_s=2.4,
                    link_samples=(0.9, 1.9))
                legs["t_prop_srcname"] = _pactlmon_r85_cap_leg(
                    "t_prop_srcname", ctx, PACTLMON_R85_VSRC,
                    prop=True, dur_s=2.4, link_samples=(0.9, 1.9))
                legs["t_sinkname"] = _pactlmon_r85_cap_leg(
                    "t_sinkname", ctx, PACTLMON_R85_NS2,
                    dur_s=2.4, link_samples=(0.9, 1.9))
                legs["t_sinkserial"] = _pactlmon_r85_cap_leg(
                    "t_sinkserial", ctx, ser2, dur_s=2.4,
                    link_samples=(0.9, 1.9))
                legs["t_prop_sinkname"] = _pactlmon_r85_cap_leg(
                    "t_prop_sinkname", ctx, PACTLMON_R85_NS2,
                    prop=True, dur_s=2.4, link_samples=(0.9, 1.9))
                # -------- the loss law (folded falsification) -----
                # rep 0 kills `vsrc`; rep 1 loads `vsrcb` and kills it.
                for rep in range(2):
                    legs[f"cap_loss_{rep}"] = \
                        _pactlmon_r85_cap_leg(
                            f"cap_loss_{rep}", ctx,
                            PACTLMON_R85_VSRC if rep == 0 else
                            PACTLMON_R85_VSRC + "b",
                            dur_s=4.8, loss_at=1.5,
                            loss_field="source_name",
                            loss_value=(PACTLMON_R85_VSRC if rep == 0
                                        else PACTLMON_R85_VSRC +
                                        "b"),
                            link_samples=(0.8, 2.4, 4.0))
                    if rep == 0:
                        loads[PACTLMON_R85_VSRC + "b"] = \
                            _pactlmon_r85_remap_load(
                                f"{PACTLMON_R85_TONE}.monitor",
                                PACTLMON_R85_VSRC + "b")
                # -------- prop-form loss -> default monitor -------
                legs["cap_loss_prop"] = _pactlmon_r85_cap_leg(
                    "cap_loss_prop", ctx, PACTLMON_R85_TONE,
                    prop=True, dur_s=4.8, loss_at=1.6,
                    loss_field="sink_name",
                    loss_value=PACTLMON_R85_TONE,
                    link_samples=(0.8, 2.4, 4.0))
                # the feeder lost its sink — kill it NOW, before the
                # r78 default-fallback lands a tag TONE on the shared
                # sink (only silence may ever land there).
                if feeder is not None and feeder.poll() is None:
                    _pactlmon_r85_killpg(feeder)
                    feeder.wait()
                # -------- Audio/Source self-destruct ladder -------
                loads[PACTLMON_R85_SD] = _pactlmon_r85_sd_load(
                    PACTLMON_R85_SD)
                # idle leg — the loaded sd above stays untouched for
                # the whole window (a --version client never binds)
                legs["sd_idle"] = _pactlmon_r85_sd_leg(
                    "sd_idle", ctx, PACTLMON_R85_SD,
                    ["pw-record", "--version"], dur_s=3.6)
                if loads[PACTLMON_R85_SD].get("module_id") is not None:
                    # still alive after idle — the connect legs each
                    # need a FRESH sd (a bound one is already dead)
                    for nm, argv in (
                            ("sd_record",
                             ["pw-record", "-P", "node.name=<TAG>",
                              "--target", "<SD>", "--rate", "48000",
                              "--channels", "2", "--format", "s16",
                              str(Path(tmp) / "sdr.wav")]),
                            ("sd_parec",
                             ["parec", "--latency-msec=50", "-d",
                              "<SD>", "--file-format=wav",
                              str(Path(tmp) / "sdp.wav")])):
                        _pactlmon_r85_unload_own(
                            loads[PACTLMON_R85_SD]["module_id"],
                            "sink_name", PACTLMON_R85_SD)
                        loads[PACTLMON_R85_SD] = \
                            _pactlmon_r85_sd_load(PACTLMON_R85_SD)
                        legs[nm] = _pactlmon_r85_sd_leg(
                            nm, ctx, PACTLMON_R85_SD, argv,
                            dur_s=2.6)
                        legs[nm]["out"] = _alsapw_r84_nz_stats(
                            Path(tmp) / ("sdr.wav" if nm ==
                                         "sd_record" else
                                         "sdp.wav"))
                # prop form — must never touch the node
                _pactlmon_r85_unload_own(
                    loads[PACTLMON_R85_SD]["module_id"],
                    "sink_name", PACTLMON_R85_SD)
                loads[PACTLMON_R85_SD] = _pactlmon_r85_sd_load(
                    PACTLMON_R85_SD)
                legs["sd_prop"] = _pactlmon_r85_cap_leg(
                    "sd_prop", ctx, PACTLMON_R85_SD, prop=True,
                    dur_s=2.4, link_samples=(0.9, 1.9))
                legs["sd_prop"]["load_leaf"] = dict(
                    loads[PACTLMON_R85_SD])
                # manual pw-link — a link is NOT a client bind
                _pactlmon_r85_unload_own(
                    loads[PACTLMON_R85_SD]["module_id"],
                    "sink_name", PACTLMON_R85_SD)
                loads[PACTLMON_R85_SD] = _pactlmon_r85_sd_load(
                    PACTLMON_R85_SD)
                pl = {"name": "sd_pwlink"}
                if loads[PACTLMON_R85_SD].get("module_id") is None:
                    pl["skipped"] = "sd never enumerated"
                else:
                    ports = _playback_r78_output_ports(
                        PACTLMON_R85_SD) or []
                    pl["sd_ports"] = ports
                    outp = next((p for p in ports
                                 if "capture_" in p), None)
                    if outp is not None:
                        ln = _pactlmon_r85_run(
                            ["pw-link", outp,
                             f"{PACTLMON_R85_NS2}:playback_FL"],
                            8.0)
                        time.sleep(1.2)
                        pl["link"] = ln
                        pl["module_alive"] = \
                            _pactlmon_r85_module_index(
                                "sink_name",
                                PACTLMON_R85_SD) is not None
                        pl["source_alive"] = PACTLMON_R85_SD in (
                            _playback_r78_source_names() or [])
                        g = _pactlmon_r85_graph()
                        pl["links"] = _pactlmon_r85_edges_out(
                            g, PACTLMON_R85_SD)
                        _pactlmon_r85_run(
                            ["pw-link", "-d", outp,
                             f"{PACTLMON_R85_NS2}:playback_FL"],
                            8.0)
                legs["sd_pwlink"] = pl
                # -------- no late-bind for a conforming source ----
                # stall on the absent name, load the CONFORMING remap
                # source under that name mid-stall (master = the
                # still-live ns2 monitor — the tone sink is dead by
                # now), and confirm the record never links.
                lb_leg = _pactlmon_r85_cap_leg(
                    "latebind", ctx, PACTLMON_R85_LATE,
                    dur_s=4.4, late_at=1.5,
                    late_master=f"{PACTLMON_R85_NS2}.monitor",
                    late_name=PACTLMON_R85_LATE,
                    link_samples=(0.9, 2.6, 4.0))
                legs["latebind"] = lb_leg
                if (lb_leg.get("late_load") or {}).get(
                        "module_id") is not None:
                    loads[PACTLMON_R85_LATE] = lb_leg["late_load"]
            finally:
                entry["legs"] = legs
            # ---------------- verdicts ----------------
            def links_of(nm):
                l = legs[nm]
                return [e for s in l.get("samples", [])
                        for e in s.get("links", [])]
            def link_ports(nm):
                return {e.get("out_port_name") for e in links_of(nm)}
            # baseline: the vsrc binds capture_* and carries content
            lb = legs["cap_baseline"]
            bp = link_ports("cap_baseline")
            if not bp or not all(
                    (p or "").startswith("capture_") for p in bp):
                failures.append(
                    f"cap_baseline: links={bp} — the remap-source "
                    "bind arm fails")
            bl = _alsapw_r84_nz_stats(lb.get("file"))
            lb["nz"] = bl
            if (bl.get("peak") or 0) < 1000:
                failures.append(
                    f"cap_baseline: peak={bl.get('peak')} — the "
                    "remap source carried no content")
            # loss legs: links die, never re-form, the stream stays
            # alive, growth CEASES (last two samples equal size), and
            # any post-loss bytes are a bounded in-flight flush
            # (<=8 quanta — the authoring pass measured exactly one
            # 2048-frame quantum of real content appended after the
            # module died; the boundary measured a clean froze and the
            # scout measured growing ZEROS — shape recorded, never
            # armed).
            for rep in range(2):
                l = legs[f"cap_loss_{rep}"]
                post = _pactlmon_r85_post_stats(
                    l.get("file"), l.get("size_at_loss"))
                l["post"] = post
                sams = l.get("samples") or []
                pre = sams[0] if sams else {}
                post_s = sams[1:] if len(sams) > 1 else []
                pre_ok = bool(pre.get("links"))
                post_links = [e for s in post_s
                              for e in s.get("links", [])]
                if not pre_ok:
                    failures.append(
                        f"cap_loss_{rep}: never linked pre-loss — "
                        "the leg measured nothing")
                if post_links:
                    failures.append(
                        f"cap_loss_{rep}: links re-formed post-"
                        f"loss: {post_links}")
                if not l.get("alive_at_end"):
                    failures.append(
                        f"cap_loss_{rep}: record died — the "
                        "process-alive arm fails")
                if (l.get("unloaded") or {}).get("exit_code") != 0:
                    failures.append(
                        f"cap_loss_{rep}: name-verified unload "
                        f"failed: {l.get('unloaded')}")
                if (post.get("post_frames") or 0) > \
                        PACTLMON_R85_FLUSH_BOUND:
                    failures.append(
                        f"cap_loss_{rep}: post_frames="
                        f"{post.get('post_frames')} > "
                        f"{PACTLMON_R85_FLUSH_BOUND} — a rebind, not "
                        "a flush")
                if len(sams) >= 2 and \
                        sams[-1].get("size") != sams[-2].get("size"):
                    failures.append(
                        f"cap_loss_{rep}: sizes {sams[-2].get('size')}"
                        f"->{sams[-1].get('size')} — growth never "
                        "ceased post-loss")
            # prop loss: re-links to the DEFAULT sink's monitor
            l = legs["cap_loss_prop"]
            def_sink = entry["inventory"]["default_sink"]
            post_l = [e for s in (l.get("samples") or [])[1:]
                      for e in s.get("links", [])]
            l["post_links"] = post_l
            mon_ok = def_sink and any(
                e.get("out_node") == def_sink and
                (e.get("out_port_name") or "")
                .startswith("monitor_") for e in post_l)
            if not mon_ok:
                failures.append(
                    f"cap_loss_prop: post-links={post_l} — never "
                    "re-linked to the default monitor")
            if (l.get("unloaded") or {}).get("exit_code") != 0:
                failures.append(
                    f"cap_loss_prop: unload failed: "
                    f"{l.get('unloaded')}")
            # --target lattice
            ts = legs["t_sinkname"]
            tsp = link_ports("t_sinkname")
            mon_hit = any((p or "").startswith("monitor_")
                          for p in tsp)
            # pw-record exits rc=1 on its SIGTERM handler — classify
            # on links + liveness, never on the bare exit code. The
            # boundary measured the arbitrary-source bind; this
            # authoring pass measured BOTH the refusal (pre-run) and
            # the vsrc bind (the run) — only a monitor_* link breaks
            # the law.
            ts_real = ("bound_source" if tsp else
                       "stalled" if ts.get("alive_at_end") else
                       "refused" if ts.get("exit_code") == 1 else
                       "other")
            legs["t_sinkname"]["realization"] = ts_real
            if mon_hit or ts_real == "other":
                failures.append(
                    f"t_sinkname: realization={ts_real} ports="
                    f"{tsp} — a noprop sink name must never link "
                    "monitor_*")
            l = legs["t_sinkserial"]
            sp = link_ports("t_sinkserial")
            if not sp or not all(
                    (p or "").startswith("monitor_") for p in sp) \
                    or not any(
                        e.get("out_node") == PACTLMON_R85_NS2
                        for s in l.get("samples", [])
                        for e in s.get("links", [])):
                failures.append(
                    f"t_sinkserial: links={sp} — the numeric-bypass "
                    "monitor arm fails")
            for nm, want_node in (("t_srcname", PACTLMON_R85_VSRC +
                                   "b"),
                                  ("t_srcserial", PACTLMON_R85_VSRC +
                                   "b"),
                                  ("t_srcid", PACTLMON_R85_VSRC +
                                   "b")):
                lp = link_ports(nm)
                if not lp or not all(
                        (p or "").startswith("capture_") for p in
                        lp):
                    failures.append(
                        f"{nm}: links={lp} — the source-bind arm "
                        "fails")
            lp = link_ports("t_prop_sinkname")
            if not lp or not all(
                    (p or "").startswith("monitor_") for p in lp):
                failures.append(
                    f"t_prop_sinkname: links={lp} — the prop-form "
                    "monitor arm fails")
            lp = link_ports("t_prop_srcname")
            pl = [e for s in legs["t_prop_srcname"].get("samples", [])
                  for e in s.get("links", [])]
            if not pl or not all(
                    (e.get("out_port_name") or "")
                    .startswith("monitor_") for e in pl) or \
                    (def_sink and not any(
                        e.get("out_node") == def_sink for e in pl)):
                failures.append(
                    f"t_prop_srcname: links={pl} — the prop form "
                    "did not resolve on the default monitor")
            # self-destruct ladder
            l = legs["sd_idle"]
            if l.get("module_dead_at_s") is not None or \
                    l.get("source_dead_at_s") is not None:
                failures.append(
                    f"sd_idle: died idle at mod="
                    f"{l.get('module_dead_at_s')} src="
                    f"{l.get('source_dead_at_s')} — the idle-"
                    "survival arm fails")
            for nm in ("sd_record", "sd_parec"):
                l = legs.get(nm) or {}
                if not l:
                    continue
                if l.get("module_dead_at_s") is None or \
                        l.get("module_dead_at_s") > 1.5:
                    failures.append(
                        f"{nm}: module_dead_at="
                        f"{l.get('module_dead_at_s')} — the "
                        "connect-kill arm fails")
                if (l.get("out") or {}).get("data_actual", 0) > 200 \
                        or l.get("links"):
                    failures.append(
                        f"{nm}: content/links formed before "
                        "death — the no-link arm fails")
            l = legs["sd_prop"]
            plinks = [e for s in l.get("samples", [])
                      for e in s.get("links", [])]
            sd_gone = _pactlmon_r85_module_index(
                "sink_name", PACTLMON_R85_SD) is None
            l["sd_module_gone_after"] = sd_gone
            # module FATE is a realization: the boundary measured a
            # clean never-touched fallback; this authoring pass
            # measured a transient name-bind that killed the trap
            # before the prop steered to the default monitor. The
            # armed invariant is the DESTINATION — every link must
            # land on the default monitor, never the trap's own
            # ports persistently.
            l["realization"] = ("clean_default_fallback"
                                if not sd_gone else
                                "bind_killed_then_default")
            if plinks and not all(
                    (e.get("out_port_name") or "")
                    .startswith("monitor_") for e in plinks):
                failures.append(
                    f"sd_prop: links={plinks} — non-monitor links "
                    "under the prop form")
            if def_sink and plinks and not any(
                    e.get("out_node") == def_sink for e in plinks):
                failures.append(
                    f"sd_prop: links={plinks} — did not fall to "
                    "the default monitor")
            if not plinks and not sd_gone:
                failures.append(
                    "sd_prop: neither bound nor dead — the leg "
                    "measured nothing")
            l = legs["sd_pwlink"]
            if not l.get("skipped"):
                if not l.get("module_alive") or \
                        not l.get("source_alive"):
                    failures.append(
                        "sd_pwlink: node/module died on a manual "
                        "link — the no-client-bind arm fails")
            # late-bind: the boundary measured a dead stall (never
            # re-armed by the conforming source, 3/3+3/3); THIS host
            # bound the late source immediately — a bimodal WP
            # re-target realization. Armed: any link that forms must
            # land on the LATE source's OWN capture_* ports (never a
            # monitor, never a foreign node); the fate is recorded.
            l = legs["latebind"]
            lk = [e for s in l.get("samples", [])
                  for e in s.get("links", [])]
            good_shape = lk and all(
                e.get("out_node") == PACTLMON_R85_LATE and
                (e.get("out_port_name") or "")
                .startswith("capture_") for e in lk)
            l["realization"] = (
                "late_bound" if good_shape else
                "foreign_bind" if lk else
                "stalled" if l.get("alive_at_end") else
                "refused" if l.get("exit_code") == 1 else "other")
            if lk and not good_shape:
                failures.append(
                    f"latebind: links={lk} — a foreign/monitor bind "
                    "breaks the target lattice")
            if l["realization"] == "other":
                failures.append(
                    f"latebind: realization=other — no stall, no "
                    "bind, no refusal measured")
    finally:
        if feeder is not None and feeder.poll() is None:
            _pactlmon_r85_killpg(feeder)
            feeder.wait()
        _pactlmon_r85_teardown(entry, failures, loads)
    entry["failures"] = failures
    return entry


def pactlmon_negctl_r85_entry():
    """The classifier unit table (canned stderr -> named class; empty/
    noise/crash-word -> None) + live no-error cells + the mid-run
    SIGKILL discriminator — a bound kill or a crash can never pass as
    a named refusal."""
    failures, legs = [], {}
    entry = _pactlmon_r85_entry_head(
        "r85a negative controls — classifier unit table + live "
        "controls")
    tools = {t: shutil.which(t) for t in
             ("pactl", "pw-dump", "pw-play", "pw-cli")}
    entry["tools"] = tools
    if not all(tools.values()):
        return _pactlmon_r85_block(
            entry, failures,
            f"missing tools: {[t for t, p in tools.items() if not p]}")
    cases = [
        ("u_getinfo", "Failed to get sink information: No such "
         "entity\n", "pa_get_info_noent"),
        ("u_getinfo_src", "Failed to get source information: No such "
         "entity\n", "pa_get_info_noent"),
        ("u_failure_noent", "Failure: No such entity\n",
         "pa_failure_noent"),
        ("u_stream_noent", "Stream error: No such entity\n",
         "pa_stream_noent"),
        ("u_invalid_arg", "Operation failed: Invalid argument\n",
         "pa_invalid_arg"),
        ("u_pwcli_global", "Error: \"info: unknown global "
         "'232456'\"\n", "pwcli_unknown_global"),
        ("u_no_target", "stream node 84 error: no target node "
         "available\nremote error: id=2 seq:7 res:-2 (No such file "
         "or directory): no target node available\n",
         "no_target_node"),
        ("u_move_parse", "Failed to move sink input to 'x': No such "
         "entity\n", "pa_no_such_entity"),
        # negatives — noise, empties, crash words, success chatter
        ("u_empty", "", None),
        ("u_noise", "Volume: front-left: 65536 / 100% / 0.00 dB\n",
         None),
        ("u_segv_words", "Segmentation fault (core dumped)\n", None),
        ("u_recording", "Recording WAVE 'x.wav' : Signed 16 bit "
         "Little Endian\n", None),
        ("u_unknown_pcm", "Unknown PCM pulse\n", "alsa_unknown_pcm"),
    ]
    for name, text, want in cases:
        got, hit = _pactlmon_r85_errclass(text)
        legs[name] = {"stderr": text, "expect": want, "got": got,
                      "hit": hit}
        if got != want:
            failures.append(f"{name}: class {got} != {want}")
    loads = {}
    try:
        loads[PACTLMON_R85_NS] = _pwcat_r83_ns_load(PACTLMON_R85_NS)
        loads[PACTLMON_R85_NS]["field"] = "sink_name"
        loads[PACTLMON_R85_NS]["value"] = PACTLMON_R85_NS
        with tempfile.TemporaryDirectory(prefix="r85a-neg-") as tmp:
            tone = Path(tmp) / "r85a_tag.wav"
            _playback_r78_write_tone(tone, 2.0)
            legs["ctl_pactl_info"] = _pactlmon_r85_run(
                ["pactl", "info"], 8.0)
            legs["ctl_pwdump"] = _pactlmon_r85_run(
                ["pw-dump"], 15.0)
            legs["ctl_pwcli_ser"] = _pactlmon_r85_run(
                ["pw-cli", "info", "999999999"], 10.0)
            kp = _alsapw_r84_spawn(
                ["pw-play", "-P",
                 f"node.name={PACTLMON_R85_PREFIX}_killctl",
                 "-P", f"media.role={PACTLMON_R85_ROLE}",
                 "--target", PACTLMON_R85_NS, str(tone)])
            time.sleep(0.8)
            _pactlmon_r85_killpg(kp)
            kp.wait()
            kerr = kp.stderr.read().decode(errors="replace") \
                if kp.stderr else ""
            kcls, khit = _pactlmon_r85_errclass(kerr)
            legs["ctl_sigkill"] = {
                "argv": "pw-play <tag> <ns> (SIGKILL at 0.8s)",
                "exit_code": kp.returncode,
                "signal": (signal.Signals(-kp.returncode).name
                           if (kp.returncode or 0) < 0 else None),
                "stderr_tail": _capture_tail(kerr, "ctl_sigkill"),
                "error_class": kcls, "error_hit": khit}
    finally:
        _pactlmon_r85_teardown(entry, failures, loads)
    for name in ("ctl_pactl_info", "ctl_pwdump"):
        l = legs[name]
        if l.get("exit_code") != 0 or l.get("error_class") or \
                l.get("signal") or l.get("killed_at_bound"):
            failures.append(
                f"{name}: rc={l.get('exit_code')} class="
                f"{l.get('error_class')} sig={l.get('signal')} "
                "killed={l.get('killed_at_bound')} — live "
                "control fails")
    l = legs["ctl_pwcli_ser"]
    blob = (l.get("stderr") or "") + (l.get("stdout") or "")
    if l.get("exit_code") != 0 or "unknown global" not in blob:
        failures.append(
            f"ctl_pwcli_ser: rc={l.get('exit_code')} — the live "
            "rc-0 unknown-global fails")
    l = legs["ctl_sigkill"]
    if l.get("signal") != "SIGKILL" or l.get("error_class") is not \
            None:
        failures.append(
            f"ctl_sigkill: sig={l.get('signal')} class="
            f"{l.get('error_class')} — kill-vs-refusal "
            "discriminator fails")
    entry["legs"] = legs
    entry["failures"] = failures
    return entry


