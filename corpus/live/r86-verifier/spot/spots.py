#!/usr/bin/env python3
"""r86-verifier independent spots (verifier-owned code, no fixture import).

Own namespace r86v_<pid>; own null sink; every module unload index-verified
against its own sink_name= arg; no set-default-*; crash legs run with
RLIMIT_CORE=0. Prints one JSON receipt + a terse PASS/FAIL table.
"""
import json
import os
import re
import resource
import signal
import subprocess
import sys
import time

PID = os.getpid()
NS = f"r86v_ns_{PID}"
ROLE = f"r86vrole{PID}"
MODULE = None
OUT = {"pid": PID, "ns": NS, "spots": {}, "failures": []}


def run(argv, timeout=10, stdin=None, env=None):
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout,
                           stdin=stdin, env=env)
        return {"rc": p.returncode,
                "signal": (signal.Signals(-p.returncode).name
                           if p.returncode < 0 else None),
                "out": p.stdout.decode(errors="replace"),
                "err": p.stderr.decode(errors="replace")}
    except subprocess.TimeoutExpired as e:
        return {"rc": None, "signal": None, "timeout": True,
                "out": (e.stdout or b"").decode(errors="replace"),
                "err": (e.stderr or b"").decode(errors="replace")}


def nocore():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def load_ns():
    r = run(["pactl", "load-module", "module-null-sink",
             f"sink_name={NS}", f"sink_properties=device.description={NS}"])
    m = re.search(r"(\d+)", r["out"])
    if not m:
        raise SystemExit(f"null sink load failed: {r}")
    idx = int(m.group(1))
    # verify the module's own arg before we will ever unload it
    lst = run(["pactl", "list", "short", "modules"])
    line = next((ln for ln in lst["out"].splitlines()
                 if ln.startswith(str(idx))), "")
    if f"sink_name={NS}" not in line:
        raise SystemExit(f"index verify failed: {idx} {line}")
    time.sleep(0.6)
    return idx


def unload_ns(idx):
    lst = run(["pactl", "list", "short", "modules"])
    line = next((ln for ln in lst["out"].splitlines()
                 if ln.startswith(str(idx))), "")
    if f"sink_name={NS}" not in line:
        OUT["failures"].append(f"unload refused: index {idx} not ours: {line}")
        return
    run(["pactl", "unload-module", str(idx)])
    time.sleep(0.4)


def node_of(name):
    d = json.loads(run(["pw-dump"], 20)["out"] or "[]")
    for o in d:
        props = (o.get("info") or {}).get("props") or {}
        if props.get("node.name") == name:
            return o["id"], str(props.get("object.serial"))
    return None, None


def spot(name, ok, detail):
    OUT["spots"][name] = {"ok": bool(ok), "detail": detail}
    if not ok:
        OUT["failures"].append(f"{name}: {detail}")


def main():
    # ---------------- s0: load own sink ----------------
    global MODULE
    MODULE = load_ns()
    nid, ser = node_of(NS)
    spot("s0_own_sink_loaded", nid is not None and ser not in (None, "None"),
         f"id={nid} serial={ser}")

    # ---------------- s1: pw-cli serial/id namespace split ----------------
    ls_ser = run(["pw-cli", "ls", str(ser)])
    ls_id = run(["pw-cli", "ls", str(nid)])
    info_id = run(["pw-cli", "info", str(nid)])
    info_ser = run(["pw-cli", "info", str(ser)])
    spot("s1_ls_serial_resolves",
         ls_ser["rc"] == 0 and NS in ls_ser["out"] and f"id {nid}," in ls_ser["out"],
         f"rc={ls_ser['rc']} lines={len(ls_ser['out'].splitlines())}")
    spot("s1_ls_id_empty",
         ls_id["rc"] == 0 and ls_id["out"] == "",
         f"rc={ls_id['rc']} bytes={len(ls_id['out'])}")
    spot("s1_info_id_resolves",
         info_id["rc"] == 0 and f"id: {nid}" in info_id["out"], f"rc={info_id['rc']}")
    spot("s1_info_serial_unknown_global",
         info_ser["rc"] == 0 and "unknown global" in info_ser["err"],
         f"rc={info_ser['rc']} err={info_ser['err'].strip()[:60]!r}")

    # ---------------- s2: pw-dump surface ----------------
    d_id = run(["pw-dump", str(nid)], 20)
    d_ser = run(["pw-dump", str(ser)], 20)
    d_bad = run(["pw-dump", "99999"], 20)
    c_sep = run(["pw-dump", "-C", "never"], 20)
    c_join = run(["pw-dump", "-Cnever"], 20)
    spot("s2_dump_id_eq_serial",
         d_id["rc"] == 0 and d_id["out"] == d_ser["out"] and d_id["out"] != "",
         f"rc={d_id['rc']}/{d_ser['rc']} bytes={len(d_id['out'])}")
    spot("s2_dump_badid_silent_empty", d_bad["rc"] == 0 and d_bad["out"] == "",
         f"rc={d_bad['rc']} bytes={len(d_bad['out'])}")
    spot("s2_color_sep_positional_trap", c_sep["rc"] == 0 and c_sep["out"] == "",
         f"rc={c_sep['rc']} bytes={len(c_sep['out'])}")
    spot("s2_color_join_full_dump", c_join["rc"] == 0 and len(c_join["out"]) > 1000,
         f"rc={c_join['rc']} bytes={len(c_join['out'])}")

    # ---------------- s3: enum-params typed matrix on own node ----------------
    props = run(["pw-cli", "enum-params", str(nid), "Props"])
    propinfo = run(["pw-cli", "enum-params", str(nid), "PropInfo"])
    enumf = run(["pw-cli", "enum-params", str(nid), "EnumFormat"])
    lat = run(["pw-cli", "enum-params", str(nid), "Latency"])
    io_ = run(["pw-cli", "enum-params", str(nid), "IO"])
    bog = run(["pw-cli", "enum-params", str(nid), "Bogus"])
    spot("s3_props_pod", props["rc"] == 0 and "Object: size" in props["out"],
         f"rc={props['rc']} bytes={len(props['out'])}")
    spot("s3_propinfo_pod", propinfo["rc"] == 0 and "PropInfo" in propinfo["out"],
         f"bytes={len(propinfo['out'])}")
    spot("s3_enumformat_pod", enumf["rc"] == 0 and "Format" in enumf["out"],
         f"bytes={len(enumf['out'])}")
    spot("s3_latency_pod_absent", lat["rc"] == 0 and lat["out"] == "",
         f"rc={lat['rc']} bytes={len(lat['out'])} err={lat['err'].strip()[:40]!r}")
    spot("s3_io_remote_enoent",
         io_["rc"] == 0 and "res:-2" in io_["err"], f"err={io_['err'].strip()[:70]!r}")
    spot("s3_bogus_unknown_param_type",
         bog["rc"] == 0 and "unknown param type" in bog["err"],
         f"err={bog['err'].strip()[:60]!r}")

    # ---------------- s4: metadata store census ----------------
    md = run(["pw-metadata", "-l"])
    ls_md = run(["pw-cli", "ls", "Metadata"])
    dump = json.loads(run(["pw-dump"], 20)["out"] or "[]")
    md_rows = len(re.findall(r'Found "[^"]+" metadata \d+', md["out"]))
    ls_rows = len(re.findall(r"\bid \d+,\s*type PipeWire:Interface:Metadata/",
                             ls_md["out"]))
    dump_ids = {o["id"] for o in dump if str(o.get("type", "")).endswith("Metadata")}
    spot("s4_two_censuses_agree", md["rc"] == 0 and ls_md["rc"] == 0
         and md_rows == ls_rows and md_rows > 0, f"metadata-l={md_rows} ls={ls_rows}")
    spot("s4_dump_sees_strict_subset",
         bool(dump_ids) and dump_ids < set(range(0, 10 ** 6)) and len(dump_ids) < md_rows,
         f"dump_ids={sorted(dump_ids)} of {md_rows}")

    # ---------------- s5: pw-link lattice ----------------
    p1 = run(["pw-link", f"{NS}:monitor_FL", f"{NS}:playback_FL"])
    dup = run(["pw-link", f"{NS}:monitor_FL", f"{NS}:playback_FL"])
    usage = run(["pw-link"])
    bogp = run(["pw-link", f"{NS}:monitor_FL", "r86v_no_such:playback_FL"])
    lst = run(["pw-link", "-l"])
    lstI = run(["pw-link", "-l", "-I"])
    lid = None
    for ln in lstI["out"].splitlines():
        if "|->" in ln and NS in ln:
            m = re.match(r"\s*(\d+)\s+\|->", ln)
            if m:
                lid = int(m.group(1))
                break
    dele = run(["pw-link", "-d", str(lid)]) if lid is not None else {"rc": None}
    after = json.loads(run(["pw-dump"], 20)["out"] or "[]")
    own_after = [o for o in after if str(o.get("type", "")).endswith("Link")
                 and NS in json.dumps(o)]
    spot("s5_link_create_rc0", p1["rc"] == 0, f"rc={p1['rc']}")
    spot("s5_link_duplicate_rc255", dup["rc"] == 255 and "File exists" in dup["err"],
         f"rc={dup['rc']} err={dup['err'].strip()[:40]!r}")
    spot("s5_link_usage_rc255", usage["rc"] == 255, f"rc={usage['rc']}")
    spot("s5_link_bogus_port_rc255", bogp["rc"] == 255, f"rc={bogp['rc']}")
    spot("s5_link_list_shows_own", lst["rc"] == 0 and NS in lst["out"],
         f"lines={len(lst['out'].splitlines())}")
    spot("s5_link_unlink_by_id_removes",
         dele.get("rc") == 0 and own_after == [], f"rc={dele.get('rc')} after={len(own_after)}")

    # ---------------- s6: pw-jack env shim ----------------
    jp = run(["pw-jack", "-p", "512", "sh", "-c",
              "echo Q=${PIPEWIRE_QUANTUM-unset} D=${PIPEWIRE_DEBUG-unset}"])
    jvv = run(["pw-jack", "-v", "-v", "sh", "-c", "echo ${PIPEWIRE_DEBUG-unset}"])
    spot("s6_jack_p_quantum", jp["rc"] == 0 and jp["out"].strip() == "Q=512/48000 D=unset",
         f"out={jp['out'].strip()!r}")
    spot("s6_jack_vv_debug4", jvv["rc"] == 0 and jvv["out"].strip() == "4",
         f"out={jvv['out'].strip()!r}")

    # ---------------- s7: pw-cli </dev/null crash class ----------------
    try:
        p = subprocess.run(["pw-cli"], stdin=subprocess.DEVNULL,
                           capture_output=True, timeout=8, preexec_fn=nocore)
        rc, sig, err = p.returncode, (signal.Signals(-p.returncode).name
                                      if p.returncode < 0 else None), p.stderr.decode(errors="replace")
    except subprocess.TimeoutExpired:
        rc, sig, err = None, None, "timeout"
    spot("s7_pwcli_eof_sigabrt",
         rc == -6 and sig == "SIGABRT" and "remove_from_poll" in err,
         f"rc={rc} sig={sig} err={err.strip()[:60]!r}")
    spot("s7_no_core_left", not any(f.startswith("core") for f in os.listdir(".")),
         "cwd core scan")

    # ---------------- s8: set-param volume dead key ----------------
    vol_before = run(["pactl", "get-sink-volume", NS])
    wr = run(["pw-cli", "set-param", str(nid), "Props", "{ volume: 0.25 }"])
    en = run(["pw-cli", "enum-params", str(nid), "Props"])
    vol_after = run(["pactl", "get-sink-volume", NS])
    store = re.search(r"volume \(65539\)[\s\S]{0,120}?Float ([-\d.]+)", en["out"])
    spot("s8_volume_write_store_readback",
         wr["rc"] == 0 and store and float(store.group(1)) == 0.25,
         f"store={store.group(1) if store else None}")
    spot("s8_pactl_still_100",
         "100%" in vol_before["out"] and "100%" in vol_after["out"],
         f"before={vol_before['out'].splitlines()[0][:60]!r}")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    finally:
        if MODULE is not None:
            unload_ns(MODULE)
        time.sleep(0.3)
        OUT["residue_after"] = run(["pw-dump"], 20)["out"].count(NS) + \
            run(["pactl", "list", "short", "modules"])["out"].count(NS)
    print(json.dumps(OUT, indent=1))
    npass = sum(1 for s in OUT["spots"].values() if s["ok"])
    print(f"SPOTS: {npass}/{len(OUT['spots'])} PASS; failures={OUT['failures']}",
          file=sys.stderr)
    sys.exit(0 if not OUT["failures"] and OUT["residue_after"] == 0 else 1)
