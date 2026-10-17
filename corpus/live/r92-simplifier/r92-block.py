# r92: THE FILTER-CHAIN DSP SURFACE — `libpipewire-module-filter-chain`,
#     the SPA filter-graph host, measured headless through a pw-cli
#     client context. The lattice pins: the module is CLIENT-LOCAL
#     (loaded in pw-cli, its nodes are real graph citizens while the
#     session lives and die with it — no daemon module, no pactl row);
#     the host-safe arming shape (node.autoconnect=false on both stream
#     prop bags + capture.props.media.class=Audio/Sink for a feedable
#     capture side; the capture side has NO ports without that class);
#     the args grammar (object elements, quoted port names, `#` starts a
#     comment even inside quotes, a control key containing a space is
#     expressible ONLY quoted — the bare form destroys the whole graph
#     with a properties parse error, a typo'd control name is a
#     warning-only no-op); the builtin label table (26 load / 6 fail);
#     the DSP core against an independent ANALYTIC RBJ reference (unity
#     `copy`, lowpass/peaking/notch/shelf rows, `param_eq` == the
#     equivalent `bq_peaking`); the clamp lattice (Gain [-120,+20], Q 10,
#     `Freq` guarded above Nyquist -> pass-through, `Freq` 0/negative ->
#     EXACT digital silence, not NaN); the inert surfaces (b0..a2
#     coefficient ports and `Gain` on labels that do not use it are
#     advertised but inert; `bq_raw` has no reachable direct-coefficient
#     path from module args); the convolver (sample-exact to the s16 LSB
#     against the file's own quantised IR, a rate-mismatched IR is
#     RESAMPLED, a 2-channel IR silently uses channel 0, `gain` hard-
#     clips at full scale) and its SILENT failure class (no config /
#     bad / empty / text / directory path: loads, streams, emits exact
#     digital zeros — silent at LOAD (E=0/W=0 at debug 3 and 5) and
#     diagnosable only at ACTIVATION, where the graph refuses to start
#     with an [E] line the rc/var never shows); the `delay` law
#     (exactly round(s*rate) samples up to `max-delay`, over-max requests
#     clamp to 2431 samples); the impulse-response tap law (the PRE/POST
#     taps are separate streams, so only a DIFFERENCE is stable and it is
#     block-quantised: every shift is asserted modulo 1024); the pw-cli
#     stdin classes (/dev/null file EOF -> SIGABRT + remove_from_poll,
#     pipe EOF -> HANG, `quit` -> rc 0); wpexec's LocalModule path
#     (live graph, self-cleaning, silent nil on a bad module/label, the
#     bare `Lua runtime error` for rawget/require_api, an empty script
#     hangs); and the absent classes (ffmpeg has no SPA plugin, LADSPA's
#     search path is empty, LV2's inventory holds no DSP plugin, the
#     shipped virtual-surround config references an IR directory that is
#     not shipped) — --probe-filterchain-r92.
#
# A NEW parallel ledger family; prior rows untouched; every r76-r91
# guard inherited (seat-owned r92a_<pid>_<tag> names unique per leg, the
# name-verified sink_name= unloads, never set-default-*, bounded process
# groups, RLIMIT_CORE=0 on every child — pw-cli aborts on file EOF).
# The family lock is a FIXED corpus/live/ path — the r84 F1 3-seat
# consensus (never $TMPDIR). All armed claims are the r92 boundary's
# THIS-HOST survivals (PipeWire 1.6.8, WirePlumber 0.5.17, python
# 3.14.7); the boundary's falsified rows are dropped (the report's
# §3 table rows, the "delay does not delay" typo artifact, the NaN
# half of the Freq=0 claim, the "3/3 byte-identical" heading) and
# the scout's absolute-latency constant is replaced by the measured
# modulo-1024 law. Volatile text (ids, serials, addresses, wall times,
# byte counts, host link inventories, foreign client names) is
# recorded, never armed.

FILTERCHAIN_R92_PID = os.getpid()
FILTERCHAIN_R92_PREFIX = f"r92a_{FILTERCHAIN_R92_PID}"
FILTERCHAIN_R92_RATE = 48000
FILTERCHAIN_R92_FREQS = (200, 1000, 4000, 12000, 20000)
FILTERCHAIN_R92_WIN = 24000          # 0.5 s; every probe is integer cycles
FILTERCHAIN_R92_MOD = "libpipewire-module-filter-chain"
FILTERCHAIN_R92_BLOCKSIZE = 1024     # the measured tap-shift quantum
FILTERCHAIN_R92_DEBUG = "3"
FILTERCHAIN_R92_EOF_S = 6.0          # the pipe-EOF hang bound
# The measured label table: 26 load / 6 fail (the six failures are
# present as strings inside the plugin .so — advertisement != objects).
FILTERCHAIN_R92_LABELS_OK = (
    "abs", "bq_allpass", "bq_bandpass", "bq_highpass", "bq_highshelf",
    "bq_lowpass", "bq_lowshelf", "bq_notch", "bq_peaking", "bq_raw",
    "clamp", "convolver", "copy", "dcblock", "delay", "exp", "invert",
    "linear", "log", "max", "mixer", "mult", "noisegate", "param_eq",
    "recip", "sine")
FILTERCHAIN_R92_LABELS_FAIL = ("avg", "gain", "min", "nop",
                               "passthrough", "sum")
FILTERCHAIN_R92_FG_DIR = "/usr/lib/spa-0.2/filter-graph"
FILTERCHAIN_R92_SPA_DIR = "/usr/lib/spa-0.2"
FILTERCHAIN_R92_LADSPA_DIRS = ("/usr/lib64/ladspa", "/usr/lib/ladspa")
FILTERCHAIN_R92_LV2_DIR = "/usr/lib/lv2"
FILTERCHAIN_R92_PW_DIR = "/usr/share/pipewire"

# r92-local error classes — family-local, checked before the r88 chain.
_FILTERCHAIN_R92_ERR_CLASSES = (
    # the LADSPA host ALSO prints `can't load plugin type 'ladspa'`, so
    # its own (more specific) line must be matched first — measured: the
    # first run classified the LADSPA refusal as the generic type class
    ("fc92_ladspa_missing",
     r"failed to load plugin '[^']+' in '[^']*'"),
    ("fc92_type_missing", r"can't load plugin type '[^']+'"),
    ("fc92_label_missing", r"cannot create label [^\s]+"),
    ("fc92_graph_not_object", r"filter.graph must be an object"),
    ("fc92_graph_no_nodes", r"filter.graph has no nodes"),
    ("fc92_props_parse",
     r"error parsing more than 0 properties: [^\n]+"),
    ("fc92_convolver_cfg", r"convolver: requires a config section"),
    ("fc92_convolver_file", r"failed file [^\n]+"),
    ("fc92_raw_no_config", r"bq_raw requires a config section"),
    ("fc92_control_typo", r"control '[^']+' can not be set"),
    ("fc92_unload_unknown", r"unknown module '[^']*'"),
    ("fc92_wpx_runtime", r"Lua runtime error"),
    ("fc92_wpx_compile", r"Failed to compile"),
    ("fc92_wpx_locate", r"Could not locate script"),
    ("fc92_abort_loop", r"remove_from_poll\(\)"),
    # the generic refusal is the WEAKEST class: every specific class
    # above is carried in the same log, so the refusal match comes last
    ("fc92_load_refused", r'Error: "Could not load module"'),
    # pw-cli's own registry dump noise (present in every session)
    ("fc92_cli_noise",
     r'unsupported type PipeWire:Interface:(SecurityContext|Profiler)'),
)


def _fc92_errclass(text):
    for name, pat in _FILTERCHAIN_R92_ERR_CLASSES:
        m = re.search(pat, text or "")
        if m:
            return name, m.group(0).strip()
    return _btwit_r88_errclass(text or "")


def _fc92_norm(text):
    """Volatile-field scrub: the r88 node/id classes plus pid-tagged
    seat names and hex pointers (pw-cli logs carry both)."""
    s = _btwit_r88_norm(text or "")
    s = s.replace(FILTERCHAIN_R92_PREFIX, "r92a_<pid>")
    return s


def _fc92_f(x, nd=6):
    """Finite-rounded float or None — the receipt is written with
    allow_nan=False, so no NaN/inf may ever reach it."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(v):
        return None
    return round(v, nd)


# ------------------------------------------------------------ own WAV I/O

def _fc92_wav_write(path, x, rate=FILTERCHAIN_R92_RATE, ch=1, fmt="s16"):
    """Own RIFF writer (s16 / s24 / f32) — no sibling fixture imported."""
    x = np.asarray(x, dtype=np.float64)
    if fmt == "s16":
        data = np.clip(np.rint(x * 32767.0), -32768,
                       32767).astype("<i2").tobytes()
        tag, bits, block = 1, 16, 2
    elif fmt == "s24":
        v = np.clip(np.rint(x * 8388607.0), -8388608,
                    8388607).astype("<i4")
        data = v.astype("<u4").view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
        tag, bits, block = 1, 24, 3
    elif fmt == "f32":
        data = x.astype("<f4").tobytes()
        tag, bits, block = 3, 32, 4
    else:
        raise ValueError(fmt)
    frames = len(x) // ch
    hdr = b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVE"
    hdr += b"fmt " + struct.pack("<IHHIIHH", 16, tag, ch, rate,
                                 rate * block * ch, block * ch, bits)
    hdr += b"data" + struct.pack("<I", len(data))
    Path(path).write_bytes(hdr + data)
    return {"path": str(path), "frames": frames, "fmt": fmt,
            "bytes": 44 + len(data)}


def _fc92_wav_read(path):
    """Own RIFF reader: PCM s16/s24/s32 + IEEE float32. Values are
    normalized to [-1,1); LSB = 1/32768 for the residual arms."""
    raw = Path(path).read_bytes()
    if raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise ValueError(f"not RIFF/WAVE: {path}")
    pos, fmt, data = 12, None, None
    while pos + 8 <= len(raw):
        cid = raw[pos:pos + 4]
        sz = struct.unpack("<I", raw[pos + 4:pos + 8])[0]
        body = raw[pos + 8:pos + 8 + sz]
        if cid == b"fmt ":
            tag, ch, rate, _br, _ba, bits = struct.unpack(
                "<HHIIHH", body[:16])
            if tag == 0xFFFE and len(body) >= 40:
                tag = struct.unpack("<H", body[24:26])[0]
            fmt = {"tag": tag, "ch": ch, "rate": rate, "bits": bits}
        elif cid == b"data":
            data = body
        pos += 8 + sz + (sz & 1)
    if fmt is None or data is None:
        raise ValueError(f"no fmt/data chunk: {path}")
    tag, bits, ch = fmt["tag"], fmt["bits"], fmt["ch"]
    if tag == 1 and bits == 16:
        x = np.frombuffer(data, "<i2").astype(np.float64) / 32768.0
    elif tag == 1 and bits == 24:
        u = np.frombuffer(data, np.uint8).reshape(-1, 3).astype(np.uint32)
        v = (u[:, 0] | (u[:, 1] << 8) | (u[:, 2] << 16)).astype(np.int32)
        v = np.where(v & 0x800000, v - 0x1000000, v)
        x = v.astype(np.float64) / 8388608.0
    elif tag == 1 and bits == 32:
        x = np.frombuffer(data, "<i4").astype(np.float64) / 2147483648.0
    elif tag == 3 and bits == 32:
        x = np.frombuffer(data, "<f4").astype(np.float64)
    else:
        raise ValueError(f"unsupported tag={tag} bits={bits}")
    return {"x": x, "frames": len(x), "ch": ch, "rate": fmt["rate"],
            "bytes": len(raw)}


# --------------------------------------------------------------- own synth

def _fc92_multitone(freqs, dur, amp=0.2):
    n = int(dur * FILTERCHAIN_R92_RATE)
    t = np.arange(n) / FILTERCHAIN_R92_RATE
    x = np.zeros(n)
    for f in freqs:
        x += amp * np.sin(2 * np.pi * f * t)
    return x / max(1, len(freqs))


def _fc92_ir_wav(path, taps, n=8192, rate=FILTERCHAIN_R92_RATE,
                 fmt="s16", ch=1):
    """taps: (offset, gain) for mono, (channel, offset, gain) for ch>1."""
    buf = np.zeros(n * ch)
    for t in taps:
        if len(t) == 3:
            c, off, g = t
        else:
            c, (off, g) = 0, t
        if 0 <= off < n and 0 <= c < ch:
            buf[off * ch + c] += g
    return _fc92_wav_write(path, buf, rate=rate, ch=ch, fmt=fmt)


def _fc92_stimuli(scratch):
    """Own deterministic stimuli: the 5-tone transfer-function probe, the
    single-sample delta (impulse), and the IR fixtures."""
    st = {}
    st["tone"] = Path(scratch) / "r92a_tone5.wav"
    _fc92_wav_write(st["tone"], _fc92_multitone(FILTERCHAIN_R92_FREQS,
                                                1.5))
    st["tone200"] = Path(scratch) / "r92a_tone200.wav"
    _fc92_wav_write(st["tone200"],
                    0.5 * np.sin(2 * np.pi * 200
                                * np.arange(int(1.5 * FILTERCHAIN_R92_RATE))
                                / FILTERCHAIN_R92_RATE))
    d = np.zeros(4096)
    d[100] = 1.0
    st["delta"] = Path(scratch) / "r92a_delta100.wav"
    _fc92_wav_write(st["delta"], d)
    st["ir_2tap"] = Path(scratch) / "r92a_ir_2tap.wav"
    _fc92_ir_wav(st["ir_2tap"], [(0, 1.0), (64, 0.5)])
    st["ir_d100"] = Path(scratch) / "r92a_ir_d100.wav"
    _fc92_ir_wav(st["ir_d100"], [(100, 1.0)])
    st["ir_decay512"] = Path(scratch) / "r92a_ir_decay512.wav"
    _fc92_ir_wav(st["ir_decay512"], [(i, 0.99 ** i)
                                     for i in range(512)])
    st["ir_441"] = Path(scratch) / "r92a_ir_44100.wav"
    _fc92_ir_wav(st["ir_441"], [(100, 1.0)], rate=44100)
    st["ir_stereo"] = Path(scratch) / "r92a_ir_stereo.wav"
    _fc92_ir_wav(st["ir_stereo"], [(0, 10, 1.0), (1, 20, 1.0)], ch=2)
    st["ir_empty"] = Path(scratch) / "r92a_ir_empty.wav"
    st["ir_empty"].write_bytes(b"")
    st["ir_text"] = Path(scratch) / "r92a_ir_text.wav"
    st["ir_text"].write_text("this is not a wav file at all\n")
    st["ir_dir"] = Path(scratch) / "r92a_ir_dir.wav"
    st["ir_dir"].mkdir(exist_ok=True)
    st["bad_path"] = "/nonexistent/r92a_ir.wav"
    return st


# --------------------------------------------------------------- analysis

def _fc92_dft(x, freqs):
    """Vectorised single-bin DFT magnitude (own estimator)."""
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    t = np.arange(n)
    out = {}
    for f in freqs:
        w = 2 * np.pi * f / FILTERCHAIN_R92_RATE
        re = float(np.dot(x, np.cos(w * t)))
        im = float(np.dot(x, np.sin(w * t)))
        out[int(f)] = 2.0 * np.hypot(re, im) / n
    return out


def _fc92_best_window(x, win=FILTERCHAIN_R92_WIN, step=2400):
    """The loudest `win`-sample window (max energy) — the scout's fixed
    skip sampled the prefill and invented a route loss; this rule is the
    boundary's fix. Deep-attenuation rows are measured with a multi-tone
    stimulus so the passing tones keep the window honest."""
    x = np.asarray(x, dtype=np.float64)
    if len(x) <= win:
        return x, 0
    best, bi = -1.0, 0
    for i in range(0, len(x) - win + 1, step):
        seg = x[i:i + win]
        r = float(np.dot(seg, seg))
        if r > best:
            best, bi = r, i
    return x[bi:bi + win], bi


def _fc92_db(a, b, floor=1e-15):
    if not (np.isfinite(a) and np.isfinite(b)):
        return None
    if a <= floor and b <= floor:
        return None
    return _fc92_f(20 * np.log10(max(floor, a) / max(floor, b)), 3)


def _fc92_sig_stats(x):
    x = np.asarray(x)
    if not len(x):
        return {"n": 0, "nz_exact": 0, "max_abs": 0.0, "rms": 0.0}
    return {"n": int(len(x)), "nz_exact": int(np.count_nonzero(x)),
            "max_abs": _fc92_f(np.max(np.abs(x)), 7),
            "rms": _fc92_f(np.sqrt(float(np.mean(x * x))), 7)}


# ------------------------------------------------- analytic RBJ reference

def _fc92_rbj(label, f0, q, gain_db=0.0, rate=FILTERCHAIN_R92_RATE,
              slope=None):
    """RBJ cookbook coefficients (analytic, float64) — the independent
    reference, never an impulse simulation. lp hp pk ls hs nt ap bp."""
    if q == 0:
        q = 0.707
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2 * np.pi * f0 / rate
    cw, sw = np.cos(w0), np.sin(w0)
    al = (sw / 2 * np.sqrt((A + 1 / A) * (1 / slope - 1) + 2)
          if slope else sw / (2 * q))
    if label == "lp":
        b, a = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2], \
            [1 + al, -2 * cw, 1 - al]
    elif label == "hp":
        b, a = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2], \
            [1 + al, -2 * cw, 1 - al]
    elif label == "pk":
        b, a = [1 + al * A, -2 * cw, 1 - al * A], \
            [1 + al / A, -2 * cw, 1 - al / A]
    elif label == "ls":
        s = 2 * np.sqrt(A) * al
        b = [A * ((A + 1) - (A - 1) * cw + s),
             2 * A * ((A - 1) - (A + 1) * cw),
             A * ((A + 1) - (A - 1) * cw - s)]
        a = [(A + 1) + (A - 1) * cw + s,
             -2 * ((A - 1) + (A + 1) * cw),
             (A + 1) + (A - 1) * cw - s]
    elif label == "hs":
        s = 2 * np.sqrt(A) * al
        b = [A * ((A + 1) + (A - 1) * cw + s),
             -2 * A * ((A - 1) + (A + 1) * cw),
             A * ((A + 1) + (A - 1) * cw - s)]
        a = [(A + 1) - (A - 1) * cw + s,
             2 * ((A - 1) - (A + 1) * cw),
             (A + 1) - (A - 1) * cw - s]
    elif label == "nt":
        b, a = [1, -2 * cw, 1], [1 + al, -2 * cw, 1 - al]
    elif label == "ap":
        b, a = [1 - al, -2 * cw, 1 + al], [1 + al, -2 * cw, 1 - al]
    elif label == "bp":
        b, a = [al, 0.0, -al], [1 + al, -2 * cw, 1 - al]
    else:
        raise ValueError(label)
    b = np.array(b, dtype=np.float64) / a[0]
    a = np.array(a, dtype=np.float64) / a[0]
    return b, a


def _fc92_rbj_gains(label, f0, q, gain_db=0.0,
                    freqs=FILTERCHAIN_R92_FREQS):
    b, a = _fc92_rbj(label, f0, q, gain_db)
    out = {}
    for f in freqs:
        z = np.exp(-2j * np.pi * f / FILTERCHAIN_R92_RATE)
        h = (b[0] + b[1] * z + b[2] * z * z) / \
            (a[0] + a[1] * z + a[2] * z * z)
        out[int(f)] = _fc92_f(20 * np.log10(abs(h)), 3)
    return out


# ----------------------------------------------------------- pw-cli driver

def _fc92_cli_open(env=None):
    """A held pw-cli session. The drain thread reads with `os.read` on
    the raw fd — a buffered `read(n)` on a pipe blocks until n bytes or
    EOF, which silently hides every reply until the session closes (the
    r87 helper's latent stall; measured while building this seat)."""
    e = dict(os.environ)
    if env:
        e.update(env)
    proc = subprocess.Popen(["pw-cli"], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            start_new_session=True, env=e,
                            preexec_fn=_pwctl_r86_no_core)
    chunks = []

    def drain():
        try:
            while True:
                b = os.read(proc.stdout.fileno(), 65536)
                if not b:
                    return
                chunks.append(b)
        except (OSError, ValueError):
            return

    threading.Thread(target=drain, daemon=True).start()
    return proc, chunks


def _fc92_wait(chunks, mark, quiet_s=0.30, wait_s=4.0):
    """Wait until the session output quiesces (or wait_s) — the load
    reply lands a moment after the command."""
    start = time.monotonic()
    last_n, last_change = len(chunks), time.monotonic()
    while True:
        now = time.monotonic()
        if now - start >= wait_s:
            break
        if len(chunks) != last_n:
            last_n, last_change = len(chunks), now
        elif now - last_change >= quiet_s:
            break
        time.sleep(0.05)
    return b"".join(chunks[mark:]).decode(errors="replace")


def _fc92_text(chunks):
    return b"".join(chunks).decode(errors="replace")


def _fc92_cli_send(proc, line):
    try:
        proc.stdin.write(line.encode() + b"\n")
        proc.stdin.flush()
        return True
    except (BrokenPipeError, OSError, ValueError):
        return False


def _fc92_cli_close(proc, chunks, bound_s=6.0):
    """Always `quit` (file-EOF abort class) and close stdin (pipe-EOF
    hang class), then bounded wait with a SIGKILL backstop."""
    _fc92_cli_send(proc, "quit")
    try:
        proc.stdin.close()
    except (OSError, ValueError):
        pass
    try:
        proc.wait(timeout=bound_s)
    except subprocess.TimeoutExpired:
        _alsapw_r84_killpg(proc)
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            pass
    return _fc92_text(chunks)


def _fc92_session_load(args_text, env=None, debug=FILTERCHAIN_R92_DEBUG,
                       wait_s=5.0, quiet_s=0.30):
    """One held session that loads the module; returns the session plus
    the parsed `N = @module:M` var (the var, not the id, is what
    unload-module takes)."""
    e = {"PIPEWIRE_DEBUG": debug}
    if env:
        e.update(env)
    proc, chunks = _fc92_cli_open(env=e)
    mark = len(chunks)
    sent = _fc92_cli_send(proc, f"load-module {FILTERCHAIN_R92_MOD} "
                                f"{args_text}")
    text = _fc92_wait(chunks, mark, quiet_s=quiet_s, wait_s=wait_s)
    m = re.search(r"^\s*(\d+)\s*=\s*@module:(\d+)", text, re.M)
    return {"proc": proc, "chunks": chunks, "sent": sent,
            "load_text": text, "var": int(m.group(1)) if m else None,
            "module_id": int(m.group(2)) if m else None}


def _fc92_session_cmd(sess, line, wait_s=2.5, quiet_s=0.25):
    mark = len(sess["chunks"])
    sent = _fc92_cli_send(sess["proc"], line)
    return sent, _fc92_wait(sess["chunks"], mark, quiet_s=quiet_s,
                            wait_s=wait_s)


def _fc92_log_stats(text):
    return {"lines": len((text or "").splitlines()),
            "E": (text or "").count("[E]"),
            "W": (text or "").count("[W]"),
            "I": (text or "").count("[I]")}


def _fc92_log_lines(text, needle):
    return [ln.strip()[:220] for ln in (text or "").splitlines()
            if needle in ln][:6]


# ---------------------------------------------------------- bounded spawns

def _fc92_run(argv, timeout_s, env=None, stdin_data=None, keep_chars=900):
    """One bounded spawn -> rc/signal/stdout/stderr + the r92 error
    class. RLIMIT_CORE is always zeroed: the pw-cli EOF abort class is
    measured, never dumped."""
    rec = {"argv": " ".join(str(a) for a in argv)}
    try:
        proc = subprocess.Popen(
            argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=(subprocess.PIPE if stdin_data is not None
                   else subprocess.DEVNULL),
            env=env, start_new_session=True,
            preexec_fn=_pwctl_r86_no_core)
    except OSError as exc:
        rec["spawn_error"] = str(exc)[:160]
        return rec
    t0 = time.monotonic()
    killed = False
    try:
        out, err = proc.communicate(input=stdin_data, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        killed = True
        _alsapw_r84_killpg(proc)
        out, err = proc.communicate()
    outt = out.decode(errors="replace")
    errt = err.decode(errors="replace")
    cls, hit = _fc92_errclass(errt + "\n" + outt)
    rec.update({"exit_code": proc.returncode,
                "signal": (signal.Signals(-proc.returncode).name
                           if (proc.returncode or 0) < 0 else None),
                "killed_at_bound": killed,
                "wall_s": round(time.monotonic() - t0, 3),
                "stdout": _fc92_norm(outt)[:keep_chars],
                "stderr": _fc92_norm(errt)[:keep_chars],
                "error_class": cls, "error_hit": hit})
    return rec


def _fc92_spawn(argv, env=None):
    try:
        return subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.DEVNULL, env=env,
                                start_new_session=True,
                                preexec_fn=_pwctl_r86_no_core)
    except OSError:
        return None


def _fc92_reap(proc, term_s=3.0):
    """SIGTERM the group (pw-record finalizes its header), then SIGKILL."""
    if proc is None:
        return None
    if proc.poll() is None:
        _alsapw_r84_killpg(proc, signal.SIGTERM)
    try:
        proc.wait(timeout=term_s)
    except subprocess.TimeoutExpired:
        _alsapw_r84_killpg(proc)
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            return None
    return proc.returncode


# --------------------------------------------------------- graph readers

def _fc92_graph():
    return _pactlmon_r85_graph()


def _fc92_ports(g, nid):
    return _pwbind_r87_ports(g, nid)


def _fc92_own_edges(g, names):
    """Every link edge whose either end is one of `names` — the
    autoconnect-gate witness (0 with node.autoconnect=false)."""
    want = set(names)
    return sorted((e for e in _pactlmon_r85_edges(g)
                   if e.get("out_node") in want or e.get("in_node") in want),
                  key=lambda e: (str(e.get("out")), str(e.get("in"))))


def _fc92_spdif_links():
    """Host-sink link census (recorded, never armed — foreign lanes ride
    the operator's SPDIF sink throughout)."""
    return [l for l in _playback_r78_links()
            if "SPDIF" in l[0] or "SPDIF" in l[1]]


def _fc92_link(a, b, tries=10):
    """pw-link with a bounded retry — a stream publishes its ports a
    moment after its client starts, so a single attempt races."""
    last = None
    for i in range(tries):
        r = _fc92_run(["pw-link", a, b], 5.0, keep_chars=300)
        last = r
        if r.get("exit_code") == 0:
            return {"rc": 0, "tries": i + 1}
        if "File exists" in (r.get("stderr") or ""):
            return {"rc": 0, "tries": i + 1, "note": "exists"}
        time.sleep(0.25)
    return {"rc": last.get("exit_code"), "tries": tries,
            "err": (last.get("stderr") or "")[:200]}


# ------------------------------------------------------------ entry plumbing

def _fc92_ctx():
    """Seat context: one scratch root (UFO_FC92_SCRATCH keeps the bytes
    for the author's live receipts; otherwise a temp dir), the live
    process list and the name-verified load ledger."""
    base = os.environ.get("UFO_FC92_SCRATCH")
    if base:
        scratch = Path(base)
        scratch.mkdir(parents=True, exist_ok=True)
    else:
        scratch = Path(tempfile.mkdtemp(prefix=f"{FILTERCHAIN_R92_PREFIX}-"))
    ctx = {"scratch": scratch, "procs": [], "loads": {}, "stim": None}
    ctx["stim"] = _fc92_stimuli(scratch)
    return ctx


def _fc92_family_lock():
    """Same-family exclusion at a FIXED lane path — the r84 F1 3-seat
    consensus (never $TMPDIR; cross-TMPDIR same-family runs must still
    exclude). A second --probe-filterchain-r92 waits HERE."""
    path = ROOT / "live" / "measure_audio-filterchain-r92.lock"
    try:
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    except OSError:
        return None
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        os.ftruncate(fd, 0)
        os.write(fd, f"pid={FILTERCHAIN_R92_PID} "
                     f"prefix={FILTERCHAIN_R92_PREFIX}\n".encode())
    except OSError:
        pass
    return fd


def _fc92_daemon_health(timeout_s=15.0):
    """The shared daemon's own health witness. A saturated daemon turns
    every enumeration into a timeout; that must be a NAMED block, never
    a silent green (this seat measured a load-56 window in which pactl
    took >30 s to answer)."""
    r = _fc92_run(["pactl", "info"], timeout_s, keep_chars=200)
    return {"exit_code": r.get("exit_code"),
            "killed_at_bound": r.get("killed_at_bound"),
            "wall_s": r.get("wall_s"),
            "ok": r.get("exit_code") == 0
            and not r.get("killed_at_bound")}


def _fc92_reader(fn, tries=3, gap=2.0):
    """Bounded retry around the shared strict readers: a saturated
    daemon answers `None` once and that must not be recorded as an
    absence witness."""
    for i in range(tries):
        v = fn()
        if v is not None:
            return v, i + 1
        time.sleep(gap)
    return None, tries


def _fc92_entry_head(probe):
    inv = _capture_inventory()
    names = _playback_r78_node_names() or []
    return {"probe": probe,
            "daemon": _fc92_daemon_health(),
            "contention": _playback_r78_foreign_clients(),
            "oracle_at_start": _loopback_r79_oracle(),
            "foreign_r92a_nodes": sorted(
                n for n in names if "r92a_" in n
                and f"r92a_{FILTERCHAIN_R92_PID}" not in n),
            "inventory": {"default_sink": inv["default_sink"],
                          "default_source": inv["default_source"],
                          "sources_count": len(inv["sources"]),
                          "monitors_count": len(inv["monitors"]),
                          "alsa_capture_devices":
                          inv["alsa_capture_devices"]},
            "loadavg": _alsapw_r84_loadavg()}


def _fc92_ns_load(ctx, name):
    leaf = _pwcat_r83_ns_load(name, extra_args=("channels=1",))
    leaf["field"] = "sink_name"
    leaf["value"] = name
    ctx["loads"][name] = leaf
    return leaf


def _fc92_unload_ns(ctx, name):
    leaf = ctx["loads"].get(name) or {}
    return _pactlmon_r85_unload_own(leaf.get("module_id"), "sink_name",
                                    name)


def _fc92_teardown(entry, failures, ctx):
    """Kill every tracked child group, name-verified unload every own
    sink, destroy any surviving r92a_<pid> node by id, then the two
    absence witnesses (sinks_gone / own_nodes_after)."""
    for proc in ctx.get("procs") or ():
        _fc92_reap(proc)
    for name in list(ctx.get("loads") or {}):
        entry.setdefault("unloads", {})[name] = _fc92_unload_ns(ctx, name)
    g = _fc92_graph()
    residual = sorted(
        (nid, n.get("name")) for nid, n in (g.get("nodes") or {}).items()
        if n.get("name") and FILTERCHAIN_R92_PREFIX in n["name"])
    if residual:
        entry["residual_destroy"] = [
            {"id": nid, "name": nm,
             **_fc92_run(["pw-cli", "destroy", str(nid)], 8.0,
                         keep_chars=200)}
            for nid, nm in residual]
        time.sleep(0.4)
    sinks_now, sink_tries = _fc92_reader(_capture_r77_sink_names_strict)
    entry["reader_tries"] = {"sinks": sink_tries}
    if sinks_now is None:
        entry["sinks_gone"] = "reader_error"
        entry.setdefault("coverage_blocked", []).append(
            "teardown: pactl sink reader failed — sinks_gone unmeasured")
    else:
        gone = {nm: nm not in sinks_now
                for nm in (ctx.get("loads") or {})}
        entry["sinks_gone"] = gone
        if not all(gone.values()):
            failures.append("teardown: probe sinks survived unload: "
                            f"{[n for n, g_ in gone.items() if not g_]}")
    names, node_tries = _fc92_reader(_playback_r78_node_names)
    entry["reader_tries"]["nodes"] = node_tries
    if names is None:
        entry["own_nodes_after"] = "reader_error"
        entry.setdefault("coverage_blocked", []).append(
            "teardown: node reader failed — own_nodes_after unmeasured")
    else:
        rest = sorted(n for n in names
                      if FILTERCHAIN_R92_PREFIX in n)
        entry["own_nodes_after"] = rest
        if rest:
            failures.append(
                f"teardown: r92a-tagged nodes survived: {rest}")
    entry["live_after"] = {
        "spdif_links": len(_fc92_spdif_links()),
        "procs": [p.pid for p in (ctx.get("procs") or [])
                  if p.poll() is None]}


def _fc92_block(entry, failures, msg, ctx=None):
    entry["blocked"] = msg
    entry.setdefault("coverage_blocked", []).append(msg)
    if ctx is not None:
        for proc in ctx.get("procs") or ():
            _fc92_reap(proc)
        for name in list(ctx.get("loads") or {}):
            entry.setdefault("unloads", {})[name] = _fc92_unload_ns(ctx,
                                                                   name)
    entry["failures"] = failures
    return entry


# ------------------------------------------------------------ load-only legs

def _fc92_load_leg(ctx, tag, graph_text, debug=FILTERCHAIN_R92_DEBUG,
                   wait_s=3.0, props=True, keep_full=False):
    """One load-only leg (no sink, no audio, no links): open a session,
    load, wait for the reply, `quit`. The verdict surface is `loaded`
    (`@module:`), the refusal class and the [E]/[W] lines."""
    tail = (f",capture.props={{node.name={FILTERCHAIN_R92_PREFIX}_{tag}"
            f"_in,node.autoconnect=false}},playback.props={{node.name="
            f"{FILTERCHAIN_R92_PREFIX}_{tag}_out,node.autoconnect=false}}"
            if props else "")
    args_text = f"node.description={FILTERCHAIN_R92_PREFIX}_{tag}," \
                f"{graph_text}{tail}"
    sess = _fc92_session_load(args_text, debug=debug, wait_s=wait_s)
    full = _fc92_cli_close(sess["proc"], sess["chunks"])
    loaded = "@module:" in sess["load_text"]
    rec = {"args": args_text, "loaded": loaded, "var": sess["var"],
           "load_text": _fc92_norm(sess["load_text"])[:700],
           "log_stats": _fc92_log_stats(full),
           "err_lines": _fc92_log_lines(full, "[E]"),
           "warn_lines": _fc92_log_lines(full, "[W]"),
           "errors": re.findall(r'Error: "([^"]+)"', full)[:4]}
    cls, hit = _fc92_errclass(full + "\n" + sess["load_text"])
    rec["error_class"] = cls
    rec["error_hit"] = hit
    if keep_full:
        rec["log_tail"] = _fc92_norm(full)[-1200:]
    return rec


def _fc92_label_leg(ctx, tag, label, rep):
    graph = ("filter.graph={nodes=[{type=builtin,name=f1,label="
             f"{label}}}]}}")
    rec = _fc92_load_leg(ctx, tag, graph)
    rec["label"] = label
    rec["rep"] = rep
    return rec


def _fc92_shape_leg(ctx, tag, media_class=True):
    """The port-shape leg: load the chain against a live driver sink,
    read the capture node's class + port set, then ATTEMPT the feed link
    into `playback_MONO` — the unfeedable class is measured, not
    inferred from the class string."""
    ns = f"{FILTERCHAIN_R92_PREFIX}_{tag}_ns"
    row = {"tag": tag, "media_class": media_class}
    leaf = _fc92_ns_load(ctx, ns)
    row["sink"] = {"module_id": leaf.get("module_id")}
    if leaf.get("module_id") is None:
        row["gate"] = "driver sink never enumerated"
        return row
    args_text = _fc92_args(tag, _fc92_node("copy"),
                           media_class=media_class)
    row["args"] = args_text
    sess = None
    try:
        sess = _fc92_session_load(args_text)
        row["loaded"] = sess["var"] is not None
        if not row["loaded"]:
            row["load_text"] = _fc92_norm(sess["load_text"])[:300]
            return row
        time.sleep(0.4)
        g = _fc92_graph()
        fin = f"{FILTERCHAIN_R92_PREFIX}_{tag}_in"
        fout = f"{FILTERCHAIN_R92_PREFIX}_{tag}_out"
        nd = _pactlmon_r85_node(g, fin)
        ou = _pactlmon_r85_node(g, fout)
        row["capture_class"] = (nd or {}).get("media_class")
        row["capture_state"] = (nd or {}).get("state")
        row["capture_ports"] = (sorted(_fc92_ports(
            g, nd["node_id"]).keys()) if nd else None)
        row["playback_ports"] = (sorted(_fc92_ports(
            g, ou["node_id"]).keys()) if ou else None)
        row["own_edges"] = _fc92_own_edges(g, (fin, fout))
        row["spdif_links"] = len(_fc92_spdif_links())
        row["feed_link"] = _fc92_link(f"{ns}:monitor_MONO",
                                      f"{fin}:playback_MONO", tries=3)
    finally:
        if sess is not None:
            _fc92_cli_close(sess["proc"], sess["chunks"])
        row["unloads"] = {ns: _fc92_unload_ns(ctx, ns)}
    return row


# ---------------------------------------------------------------- audio legs

def _fc92_args(tag, node, media_class=True):
    """The host-safe arming shape: autoconnect=false on both streams,
    media.class=Audio/Sink on the capture side (without it the capture
    node has NO ports and cannot be fed)."""
    parts = [
        f"node.description={FILTERCHAIN_R92_PREFIX}_{tag}",
        "filter.graph={nodes=[" + node + "]}",
        "audio.channels=1", "audio.position=[MONO]",
        ("capture.props={node.name=" + FILTERCHAIN_R92_PREFIX + "_"
         + tag + "_in,node.autoconnect=false"
         + (",media.class=Audio/Sink" if media_class else "") + "}"),
        ("playback.props={node.name=" + FILTERCHAIN_R92_PREFIX + "_"
         + tag + "_out,node.autoconnect=false}"),
    ]
    return ",".join(parts)


def _fc92_node(label, ctl=None, config=None, name="f1", ntype="builtin"):
    s = f"{{type={ntype},name={name},label={label}"
    if config:
        s += ",config={" + ",".join(config) + "}"
    if ctl:
        s += ",control={" + ",".join(ctl) + "}"
    return s + "}"


def _fc92_analyze_dsp(ref_path, out_path):
    wr = _fc92_wav_read(ref_path)
    wo = _fc92_wav_read(out_path)
    xr, xo = wr["x"], wo["x"]
    sr, offr = _fc92_best_window(xr)
    so, offo = _fc92_best_window(xo)
    mr = _fc92_dft(sr, FILTERCHAIN_R92_FREQS)
    mo = _fc92_dft(so, FILTERCHAIN_R92_FREQS)
    return {"ref_bytes": wr["bytes"], "out_bytes": wo["bytes"],
            "ref_frames": wr["frames"], "out_frames": wo["frames"],
            "win_offsets": [offr, offo],
            "ref_stats": _fc92_sig_stats(xr),
            "out_stats": _fc92_sig_stats(xo),
            "ref_mags": {str(f): _fc92_f(mr[f], 8)
                         for f in FILTERCHAIN_R92_FREQS},
            "out_mags": {str(f): _fc92_f(mo[f], 8)
                         for f in FILTERCHAIN_R92_FREQS},
            "gain_db": {str(f): _fc92_db(mo[f], mr[f])
                        for f in FILTERCHAIN_R92_FREQS}}


def _fc92_analyze_ir(ref_path, out_path, thresh=1e-4):
    wr = _fc92_wav_read(ref_path)
    wo = _fc92_wav_read(out_path)
    xr, xo = wr["x"], wo["x"]
    r = {"ref_bytes": wr["bytes"], "out_bytes": wo["bytes"],
         "ref_frames": wr["frames"], "out_frames": wo["frames"],
         "ref_stats": _fc92_sig_stats(xr),
         "out_stats": _fc92_sig_stats(xo)}
    for tag, x in (("ref", xr), ("out", xo)):
        idx = np.nonzero(np.abs(x) > thresh)[0]
        r[f"{tag}_n_gt"] = int(len(idx))
        r[f"{tag}_first"] = ([int(idx[0]), _fc92_f(x[idx[0]], 7)]
                             if len(idx) else None)
        if len(idx):
            order = idx[np.argsort(-np.abs(x[idx]))]
            r[f"{tag}_top"] = [[int(i), _fc92_f(x[i], 7)]
                               for i in order[:6]]
    if r.get("ref_first") and r.get("out_first"):
        r["delta_samples"] = r["out_first"][0] - r["ref_first"][0]
        r["delta_mod_block"] = (r["delta_samples"]
                                % FILTERCHAIN_R92_BLOCKSIZE)
    if len(r.get("out_top") or []) >= 2:
        (i0, a0), (i1, a1) = r["out_top"][0], r["out_top"][1]
        r["peak_gap"] = i1 - i0
        r["peak_ratio"] = _fc92_f(a1 / a0, 6) if a0 else None
    if len(r.get("ref_top") or []) >= 1 and len(r.get("out_top") or []) >= 1:
        r["peak_delta"] = r["out_top"][0][0] - r["ref_top"][0][0]
    return r


def _fc92_residual(out_path, ir_path, stim_path, coarse=64, slack=128):
    """Full-convolution residual in s16 LSB at the best alignment lag:
    the POST capture compared sample-by-sample against the IR FILE's own
    quantised kernel x the quantised delta. The two pw-record taps are
    separate streams, so the lag is searched — but ONLY over alignments
    that contain (nearly) the whole expected convolution: a degenerate
    edge overlap of silence reads a fake 0.0 LSB (measured while
    building this seat)."""
    wo = _fc92_wav_read(out_path)
    wi = _fc92_wav_read(ir_path)
    ws = _fc92_wav_read(stim_path)
    xo, ir, st = wo["x"], wi["x"], ws["x"]
    e = np.convolve(st, ir)
    n = len(e)
    lo, hi = -slack, len(xo) - n + slack
    if hi <= lo:
        return {"alignment_error": f"capture too short ({len(xo)} < {n})"}
    need = n - slack

    def resid(lag):
        a = max(0, -lag)
        b = min(n, len(xo) - lag)
        if b - a < need:
            return None
        d = e[a:b] - xo[a + lag:b + lag]
        return float(np.max(np.abs(d))), d

    best = None
    for lag in range(lo, hi + 1, coarse):
        r = resid(lag)
        if r is not None and (best is None or r[0] < best[0]):
            best = (r[0], lag)
    if best is None:
        return {"alignment_error": "no lag with a near-full overlap"}
    for lag in range(max(lo, best[1] - coarse),
                     min(hi, best[1] + coarse) + 1):
        r = resid(lag)
        if r is not None and r[0] < best[0]:
            best = (r[0], lag)
    m, lag = best
    d = resid(lag)[1]
    lsb = 1.0 / 32768.0
    return {"max_residual_lsb": _fc92_f(m / lsb, 3), "lag": lag,
            "compared": int(len(d)),
            "n_gt_1lsb": int(np.count_nonzero(np.abs(d) > lsb)),
            "peak_expected": _fc92_f(np.max(np.abs(e)), 7),
            "ir_bytes": wi["bytes"], "stim_bytes": ws["bytes"]}


def _fc92_shift_ok(delta, want, tol=2):
    """The tap-shift law: a DIFFERENCE between the PRE and POST taps is
    stable only modulo the block quantum (measured +/-1024-sample
    jumps), so the arm is `delta == want + k*blocksize`."""
    if delta is None:
        return False, None
    ks = []
    for k in range(-4, 5):
        if abs(delta - (want + k * FILTERCHAIN_R92_BLOCKSIZE)) <= tol:
            ks.append(k)
    return bool(ks), ks


def _fc92_audio_attempt(ctx, tag, node, kind, stim, fmt="s16",
                        attempt=0, media_class=True):
    """One triple-bounded audio leg: mono null-sink driver -> chain
    capture side; chain playback side -> a SECOND null sink whose monitor
    is the POST tap (a stream-to-stream link has no driver on this host —
    both ends stay suspended and the capture is exact zeros; measured,
    recorded, and the reason this rig drives the POST side with a sink).
    PRE tap = driver monitor. Unique per-leg node names, name-verified
    unloads, RLIMIT_CORE=0 on every child."""
    ns = f"{FILTERCHAIN_R92_PREFIX}_{tag}_ns"
    ns2 = f"{FILTERCHAIN_R92_PREFIX}_{tag}_ns2"
    fin = f"{FILTERCHAIN_R92_PREFIX}_{tag}_in"
    fout = f"{FILTERCHAIN_R92_PREFIX}_{tag}_out"
    refn = f"{FILTERCHAIN_R92_PREFIX}_{tag}_ref"
    recn = f"{FILTERCHAIN_R92_PREFIX}_{tag}_rec"
    playn = f"{FILTERCHAIN_R92_PREFIX}_{tag}_play"
    scratch = Path(ctx["scratch"])
    refp = scratch / f"{tag}_{attempt}_ref.wav"
    outp = scratch / f"{tag}_{attempt}_out.wav"
    for p in (refp, outp):
        if p.exists():
            p.unlink()
    row = {"tag": tag, "attempt": attempt, "kind": kind, "fmt": fmt,
           "args": _fc92_args(tag, node, media_class=media_class)}
    ref = rec = play = None
    sess = None
    try:
        for name in (ns, ns2):
            leaf = _fc92_ns_load(ctx, name)
            row.setdefault("sinks", {})[name] = {
                "module_id": leaf.get("module_id"),
                "sink_seen": leaf.get("sink_seen"),
                "monitor_seen": leaf.get("monitor_seen")}
            if leaf.get("module_id") is None:
                row["gate"] = f"null sink {name} never enumerated"
                return row
        sess = _fc92_session_load(row["args"])
        row["load"] = {"var": sess["var"],
                       "loaded": "@module:" in sess["load_text"],
                       "load_text": _fc92_norm(sess["load_text"])[:500]}
        if sess["var"] is None:
            row["gate"] = "module did not load"
            row["errors"] = re.findall(r'Error: "([^"]+)"',
                                       sess["load_text"])[:3]
            return row
        time.sleep(0.5)
        fmt_args = [] if fmt == "s16" else ["--format", fmt]
        ref = _fc92_spawn(["pw-record", "--channels", "1", *fmt_args,
                           "-P", f"node.name={refn}",
                           "-P", "node.autoconnect=false", str(refp)])
        rec = _fc92_spawn(["pw-record", "--channels", "1", *fmt_args,
                           "-P", f"node.name={recn}",
                           "-P", "node.autoconnect=false", str(outp)])
        ctx["procs"].extend([p for p in (ref, rec) if p is not None])
        if ref is None or rec is None:
            row["gate"] = "pw-record spawn failed"
            return row
        time.sleep(0.7)
        row["links"] = {
            "feed": _fc92_link(f"{ns}:monitor_MONO", f"{fin}:playback_MONO"),
            "pre": _fc92_link(f"{ns}:monitor_MONO", f"{refn}:input_MONO"),
            "post": _fc92_link(f"{fout}:output_MONO",
                               f"{ns2}:playback_MONO"),
            "tap": _fc92_link(f"{ns2}:monitor_MONO", f"{recn}:input_MONO")}
        time.sleep(0.4)
        play = _fc92_spawn(["pw-play", "--target", ns,
                            "-P", f"node.name={playn}", str(stim)])
        if play is not None:
            ctx["procs"].append(play)
            t0 = time.monotonic()
            while play.poll() is None and time.monotonic() - t0 < 8.0:
                time.sleep(0.1)
        time.sleep(0.8)
    finally:
        for proc in (ref, rec):
            _fc92_reap(proc)
        if play is not None:
            _fc92_reap(play)
        if sess is not None:
            sent, txt = _fc92_session_cmd(
                sess, f"unload-module {sess['var']}", wait_s=2.5)
            row["unload_module"] = {"sent": sent,
                                    "text": _fc92_norm(txt)[:200]}
            full = _fc92_cli_close(sess["proc"], sess["chunks"])
        else:
            full = ""
        row["log_stats"] = _fc92_log_stats(full)
        row["err_lines"] = _fc92_log_lines(full, "[E]")
        row["warn_lines"] = _fc92_log_lines(full, "[W]")
        cls, hit = _fc92_errclass(full)
        row["error_class"] = cls
        row["error_hit"] = hit
        row["unloads"] = {nm: _fc92_unload_ns(ctx, nm)
                          for nm in (ns, ns2)}
    # ---- analysis
    if not (refp.exists() and outp.exists()):
        row["gate"] = "capture files missing"
        return row
    try:
        if kind == "ir":
            row["analysis"] = _fc92_analyze_ir(refp, outp)
        elif kind == "silent":
            wo = _fc92_wav_read(outp)
            wr = _fc92_wav_read(refp)
            row["analysis"] = {
                "ref_bytes": wr["bytes"], "out_bytes": wo["bytes"],
                "ref_stats": _fc92_sig_stats(wr["x"]),
                "out_stats": _fc92_sig_stats(wo["x"]),
                "ref_n_gt": int(np.count_nonzero(np.abs(wr["x"]) > 1e-4)),
                "out_nz_exact": int(np.count_nonzero(wo["x"]))}
        else:
            row["analysis"] = _fc92_analyze_dsp(refp, outp)
    except (ValueError, OSError) as exc:
        row["gate"] = f"analysis failed: {exc}"
        return row
    # ---- validity gate (a leg that cannot be measured is never green)
    a = row["analysis"]
    links = row.get("links") or {}
    row["links_ok"] = all((links.get(k) or {}).get("rc") == 0
                          for k in ("feed", "pre", "post", "tap"))
    if kind == "silent":
        row["valid"] = bool(a.get("ref_n_gt", 0) >= 1
                            and a.get("out_bytes", 0) > 1000)
    elif kind == "ir":
        row["valid"] = bool(a.get("ref_n_gt", 0) >= 1
                            and a.get("out_bytes", 0) > 1000)
    else:
        row["valid"] = bool(
            a.get("out_bytes", 0) > 1000
            and max((a.get("ref_mags") or {"0": 0}).values()) > 1e-6
            and max((a.get("out_mags") or {"0": 0}).values()) > 1e-6)
    return row


def _fc92_audio_leg(ctx, entry, tag, node, kind, stim, fmt="s16",
                    attempt_max=2, media_class=True):
    row = None
    for attempt in range(attempt_max):
        row = _fc92_audio_attempt(ctx, tag, node, kind, stim, fmt=fmt,
                                  attempt=attempt,
                                  media_class=media_class)
        for k, v in (row.pop("unloads", None) or {}).items():
            entry.setdefault("unloads", {})[k] = v
        if row.get("valid"):
            return row
        time.sleep(0.5)
    return row


def _fc92_leg_fail(failures, tag, row, why):
    failures.append(
        f"{tag}: {why} (attempts={row.get('attempt')} "
        f"links_ok={row.get('links_ok')} gate={row.get('gate')} "
        f"valid={row.get('valid')})")


# ------------------------------------------------------ entry 1: the arming

def _fc92_lifetime_leg(ctx, tag="life"):
    """The client-local lifetime + shape leg: nodes exported while the
    pw-cli session lives, 0 autoconnect edges, unload-module takes the
    VAR (the id is refused), the module dies with the session."""
    ns = f"{FILTERCHAIN_R92_PREFIX}_{tag}_ns"
    fin = f"{FILTERCHAIN_R92_PREFIX}_{tag}_in"
    fout = f"{FILTERCHAIN_R92_PREFIX}_{tag}_out"
    row = {"tag": tag}
    leaf = _fc92_ns_load(ctx, ns)
    row["sink"] = {"module_id": leaf.get("module_id"),
                   "sink_seen": leaf.get("sink_seen")}
    if leaf.get("module_id") is None:
        row["gate"] = "driver sink never enumerated"
        return row
    sess = sess2 = None
    try:
        sess = _fc92_session_load(_fc92_args(tag, _fc92_node("copy")))
        row["load"] = {"var": sess["var"],
                       "loaded": "@module:" in sess["load_text"],
                       "module_id": sess["module_id"]}
        if sess["var"] is None:
            row["gate"] = "module did not load"
            return row
        time.sleep(0.5)
        g = _fc92_graph()
        nin = _pactlmon_r85_node(g, fin)
        nout = _pactlmon_r85_node(g, fout)
        row["live_shape"] = {
            "nodes": [bool(nin), bool(nout)],
            "capture_class": (nin or {}).get("media_class"),
            "capture_ports": sorted(_fc92_ports(g, (nin or {}).get(
                "node_id")).keys()) if nin else None,
            "playback_ports": sorted(_fc92_ports(g, (nout or {}).get(
                "node_id")).keys()) if nout else None,
            "own_edges": _fc92_own_edges(g, (fin, fout)),
            "spdif_links": len(_fc92_spdif_links())}
        # the var/id law: unload-module takes the var
        sent, txt = _fc92_session_cmd(sess, f"unload-module "
                                            f"{sess['module_id']}",
                                      wait_s=2.0)
        row["id_unload"] = {"sent": sent, "text": _fc92_norm(txt)[:220],
                            "error_class": _fc92_errclass(txt)[0]}
        time.sleep(0.3)
        g = _fc92_graph()
        row["after_id_unload"] = {
            "capture_present": bool(_pactlmon_r85_node(g, fin)),
            "playback_present": bool(_pactlmon_r85_node(g, fout))}
        sent, txt = _fc92_session_cmd(sess, f"unload-module {sess['var']}",
                                      wait_s=2.0)
        row["var_unload"] = {"sent": sent, "text": _fc92_norm(txt)[:220]}
        time.sleep(0.3)
        g = _fc92_graph()
        row["after_var_unload"] = {
            "capture_present": bool(_pactlmon_r85_node(g, fin)),
            "playback_present": bool(_pactlmon_r85_node(g, fout))}
        # re-load in the same session, then quit: the module dies with it
        sess2 = _fc92_session_load(_fc92_args(tag + "b",
                                             _fc92_node("copy")))
        row["reload"] = {"var": sess2["var"]}
        time.sleep(0.4)
        g = _fc92_graph()
        row["after_reload"] = {
            "capture_present": bool(_pactlmon_r85_node(
                g, f"{FILTERCHAIN_R92_PREFIX}_{tag}b_in"))}
        _fc92_cli_close(sess2["proc"], sess2["chunks"])
        sess2 = None
        full = _fc92_cli_close(sess["proc"], sess["chunks"])
        sess = None
        row["log_stats"] = _fc92_log_stats(full)
    finally:
        for s in (sess, sess2):
            if s is not None and s["proc"].poll() is None:
                _fc92_cli_close(s["proc"], s["chunks"])
        row["unloads"] = {ns: _fc92_unload_ns(ctx, ns)}
        time.sleep(0.4)
        g = _fc92_graph()
        row["after_session_exit"] = {
            "capture_present": bool(_pactlmon_r85_node(g, fin)),
            "playback_present": bool(_pactlmon_r85_node(g, fout)),
            "reload_present": bool(_pactlmon_r85_node(
                g, f"{FILTERCHAIN_R92_PREFIX}_{tag}b_in")),
            "spdif_links": len(_fc92_spdif_links())}
    return row


def filterchain_arm_r92_probe():
    """The arming/shape/grammar/label lattice: client-local lifetime,
    the media.class port law, the node.autoconnect=false gate (0 edges),
    the args-grammar refusal classes, the 26/6 label table, the pw-cli
    stdin classes and the convolver's silent-at-load half."""
    failures, legs = [], {}
    entry = _fc92_entry_head("r92a filter-chain arming lattice")
    tools = {t: shutil.which(t) for t in
             ("pw-cli", "pw-play", "pw-record", "pw-dump", "pw-link",
              "pactl")}
    entry["tools"] = tools
    entry["not_armed_by_policy"] = [
        "node.autoconnect=true (would link a seat stream to the "
        "operator's default sink — the scout measured that class once; "
        "this seat declines to repeat it)",
        "the pipewire -c filter-chain.conf route (starts a second "
        "daemon — refused on a shared host)"]
    if not all(tools.values()):
        return _fc92_block(
            entry, failures,
            f"missing tools: {[t for t, p in tools.items() if not p]}")
    if not (entry.get("daemon") or {}).get("ok"):
        # a wedged/saturated daemon makes the WHOLE entry unmeasurable:
        # it is named as a block AND as a failure — a battery that
        # measured nothing must never read as green.
        failures.append(
            "daemon unreachable or saturated: pactl info "
            f"rc={(entry.get('daemon') or {}).get('exit_code')} "
            f"killed={(entry.get('daemon') or {}).get('killed_at_bound')} "
            f"wall={(entry.get('daemon') or {}).get('wall_s')}s — the "
            "entry is unmeasurable")
        return _fc92_block(
            entry, failures,
            "daemon unreachable or saturated: pactl info "
            f"rc={(entry.get('daemon') or {}).get('exit_code')} "
            f"killed={(entry.get('daemon') or {}).get('killed_at_bound')} "
            f"wall={(entry.get('daemon') or {}).get('wall_s')}s")
    ctx = _fc92_ctx()
    try:
        legs["a_lifetime"] = _fc92_lifetime_leg(ctx)
        for k, v in (legs["a_lifetime"].pop("unloads", None) or {}).items():
            entry.setdefault("unloads", {})[k] = v
        # ---- shape: media.class decides whether the capture side has
        #      ports at all (the shipped configs' class is load-bearing)
        legs["a_ports_none"] = _fc92_shape_leg(ctx, "noclass",
                                               media_class=False)
        for k, v in (legs["a_ports_none"].pop("unloads", None)
                     or {}).items():
            entry.setdefault("unloads", {})[k] = v
        legs["a_ports_sink"] = _fc92_shape_leg(ctx, "sinkclass",
                                               media_class=True)
        for k, v in (legs["a_ports_sink"].pop("unloads", None)
                     or {}).items():
            entry.setdefault("unloads", {})[k] = v
        # ---- grammar refusals (load-only, one session each)
        legs["a_links_quoted"] = _fc92_load_leg(
            ctx, "lq",
            "filter.graph={nodes=[{type=builtin,name=f1,label=copy},"
            "{type=builtin,name=f2,label=copy}],"
            'links=[{output="f1:Out",input="f2:In"}]}')
        legs["a_links_bare"] = _fc92_load_leg(
            ctx, "lb",
            "filter.graph={nodes=[{type=builtin,name=f1,label=copy},"
            "{type=builtin,name=f2,label=copy}],"
            "links=[{output=f1:Out,input=f2:In}]}")
        legs["a_hash_uri"] = _fc92_load_leg(
            ctx, "hsh",
            'filter.graph={nodes=[{type=lv2,name=f1,label=x,'
            'plugin="http://example.org/r92a#none"}]}')
        legs["a_graph_num"] = _fc92_load_leg(ctx, "gn", "filter.graph=42")
        legs["a_graph_empty"] = _fc92_load_leg(
            ctx, "ge", "filter.graph={nodes=[]}")
        legs["a_bad_label"] = _fc92_load_leg(
            ctx, "bl", "filter.graph={nodes=[{type=builtin,name=f1,"
                       "label=not_a_filter}]}")
        legs["a_bad_type"] = _fc92_load_leg(
            ctx, "bt", "filter.graph={nodes=[{type=r92a_bogus,name=f1,"
                       "label=copy}]}")
        legs["a_ffmpeg"] = _fc92_load_leg(
            ctx, "ff", "filter.graph={nodes=[{type=ffmpeg,name=f1,"
                       "label=copy}]}")
        legs["a_ladspa"] = _fc92_load_leg(
            ctx, "ld", 'filter.graph={nodes=[{type=ladspa,name=f1,'
                       'label=x,plugin="g2reverb"}]}')
        # ---- the control-key law: a space is expressible ONLY quoted
        legs["a_bare_spaced"] = _fc92_load_leg(
            ctx, "bs", "filter.graph={nodes=[{type=builtin,name=f1,"
                       "label=delay,config={max-delay=0.05},"
                       "control={Delay (s)=0.01}}]}")
        legs["a_quoted_spaced"] = _fc92_load_leg(
            ctx, "qs", "filter.graph={nodes=[{type=builtin,name=f1,"
                       "label=delay,config={max-delay=0.05},"
                       'control={"Delay (s)"=0.01}}]}')
        legs["a_typo_ctl"] = _fc92_load_leg(
            ctx, "tc", "filter.graph={nodes=[{type=builtin,name=f1,"
                       "label=delay,config={max-delay=0.05},"
                       "control={Delay=0.01}}]}")
        # ---- the type inventory (load-only; the sofa config trap is a
        #      silent-config class, the ebur128 label is exact)
        legs["a_ebur128"] = _fc92_load_leg(
            ctx, "eb", "filter.graph={nodes=[{type=ebur128,name=f1,"
                       "label=ebur128}]}")
        legs["a_ebur128_bad"] = _fc92_load_leg(
            ctx, "ebx", "filter.graph={nodes=[{type=ebur128,name=f1,"
                        "label=loudness}]}")
        legs["a_sofa"] = _fc92_load_leg(
            ctx, "sf", "filter.graph={nodes=[{type=sofa,name=f1,"
                       "label=spatializer}]}")
        legs["a_sofa_cfg"] = _fc92_load_leg(
            ctx, "sfc", 'filter.graph={nodes=[{type=sofa,name=f1,'
                        'label=spatializer,config={filename='
                        '"/nonexistent/r92a.sofa"}}]}')
        # ---- the label table, 2 reps each
        labs = {}
        for rep in (0, 1):
            for lab in FILTERCHAIN_R92_LABELS_OK + \
                    FILTERCHAIN_R92_LABELS_FAIL:
                key = f"{lab}#{rep}"
                labs[key] = _fc92_label_leg(ctx, f"lab{rep}", lab, rep)
        legs["a_labels"] = labs
        # ---- the pw-cli stdin classes
        legs["a_eof_null"] = _fc92_run(["pw-cli"], 8.0)
        legs["a_eof_pipe"] = _fc92_run(["pw-cli"],
                                       FILTERCHAIN_R92_EOF_S,
                                       stdin_data=b"")
        legs["a_quit"] = _fc92_run(["pw-cli"], 8.0,
                                   stdin_data=b"quit\n")
        # ---- the silent-at-load half of the convolver class
        legs["a_load_noconfig"] = _fc92_load_leg(
            ctx, "lnc", "filter.graph={nodes=[{type=builtin,name=f1,"
                        "label=convolver}]}")
        legs["a_load_missing"] = _fc92_load_leg(
            ctx, "lms", "filter.graph={nodes=[{type=builtin,name=f1,"
                        "label=convolver,config={filename="
                        '"/nonexistent/r92a_ir.wav"}}]}')
        legs["a_load_dbg5"] = _fc92_load_leg(
            ctx, "l5", "filter.graph={nodes=[{type=builtin,name=f1,"
                       "label=convolver}]}",
            debug="5", wait_s=6.0, keep_full=True)
    finally:
        _fc92_teardown(entry, failures, ctx)
    # ------------------------------ verdicts
    l = legs["a_lifetime"]
    if l.get("gate"):
        entry.setdefault("coverage_blocked", []).append(
            f"a_lifetime: {l['gate']}")
    else:
        sh = l.get("live_shape") or {}
        if not all(sh.get("nodes") or []):
            _fc92_leg_fail(failures, "a_lifetime", l,
                           "the loaded chain's two stream nodes are not "
                           "both exported to the graph")
        if sh.get("capture_class") != "Audio/Sink" or \
                sorted(sh.get("capture_ports") or []) != \
                ["monitor_MONO", "playback_MONO"]:
            _fc92_leg_fail(failures, "a_lifetime", l,
                           "the capture side is not the expected "
                           f"Audio/Sink with both ports: {sh}")
        if sh.get("own_edges"):
            _fc92_leg_fail(failures, "a_lifetime", l,
                           "node.autoconnect=false still produced links: "
                           f"{sh.get('own_edges')}")
        if l.get("after_id_unload", {}).get("capture_present") is not True \
                or l.get("after_id_unload", {}).get(
                    "playback_present") is not True:
            _fc92_leg_fail(failures, "a_lifetime", l,
                           "the module id was accepted by unload-module "
                           "(the nodes did not survive it) — the var is "
                           "the only handle")
        if (l.get("id_unload") or {}).get("error_class") != \
                "fc92_unload_unknown":
            _fc92_leg_fail(failures, "a_lifetime", l,
                           "the id unload did not carry the "
                           "unknown-module refusal class: "
                           f"{l.get('id_unload')}")
        if l.get("var_unload") is None or \
                l.get("after_var_unload", {}).get("capture_present") \
                is not False or \
                l.get("after_var_unload", {}).get("playback_present") \
                is not False:
            _fc92_leg_fail(failures, "a_lifetime", l,
                           "unload-module <var> did not destroy the nodes")
        if l.get("after_reload", {}).get("capture_present") is not True:
            _fc92_leg_fail(failures, "a_lifetime", l,
                           "the re-loaded chain is not exported")
        ae = l.get("after_session_exit") or {}
        if ae.get("capture_present") or ae.get("playback_present") or \
                ae.get("reload_present"):
            _fc92_leg_fail(failures, "a_lifetime", l,
                           "nodes survived the pw-cli session — the "
                           "module is not client-local")
    l = legs["a_ports_none"]
    if not l.get("loaded") or \
            l.get("capture_class") != "Stream/Input/Audio" or \
            "playback_MONO" in (l.get("capture_ports") or []) or \
            (l.get("feed_link") or {}).get("rc") == 0:
        _fc92_leg_fail(failures, "a_ports_none", l,
                       "without media.class the capture side is not the "
                       "unfeedable Stream/Input/Audio class (no "
                       "playback_MONO port, the feed link cannot bind)")
    l = legs["a_ports_sink"]
    if not l.get("loaded") or \
            l.get("capture_class") != "Audio/Sink" or \
            sorted(l.get("capture_ports") or []) != \
            ["monitor_MONO", "playback_MONO"] or \
            (l.get("feed_link") or {}).get("rc") != 0:
        _fc92_leg_fail(failures, "a_ports_sink", l,
                       "media.class=Audio/Sink does not yield a feedable "
                       "playback_MONO+monitor_MONO pair")
    if l.get("own_edges"):
        _fc92_leg_fail(failures, "a_ports_sink", l,
                       f"the sink-class shape produced autoconnect "
                       f"edges: {l.get('own_edges')}")
    # grammar refusals
    if not legs["a_links_quoted"].get("loaded"):
        _fc92_leg_fail(failures, "a_links_quoted", legs["a_links_quoted"],
                       "the documented quoted-port link form does not "
                       "load")
    for tag in ("a_links_bare", "a_hash_uri", "a_graph_num",
                "a_graph_empty", "a_bad_label", "a_bad_type", "a_ffmpeg",
                "a_ladspa", "a_bare_spaced"):
        l = legs[tag]
        if l.get("loaded"):
            _fc92_leg_fail(failures, tag, l,
                           "the refusal class loaded — the grammar law "
                           "is broken")
    want_cls = {"a_links_bare": "fc92_props_parse",
                "a_hash_uri": "fc92_props_parse",
                "a_graph_num": "fc92_graph_not_object",
                "a_graph_empty": "fc92_graph_no_nodes",
                "a_bad_label": "fc92_label_missing",
                "a_bad_type": "fc92_type_missing",
                "a_ffmpeg": "fc92_type_missing",
                "a_ladspa": "fc92_ladspa_missing",
                "a_bare_spaced": "fc92_props_parse"}
    for tag, cls in want_cls.items():
        if legs[tag].get("error_class") != cls:
            _fc92_leg_fail(failures, tag, legs[tag],
                           f"expected error class {cls}, got "
                           f"{legs[tag].get('error_class')}")
    if not legs["a_quoted_spaced"].get("loaded") or \
            legs["a_quoted_spaced"].get("warn_lines"):
        _fc92_leg_fail(failures, "a_quoted_spaced",
                       legs["a_quoted_spaced"],
                       "the quoted spaced control key does not load clean")
    if not legs["a_typo_ctl"].get("loaded") or \
            legs["a_typo_ctl"].get("error_class") != "fc92_control_typo":
        _fc92_leg_fail(failures, "a_typo_ctl", legs["a_typo_ctl"],
                       "a typo'd control name is not the warning-only "
                       "class")
    for tag in ("a_ebur128", "a_sofa", "a_sofa_cfg"):
        if not legs[tag].get("loaded"):
            _fc92_leg_fail(failures, tag, legs[tag],
                           "the present type/label does not load")
    if legs["a_ebur128_bad"].get("loaded") or \
            legs["a_ebur128_bad"].get("error_class") != \
            "fc92_label_missing":
        _fc92_leg_fail(failures, "a_ebur128_bad",
                       legs["a_ebur128_bad"],
                       "the ebur128 label is not exact")
    # the label table
    labs = legs["a_labels"]
    for lab in FILTERCHAIN_R92_LABELS_OK:
        for rep in (0, 1):
            l = labs.get(f"{lab}#{rep}") or {}
            if not l.get("loaded"):
                _fc92_leg_fail(failures, f"label:{lab}#{rep}", l,
                               "a table label did not load")
    for lab in FILTERCHAIN_R92_LABELS_FAIL:
        for rep in (0, 1):
            l = labs.get(f"{lab}#{rep}") or {}
            if l.get("loaded") or l.get("error_class") != \
                    "fc92_label_missing":
                _fc92_leg_fail(failures, f"label:{lab}#{rep}", l,
                               "a non-label loaded, or refused without "
                               "the cannot-create-label class")
    # pw-cli stdin classes
    l = legs["a_eof_null"]
    if l.get("exit_code") != -6 or l.get("error_class") != \
            "fc92_abort_loop":
        _fc92_leg_fail(failures, "a_eof_null", l,
                       "file EOF is not the SIGABRT+remove_from_poll "
                       "class")
    l = legs["a_eof_pipe"]
    if not l.get("killed_at_bound"):
        _fc92_leg_fail(failures, "a_eof_pipe", l,
                       "pipe EOF did not hang (the scout's 'aborts on "
                       "EOF' is a file-EOF-only property)")
    l = legs["a_quit"]
    if l.get("exit_code") != 0 or l.get("killed_at_bound"):
        _fc92_leg_fail(failures, "a_quit", l, "quit is not rc 0")
    # silent-at-load half
    for tag in ("a_load_noconfig", "a_load_missing"):
        l = legs[tag]
        if not l.get("loaded") or l["log_stats"]["E"] or \
                l["log_stats"]["W"]:
            _fc92_leg_fail(failures, tag, l,
                           "the silent convolver config does not load "
                           "with E=0/W=0 (the load half of the silent "
                           "class)")
    l = legs["a_load_dbg5"]
    if not l.get("loaded") or l["log_stats"]["E"] or \
            l["log_stats"]["W"] or l["log_stats"]["lines"] < 500:
        _fc92_leg_fail(failures, "a_load_dbg5", l,
                       "debug 5 does not show the same silent load "
                       "(E=0/W=0 over a full log)")
    entry["legs"] = legs
    entry["failures"] = failures
    return entry


# ------------------------------------------------- entry 2: the DSP lattice

def filterchain_dsp_r92_probe():
    """The transfer-function lattice against an independent analytic RBJ
    reference: unity `copy`, lowpass/peaking/notch rows, `param_eq` ==
    the equivalent `bq_peaking`, the Gain/Q clamp edges, the >Nyquist
    pass-through guard, the exact-silence `Freq` arms and the inert
    port surfaces (b0..a2, Gain, bq_raw)."""
    failures, legs = [], {}
    entry = _fc92_entry_head("r92a filter-chain DSP lattice")
    tools = {t: shutil.which(t) for t in
             ("pw-cli", "pw-play", "pw-record", "pw-dump", "pw-link",
              "pactl")}
    entry["tools"] = tools
    entry["rbj_reference"] = {
        "lp_1000_0707": _fc92_rbj_gains("lp", 1000, 0.707),
        "pk_1000_q1_plus6": _fc92_rbj_gains("pk", 1000, 1.0, 6.0),
        "pk_1000_q20_plus20": _fc92_rbj_gains("pk", 1000, 20.0, 20.0),
        "pk_1000_q1_minus120": _fc92_rbj_gains("pk", 1000, 1.0, -120.0),
        "nt_1000_q1": _fc92_rbj_gains("nt", 1000, 1.0)}
    if not all(tools.values()):
        return _fc92_block(
            entry, failures,
            f"missing tools: {[t for t, p in tools.items() if not p]}")
    if not (entry.get("daemon") or {}).get("ok"):
        # a wedged/saturated daemon makes the WHOLE entry unmeasurable:
        # it is named as a block AND as a failure — a battery that
        # measured nothing must never read as green.
        failures.append(
            "daemon unreachable or saturated: pactl info "
            f"rc={(entry.get('daemon') or {}).get('exit_code')} "
            f"killed={(entry.get('daemon') or {}).get('killed_at_bound')} "
            f"wall={(entry.get('daemon') or {}).get('wall_s')}s — the "
            "entry is unmeasurable")
        return _fc92_block(
            entry, failures,
            "daemon unreachable or saturated: pactl info "
            f"rc={(entry.get('daemon') or {}).get('exit_code')} "
            f"killed={(entry.get('daemon') or {}).get('killed_at_bound')} "
            f"wall={(entry.get('daemon') or {}).get('wall_s')}s")
    ctx = _fc92_ctx()
    stim = ctx["stim"]["tone"]
    legs_spec = [
        ("d_copy", _fc92_node("copy")),
        ("d_lp", _fc92_node("bq_lowpass",
                            ["Freq=1000.0", "Q=0.707"])),
        ("d_pk6", _fc92_node("bq_peaking",
                             ["Freq=1000.0", "Q=1.0", "Gain=6.0"])),
        ("d_peq", _fc92_node(
            "param_eq", config=[
                "filters=[{type=bq_peaking,freq=1000.0,gain=6.0,q=1.0}]"])),
        ("d_nt", _fc92_node("bq_notch", ["Freq=1000.0", "Q=1.0"])),
        ("d_f0", _fc92_node("bq_lowpass",
                            ["Freq=0.0", "Q=0.707"])),
        ("d_fneg", _fc92_node("bq_lowpass",
                              ["Freq=-1000.0", "Q=0.707"])),
        ("d_fhi", _fc92_node("bq_lowpass",
                             ["Freq=49000.0", "Q=0.707"])),
        ("d_g20", _fc92_node("bq_peaking",
                             ["Freq=1000.0", "Q=20.0", "Gain=20.0"])),
        ("d_g20x", _fc92_node("bq_peaking",
                              ["Freq=1000.0", "Q=20.0", "Gain=20.5"])),
        ("d_gneg", _fc92_node("bq_peaking",
                              ["Freq=1000.0", "Q=1.0", "Gain=-120.0"])),
        ("d_gnegx", _fc92_node("bq_peaking",
                               ["Freq=1000.0", "Q=1.0",
                                "Gain=-120.5"])),
        ("d_q707", _fc92_node("bq_peaking",
                              ["Freq=1000.0", "Q=0.707",
                               "Gain=20.0"])),
        ("d_q10", _fc92_node("bq_peaking",
                             ["Freq=1000.0", "Q=10.0", "Gain=20.0"])),
        ("d_q1e9", _fc92_node("bq_peaking",
                              ["Freq=1000.0", "Q=1e9", "Gain=20.0"])),
        ("d_qneg", _fc92_node("bq_peaking",
                              ["Freq=1000.0", "Q=-1.0", "Gain=20.0"])),
        ("d_raw", _fc92_node("bq_raw")),
        ("d_coeff", _fc92_node("bq_lowpass",
                               ["Freq=1000.0", "Q=0.707", "b0=1.0",
                                "b1=0.0", "b2=0.0", "a0=1.0", "a1=0.0",
                                "a2=0.0"])),
        ("d_lp_g6", _fc92_node("bq_lowpass",
                               ["Freq=1000.0", "Q=0.707",
                                "Gain=6.0"])),
    ]
    # the min-side clamp witness needs a LOUDER single-tone probe: with
    # the 4-tone stimulus a -140 dB request lands under the s16 floor,
    # where a clamped and an unclamped response are indistinguishable.
    # RBJ(-140)@200 Hz = -66.4 dB vs RBJ(-120)@200 = -46.4 dB: a 20 dB
    # separation, both measurable against a 0.5-full-scale tone.
    CLAMP_EXTRA = [("d_gneg140",
                    _fc92_node("bq_peaking",
                               ["Freq=1000.0", "Q=1.0", "Gain=-140.0"]))]
    try:
        for tag, node in legs_spec:
            kind = "silent" if tag in ("d_f0", "d_fneg", "d_raw") \
                else "dsp"
            legs[tag] = _fc92_audio_leg(ctx, entry, tag, node, kind,
                                        stim)
        for tag, node in CLAMP_EXTRA:
            legs[tag] = _fc92_audio_leg(ctx, entry, tag, node, "dsp",
                                        ctx["stim"]["tone200"])
    finally:
        _fc92_teardown(entry, failures, ctx)

    def gains(tag):
        return (legs[tag].get("analysis") or {}).get("gain_db") or {}

    def close(tag, other, probes, tol):
        a, b = gains(tag), gains(other)
        bad = []
        for p in probes:
            k = str(p)
            if a.get(k) is None or b.get(k) is None or \
                    abs(a[k] - b[k]) > tol:
                bad.append({"hz": p, "a": a.get(k), "b": b.get(k)})
        return bad

    def vs_rbj(tag, label, f0, q, gain_db, probes, tol):
        """The receipt keys the measured gains by str, the analytic
        reference by int — the first run compared str against int and
        read `rbj: None` for every probe (a green-looking arm that
        never compared anything)."""
        got, ref, bad = gains(tag), _fc92_rbj_gains(label, f0, q,
                                                   gain_db), []
        for p in probes:
            k, r = str(p), ref.get(int(p))
            if got.get(k) is None or r is None or \
                    abs(got[k] - r) > tol:
                bad.append({"hz": p, "measured": got.get(k), "rbj": r})
        return bad

    # ---- per-leg validity first: an unmeasurable leg is a failure
    for tag, _ in legs_spec + CLAMP_EXTRA:
        l = legs[tag]
        if l.get("gate"):
            _fc92_leg_fail(failures, tag, l, f"blocked: {l['gate']}")
        elif not l.get("valid"):
            if not l.get("links_ok"):
                entry.setdefault("coverage_blocked", []).append(
                    f"{tag}: taps never bound — contention class")
            else:
                _fc92_leg_fail(failures, tag, l,
                               "the leg did not measure (valid=False)")
    # ---- the laws
    if any(abs(v) > 0.05 for v in gains("d_copy").values()) or \
            len(gains("d_copy")) != 5:
        _fc92_leg_fail(failures, "d_copy", legs["d_copy"],
                       f"copy is not unity: {gains('d_copy')}")
    bad = vs_rbj("d_lp", "lp", 1000, 0.707, 0.0,
                 (200, 1000, 4000, 12000), 0.06)
    if bad:
        _fc92_leg_fail(failures, "d_lp", legs["d_lp"],
                       f"the lowpass does not reproduce RBJ: {bad}")
    bad = vs_rbj("d_pk6", "pk", 1000, 1.0, 6.0,
                 (200, 1000, 4000, 12000, 20000), 0.06)
    if bad:
        _fc92_leg_fail(failures, "d_pk6", legs["d_pk6"],
                       f"the peaking row does not reproduce RBJ: {bad}")
    if gains("d_pk6").get("1000") is None or \
            abs(gains("d_pk6")["1000"] - 6.0) > 0.06:
        _fc92_leg_fail(failures, "d_pk6", legs["d_pk6"],
                       "bq_peaking(+6) is not +6.000 dB at fc")
    bad = close("d_peq", "d_pk6", (200, 1000, 4000, 12000, 20000), 0.05)
    if bad:
        _fc92_leg_fail(failures, "d_peq", legs["d_peq"],
                       "param_eq != the equivalent bq_peaking: "
                       f"{bad}")
    nt = gains("d_nt")
    if nt.get("1000") is None or nt["1000"] > -60 or \
            abs((nt.get("200") or 0) - (-0.184)) > 0.5 or \
            abs((nt.get("4000") or 0) - (-0.284)) > 0.5:
        _fc92_leg_fail(failures, "d_nt", legs["d_nt"],
                       f"the notch row fails (fc bin must be <= -60 dB, "
                       f"the skirts pass): {nt}")
    for tag in ("d_f0", "d_fneg", "d_raw"):
        a = legs[tag].get("analysis") or {}
        if a.get("out_nz_exact") != 0 or a.get("out_bytes", 0) < 1000:
            _fc92_leg_fail(failures, tag, legs[tag],
                           "the silence class is not exact digital "
                           f"zeros: {a.get('out_nz_exact')}")
    if any(abs(v) > 0.05 for v in gains("d_fhi").values()):
        _fc92_leg_fail(failures, "d_fhi", legs["d_fhi"],
                       "Freq above Nyquist is not a pass-through "
                       f"(an unguarded biquad would read -3.012 dB at "
                       f"1 kHz): {gains('d_fhi')}")
    if gains("d_g20").get("1000") is None or \
            abs(gains("d_g20")["1000"] - 20.0) > 0.06:
        _fc92_leg_fail(failures, "d_g20", legs["d_g20"],
                       "Gain=20 is not +20.000 dB at fc")
    bad = close("d_g20x", "d_g20", (200, 1000, 4000, 12000, 20000), 0.05)
    if bad:
        _fc92_leg_fail(failures, "d_g20x", legs["d_g20x"],
                       f"Gain=20.5 is not clamped to 20: {bad}")
    bad = vs_rbj("d_gneg", "pk", 1000, 1.0, -120.0,
                 (200, 4000, 12000, 20000), 0.5)
    if bad or (gains("d_gneg").get("1000") or 0) > -60:
        _fc92_leg_fail(failures, "d_gneg", legs["d_gneg"],
                       "Gain=-120 does not match RBJ(-120) on the "
                       f"skirts / is not annihilated at fc: {bad}")
    # the deep-attenuation cells carry a +/-0.6 dB instrument spread
    # under contention (measured: 200/4000/12000 deltas 0.03/0.57/0.00),
    # so the min-side clamp is pinned by the -140 leg below and this
    # boundary cell is armed loosely.
    bad = close("d_gnegx", "d_gneg", (200, 4000, 12000, 20000), 1.0)
    if bad:
        _fc92_leg_fail(failures, "d_gnegx", legs["d_gnegx"],
                       f"Gain=-120.5 is not clamped to -120: {bad}")
    g140 = gains("d_gneg140")
    if g140.get("200") is None or \
            abs(g140["200"] - (-46.362)) > 1.5 or \
            abs(g140["200"] - (-66.362)) < 5.0:
        _fc92_leg_fail(failures, "d_gneg140", legs["d_gneg140"],
                       "Gain=-140 is not clamped to the advertised "
                       "-120 min (an unclamped request would read "
                       f"~-66.4 dB at 200 Hz): {g140}")
    if gains("d_q707").get("1000") is None or \
            abs(gains("d_q707")["1000"] - 20.0) > 0.06:
        _fc92_leg_fail(failures, "d_q707", legs["d_q707"],
                       "the Q=0.707 reference row fails at fc")
    if gains("d_q10").get("1000") is None or \
            abs(gains("d_q10")["1000"] - 20.0) > 0.06:
        _fc92_leg_fail(failures, "d_q10", legs["d_q10"],
                       "Q=10 is not +20.000 dB at fc")
    bad = close("d_q1e9", "d_q10", (200, 1000, 4000, 12000, 20000), 0.05)
    if bad:
        _fc92_leg_fail(failures, "d_q1e9", legs["d_q1e9"],
                       f"Q=1e9 is not clamped to Q=10: {bad}")
    # The boundary's row 15 ("Q=-1 -> identical to the 0.707 default") is
    # FALSIFIED on this host: Q=-1 measures a BROADBAND ~+19 dB gain
    # (19.015/18.979/19.289/18.729/19.289), not a peaking curve and not
    # the default. The arm pins the falsification + the measured shape;
    # the mechanism (the RBJ formula with q=-1 gives 1.543/20.0/2.216/
    # 0.182/0.013, which does not match) is recorded, not explained.
    qn, q7 = gains("d_qneg"), gains("d_q707")
    if abs((qn.get("200") or 0) - (q7.get("200") or 0)) < 3.0 or \
            max((qn.get(k) for k in qn), default=None) is None:
        _fc92_leg_fail(failures, "d_qneg", legs["d_qneg"],
                       "Q=-1 still measures the 0.707 default: "
                       f"{qn} vs {q7}")
    if max(qn.values()) - min(qn.values()) > 2.0:
        _fc92_leg_fail(failures, "d_qneg", legs["d_qneg"],
                       "the negative-Q response is not the measured "
                       f"broadband gain: {qn}")
    bad = close("d_coeff", "d_lp", (200, 1000, 4000, 12000), 0.06)
    if bad:
        _fc92_leg_fail(failures, "d_coeff", legs["d_coeff"],
                       "the advertised b0..a2 ports are not inert: "
                       f"{bad}")
    bad = close("d_lp_g6", "d_lp", (200, 1000, 4000, 12000), 0.06)
    if bad:
        _fc92_leg_fail(failures, "d_lp_g6", legs["d_lp_g6"],
                       "Gain is not inert on bq_lowpass: "
                       f"{bad}")
    entry["legs"] = legs
    entry["failures"] = failures
    return entry


# ------------------------- entry 3: the convolver + delay lattice

def filterchain_ir_r92_probe():
    """The convolver/delay lattice: sample-exactness to the s16 LSB
    against the file's own quantised kernel, the rate/channel/clip
    limits, the delay map with its over-max clamp, and the silent class
    at ACTIVATION (exact digital zeros + an [E] line the load never
    shows)."""
    failures, legs = [], {}
    entry = _fc92_entry_head("r92a filter-chain convolver/delay lattice")
    tools = {t: shutil.which(t) for t in
             ("pw-cli", "pw-play", "pw-record", "pw-dump", "pw-link",
              "pactl")}
    entry["tools"] = tools
    if not all(tools.values()):
        return _fc92_block(
            entry, failures,
            f"missing tools: {[t for t, p in tools.items() if not p]}")
    if not (entry.get("daemon") or {}).get("ok"):
        # a wedged/saturated daemon makes the WHOLE entry unmeasurable:
        # it is named as a block AND as a failure — a battery that
        # measured nothing must never read as green.
        failures.append(
            "daemon unreachable or saturated: pactl info "
            f"rc={(entry.get('daemon') or {}).get('exit_code')} "
            f"killed={(entry.get('daemon') or {}).get('killed_at_bound')} "
            f"wall={(entry.get('daemon') or {}).get('wall_s')}s — the "
            "entry is unmeasurable")
        return _fc92_block(
            entry, failures,
            "daemon unreachable or saturated: pactl info "
            f"rc={(entry.get('daemon') or {}).get('exit_code')} "
            f"killed={(entry.get('daemon') or {}).get('killed_at_bound')} "
            f"wall={(entry.get('daemon') or {}).get('wall_s')}s")
    ctx = _fc92_ctx()
    st = ctx["stim"]
    conv = lambda ir=None, extra=None: _fc92_node(          # noqa: E731
        "convolver", config=(([f"filename={ir}"] if ir else [])
                             + list(extra or [])))
    dly = lambda s: _fc92_node(                             # noqa: E731
        "delay", config=["max-delay=0.05"],
        ctl=[f'"Delay (s)"={s}'])
    specs = [
        ("i_2tap", conv(st["ir_2tap"]), "ir", st["delta"]),
        ("i_gain05", conv(st["ir_2tap"], ["gain=0.5"]), "ir",
         st["delta"]),
        ("i_d100", conv(st["ir_d100"]), "ir", st["delta"]),
        ("i_decay512", conv(st["ir_decay512"]), "ir", st["delta"]),
        ("i_441", conv(st["ir_441"]), "ir", st["delta"]),
        ("i_stereo", conv(st["ir_stereo"]), "ir", st["delta"]),
        ("i_clip", conv(st["ir_2tap"], ["gain=4.0"]), "ir",
         st["delta"]),
        ("i_noconfig", conv(), "silent", st["delta"]),
        ("i_missing", conv(st["bad_path"]), "silent", st["delta"]),
        ("i_empty", conv(st["ir_empty"]), "silent", st["delta"]),
        ("i_text", conv(st["ir_text"]), "silent", st["delta"]),
        ("i_dir", conv(st["ir_dir"]), "silent", st["delta"]),
        ("d_10ms", dly("0.01"), "ir", st["delta"]),
        ("d_1ms", dly("0.001"), "ir", st["delta"]),
        ("d_50ms", dly("0.05"), "ir", st["delta"]),
        ("d_over", dly("0.1"), "ir", st["delta"]),
        ("d_over2", dly("0.06"), "ir", st["delta"]),
    ]
    try:
        for tag, node, kind, stim in specs:
            legs[tag] = _fc92_audio_leg(ctx, entry, tag, node, kind,
                                        stim)
        legs["i_residual"] = {}
        for tag, ir_key in (("i_2tap", "ir_2tap"),
                            ("i_decay512", "ir_decay512"),
                            ("i_d100", "ir_d100")):
            l = legs[tag]
            if not l.get("valid"):
                continue
            try:
                legs["i_residual"][tag] = _fc92_residual(
                    ctx["scratch"] / f"{tag}_{l.get('attempt', 0)}_out.wav",
                    st[ir_key], st["delta"])
            except (ValueError, OSError) as exc:
                legs["i_residual"][tag] = {"error": str(exc)[:120]}
    finally:
        _fc92_teardown(entry, failures, ctx)
    # ------------------------------ verdicts
    for tag, _, _, _ in specs:
        l = legs[tag]
        if l.get("gate"):
            _fc92_leg_fail(failures, tag, l, f"blocked: {l['gate']}")
        elif not l.get("valid"):
            if not l.get("links_ok"):
                entry.setdefault("coverage_blocked", []).append(
                    f"{tag}: taps never bound — contention class")
            else:
                _fc92_leg_fail(failures, tag, l,
                               "the leg did not measure (valid=False)")

    def an(tag):
        return legs[tag].get("analysis") or {}

    # ---- convolver: the IR kernel is reproduced
    a = an("i_2tap")
    if a.get("peak_gap") != 64 or \
            a.get("peak_ratio") is None or \
            abs(a["peak_ratio"] - 0.5) > 0.0015 or \
            a.get("out_top", [[None, None]])[0][1] is None or \
            abs(a["out_top"][0][1] - 0.99994) > 0.002:
        _fc92_leg_fail(failures, "i_2tap", legs["i_2tap"],
                       "the 2-tap IR is not reproduced (gap 64, ratio "
                       f"0.5, first tap 0.999939): {a}")
    ok, ks = _fc92_shift_ok(a.get("delta_samples"), 0)
    if not ok:
        _fc92_leg_fail(failures, "i_2tap", legs["i_2tap"],
                       "the IR[0] tap is not at the reference position "
                       f"(mod {FILTERCHAIN_R92_BLOCKSIZE}): "
                       f"delta={a.get('delta_samples')}")
    a = an("i_gain05")
    if a.get("peak_gap") != 64 or \
            a.get("out_top", [[None, None]])[0][1] is None or \
            abs(a["out_top"][0][1] - 0.49997) > 0.002:
        _fc92_leg_fail(failures, "i_gain05", legs["i_gain05"],
                       "convolver gain=0.5 does not scale the kernel "
                       f"exactly: {a}")
    a = an("i_d100")
    ok, ks = _fc92_shift_ok(a.get("delta_samples"), 100)
    if not ok or a.get("out_n_gt") != 1:
        _fc92_leg_fail(failures, "i_d100", legs["i_d100"],
                       "the delta@100 IR is not a single impulse at "
                       f"+100 samples: {a}")
    a = an("i_441")
    # the peak offset is a PRE/POST difference like every other tap
    # shift: block-quantised (measured 1134 = 1024 + 110)
    ok, _ks = _fc92_shift_ok(a.get("peak_delta"), 110)
    if not ok or (a.get("out_n_gt") or 0) < 30:
        _fc92_leg_fail(failures, "i_441", legs["i_441"],
                       "a 44.1 kHz IR in a 48 kHz graph is not the "
                       "resampled 47-tap kernel peaked at ~+110 "
                       f"(mod {FILTERCHAIN_R92_BLOCKSIZE}): {a}")
    a = an("i_stereo")
    ok, ks = _fc92_shift_ok(a.get("delta_samples"), 10)
    if not ok or a.get("out_n_gt") != 1:
        _fc92_leg_fail(failures, "i_stereo", legs["i_stereo"],
                       "a 2-channel IR does not silently use channel 0 "
                       f"only: {a}")
    a = an("i_clip")
    if a.get("out_stats", {}).get("max_abs") is None or \
            not (0.99 <= a["out_stats"]["max_abs"] <= 1.0) or \
            a.get("peak_gap") != 64:
        _fc92_leg_fail(failures, "i_clip", legs["i_clip"],
                       "gain=4.0 does not hard-clip at full scale: "
                       f"{a}")
    # ---- the residual arms (the file's own quantised kernel)
    for tag, want in (("i_2tap", 1.0), ("i_decay512", 1.0),
                      ("i_d100", 0.5)):
        r = (legs["i_residual"] or {}).get(tag) or {}
        if r.get("error"):
            _fc92_leg_fail(failures, f"i_residual:{tag}", legs[tag],
                           f"residual failed: {r['error']}")
        elif r.get("max_residual_lsb") is None or \
                r["max_residual_lsb"] > want or \
                r.get("n_gt_1lsb", 1) != 0:
            _fc92_leg_fail(failures, f"i_residual:{tag}", legs[tag],
                           "the full-convolution residual exceeds "
                           f"{want} LSB / has samples over 1 LSB: {r}")
    # ---- the silent class at activation
    silent_cls = {"i_noconfig": "fc92_convolver_cfg",
                  "i_missing": "fc92_convolver_file",
                  "i_empty": "fc92_convolver_file",
                  "i_text": "fc92_convolver_file",
                  "i_dir": "fc92_convolver_file"}
    for tag, cls in silent_cls.items():
        a = an(tag)
        if a.get("out_nz_exact") != 0:
            _fc92_leg_fail(failures, tag, legs[tag],
                           "the silent convolver class is not exact "
                           f"digital zeros: nz={a.get('out_nz_exact')}")
        if legs[tag].get("error_class") != cls:
            _fc92_leg_fail(failures, tag, legs[tag],
                           "the activation error class is not "
                           f"{cls}: {legs[tag].get('error_class')} "
                           f"({legs[tag].get('error_hit')})")
    # ---- the delay map (block-quantised differences)
    for tag, want in (("d_1ms", 48), ("d_10ms", 480),
                      ("d_50ms", 2400), ("d_over", 2431),
                      ("d_over2", 2431)):
        a = an(tag)
        ok, ks = _fc92_shift_ok(a.get("delta_samples"), want)
        if not ok or a.get("out_n_gt") != 1:
            _fc92_leg_fail(failures, tag, legs[tag],
                           f"the delay is not {want} samples "
                           f"(mod {FILTERCHAIN_R92_BLOCKSIZE}): "
                           f"delta={a.get('delta_samples')}")
    entry["legs"] = legs
    entry["failures"] = failures
    return entry


# --------------------- entry 4: wpexec + the absent-class inventory

def _fc92_wpx_write(ctx, name, body):
    p = Path(ctx["scratch"]) / f"{name}.lua"
    p.write_text(body)
    return p


def _fc92_wpx_leg(ctx, name, body, timeout_s=8.0):
    p = _fc92_wpx_write(ctx, name, body)
    return _fc92_run(["wpexec", str(p)], timeout_s, keep_chars=1200)


def _fc92_wpx_bg(ctx, name, body, observe=(0.9, 1.7), bound=8.0):
    """The LocalModule leg: a live graph while the interpreter lives,
    self-cleaned on exit. Nodes are sampled, never inferred."""
    p = _fc92_wpx_write(ctx, name, body)
    rec = {"script": str(p)}
    try:
        proc = subprocess.Popen(["wpexec", str(p)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.DEVNULL,
                                start_new_session=True,
                                preexec_fn=_pwctl_r86_no_core)
    except OSError as exc:
        rec["spawn_error"] = str(exc)[:160]
        return rec
    ctx["procs"].append(proc)
    t0 = time.monotonic()
    snaps = []
    for at in observe:
        left = at - (time.monotonic() - t0)
        if left > 0:
            time.sleep(left)
        g = _fc92_graph()
        own = sorted(n.get("name") for n in (g.get("nodes") or {}).values()
                     if n.get("name") and
                     FILTERCHAIN_R92_PREFIX in n["name"])
        snaps.append({"at_s": at, "own_nodes": own,
                      "own_edges": len(_fc92_own_edges(g, own)),
                      "spdif_links": len(_fc92_spdif_links())})
    killed = False
    try:
        out, err = proc.communicate(timeout=max(
            0.5, bound - (time.monotonic() - t0)))
    except subprocess.TimeoutExpired:
        killed = True
        _alsapw_r84_killpg(proc)
        out, err = proc.communicate()
    outt = out.decode(errors="replace")
    errt = err.decode(errors="replace")
    rec.update({"exit_code": proc.returncode, "killed_at_bound": killed,
                "snapshots": snaps,
                "stdout": _fc92_norm(outt)[:800],
                "stderr": _fc92_norm(errt)[:400]})
    time.sleep(0.5)
    g = _fc92_graph()
    rec["own_nodes_after"] = sorted(
        n.get("name") for n in (g.get("nodes") or {}).values()
        if n.get("name") and FILTERCHAIN_R92_PREFIX in n["name"])
    return rec


def _fc92_dir_scan(root):
    """Walk a directory tree -> (files, dirs, *.so count)."""
    files, dirs, sos = [], [], 0
    for base, dnames, fnames in os.walk(root):
        for d in dnames:
            dirs.append(os.path.join(base, d))
        for f in fnames:
            files.append(os.path.join(base, f))
            if f.endswith(".so"):
                sos += 1
    return files, dirs, sos


def filterchain_wpx_r92_probe():
    """wpexec's script-side loader (LocalModule -> a live, self-cleaning
    graph; the bare `Lua runtime error` classes; the hanging empty
    script) plus the read-only absent-class inventory (ffmpeg has no SPA
    plugin, LADSPA's search path is empty, LV2 holds no DSP plugin, the
    shipped virtual-surround config references an unshipped IR dir)."""
    failures, legs = [], {}
    entry = _fc92_entry_head("r92a wpexec + absent-class inventory")
    tools = {t: shutil.which(t) for t in
             ("wpexec", "pw-cli", "pw-dump", "pactl", "strings")}
    entry["tools"] = tools
    if not all(tools.values()):
        return _fc92_block(
            entry, failures,
            f"missing tools: {[t for t, p in tools.items() if not p]}")
    if not (entry.get("daemon") or {}).get("ok"):
        # a wedged/saturated daemon makes the WHOLE entry unmeasurable:
        # it is named as a block AND as a failure — a battery that
        # measured nothing must never read as green.
        failures.append(
            "daemon unreachable or saturated: pactl info "
            f"rc={(entry.get('daemon') or {}).get('exit_code')} "
            f"killed={(entry.get('daemon') or {}).get('killed_at_bound')} "
            f"wall={(entry.get('daemon') or {}).get('wall_s')}s — the "
            "entry is unmeasurable")
        return _fc92_block(
            entry, failures,
            "daemon unreachable or saturated: pactl info "
            f"rc={(entry.get('daemon') or {}).get('exit_code')} "
            f"killed={(entry.get('daemon') or {}).get('killed_at_bound')} "
            f"wall={(entry.get('daemon') or {}).get('wall_s')}s")
    ctx = _fc92_ctx()
    try:
        legs["w_print"] = _fc92_wpx_leg(
            ctx, "w_print",
            'print("r92a hello from wpexec")\nCore.quit()\n')
        legs["w_globals"] = _fc92_wpx_leg(
            ctx, "w_globals",
            'print("Core="..type(Core).." LocalModule="..'
            'type(LocalModule).." Settings="..type(Settings)..'
            '" require_api="..tostring(require_api))\nCore.quit()\n')
        legs["w_rawget"] = _fc92_wpx_leg(
            ctx, "w_rawget",
            "local x = rawget(_G, 'Core')\nprint(tostring(x))\n"
            "Core.quit()\n")
        legs["w_require_api"] = _fc92_wpx_leg(
            ctx, "w_req",
            'Core.require_api("support.settings")\nCore.quit()\n')
        legs["w_settings"] = _fc92_wpx_leg(
            ctx, "w_settings",
            'print("restore-props="..tostring('
            "Settings.get_boolean('node.stream.restore-props')))\n"
            "Core.quit()\n")
        lm_args = _fc92_args("wlm", _fc92_node("copy"))
        assert "]]" not in lm_args
        legs["w_localmodule"] = _fc92_wpx_bg(
            ctx, "w_lm",
            f"local args = [[{lm_args}]]\n"
            'local ok, mod = pcall(LocalModule, '
            '"libpipewire-module-filter-chain", args)\n'
            'print("pcall ok="..tostring(ok).." mod="..tostring(mod))\n'
            "Core.timeout_add(2500, Core.quit)\n")
        legs["w_lm_bad_module"] = _fc92_wpx_leg(
            ctx, "w_lmb",
            'local ok, mod = pcall(LocalModule, '
            '"libpipewire-module-r92a_nope", "")\n'
            'print("pcall ok="..tostring(ok).." mod="..tostring(mod))\n'
            "Core.quit()\n")
        bad_args = _fc92_args("wlmx", _fc92_node("not_a_filter"))
        legs["w_lm_bad_label"] = _fc92_wpx_leg(
            ctx, "w_lml",
            f"local args = [[{bad_args}]]\n"
            'local ok, mod = pcall(LocalModule, '
            '"libpipewire-module-filter-chain", args)\n'
            'print("pcall ok="..tostring(ok).." mod="..tostring(mod))\n'
            "Core.quit()\n")
        legs["w_noquit"] = _fc92_wpx_leg(
            ctx, "w_noquit", 'print("no quit here")\n', timeout_s=4.0)
        legs["w_empty"] = _fc92_wpx_leg(ctx, "w_empty", "",
                                        timeout_s=4.0)
        legs["w_syntax"] = _fc92_wpx_leg(ctx, "w_syntax",
                                         "this is not lua\n")
        legs["w_missing"] = _fc92_run(
            ["wpexec", "/nonexistent/r92a_missing.lua"], 8.0)
        legs["w_noargv"] = _fc92_run(["wpexec"], 8.0)
        # ---- the absent-class inventory (read-only)
        try:
            fg = sorted(os.listdir(FILTERCHAIN_R92_FG_DIR))
        except OSError as exc:
            fg = [f"<unreadable: {exc.__class__.__name__}>"]
        spa_files, _spa_dirs, _spa_sos = _fc92_dir_scan(
            FILTERCHAIN_R92_SPA_DIR)
        legs["v_spa"] = {
            "filter_graph_dir": fg,
            "filter_graph_count": len(fg),
            "spa_ffmpeg_hits": sorted(os.path.basename(f) for f in
                                      spa_files
                                      if "ffmpeg" in f or "avfilter" in f),
            "spa_file_count": len(spa_files)}
        legs["v_ladspa"] = {
            d: (sorted(os.listdir(d)) if os.path.isdir(d) else None)
            for d in FILTERCHAIN_R92_LADSPA_DIRS}
        legs["v_ladspa"]["absent_dirs"] = sorted(
            d for d, v in legs["v_ladspa"].items() if v is None)
        try:
            lv2_bundles = sorted(os.listdir(FILTERCHAIN_R92_LV2_DIR))
        except OSError as exc:
            lv2_bundles = [f"<unreadable: {exc.__class__.__name__}>"]
        _lv2_files, _lv2_dirs, lv2_sos = _fc92_dir_scan(
            FILTERCHAIN_R92_LV2_DIR)
        legs["v_lv2"] = {"bundle_count": len(lv2_bundles),
                         "so_count": lv2_sos,
                         "bundles_head": lv2_bundles[:8]}
        # the shipped virtual-surround config references an IR dir that
        # is not shipped (the silent-chain mechanism, read-only half)
        conf = Path(FILTERCHAIN_R92_PW_DIR) / "filter-chain" / \
            "sink-virtual-surround-5.1-kemar.conf"
        refs = []
        if conf.is_file():
            text = conf.read_text(errors="replace")
            refs = sorted(set(re.findall(
                r"hrir[a-z0-9_]*/[A-Za-z0-9_.\-]+", text)))
        hits = []
        for base, _dn, fnames in os.walk(FILTERCHAIN_R92_PW_DIR):
            for f in fnames:
                if "kemar" in f.lower() or "hesuvi" in f.lower():
                    hits.append(os.path.join(base, f))
        legs["v_kemar"] = {
            "conf_exists": conf.is_file(),
            "conf_refs": refs,
            "refs_exist": {r: (Path(FILTERCHAIN_R92_PW_DIR) / "filter-chain"
                               / r).exists() for r in refs},
            "kemar_hesuvi_files_under_pipewire": sorted(hits)}
    finally:
        _fc92_teardown(entry, failures, ctx)
    # ------------------------------ verdicts
    l = legs["w_print"]
    if l.get("exit_code") != 0 or "r92a hello from wpexec" not in \
            (l.get("stdout") or ""):
        _fc92_leg_fail(failures, "w_print", l,
                       "the trivial wpexec script does not run rc 0")
    l = legs["w_globals"]
    if l.get("exit_code") != 0 or \
            "Core=table LocalModule=function Settings=table " \
            "require_api=nil" not in (l.get("stdout") or ""):
        _fc92_leg_fail(failures, "w_globals", l,
                       "the wpexec global namespace is not "
                       "table/function/table/nil")
    for tag in ("w_rawget", "w_require_api"):
        l = legs[tag]
        if l.get("exit_code") != 70 or l.get("error_class") != \
                "fc92_wpx_runtime":
            _fc92_leg_fail(failures, tag, l,
                           "the bare `Lua runtime error` class fails "
                           "(rc 70, no location)")
    l = legs["w_settings"]
    if l.get("exit_code") != 0 or \
            not re.search(r"restore-props=(true|false)",
                          l.get("stdout") or ""):
        _fc92_leg_fail(failures, "w_settings", l,
                       "the Settings API is not reachable from wpexec")
    l = legs["w_localmodule"]
    live = [s for s in (l.get("snapshots") or []) if s.get("own_nodes")]
    if not live or l.get("own_nodes_after") != [] or \
            any(s.get("own_edges") for s in (l.get("snapshots") or [])):
        _fc92_leg_fail(failures, "w_localmodule", l,
                       "LocalModule does not build a live, "
                       "link-free, self-cleaning graph")
    for tag in ("w_lm_bad_module", "w_lm_bad_label"):
        l = legs[tag]
        if l.get("exit_code") != 0 or \
                "pcall ok=true mod=nil" not in (l.get("stdout") or ""):
            _fc92_leg_fail(failures, tag, l,
                           "a bad module/label is not the silent "
                           "pcall ok=true mod=nil class")
    for tag in ("w_noquit", "w_empty"):
        l = legs[tag]
        if not l.get("killed_at_bound"):
            _fc92_leg_fail(failures, tag, l,
                           "the script did not hang (no Core.quit is "
                           "unbounded; an empty script hangs)")
    for tag, cls in (("w_syntax", "fc92_wpx_compile"),
                     ("w_missing", "fc92_wpx_locate"),
                     ("w_noargv", "fc92_wpx_locate")):
        l = legs[tag]
        if l.get("exit_code") != 70 or l.get("error_class") != cls:
            _fc92_leg_fail(failures, tag, l,
                           f"the rc-70 {cls} class fails")
    l = legs["v_spa"]
    if "libspa-filter-graph.so" not in l["filter_graph_dir"] or \
            l["spa_ffmpeg_hits"] or l["filter_graph_count"] != 6:
        _fc92_leg_fail(failures, "v_spa", {}, 
                       "the SPA filter-graph inventory is not the six "
                       f"measured plugins with no ffmpeg: {l}")
    l = legs["v_ladspa"]
    if sorted(l.get("absent_dirs") or []) != \
            sorted(FILTERCHAIN_R92_LADSPA_DIRS):
        _fc92_leg_fail(failures, "v_ladspa", {},
                       "the LADSPA search path is not empty "
                       f"(dirs: {l})")
    l = legs["v_lv2"]
    if l.get("bundle_count", 0) < 1 or l.get("so_count", 1) != 0:
        _fc92_leg_fail(failures, "v_lv2", {},
                       "the LV2 inventory is not spec-bundles-only "
                       f"(no DSP plugin): {l}")
    l = legs["v_kemar"]
    if not l.get("conf_exists") or not l.get("conf_refs") or \
            any(l.get("refs_exist", {}).values()):
        _fc92_leg_fail(failures, "v_kemar", {},
                       "the shipped virtual-surround config does not "
                       "reference an unshipped IR path: "
                       f"{l}")
    entry["legs"] = legs
    entry["failures"] = failures
    return entry

