# r94: the SoX_ng v14.8.0.1 EFFECT/DSP LATTICE — the province's own
#     content-production toolchain (ffmpeg/ffprobe/**sox**) measured as
#     an EFFECT machine for the first time. Rounds r62-r75 used sox only
#     as a decoder/detector (`sox --i`, `-V6 -n stat`, transport forks);
#     not one effect row existed. This family pins the boundary-surviving
#     half of the r94 scout's 18 proposed rows / 15 headline claims:
#
#     (1) DETERMINISM IS A PRECISION TRACKING CONSEQUENCE. Auto-dither is
#         inserted iff (no user `dither`) and not `-D` and tracked precision
#         > output precision and output precision < 24 — so a default s16
#         effect that changes a sample is time-seeded-TPDF nondeterministic,
#         while `-D` makes it exact, s24/s32 output suppresses it entirely,
#         and integer/unity operations (`gain 0`, `copy`, `rate <same>`,
#         `pad %50`) are byte-identical to the input. `-R` (not `-D`) is
#         what makes an EXPLICIT `dither` reproducible; `-D -R` == `-R`.
#     (2) THE ROUNDING LAWS: `gain`/`vol <dB>`/`vol <p>` round to nearest
#         (±0.5 LSB, mismatch 0 vs rint); the `vol` AMPLITUDE form rounds
#         CEIL — so `vol 0.5` != `vol -6.0206 d` (exactly 1 LSB apart).
#     (3) THE RESAMPLER: output length is within ±1 frame of in·out/in_rate
#         with NO single rounding rule fitting the .5 rows; same-rate is a
#         true no-op; pitch is preserved; and the `-q` content hazard folds
#         23 kHz to 21.1 kHz at ~-6.3 dB — **the scout's "-v rejects at
#         -130 dB" claim is FALSIFIED by the r94 boundary and is NOT armed
#         here**: `-v`/`-u` sit at the same ~-104 dB band as the default and
#         `-h` (byte-distinct but level-identical), and the only ~-129.6 dB
#         row in the lattice is the 20 kHz stimulus default leg. The
#         falsified form is re-armed at its corrected values plus an
#         explicit disarm guard (`rate_130db_home`).
#     (4) THE CHANNEL LAWS: `remix 1` SELECTS channel 1 (it does not sum);
#         auto downmix is floor((L+R+1)/2) (`channels 1` is the same bytes);
#         `-m` is the raw sum; `-p` is rint((L+R)/sqrt2).
#     (5) THE ENVELOPE LAWS: `fade` TRUNCATES at its stop positional (silent
#         data loss); the log curve is exactly 100 dB per span; the six
#         curve types are a pinned table; `trim`'s `s` suffix means SAMPLES;
#         `repeat N` is N ADDITIONAL copies; `pad %50` is a silent no-op;
#         `silence`'s below-periods side keeps window_size-1 = rate/50-1
#         samples.
#     (6) `-G` is not a limiter (only the `-D` equality is reproducible),
#         `stat`'s RMS is a per-channel quadratic mean, and `stat -e`'s
#         loudness row is the one r93-adjacent cell (SoX's own
#         implementation, no libebur128 linkage) — bounded to one row.
#
# A NEW parallel ledger family; prior rows untouched; every r76-r93 guard
# inherited (bounded process groups with SIGTERM->SIGKILL escalation,
# RLIMIT_CORE=0, continuously drained captures, seat-owned r94a_<pid>
# names, never set-default-*). **This family is FILE-ONLY**: it creates no
# PipeWire object, loads no module, opens no device, and never invokes sox
# with -d/-p/play/rec — the entry census arms that absence at entry and at
# exit (own_prefix objects == 0) as a negative control, so a leak shows up
# as a failure rather than a silent green. The family lock is a FIXED
# corpus/live/ path (the r84 F1 3-seat consensus — a $TMPDIR-scoped lock
# does not exclude cross-TMPDIR same-family runs); it matters here because
# every leg writes into the family's own scratch dir.
#
# Every armed law is a boundary survival. The scout's falsified rows are
# dropped or re-armed at the boundary's corrected values, and each such
# re-arm carries its correction in the leg note. Volatile fields (wall
# times, loadavg, absolute paths, sha of nondeterministic legs) are
# recorded, never armed. The cross-seat witness compares this seat's
# deterministic output bytes against the r94 scout's own receipts when
# they are readable on this tree; when they are absent the witness is
# recorded as coverage_blocked, never as a pass.

SOX_R94 = "/usr/bin/sox"
SOX_R94_FFMPEG = "/usr/bin/ffmpeg"
SOX_R94_PID = os.getpid()
SOX_R94_TAG = f"r94a_{SOX_R94_PID}"
SOX_R94_RATE = 48000
SOX_R94_WALL = 25.0
SOX_R94_OUT_CAP = 1 << 22          # drained-capture byte cap
SOX_R94_REPS = 3
SOX_R94_SCOUT = ROOT / "live" / "r94-scout" / "receipts"
# The band metric's calibration constant: the family's own Hann-windowed
# band-power estimator, offset so it lands in the SCOUT'S band convention (a
# 0.5-amplitude tone reads 0.0 dB). The constant is calibrated on the scout's
# published table across six independent rows — 23 kHz default/-q/-a/-m -a and
# the 20 kHz default row at two bands — where it reproduces every value to
# <0.02 dB, and the calibration is re-armed per run by the cross-seat METRIC
# comparison (never taken on faith).
SOX_R94_BAND_OFFSET_DB = 2.5403
SOX_R94_REF_METRIC_KEYS = ("frames", "peak_db", "rms_db", "band_21100hz_db",
                           "band_20000hz_db", "band_997hz_db",
                           "mismatch_vs_rint_formula", "max_abs_diff_vs_formula",
                           "clipped_ge32766", "clipped_ge32767", "max_abs_err",
                           "err_rms", "byte_identical_to_input")

# r94-local error classes, checked in this order (specific before generic).
# The measured spellings use a BACKTICK quote (`-R'), not an apostrophe.
_SOX_R94_ERR_CLASSES = (
    ("sox_r94_parse", r"sox FAIL trim: cannot parse position[^\n]*"),
    ("sox_r94_opt", r"sox FAIL dither: invalid option[^\n]*"),
    ("sox_r94_usage", r"sox FAIL gain: usage:[^\n]*"),
    ("sox_r94_silence_args", r"sox FAIL silence: below-periods requires[^\n]*"),
    ("sox_r94_repeat_range", r"sox FAIL repeat: num_repeats[^\n]*"),
    ("sox_r94_rate_override", r"sox FAIL rate: override options[^\n]*"),
    ("sox_r94_fail", r"sox FAIL[^\n]*"),
)


def _sox_r94_scratch():
    d = ROOT / "live" / "r94-author" / "scratch"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sox_r94_sha(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()


def _sox_r94_family_lock():
    """Same-family exclusion at a FIXED lane path — the r84 F1 3-seat
    consensus (never $TMPDIR; cross-TMPDIR same-family runs must still
    exclude). It matters here because every leg writes into the family's own
    scratch dir, so two concurrent runs would collide on the same product
    paths. A second --probe-sox-r94 waits HERE."""
    path = ROOT / "live" / "measure_audio-sox-r94.lock"
    try:
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    except OSError:
        return None
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        os.ftruncate(fd, 0)
        os.write(fd, f"pid={SOX_R94_PID} tag={SOX_R94_TAG} "
                     f"file_only=1\n".encode())
    except OSError:
        pass
    return fd


def _sox_r94_norm(text):
    """Volatile-field scrub for recorded text: the absolute scratch path
    of THIS run, plus the r94-foreign path classes a co-tenant seat's
    receipts can leak into a stderr line."""
    s = text or ""
    s = s.replace(str(ROOT), "<ROOT>")
    s = re.sub(r"r94a_[A-Za-z0-9_]+", "r94a_<own>", s)
    s = re.sub(r"\b\d+\.\d{4,} s\b", "<wall> s", s)
    return s


def _sox_r94_errclass(text):
    for name, pat in _SOX_R94_ERR_CLASSES:
        m = re.search(pat, text or "")
        if m:
            return name, m.group(0).strip()[:120]
    return None, None


def _sox_r94_limit():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def _sox_r94_killpg(proc, sig=signal.SIGKILL):
    try:
        os.killpg(os.getpgid(proc.pid), sig)
    except (ProcessLookupError, PermissionError, OSError):
        pass


def _sox_r94_spawn(argv, timeout=SOX_R94_WALL, env=None, wd=None):
    """One triple-bounded sox spawn: wall cap, drained-capture byte cap,
    RLIMIT_CORE=0, own session + process-group kill escalation. sox writes
    its product to a FILE (never a device), so stdout is /dev/null and only
    stderr is drained."""
    rec = {"argv": [str(a) for a in argv]}
    try:
        proc = subprocess.Popen(
            [str(a) for a in argv], stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
            env=env, cwd=wd, start_new_session=True,
            preexec_fn=_sox_r94_limit)
    except OSError as exc:
        rec["spawn_error"] = str(exc)[:160]
        rec["exit_code"] = None
        return rec
    try:
        os.set_blocking(proc.stderr.fileno(), False)
    except OSError:
        pass
    t0 = time.monotonic()
    buf = bytearray()
    killed = False
    while True:
        try:
            chunk = os.read(proc.stderr.fileno(), 65536)
        except (BlockingIOError, OSError):
            chunk = b""
        if chunk and len(buf) < SOX_R94_OUT_CAP:
            buf += chunk[:SOX_R94_OUT_CAP - len(buf)]
        if proc.poll() is not None:
            break
        if time.monotonic() - t0 >= timeout:
            killed = True
            _sox_r94_killpg(proc)
            proc.wait()
            break
        time.sleep(0.005)
    try:
        rest = proc.stderr.read() or b""
    except OSError:
        rest = b""
    if rest and len(buf) < SOX_R94_OUT_CAP:
        buf += rest[:SOX_R94_OUT_CAP - len(buf)]
    errt = bytes(buf).decode(errors="replace")
    cls, hit = _sox_r94_errclass(errt)
    rec.update({"exit_code": proc.returncode,
                "signal": (signal.Signals(-proc.returncode).name
                           if (proc.returncode or 0) < 0 else None),
                "killed_at_bound": killed,
                "wall_s": round(time.monotonic() - t0, 3),
                "stderr": _sox_r94_norm(errt)[:400],
                "stderr_text": _sox_r94_norm(errt)[:2 << 20],
                "stderr_bytes": len(errt),
                "error_class": cls, "error_hit": hit})
    return rec


# ------------------------------------------------------- own RIFF I/O ----
# sox never sits in the measurement path of a sox product: the family's
# own parser reads every output (the scout's control leg cross-checked an
# own reader against `sox -t f32 -` at max abs diff 0.0 over 96 000
# floats; the same construction is reused here).

def _sox_r94_write_pcm16(path, data_i16, rate):
    arr = np.asarray(data_i16)
    if arr.ndim == 1:
        arr = arr[:, None]
    frames, channels = arr.shape
    body = arr.astype("<i2").tobytes()
    block = channels * 2
    fmt = struct.pack("<HHIIHH", 1, channels, rate, rate * block, block, 16)
    chunks = b"fmt " + struct.pack("<I", len(fmt)) + fmt
    chunks += b"data" + struct.pack("<I", len(body)) + body
    riff = b"WAVE" + chunks
    Path(path).write_bytes(b"RIFF" + struct.pack("<I", len(riff)) + riff)


def _sox_r94_write_f32(path, data_f, rate):
    arr = np.asarray(data_f)
    if arr.ndim == 1:
        arr = arr[:, None]
    frames, channels = arr.shape
    body = arr.astype("<f4").tobytes()
    block = channels * 4
    fmt = struct.pack("<HHIIHH", 3, channels, rate, rate * block, block, 32)
    chunks = b"fmt " + struct.pack("<I", len(fmt)) + fmt
    chunks += b"fact" + struct.pack("<I", 4) + struct.pack("<I", frames)
    chunks += b"data" + struct.pack("<I", len(body)) + body
    riff = b"WAVE" + chunks
    Path(path).write_bytes(b"RIFF" + struct.pack("<I", len(riff)) + riff)


def _sox_r94_read(path):
    """Own RIFF parser -> (float64 (frames, ch) sample matrix, meta).

    Handles PCM s16/s24/s32 and IEEE float32; the sample matrix is scaled
    to [-1, 1) so every metric is scale-free. A non-RIFF product raises,
    and the caller records that as a leg-level blockage."""
    raw = Path(path).read_bytes()
    if len(raw) < 12 or raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise ValueError(f"not RIFF/WAVE: {path}")
    pos, fmt, data = 12, None, None
    while pos + 8 <= len(raw):
        cid = raw[pos:pos + 4]
        size = int.from_bytes(raw[pos + 4:pos + 8], "little")
        body = raw[pos + 8:pos + 8 + size]
        if cid == b"fmt ":
            fmt = body
        elif cid == b"data":
            data = body
        pos += 8 + size + (size & 1)
    if fmt is None or data is None:
        raise ValueError(f"missing fmt/data: {path}")
    tag, channels, rate, _br, _ba, bits = struct.unpack("<HHIIHH", fmt[:16])
    sub = None
    if tag == 0xFFFE and len(fmt) >= 26:
        sub = int.from_bytes(fmt[24:26], "little")
    eff = sub if sub is not None else tag
    if eff == 3 and bits == 32:
        arr = np.frombuffer(data[:len(data) - (len(data) % (4 * channels))],
                            dtype="<f4").astype(np.float64)
        scale = 1.0
    elif eff == 1 and bits == 16:
        arr = np.frombuffer(data[:len(data) - (len(data) % (2 * channels))],
                            dtype="<i2").astype(np.float64)
        scale = 32768.0
    elif eff == 1 and bits == 32:
        arr = np.frombuffer(data[:len(data) - (len(data) % (4 * channels))],
                            dtype="<i4").astype(np.float64)
        scale = 2147483648.0
    elif eff == 1 and bits == 24:
        b = np.frombuffer(data[:len(data) - (len(data) % (3 * channels))],
                          dtype=np.uint8).reshape(-1, 3)
        v = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8)
             | (b[:, 2].astype(np.int32) << 16))
        v = np.where(v & 0x800000, v - 0x1000000, v)
        arr = v.astype(np.float64)
        scale = 8388608.0
    else:
        raise ValueError(f"unsupported fmt tag={eff} bits={bits}")
    frames = arr.size // channels
    arr = arr[:frames * channels].reshape(frames, channels) / scale
    return arr, {"channels": channels, "rate": rate, "bits": bits,
                 "fmt_tag": eff, "frames": frames}


def _sox_r94_db(x):
    x = float(x)
    if not np.isfinite(x) or x <= 0.0:
        return None
    return round(20.0 * np.log10(x), 6)


def _sox_r94_metrics(path):
    """Own metrics on one sox product: frames/channels/rate/bits, per-channel
    peak/rms dBFS, first-8 sample ints, and the whole-file int sample matrix
    handed back for formula comparisons."""
    arr, meta = _sox_r94_read(path)
    m = {"frames": meta["frames"], "channels": meta["channels"],
         "rate": meta["rate"], "bits": meta["bits"], "fmt_tag": meta["fmt_tag"]}
    if meta["frames"] == 0:
        m.update({"peak_db": [None] * meta["channels"],
                  "rms_db": [None] * meta["channels"]})
    else:
        peak = np.abs(arr).max(axis=0)
        rms = np.sqrt((arr ** 2).mean(axis=0))
        m["peak_db"] = [_sox_r94_db(p) for p in peak]
        m["rms_db"] = [_sox_r94_db(r) for r in rms]
    first = (arr[:8] * (2 ** (meta["bits"] - 1))).round().astype("int64")
    m["first8_ints"] = [[int(v) for v in row] for row in first]
    return m, arr


def _sox_r94_band_db(arr, rate, freq, half_hz=10.0):
    """Hann-windowed BAND level over +/- half_hz, in the scout's band
    convention (see SOX_R94_BAND_OFFSET_DB). An own estimator (sox never sits
    in the measurement path), so every rate row compares like-for-like across
    the option lattice; the published table's values are re-derived by the
    cross-seat metric law rather than assumed."""
    x = np.asarray(arr).reshape(-1)
    if x.size == 0:
        return None
    w = np.hanning(x.size)
    n = 1 << int(np.ceil(np.log2(max(x.size, 16))))
    spec = np.abs(np.fft.rfft(x * w, n))
    freqs = np.fft.rfftfreq(n, 1.0 / rate)
    sel = (freqs >= freq - half_hz) & (freqs <= freq + half_hz)
    if not sel.any():
        return None
    power = float((spec[sel] ** 2).sum())
    norm = float(w.sum()) / 2.0
    if power <= 0.0 or norm <= 0.0:
        return None
    return round(10.0 * np.log10(power / (norm ** 2)) + SOX_R94_BAND_OFFSET_DB, 6)


def _sox_r94_peak_hz(arr, rate, center, span=120.0):
    """Interpolated peak FREQUENCY near `center` — the pitch witness. A band
    LEVEL is estimator-fragile for non-bin-centred tones (the window's main
    lobe width scales with the record length), so the pitch law compares the
    frequency estimate the way the scout's `tone0` estimator did."""
    x = np.asarray(arr).reshape(-1)
    if x.size < 16:
        return None
    w = np.hanning(x.size)
    n = 1 << int(np.ceil(np.log2(max(x.size, 32))))
    spec = np.abs(np.fft.rfft(x * w, n))
    freqs = np.fft.rfftfreq(n, 1.0 / rate)
    sel = (freqs >= center - span) & (freqs <= center + span)
    if not sel.any():
        return None
    idx = np.nonzero(sel)[0][int(np.argmax(spec[sel]))]
    if idx == 0 or idx + 1 >= spec.size:
        return round(float(freqs[idx]), 3)
    a, b, c = spec[idx - 1], spec[idx], spec[idx + 1]
    denom = (a - 2.0 * b + c)
    delta = 0.0 if denom == 0 else 0.5 * (a - c) / denom
    step = freqs[1] - freqs[0]
    return round(float(freqs[idx] + delta * step), 3)


def _sox_r94_close(a, b, tol=1e-3):
    """Element-wise comparison of a metric against an expected value/list."""
    if a is None or b is None:
        return False
    if isinstance(b, (list, tuple)):
        if not isinstance(a, (list, tuple)) or len(a) != len(b):
            return False
        return all(x is not None and abs(float(x) - float(y)) <= tol
                   for x, y in zip(a, b))
    return abs(float(a) - float(b)) <= tol


def _sox_r94_mismatch(a, b):
    """(count of differing samples, max abs difference) between two sample
    matrices — the family's rounding-law comparator."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    n = min(a.shape[0], b.shape[0])
    if a.ndim == 1:
        a = a[:, None]
    if b.ndim == 1:
        b = b[:, None]
    if n == 0:
        return None, None
    d = np.abs(a[:n] - b[:n])
    return int(np.count_nonzero(d > 0)), round(float(d.max()), 10)


def _sox_r94_scout_refs():
    """The r94 scout's own receipts, read as a cross-seat witness. Absence is
    recorded (coverage_blocked), never treated as a pass."""
    refs = {"dir": str(SOX_R94_SCOUT), "available": False,
            "receipts": {}, "legs": {}, "stimuli": {}, "metrics": {}}
    if not SOX_R94_SCOUT.is_dir():
        return refs
    refs["available"] = True
    for p in sorted(SOX_R94_SCOUT.glob("*.json")):
        try:
            doc = json.loads(p.read_text())
        except Exception as exc:               # noqa: BLE001 - recorded
            refs["receipts"][p.name] = {"error": str(exc)[:120]}
            continue
        refs["receipts"][p.name] = {"sha256": _sox_r94_sha(p),
                                    "legs": len(doc.get("legs", []) or [])}
        if p.name == "prep.json":
            for note in doc.get("notes", []) or []:
                if isinstance(note, dict) and isinstance(note.get("stimuli"), dict):
                    refs["stimuli"].update(note["stimuli"])
        for leg in doc.get("legs", []) or []:
            if not isinstance(leg, dict):
                continue
            reps = leg.get("reps") or []
            if not reps or not isinstance(reps[0], dict):
                continue
            sha = reps[0].get("out_sha256")
            if sha:
                refs["legs"][f"{p.name}:{leg.get('name')}"] = sha
            m0 = reps[0].get("metrics")
            if isinstance(m0, dict):
                sel = {k: m0[k] for k in SOX_R94_REF_METRIC_KEYS if k in m0}
                if sel:
                    refs["metrics"][f"{p.name}:{leg.get('name')}"] = sel
    return refs


def _sox_r94_ref_metric_arm(entry, leg, refs, receipt, refname, keys, tol):
    """Cross-seat METRIC law: this seat's own metric must reproduce the value
    the scout's receipt recorded for the same leg. The witness is data (never
    an instruction source) and its absence is coverage_blocked."""
    key = f"{receipt}:{refname}"
    exp = refs["metrics"].get(key) or {}
    got = dict(leg.get("metrics") or {})
    for k in SOX_R94_REF_METRIC_KEYS:
        if k in leg:
            got[k] = leg[k]
    compared = {}
    for k in keys:
        if k not in exp:
            continue
        a, b = got.get(k), exp[k]
        if isinstance(a, list) and isinstance(b, list):
            ok = (len(a) == len(b) and
                  all(x is not None and abs(float(x) - float(y)) <= tol
                      for x, y in zip(a, b)))
        elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
            ok = abs(float(a) - float(b)) <= tol
        else:
            ok = a == b
        compared[k] = {"own": a, "scout": b, "match": bool(ok)}
        if not ok:
            _sox_r94_fail(
                entry,
                f"{leg['name']}: cross-seat metric mismatch on {k} vs {key} "
                f"(own {a} vs scout {b}, tol {tol})")
    leg["scout_metric_ref"] = {"key": key, "tol": tol, "compared": compared}
    if not compared:
        _sox_r94_block(
            entry,
            f"{leg['name']}: no scout metric recorded for {key} -> cross-seat "
            "metric law not armed")


def _sox_r94_ref_arm(entry, leg, refs, receipt, refname):
    key = f"{receipt}:{refname}"
    exp = refs["legs"].get(key)
    leg["scout_ref"] = {"key": key, "expected_sha256": exp,
                        "receipt_available": refs["available"]}
    if exp is None:
        if refs["available"]:
            _sox_r94_block(
                entry,
                f"{leg['name']}: scout receipt set present but {key} has no "
                "recorded output sha -> cross-seat witness not armed")
        else:
            _sox_r94_block(
                entry,
                f"{leg['name']}: scout receipts absent at {refs['dir']} -> "
                "cross-seat witness not armed")
        return
    ok = leg.get("out_sha256") == exp
    leg["scout_ref"]["sha_match"] = ok
    if not ok:
        _sox_r94_fail(
            entry,
            f"{leg['name']}: cross-seat sha mismatch vs {key} "
            f"(own {str(leg.get('out_sha256'))[:16]} vs "
            f"{exp[:16]})")


def _sox_r94_fail(entry, msg):
    """An armed law was violated -> a real failure on this leg."""
    entry["failures"].append(msg)


def _sox_r94_block(entry, msg):
    """A law could not be armed (missing witness / unparseable product) ->
    coverage_blocked, NEVER a pass and never a failure."""
    entry["coverage_blocked"].append(msg)


def _sox_r94_arm(entry, leg, cond, msg):
    if not cond:
        _sox_r94_fail(entry, f"{leg['name']}: {msg}")


def _sox_r94_pw_census():
    """Read-only PipeWire census. This family is file-only, so the census is
    a NEGATIVE CONTROL: any r94a_-tagged object at entry or exit is a leak.
    Nothing is ever unloaded or destroyed here (no module is ever loaded),
    and no default is ever written."""
    cen = {"own_prefix": SOX_R94_TAG, "own_objects": [],
           "own_modules": [], "sink_total": None, "source_total": None,
           "module_total": None, "default_sink": None, "default_source": None}
    def _pactl(args):
        try:
            out = subprocess.run(["pactl"] + args, capture_output=True,
                                 timeout=12.0).stdout.decode(errors="replace")
        except (OSError, subprocess.TimeoutExpired):
            return None
        return out
    for args, key, total in ((["list", "short", "sinks"], "own_objects", "sink_total"),
                             (["list", "short", "sources"], "own_objects", "source_total"),
                             (["list", "short", "modules"], "own_modules", "module_total")):
        text = _pactl(args)
        if text is None:
            cen.setdefault("unreadable", []).append(" ".join(args))
            continue
        rows = [ln for ln in text.splitlines() if ln.strip()]
        cen[total] = len(rows)
        cen[key] += [ln.split("\t")[0] if "\t" in ln else ln[:60]
                     for ln in rows if SOX_R94_TAG in ln]
    for args, key in ((["get-default-sink"], "default_sink"),
                      (["get-default-source"], "default_source")):
        text = _pactl(args)
        cen[key] = text.strip() if text else None
    cen["own_objects"] = sorted(set(cen["own_objects"]))
    cen["own_modules"] = sorted(set(cen["own_modules"]))
    return cen


def _sox_r94_host():
    def _out(argv):
        try:
            return subprocess.run(argv, capture_output=True,
                                  timeout=12.0).stdout.decode(errors="replace").strip()
        except (OSError, subprocess.TimeoutExpired):
            return None
    return {"utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "loadavg": _out(["cat", "/proc/loadavg"]),
            "nproc": os.cpu_count(),
            "sox_version": _out([SOX_R94, "--version"]),
            "sox_sha256": _sox_r94_sha(SOX_R94),
            "python": sys.version.split()[0],
            "numpy": np.__version__}


def _sox_r94_entry(probe, note=None):
    entry = {"probe": probe, "host": _sox_r94_host(),
             "pw_census_entry": _sox_r94_pw_census(),
             "legs": {}, "failures": [], "coverage_blocked": [], "notes": []}
    if note:
        entry["notes"].append(note)
    if entry["pw_census_entry"]["own_objects"] or \
            entry["pw_census_entry"]["own_modules"]:
        _sox_r94_fail(entry, "entry census: r94a_-tagged PipeWire objects "
                             "already exist -> family is not file-only")
    return entry


def _sox_r94_exit(entry):
    entry["pw_census_exit"] = _sox_r94_pw_census()
    if entry["pw_census_exit"]["own_objects"] or \
            entry["pw_census_exit"]["own_modules"]:
        _sox_r94_fail(entry, "exit census: r94a_-tagged PipeWire objects "
                             "survived a file-only family")
    entry["host_exit"] = _sox_r94_host()
    return entry


def _sox_r94_leg(scratch, name, argv, infile, reps=1, env=None,
                 timeout=SOX_R94_WALL, want_metrics=True, note=None):
    """One leg = `reps` fresh-process runs of the same argv. Output files are
    per-rep (fresh process, fresh product); the sha set is the determinism
    witness. Returns the leg record; the caller arms it."""
    reps_rec, shas, paths = [], [], []
    for r in range(reps):
        op = scratch / f"{name}_r{r}.wav"
        try:
            op.unlink()
        except OSError:
            pass
        concrete = []
        for tok in argv:
            t = str(tok)
            concrete.append(t.replace("{in}", str(infile))
                            .replace("{out}", str(op)))
        rec = _sox_r94_spawn(concrete, timeout=timeout, env=env)
        sha = _sox_r94_sha(op) if op.exists() else None
        shas.append(sha)
        paths.append(op)
        reps_rec.append({"rc": rec.get("exit_code"),
                         "signal": rec.get("signal"),
                         "killed_at_bound": rec.get("killed_at_bound"),
                         "wall_s": rec.get("wall_s"),
                         "out_bytes": (op.stat().st_size if op.exists() else 0),
                         "out_sha256": sha,
                         "error_class": rec.get("error_class"),
                         "error_hit": rec.get("error_hit"),
                         "stderr": rec.get("stderr", ""),
                         "spawn_error": rec.get("spawn_error")})
    distinct = sorted({s for s in shas if s})
    shown = [str(a).replace(str(infile), "<in>").replace(str(paths[0]), "<out>")
             for a in argv]
    leg = {"name": name, "argv": shown,
           "rc": reps_rec[0]["rc"], "reps_n": reps,
           "out_sha256": shas[0], "out_sha256_all": shas,
           "n_distinct_shas": len(distinct),
           "stable": len(distinct) == 1 and shas[0] is not None,
           "reps": reps_rec}
    if len(distinct) > 1:
        # The sha is volatile BY LAW on this leg (the law is nondeterminism),
        # so a cross-run diff must exclude it rather than read it as drift.
        leg["volatile_sha"] = True
    if note:
        leg["note"] = note
    if want_metrics and paths[0].exists() and leg["rc"] == 0:
        try:
            m, arr = _sox_r94_metrics(paths[0])
            leg["metrics"] = m
            leg["_arr"] = arr
        except (ValueError, OSError) as exc:
            leg["metrics_error"] = str(exc)[:160]
    return leg


def _sox_r94_drop_arrays(entry):
    """The sample matrices and the full text captures are comparison scratch,
    not receipt content."""
    for leg in entry["legs"].values():
        leg.pop("_arr", None)
        leg.pop("_text_full", None)
    return entry


def _sox_r94_m(leg, key, default=None):
    m = leg.get("metrics") or {}
    return m.get(key, default)


def _sox_r94_stimuli(entry, refs):
    """Own deterministic stimulus set — the scout's own definitions, rebuilt
    from scratch (so this family is self-sufficient on a fresh tree) and
    hash-armed against the scout's prep.json when it is readable."""
    scratch = _sox_r94_scratch()
    rate = SOX_R94_RATE
    t_a = np.arange(48000) / rate
    a = np.column_stack([
        np.rint(16384.0 * np.sin(2 * np.pi * 1000.0 * t_a)),
        np.rint(8192.0 * np.sin(2 * np.pi * 1500.0 * t_a)),
    ]).astype("<i2")
    _sox_r94_write_pcm16(scratch / "r94a_stim_a.wav", a, rate)

    t_b = np.arange(12000) / rate
    b = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * t_b)).astype("<i2")
    _sox_r94_write_pcm16(scratch / "r94a_stim_b.wav", b, rate)

    c = np.zeros(19200, dtype="<i2")
    t_c = np.arange(9600) / rate
    c[4800:14400] = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * t_c)).astype("<i2")
    _sox_r94_write_pcm16(scratch / "r94a_stim_c.wav", c, rate)

    f = (0.5 * np.sin(2 * np.pi * 997.0 * t_b)).astype("<f4")
    _sox_r94_write_f32(scratch / "r94a_stim_f.wav", f, rate)

    h = np.rint(16384.0 * np.sin(2 * np.pi * 20000.0 * t_b)).astype("<i2")
    _sox_r94_write_pcm16(scratch / "r94a_stim_h.wav", h, rate)

    i = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * np.arange(12001) / rate)).astype("<i2")
    _sox_r94_write_pcm16(scratch / "r94a_stim_i.wav", i, rate)

    j = np.rint(16384.0 * np.sin(2 * np.pi * 23000.0 * t_b)).astype("<i2")
    _sox_r94_write_pcm16(scratch / "r94a_stim_j.wav", j, rate)

    rng = np.random.default_rng(94)
    r = rng.integers(-32768, 32768, size=4800, dtype=np.int64).astype("<i2")
    _sox_r94_write_pcm16(scratch / "r94a_stim_r.wav", r, rate)

    c2 = np.zeros(21600, dtype="<i2")
    t_c2 = np.arange(9600) / rate
    c2[4800:14400] = np.rint(16384.0 * np.sin(2 * np.pi * 997.0 * t_c2)).astype("<i2")
    _sox_r94_write_pcm16(scratch / "r94a_stim_c2.wav", c2, rate)

    # The one r93-adjacent loudness cell (stim_a, 1 s stereo) is reused below
    # by the `stat -e` rows: SoX's own EBU R128 implementation prints
    # Integrated only once the file is long enough, while ffmpeg's ebur128
    # gates the 0.25 s mono file to -70 LUFS on the same input.
    stim = {"a": scratch / "r94a_stim_a.wav", "b": scratch / "r94a_stim_b.wav",
            "c": scratch / "r94a_stim_c.wav", "c2": scratch / "r94a_stim_c2.wav",
            "f": scratch / "r94a_stim_f.wav", "h": scratch / "r94a_stim_h.wav",
            "i": scratch / "r94a_stim_i.wav", "j": scratch / "r94a_stim_j.wav",
            "r": scratch / "r94a_stim_r.wav"}
    shas, matches, blocked = {}, {}, []
    for key, path in stim.items():
        shas[key] = _sox_r94_sha(path)
        exp = refs["stimuli"].get(f"r94s_stim_{key}.wav")
        if exp is None:
            blocked.append(f"stimulus {key}: no scout prep sha available")
            continue
        matches[key] = (shas[key] == exp)
        if not matches[key]:
            _sox_r94_fail(
                entry,
                f"stimulus {key}: rebuilt bytes differ from the scout's "
                f"prep.json ({str(shas[key])[:16]} vs {exp[:16]})")
    entry["stimuli"] = {"sha256": shas, "scout_sha_match": matches,
                        "scout_prep_available": refs["available"]}
    entry["coverage_blocked"].extend(blocked)
    return stim


def sox_det_r94_entry():
    """The determinism / precision-tracking lattice — the headline law."""
    entry = _sox_r94_entry(
        "r94 sox determinism + precision-tracking lattice",
        "auto-dither is a precision consequence: -D fixes a sample-changing "
        "s16 effect, s24/s32 output suppresses the insertion, and an "
        "explicit `dither` needs -R (not -D)")
    scratch = _sox_r94_scratch()
    refs = _sox_r94_scout_refs()
    st = _sox_r94_stimuli(entry, refs)
    A, B, F, I = st["a"], st["b"], st["f"], st["i"]
    L = entry["legs"]

    # --- the auto-dither predicate: default s16 is nondeterministic -------
    L["det_gain_m6_default"] = _sox_r94_leg(
        scratch, "det_gain_m6_default",
        [SOX_R94, "{in}", "{out}", "gain", "-6"], A, reps=5)
    _sox_r94_arm(entry, L["det_gain_m6_default"],
                 L["det_gain_m6_default"]["n_distinct_shas"] >= 2,
                 "default s16 gain -6 must be NONDETERMINISTIC (time-seeded "
                 "auto-dither); got one sha across 5 fresh processes")

    L["det_gain_m6_D"] = _sox_r94_leg(
        scratch, "det_gain_m6_D",
        [SOX_R94, "-D", "{in}", "{out}", "gain", "-6"], A, reps=SOX_R94_REPS)
    _sox_r94_arm(entry, L["det_gain_m6_D"], L["det_gain_m6_D"]["stable"],
                 "-D gain -6 must be byte-stable across 3 fresh processes")
    _sox_r94_ref_arm(entry, L["det_gain_m6_D"], refs, "gain_D.json", "gain_m6")

    L["det_dither_explicit_default"] = _sox_r94_leg(
        scratch, "det_dither_explicit_default",
        [SOX_R94, "{in}", "-b", "16", "{out}", "dither"], F, reps=5)
    _sox_r94_arm(entry, L["det_dither_explicit_default"],
                 L["det_dither_explicit_default"]["n_distinct_shas"] >= 2,
                 "an explicit `dither` must be nondeterministic without -R")

    L["det_dither_explicit_D"] = _sox_r94_leg(
        scratch, "det_dither_explicit_D",
        [SOX_R94, "-D", "{in}", "-b", "16", "{out}", "dither"], F, reps=5)
    _sox_r94_arm(entry, L["det_dither_explicit_D"],
                 L["det_dither_explicit_D"]["n_distinct_shas"] >= 2,
                 "-D must NOT make an explicit `dither` reproducible "
                 "(it only suppresses the AUTOMATIC one)")

    L["det_dither_explicit_R"] = _sox_r94_leg(
        scratch, "det_dither_explicit_R",
        [SOX_R94, "-R", "{in}", "-b", "16", "{out}", "dither"], F, reps=SOX_R94_REPS)
    _sox_r94_arm(entry, L["det_dither_explicit_R"],
                 L["det_dither_explicit_R"]["stable"],
                 "-R must make an explicit `dither` reproducible (one sha)")

    L["det_dither_R_D"] = _sox_r94_leg(
        scratch, "det_dither_R_D",
        [SOX_R94, "-R", "-D", "{in}", "-b", "16", "{out}", "dither"], F, reps=SOX_R94_REPS)
    _sox_r94_arm(entry, L["det_dither_R_D"],
                 L["det_dither_R_D"]["stable"] and
                 L["det_dither_R_D"]["out_sha256"] ==
                 L["det_dither_explicit_R"]["out_sha256"],
                 "-R -D must equal -R byte-for-byte for an explicit dither")

    # --- integer / unity operations are byte-identical to the input -------
    for name, infile, tail in (("det_gain0_identity", A, ["gain", "0"]),
                               ("det_passthrough_identity", A, []),
                               ("det_rate_same_identity", B, ["rate", "48000"]),
                               ("det_pad_pct50_identity", B, ["pad", "%50"])):
        leg = _sox_r94_leg(scratch, name, [SOX_R94, "-D", "{in}", "{out}"] + tail,
                           infile, reps=1)
        L[name] = leg
        _sox_r94_arm(entry, leg, leg["out_sha256"] == _sox_r94_sha(infile),
                     f"{' '.join(tail) or 'the no-effect pass-through'} must be "
                     "byte-identical to its input")
    _sox_r94_ref_arm(entry, L["det_gain0_identity"], refs, "gain_D.json", "gain_0")
    _sox_r94_ref_arm(entry, L["det_passthrough_identity"], refs, "dither_D.json",
                     "copy_plain")
    _sox_r94_ref_arm(entry, L["det_pad_pct50_identity"], refs,
                     "repeat_pad_silence_D.json", "pad_pct50")

    # CORRECTION to the scout's D10 wording: `copy` is NOT an effect on this
    # build. `sox in.wav out.wav copy` parses the token as a THIRD positional
    # (a second INPUT, the multi-input concatenation grammar) and refuses rc 2
    # `can't open input file <out>`. The scout's "copy is byte-identical to
    # the input" row was measured with NO effect at all (its argv carries no
    # effect token) — armed above as det_passthrough_identity, and disarmed
    # here as an effect name.
    copy_tok = _sox_r94_leg(scratch, "det_copy_token_not_an_effect",
                            [SOX_R94, "-D", "{in}", "{out}", "copy"], A,
                            reps=1, want_metrics=False)
    L["det_copy_token_not_an_effect"] = copy_tok
    copy_err = copy_tok["reps"][0]["stderr"] or ""
    _sox_r94_arm(entry, copy_tok,
                 copy_tok["rc"] == 2 and "can't open input file" in copy_err,
                 "`copy` must NOT be a valid effect on this build: it is parsed "
                 "as a third positional (a second input) and refuses rc 2 "
                 "'can't open input file'")

    # --- the `< 24` output-precision clause -------------------------------
    for name, bits in (("det_f32_to_s16_plain", 16), ("det_f32_to_s24", 24),
                       ("det_f32_to_s32", 32)):
        leg = _sox_r94_leg(scratch, name,
                           [SOX_R94, "{in}", "-b", str(bits), "{out}"], F, reps=5)
        L[name] = leg
        if bits < 24:
            _sox_r94_arm(entry, leg, leg["n_distinct_shas"] >= 2,
                         "f32 -> s16 conversion must be nondeterministic "
                         "(output precision < 24 keeps the auto-dither)")
        else:
            _sox_r94_arm(entry, leg, leg["stable"],
                         f"f32 -> s{bits} must be byte-stable (output "
                         "precision >= 24 suppresses the auto-dither)")

    L["det_s16_to_s24_gain"] = _sox_r94_leg(
        scratch, "det_s16_to_s24_gain",
        [SOX_R94, "{in}", "-b", "24", "{out}", "gain", "-6"], A, reps=SOX_R94_REPS)
    _sox_r94_arm(entry, L["det_s16_to_s24_gain"], L["det_s16_to_s24_gain"]["stable"],
                 "s16 -> s24 + gain must be byte-stable (output precision "
                 ">= 24 suppresses the auto-dither)")

    # --- the independent axes: flag order, buffers, client env -----------
    order_shas = {}
    variants = (("before_infile", [SOX_R94, "-D", "{in}", "{out}", "gain", "-6"]),
                ("after_infile", [SOX_R94, "{in}", "-D", "{out}", "gain", "-6"]),
                ("after_outfile", [SOX_R94, "{in}", "{out}", "-D", "gain", "-6"]),
                ("long_form", [SOX_R94, "--no-dither", "{in}", "{out}", "gain", "-6"]),
                ("D_then_R", [SOX_R94, "-D", "-R", "{in}", "{out}", "gain", "-6"]),
                ("R_then_D", [SOX_R94, "-R", "-D", "{in}", "{out}", "gain", "-6"]))
    for label, argv in variants:
        leg = _sox_r94_leg(scratch, f"det_flag_order_{label}", argv, A, reps=1)
        order_shas[label] = leg["out_sha256"]
        entry["legs"][f"det_flag_order_{label}"] = leg
    entry["legs"]["det_flag_order"] = {
        "name": "det_flag_order", "variants": order_shas,
        "n_distinct_shas": len({s for s in order_shas.values() if s}),
        "stable": len({s for s in order_shas.values() if s}) == 1}
    _sox_r94_arm(entry, entry["legs"]["det_flag_order"],
                 entry["legs"]["det_flag_order"]["stable"],
                 "-D/--no-dither/-R must be position-invariant (all six "
                 "placements byte-identical)")

    for label, argv, want in (
            ("det_flag_after_effect",
             [SOX_R94, "{in}", "{out}", "gain", "-6", "-D"], "sox_r94_usage"),
            ("det_flag_after_dither",
             [SOX_R94, "{in}", "-b", "16", "{out}", "dither", "-R"], "sox_r94_opt")):
        leg = _sox_r94_leg(scratch, label, argv, A, reps=1, want_metrics=False)
        L[label] = leg
        _sox_r94_arm(entry, leg, leg["rc"] == 1 and leg["reps"][0]["error_class"] == want,
                     f"a global option placed after the effect must refuse rc 1 "
                     f"with class {want} (gopts stop at the first effect)")

    buf_shas = {}
    for label, opts in (("control", []), ("buffer1024", ["--buffer", "1024"]),
                        ("buffer4096", ["--buffer", "4096"]),
                        ("buffer16384", ["--buffer", "16384"]),
                        ("input_buffer4096", ["--input-buffer", "4096"])):
        leg = _sox_r94_leg(scratch, f"det_buffer_{label}",
                           [SOX_R94, "-D"] + opts + ["{in}", "{out}", "gain", "-6"],
                           A, reps=1)
        buf_shas[label] = leg["out_sha256"]
        L[f"det_buffer_{label}"] = leg
    L["det_buffer_invariant"] = {
        "name": "det_buffer_invariant", "variants": buf_shas,
        "n_distinct_shas": len({s for s in buf_shas.values() if s}),
        "stable": len({s for s in buf_shas.values() if s}) == 1}
    _sox_r94_arm(entry, L["det_buffer_invariant"], L["det_buffer_invariant"]["stable"],
                 "sox --buffer/--input-buffer must not change a file transform")

    env_variants = (("quantum32", {"PIPEWIRE_QUANTUM": "32"}),
                    ("quantum8192", {"PIPEWIRE_QUANTUM": "8192"}),
                    ("rate44100", {"PIPEWIRE_RATE": "44100"}),
                    ("rate96000", {"PIPEWIRE_RATE": "96000"}),
                    ("latency64", {"PIPEWIRE_LATENCY": "64"}),
                    ("latency48000", {"PIPEWIRE_LATENCY": "48000"}),
                    ("node", {"PIPEWIRE_NODE": "r94a_absent_node"}),
                    ("pulse_sink", {"PULSE_SINK": "r94a_absent_sink"}),
                    ("pulse_source", {"PULSE_SOURCE": "r94a_absent_source"}),
                    ("combo", {"PIPEWIRE_QUANTUM": "64", "PIPEWIRE_RATE": "96000",
                               "PIPEWIRE_LATENCY": "128", "PIPEWIRE_NODE": "r94a_absent_node",
                               "PULSE_SINK": "r94a_absent_sink",
                               "PULSE_SOURCE": "r94a_absent_source"}))
    env_shas = {"control": None}
    ctrl = _sox_r94_leg(scratch, "det_env_control",
                        [SOX_R94, "-D", "{in}", "{out}", "gain", "-6"], A, reps=1)
    env_shas["control"] = ctrl["out_sha256"]
    L["det_env_control"] = ctrl
    for label, extra in env_variants:
        env = dict(os.environ)
        env.update(extra)
        leg = _sox_r94_leg(scratch, f"det_env_{label}",
                           [SOX_R94, "-D", "{in}", "{out}", "gain", "-6"], A,
                           reps=1, env=env)
        env_shas[label] = leg["out_sha256"]
        L[f"det_env_{label}"] = leg
    L["det_env_invariant"] = {
        "name": "det_env_invariant", "variants": env_shas,
        "n_distinct_shas": len({s for s in env_shas.values() if s}),
        "stable": len({s for s in env_shas.values() if s}) == 1,
        "note": "a file transform never opens a device: the client env is inert"}
    _sox_r94_arm(entry, L["det_env_invariant"], L["det_env_invariant"]["stable"],
                 "the PipeWire/pulse client env must not touch a FILE leg")

    # --- process concurrency --------------------------------------------
    for label, prefix, reps, arm_min, arm_max in (
            ("det_concurrency_D", ["-D"], 16, 1, 1),
            ("det_concurrency_R_dither", ["-R"], 16, 1, 1),
            ("det_concurrency_default", [], 16, 2, None)):
        paths = [scratch / f"{label}_r{i}.wav" for i in range(reps)]
        argv_list = []
        for op in paths:
            try:
                op.unlink()
            except OSError:
                pass
            if label == "det_concurrency_R_dither":
                argv_list.append([SOX_R94] + prefix +
                                 [str(F), "-b", "16", str(op), "dither"])
            else:
                argv_list.append([SOX_R94] + prefix +
                                 [str(A), str(op), "gain", "-6"])
        procs = []
        for argv in argv_list:
            try:
                procs.append(subprocess.Popen(
                    argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL, start_new_session=True,
                    preexec_fn=_sox_r94_limit))
            except OSError:
                procs.append(None)
        deadline = time.monotonic() + SOX_R94_WALL
        rcs = []
        for p in procs:
            if p is None:
                rcs.append(None)
                continue
            try:
                p.wait(timeout=max(0.0, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                _sox_r94_killpg(p)
                p.wait()
            rcs.append(p.returncode)
        shas = [_sox_r94_sha(op) if op.exists() else None for op in paths]
        distinct = sorted({s for s in shas if s})
        leg = {"name": label, "concurrency": reps, "rcs": rcs,
               "out_sha256_all": shas, "n_distinct_shas": len(distinct),
               "stable": len(distinct) == 1 and shas[0] is not None}
        if len(distinct) > 1:
            leg["volatile_sha"] = True
        L[label] = leg
        if arm_max is not None:
            _sox_r94_arm(entry, leg, len(distinct) == arm_max,
                         f"{reps} concurrent identical invocations must yield "
                         f"exactly {arm_max} distinct sha(s); got {len(distinct)}")
        else:
            _sox_r94_arm(entry, leg, len(distinct) >= arm_min,
                         f"{reps} concurrent DEFAULT invocations must be mutually "
                         f"nondeterministic (>= {arm_min} distinct shas); got "
                         f"{len(distinct)}")
    return _sox_r94_exit(_sox_r94_drop_arrays(entry))


def sox_gain_r94_entry():
    """gain / vol: the rounding laws and the chain-order law (all under -D)."""
    entry = _sox_r94_entry(
        "r94 sox gain/vol rounding + chain order",
        "gain and the vol dB/power forms round to nearest; the vol AMPLITUDE "
        "form rounds ceil, so the two spellings are 1 LSB apart")
    scratch = _sox_r94_scratch()
    refs = _sox_r94_scout_refs()
    st = _sox_r94_stimuli(entry, refs)
    A, B = st["a"], st["b"]
    L = entry["legs"]
    ain, _ = _sox_r94_read(A)

    def rint_formula(arr, factor):
        return np.rint(arr * factor)

    def ceil_formula(arr, factor):
        return np.ceil(arr * factor)

    leg = _sox_r94_leg(scratch, "gain_m6_rint",
                       [SOX_R94, "-D", "{in}", "{out}", "gain", "-6"], A)
    L["gain_m6_rint"] = leg
    arr = leg.get("_arr")
    if arr is not None:
        n, mx = _sox_r94_mismatch(arr * 32768.0, rint_formula(ain, 10 ** (-6 / 20) * 32768.0))
        leg["mismatch_vs_rint_formula"] = n
        leg["max_abs_diff_vs_formula"] = mx
        _sox_r94_arm(entry, leg, n == 0,
                     "gain -6 under -D must equal rint(x*10^(-6/20)) exactly")
        _sox_r94_arm(entry, leg,
                     _sox_r94_close(_sox_r94_m(leg, "peak_db"), [-12.0211, -18.0406], 5e-4),
                     f"gain -6 peaks must be [-12.0211, -18.0406]; got "
                     f"{_sox_r94_m(leg, 'peak_db')}")
    _sox_r94_ref_arm(entry, leg, refs, "gain_D.json", "gain_m6")
    _sox_r94_ref_metric_arm(entry, leg, refs, "gain_D.json", "gain_m6",
                            ("mismatch_vs_rint_formula", "max_abs_diff_vs_formula",
                             "peak_db"), 5e-4)

    leg = _sox_r94_leg(scratch, "gain_p6_rint",
                       [SOX_R94, "-D", "{in}", "{out}", "gain", "6"], B)
    L["gain_p6_rint"] = leg
    arr = leg.get("_arr")
    if arr is not None:
        bin_, _ = _sox_r94_read(B)
        n, mx = _sox_r94_mismatch(arr * 32768.0, rint_formula(bin_, 10 ** (6 / 20) * 32768.0))
        leg["mismatch_vs_rint_formula"] = n
        leg["max_abs_diff_vs_formula"] = mx
        _sox_r94_arm(entry, leg, n == 0, "gain +6 must equal rint(x*10^(6/20))")
    _sox_r94_ref_arm(entry, leg, refs, "gain_D.json", "gain_p6")

    vol_legs = {}
    for name, tail in (("vol_amp_0.5", ["vol", "0.5"]),
                       ("vol_db_m6_0206", ["vol", "-6.0206", "d"]),
                       ("vol_pow_0.5", ["vol", "0.5", "p"])):
        leg = _sox_r94_leg(scratch, name, [SOX_R94, "-D", "{in}", "{out}"] + tail, A)
        L[name] = leg
        vol_legs[name] = leg
        arr = leg.get("_arr")
        if arr is None:
            continue
        if name == "vol_amp_0.5":
            n_ceil, mx_ceil = _sox_r94_mismatch(arr * 32768.0, ceil_formula(ain, 0.5 * 32768.0))
            n_rint, mx_rint = _sox_r94_mismatch(arr * 32768.0, rint_formula(ain, 0.5 * 32768.0))
            leg.update({"mismatch_vs_ceil": n_ceil, "max_abs_diff_vs_ceil_lsb": mx_ceil,
                        "mismatch_vs_rint_formula": n_rint, "max_abs_diff_vs_formula": mx_rint})
            _sox_r94_arm(entry, leg, n_ceil == 0,
                         "the vol AMPLITUDE form must round CEIL (mismatch 0)")
            _sox_r94_arm(entry, leg, n_rint > 0,
                         "the vol amplitude form must NOT be a nearest-rounding "
                         "form (a nonzero rint mismatch is the discriminator)")
        elif name == "vol_db_m6_0206":
            n, mx = _sox_r94_mismatch(arr * 32768.0,
                                      rint_formula(ain, 10 ** (-6.0206 / 20) * 32768.0))
            leg.update({"mismatch_vs_rint_formula": n, "max_abs_diff_vs_formula": mx})
            _sox_r94_arm(entry, leg, n == 0,
                         "the vol dB form must round to nearest (mismatch 0 vs rint)")
        else:
            n, mx = _sox_r94_mismatch(arr * 32768.0,
                                      rint_formula(ain, np.sqrt(0.5) * 32768.0))
            leg.update({"mismatch_vs_rint_formula": n, "max_abs_diff_vs_formula": mx,
                        "factor": "sqrt(0.5) = -3.0103 dB"})
            _sox_r94_arm(entry, leg, n == 0,
                         "the vol POWER form must round to nearest with a "
                         "sqrt(gain) amplitude (mismatch 0 vs rint)")
    _sox_r94_ref_arm(entry, L["vol_amp_0.5"], refs, "gain_D.json", "vol_amp_0.5")
    _sox_r94_ref_arm(entry, L["vol_db_m6_0206"], refs, "gain_D.json", "vol_db_m6.0206")

    a_amp, b_db = L["vol_amp_0.5"], L["vol_db_m6_0206"]
    if a_amp.get("_arr") is not None and b_db.get("_arr") is not None:
        n, mx = _sox_r94_mismatch(a_amp["_arr"] * 32768.0, b_db["_arr"] * 32768.0)
        L["vol_spelling_delta"] = {
            "name": "vol_spelling_delta", "a": "vol 0.5", "b": "vol -6.0206 d",
            "same_sha": a_amp["out_sha256"] == b_db["out_sha256"],
            "n_diff_samples": n, "max_abs_diff_lsb": mx}
        _sox_r94_arm(entry, L["vol_spelling_delta"],
                     n is not None and n > 0 and mx == 1.0 and
                     not L["vol_spelling_delta"]["same_sha"],
                     "`vol 0.5` and `vol -6.0206 d` must differ by exactly 1 LSB "
                     f"(not interchangeable); got n_diff={n} max={mx}")

    leg = _sox_r94_leg(scratch, "global_v_0.5",
                       [SOX_R94, "-D", "-v", "0.5", "{in}", "{out}"], A)
    L["global_v_0.5"] = leg
    _sox_r94_arm(entry, leg, leg["out_sha256"] == L["vol_amp_0.5"]["out_sha256"],
                 "the global `-v 0.5` must equal `vol 0.5` byte-for-byte "
                 "(same ceil path)")

    leg = _sox_r94_leg(scratch, "gain_n_normalize",
                       [SOX_R94, "-D", "{in}", "{out}", "gain", "-n"], A)
    L["gain_n_normalize"] = leg
    _sox_r94_arm(entry, leg, _sox_r94_close(_sox_r94_m(leg, "peak_db"), [0.0, -6.0206], 5e-4),
                 "gain -n must normalize the file peak to 0 dBFS "
                 f"(both channels scaled by one factor); got {_sox_r94_m(leg, 'peak_db')}")
    _sox_r94_ref_arm(entry, leg, refs, "gain_D.json", "gain_n")

    for name, flag in (("gain_e_lift", "-e"), ("gain_b_lift", "-b")):
        leg = _sox_r94_leg(scratch, name,
                           [SOX_R94, "-D", "{in}", "{out}", "gain", flag], A)
        L[name] = leg
        _sox_r94_arm(entry, leg,
                     _sox_r94_close(_sox_r94_m(leg, "peak_db"), [-6.0206, -6.0206], 5e-4),
                     f"gain {flag} must lift BOTH channels to the same peak "
                     f"(per-channel normalization); got {_sox_r94_m(leg, 'peak_db')}")
    _sox_r94_ref_arm(entry, L["gain_e_lift"], refs, "gain_D.json", "gain_e")
    _sox_r94_arm(entry, L["gain_b_lift"],
                 L["gain_b_lift"]["out_sha256"] == L["gain_e_lift"]["out_sha256"],
                 "gain -e and gain -b must be the same bytes on a stereo file")

    # The guard row: -G is NOT a limiter. Only the -D equality is reproducible
    # (the scout's >=32767 threshold row is dither-sensitive; the boundary
    # re-armed the >=32766 equality under -D).
    def clipped_ge(arr, thresh):
        if arr is None:
            return None
        ints = np.rint(arr * 32768.0)
        return int(np.count_nonzero(np.abs(ints) >= thresh))

    plain = _sox_r94_leg(scratch, "guard_gain_p12_D",
                         [SOX_R94, "-D", "{in}", "{out}", "gain", "12"], A)
    guarded = _sox_r94_leg(scratch, "guard_gain_p12_G_D",
                           [SOX_R94, "-D", "-G", "{in}", "{out}", "gain", "12"], A)
    L["guard_gain_p12_D"], L["guard_gain_p12_G_D"] = plain, guarded
    c_plain = clipped_ge(plain.get("_arr"), 32766)
    c_guard = clipped_ge(guarded.get("_arr"), 32766)
    L["guard_not_limiter"] = {
        "name": "guard_not_limiter", "threshold": 32766,
        "clipped_gain12_D": c_plain, "clipped_G_gain12_D": c_guard,
        "same_sha": plain["out_sha256"] == guarded["out_sha256"],
        "note": "-G is not a limiter: the railed-sample count is identical with "
                "and without it. The scout's >=32767 threshold row is "
                "dither-sensitive (boundary: 7979 vs 3989 on the default path); "
                "only this -D equality is armed."}
    _sox_r94_arm(entry, L["guard_not_limiter"],
                 c_plain is not None and c_plain == c_guard and c_plain > 0,
                 "-G must not reduce the railed-sample count (it is not a limiter)")

    order = {}
    for name, tail in (("chain_gain_then_norm", ["gain", "-6", "norm", "-3"]),
                       ("chain_norm_then_gain", ["norm", "-3", "gain", "-6"])):
        leg = _sox_r94_leg(scratch, name, [SOX_R94, "-D", "{in}", "{out}"] + tail, A)
        L[name] = leg
        order[name] = _sox_r94_m(leg, "peak_db")
    _sox_r94_arm(entry, L["chain_gain_then_norm"],
                 _sox_r94_close(order["chain_gain_then_norm"][0], -3.0, 5e-3),
                 "`gain -6 norm -3` must end at the norm target (-3.0 dBFS on "
                 f"the normalized channel); got {order['chain_gain_then_norm']}")
    _sox_r94_arm(entry, L["chain_norm_then_gain"],
                 _sox_r94_close(order["chain_norm_then_gain"][0], -8.9996, 5e-3),
                 "`norm -3 gain -6` must be the OTHER order (-8.9996 dBFS): "
                 f"effect order is content-visible; got {order['chain_norm_then_gain']}")
    _sox_r94_ref_metric_arm(entry, L["chain_gain_then_norm"], refs, "chain_D.json",
                            "gain_m6_then_norm_m3", ("peak_db", "rms_db"), 5e-4)
    _sox_r94_ref_metric_arm(entry, L["chain_norm_then_gain"], refs, "chain_D.json",
                            "norm_m3_then_gain_m6", ("peak_db", "rms_db"), 5e-4)
    _sox_r94_ref_arm(entry, L["chain_gain_then_norm"], refs, "chain_D.json",
                     "gain_m6_then_norm_m3")
    _sox_r94_ref_arm(entry, L["chain_norm_then_gain"], refs, "chain_D.json",
                     "norm_m3_then_gain_m6")
    return _sox_r94_exit(_sox_r94_drop_arrays(entry))


def sox_rate_r94_entry():
    """The resampler: length law, same-rate identity, pitch, and the
    boundary-CORRECTED alias lattice (the scout's -130 dB -v claim is dead)."""
    entry = _sox_r94_entry(
        "r94 sox rate: length + alias lattice (boundary-corrected)",
        "length is within +/-1 frame of in*out/in_rate with no single rounding "
        "rule; the content hazard is -q ONLY (23 kHz folds to 21.1 kHz at "
        "-6.3 dB); the scout's '-v rejects at -130 dB' is falsified and the "
        "only ~-129.6 dB row is the 20 kHz stimulus DEFAULT leg")
    scratch = _sox_r94_scratch()
    refs = _sox_r94_scout_refs()
    st = _sox_r94_stimuli(entry, refs)
    B, H, I, J = st["b"], st["h"], st["i"], st["j"]
    L = entry["legs"]

    # --- the length matrix -------------------------------------------------
    length_rows = (("len_12000_to_44100", B, 44100, 12000, 11025),
                   ("len_12001_to_44100", I, 44100, 12001, 11026),
                   ("len_12000_to_22050", B, 22050, 12000, 5512),
                   ("len_12000_to_24050", B, 24050, 12000, 6013),
                   ("len_12000_to_11025", B, 11025, 12000, 2756),
                   ("len_12000_to_32000", B, 32000, 12000, 8000))
    fitted = {"floor": [], "round": [], "half_even": [], "ceil": []}
    for name, infile, out_rate, in_frames, expect in length_rows:
        leg = _sox_r94_leg(scratch, name,
                           [SOX_R94, "-D", "{in}", "{out}", "rate", str(out_rate)],
                           infile)
        L[name] = leg
        frames = _sox_r94_m(leg, "frames")
        exact = in_frames * out_rate / SOX_R94_RATE
        leg["in_frames"] = in_frames
        leg["out_rate"] = out_rate
        leg["exact_frames"] = round(exact, 6)
        leg["delta_vs_exact"] = None if frames is None else frames - exact
        _sox_r94_arm(entry, leg, frames is not None and abs(frames - exact) <= 1.0,
                     f"length must be within +/-1 frame of in*out/in_rate "
                     f"({exact}); got {frames}")
        for rule, val in (("floor", int(np.floor(exact))),
                          ("round", int(np.round(exact))),
                          ("half_even", int(np.floor(exact + 0.5)) if (exact % 1) != 0.5
                           else int(2 * np.round(exact / 2))),
                          ("ceil", int(np.ceil(exact)))):
            if frames == val:
                fitted[rule].append(name)
    half_rows = ("len_12000_to_22050", "len_12001_to_44100", "len_12000_to_24050")
    L["len_rounding_rules"] = {
        "name": "len_rounding_rules", "rules_fitting_all_half_rows": [
            r for r, names in fitted.items() if all(n in names for n in half_rows)],
        "half_rows": list(half_rows),
        "note": "no single rounding rule fits the .5 rows: the rate machinery "
                "approximates the ratio internally, so the row is armed as "
                "|measured - exact| <= 1 frame, never as a rounding law"}
    _sox_r94_arm(entry, L["len_rounding_rules"],
                 L["len_rounding_rules"]["rules_fitting_all_half_rows"] == [],
                 "a single rounding rule must NOT fit all .5-boundary rows "
                 f"(scout and boundary both found none); fitted={fitted}")
    _sox_r94_ref_arm(entry, L["len_12000_to_44100"], refs, "rate_D.json",
                     "rate44100_default")
    _sox_r94_ref_arm(entry, L["len_12001_to_44100"], refs, "rate_D.json",
                     "rate44100_odd12001")
    _sox_r94_ref_arm(entry, L["len_12000_to_22050"], refs, "rate_D.json", "rate22050")
    _sox_r94_ref_arm(entry, L["len_12000_to_24050"], refs, "rate_D.json", "rate24050")
    _sox_r94_ref_arm(entry, L["len_12000_to_11025"], refs, "rate_D.json", "rate11025")
    for legname, refname, keys in (
            ("len_12000_to_44100", "rate44100_default", ("frames",)),
            ("len_12001_to_44100", "rate44100_odd12001", ("frames",)),
            ("len_12000_to_22050", "rate22050", ("frames",)),
            ("len_12000_to_24050", "rate24050", ("frames",)),
            ("len_12000_to_11025", "rate11025", ("frames",))):
        _sox_r94_ref_metric_arm(entry, L[legname], refs, "rate_D.json", refname,
                                keys, 0.05)

    # --- same-rate identity + pitch preservation --------------------------
    leg = _sox_r94_leg(scratch, "rate_same_identity",
                       [SOX_R94, "-D", "{in}", "{out}", "rate", "48000"], B)
    L["rate_same_identity"] = leg
    _sox_r94_arm(entry, leg, leg["out_sha256"] == _sox_r94_sha(B),
                 "`rate <same rate>` must be byte-identical to the input "
                 "(SOX_EFF_NULL)")
    _sox_r94_ref_arm(entry, leg, refs, "rate_D.json", "rate48000")

    pitch = {}
    base_arr, _ = _sox_r94_read(B)
    pitch["input_hz"] = _sox_r94_peak_hz(base_arr, SOX_R94_RATE, 997.0)
    for name in ("len_12000_to_44100", "len_12000_to_22050", "len_12000_to_32000"):
        leg = L[name]
        arr = leg.get("_arr")
        if arr is None:
            continue
        pitch[name] = _sox_r94_peak_hz(arr, leg["out_rate"], 997.0)
    L["rate_pitch_preserved"] = {
        "name": "rate_pitch_preserved", "peak_hz": pitch,
        "note": "the tone stays at 997 Hz (own interpolated peak-frequency "
                "estimator, +/-120 Hz search); duration is frames/out_rate "
                "within one output sample"}
    vals = [v for k, v in pitch.items() if k != "input_hz" and v is not None]
    _sox_r94_arm(entry, L["rate_pitch_preserved"],
                 bool(vals) and all(abs(v - pitch["input_hz"]) <= 3.0 for v in vals),
                 "resampling must preserve pitch (997 Hz within 3 Hz of the "
                 f"input estimate at every output rate); got {pitch}")

    # --- the boundary-corrected alias lattice -----------------------------
    alias_specs = (
        ("alias_23k_default", J, ["rate", "44100"], "default"),
        ("alias_23k_h", J, ["rate", "-h", "44100"], "h"),
        ("alias_23k_v", J, ["rate", "-v", "44100"], "v"),
        ("alias_23k_u", J, ["rate", "-u", "44100"], "u"),
        ("alias_23k_q", J, ["rate", "-q", "44100"], "q"),
        ("alias_23k_a", J, ["rate", "-a", "44100"], "a"),
        ("alias_23k_m_a", J, ["rate", "-m", "-a", "44100"], "m_a"),
        ("alias_20k_default", H, ["rate", "44100"], "default"),
        ("alias_20k_l", H, ["rate", "-l", "44100"], "l"),
        ("alias_20k_a", H, ["rate", "-a", "44100"], "a"),
        ("alias_20k_v", H, ["rate", "-v", "44100"], "v"),
    )
    for name, infile, tail, opt in alias_specs:
        leg = _sox_r94_leg(scratch, name, [SOX_R94, "-D", "{in}", "{out}"] + tail, infile)
        L[name] = leg
        arr = leg.get("_arr")
        if arr is None:
            continue
        out_rate = _sox_r94_m(leg, "rate") or 44100
        leg["band_21100hz_db"] = _sox_r94_band_db(arr, out_rate, 21100.0)
        leg["band_20000hz_db"] = _sox_r94_band_db(arr, out_rate, 20000.0)
        leg["band_997hz_db"] = _sox_r94_band_db(arr, out_rate, 997.0)
        leg["peak_db_overall"] = _sox_r94_db(np.abs(arr).max()) if arr.size else None
        leg["option"] = opt
    _sox_r94_ref_arm(entry, L["alias_23k_default"], refs, "rate_D.json",
                     "rate44100_23k_default")
    _sox_r94_ref_arm(entry, L["alias_23k_q"], refs, "rate_D.json", "rate44100_23k_q")
    _sox_r94_ref_arm(entry, L["alias_23k_a"], refs, "rate_D.json",
                     "rate44100_23k_alias_a")
    _sox_r94_ref_arm(entry, L["alias_23k_m_a"], refs, "rate_D.json",
                     "rate44100_23k_m_alias_a")
    _sox_r94_ref_arm(entry, L["alias_20k_default"], refs, "rate_D.json",
                     "rate44100_20k_default")
    # The cross-seat METRIC law: this seat's own band estimator (calibrated by
    # SOX_R94_BAND_OFFSET_DB) must reproduce the scout's published band table
    # to 0.05 dB on the five rows it recorded — including a -129.6 dB
    # rejection floor. That is what re-derives the calibration per run.
    for legname, refname, keys in (
            ("alias_23k_default", "rate44100_23k_default",
             ("band_21100hz_db", "band_20000hz_db", "peak_db")),
            ("alias_23k_q", "rate44100_23k_q",
             ("band_21100hz_db", "band_20000hz_db", "peak_db")),
            ("alias_23k_a", "rate44100_23k_alias_a",
             ("band_21100hz_db", "peak_db")),
            ("alias_23k_m_a", "rate44100_23k_m_alias_a",
             ("band_21100hz_db", "peak_db")),
            ("alias_20k_default", "rate44100_20k_default",
             ("band_21100hz_db", "band_20000hz_db", "peak_db"))):
        _sox_r94_ref_metric_arm(entry, L[legname], refs, "rate_D.json", refname,
                                keys, 0.05)

    d23 = L["alias_23k_default"]
    q23 = L["alias_23k_q"]
    a23 = L["alias_23k_a"]
    m23 = L["alias_23k_m_a"]
    v23 = L["alias_23k_v"]
    h23 = L["alias_23k_h"]
    u23 = L["alias_23k_u"]
    _sox_r94_arm(entry, q23,
                 q23.get("band_21100hz_db") is not None and
                 q23["band_21100hz_db"] > -20.0 and
                 q23.get("peak_db_overall") is not None and
                 abs(q23["band_21100hz_db"] - q23["peak_db_overall"]) < 3.0,
                 "-q must FOLD the 23 kHz tone to 21.1 kHz at near-full level "
                 f"(content hazard); got band={q23.get('band_21100hz_db')} "
                 f"peak={q23.get('peak_db_overall')}")
    _sox_r94_arm(entry, d23,
                 d23.get("band_21100hz_db") is not None and
                 d23.get("peak_db_overall") is not None and
                 d23["band_21100hz_db"] < d23["peak_db_overall"] - 10.0,
                 "the DEFAULT resampler must reject the 23 kHz alias well below "
                 f"its own peak; got band={d23.get('band_21100hz_db')} "
                 f"peak={d23.get('peak_db_overall')}")
    _sox_r94_arm(entry, L["alias_23k_h"],
                 h23.get("band_21100hz_db") == d23.get("band_21100hz_db") and
                 h23["out_sha256"] == d23["out_sha256"],
                 "`-h` must be byte-identical to the default on the 23 kHz leg")
    _sox_r94_arm(entry, v23,
                 v23.get("band_21100hz_db") is not None and
                 d23.get("band_21100hz_db") is not None and
                 abs(v23["band_21100hz_db"] - d23["band_21100hz_db"]) < 1.0,
                 "`-v` must sit at the SAME rejection level as the default "
                 "(the scout's -130 dB claim is falsified; only the bytes differ)")
    _sox_r94_arm(entry, v23, v23["out_sha256"] != d23["out_sha256"],
                 "`-v` must still be a DIFFERENT filter (distinct bytes from "
                 "the default) even though its rejection level is identical")
    _sox_r94_arm(entry, u23, u23["out_sha256"] == v23["out_sha256"],
                 "`-u` must be byte-identical to `-v` on this build")
    _sox_r94_arm(entry, a23,
                 a23.get("band_21100hz_db") is not None and
                 -100.0 < a23["band_21100hz_db"] < -60.0,
                 "`-a` alone must leave the 23 kHz alias in the -60..-100 dB "
                 f"band; got {a23.get('band_21100hz_db')}")
    _sox_r94_arm(entry, m23,
                 m23.get("band_21100hz_db") is not None and
                 -95.0 < m23["band_21100hz_db"] < -60.0,
                 "`-m -a` must leave the alias in the -60..-95 dB band "
                 f"(worse than plain -a); got {m23.get('band_21100hz_db')}")

    # The disarm guard: the ~-130 dB figure belongs to the 20 kHz DEFAULT leg.
    d20 = L["alias_20k_default"]
    _sox_r94_arm(entry, d20,
                 d20.get("band_21100hz_db") is not None and
                 d20["band_21100hz_db"] < -110.0,
                 "the only ~-129.6 dB row in the lattice is the 20 kHz stimulus "
                 f"DEFAULT leg; got {d20.get('band_21100hz_db')}")
    L["rate_130db_home"] = {
        "name": "rate_130db_home",
        "disarmed_claim": "23 kHz `-v` rejects at -130 dB",
        "armed_corrected": {
            "23k_default_band_21100hz_db": d23.get("band_21100hz_db"),
            "23k_v_band_21100hz_db": v23.get("band_21100hz_db"),
            "23k_default_peak_db": d23.get("peak_db_overall"),
            "23k_v_peak_db": v23.get("peak_db_overall"),
            "20k_default_band_21100hz_db": d20.get("band_21100hz_db"),
        },
        "note": "FALSIFIED by the r94 boundary: no 23 kHz leg is near -130 dB; "
                "the figure is the 20 kHz default leg's 21.1 kHz band. Every "
                "23 kHz leg here is armed ABOVE -110 dB and the 20 kHz default "
                "row carries the -129.6 dB value."}
    band23 = [v for v in (d23.get("band_21100hz_db"), v23.get("band_21100hz_db"),
                          q23.get("band_21100hz_db"), a23.get("band_21100hz_db"),
                          m23.get("band_21100hz_db")) if v is not None]
    worst23 = min(band23) if band23 else None
    _sox_r94_arm(entry, L["rate_130db_home"],
                 worst23 is not None and worst23 > -110.0,
                 "no 23 kHz leg may be armed near -130 dB (falsified claim)")
    _sox_r94_arm(entry, L["rate_130db_home"],
                 d20.get("band_21100hz_db") is not None and
                 d20["band_21100hz_db"] < -120.0,
                 "the 20 kHz default leg must carry the ~-129.6 dB band")

    # --- the boundary's 20 kHz extensions (not in the scout's table) ------
    l20 = L["alias_20k_l"]
    a20 = L["alias_20k_a"]
    _sox_r94_arm(entry, l20,
                 l20.get("band_20000hz_db") is not None and
                 l20["band_20000hz_db"] < -10.0,
                 "`-l` is the real 20 kHz hole: the tone must be attenuated "
                 f"> 10 dB at 20 kHz; got {l20.get('band_20000hz_db')}")
    _sox_r94_arm(entry, a20,
                 a20.get("band_20000hz_db") is not None and
                 abs(a20["band_20000hz_db"]) < 1.5,
                 "`-a` must be FLAT at 20 kHz (the scout's curve table missed "
                 f"this row); got {a20.get('band_20000hz_db')}")
    _sox_r94_arm(entry, a20,
                 a20.get("band_21100hz_db") is not None and
                 a20["band_21100hz_db"] < -110.0,
                 "`-a` must carry the BEST alias rejection of the set at 21.1 kHz "
                 f"(boundary: -142.18 dB); got {a20.get('band_21100hz_db')}")

    # --- the -q -a refusal -------------------------------------------------
    leg = _sox_r94_leg(scratch, "rate_q_a_refusal",
                       [SOX_R94, "-D", "{in}", "{out}", "rate", "-q", "-a", "44100"],
                       J, want_metrics=False)
    L["rate_q_a_refusal"] = leg
    _sox_r94_arm(entry, leg,
                 leg["rc"] == 1 and "override options only work at higher quality "
                                    "levels" in (leg["reps"][0]["stderr"] or ""),
                 "`rate -q -a` must be a hard refusal rc 1 ('override options "
                 "only work at higher quality levels')")
    return _sox_r94_exit(_sox_r94_drop_arrays(entry))


def sox_remix_r94_entry():
    """remix / channels: the channel-selection laws (all under -D)."""
    entry = _sox_r94_entry(
        "r94 sox remix/channels: selection vs downmix",
        "`remix 1` SELECTS channel 1 (it does not sum); the auto downmix is "
        "floor((L+R+1)/2) and `channels 1` is the same bytes; -m is the raw "
        "sum and -p is rint((L+R)/sqrt2)")
    scratch = _sox_r94_scratch()
    refs = _sox_r94_scout_refs()
    st = _sox_r94_stimuli(entry, refs)
    A, B = st["a"], st["b"]
    L = entry["legs"]
    ain, _ = _sox_r94_read(A)
    bin_arr, _ = _sox_r94_read(B)
    Li = ain[:, 0] * 32768.0
    Ri = ain[:, 1] * 32768.0
    Bi = bin_arr[:, 0] * 32768.0

    def out_ints(leg):
        arr = leg.get("_arr")
        if arr is None:
            return None
        return arr * 32768.0

    def expect(name, tail, infile, want, msg, channel=None):
        leg = _sox_r94_leg(scratch, name, [SOX_R94, "-D", "{in}", "{out}"] + tail, infile)
        L[name] = leg
        o = out_ints(leg)
        if o is None:
            _sox_r94_block(entry, f"{name}: no parseable output -> law not armed")
            return leg
        if channel is not None:
            o = o[:, channel:channel + 1]
        n, mx = _sox_r94_mismatch(o, want)
        leg["mismatch"] = n
        leg["max_abs_diff"] = mx
        _sox_r94_arm(entry, leg, n == 0, msg)
        return leg

    sel_l = expect("remix_1_selects_L", ["remix", "1"], A, Li[:, None],
                   "`remix 1` must SELECT channel 1 (mismatch 0 vs L)")
    if sel_l.get("mismatch") == 0:
        n, mx = _sox_r94_mismatch(out_ints(sel_l), ((Li + Ri) / 2.0)[:, None])
        sel_l["mismatch_vs_mean"] = n
        _sox_r94_arm(entry, sel_l, n > 0,
                     "`remix 1` must NOT downmix to (L+R)/2 (a nonzero mean "
                     "mismatch is the discriminator)")

    auto = expect("remix_1_2_auto", ["remix", "1,2"], A,
                  np.floor((Li + Ri + 1.0) / 2.0)[:, None],
                  "the auto downmix must be floor((L+R+1)/2)")
    if auto.get("mismatch") == 0:
        n_nearest, _ = _sox_r94_mismatch(out_ints(auto), np.rint((Li + Ri) / 2.0)[:, None])
        auto["mismatch_vs_nearest_even"] = n_nearest
        _sox_r94_arm(entry, auto, n_nearest > 0,
                     "the auto downmix must NOT be a nearest-even mean (a "
                     "nonzero mismatch vs rint((L+R)/2) is the discriminator)")
    _sox_r94_ref_arm(entry, auto, refs, "remix_D.json", "remix_1_2_sum")

    ch1 = expect("channels_1", ["channels", "1"], A,
                 np.floor((Li + Ri + 1.0) / 2.0)[:, None],
                 "`channels 1` must be the same downmix as `remix 1,2`")
    _sox_r94_arm(entry, ch1, ch1["out_sha256"] == auto["out_sha256"],
                 "`channels 1` and `remix 1,2` must be the same bytes")
    _sox_r94_ref_arm(entry, ch1, refs, "remix_D.json", "channels_1")

    msum = expect("remix_m_1_2", ["remix", "-m", "1,2"], A, (Li + Ri)[:, None],
                  "`-m 1,2` must be the exact (unscaled) L+R sum")
    _sox_r94_ref_arm(entry, msum, refs, "remix_D.json", "remix_m_1_2")
    psum = expect("remix_p_1_2", ["remix", "-p", "1,2"], A,
                  np.rint((Li + Ri) / np.sqrt(2.0))[:, None],
                  "`-p 1,2` must be rint((L+R)/sqrt2)")
    _sox_r94_ref_arm(entry, psum, refs, "remix_D.json", "remix_p_1_2")

    swap = expect("remix_swap_2_1", ["remix", "2", "1"], A,
                  np.column_stack([Ri, Li]), "`remix 2 1` must swap the channels")
    _sox_r94_ref_arm(entry, swap, refs, "remix_D.json", "remix_swap_2_1")
    left = expect("remix_left_only", ["remix", "1", "0"], A,
                  np.column_stack([Li, np.zeros_like(Li)]),
                  "`remix 1 0` must keep L and zero channel 2")
    # CORRECTION to the scout's leg NAMING: `remix 0 1` is [silence, in1] —
    # the Nth spec argument describes the Nth OUTPUT channel and its number
    # names an INPUT channel, so the second output channel carries L (peak
    # -6.0206), not R. The scout's receipt calls this row `remix_right_only`
    # (its peak is [-inf, -6.0206]); the semantics are pinned here.
    right = expect("remix_0_1_zero_then_in1", ["remix", "0", "1"], A,
                   np.column_stack([np.zeros_like(Li), Li]),
                   "`remix 0 1` must be [silence, INPUT channel 1] — the "
                   "spec number names an INPUT channel and the position names "
                   "the output channel")
    _sox_r94_ref_arm(entry, left, refs, "remix_D.json", "remix_left_only")
    _sox_r94_ref_arm(entry, right, refs, "remix_D.json", "remix_right_only")

    vhalf = expect("remix_v_half", ["remix", "1v0.5", "2v0.5"], A,
                   np.column_stack([np.ceil(Li * 0.5), np.ceil(Ri * 0.5)]),
                   "`remix 1v0.5 2v0.5` must apply the v multiplier on the "
                   "amplitude (ceil) path")
    vol_ctl = _sox_r94_leg(scratch, "remix_vol_control",
                           [SOX_R94, "-D", "{in}", "{out}", "vol", "0.5"], A)
    L["remix_vol_control"] = vol_ctl
    _sox_r94_arm(entry, vhalf, vhalf["out_sha256"] == vol_ctl["out_sha256"],
                 "`remix 1v0.5 2v0.5` must be the SAME BYTES as `vol 0.5` "
                 "(the v multiplier is the amplitude/ceil path)")
    _sox_r94_ref_arm(entry, vhalf, refs, "remix_D.json", "remix_v_half")

    p6 = _sox_r94_leg(scratch, "remix_p_minus6",
                      [SOX_R94, "-D", "{in}", "{out}", "remix", "1p-6"], A)
    L["remix_p_minus6"] = p6
    _sox_r94_arm(entry, p6, _sox_r94_close(_sox_r94_m(p6, "peak_db"), [-12.0211], 5e-4),
                 "`remix 1p-6` must apply exactly -6 dB on the p path "
                 f"(peak -12.0211 = -6.0206 - 6.0005); got {_sox_r94_m(p6, 'peak_db')}")
    _sox_r94_ref_arm(entry, p6, refs, "remix_D.json", "remix_p_minus6")

    up = _sox_r94_leg(scratch, "mono_to_stereo_1_1",
                      [SOX_R94, "-D", "{in}", "{out}", "remix", "1", "1"], B)
    L["mono_to_stereo_1_1"] = up
    o = out_ints(up)
    if o is not None:
        n0, _ = _sox_r94_mismatch(o[:, 0:1], Bi[:, None])
        n1, _ = _sox_r94_mismatch(o[:, 1:2], Bi[:, None])
        up["mismatch_ch0"], up["mismatch_ch1"] = n0, n1
        _sox_r94_arm(entry, up, _sox_r94_m(up, "channels") == 2 and n0 == 0 and n1 == 0,
                     "`remix 1 1` must duplicate a mono input into both channels")
    _sox_r94_ref_arm(entry, up, refs, "remix_D.json", "mono_to_stereo_1_1")
    return _sox_r94_exit(_sox_r94_drop_arrays(entry))


def sox_trim_r94_entry():
    """trim: the `s`-suffix law, the rounding boundary, and the form lattice."""
    entry = _sox_r94_entry(
        "r94 sox trim: sample suffix + rounding + forms",
        "the `s` suffix means SAMPLES; the sub-sample decimals follow float32 "
        "representation, so the row is armed as |measured - round(len*rate)| "
        "<= 1, never as a decimal-exact pin")
    scratch = _sox_r94_scratch()
    refs = _sox_r94_scout_refs()
    st = _sox_r94_stimuli(entry, refs)
    B = st["b"]
    L = entry["legs"]
    bin_arr, _ = _sox_r94_read(B)
    bin_i = bin_arr * 32768.0
    IN_FRAMES = bin_arr.shape[0]

    def trim_leg(name, tail, reps=1):
        leg = _sox_r94_leg(scratch, name, [SOX_R94, "-D", "{in}", "{out}"] + tail,
                           B, reps=reps)
        L[name] = leg
        return leg

    one = trim_leg("trim_0_1s", ["trim", "0", "1s"])
    _sox_r94_arm(entry, one, _sox_r94_m(one, "frames") == 1,
                 "`trim 0 1s` must keep ONE SAMPLE (the s suffix is samples, "
                 f"not seconds); got {_sox_r94_m(one, 'frames')}")
    four8 = trim_leg("trim_0_4800s", ["trim", "0", "4800s"])
    _sox_r94_arm(entry, four8, _sox_r94_m(four8, "frames") == 4800,
                 "`trim 0 4800s` must keep 4 800 samples")
    tiny = trim_leg("trim_0_1e-9", ["trim", "0", "1e-9"])
    _sox_r94_arm(entry, tiny, tiny["rc"] == 1,
                 "`trim 0 1e-9` must refuse rc 1")
    sec = trim_leg("trim_0_1sec", ["trim", "0", "1sec"])
    _sox_r94_arm(entry, sec,
                 sec["rc"] == 1 and
                 sec["reps"][0]["error_class"] == "sox_r94_parse",
                 "`trim 0 1sec` must refuse with the cannot-parse-position class")

    matrix = (0.09995, 0.09997917, 0.09998958, 0.1000104, 0.1000208,
              0.10003125, 0.10001, 0.09999)
    rows = {}
    for val in matrix:
        name = f"trim_round_{str(val).replace('.', '_')}"
        leg = trim_leg(name, ["trim", "0", repr(val)])
        frames = _sox_r94_m(leg, "frames")
        want = round(val * SOX_R94_RATE)
        leg["want_frames"] = want
        leg["delta"] = None if frames is None else frames - want
        rows[str(val)] = frames
        _sox_r94_arm(entry, leg, frames is not None and abs(frames - want) <= 1,
                     f"trim 0 {val} must be within +/-1 frame of "
                     f"round(len*rate) = {want}; got {frames}")
    L["trim_rounding_matrix"] = {"name": "trim_rounding_matrix", "frames": rows,
                                 "note": "sub-sample decimals follow the float32 "
                                         "representation: armed with a +/-1 frame "
                                         "tolerance, never as a decimal pin"}
    _sox_r94_ref_arm(entry, L["trim_round_0_09997917"], refs, "trim_D.json",
                     "trim_0_0.09997917")

    forms = (("trim_0_0.1", ["trim", "0", "0.1"], 4800),
             ("trim_0.1", ["trim", "0.1"], 7200),
             ("trim_0_minus0.1", ["trim", "0", "-0.1"], 7200),
             ("trim_0_eq0.1", ["trim", "0", "=0.1"], 4800),
             ("trim_0.05_plus0.05", ["trim", "0.05+0.05"], 7200),
             ("trim_0_100", ["trim", "0", "100"], IN_FRAMES),
             ("trim_0_0", ["trim", "0", "0"], 0))
    for name, tail, want in forms:
        leg = trim_leg(name, tail)
        _sox_r94_arm(entry, leg, _sox_r94_m(leg, "frames") == want,
                     f"`{' '.join(tail)}` must produce {want} frames; got "
                     f"{_sox_r94_m(leg, 'frames')}")
    _sox_r94_arm(entry, L["trim_0_100"],
                 "End position is after expected end of audio" in
                 (L["trim_0_100"]["reps"][0]["stderr"] or ""),
                 "`trim 0 100` must WARN that the end position was not reached "
                 "while still taking what exists")
    _sox_r94_ref_arm(entry, L["trim_0_0.1"], refs, "trim_D.json", "trim_0_0.1")
    _sox_r94_ref_arm(entry, L["trim_0.1"], refs, "trim_D.json", "trim_0.1")
    _sox_r94_ref_arm(entry, L["trim_0_minus0.1"], refs, "trim_D.json",
                     "trim_0_minus0.1")
    _sox_r94_ref_arm(entry, L["trim_0_eq0.1"], refs, "trim_D.json", "trim_0_eq0.1")
    _sox_r94_ref_arm(entry, L["trim_0_100"], refs, "trim_D.json", "trim_0_100")
    _sox_r94_ref_arm(entry, L["trim_0_0"], refs, "trim_D.json", "trim_0_0")

    exact = L["trim_0_0.1"]
    arr = exact.get("_arr")
    if arr is not None:
        n, mx = _sox_r94_mismatch(arr * 32768.0, bin_i[:4800])
        exact["mismatch_vs_input_head"] = n
        _sox_r94_arm(entry, exact, n == 0,
                     "trim content must be SAMPLE-EXACT (the first 4 800 frames "
                     "of the input, mismatch 0)")
    return _sox_r94_exit(_sox_r94_drop_arrays(entry))


def sox_fade_r94_entry():
    """fade: the truncation trap and the 100 dB-per-span log law."""
    entry = _sox_r94_entry(
        "r94 sox fade: stop-truncation + log law + curve table",
        "fade TRUNCATES the file at its second positional (stop) argument — a "
        "silent data-loss trap; the log curve is exactly 100 dB per span "
        "(10^(-5(1-x))) and the default type is `l`")
    scratch = _sox_r94_scratch()
    refs = _sox_r94_scout_refs()
    st = _sox_r94_stimuli(entry, refs)
    B = st["b"]
    L = entry["legs"]
    bin_arr, _ = _sox_r94_read(B)
    bin_i = bin_arr[:, 0] * 32768.0
    SPAN = 4800                     # 0.1 s at 48 kHz

    def ratio_at(leg, x):
        arr = leg.get("_arr")
        if arr is None:
            return None
        f = int(round(x * SPAN))
        if f >= arr.shape[0] or f >= bin_i.shape[0]:
            return None
        i = float(bin_i[f])
        if abs(i) < 2000.0:
            return None
        return round(float(arr[f, 0]) * 32768.0 / i, 6)

    trunc = (("fade_stop_0.15_len_0.1", ["fade", "0", "0.15", "0.1"], 7200),
             ("fade_stop_0.2_len_0.05", ["fade", "0", "0.2", "0.05"], 9600),
             ("fade_stop_0.25_len_0.1", ["fade", "0", "0.25", "0.1"], 12000))
    for name, tail, want in trunc:
        leg = _sox_r94_leg(scratch, name, [SOX_R94, "-D", "{in}", "{out}"] + tail, B)
        L[name] = leg
        _sox_r94_arm(entry, leg, _sox_r94_m(leg, "frames") == want,
                     f"`{' '.join(tail)}` must TRUNCATE the file to {want} frames "
                     f"(the stop positional ends the output); got "
                     f"{_sox_r94_m(leg, 'frames')}")
    _sox_r94_ref_arm(entry, L["fade_stop_0.15_len_0.1"], refs, "fade_D.json",
                     "fade_out_stop0.15_len0.1")
    _sox_r94_ref_arm(entry, L["fade_stop_0.2_len_0.05"], refs, "fade_D.json",
                     "fade_out_stop0.2_len0.05")

    log = _sox_r94_leg(scratch, "fade_log_100db",
                       [SOX_R94, "-D", "{in}", "{out}", "fade", "l", "0.1"], B)
    L["fade_log_100db"] = log
    measured, want = {}, {}
    for x in (0.5, 0.75, 0.9):
        measured[str(x)] = ratio_at(log, x)
        want[str(x)] = round(10 ** (-5 * (1 - x)), 6)
    log["envelope_measured"] = measured
    log["envelope_expected"] = want
    ok = True
    for x in measured:
        if measured[x] is None or want[x] is None:
            ok = False
            continue
        if abs(measured[x] - want[x]) / want[x] > 0.03:
            ok = False
    _sox_r94_arm(entry, log, ok,
                 "the log fade must follow 10^(-5(1-x)) (100 dB per span) "
                 f"within 3%; measured {measured} vs {want}")
    _sox_r94_ref_arm(entry, log, refs, "fade_D.json", "fade_in_l_0.1")

    curves = {"q": {"0.25": 0.382630, "0.5": 0.707129, "0.75": 0.923866},
              "h": {"0.25": 0.146410, "0.5": 0.499962, "0.75": 0.853541},
              "t": {"0.25": 0.249933, "0.5": 0.499962, "0.75": 0.749969},
              "p": {"0.25": 0.437483, "0.5": 0.749981, "0.75": 0.937523},
              "s": {"0.25": 0.062517, "0.5": 0.250019, "0.75": 0.562477}}
    table = {}
    for ctype, expect_map in curves.items():
        leg = _sox_r94_leg(scratch, f"fade_curve_{ctype}",
                           [SOX_R94, "-D", "{in}", "{out}", "fade", ctype, "0.1"], B)
        L[f"fade_curve_{ctype}"] = leg
        got = {x: ratio_at(leg, float(x)) for x in expect_map}
        table[ctype] = {"measured": got, "expected": expect_map}
        bad = [x for x in expect_map
               if got[x] is None or
               abs(got[x] - expect_map[x]) / expect_map[x] > 0.03]
        _sox_r94_arm(entry, leg, not bad,
                     f"the `{ctype}` curve must match its pinned table within "
                     f"3% (bad: {bad})")
    L["fade_curve_table"] = {"name": "fade_curve_table", "table": table,
                             "note": "the scout's six-type table, re-measured "
                                     "as out/in ratios at x = .25/.5/.75"}
    _sox_r94_ref_arm(entry, L["fade_curve_q"], refs, "fade_D.json", "fade_in_q_0.1")
    _sox_r94_ref_arm(entry, L["fade_curve_h"], refs, "fade_D.json", "fade_in_h_0.1")
    _sox_r94_ref_arm(entry, L["fade_curve_t"], refs, "fade_D.json", "fade_in_t_0.1")
    _sox_r94_ref_arm(entry, L["fade_curve_p"], refs, "fade_D.json", "fade_in_p_0.1")
    _sox_r94_ref_arm(entry, L["fade_curve_s"], refs, "fade_D.json", "fade_in_s_0.1")

    default = _sox_r94_leg(scratch, "fade_default_type",
                           [SOX_R94, "-D", "{in}", "{out}", "fade", "0.1"], B)
    L["fade_default_type"] = default
    _sox_r94_arm(entry, default, default["out_sha256"] == log["out_sha256"],
                 "the DEFAULT fade type must be `l` (identical bytes)")
    _sox_r94_ref_arm(entry, default, refs, "fade_D.json", "fade_in_0.1")

    arr = log.get("_arr")
    if arr is not None and arr.shape[0] > 0:
        log["first_out_sample"] = int(round(float(arr[0, 0]) * 32768.0))
        _sox_r94_arm(entry, log, log["first_out_sample"] == 0,
                     "the first frame of a log fade must be 0 under -D (the "
                     "scout's -1 in the default pass was dither on a zero sample)")
    return _sox_r94_exit(_sox_r94_drop_arrays(entry))


def sox_repeat_pad_silence_r94_entry():
    """repeat / pad / silence: the tiling, insertion and window-lag laws."""
    entry = _sox_r94_entry(
        "r94 sox repeat/pad/silence",
        "repeat N is N ADDITIONAL copies (sample-exact tiling); `pad %50` is a "
        "silent no-op; silence's below-periods side keeps window_size-1 = "
        "rate/50-1 samples of the silent period")
    scratch = _sox_r94_scratch()
    refs = _sox_r94_scout_refs()
    st = _sox_r94_stimuli(entry, refs)
    B, C2 = st["b"], st["c2"]
    L = entry["legs"]
    bin_arr, _ = _sox_r94_read(B)
    bin_i = bin_arr[:, 0] * 32768.0
    N = bin_arr.shape[0]

    rep2 = _sox_r94_leg(scratch, "repeat_2",
                        [SOX_R94, "-D", "{in}", "{out}", "repeat", "2"], B)
    L["repeat_2"] = rep2
    arr = rep2.get("_arr")
    if arr is not None:
        tiled = np.tile(bin_i, 3)[:arr.shape[0]]
        n, mx = _sox_r94_mismatch(arr[:, 0] * 32768.0, tiled)
        rep2["mismatch_vs_tiling"] = n
        _sox_r94_arm(entry, rep2,
                     _sox_r94_m(rep2, "frames") == 3 * N and n == 0,
                     "`repeat 2` must be N ADDITIONAL copies: 3N frames, "
                     "sample-exact tiling (out[n] == in[n mod N])")
    _sox_r94_ref_arm(entry, rep2, refs, "repeat_pad_silence_D.json", "repeat_2")

    rep0 = _sox_r94_leg(scratch, "repeat_0",
                        [SOX_R94, "-D", "{in}", "{out}", "repeat", "0"], B)
    L["repeat_0"] = rep0
    _sox_r94_arm(entry, rep0, rep0["out_sha256"] == _sox_r94_sha(B),
                 "`repeat 0` must be the identity")
    _sox_r94_ref_arm(entry, rep0, refs, "repeat_pad_silence_D.json", "repeat_0")

    repneg = _sox_r94_leg(scratch, "repeat_neg1",
                          [SOX_R94, "-D", "{in}", "{out}", "repeat", "-1"], B,
                          want_metrics=False)
    L["repeat_neg1"] = repneg
    _sox_r94_arm(entry, repneg, repneg["rc"] == 1,
                 "`repeat -1` must refuse rc 1")

    pad = _sox_r94_leg(scratch, "pad_0.1_0.2",
                       [SOX_R94, "-D", "{in}", "{out}", "pad", "0.1", "0.2"], B)
    L["pad_0.1_0.2"] = pad
    arr = pad.get("_arr")
    if arr is not None:
        ints = np.rint(arr[:, 0] * 32768.0).astype("int64")
        nz = np.nonzero(ints)[0]
        pad["first_nonzero_frame"] = int(nz[0]) if nz.size else None
        pad["last_nonzero_frame"] = int(nz[-1]) if nz.size else None
        pad["zero_frames_total"] = int(np.count_nonzero(ints == 0))
        _sox_r94_arm(entry, pad,
                     _sox_r94_m(pad, "frames") == N + 4800 + 9600 and
                     pad["first_nonzero_frame"] == 4801 and
                     pad["last_nonzero_frame"] == 16799,
                     "`pad 0.1 0.2` must insert 4 800 frames before and 9 600 "
                     "after (first_nonzero 4801 — b[0] is already 0)")
    _sox_r94_ref_arm(entry, pad, refs, "repeat_pad_silence_D.json", "pad_0.1_0.2")

    padv = _sox_r94_leg(scratch, "pad_0.05_at_0.05",
                        [SOX_R94, "-D", "{in}", "{out}", "pad", "0.05@0.05"], B)
    L["pad_0.05_at_0.05"] = padv
    _sox_r94_arm(entry, padv, _sox_r94_m(padv, "frames") == N + 2400,
                 "`pad 0.05@0.05` must insert 2 400 frames at 0.05 s")

    padpct = _sox_r94_leg(scratch, "pad_pct50",
                          [SOX_R94, "-D", "{in}", "{out}", "pad", "%50"], B)
    L["pad_pct50"] = padpct
    _sox_r94_arm(entry, padpct, padpct["out_sha256"] == _sox_r94_sha(B),
                 "`pad %50` must be a SILENT NO-OP on this build (byte-identical "
                 "to the input, not 'pads by 50%')")
    _sox_r94_ref_arm(entry, padpct, refs, "repeat_pad_silence_D.json", "pad_pct50")

    # --- silence: the window-lag law -------------------------------------
    WINDOW = SOX_R94_RATE // 50 - 1          # 959 at 48 kHz
    c2_arr, _ = _sox_r94_read(C2)
    sil = _sox_r94_leg(scratch, "silence_above_only",
                       [SOX_R94, "-D", "{in}", "{out}", "silence", "1", "0.1", "1%"], C2)
    L["silence_above_only"] = sil
    arr = sil.get("_arr")
    if arr is not None:
        ints = np.rint(arr[:, 0] * 32768.0).astype("int64")
        trail = 0
        for v in ints[::-1]:
            if v != 0:
                break
            trail += 1
        sil["trailing_zero_frames"] = trail
        nz = np.nonzero(ints)[0]
        sil["last_nonzero_frame"] = int(nz[-1]) if nz.size else None
        _sox_r94_arm(entry, sil,
                     _sox_r94_m(sil, "frames") == c2_arr.shape[0] - 4804,
                     "`silence 1 0.1 1%` must cut the LEADING silence at the "
                     f"windowed-RMS crossing (4 804 frames); got "
                     f"{_sox_r94_m(sil, 'frames')} (input {c2_arr.shape[0]})")
        _sox_r94_arm(entry, sil, trail == 7200,
                     "without a below-periods clause the TRAILING silence must "
                     f"be kept whole (7 200 frames); got {trail}")
    _sox_r94_ref_arm(entry, sil, refs, "repeat_pad_silence_D.json",
                     "c2_silence_above_only")

    both = _sox_r94_leg(scratch, "silence_both_0.1",
                        [SOX_R94, "-D", "{in}", "{out}", "silence", "1", "0.1", "1%",
                         "1", "0.1", "1%"], C2)
    L["silence_both_0.1"] = both
    arr = both.get("_arr")
    if arr is not None:
        ints = np.rint(arr[:, 0] * 32768.0).astype("int64")
        trail = 0
        for v in ints[::-1]:
            if v != 0:
                break
            trail += 1
        both["trailing_zero_frames"] = trail
        _sox_r94_arm(entry, both, trail == WINDOW,
                     "the below-periods side must keep window_size-1 = "
                     f"rate/50-1 = {WINDOW} samples of the silent period; "
                     f"got {trail}")
        _sox_r94_arm(entry, both,
                     _sox_r94_m(both, "frames") == c2_arr.shape[0] - 4804 - (7200 - WINDOW),
                     "the both-sides leg must cut leading 4 804 AND trailing "
                     f"{7200 - WINDOW} frames; got {_sox_r94_m(both, 'frames')}")
    _sox_r94_ref_arm(entry, both, refs, "repeat_pad_silence_D.json",
                     "c2_silence_both_0.1")

    leave = _sox_r94_leg(scratch, "silence_both_leave",
                         [SOX_R94, "-D", "{in}", "{out}", "silence", "-l",
                          "1", "0.1", "1%", "1", "0.1", "1%"], C2)
    L["silence_both_leave"] = leave
    arr = leave.get("_arr")
    if arr is not None:
        ints = np.rint(arr[:, 0] * 32768.0).astype("int64")
        trail = 0
        for v in ints[::-1]:
            if v != 0:
                break
            trail += 1
        leave["trailing_zero_frames"] = trail
        _sox_r94_arm(entry, leave, trail == WINDOW + 4800,
                     "`-l` must KEEP the declared duration plus the window lag "
                     f"({WINDOW + 4800} = {WINDOW} + 4 800); got {trail}")
    _sox_r94_ref_arm(entry, leave, refs, "repeat_pad_silence_D.json",
                     "c2_silence_both_leave")

    zero = _sox_r94_leg(scratch, "silence_zero_periods",
                        [SOX_R94, "-D", "{in}", "{out}", "silence", "0", "0.1", "1%"],
                        C2, want_metrics=False)
    L["silence_zero_periods"] = zero
    _sox_r94_arm(entry, zero, zero["rc"] == 1,
                 "`silence 0 ...` must refuse rc 1 (below-periods requires a "
                 "duration and a threshold)")

    for name, thresh in (("silence_thresh_frac", "0.01"), ("silence_thresh_db", "-60d")):
        leg = _sox_r94_leg(scratch, name,
                           [SOX_R94, "-D", "{in}", "{out}", "silence", "1",
                            "0.05", thresh], st["c"])
        L[name] = leg
        _sox_r94_arm(entry, leg, leg["rc"] == 0,
                     f"the threshold spelling `{thresh}` must be accepted rc 0")
    _sox_r94_ref_arm(entry, L["silence_thresh_frac"], refs,
                     "repeat_pad_silence_D.json", "silence_1_0.05_0.01frac")
    _sox_r94_ref_arm(entry, L["silence_thresh_db"], refs,
                     "repeat_pad_silence_D.json", "silence_1_0.05_neg60d")
    return _sox_r94_exit(_sox_r94_drop_arrays(entry))


def sox_dither_stat_r94_entry():
    """dither error envelope, the guard row, and the stat field definitions."""
    entry = _sox_r94_entry(
        "r94 sox dither envelope + stat field definitions",
        "dither -s under -R has a pinned error envelope (max ~21-22 LSB, rms "
        "5.7407); stat's RMS is the per-channel quadratic mean and its delta "
        "fields are computed on the INTERLEAVED stream")
    scratch = _sox_r94_scratch()
    refs = _sox_r94_scout_refs()
    st = _sox_r94_stimuli(entry, refs)
    A, B, F = st["a"], st["b"], st["f"]
    L = entry["legs"]
    f_arr, _ = _sox_r94_read(F)
    A_arr, _ = _sox_r94_read(A)
    aim = A_arr.reshape(-1)

    def dither_err(leg):
        arr = leg.get("_arr")
        if arr is None:
            return None, None, None
        ints = np.rint(np.asarray(arr).reshape(-1) * 32768.0)
        want = np.rint(f_arr.reshape(-1) * 32768.0)
        n = min(ints.size, want.size)
        e = np.abs(ints[:n] - want[:n])
        if not e.size:
            return None, None, None
        return int(e.max()), round(float(np.sqrt((e ** 2).mean())), 6), int(np.count_nonzero(e))

    d_s = _sox_r94_leg(scratch, "dither_s_R",
                       [SOX_R94, "-R", "{in}", "-b", "16", "{out}", "dither", "-s"],
                       F, reps=SOX_R94_REPS)
    L["dither_s_R"] = d_s
    mx, rms, nz = dither_err(d_s)
    d_s.update({"max_abs_err": mx, "err_rms": rms, "nonzero_err_samples": nz})
    _sox_r94_arm(entry, d_s, mx is not None and 15 <= mx <= 30,
                 f"noise-shaped dither -s must stay in the ~21-22 LSB envelope; "
                 f"got max {mx}")
    _sox_r94_arm(entry, d_s, rms is not None and 5.70 <= rms <= 5.78,
                 f"the -R error RMS must be ~5.7407 (the DETERMINISTIC leg — the "
                 f"scout's 5.8 was the nondeterministic one); got {rms}")
    _sox_r94_arm(entry, d_s, d_s["stable"],
                 "`-R dither -s` must be byte-stable across 3 fresh processes")
    _sox_r94_ref_arm(entry, d_s, refs, "dither_D.json", "f32_to_s16_dither_s_R")
    _sox_r94_ref_metric_arm(entry, d_s, refs, "dither_D.json",
                            "f32_to_s16_dither_s_R", ("max_abs_err", "err_rms"), 1e-6)

    d_p = _sox_r94_leg(scratch, "dither_p12_R",
                       [SOX_R94, "-R", "{in}", "-b", "16", "{out}", "dither", "-p", "12"],
                       F)
    L["dither_p12_R"] = d_p
    mx, rms, nz = dither_err(d_p)
    d_p.update({"max_abs_err": mx, "err_rms": rms, "nonzero_err_samples": nz})
    _sox_r94_arm(entry, d_p, mx is not None and 15 <= mx <= 30,
                 f"`dither -p 12` must stay in the same envelope (scout: 23 LSB); "
                 f"got {mx}")
    _sox_r94_ref_metric_arm(entry, d_p, refs, "dither_D.json",
                            "f32_to_s16_dither_p12_R", ("max_abs_err", "err_rms"), 1e-6)

    # The guard row: -G is not a limiter. The DEFAULT path is dither-sensitive
    # (the boundary measured 7 979 vs 3 989 at the >=32767 threshold) and is
    # recorded, never armed; the -D equality is armed in sox_gain_r94_entry.
    def railed(leg, thresh):
        arr = leg.get("_arr")
        if arr is None:
            return None
        ints = np.rint(arr * 32768.0)
        return int(np.count_nonzero(np.abs(ints) >= thresh))

    g_def = _sox_r94_leg(scratch, "guard_gain_p12_default",
                         [SOX_R94, "{in}", "{out}", "gain", "12"], A)
    g_g_def = _sox_r94_leg(scratch, "guard_G_gain_p12_default",
                           [SOX_R94, "-G", "{in}", "{out}", "gain", "12"], A)
    # Single-rep default-path legs: their bytes are time-seeded-dither
    # nondeterministic across runs even though one rep cannot show it, so the
    # sha is marked volatile by law (the guard row is RECORDED, not armed).
    for _leg in (g_def, g_g_def):
        _leg["volatile_sha"] = True
        _leg["volatile_reason"] = "default-path auto-dither (time-seeded TPDF)"
    L["guard_gain_p12_default"], L["guard_G_gain_p12_default"] = g_def, g_g_def
    c1, c2_ = railed(g_def, 32767), railed(g_g_def, 32767)
    L["guard_default_path_row"] = {
        "name": "guard_default_path_row", "threshold": 32767,
        "railed_gain12_default": c1, "railed_G_gain12_default": c2_,
        "note": "IMPRECISION, arm differently: the default-path count is "
                "dither-sensitive (boundary: 7 979 vs 3 989), so this row is "
                "RECORDED and only the -D equality (>= 32 766) is armed."}
    _sox_r94_arm(entry, L["guard_default_path_row"],
                 c1 is not None and c1 > 0 and c2_ is not None and c2_ > 0,
                 "`gain 12` must clip on the default path (a positive railed "
                 "count is the only stable half of this row)")

    # --- stat: the field definitions -------------------------------------
    def text_leg(name, argv, reps=1):
        recs, texts, shas = [], [], []
        for _ in range(reps):
            r = _sox_r94_spawn(argv, timeout=SOX_R94_WALL)
            t = r.get("stderr_text") or ""
            texts.append(t)
            shas.append(hashlib.sha256(t.encode()).hexdigest())
            recs.append({"rc": r.get("exit_code"), "wall_s": r.get("wall_s"),
                         "stderr_bytes": r.get("stderr_bytes"),
                         "text_sha256": shas[-1],
                         "killed_at_bound": r.get("killed_at_bound")})
        leg = {"name": name, "argv": [str(x).replace(str(ROOT), "<ROOT>") for x in argv],
               "rc": recs[0]["rc"], "reps": recs, "reps_n": reps,
               "text_sha256": shas[0], "n_distinct_text_shas": len(set(shas)),
               "stable": len(set(shas)) == 1, "text": texts[0][:4000],
               "_text_full": texts[0]}
        L[name] = leg
        return leg

    def fields_of(text):
        """sox's `stat` field block. Keys carry digits (EBUR128 ...), so the
        key class must admit them."""
        out = {}
        for ln in (text or "").splitlines():
            m = re.match(r"^([A-Za-z][A-Za-z0-9 ]*?):\s+(.+?)\s*$", ln)
            if m:
                out[re.sub(r"\s+", " ", m.group(1)).strip()] = m.group(2)
        return out

    stat = text_leg("stat_plain_a", [SOX_R94, str(A), "-n", "stat"], reps=2)
    f = fields_of(stat["_text_full"])
    stat["fields"] = f
    _sox_r94_arm(entry, stat, stat["stable"],
                 "`sox <in> -n stat` text must be byte-stable across reps")
    np_rms = round(float(np.sqrt((aim ** 2).mean())), 6)
    np_delta = round(float(np.abs(np.diff(aim)).max()), 6)
    stat["numpy_rms_quadratic_mean"] = np_rms
    stat["numpy_max_interleaved_delta"] = np_delta
    if "RMS amplitude" in f:
        got = float(f["RMS amplitude"])
        _sox_r94_arm(entry, stat, abs(got - np_rms) < 1e-5,
                     "stat's RMS amplitude must be the quadratic mean over the "
                     f"INTERLEAVED stream ({np_rms}); got {got}")
    else:
        _sox_r94_block(entry, "stat_plain_a: no RMS amplitude field parsed")
    if "Maximum delta" in f:
        got = float(f["Maximum delta"])
        _sox_r94_arm(entry, stat, abs(got - np_delta) < 1e-5,
                     "stat's Maximum delta must be the max |x[i+1]-x[i]| on the "
                     f"INTERLEAVED stream ({np_delta} — not the per-channel "
                     f"0.065277); got {got}")
    if "Volume adjustment" in f:
        _sox_r94_arm(entry, stat, float(f["Volume adjustment"]) == 2.0,
                     "stat's Volume adjustment must be the factor to 0 dBFS "
                     f"(2.000 for a 0.5 FS file); got {f['Volume adjustment']}")

    statv = text_leg("stat_v_a", [SOX_R94, str(A), "-n", "stat", "-v"], reps=2)
    statv["only_number"] = statv["_text_full"].strip()
    _sox_r94_arm(entry, statv, statv["_text_full"].strip() == "2.000",
                 "`stat -v` must print ONLY the volume-adjustment number")

    statsj = text_leg("stats_j_a", [SOX_R94, str(A), "-n", "stats", "-j"], reps=2)
    try:
        jdoc = json.loads(statsj["_text_full"])
    except Exception as exc:                       # noqa: BLE001 - recorded
        jdoc = None
        statsj["json_error"] = str(exc)[:120]
    statsj["json"] = jdoc
    if isinstance(jdoc, dict):
        _sox_r94_arm(entry, statsj,
                     jdoc.get("channel_count") == 2 and
                     jdoc.get("overall", {}).get("window") == 0.05,
                     "`stats -j` must report channel_count and the 0.05 s window")
        ch0 = (jdoc.get("channels") or [{}])[0]
        statsj["channel0"] = {k: ch0.get(k) for k in
                              ("rms_level_db", "crest_factor", "peak_count",
                               "min_level", "max_level")}
        _sox_r94_arm(entry, statsj,
                     abs(float(ch0.get("rms_level_db", 0)) - (-9.03088)) < 1e-3 and
                     ch0.get("peak_count") == 2000,
                     "`stats -j` channel 0 must report the per-channel rms level "
                     f"(-9.03088) and its peak_count; got {statsj['channel0']}")
    else:
        _sox_r94_block(entry, "stats_j_a: JSON not parseable -> not armed")

    for name, infile in (("stat_freq_a", A), ("stat_freq_b", B)):
        leg = text_leg(name, [SOX_R94, str(infile), "-n", "stat", "-freq"])
        full = leg["_text_full"]
        nums = [ln for ln in full.splitlines()
                if re.match(r"^\s*[\d.]+\s+[\d.]+\s*$", ln)]
        freqs = [float(ln.split()[0]) for ln in nums]
        step = round(freqs[1] - freqs[0], 6) if len(freqs) > 1 else None
        samples = None
        flds = fields_of(full)
        if "Samples read" in flds:
            samples = int(flds["Samples read"])
        n_spec = None
        if samples:
            n_spec = -(-samples // 4096)
        leg.update({"numeric_lines": len(nums), "step_hz": step,
                    "samples_read": samples, "spectra_expected": n_spec,
                    "lines_per_spectrum": (len(nums) // n_spec) if n_spec else None})
        _sox_r94_arm(entry, leg, step == round(SOX_R94_RATE / 4096.0, 6),
                     f"`stat -freq` must print a 4 096-point spectrum "
                     f"(step {SOX_R94_RATE / 4096.0} Hz); got {step}")
        _sox_r94_arm(entry, leg,
                     n_spec is not None and len(nums) == 2048 * n_spec,
                     "`stat -freq` must print one 2 048-line spectrum per "
                     f"4 096-sample window (ceil(samples/4096) = {n_spec}); got "
                     f"{len(nums)} lines")

    # --- the one r93-adjacent row: SoX's own EBU R128 vs ffmpeg's ebur128 --
    e_short = text_leg("stat_e_short_mono", [SOX_R94, str(B), "-n", "stat", "-e"])
    f_short = fields_of(e_short["_text_full"])
    e_short["ebur"] = {k: v for k, v in f_short.items() if k.startswith("EBUR128")}
    _sox_r94_arm(entry, e_short, "EBUR128 Momentary" in f_short,
                 "`stat -e` must print a Momentary loudness on a 0.25 s mono file")
    _sox_r94_arm(entry, e_short, "EBUR128 Integrated" not in f_short,
                 "`stat -e` must NOT print Integrated on a 0.25 s file (the "
                 "length gate the scout found — SoX's own implementation, no "
                 "libebur128 linkage)")

    e_long = text_leg("stat_e_long_stereo", [SOX_R94, str(A), "-n", "stat", "-e"])
    f_long = fields_of(e_long["_text_full"])
    e_long["ebur"] = {k: v for k, v in f_long.items() if k.startswith("EBUR128")}
    _sox_r94_arm(entry, e_long, "EBUR128 Integrated" in f_long,
                 "`stat -e` must print Integrated once the file is long enough "
                 "(1 s stereo)")

    ff = _sox_r94_spawn([SOX_R94_FFMPEG, "-i", str(B), "-filter_complex",
                         "ebur128=peak=true", "-f", "null", "-"],
                        timeout=SOX_R94_WALL)
    ftext = ff.get("stderr_text") or ""
    m = re.search(r"I:\s*(-?[\d.]+)\s*LUFS", ftext)
    last = ""
    for ln in ftext.splitlines():
        if "LUFS" in ln:
            last = ln.strip()[-160:]
    L["ffmpeg_ebur128_short_mono"] = {
        "name": "ffmpeg_ebur128_short_mono", "rc": ff.get("exit_code"),
        "integrated_lufs": float(m.group(1)) if m else None,
        "integrated_line": last}
    _sox_r94_arm(entry, L["ffmpeg_ebur128_short_mono"],
                 m is not None and float(m.group(1)) <= -60.0,
                 "ffmpeg's ebur128 must GATE the same 0.25 s file to -70 LUFS "
                 "while SoX prints no Integrated at all — the two "
                 "implementations partition on the same input")
    return _sox_r94_exit(_sox_r94_drop_arrays(entry))


