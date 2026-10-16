#!/usr/bin/env python3
"""r87-critic absorption-gap proof.

Executes the COMMITTED midi + cli verdict blocks (sliced verbatim from
`git show d1e687b9:...`) over mutated leg dicts to prove/disprove
silent-skip and vacuity channels. A case that PASSES where the law is
unmeasured is an absorption finding.
"""
import json
import os
import re
import subprocess

ROOT = "/home/vgpnk/Projects/shokunin/audio-shokunin"
HERE = os.path.join(ROOT, "corpus/live/r87-critic")
COMMIT = "d1e687b9"
FIXTURE = "corpus/fixtures/measure_audio.py"
RUN = "20261016T070036115509Z-pwbind-r87"


def committed_text():
    return subprocess.run(["git", "show", f"{COMMIT}:{FIXTURE}"],
                          cwd=ROOT, capture_output=True, check=True).stdout.decode()


def fn_bounds(src, name):
    lines = src.split("\n")
    start = next(i for i, ln in enumerate(lines) if ln.startswith(f"def {name}("))
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("def "):
            end = j
            break
    return lines, start, end


def extract_fn(src, name):
    lines, s, e = fn_bounds(src, name)
    return "\n".join(lines[s:e]).rstrip() + "\n"


def extract_block(src, owner, start_marker, end_marker):
    lines, fs, fe = fn_bounds(src, owner)
    s = next(i for i in range(fs, fe) if start_marker in lines[i])
    e = next(i for i in range(s, fe) if end_marker in lines[i])
    return "\n".join(lines[s:e + 1])


def build(owner):
    src = committed_text()
    ns = {"json": json, "os": os, "re": re}
    for fn in ("_pwbind_r87_consumers", "_pwbind_r87_last_snap",
               "_pwbind_r87_parse_format"):
        exec(compile(extract_fn(src, fn), f"<{fn}>", "exec"), ns)
    blk = extract_block(src, owner,
                        "# ---------------- verdicts ----------------",
                        'entry["failures"] = failures')
    return ns, blk


def run_block(ns, blk, legs, entry, extra):
    env = dict(ns)
    env.update({"legs": legs, "entry": entry, "failures": []})
    env.update(extra)
    body = "def _arm():\n" + "\n".join(
        ("    " + l if l.strip() else l) for l in blk.split("\n")) + "\n"
    exec(compile(body, "<verdict-block>", "exec"), env)
    env["_arm"]()
    return env["failures"], env["entry"]


def main():
    d = json.load(open(os.path.join(ROOT, "corpus/live/runs", RUN,
                                    "measurements.json")))
    cli0 = d["measurements"]["pwbind_cli_r87_probe"]
    mid0 = d["measurements"]["pwbind_midi_r87_probe"]
    nid = cli0["legs"]["stream_leaf"]["node_id"]

    mid_ns, mid_blk = build("pwbind_midi_r87_entry")
    cli_ns, cli_blk = build("pwbind_cli_r87_entry")
    open(os.path.join(HERE, "armfrag-midi-verdict-block.py"), "w").write(mid_blk)
    open(os.path.join(HERE, "armfrag-cli-verdict-block.py"), "w").write(cli_blk)

    MID_CONST = {
        "PWBIND_R87_DEAD": "99999999", "PWBIND_R87_MIDI_BRIDGE": "Midi-Bridge",
        "PWBIND_R87_PREFIX": "r87a_x", "PWBIND_R87_BOGUS": "no_such_r87a",
        "PWBIND_R87_STALE_SERIAL": "98765432",
    }
    CLI_CONST = {
        "PWBIND_R87_DEAD": "99999999", "PWBIND_R87_AMP": 8192,
        "PWBIND_R87_SOLO_ENV": (0.85, 1.18),
        "PWBIND_R87_V25_ENV": (0.15, 0.35),
        "PWBIND_R87_MUTE_MAX": 128,
        "PWBIND_R87_V50_ENV": (0.40, 0.60),
        "PWBIND_R87_V150_ENV": (1.35, 1.65),
        "PWBIND_R87_V000_MAX": 200,
        "PWBIND_R87_PREFIX": "r87a_x",
        "PWBIND_R87_NS": "r87a_ns_x",
        "nid": nid,
    }

    def clone(o):
        return json.loads(json.dumps(o))

    out = []

    def case(block_ns, blk, legs0, entry0, extra, label, note):
        legs, entry = clone(legs0), clone(entry0)
        fl, en = run_block(block_ns, blk, legs, entry, extra)
        cb = en.get("coverage_blocked") or []
        out.append({"label": label, "note": note, "n_failures": len(fl),
                    "failures": fl[:3], "coverage_blocked": cb,
                    "verdict": "PASS" if not fl else "FAIL",
                    "silent": (not fl) and (not cb)})

    # ---------------- MIDI ----------------
    case(mid_ns, mid_blk, mid0["legs"], mid0,
         dict(MID_CONST),
         "MID-control committed receipt re-derivation",
         "baseline — must be green")

    def g_drop_all(lg, en):
        for n in ("m_t_bridge", "m_t_serial", "m_t_objid", "m_t_garbage",
                  "m_t_prop", "m_t_nt"):
            lg.pop(n, None)
    case(mid_ns, mid_blk, mid0["legs"], mid0, dict(MID_CONST),
         "MID-G1 all six dead-target legs ABSENT", "")  # placeholder

    lg, en = clone(mid0["legs"]), clone(mid0)
    g_drop_all(lg, en)
    fl, e2 = run_block(mid_ns, mid_blk, lg, en, dict(MID_CONST))
    out[-1] = {"label": "MID-G1 all six dead-target legs ABSENT",
               "note": "the verdict loop does `if l is None: continue` — "
                       "is the dead-target census silently unmeasured?",
               "n_failures": len(fl), "failures": fl[:3],
               "coverage_blocked": e2.get("coverage_blocked") or [],
               "verdict": "PASS" if not fl else "FAIL",
               "silent": (not fl) and not (e2.get("coverage_blocked") or [])}

    lg, en = clone(mid0["legs"]), clone(mid0)
    lg.pop("m_t_serial", None)
    lg.pop("m_t_objid", None)
    fl, e2 = run_block(mid_ns, mid_blk, lg, en, dict(MID_CONST))
    out.append({"label": "MID-G2 only m_t_serial+m_t_objid ABSENT "
                         "(the `if bridge:` branch)",
                "note": "the serial/object.id dead-target claim is the "
                        "one the task names — is it measured when "
                        "Midi-Bridge is absent?",
                "n_failures": len(fl), "failures": fl[:3],
                "coverage_blocked": e2.get("coverage_blocked") or [],
                "verdict": "PASS" if not fl else "FAIL",
                "silent": (not fl) and not (e2.get("coverage_blocked") or [])})

    lg, en = clone(mid0["legs"]), clone(mid0)
    lg["mdump_live"] = {"attempts": []}
    fl, e2 = run_block(mid_ns, mid_blk, lg, en, dict(MID_CONST))
    out.append({"label": "MID-G3 mdump_live attempts == []",
                "note": "empty attempts list — the boundary's startup-flake "
                        "arm requires `live and not noted`",
                "n_failures": len(fl), "failures": fl[:3],
                "coverage_blocked": e2.get("coverage_blocked") or [],
                "verdict": "PASS" if not fl else "FAIL",
                "silent": (not fl) and not (e2.get("coverage_blocked") or [])})

    # controls: the arms are live
    lg, en = clone(mid0["legs"]), clone(mid0)
    lg["m_t_bridge"]["exit_code"] = 0
    fl, e2 = run_block(mid_ns, mid_blk, lg, en, dict(MID_CONST))
    out.append({"label": "MID-C1 m_t_bridge rc=0 (CONTROL: arm is live)",
                "note": "must FAIL", "n_failures": len(fl),
                "failures": fl[:2], "coverage_blocked": e2.get("coverage_blocked") or [],
                "verdict": "PASS" if not fl else "FAIL", "silent": False})

    lg, en = clone(mid0["legs"]), clone(mid0)
    lg["mdump_live"] = {"attempts": [{"attempt": 0, "node": True,
                                      "in_ports": ["input"],
                                      "pwlink_rc": 0, "stdout": "no notes"}]}
    fl, e2 = run_block(mid_ns, mid_blk, lg, en, dict(MID_CONST))
    out.append({"label": "MID-C2 mdump_live published but no Note On "
                         "(CONTROL)",
                "note": "must FAIL", "n_failures": len(fl),
                "failures": fl[:2], "coverage_blocked": e2.get("coverage_blocked") or [],
                "verdict": "PASS" if not fl else "FAIL", "silent": False})

    lg, en = clone(mid0["legs"]), clone(mid0)
    lg["pin"] = {"bridge": None, "seq_port": None}
    fl, e2 = run_block(mid_ns, mid_blk, lg, en, dict(MID_CONST))
    out.append({"label": "MID-C3 pin.file absent (CONTROL: coverage_blocked "
                         "is recorded)",
                "note": "must record coverage_blocked, not pass silently",
                "n_failures": len(fl), "failures": fl[:2],
                "coverage_blocked": e2.get("coverage_blocked") or [],
                "verdict": "PASS" if not fl else "FAIL", "silent": False})

    # ---------------- CLI ----------------
    def cli_case(label, fn, note):
        lg, en = clone(cli0["legs"]), clone(cli0)
        fn(lg, en)
        fl, e2 = run_block(cli_ns, cli_blk, lg, en, dict(CLI_CONST))
        out.append({"label": label, "note": note, "n_failures": len(fl),
                    "failures": fl[:3],
                    "coverage_blocked": e2.get("coverage_blocked") or [],
                    "verdict": "PASS" if not fl else "FAIL",
                    "silent": (not fl) and not (e2.get("coverage_blocked") or [])})

    cli_case("CLI-control committed receipt re-derivation", lambda l, e: None,
             "baseline — must be green")

    def c_volnone(l, e):
        l["foreign"]["volume_read"] = None
    cli_case("CLI-G1 foreign.volume_read is None",
             c_volnone,
             "the identical-value-write arm is guarded by "
             "`if volume_read is not None` — vacuous, no coverage_blocked?")

    def c_volmove(l, e):
        l["foreign"]["volume_read"] = 1.0
        l["foreign"]["volume_after"] = 0.5
    cli_case("CLI-C1 foreign identical-value write moved the volume (CONTROL)",
             c_volmove, "must FAIL")

    def c_propunk(l, e):
        l.pop("props_unk", None)
    cli_case("CLI-G2 props_unk absent", c_propunk,
             "arm guarded by `if legs.get('props_unk') is not None` — "
             "vacuous?")

    def c_vol25_lo(l, e):
        l["regions"]["vol25"]["median_peak"] = 0.16 * 8192
    cli_case("CLI-G3 vol25 ratio = 0.16 (a 6.25x-lower multiplier)",
             c_vol25_lo,
             "the V25 envelope (0.15,0.35) is 2.3x wide around the claimed "
             "exact 0.25 — what else passes?")

    def c_vol25_hi(l, e):
        l["regions"]["vol25"]["median_peak"] = 0.34 * 8192
    cli_case("CLI-G4 vol25 ratio = 0.34", c_vol25_hi,
             "upper edge of the same envelope")

    def c_vol25_noop(l, e):
        l["regions"]["vol25"]["median_peak"] = 8192.0
    cli_case("CLI-C2 vol25 ratio = 1.0 (CONTROL: no-op write)",
             c_vol25_noop, "must FAIL")

    def c_mute_lo(l, e):
        l["regions"]["mute"]["median_peak"] = 64.0
    cli_case("CLI-G5 mute median_peak = 64 (0.8% of solo, not 0)",
             c_mute_lo, "MUTE_MAX=128 admits non-zero residue")

    def c_fmtmove(l, e):
        t = l["fmt_stream"]["post_valid"]["stdout"]
        l["fmt_stream"]["post_valid"]["stdout"] = re.sub(
            r"(Format:Audio:rate \(65539\).*?)Int \d+", r"\g<1>Int 96000",
            t, count=1, flags=re.S)
    cli_case("CLI-C3 fmt_stream negotiated Format moved 48000->96000 "
             "(CONTROL)",
             c_fmtmove, "must FAIL")

    def c_fmtunparsed(l, e):
        t = l["fmt_stream"]["pre"]["stdout"]
        l["fmt_stream"]["pre"]["stdout"] = re.sub(
            r"Format:Audio:rate \(65539\)", "Format:Audio:rateX", t,
            count=1)
    cli_case("CLI-C4 fmt_stream pre-rate unparseable (CONTROL)",
             c_fmtunparsed, "must FAIL (pre.rate is None)")

    def c_sendcmd(l, e):
        l["sendcmd"]["Resume"]["cmd"]["stderr"] = "accepted"
    cli_case("CLI-C5 sendcmd/Resume accepted (CONTROL)", c_sendcmd,
             "must FAIL")

    def c_linger(l, e):
        l["create_linger"]["present_after_destroy"] = True
    cli_case("CLI-C6 linger survived destroy (CONTROL)", c_linger,
             "must FAIL")

    json.dump(out, open(os.path.join(HERE, "arm-replay-gaps.json"), "w"),
              indent=1, sort_keys=True)
    lines = []
    for r in out:
        lines.append(f"{r['verdict']:4s} nf={r['n_failures']:<2} "
                     f"silent={r['silent']!s:5s} cb={r['coverage_blocked']!r:60s} "
                     f"{r['label']}")
        lines.append(f"        note: {r['note']}")
        for x in r["failures"][:2]:
            lines.append(f"        - {x}")
    txt = "\n".join(lines) + "\n"
    open(os.path.join(HERE, "arm-replay-gaps.out"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
