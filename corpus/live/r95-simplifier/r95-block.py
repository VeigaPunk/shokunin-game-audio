# r95: the JACK <-> PIPEWIRE INTEROP LATTICE — pipewire-jack 1.6.8 is
#     this host's ONLY libjack (no jack2, no jackd/jack_lsp/jack_connect),
#     so the JACK client ABI is a PipeWire client surface: a JACK client
#     IS a native PW client+node, its ports become PW ports, and every
#     JACK API family is a projection of the PW graph. The lattice pins
#     the boundary-surviving claims (reports/round-95/r95-boundary.md,
#     which re-measured the scout's table under load and falsified/
#     refined four rows):
#       - availability: the version quadruple [3,1,6,8] ("3.1.6.8 (using
#         PipeWire 1.6.8)"), 168 exported `jack_*` symbols and the
#         absent netjack/slist/adapter + weak-helper class;
#       - citizen shape: client.api=jack, node.group=group.dsp.0,
#         media.category=Duplex, media.role=DSP, node.always-process
#         true, ZERO autoconnect links; port alias/object.path/
#         format.dsp triple; Physical/Terminal survive as port props,
#         CanMonitor does not (and — the author correction read off the
#         boundary's own receipts — the CanMonitor BIT does not survive
#         jack_port_flags either: the round-trip is 2, not 0xA);
#       - the addressing law: jack_connect resolves the RENDERED
#         `<node.description>:<port>` name (rc 0) and the native
#         `<node.name>:<port>` form only when the two coincide (corner,
#         node.description == node.name); the `object.path` alias
#         (`<node.name>:playback_0`) resolves under jack.fill-aliases;
#       - both byte witnesses: the JACK->PW capture peak/energy and the
#         PW->JACK input peak are SAMPLE-EXACT (in_peak is the source
#         WAV's own int16 peak / 32768), and the Goertzel energy tracks
#         the tone window — the whole-file hash/rms is the boundary's
#         falsified window artifact and is RECORDED, never armed;
#       - the quantum law: an inactive jack_set_buffer_size is invisible
#         to jack_get_buffer_size (latency default), the activated value
#         lands as node.force-quantum, a live set delivers a
#         buffer-size callback, a second client sees the changed value,
#         and PIPEWIRE_QUANTUM=q/rate == `pw-jack -p q` (node props);
#         the jack.global-buffer-size opt-in writes the `settings`
#         clock.force-quantum metadata instead (restored to "0" by
#         jack_set_buffer_size(1) — the ONLY host-state mutation this
#         family performs, restored and verified in the same entry),
#         while without the opt-in nframes==1 writes node.force-quantum
#         "1" (metadata-path-only reset — the boundary's F7);
#       - the broken families: the xrun callback cannot see client-side
#         stalls (it mirrors the DRIVER counter), the RT-priority
#         accessors return uninitialized stack (poison control:
#         0xAA/0xBB pattern returns verbatim), latency is a local store
#         deferred to the data loop, the transport is a read-only
#         projection (start/stop gate it; locate/reposition are inert),
#         and jack_set_property writes the `default` metadata keyed by
#         the object's registry id.
#
# A NEW parallel ledger family; prior rows untouched; every r76-r89
# guard inherited (seat-owned r95a_<pid> names, the private
# r95arole<pid> key, name-verified sink_name= unloads, never
# set-default-*, bounded process groups, own-session children with
# SIGTERM->SIGKILL escalation). The family lock is a FIXED lane path
# under corpus/live/ (the r84 F1 3-seat consensus — never TMPDIR). The
# own JACK client is a FIXTURE SOURCE (corpus/fixtures/r95jack.c)
# compiled into the entry's temp dir with gcc -ljack -lm; a missing
# compiler/header/libjack is a named coverage block, never a silent
# green. Volatile values (ids, serials, uuids, cpu_load, wall times,
# loadavg, sibling driver names, the stack-garbage RT values) are
# RECORDED, never armed; foreign objects are censused, never touched.

JACK_R95_PID = os.getpid()
JACK_R95_PREFIX = f"r95a_{JACK_R95_PID}"
JACK_R95_NS = f"r95a_ns_{JACK_R95_PID}"       # driver sink: description != name
JACK_R95_DS = f"r95a_ds_{JACK_R95_PID}"       # its rendered description
JACK_R95_CORNER = f"r95a_t4_{JACK_R95_PID}"   # corner sink: description == name
JACK_R95_ROLE = f"r95arole{JACK_R95_PID}"     # private role key — never `music`
JACK_R95_SRC = ROOT / "fixtures" / "r95jack.c"
JACK_R95_JSON = "R95AJSON "
JACK_R95_TONE_HZ = 997.0
JACK_R95_TONE_RATE = 48000
JACK_R95_AMP_I16 = 16383                      # int16 peak of the tone fixture
JACK_R95_LIBJACK = Path("/usr/lib/libjack.so.0.3.1608")
JACK_R95_ABSENT_SYMS = ("jack_net_open", "jack_client_activate",
                        "jack_uuid_to_string", "jack_error", "jack_info",
                        "jack_log", "jack_create_adapter")
JACK_R95_PRESENT_SYMS = ("jack_session_notify", "jack_reserve_client_name",
                         "jack_client_real_time_priority",
                         "jack_client_max_real_time_priority",
                         "jack_set_buffer_size", "jack_connect",
                         "jack_set_property", "jack_transport_reposition")

_JACK_R95_ERR_CLASSES = (
    ("jack_r95_no_daemon", r"Could not connect to JACK server"),
    ("jack_r95_unknown_mode", r"unknown"),
)


def _jack_r95_errclass(text):
    for name, pat in _JACK_R95_ERR_CLASSES:
        m = re.search(pat, text or "")
        if m:
            return name, m.group(0).strip()
    return _pwprof_r89_errclass(text or "")


def _jack_r95_norm(text):
    """Volatile-field scrub: r88's node/seq/id classes, the nanosecond
    counters, uuids and the client pid suffix."""
    s = _pwprof_r89_norm(text or "")
    s = re.sub(rf"r95a_[0-9]+", "r95a_<pid>", s)
    return s


def _jack_r95_env(name, extra=None):
    """Per-leg environment: the R95A_NAME client-name override (the seat
    pid rides in the name, so a same-family run in another tree can
    never collide on an exact-name open) plus any leg-specific env."""
    env = os.environ.copy()
    env["R95A_NAME"] = name
    for key, val in (extra or {}).items():
        env[key] = val
    return env


def _jack_r95_run(argv, timeout_s, env=None, wd=None, sig_at=None,
                  sig=signal.SIGTERM, mid=None, mid_at=0.0,
                  keep_chars=1400, keep_raw=False):
    """One bounded child with its own session and a CONTINUOUSLY
    drained stdout. `mid` is a callable fired once at `mid_at` seconds
    whose return value is stored under `mid` — the concurrent-witness
    hook (pw-dump/pw-link/pw-metadata snapshots while the client runs).
    SIGTERM at `sig_at`, SIGKILL at the bound; both through the process
    group (a JACK client's helper threads die with it)."""
    rec = {"argv": " ".join(str(a) for a in argv)}
    try:
        proc = subprocess.Popen(
            argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, env=env, cwd=wd,
            start_new_session=True)
    except OSError as exc:
        rec["spawn_error"] = str(exc)[:160]
        return rec
    try:
        os.set_blocking(proc.stdout.fileno(), False)
    except OSError:
        pass
    t0 = time.monotonic()
    buf = bytearray()
    fired_sig = False
    alive_at_sig = None
    killed = False
    mid_done = False
    mid_rec = None
    while True:
        now = time.monotonic() - t0
        if mid is not None and not mid_done and now >= mid_at:
            mid_done = True
            try:
                mid_rec = mid()
            except Exception as exc:            # a witness may never
                mid_rec = {"error":                # abort the leg
                           f"{type(exc).__name__}: {exc}"[:200]}
        if sig_at is not None and not fired_sig and now >= sig_at:
            fired_sig = True
            alive_at_sig = proc.poll() is None
            if alive_at_sig:
                _alsapw_r84_killpg(proc, sig)
        if now > timeout_s:
            killed = True
            _alsapw_r84_killpg(proc, signal.SIGKILL)
            proc.wait()
            break
        if proc.poll() is not None:
            break
        try:
            chunk = os.read(proc.stdout.fileno(), 65536)
            if chunk:
                buf += chunk
        except (BlockingIOError, OSError):
            pass
        time.sleep(0.01)
    try:
        buf += proc.stdout.read() or b""
    except (OSError, ValueError):
        pass
    try:
        err = proc.stderr.read() or b""
    except (OSError, ValueError):
        err = b""
    outt = bytes(buf).decode(errors="replace")
    errt = err.decode(errors="replace")
    cls, hit = _jack_r95_errclass(errt + "\n" + outt)
    rec.update({"exit_code": proc.returncode,
                "signal": (signal.Signals(-proc.returncode).name
                           if (proc.returncode or 0) < 0 else None),
                "killed_at_bound": killed,
                "alive_at_sig": alive_at_sig,
                "wall_s": round(time.monotonic() - t0, 3),
                "stdout": _jack_r95_norm(outt)[:keep_chars],
                "stdout_bytes": len(buf),
                "stderr": _jack_r95_norm(errt)[:keep_chars],
                "stderr_bytes": len(errt),
                "error_class": cls, "error_hit": hit})
    if mid_rec is not None:
        rec["mid"] = mid_rec
    if keep_raw:
        rec["stdout_raw"] = outt
        rec["stderr_raw"] = errt
    return rec


def _jack_r95_json(rec):
    """The probe's one-line `R95AJSON {...}` record (None when absent or
    unparseable — an open failure exits 3 with a status line)."""
    for ln in (rec.get("stdout_raw") or "").splitlines():
        if ln.startswith(JACK_R95_JSON):
            try:
                return json.loads(ln[len(JACK_R95_JSON):])
            except ValueError:
                return None
    return None


def _jack_r95_probe(probe, args, timeout_s, env=None, wd=None,
                    mid=None, mid_at=0.0, keep_raw=True):
    """One probe invocation + the parsed R95AJSON record folded into the
    leg under `json` (raw text kept for the JSON line, scrubbed copy for
    the receipt). `probe=None` means `args` already IS the full argv
    (the pw-jack wrapper leg)."""
    argv = ([*[str(a) for a in args]] if probe is None
            else [probe, *[str(a) for a in args]])
    rec = _jack_r95_run(argv, timeout_s,
                        env=env, wd=wd, mid=mid, mid_at=mid_at,
                        keep_chars=1600, keep_raw=keep_raw)
    rec["json"] = _jack_r95_json(rec)
    return rec


def _jack_r95_build(tmp):
    """Compile the fixture source into the entry's temp dir. gcc is the
    host compiler (16.1.1); `-ljack` is pipewire-jack's libjack and
    `-lm` the math the tone/Goertzel need. A failure is returned as a
    named build record, never raised."""
    out = Path(tmp) / "r95jack"
    rec = {"src": "corpus/fixtures/r95jack.c",
           "src_sha256": _capture_r77_sha256(JACK_R95_SRC)}
    if not JACK_R95_SRC.exists():
        rec["error"] = "fixture source missing"
        return None, rec
    cc = shutil.which("gcc") or shutil.which("cc")
    if cc is None:
        rec["error"] = "no compiler"
        return None, rec
    try:
        proc = subprocess.run(
            [cc, "-O1", "-w", "-o", str(out), str(JACK_R95_SRC),
             "-ljack", "-lm"],
            capture_output=True, timeout=180)
    except (subprocess.TimeoutExpired, OSError) as exc:
        rec["error"] = f"{type(exc).__name__}: {exc}"[:200]
        return None, rec
    rec.update({"compiler": cc, "rc": proc.returncode,
                "stderr_tail": proc.stderr.decode(
                    errors="replace").strip()[-400:] or None,
                "binary_sha256": (_capture_r77_sha256(out)
                                  if out.exists() else None)})
    if proc.returncode != 0 or not out.exists():
        return None, rec
    return str(out), rec


def _jack_r95_graph():
    """pw-dump -> the full census the JACK projection is compared
    against: clients (api/name), nodes (description/group/category/
    role/always-process/force-quantum/force-rate/driver-id), ports
    (alias/object.path/format.dsp/physical/terminal/extra), link edges
    as name:port pairs, and every metadata store's rows."""
    try:
        proc = subprocess.run(["pw-dump"], capture_output=True,
                              timeout=20)
        dump = json.loads(proc.stdout or b"[]")
    except (subprocess.TimeoutExpired, OSError, ValueError) as exc:
        return {"error": f"{type(exc).__name__}: {exc}"[:160]}
    clients, nodes, ports, links, meta = {}, {}, {}, [], {}
    for o in dump:
        t = str(o.get("type", ""))
        info = o.get("info") or {}
        props = info.get("props") or {}
        if t.endswith("Client"):
            clients[o["id"]] = {
                "name": props.get("client.name"),
                "api": props.get("client.api"),
                "application": props.get("application.name"),
                "binary": props.get("application.process.binary"),
                "pid": props.get("application.process.id")}
        elif t.endswith("Node"):
            nodes[o["id"]] = {
                "id": o["id"], "name": props.get("node.name"),
                "description": props.get("node.description"),
                "client_api": props.get("client.api"),
                "media_class": props.get("media.class"),
                "media_category": props.get("media.category"),
                "media_role": props.get("media.role"),
                "group": props.get("node.group"),
                "always_process": props.get("node.always-process"),
                "force_quantum": (str(props.get("node.force-quantum"))
                                  if props.get("node.force-quantum")
                                  is not None else None),
                "force_rate": (str(props.get("node.force-rate"))
                               if props.get("node.force-rate")
                               is not None else None),
                "driver": props.get("node.driver"),
                "driver_id": props.get("node.driver-id"),
                "priority_driver": props.get("priority.driver"),
                "state": info.get("state"),
                "serial": props.get("object.serial")}
        elif t.endswith("Port"):
            nid = info.get("node-id")
            if nid is None:
                nid = props.get("node.id")
            ports[o["id"]] = {
                "node_id": nid,
                "name": props.get("port.name"),
                "alias": props.get("port.alias"),
                "object_path": props.get("object.path"),
                "direction": props.get("port.direction"),
                "format_dsp": props.get("format.dsp"),
                "physical": props.get("port.physical"),
                "terminal": props.get("port.terminal"),
                "extra": props.get("port.extra")}
        elif t.endswith("Link"):
            links.append({"out_node": info.get("output-node-id"),
                          "out_port": info.get("output-port-id"),
                          "in_node": info.get("input-node-id"),
                          "in_port": info.get("input-port-id"),
                          "state": info.get("state")})
        elif t.endswith("Metadata"):
            name = props.get("metadata.name")
            if name:
                meta[name] = {str(m.get("key")): m.get("value")
                              for m in (info.get("metadata") or [])}
    by_name = {}
    for n in nodes.values():
        if n.get("name"):
            by_name[n["name"]] = n
    edges = []
    for l in links:
        op = ports.get(l["out_port"]) or {}
        ip = ports.get(l["in_port"]) or {}
        on = (nodes.get(l["out_node"]) or {}).get("name")
        inn = (nodes.get(l["in_node"]) or {}).get("name")
        edges.append({"out": f"{on}:{op.get('name')}",
                      "in": f"{inn}:{ip.get('name')}",
                      "state": l.get("state")})
    return {"clients": clients, "nodes": nodes, "ports": ports,
            "links": links, "edges": edges, "metadata": meta,
            "node_by_name": by_name}


def _jack_r95_edges_touching(g, tag):
    return sorted(e for e in (g.get("edges") or [])
                  if tag in (e.get("out") or "") or tag in (e.get("in") or ""))


def _jack_r95_port(g, node_name, port_name):
    nid = ((g.get("node_by_name") or {}).get(node_name) or {}).get("id")
    for pid, p in (g.get("ports") or {}).items():
        if p.get("node_id") == nid and p.get("name") == port_name:
            return {"port_id": pid, **p}
    return None


def _jack_r95_meta_rows(name):
    """`pw-metadata -n <name>` -> {key: {subject, value, type}}.
    pw-dump carries Metadata objects with a null info on this host, so
    the text surface is the only row witness (the boundary's receipts
    read it the same way); the `update: id:N key:'…' value:'…'
    type:'…'` row shape is parsed verbatim and the trailing
    `type:' type:' type:''` quirk some rows carry is tolerated."""
    rec = _jack_r95_run(["pw-metadata", "-n", name], 12.0, keep_raw=True)
    rows = {}
    for m in re.finditer(
            r"id:(\d+)\s+key:'((?:[^'\\]|\\.)*)'\s+"
            r"value:'((?:[^'\\]|\\.)*)'\s+type:'", rec.get("stdout_raw") or ""):
        rows[m.group(2)] = {"subject": int(m.group(1)),
                            "value": m.group(3)}
    rec["rows"] = rows
    rec["row_count"] = len(rows)
    return rec


def _jack_r95_settings():
    """The `settings` store as {key: str(value)} — the host-global
    quantum/rate lattice this family must never leave perturbed (only
    the disclosed global-buffer-size arm writes it)."""
    return {k: v["value"] for k, v in
            (_jack_r95_meta_rows("settings").get("rows") or {}).items()}


def _jack_r95_driver(g, node):
    """Resolve a node's node.driver-id to the driver node leaf."""
    did = (node or {}).get("driver_id")
    if did is None:
        return None
    return (g.get("nodes") or {}).get(did) or (g.get("nodes") or {}).get(str(did))


def _jack_r95_shape_slice(g, cname):
    """The concurrent witness for one JACK client run: its Client and
    Node leaves, its own port props, the links touching it, the
    resolved driver and the settings store."""
    client = next((c for c in (g.get("clients") or {}).values()
                   if c.get("name") == cname), None)
    node = (g.get("node_by_name") or {}).get(cname)
    ports = {}
    if node:
        nid = node.get("id")
        for pid, p in (g.get("ports") or {}).items():
            if p.get("node_id") == nid:
                ports[p.get("name")] = {"port_id": pid, **p}
    drv = _jack_r95_driver(g, node)
    return {"client": client, "node": node, "ports": ports,
            "links": _jack_r95_edges_touching(g, cname),
            "driver": drv, "settings": _jack_r95_settings()}


def _jack_r95_tone(path, seconds=1.6, amp_i16=None, freq=JACK_R95_TONE_HZ,
                   rate=JACK_R95_TONE_RATE):
    """Own int16 mono tone fixture (no foreign WAV is ever played to a
    probe-owned sink); the receipt carries the source's own int16 peak
    so the PW->JACK arm can arm SAMPLE identity, not a band."""
    amp = JACK_R95_AMP_I16 if amp_i16 is None else amp_i16
    n = int(round(seconds * rate))
    idx = np.arange(n, dtype=np.float64)
    wave_i16 = np.round(np.sin(2.0 * np.pi * freq * idx / rate)
                        * amp).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(wave_i16.tobytes())
    return {"path": str(path), "frames": n, "rate": rate,
            "freq_hz": freq, "amp_i16": int(amp),
            "peak_i16": int(np.max(np.abs(wave_i16.astype(np.int32)))),
            "sha256": _capture_r77_sha256(Path(path))}


def _jack_r95_wav_stats(path, freq=JACK_R95_TONE_HZ):
    """Own reader + own direct DFT (no foreign analyzer): the captured
    window's peak/rms/nonzero plus the 997 Hz energy. The window length
    is the boundary's falsified-hash artifact, so it is recorded here
    and the arms use ratios against the tone that produced it."""
    try:
        with wave.open(str(path)) as w:
            rate = w.getframerate()
            ch = w.getnchannels()
            sw = w.getsampwidth()
            n = w.getnframes()
            raw = w.readframes(n)
    except (wave.Error, OSError) as exc:
        return {"error": f"{type(exc).__name__}: {exc}"[:160]}
    if sw == 2:
        x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    elif sw == 4:
        x = np.frombuffer(raw, dtype="<f4").astype(np.float64)
    else:
        return {"error": f"unsupported sampwidth {sw}"}
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    idx = np.arange(x.size, dtype=np.float64)
    w0 = 2.0 * np.pi * freq / rate
    re_ = float(np.dot(x, np.cos(w0 * idx)))
    im_ = float(np.dot(x, np.sin(w0 * idx)))
    return {"frames": int(x.size), "rate": rate, "channels": ch,
            "sampwidth": sw, "peak": float(np.max(np.abs(x))),
            "rms": float(np.sqrt(np.mean(x * x))),
            "nonzero": int(np.count_nonzero(np.abs(x) > 1e-6)),
            "goertzel_mag2": re_ * re_ + im_ * im_,
            "sha256": _capture_r77_sha256(Path(path))}


def _jack_r95_symbols():
    """`nm -D --defined-only` over the host's only libjack -> the
    exported `jack_*` set (the boundary's 168 exports / 51 absent
    class)."""
    rec = _jack_r95_run(
        ["nm", "-D", "--defined-only", str(JACK_R95_LIBJACK)],
        40.0, keep_raw=True)
    rows = re.findall(r"^[0-9a-fA-F]+\s+(\S)\s+(jack_[A-Za-z0-9_]+)\s*$",
                      rec.get("stdout_raw") or "", re.M)
    syms = sorted({name for kind, name in rows if kind == "T"})
    rec["exports"] = syms
    rec["export_count"] = len(syms)
    rec["export_kinds"] = sorted({kind for kind, _ in rows})
    rec["absent"] = sorted(s for s in JACK_R95_ABSENT_SYMS
                           if s not in syms)
    rec["present"] = sorted(s for s in JACK_R95_PRESENT_SYMS
                            if s in syms)
    return rec


def _jack_r95_load_ns(name, desc=None, channels=1):
    """Load + gate one probe-owned null sink. `sink_properties` uses the
    SPACE-separated form (the boundary's F4 comma artifact: the comma
    form parses as ONE property and writes a stream-properties row),
    so state.restore-props parses to boolean false and no restore row
    is left behind; `device.description` sets node.description exactly
    (the addressing law's rendered name)."""
    props = "state.restore-props=false"
    if desc:
        props += f" device.description={desc}"
    leaf = _pwcat_r83_ns_load(
        name, (f"channels={channels}", f"sink_properties={props}"))
    leaf["field"] = "sink_name"
    leaf["value"] = name
    leaf["description"] = desc
    return leaf


def _jack_r95_family_lock():
    """Same-family exclusion at a FIXED lane path — the r84 F1 3-seat
    consensus (never $TMPDIR; cross-TMPDIR same-family runs must still
    exclude). A second --probe-jack-r95 waits HERE."""
    path = ROOT / "live" / "measure_audio-jack-r95.lock"
    try:
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    except OSError:
        return None
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        os.ftruncate(fd, 0)
        os.write(fd, f"pid={JACK_R95_PID} ns={JACK_R95_NS} "
                     f"role={JACK_R95_ROLE}\n".encode())
    except OSError:
        pass
    return fd


def _jack_r95_entry_head(probe):
    """Shared entry preamble: contention census, loadavg, the settings
    store (the host-global quantum/rate lattice), and the foreign-r95a
    census (another seat's residue is a witness, never a verdict)."""
    g = _jack_r95_graph()
    return {"probe": probe,
            "contention": _playback_r78_foreign_clients(),
            "foreign_r95a_nodes": sorted(
                n for n in (g.get("node_by_name") or {})
                if "r95a_" in n and f"_{JACK_R95_PID}" not in n),
            "foreign_r95a_clients": sorted(
                c.get("name") for c in (g.get("clients") or {}).values()
                if c.get("name") and "r95a_" in c["name"]
                and f"_{JACK_R95_PID}" not in c["name"]),
            "settings_at_start": _jack_r95_settings(),
            "loadavg": _alsapw_r84_loadavg()}


def _jack_r95_teardown(entry, failures, loads, procs=()):
    """Kill every tracked child process group first, then the
    name-verified unload of every own module, then the residue destroy:
    any surviving r95a_<pid>-tagged node is destroyed by id via pw-cli
    before the final sweep."""
    for proc in procs or ():
        if proc is None:
            continue
        _alsapw_r84_killpg(proc, signal.SIGTERM)
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _alsapw_r84_killpg(proc)
    for tag, leaf in (loads or {}).items():
        leaf = leaf or {}
        entry.setdefault("unloads", {})[tag] = \
            _pactlmon_r85_unload_own(
                leaf.get("module_id"),
                leaf.get("field", "sink_name"),
                leaf.get("value", tag))
    g = _jack_r95_graph()
    residual = sorted(
        (nid, n.get("name")) for nid, n in (g.get("nodes") or {}).items()
        if n.get("name") and f"r95a_{JACK_R95_PID}" in n["name"])
    if residual:
        entry["residual_destroy"] = [
            {"id": nid, "name": nm,
             **_jack_r95_run(["pw-cli", "destroy", nid], 8.0,
                             keep_chars=300)}
            for nid, nm in residual]
        time.sleep(0.4)
    sinks_now = _capture_r77_sink_names_strict()
    if sinks_now is None:
        entry["sinks_gone"] = "reader_error"
        entry.setdefault("coverage_blocked", []).append(
            "teardown: pactl sink reader failed — sinks_gone unmeasured")
    else:
        gone = {nm: nm not in sinks_now for nm in (loads or {})}
        entry["sinks_gone"] = gone
        if not all(gone.values()):
            failures.append(
                "teardown: probe sinks survived unload: "
                f"{[n for n, g2 in gone.items() if not g2]}")
    store = Path.home() / ".local/state/wireplumber" / "stream-properties"
    own_rows = None
    if store.exists():
        try:
            own_rows = sorted({
                ln.split("=", 1)[0] for ln in
                store.read_text(errors="replace").splitlines()
                if f"r95a_{JACK_R95_PID}" in ln})
        except OSError:
            own_rows = None
    entry["stream_properties_own_rows"] = own_rows
    if own_rows:
        failures.append(
            "teardown: stream-properties rows left by this seat: "
            f"{own_rows} — the space-separated sink_properties form "
            "must leave none")
    elif own_rows is None:
        entry.setdefault("coverage_blocked", []).append(
            "teardown: stream-properties store unreadable — the "
            "restore-row witness is unmeasured")
    names = _playback_r78_node_names()
    if names is None:
        entry["own_nodes_after"] = "reader_error"
        entry.setdefault("coverage_blocked", []).append(
            "teardown: node reader failed — own_nodes_after unmeasured")
    else:
        rest = sorted(n for n in names
                      if f"r95a_{JACK_R95_PID}" in n
                      or n in (loads or {}))
        entry["own_nodes_after"] = rest
        if rest:
            failures.append(
                f"teardown: r95a-tagged nodes survived: {rest}")


def _jack_r95_block(entry, failures, msg, loads=None, procs=()):
    """The named coverage block: kill children, unload anything loaded,
    record the block (a missing tool/compiler/daemon is a block, never
    a silent green)."""
    for proc in procs or ():
        if proc is None:
            continue
        _alsapw_r84_killpg(proc, signal.SIGTERM)
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _alsapw_r84_killpg(proc)
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


def _jack_r95_eq(failures, lname, what, got, want):
    if got != want:
        failures.append(
            f"{lname}: {what} = {got!r}, want {want!r}")


def _jack_r95_band(failures, lname, what, got, lo, hi):
    if got is None or not (lo <= got <= hi):
        failures.append(
            f"{lname}: {what} = {got!r}, want [{lo}, {hi}]")


def _jack_r95_true(failures, lname, what, got):
    if got is not True:
        failures.append(f"{lname}: {what} = {got!r}, want true")


def jack_surface_r95_entry():
    """Availability + the JACK client as a PW citizen: the version
    quadruple and the export class, the client/node/port projection
    (alias triple, format.dsp, Physical/Terminal survive, CanMonitor
    does not), the monitor API as local bookkeeping, zero autoconnect,
    the whole-graph census, and the always-process liveness law with no
    seat driver (the boundary's F1: the node itself keeps the fallback
    driver running)."""
    failures, legs = [], {}
    entry = _jack_r95_entry_head("r95a JACK availability + citizen shape")
    tools = {t: shutil.which(t) for t in
             ("gcc", "jackd", "jack_lsp", "jack_connect", "pw-jack",
              "pactl", "pw-dump", "pw-cli", "pw-play", "pw-record",
              "pw-link", "nm", "pacman")}
    entry["tools"] = tools
    missing = [t for t in ("gcc", "pw-jack", "pactl", "pw-dump",
                           "pw-play", "pw-record", "pw-link", "nm")
               if not tools[t]]
    if missing:
        return _jack_r95_block(entry, failures,
                               f"missing tools: {missing}")
    loads, procs = {}, []
    try:
        with tempfile.TemporaryDirectory(prefix="r95a-surf-") as tmp:
            probe, build = _jack_r95_build(tmp)
            entry["build"] = build
            if probe is None:
                return _jack_r95_block(
                    entry, failures,
                    f"fixture build failed: {build.get('rc')} "
                    f"{build.get('stderr_tail')}")
            # --- a_avail: the host has no JACK server, only the lib.
            leg = {"jackd": tools["jackd"], "jack_lsp": tools["jack_lsp"],
                   "jack_connect": tools["jack_connect"],
                   "pw_jack": tools["pw-jack"],
                   "libjack_path": str(JACK_R95_LIBJACK),
                   "libjack_sha256": _capture_r77_sha256(JACK_R95_LIBJACK)}
            leg["pacman"] = _jack_r95_run(
                ["pacman", "-Q", "pipewire-jack"], 15.0, keep_chars=200)
            leg["symbols"] = _jack_r95_symbols()
            leg["version_probe"] = _jack_r95_probe(
                probe, ["info", "0.2"], 10.0,
                env=_jack_r95_env(f"{JACK_R95_PREFIX}_avail"))
            legs["a_avail"] = leg
            vj = (leg["version_probe"].get("json") or {})
            if tools["jackd"] is not None or tools["jack_lsp"] is not None \
                    or tools["jack_connect"] is not None:
                failures.append(
                    "a_avail: a JACK server binary is present — the "
                    "no-server premise fails")
            _jack_r95_true(failures, "a_avail", "pw-jack present",
                           tools["pw-jack"] is not None)
            pq = leg["pacman"]
            _jack_r95_eq(failures, "a_avail", "pacman rc",
                         pq.get("exit_code"), 0)
            if "pipewire-jack 1:1.6.8" not in (pq.get("stdout") or ""):
                failures.append(
                    f"a_avail: pacman version = "
                    f"{(pq.get('stdout') or '').strip()!r} — the "
                    "version-pinned premise fails")
            _jack_r95_eq(failures, "a_avail", "version_ints",
                         vj.get("version_ints"), [3, 1, 6, 8])
            if "PipeWire 1.6.8" not in (vj.get("version") or ""):
                failures.append(
                    f"a_avail: version = {vj.get('version')!r} — the "
                    "PW-backed version string fails")
            _jack_r95_eq(failures, "a_avail", "export_count",
                         leg["symbols"].get("export_count"), 168)
            if leg["symbols"].get("absent") != sorted(JACK_R95_ABSENT_SYMS):
                failures.append(
                    "a_avail: absent class = "
                    f"{leg['symbols'].get('absent')} — the declared-"
                    "but-unexported set fails")
            if leg["symbols"].get("present") != sorted(JACK_R95_PRESENT_SYMS):
                failures.append(
                    "a_avail: present class = "
                    f"{leg['symbols'].get('present')} — the exported "
                    "class fails")

            # --- s_shape: the citizen shape with a probe-owned sink
            # present but NOT linked (no autoconnect).
            leaf = _jack_r95_load_ns(JACK_R95_NS, desc=JACK_R95_DS)
            loads = {JACK_R95_NS: leaf}
            if leaf.get("module_id") is None:
                return _jack_r95_block(
                    entry, failures,
                    f"probe null sink {JACK_R95_NS} never enumerated",
                    loads, procs)
            cname = f"{JACK_R95_PREFIX}_shape"
            legs["s_shape"] = _jack_r95_probe(
                probe, ["shape", "2.4"], 14.0,
                env=_jack_r95_env(cname),
                mid=lambda: _jack_r95_shape_slice(
                    _jack_r95_graph(), cname), mid_at=0.9)
            l = legs["s_shape"]
            j = l.get("json") or {}
            mid = l.get("mid") or {}
            l["mid"] = mid
            l["ns_load"] = {"module_id": leaf.get("module_id"),
                            "sink_seen": leaf.get("sink_seen"),
                            "monitor_seen": leaf.get("monitor_seen")}
            _jack_r95_eq(failures, "s_shape", "rc", l.get("exit_code"), 0)
            _jack_r95_eq(failures, "s_shape", "status", j.get("status"), 0)
            pnames = j.get("ports") or {}
            for tag in ("out", "in", "outp", "outt", "outm"):
                _jack_r95_eq(failures, "s_shape", f"port name {tag}",
                             pnames.get(tag), f"{cname}:{tag}")
            for tag, want in (("out", 2), ("in", 1), ("outp", 6),
                              ("outt", 18), ("outm", 2)):
                _jack_r95_eq(
                    failures, "s_shape", f"jack_port_flags {tag}",
                    (j.get(f"lat_{tag}") or {}).get("flags"), want)
            _jack_r95_eq(failures, "s_shape", "port type",
                         (j.get("lat_out") or {}).get("type"),
                         "32 bit float mono audio")
            _jack_r95_eq(failures, "s_shape", "out_connected",
                         j.get("out_connected"), 0)
            _jack_r95_eq(failures, "s_shape", "out_connections",
                         j.get("out_connections"), [])
            _jack_r95_eq(failures, "s_shape", "request_monitor_rc",
                         j.get("request_monitor_rc"), 0)
            _jack_r95_eq(failures, "s_shape", "monitoring_input",
                         j.get("monitoring_input"), 1)
            _jack_r95_eq(failures, "s_shape", "ensure_monitor_rc",
                         j.get("ensure_monitor_rc"), 0)
            _jack_r95_eq(failures, "s_shape", "monitoring_input_in",
                         j.get("monitoring_input_in"), 0)
            census = j.get("census") or {}
            _jack_r95_band(failures, "s_shape", "pattern_r95a",
                           census.get("pattern_r95a"), 5, 100)
            _jack_r95_eq(
                failures, "s_shape", "census own ports",
                sorted(p for p in (census.get("pattern_r95a_list") or [])
                       if p.startswith(f"{cname}:")),
                sorted(f"{cname}:{t}" for t in
                       ("out", "in", "outp", "outt", "outm")))
            for r in (j.get("resolve") or []):
                _jack_r95_true(failures, "s_shape",
                               f"resolve {r.get('name')}", r.get("found"))
            client = mid.get("client") or {}
            node = mid.get("node") or {}
            _jack_r95_eq(failures, "s_shape", "client.api",
                         client.get("api"), "jack")
            _jack_r95_eq(failures, "s_shape", "node.name",
                         node.get("name"), cname)
            _jack_r95_eq(failures, "s_shape", "node.description",
                         node.get("description"), cname)
            _jack_r95_eq(failures, "s_shape", "node.group",
                         node.get("group"), "group.dsp.0")
            _jack_r95_eq(failures, "s_shape", "media.category",
                         node.get("media_category"), "Duplex")
            _jack_r95_eq(failures, "s_shape", "media.role",
                         node.get("media_role"), "DSP")
            _jack_r95_true(failures, "s_shape", "node.always-process",
                           node.get("always_process"))
            _jack_r95_eq(failures, "s_shape", "media.class absent",
                         node.get("media_class"), None)
            own = mid.get("ports") or {}
            for tag, path_idx in (("out", 0), ("outp", 1), ("outt", 2),
                                  ("outm", 3)):
                p = own.get(tag) or {}
                _jack_r95_eq(failures, "s_shape", f"PW port.alias {tag}",
                             p.get("alias"), f"{cname}:{tag}")
                _jack_r95_eq(
                    failures, "s_shape", f"PW object.path {tag}",
                    p.get("object_path"), f"{cname}:output_{path_idx}")
                _jack_r95_eq(failures, "s_shape", f"PW direction {tag}",
                             p.get("direction"), "out")
                _jack_r95_eq(failures, "s_shape", f"PW format.dsp {tag}",
                             p.get("format_dsp"),
                             "32 bit float mono audio")
            pin = own.get("in") or {}
            _jack_r95_eq(failures, "s_shape", "PW port.alias in",
                         pin.get("alias"), f"{cname}:in")
            _jack_r95_eq(failures, "s_shape", "PW direction in",
                         pin.get("direction"), "in")
            _jack_r95_true(failures, "s_shape", "PW port.physical outp",
                           (own.get("outp") or {}).get("physical"))
            _jack_r95_true(failures, "s_shape", "PW port.terminal outt",
                           (own.get("outt") or {}).get("terminal"))
            _jack_r95_eq(failures, "s_shape", "PW port.physical outm",
                         (own.get("outm") or {}).get("physical"), None)
            _jack_r95_eq(failures, "s_shape", "PW port.terminal outm",
                         (own.get("outm") or {}).get("terminal"), None)
            _jack_r95_eq(failures, "s_shape", "PW port.extra outm",
                         (own.get("outm") or {}).get("extra"), None)
            _jack_r95_eq(failures, "s_shape", "links while running",
                         mid.get("links"), [])
            drv = mid.get("driver") or {}
            l["driver_name"] = drv.get("name")
            l["driver_priority"] = drv.get("priority_driver")
            if drv.get("name") == "Dummy-Driver":
                _jack_r95_true(failures, "s_shape",
                               "Dummy-Driver node.driver",
                               drv.get("driver"))
                _jack_r95_eq(failures, "s_shape",
                             "Dummy-Driver priority.driver",
                             drv.get("priority_driver"), 200000)
            else:
                entry.setdefault("coverage_blocked", []).append(
                    f"s_shape: driver resolved to {drv.get('name')!r} "
                    "— foreign driver confound, the fallback-driver "
                    "props are unmeasured")
            ns_port = _jack_r95_port(_jack_r95_graph(), JACK_R95_NS,
                                     "playback_MONO")
            l["ns_port"] = {"alias": (ns_port or {}).get("alias"),
                            "object_path": (ns_port or {}).get("object_path")}
            _jack_r95_eq(failures, "s_shape", "ns rendered alias",
                         (ns_port or {}).get("alias"),
                         f"{JACK_R95_DS}:playback_MONO")
            _jack_r95_eq(failures, "s_shape", "ns object.path",
                         (ns_port or {}).get("object_path"),
                         f"{JACK_R95_NS}:playback_0")

            # --- s_liveness: no seat sink, no links, the always-process
            # node must still be scheduled (the boundary's F1).
            entry.setdefault("unloads", {})[JACK_R95_NS] = \
                _pactlmon_r85_unload_own(
                    leaf.get("module_id"), "sink_name", JACK_R95_NS)
            loads = {}
            sinks_now = _capture_r77_sink_names_strict()
            entry["ns_gone_after_unload"] = (
                None if sinks_now is None else JACK_R95_NS not in sinks_now)
            if entry["ns_gone_after_unload"] is False:
                failures.append(
                    f"s_shape: probe sink {JACK_R95_NS} survived the "
                    "name-verified unload")
            cname2 = f"{JACK_R95_PREFIX}_live"
            legs["s_liveness"] = _jack_r95_probe(
                probe, ["tone", "1.8", "0", "0", ""], 12.0,
                env=_jack_r95_env(cname2),
                mid=lambda: _jack_r95_shape_slice(
                    _jack_r95_graph(), cname2), mid_at=0.7)
            l = legs["s_liveness"]
            j = l.get("json") or {}
            mid = l.get("mid") or {}
            l["mid"] = mid
            drv = mid.get("driver") or {}
            l["driver_name"] = drv.get("name")
            _jack_r95_eq(failures, "s_liveness", "rc",
                         l.get("exit_code"), 0)
            _jack_r95_band(failures, "s_liveness", "cb",
                           j.get("cb"), 30, 100000)
            _jack_r95_true(
                failures, "s_liveness", "frames advance",
                (j.get("last_last_frame") or 0)
                > (j.get("first_last_frame") or 0))
            if drv.get("name") == "Dummy-Driver":
                _jack_r95_true(failures, "s_liveness",
                               "Dummy-Driver node.driver",
                               drv.get("driver"))
            else:
                entry.setdefault("coverage_blocked", []).append(
                    "s_liveness: driver resolved to "
                    f"{drv.get('name')!r} — foreign driver confound")
            _jack_r95_eq(failures, "s_liveness", "links",
                         mid.get("links"), [])
        entry["legs"] = legs
        entry["failures"] = failures
        _jack_r95_teardown(entry, failures, loads, procs)
    except Exception as exc:                      # never lose the receipt
        entry.setdefault("coverage_blocked", []).append(
            f"entry aborted: {type(exc).__name__}: {exc}"[:200])
        entry["legs"] = legs
        entry["failures"] = failures
    return entry


def jack_addr_r95_entry():
    """The addressing law: jack_connect resolves the RENDERED
    `<node.description>:<port>` name; the native `<node.name>:<port>`
    form fails (rc 22, no link) unless description == node.name (the
    boundary's F6 corner); with jack.fill-aliases the `object.path`
    alias resolves. Both domains are witnessed (the probe's own
    connection list + a concurrent pw-dump link edge)."""
    failures, legs = [], {}
    entry = _jack_r95_entry_head("r95a JACK cross-domain addressing")
    missing = [t for t in ("gcc", "pactl", "pw-dump", "pw-cli")
               if not shutil.which(t)]
    if missing:
        return _jack_r95_block(entry, failures, f"missing tools: {missing}")
    loads, procs = {}, []
    try:
        with tempfile.TemporaryDirectory(prefix="r95a-addr-") as tmp:
            probe, build = _jack_r95_build(tmp)
            entry["build"] = build
            if probe is None:
                return _jack_r95_block(
                    entry, failures,
                    f"fixture build failed: {build.get('rc')}")
            for name, desc in ((JACK_R95_NS, JACK_R95_DS),
                               (JACK_R95_CORNER, JACK_R95_CORNER)):
                leaf = _jack_r95_load_ns(name, desc=desc)
                loads[name] = leaf
                if leaf.get("module_id") is None:
                    return _jack_r95_block(
                        entry, failures,
                        f"probe null sink {name} never enumerated",
                        loads, procs)
            cname = f"{JACK_R95_PREFIX}_xc"
            src = f"{cname}:out"
            # conns_want is the CANONICAL rendered name the connection
            # list reports — the fill-aliases arm addresses the port by
            # its object.path alias but the graph reports the canonical
            # name back (measured here; the alias resolves, it does not
            # rename).
            arms = (
                ("x_rendered", f"{JACK_R95_DS}:playback_MONO", None, True,
                 0, f"{JACK_R95_NS}:playback_MONO",
                 [f"{JACK_R95_DS}:playback_MONO"]),
                ("x_native", f"{JACK_R95_NS}:playback_MONO", None, False,
                 22, None, []),
                ("x_fillalias", f"{JACK_R95_NS}:playback_0",
                 {"PIPEWIRE_PROPS": "{ jack.fill-aliases = true }"},
                 True, 0, f"{JACK_R95_NS}:playback_MONO",
                 [f"{JACK_R95_DS}:playback_MONO"]),
                ("x_corner", f"{JACK_R95_CORNER}:playback_MONO", None,
                 True, 0, f"{JACK_R95_CORNER}:playback_MONO",
                 [f"{JACK_R95_CORNER}:playback_MONO"]),
            )
            for lname, dst, env_extra, found, rc, edge_in, conns_want in arms:
                legs[lname] = _jack_r95_probe(
                    probe, ["xconnect", src, dst, "0.9"], 12.0,
                    env=_jack_r95_env(cname, env_extra),
                    mid=lambda: {"edges": _jack_r95_edges_touching(
                        _jack_r95_graph(), cname)}, mid_at=0.6)
                l = legs[lname]
                j = l.get("json") or {}
                l["dst"] = dst
                _jack_r95_eq(failures, lname, "rc", l.get("exit_code"), 0)
                _jack_r95_eq(failures, lname, "src_found",
                             j.get("src_found"), True)
                _jack_r95_eq(failures, lname, "dst_found",
                             j.get("dst_found"), found)
                _jack_r95_eq(failures, lname, "connect_rc",
                             j.get("connect_rc"), rc)
                _jack_r95_eq(failures, lname, "connected",
                             j.get("connected"), 1 if found else 0)
                _jack_r95_eq(failures, lname, "conns",
                             j.get("conns"), conns_want)
                if dst != conns_want[0] if conns_want else False:
                    l["alias_addressed"] = dst
                    l["conns_canonical"] = conns_want
                edges = sorted(
                    e.get("out") + "|->" + e.get("in")
                    for e in ((l.get("mid") or {}).get("edges") or []))
                l["edges"] = edges
                want = [f"{src}|->{edge_in}"] if edge_in else []
                _jack_r95_eq(failures, lname, "pw link edges",
                             edges, want)
            l = legs["x_fillalias"]
            j = l.get("json") or {}
            _jack_r95_eq(failures, "x_fillalias", "dst_type",
                         j.get("dst_type"), "32 bit float mono audio")
            g = _jack_r95_graph()
            corner = (g.get("node_by_name") or {}).get(JACK_R95_CORNER) or {}
            ns = (g.get("node_by_name") or {}).get(JACK_R95_NS) or {}
            legs["x_corner"]["corner_description"] = corner.get("description")
            legs["x_corner"]["corner_name"] = corner.get("name")
            legs["x_rendered"]["ns_description"] = ns.get("description")
            legs["x_rendered"]["ns_name"] = ns.get("name")
            _jack_r95_eq(failures, "x_corner", "corner description",
                         corner.get("description"), JACK_R95_CORNER)
            _jack_r95_eq(failures, "x_corner", "corner name",
                         corner.get("name"), JACK_R95_CORNER)
            if ns.get("description") == ns.get("name"):
                entry.setdefault("coverage_blocked", []).append(
                    "x_rendered/x_native: the driver sink's description "
                    "equals its name — the two forms coincide")
        entry["legs"] = legs
        entry["failures"] = failures
        _jack_r95_teardown(entry, failures, loads, procs)
    except Exception as exc:
        entry.setdefault("coverage_blocked", []).append(
            f"entry aborted: {type(exc).__name__}: {exc}"[:200])
        entry["legs"] = legs
        entry["failures"] = failures
    return entry


def jack_bytes_r95_entry():
    """Both byte witnesses. JACK->PW: the probe's 997 Hz tone is linked
    into a probe-owned null sink and captured on its monitor by
    pw-record; the capture's peak and its 997 Hz energy are armed
    against the tone the probe actually generated (cb x bufsize) — the
    whole-file hash/rms is recorded, never armed (the boundary's F2).
    PW->JACK: an own int16 tone is played by pw-play and linked into
    the probe's input; the probe's own input analysis must return the
    source WAV's int16 peak EXACTLY (peak/32768) and its 997 Hz energy
    must track the nonzero window."""
    failures, legs = [], {}
    entry = _jack_r95_entry_head("r95a JACK byte path (both directions)")
    missing = [t for t in ("gcc", "pactl", "pw-dump", "pw-cli",
                           "pw-record", "pw-play", "pw-link")
               if not shutil.which(t)]
    if missing:
        return _jack_r95_block(entry, failures, f"missing tools: {missing}")
    loads, procs = {}, []
    try:
        with tempfile.TemporaryDirectory(prefix="r95a-bytes-") as tmp:
            probe, build = _jack_r95_build(tmp)
            entry["build"] = build
            if probe is None:
                return _jack_r95_block(
                    entry, failures,
                    f"fixture build failed: {build.get('rc')}")
            leaf = _jack_r95_load_ns(JACK_R95_NS, desc=JACK_R95_DS)
            loads = {JACK_R95_NS: leaf}
            if leaf.get("module_id") is None:
                return _jack_r95_block(
                    entry, failures,
                    f"probe null sink {JACK_R95_NS} never enumerated",
                    loads, procs)

            # --- b_jack2pw
            cap = Path(tmp) / "jack2pw.wav"
            rec_tag = f"{JACK_R95_PREFIX}_rec"
            cname = f"{JACK_R95_PREFIX}_j2p"
            try:
                recorder = subprocess.Popen(
                    ["pw-record", "-P", "stream.capture.sink=true",
                     "-P", f"node.name={rec_tag}", "--target",
                     JACK_R95_NS, "--channels", "1",
                     "--rate", str(JACK_R95_TONE_RATE), str(cap)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                    stdin=subprocess.DEVNULL, start_new_session=True)
            except OSError as exc:
                recorder = None
                entry["recorder_error"] = str(exc)[:160]
            procs.append(recorder)
            linked = False
            if recorder is not None:
                deadline = time.monotonic() + 6.0
                while time.monotonic() < deadline:
                    g = _jack_r95_graph()
                    if _jack_r95_edges_touching(g, rec_tag):
                        linked = True
                        break
                    time.sleep(0.25)
            legs["b_jack2pw"] = _jack_r95_probe(
                probe,
                ["tone", "1.8", "0", "0",
                 f"{JACK_R95_DS}:playback_MONO"], 12.0,
                env=_jack_r95_env(cname),
                mid=lambda: {"edges": _jack_r95_edges_touching(
                    _jack_r95_graph(), cname)}, mid_at=1.1)
            l = legs["b_jack2pw"]
            j = l.get("json") or {}
            l["recorder_linked"] = linked
            l["capture"] = None
            if recorder is not None:
                _alsapw_r84_killpg(recorder, signal.SIGTERM)
                try:
                    recorder.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    _alsapw_r84_killpg(recorder)
                if recorder.stderr is not None:
                    try:
                        recorder.stderr.read()
                    except (OSError, ValueError):
                        pass
                time.sleep(0.2)
                l["capture"] = _jack_r95_wav_stats(cap)
            _jack_r95_eq(failures, "b_jack2pw", "rc",
                         l.get("exit_code"), 0)
            _jack_r95_eq(failures, "b_jack2pw", "conn_rc",
                         j.get("conn_rc"), 0)
            edges = sorted(
                e.get("out") + "|->" + e.get("in")
                for e in ((l.get("mid") or {}).get("edges") or []))
            l["edges"] = edges
            _jack_r95_eq(
                failures, "b_jack2pw", "pw link edge", edges,
                [f"{cname}:out|->{JACK_R95_NS}:playback_MONO"])
            cap_st = l.get("capture") or {}
            _jack_r95_true(failures, "b_jack2pw", "recorder linked",
                           linked)
            n_tone = (j.get("cb") or 0) * (j.get("bufsize_live") or 0)
            l["n_tone"] = n_tone
            l["ideal_mag2"] = (0.25 * n_tone) ** 2
            _jack_r95_band(failures, "b_jack2pw", "capture peak",
                           cap_st.get("peak"), 0.4985, 0.5005)
            # the capture window is set by process start/stop timing
            # (the boundary's F2): arm the tone's own fraction instead
            # of an absolute rms/frames value.
            if cap_st.get("rms") is not None:
                _jack_r95_band(
                    failures, "b_jack2pw", "rms ratio to sine ideal",
                    cap_st["rms"] / (0.5 / 2 ** 0.5), 0.80, 1.02)
            if cap_st.get("frames"):
                _jack_r95_band(
                    failures, "b_jack2pw", "capture nonzero fraction",
                    (cap_st.get("nonzero") or 0) / cap_st["frames"],
                    0.70, 1.0)
            if n_tone:
                _jack_r95_band(
                    failures, "b_jack2pw", "mag2 ratio",
                    (cap_st.get("goertzel_mag2") or 0)
                    / l["ideal_mag2"], 0.90, 1.03)
            else:
                failures.append(
                    "b_jack2pw: cb x bufsize_live = 0 — the tone "
                    "window is unmeasurable")
            _jack_r95_band(failures, "b_jack2pw", "capture frames",
                           cap_st.get("frames"), 60000, 300000)
            # teardown of the driver sink before the reverse leg
            entry.setdefault("unloads", {})[JACK_R95_NS] = \
                _pactlmon_r85_unload_own(
                    leaf.get("module_id"), "sink_name", JACK_R95_NS)
            loads = {}
            sinks_now = _capture_r77_sink_names_strict()
            entry["ns_gone_after_unload"] = (
                None if sinks_now is None else JACK_R95_NS not in sinks_now)
            if entry["ns_gone_after_unload"] is False:
                failures.append(
                    f"b_jack2pw: probe sink {JACK_R95_NS} survived the "
                    "name-verified unload")

            # --- b_pw2jack
            tone = _jack_r95_tone(Path(tmp) / "tone997.wav", 1.5)
            cname2 = f"{JACK_R95_PREFIX}_p2j"
            play_tag = f"{JACK_R95_PREFIX}_play"
            holder = {}

            def mid():
                g = _jack_r95_graph()
                try:
                    player = subprocess.Popen(
                        ["pw-play", "-P", "node.autoconnect=false",
                         "-P", f"node.name={play_tag}",
                         "-P", f"media.role={JACK_R95_ROLE}",
                         "--channels", "1",
                         "--rate", str(JACK_R95_TONE_RATE), str(tone["path"])],
                        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                        stdin=subprocess.DEVNULL, start_new_session=True)
                except OSError as exc:
                    return {"error": str(exc)[:160],
                            "edges": _jack_r95_edges_touching(g, cname2)}
                holder["player"] = player
                link_rc, linked = None, False
                deadline = time.monotonic() + 5.0
                while time.monotonic() < deadline:
                    if player.poll() is not None:
                        break
                    link_rc = _jack_r95_run(
                        ["pw-link", f"{play_tag}:output_MONO",
                         f"{cname2}:in"], 6.0, keep_chars=200)
                    if link_rc.get("exit_code") == 0:
                        linked = True
                        break
                    time.sleep(0.25)
                time.sleep(1.1)
                edges_live = _jack_r95_edges_touching(
                    _jack_r95_graph(), cname2)
                _alsapw_r84_killpg(player, signal.SIGTERM)
                try:
                    player.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    _alsapw_r84_killpg(player)
                return {"edges": edges_live,
                        "edges_after_exit": _jack_r95_edges_touching(
                            _jack_r95_graph(), cname2),
                        "link_rc": link_rc, "linked": linked,
                        "player_rc": player.returncode}

            legs["b_pw2jack"] = _jack_r95_probe(
                probe, ["tone", "2.6", "0", "0", ""], 16.0,
                env=_jack_r95_env(cname2), mid=mid, mid_at=1.0)
            l = legs["b_pw2jack"]
            j = l.get("json") or {}
            l["tone_source"] = tone
            m = l.get("mid") or {}
            l["mid"] = m
            procs.append(holder.get("player"))
            _jack_r95_eq(failures, "b_pw2jack", "rc",
                         l.get("exit_code"), 0)
            _jack_r95_eq(failures, "b_pw2jack", "tone peak_i16",
                         tone.get("peak_i16"), JACK_R95_AMP_I16)
            _jack_r95_true(failures, "b_pw2jack", "pw-link rc 0",
                           m.get("linked"))
            expected = tone["peak_i16"] / 32768.0
            l["expected_peak"] = expected
            if j.get("in_peak") is None or \
                    abs(j.get("in_peak") - expected) > 1e-9:
                failures.append(
                    f"b_pw2jack: in_peak = {j.get('in_peak')!r}, want "
                    f"the source int16 peak/32768 = {expected!r} — the "
                    "sample-exact copy law fails")
            # the player is linked AFTER it starts, so the head of the
            # tone never reaches the input: arm a substantial fraction
            # of the 1.5 s source (72000 samples), never an exact count.
            _jack_r95_band(failures, "b_pw2jack", "in_nonzero",
                           j.get("in_nonzero"), 30000, 75000)
            n_in = j.get("in_nonzero") or 0
            l["ideal_mag2"] = (0.25 * n_in) ** 2
            if n_in:
                _jack_r95_band(
                    failures, "b_pw2jack", "mag2 ratio",
                    (j.get("goertzel_mag2") or 0) / l["ideal_mag2"],
                    0.985, 1.005)
            else:
                failures.append(
                    "b_pw2jack: in_nonzero = 0 — no tone reached the "
                    "JACK input")
            _jack_r95_band(failures, "b_pw2jack", "cb_in_nonzero",
                           j.get("cb_in_nonzero"), 10, 100000)
            edges = sorted(
                e.get("out") + "|->" + e.get("in")
                for e in (m.get("edges") or []))
            l["edges"] = edges
            _jack_r95_eq(
                failures, "b_pw2jack", "pw link edge", edges,
                [f"{play_tag}:output_MONO|->{cname2}:in"])
        entry["legs"] = legs
        entry["failures"] = failures
        _jack_r95_teardown(entry, failures, loads, procs)
    except Exception as exc:
        entry.setdefault("coverage_blocked", []).append(
            f"entry aborted: {type(exc).__name__}: {exc}"[:200])
        entry["legs"] = legs
        entry["failures"] = failures
    return entry


def jack_quantum_r95_entry():
    """The period-size lattice. Per-client default: an inactive
    jack_set_buffer_size is invisible to jack_get_buffer_size, the
    activated value lands as node.force-quantum and moves the graph
    quantum for a second client; a live set delivers the buffer-size
    callback. Env/wrapper: PIPEWIRE_QUANTUM=q/rate and `pw-jack -p q`
    are the same node props (and the rate axis runs the client at
    44100 despite clock.allowed-rates=[48000]). The global arm is the
    ONE host-state mutation this family performs: with
    jack.global-buffer-size=true the same call writes the `settings`
    clock.force-quantum metadata, which outlives the writer and is
    restored by jack_set_buffer_size(1) -> "0" (verified in-entry, and
    re-verified by teardown)."""
    failures, legs = [], {}
    entry = _jack_r95_entry_head("r95a JACK period-size / quantum lattice")
    missing = [t for t in ("gcc", "pactl", "pw-dump", "pw-cli", "pw-jack")
               if not shutil.which(t)]
    if missing:
        return _jack_r95_block(entry, failures, f"missing tools: {missing}")
    loads, procs = {}, []
    settings_before = entry.get("settings_at_start") or {}
    try:
        with tempfile.TemporaryDirectory(prefix="r95a-quant-") as tmp:
            probe, build = _jack_r95_build(tmp)
            entry["build"] = build
            if probe is None:
                return _jack_r95_block(
                    entry, failures,
                    f"fixture build failed: {build.get('rc')}")
            leaf = _jack_r95_load_ns(JACK_R95_NS, desc=JACK_R95_DS)
            loads = {JACK_R95_NS: leaf}
            if leaf.get("module_id") is None:
                return _jack_r95_block(
                    entry, failures,
                    f"probe null sink {JACK_R95_NS} never enumerated",
                    loads, procs)

            def node_slice(cname, tag="q"):
                def hook():
                    g = _jack_r95_graph()
                    n = (g.get("node_by_name") or {}).get(cname) or {}
                    return {tag: {"force_quantum": n.get("force_quantum"),
                                  "force_rate": n.get("force_rate"),
                                  "state": n.get("state")},
                            "settings": _jack_r95_settings()}
                return hook

            # --- q_default: inactive set invisible, activated lands.
            cname = f"{JACK_R95_PREFIX}_q"
            legs["q_default"] = _jack_r95_probe(
                probe, ["bufsize", "1.4", "2048", "0"], 10.0,
                env=_jack_r95_env(cname), mid=node_slice(cname),
                mid_at=0.7)
            l = legs["q_default"]
            j = l.get("json") or {}
            _jack_r95_eq(failures, "q_default", "set_inactive_rc",
                         j.get("set_inactive_rc"), 0)
            _jack_r95_eq(failures, "q_default",
                         "inactive read-back unchanged",
                         j.get("bufsize_after_set_inactive"),
                         j.get("bufsize_inactive"))
            _jack_r95_eq(failures, "q_default", "activated",
                         j.get("bufsize_activated"), 2048)
            _jack_r95_eq(failures, "q_default", "node.force-quantum",
                         ((l.get("mid") or {}).get("q") or {})
                         .get("force_quantum"), "2048")
            _jack_r95_eq(failures, "q_default", "settings force-quantum",
                         ((l.get("mid") or {}).get("settings") or {})
                         .get("clock.force-quantum"), "0")

            # --- q_live: the live set delivers the callback.
            cname = f"{JACK_R95_PREFIX}_ql"
            legs["q_live"] = _jack_r95_probe(
                probe, ["bufsize", "2.6", "2048", "512"], 12.0,
                env=_jack_r95_env(cname),
                mid=node_slice(cname, "q2"), mid_at=3.0)
            l = legs["q_live"]
            j = l.get("json") or {}
            _jack_r95_eq(failures, "q_live", "set_active_rc",
                         j.get("set_active_rc"), 0)
            _jack_r95_eq(failures, "q_live", "bufsize after live set",
                         j.get("bufsize_after_set_active"), 512)
            _jack_r95_true(
                failures, "q_live", "buffer-size callback fired",
                (j.get("bufsize_cbs_after") or 0)
                > (j.get("bufsize_cbs") or 0))
            _jack_r95_eq(failures, "q_live", "last_bufsize_cb_after",
                         j.get("last_bufsize_cb_after"), 512)
            _jack_r95_eq(failures, "q_live", "node.force-quantum after",
                         ((l.get("mid") or {}).get("q2") or {})
                         .get("force_quantum"), "512")

            # --- q_cross: a second client sees the changed value.
            cname = f"{JACK_R95_PREFIX}_qa"
            cname_b = f"{JACK_R95_PREFIX}_qb"

            def cross_mid():
                rec = _jack_r95_probe(
                    probe, ["info", "0.5"], 8.0,
                    env=_jack_r95_env(cname_b))
                g = _jack_r95_graph()
                n = (g.get("node_by_name") or {}).get(cname) or {}
                return {"client_b": rec.get("json"),
                        "client_b_rc": rec.get("exit_code"),
                        "a_force_quantum": n.get("force_quantum"),
                        "settings": _jack_r95_settings()}

            legs["q_cross"] = _jack_r95_probe(
                probe, ["bufsize", "2.8", "2048", "0"], 12.0,
                env=_jack_r95_env(cname), mid=cross_mid, mid_at=1.5)
            l = legs["q_cross"]
            j = l.get("json") or {}
            m = l.get("mid") or {}
            _jack_r95_eq(failures, "q_cross", "a activated",
                         j.get("bufsize_activated"), 2048)
            _jack_r95_eq(failures, "q_cross", "a force-quantum",
                         m.get("a_force_quantum"), "2048")
            _jack_r95_eq(failures, "q_cross", "second client rc",
                         m.get("client_b_rc"), 0)
            _jack_r95_eq(
                failures, "q_cross", "second client bufsize_active",
                (m.get("client_b") or {}).get("bufsize_active"), 2048)
            _jack_r95_eq(failures, "q_cross", "settings force-quantum",
                         (m.get("settings") or {}).get("clock.force-quantum"),
                         "0")

            # --- q_env / q_wrapper: the same node props.
            for lname, argv, env_extra in (
                    ("q_env", [probe, "bufsize", "1.4", "0", "0"],
                     {"PIPEWIRE_QUANTUM": "512/48000"}),
                    ("q_wrapper",
                     ["pw-jack", "-p", "512", probe, "bufsize",
                      "1.4", "0", "0"],
                     None)):
                cname = f"{JACK_R95_PREFIX}_{lname}"
                legs[lname] = _jack_r95_probe(
                    (None if lname == "q_wrapper" else probe),
                    (argv if lname == "q_wrapper" else argv[1:]),
                    10.0, env=_jack_r95_env(cname, env_extra),
                    mid=node_slice(cname), mid_at=0.7)
                if lname == "q_wrapper":
                    legs[lname]["argv"] = " ".join(
                        ["pw-jack", "-p", "512", "<probe>",
                         "bufsize", "1.4", "0", "0"])
                l = legs[lname]
                j = l.get("json") or {}
                mid = (l.get("mid") or {}).get("q") or {}
                _jack_r95_eq(failures, lname, "set skipped",
                             j.get("set_inactive_attempted"), False)
                _jack_r95_eq(failures, lname, "force-quantum",
                             mid.get("force_quantum"), "512")
                _jack_r95_eq(failures, lname, "force-rate",
                             mid.get("force_rate"), "48000")
                _jack_r95_eq(failures, lname, "bufsize_activated",
                             j.get("bufsize_activated"), 512)
                _jack_r95_eq(failures, lname, "srate_live",
                             j.get("srate_live"), 48000)

            # --- q_env_rate: the rate axis lands and the client runs.
            cname = f"{JACK_R95_PREFIX}_qr"
            legs["q_env_rate"] = _jack_r95_probe(
                probe, ["bufsize", "1.4", "0", "0"], 10.0,
                env=_jack_r95_env(cname, {"PIPEWIRE_QUANTUM": "512/44100"}),
                mid=node_slice(cname), mid_at=0.7)
            l = legs["q_env_rate"]
            j = l.get("json") or {}
            mid = (l.get("mid") or {}).get("q") or {}
            _jack_r95_eq(failures, "q_env_rate", "force-rate",
                         mid.get("force_rate"), "44100")
            _jack_r95_eq(failures, "q_env_rate", "srate_active",
                         j.get("srate_active"), 44100)
            _jack_r95_eq(failures, "q_env_rate", "srate_live",
                         j.get("srate_live"), 44100)
            _jack_r95_eq(failures, "q_env_rate", "bufsize_live",
                         j.get("bufsize_live"), 512)
            _jack_r95_eq(failures, "q_env_rate", "bufsize_activated",
                         j.get("bufsize_activated"), 512)
            after_rate = _jack_r95_settings()
            l["settings_after"] = after_rate
            _jack_r95_eq(failures, "q_env_rate", "clock.rate restored",
                         after_rate.get("clock.rate"),
                         settings_before.get("clock.rate"))

            # --- q_bufsize1: the metadata-only reset (F7).
            cname = f"{JACK_R95_PREFIX}_q1"
            legs["q_bufsize1"] = _jack_r95_probe(
                probe, ["bufsize", "1.4", "1", "0"], 10.0,
                env=_jack_r95_env(cname), mid=node_slice(cname),
                mid_at=0.7)
            l = legs["q_bufsize1"]
            j = l.get("json") or {}
            mid = (l.get("mid") or {}).get("q") or {}
            _jack_r95_eq(failures, "q_bufsize1", "node.force-quantum",
                         mid.get("force_quantum"), "1")
            _jack_r95_band(failures, "q_bufsize1", "effective bufsize",
                           j.get("bufsize_activated"), 1, 8)
            _jack_r95_eq(failures, "q_bufsize1", "settings untouched",
                         (l.get("mid") or {}).get("settings", {})
                         .get("clock.force-quantum"), "0")

            # --- q_global: the metadata write + restore (disclosed).
            cname = f"{JACK_R95_PREFIX}_qg"
            env_global = _jack_r95_env(
                cname, {"PIPEWIRE_PROPS":
                        "{ jack.global-buffer-size = true }"})

            def global_mid():
                g = _jack_r95_graph()
                n = (g.get("node_by_name") or {}).get(cname) or {}
                return {"settings": _jack_r95_settings(),
                        "node_force_quantum": n.get("force_quantum")}

            legs["q_global"] = _jack_r95_probe(
                probe, ["bufsize", "1.4", "512", "0"], 10.0,
                env=env_global, mid=global_mid, mid_at=0.7)
            l = legs["q_global"]
            j = l.get("json") or {}
            m = l.get("mid") or {}
            l["settings_during"] = m.get("settings")
            l["settings_after_exit"] = _jack_r95_settings()
            _jack_r95_eq(failures, "q_global", "metadata during",
                         (m.get("settings") or {})
                         .get("clock.force-quantum"), "512")
            _jack_r95_eq(failures, "q_global", "metadata after exit",
                         (l["settings_after_exit"] or {})
                         .get("clock.force-quantum"), "512")
            cname_b = f"{JACK_R95_PREFIX}_qgb"
            legs["q_global_second"] = _jack_r95_probe(
                probe, ["info", "0.5"], 8.0, env=_jack_r95_env(cname_b))
            jb = legs["q_global_second"].get("json") or {}
            _jack_r95_eq(failures, "q_global_second", "second client",
                         jb.get("bufsize_active"), 512)
            cname_r = f"{JACK_R95_PREFIX}_qgr"
            legs["q_global_reset"] = _jack_r95_probe(
                probe, ["bufsize", "1.4", "1", "0"], 10.0,
                env=_jack_r95_env(cname_r, {
                    "PIPEWIRE_PROPS":
                    "{ jack.global-buffer-size = true }"}),
                mid=lambda: {"settings": _jack_r95_settings()},
                mid_at=0.7)
            settings_final = _jack_r95_settings()
            entry["settings_final"] = settings_final
            l["settings_final"] = settings_final
            _jack_r95_eq(failures, "q_global_reset", "metadata restored",
                         settings_final.get("clock.force-quantum"), "0")
            moved = sorted(
                k for k in set(settings_before) | set(settings_final)
                if settings_before.get(k) != settings_final.get(k)
                and k != "clock.force-quantum")
            entry["settings_moved"] = moved
            if moved:
                failures.append(
                    f"q_global: settings keys moved across the global "
                    f"arm: {moved} — only clock.force-quantum may move")
        entry["legs"] = legs
        entry["failures"] = failures
        _jack_r95_teardown(entry, failures, loads, procs)
    except Exception as exc:
        entry.setdefault("coverage_blocked", []).append(
            f"entry aborted: {type(exc).__name__}: {exc}"[:200])
        entry["legs"] = legs
        entry["failures"] = failures
    return entry


def jack_defects_r95_entry():
    """The broken families (the interesting part). xrun: client-side
    stalls (8 x 150 ms) produce no callback — the callback mirrors the
    DRIVER counter, so the count is armed as an envelope (<= 1), never
    as a startup artifact. RT priority: the stack-poison control returns
    the 0xAA/0xBB pattern verbatim. Latency: a local store, invisible
    pre-activation, exact post-activation. Transport: start/stop gate a
    read-only projection; locate/reposition are inert. Metadata:
    jack_set_property writes the `default` store keyed by the object's
    REGISTRY id (the row is visible to pw-dump while the client lives
    and dies with it), while the client's own getter stays stale after
    its own removal."""
    failures, legs = [], {}
    entry = _jack_r95_entry_head("r95a JACK defect families")
    missing = [t for t in ("gcc", "pactl", "pw-dump", "pw-cli")
               if not shutil.which(t)]
    if missing:
        return _jack_r95_block(entry, failures, f"missing tools: {missing}")
    loads, procs = {}, []
    try:
        with tempfile.TemporaryDirectory(prefix="r95a-def-") as tmp:
            probe, build = _jack_r95_build(tmp)
            entry["build"] = build
            if probe is None:
                return _jack_r95_block(
                    entry, failures,
                    f"fixture build failed: {build.get('rc')}")
            leaf = _jack_r95_load_ns(JACK_R95_NS, desc=JACK_R95_DS)
            loads = {JACK_R95_NS: leaf}
            if leaf.get("module_id") is None:
                return _jack_r95_block(
                    entry, failures,
                    f"probe null sink {JACK_R95_NS} never enumerated",
                    loads, procs)

            # --- d_xrun_stall: 8 deliberate stalls, no callback.
            cname = f"{JACK_R95_PREFIX}_xrun"
            legs["d_xrun_stall"] = _jack_r95_probe(
                probe, ["stall", "2.0", "4", "150000",
                        f"{JACK_R95_DS}:playback_MONO"], 25.0,
                env=_jack_r95_env(cname))
            l = legs["d_xrun_stall"]
            j = l.get("json") or {}
            if l.get("killed_at_bound"):
                # the stall arm is the family's own RT perturbation: a
                # client that does not return from a 150 ms in-callback
                # sleep inside the bound is recorded as a confound, and
                # the xrun envelope is not judged from a killed run.
                entry.setdefault("coverage_blocked", []).append(
                    "d_xrun_stall: killed at the bound (client did not "
                    "return from the stall arm) — xrun envelope "
                    "unjudged")
            else:
                _jack_r95_eq(failures, "d_xrun_stall", "rc",
                             l.get("exit_code"), 0)
            if not l.get("killed_at_bound"):
                _jack_r95_band(failures, "d_xrun_stall", "stall_cycles",
                               j.get("stall_cycles"), 4, 100000)
                _jack_r95_band(failures, "d_xrun_stall", "cb",
                               j.get("cb"), 10, 100000)
                _jack_r95_band(failures, "d_xrun_stall", "xrun_cbs",
                               j.get("xrun_cbs"), 0, 1)

            # --- d_rtprio_poison: the pattern comes back verbatim.
            cname = f"{JACK_R95_PREFIX}_poison"
            legs["d_rtprio_poison"] = _jack_r95_probe(
                probe, ["rtprio_poison", "0.2"], 12.0,
                env=_jack_r95_env(cname))
            l = legs["d_rtprio_poison"]
            j = l.get("json") or {}
            _jack_r95_eq(failures, "d_rtprio_poison", "rc",
                         l.get("exit_code"), 0)
            for arm, pat in (("poison_aa", 0xAAAAAAA0),
                             ("poison_bb", 0xBBBBBBB0)):
                vals = j.get(arm) or []
                l[f"{arm}_masked"] = [
                    [f"0x{v[0] & 0xFFFFFFFF & ~0xF:08x}",
                     f"0x{v[1] & 0xFFFFFFFF & ~0xF:08x}"]
                    for v in vals if isinstance(v, list) and len(v) == 2]
                if len(vals) < 3 or any(
                        (v[0] & 0xFFFFFFFF & ~0xF) != pat
                        or (v[1] & 0xFFFFFFFF & ~0xF) != pat
                        for v in vals):
                    failures.append(
                        f"d_rtprio_poison: {arm} = {vals} — the "
                        "stack-poison pattern does not return verbatim")

            # --- d_latency: local store deferred to the data loop.
            cname = f"{JACK_R95_PREFIX}_lat"
            legs["d_latency"] = _jack_r95_probe(
                probe, ["latency", "1.2"], 12.0,
                env=_jack_r95_env(cname))
            l = legs["d_latency"]
            j = l.get("json") or {}
            for tag in ("out_before", "out_after_set"):
                _jack_r95_eq(failures, "d_latency", f"{tag} lat_cap",
                             (j.get(tag) or {}).get("lat_cap"), [0, 0])
                _jack_r95_eq(failures, "d_latency", f"{tag} lat_play",
                             (j.get(tag) or {}).get("lat_play"), [0, 0])
            _jack_r95_eq(failures, "d_latency", "out_active lat_cap",
                         (j.get("out_active") or {}).get("lat_cap"),
                         [100, 200])
            _jack_r95_eq(failures, "d_latency", "out_active lat_play",
                         (j.get("out_active") or {}).get("lat_play"),
                         [10, 20])
            _jack_r95_eq(failures, "d_latency", "out_active total",
                         (j.get("out_active") or {}).get("total"), 150)
            _jack_r95_eq(failures, "d_latency", "in_active lat_cap",
                         (j.get("in_active") or {}).get("lat_cap"), [0, 0])
            _jack_r95_eq(failures, "d_latency", "recompute_rc",
                         j.get("recompute_rc"), 0)

            # --- d_transport: a read-only projection.
            cname = f"{JACK_R95_PREFIX}_tr"
            legs["d_transport"] = _jack_r95_probe(
                probe, ["transport", "1.0",
                        f"{JACK_R95_DS}:playback_MONO"],
                14.0, env=_jack_r95_env(cname))
            l = legs["d_transport"]
            j = l.get("json") or {}
            _jack_r95_eq(failures, "d_transport", "state before activate",
                         j.get("state_before_activate"), 0)
            _jack_r95_eq(failures, "d_transport", "state after activate",
                         j.get("state_after_activate"), 0)
            _jack_r95_eq(failures, "d_transport", "tconn_rc",
                         j.get("tconn_rc"), 0)
            _jack_r95_eq(failures, "d_transport", "out_connected",
                         j.get("out_connected"), 1)
            _jack_r95_eq(failures, "d_transport", "state after start",
                         j.get("state_after_start"), 1)
            _jack_r95_true(
                failures, "d_transport", "frame advances on start",
                (j.get("frame_after_start") or 0) > (j.get("frame_after") or 0))
            _jack_r95_eq(failures, "d_transport", "state after stop",
                         j.get("state_after_stop"), 0)
            _jack_r95_eq(failures, "d_transport", "locate_rc",
                         j.get("locate_rc"), 0)
            _jack_r95_eq(failures, "d_transport", "reposition_rc",
                         j.get("reposition_rc"), 0)
            _jack_r95_eq(failures, "d_transport", "locate inert",
                         j.get("frame_after_locate"),
                         j.get("frame_after_stop"))
            _jack_r95_eq(failures, "d_transport", "reposition inert",
                         j.get("frame_after_reposition"),
                         j.get("frame_after_stop"))

            # --- d_metadata: the `default` store keyed by registry id.
            cname = f"{JACK_R95_PREFIX}_meta"

            def meta_mid():
                g = _jack_r95_graph()
                n = (g.get("node_by_name") or {}).get(cname) or {}
                rows = _jack_r95_meta_rows("default").get("rows") or {}
                return {"node_id": n.get("id"),
                        "rows": {k: v for k, v in rows.items()
                                 if str(k).startswith("r95a/")}}

            legs["d_metadata"] = _jack_r95_probe(
                probe, ["metadata", "0.6"], 14.0,
                env=_jack_r95_env(cname), mid=meta_mid, mid_at=0.5)
            l = legs["d_metadata"]
            j = l.get("json") or {}
            m = l.get("mid") or {}
            l["rows_after_exit"] = {
                k: v for k, v in
                (_jack_r95_meta_rows("default").get("rows") or {}).items()
                if str(k).startswith("r95a/")}
            _jack_r95_eq(failures, "d_metadata", "set_client_rc",
                         j.get("set_client_rc"), 0)
            _jack_r95_eq(failures, "d_metadata", "set_port_rc",
                         j.get("set_port_rc"), 0)
            _jack_r95_eq(failures, "d_metadata", "get_client_rc",
                         j.get("get_client_rc"), 0)
            _jack_r95_eq(failures, "d_metadata", "get_client_value",
                         j.get("get_client_value"), "value1")
            _jack_r95_eq(failures, "d_metadata", "get_client_type",
                         j.get("get_client_type"), "text/plain")
            _jack_r95_eq(failures, "d_metadata", "get_port_value",
                         j.get("get_port_value"), "portval")
            _jack_r95_eq(failures, "d_metadata", "get_missing_rc",
                         j.get("get_missing_rc"), -1)
            _jack_r95_eq(failures, "d_metadata", "own_desc_count",
                         j.get("own_desc_count"), 2)
            _jack_r95_eq(failures, "d_metadata", "remove_client_rc",
                         j.get("remove_client_rc"), 0)
            _jack_r95_eq(failures, "d_metadata", "stale after remove",
                         j.get("get_after_remove_value"), "value1")
            rows = m.get("rows") or {}
            _jack_r95_eq(failures, "d_metadata", "live row value",
                         (rows.get("r95a/key1") or {}).get("value"),
                         "value1")
            if not rows:
                failures.append(
                    "d_metadata: no r95a/ row in the `default` store "
                    "while the client ran — the live-row law fails")
            else:
                subj = (rows.get("r95a/key1") or {}).get("subject")
                _jack_r95_eq(failures, "d_metadata",
                             "row subject is the registry id",
                             subj, m.get("node_id"))
            l["rows_after_exit_ok"] = not l["rows_after_exit"]
            if l["rows_after_exit"]:
                failures.append(
                    "d_metadata: r95a/ rows survived the writer: "
                    f"{l['rows_after_exit']}")
        entry["legs"] = legs
        entry["failures"] = failures
        _jack_r95_teardown(entry, failures, loads, procs)
    except Exception as exc:
        entry.setdefault("coverage_blocked", []).append(
            f"entry aborted: {type(exc).__name__}: {exc}"[:200])
        entry["legs"] = legs
        entry["failures"] = failures
    return entry

