#!/usr/bin/env python3
"""r90 scout harness — wpctl / SPA registry / control-plane remainder /
network-module lattice / EnumFormat renegotiation / pw-link semantics.
Every leg: fresh subprocess, argv+timeout+reps, raw capture, receipt line.
Writes only under corpus/live/r90-scout/. Cleanup by id only."""
import json, os, re, signal, subprocess, sys, time, hashlib
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "raw"; RCPTS = BASE / "receipts"; RUNS = BASE / "runs"
for d in (RAW, RCPTS, RUNS): d.mkdir(exist_ok=True)
RECEIPT = RCPTS / "r90-legs.jsonl"
RECEIPT.write_text("")  # fresh per harness run-id

RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
records = []

def nowz():
    return time.strftime("%H:%M:%S", time.gmtime()) + f".{int(time.time_ns()/1e6)%1000:03d}Z"

def run(name, argv, rep, timeout=8, env=None, stdin=None, term_after=None):
    """Run argv; capture. term_after: seconds, then SIGTERM then wait up to 3s then SIGKILL."""
    t0 = time.time()
    rec = {"leg": name, "rep": rep, "argv": argv, "t0": nowz()}
    try:
        if term_after is None:
            p = subprocess.run(argv, capture_output=True, timeout=timeout,
                               env={**os.environ, **(env or {})}, text=True,
                               input=stdin)
            rec.update(rc=p.returncode, out=p.stdout, err=p.stderr,
                       wall_ms=int((time.time()-t0)*1000), how="exit")
        else:
            p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 env={**os.environ, **(env or {})}, text=True,
                                 start_new_session=True, stdin=subprocess.DEVNULL)
            try:
                out, err = p.communicate(timeout=term_after)
                rec.update(rc=p.returncode, out=out, err=err, how="exit")
            except subprocess.TimeoutExpired:
                p.send_signal(signal.SIGTERM)
                try:
                    out, err = p.communicate(timeout=3)
                    rec.update(rc=p.returncode, out=out, err=err, how="sigterm")
                except subprocess.TimeoutExpired:
                    p.kill(); out, err = p.communicate()
                    rec.update(rc=p.returncode, out=out, err=err, how="sigkill")
            rec["wall_ms"] = int((time.time()-t0)*1000)
    except subprocess.TimeoutExpired as e:
        rec.update(rc=None, out=e.stdout or "", err=(e.stderr or "")+" [HARNESS TIMEOUT]",
                   wall_ms=int((time.time()-t0)*1000), how="timeout")
    except FileNotFoundError as e:
        rec.update(rc=None, out="", err=str(e), wall_ms=0, how="spawn-fail")
    fn = f"{name}.{rep}"
    (RAW / f"{fn}.out").write_text(rec["out"] or "")
    (RAW / f"{fn}.err").write_text(rec["err"] or "")
    slim = {k: rec[k] for k in ("leg","rep","argv","t0","rc","wall_ms","how")}
    slim["out_sha"] = hashlib.sha256((rec["out"] or "").encode()).hexdigest()[:16]
    slim["err_sha"] = hashlib.sha256((rec["err"] or "").encode()).hexdigest()[:16]
    slim["out_len"] = len(rec["out"] or ""); slim["err_len"] = len(rec["err"] or "")
    records.append(slim)
    with RECEIPT.open("a") as f: f.write(json.dumps(slim)+"\n")
    return rec

def leg(name, argv, reps=3, **kw):
    return [run(name, argv, i+1, **kw) for i in range(reps)]

def pw_dump():
    p = subprocess.run(["pw-dump"], capture_output=True, text=True, timeout=10)
    return json.loads(p.stdout)

def find_ids(pred):
    return [o["id"] for o in pw_dump() if pred(o)]

def node_ids(namefrag):
    return find_ids(lambda o: o.get("type","").endswith("Node")
                    and namefrag in (o.get("info",{}).get("props",{}) or {}).get("node.name",""))

def obj_serials():
    out={}
    for o in pw_dump():
        p=(o.get("info",{}) or {}).get("props",{}) or {}
        out[o["id"]]=p.get("object.serial")
    return out

def census_r90():
    d = pw_dump()
    hits=[]
    for o in d:
        blob = json.dumps(o)
        if "r90" in blob: hits.append((o["id"], o.get("type","").split(":")[-1]))
    return hits, len(d)

def pactl_modules():
    p = subprocess.run(["pactl","list","short","modules"], capture_output=True, text=True)
    return p.stdout.strip()

# ============ S0: baseline census ============
def s0():
    leg("s0-uname", ["uname","-srvmo"], reps=1)
    leg("s0-date", ["date","-u","+%Y-%m-%dT%H:%M:%SZ"], reps=1)
    leg("s0-pkg", ["bash","-c","pacman -Q pipewire pipewire-audio pipewire-pulse wireplumber libpulse alsa-utils 2>&1"], reps=1)
    leg("s0-pactl-info", ["pactl","info"], reps=3)
    leg("s0-pactl-modules", ["pactl","list","short","modules"], reps=3)
    leg("s0-wpctl-status", ["wpctl","status"], reps=3)
    leg("s0-pw-dump-census", ["bash","-c","pw-dump | python3 -c 'import json,sys,collections;d=json.load(sys.stdin);print(len(d));print(collections.Counter(o[\"type\"].split(\":\")[-1] for o in d))'"], reps=3)
    leg("s0-git-head", ["git","-C",str(BASE.parent.parent),"rev-parse","--short","HEAD"], reps=1)
    leg("s0-git-status", ["git","-C",str(BASE.parent.parent),"status","--short"], reps=1)
    Path(RUNS/"s0-modset.txt").write_text(pactl_modules())

# ============ S1: wpctl lattice ============
def s1():
    own = node_ids("r90")
    leg("wp-status", ["wpctl","status"])
    for a in (["list"],["list","audio"],["list","audio","sinks"],["list","audio","sources"],
              ["list","audio","devices"],["list","video"],["list","bogus"],["list","audio","bogus"],
              ["list","audio","streams"],["list","audio","filters"]):
        leg("wp-list-"+"-".join(a[1:]) if len(a)>1 else "wp-list", ["wpctl"]+a)
    # id space: object.id vs object.serial. node 46 serial measured at runtime.
    sers = obj_serials()
    n46ser = sers.get(46)
    leg("wp-inspect-id46", ["wpctl","inspect","46"])
    if n46ser and n46ser != 46:
        leg("wp-inspect-serial46", ["wpctl","inspect",str(n46ser)])   # serial space?
    # a live port id + client id + bogus
    d = pw_dump()
    port = next((o["id"] for o in d if o["type"].endswith("Port")), None)
    if port: leg("wp-inspect-portid", ["wpctl","inspect",str(port)])
    leg("wp-inspect-client33", ["wpctl","inspect","33"])
    leg("wp-inspect-bogus", ["wpctl","inspect","999999"])
    leg("wp-inspect-name", ["wpctl","inspect","alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"])
    leg("wp-inspect-noarg", ["wpctl","inspect"])
    leg("wp-inspect-neg", ["wpctl","inspect","-1"])
    leg("wp-getvol-46", ["wpctl","get-volume","46"])
    leg("wp-getvol-bogus", ["wpctl","get-volume","999999"])
    leg("wp-getvol-noarg", ["wpctl","get-volume"])
    leg("wp-getvol-node35", ["wpctl","get-volume","35"])   # midi bridge node — not audio sink
    leg("wp-setvol-bogusid", ["wpctl","set-volume","999999","0.5"])
    leg("wp-setvol-badval", ["wpctl","set-volume","46","abc"], reps=1)
    leg("wp-setmute-bogus", ["wpctl","set-mute","999999","1"])
    leg("wp-setprofile-bogus", ["wpctl","set-profile","999999","0"])
    leg("wp-setprofile-noarg", ["wpctl","set-profile"])
    leg("wp-setroute-bogus", ["wpctl","set-route","999999","0"])
    leg("wp-cleardefault-bogus", ["wpctl","clear-default","999999"], reps=1)
    leg("wp-setloglevel-bad", ["wpctl","set-log-level","999999","X"], reps=1)
    leg("wp-setloglevel-noarg", ["wpctl","set-log-level"], reps=1)
    leg("wp-reset-bogus", ["wpctl","reset","999999"], reps=1)
    leg("wp-bogus-cmd", ["wpctl","boguscommand"], reps=1)
    leg("wp-noargs", ["wpctl"], reps=1)

def s1_mutate():
    """Own null sink lifecycle for wpctl mutation legs. Caller guarantees cleanup."""
    out={}
    p = subprocess.run(["pactl","load-module","module-null-sink",
                        "sink_name=r90_ns","sink_properties=device.description=r90_ns",
                        "rate=48000","channels=2"], capture_output=True, text=True)
    out["ns_module_idx"]=p.stdout.strip()
    time.sleep(0.7)
    d = pw_dump()
    nsid = next((o["id"] for o in d if o["type"].endswith("Node")
                 and (o.get("info",{}).get("props",{}) or {}).get("node.name")=="r90_ns"), None)
    out["ns_id"]=nsid
    if nsid is None:
        out["error"]="null sink did not appear"; return out
    leg("wp-inspect-ownns", ["wpctl","inspect",str(nsid)])
    leg("wp-getvol-ownns", ["wpctl","get-volume",str(nsid)])
    # set-volume ladder on own sink — verify via get-volume
    for v in ("0.50","25%","+10%","150%","-5%","0"):
        leg(f"wp-setvol-{v.replace('%','pct').replace('+','p').replace('-','m')}",
            ["wpctl","set-volume",str(nsid),v])
        leg("wp-getvol-after", ["wpctl","get-volume",str(nsid)], reps=1)
    for m in ("1","toggle","toggle","0","bogus"):
        leg(f"wp-setmute-{m}", ["wpctl","set-mute",str(nsid),m], reps=1)
        leg("wp-inspect-mute", ["bash","-c",f"wpctl inspect {nsid} | grep -iE 'mute|vol'"], reps=1)
    # default-object steering: set-default own → verify → restore SPDIF
    leg("wp-setdefault-own", ["wpctl","set-default",str(nsid)], reps=1)
    leg("wp-pactl-defsink-after", ["pactl","get-default-sink"], reps=1)
    leg("wp-status-marker", ["bash","-c","wpctl status | sed -n '/Sinks:/,/Sources:/p'"], reps=1)
    # restore default to SPDIF node id 46 (was default at entry)
    leg("wp-setdefault-restore", ["wpctl","set-default","46"], reps=1)
    leg("wp-pactl-defsink-restored", ["pactl","get-default-sink"], reps=1)
    leg("wp-cleardefault-own", ["wpctl","clear-default",str(nsid)], reps=1)
    leg("wp-defsink-postclear", ["pactl","get-default-sink"], reps=1)
    # settings surface: read lattice + own-key write/read/save/delete
    leg("wp-settings-all", ["wpctl","settings"])
    leg("wp-settings-boguskey", ["wpctl","settings","r90scout.probe"])
    leg("wp-settings-realkey", ["wpctl","settings","node.stream.restore-props"])
    leg("wp-settings-write", ["wpctl","settings","r90scout.probe","1"], reps=1)
    leg("wp-settings-readback", ["wpctl","settings","r90scout.probe"], reps=1)
    leg("wp-settings-save", ["wpctl","settings","-s","r90scout.probe"], reps=1)
    leg("wp-settings-savedval", ["wpctl","settings","r90scout.probe","saved"], reps=1)
    leg("wp-settings-delete", ["wpctl","settings","-d","r90scout.probe"], reps=1)
    leg("wp-settings-final", ["wpctl","settings","r90scout.probe"], reps=1)
    leg("wp-settings-all-final", ["wpctl","settings"], reps=1)
    # set-profile on a real device at its CURRENT index? -> measured refusal only; skip mutations
    # unload own sink by index
    idx = out["ns_module_idx"]
    if idx and idx.isdigit():
        subprocess.run(["pactl","unload-module",idx], capture_output=True)
        time.sleep(0.5)
    out["post"]=census_r90()
    Path(RUNS/"s1-mutate-ctx.json").write_text(json.dumps(out,indent=1))
    return out

# ============ S2: SPA registry ============
def s2():
    import glob
    sos = sorted(glob.glob("/usr/lib/spa-0.2/*/*.so") + glob.glob("/usr/lib/spa-0.2/*.so"))
    inv=[]
    for so in sos:
        short = so.replace("/usr/lib/spa-0.2/","spa:")
        r = run("spa-inspect-"+re.sub(r'[^A-Za-z0-9]+','_',short), ["spa-inspect", so], 1, timeout=15)
        facts=[]
        for line in r["out"].splitlines():
            line=line.strip()
            if line.startswith(("factory name:","interface:")):
                facts.append(line)
        inv.append({"so":short,"rc":r["rc"],"factories":[f for f in facts if f.startswith("factory name")],
                    "ifaces":[f for f in facts if f.startswith("interface")],
                    "errs":[l for l in r["err"].splitlines() if l.strip()][:6],
                    "notes":[l for l in r["out"].splitlines() if "skipping" in l or "can't" in l][:6]})
    Path(RUNS/"s2-spa-inventory.json").write_text(json.dumps(inv,indent=1))
    # stability: 3 reps on two representative plugins
    leg("spa-inspect-support-r3", ["spa-inspect","/usr/lib/spa-0.2/support/libspa-support.so"], reps=2)
    leg("spa-inspect-audioconv-r3", ["spa-inspect","/usr/lib/spa-0.2/audioconvert/libspa-audioconvert.so"], reps=2)
    # refusal classes
    leg("spa-inspect-noarg", ["spa-inspect"])
    leg("spa-inspect-missing", ["spa-inspect","/usr/lib/spa-0.2/nonexistent/libspa-nope.so"])
    leg("spa-inspect-libspa", ["spa-inspect","/usr/lib/spa-0.2/libspa.so"])
    leg("spa-inspect-libz", ["spa-inspect","/usr/lib/libz.so.1"])
    leg("spa-inspect-dir", ["spa-inspect","/usr/lib/spa-0.2/support/"])
    leg("spa-inspect-text", ["spa-inspect","/etc/hostname"])
    leg("spa-inspect-twoargs", ["spa-inspect","/usr/lib/spa-0.2/support/libspa-support.so","/usr/lib/spa-0.2/audioconvert/libspa-audioconvert.so"], reps=1)
    # spa-json-dump
    Path(RUNS/"fixture.json").write_text('{\n  "a": 1, "b": [true, "x"], "c": { "k": null }\n}\n')
    leg("spajson-fixture", ["spa-json-dump",str(RUNS/"fixture.json")])
    leg("spajson-spa", ["spa-json-dump","-s",str(RUNS/"fixture.json")])
    leg("spajson-indent0", ["spa-json-dump","-i","0",str(RUNS/"fixture.json")], reps=1)
    leg("spajson-pwconf", ["spa-json-dump","/usr/share/pipewire/pipewire.conf"], reps=1)
    leg("spajson-invalid", ["spa-json-dump","/etc/hostname"])
    leg("spajson-missing", ["spa-json-dump","/nonexistent.json"])
    leg("spajson-stdin-dash", ["spa-json-dump","-"], reps=1, stdin='{"x":2}')
    # spa-monitor (loads a monitor plugin .so)
    for so in ("/usr/lib/spa-0.2/alsa/libspa-alsa.so",
               "/usr/lib/spa-0.2/v4l2/libspa-v4l2.so",
               "/usr/lib/spa-0.2/bluez5/libspa-bluez5.so",
               "/usr/lib/spa-0.2/support/libspa-support.so",
               "/usr/lib/spa-0.2/audiotestsrc/libspa-audiotestsrc.so"):
        tag = re.sub(r'[^A-Za-z0-9]+','_',so.split("spa-0.2/")[-1])
        leg(f"spa-monitor-{tag}", ["spa-monitor",so], reps=1, term_after=2.5, timeout=6)
    leg("spa-monitor-missing", ["spa-monitor","/usr/lib/spa-0.2/nope.so"], reps=1)
    leg("spa-monitor-noarg", ["spa-monitor"], reps=1)
    # spa-acp-tool read-only on the three cards
    for c in ("0","1","2","99"):
        leg(f"acp-card{c}-info", ["spa-acp-tool","-c",c,"info"], reps=1, timeout=15)
    leg("acp-card0-listprofs", ["spa-acp-tool","-c","0","list-profiles"], reps=1, timeout=15)
    leg("acp-card1-listprofs", ["spa-acp-tool","-c","1","list-profiles"], reps=1, timeout=15)
    leg("acp-card2-listprofs", ["spa-acp-tool","-c","2","list-profiles"], reps=1, timeout=15)
    leg("acp-card0-ports", ["spa-acp-tool","-c","0","list-ports"], reps=1, timeout=15)
    leg("acp-card0-devs", ["spa-acp-tool","-c","0","list-devices"], reps=1, timeout=15)
    leg("acp-noarg", ["spa-acp-tool"], reps=1, term_after=2.0, timeout=5)
    leg("acp-badcmd", ["spa-acp-tool","-c","0","bogus"], reps=1, term_after=2.0, timeout=5)

# ============ S3: control-plane remainder ============
def s3():
    # pw-dump -m : monitor mode shape — run 3s while a module loads+unloads
    for rep in (1,2,3):
        p = subprocess.Popen(["pw-dump","-m"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, start_new_session=True)
        time.sleep(0.6)
        li = subprocess.run(["pactl","load-module","module-null-sink",
                             f"sink_name=r90mon_{rep}"], capture_output=True, text=True)
        time.sleep(1.2)
        if li.stdout.strip().isdigit():
            subprocess.run(["pactl","unload-module",li.stdout.strip()], capture_output=True)
        time.sleep(0.8)
        p.send_signal(signal.SIGTERM)
        try: out,err=p.communicate(timeout=3); how="sigterm"
        except subprocess.TimeoutExpired:
            p.kill(); out,err=p.communicate(); how="sigkill"
        rec={"leg":"pwdump-monitor","rep":rep,"argv":["pw-dump","-m"],"t0":nowz(),
             "rc":p.returncode,"wall_ms":None,"how":how,
             "out":out,"err":err}
        (RAW/f"pwdump-monitor.{rep}.out").write_text(out); (RAW/f"pwdump-monitor.{rep}.err").write_text(err)
        slim={k:rec[k] for k in ("leg","rep","argv","t0","rc","how")}
        slim["out_sha"]=hashlib.sha256(out.encode()).hexdigest()[:16]
        slim["out_len"]=len(out); slim["err_len"]=len(err); records.append(slim)
        RECEIPT.open("a").write(json.dumps(slim)+"\n")
        time.sleep(0.4)
    # pw-dot variants
    leg("pwdot-default", ["pw-dot","-o",str(RAW/"pwdot-default.dot")])
    leg("pwdot-all", ["pw-dot","-a","-o",str(RAW/"pwdot-all.dot")], reps=1)
    leg("pwdot-smart", ["pw-dot","-s","-o",str(RAW/"pwdot-smart.dot")], reps=1)
    leg("pwdot-detail", ["pw-dot","-d","-o",str(RAW/"pwdot-detail.dot")], reps=1)
    leg("pwdot-lr", ["pw-dot","-L","-o",str(RAW/"pwdot-lr.dot")], reps=1)
    leg("pwdot-90", ["pw-dot","-9","-o",str(RAW/"pwdot-90.dot")], reps=1)
    # -j offline render from a pw-dump file
    dj = subprocess.run(["pw-dump"], capture_output=True, text=True)
    (RUNS/"dump-for-dot.json").write_text(dj.stdout)
    leg("pwdot-json", ["pw-dot","-j",str(RUNS/"dump-for-dot.json"),"-o",str(RAW/"pwdot-json.dot")], reps=1)
    leg("pwdot-json-bogus", ["pw-dot","-j","/etc/hostname","-o",str(RAW/"pwdot-bogus.dot")], reps=1)
    leg("pwdot-badremote", ["pw-dot","-r","r90_no_such"], reps=1)
    # pw-profiler
    leg("pwprof-n3", ["pw-profiler","-n","3","-o",str(RAW/"profiler.log")], reps=1, timeout=20)
    leg("pwprof-json", ["pw-profiler","-J","-n","2"], reps=1, timeout=20)
    leg("pwprof-n0", ["pw-profiler","-n","0","-o",str(RAW/"profiler0.log")], reps=1, timeout=10)
    leg("pwprof-badremote", ["pw-profiler","-r","r90_no_such","-n","1"], reps=1, timeout=10)
    # pw-config
    leg("pwconfig-paths", ["pw-config","paths"])
    leg("pwconfig-list", ["pw-config","list"])
    leg("pwconfig-list-ctx", ["pw-config","list","context.properties"], reps=1)
    leg("pwconfig-list-bogus", ["pw-config","list","bogus.section"])
    leg("pwconfig-merge", ["pw-config","merge","context.properties"], reps=1)
    leg("pwconfig-pulse", ["pw-config","-n","pipewire-pulse.conf","list"], reps=1)
    leg("pwconfig-badname", ["pw-config","-n","r90_nope.conf","list"], reps=1)
    leg("pwconfig-badcmd", ["pw-config","bogus"], reps=1)
    # pw-mon
    leg("pwmon-2s", ["pw-mon"], reps=2, term_after=2.0, timeout=8)
    leg("pwmon-hideprops", ["pw-mon","-o","-a","-p"], reps=1, term_after=2.0, timeout=8)
    leg("pwmon-badremote", ["pw-mon","-r","r90_no_such"], reps=1, term_after=2.0, timeout=8)
    # pw-container
    leg("pwcontainer-true", ["pw-container","/bin/true"], reps=1, timeout=10)
    leg("pwcontainer-pwdump", ["pw-container","pw-dump"], reps=1, timeout=15)
    leg("pwcontainer-pactlinfo", ["pw-container","pactl","info"], reps=1, timeout=15)
    leg("pwcontainer-bogus", ["pw-container","r90_no_such_app"], reps=1, timeout=10)
    leg("pwcontainer-noarg", ["pw-container"], reps=1, term_after=2.0, timeout=8)
    # pw-reserve — monitor-only on real names; acquire only on a fake name
    leg("pwreserve-mon-audio0", ["pw-reserve","-m","-n","Audio0"], reps=1, term_after=2.0, timeout=8)
    leg("pwreserve-fake-acquire", ["pw-reserve","-n","r90fake"], reps=1, term_after=2.5, timeout=8)
    leg("pwreserve-mon-video9", ["pw-reserve","-m","-n","Video9"], reps=1, term_after=2.0, timeout=8)
    leg("pwreserve-release-fake", ["pw-reserve","-r","-n","r90fake"], reps=1, term_after=2.0, timeout=8)
    # wpexec — trivial script only; never session objects
    (RUNS/"wpexec-hello.lua").write_text('print("r90_wpexec_alive")\nos.exit(0)\n')
    leg("wpexec-hello", ["wpexec",str(RUNS/"wpexec-hello.lua")], reps=1, timeout=8)
    leg("wpexec-missing", ["wpexec","/nonexistent.lua"], reps=1, timeout=8)
    leg("wpexec-noarg", ["wpexec"], reps=1, term_after=2.0, timeout=8)

# ============ S4: network/tunnel module lattice ============
def s4():
    # pulse namespace refusals (×3)
    for mod,args in [("module-tunnel-sink","server=127.0.0.1:1 sink_name=r90_tun"),
                     ("module-tunnel-source","server=127.0.0.1:1 source_name=r90_tuns"),
                     ("module-tunnel-sink-new","server=127.0.0.1:1"),
                     ("module-tunnel","server=127.0.0.1:1"),
                     ("module-rtp-send","destination_ip=127.0.0.1 port=14713"),
                     ("module-rtp-recv","sap_address=127.0.0.1"),
                     ("module-netjack2-sink","remote=127.0.0.1:1"),
                     ("module-vban-send","destination_ip=127.0.0.1"),
                     ("module-zeroconf-publish","")]:
        leg(f"plm-{mod}", ["bash","-c",f"pactl load-module {mod} {args}"], reps=3)
    # a pulse module that may actually LOAD: native-protocol-tcp on loopback+high port
    before = pactl_modules()
    r = leg("plm-native-tcp", ["pactl","load-module","module-native-protocol-tcp",
                               "port=14713","listen=127.0.0.1","auth-anonymous=1"], reps=1)
    if r[0]["out"].strip().isdigit():
        leg("plm-native-tcp-verify", ["pactl","list","short","modules"], reps=1)
        subprocess.run(["pactl","unload-module",r[0]["out"].strip()], capture_output=True)
    Path(RUNS/"s4-modset-after-tcp.txt").write_text(pactl_modules())
    # native load-module lattice via pw-cli (loads INTO the running daemon)
    for lib,args in [("libpipewire-module-pulse-tunnel","{ server = \"127.0.0.1:1\" }"),
                     ("libpipewire-module-pipe-tunnel","{ remote.socket = \"/tmp/r90_nope.sock\" }"),
                     ("libpipewire-module-rtp-sink","{ destination.ip = \"127.0.0.1\" destination.port = 14713 }"),
                     ("libpipewire-module-rtp-source","{ local.ip = \"127.0.0.1\" }"),
                     ("libpipewire-module-vban-send","{ destination.ip = \"127.0.0.1\" }"),
                     ("libpipewire-module-vban-recv","{ source.ip = \"127.0.0.1\" }"),
                     ("libpipewire-module-netjack2-driver","{ net.ip = \"127.0.0.1\" net.port = 1 }"),
                     ("libpipewire-module-netjack2-manager","{ net.ip = \"127.0.0.1\" net.port = 14713 }"),
                     ("libpipewire-module-pulse-tunnel","{ server = \"bogus.invalid\" }")]:
        tag = lib.replace("libpipewire-module-","")
        # load via a live pw-cli session: load-module then sleep then destroy handled post-hoc
        pre = set(o["id"] for o in pw_dump())
        rc = run(f"nat-{tag}", ["pw-cli","load-module",lib,args], 1, timeout=10)
        time.sleep(1.6)   # let async connect failures fire
        dpost = pw_dump()
        new = [o for o in dpost if o["id"] not in pre]
        (RUNS/f"s4-newobjs-{tag}.json").write_text(json.dumps(new,indent=1))
        leg(f"nat-{tag}-census", ["bash","-c","pw-dump | python3 -c 'import json,sys;d=json.load(sys.stdin);print(len(d))'"], reps=1)
        # cleanup by id: destroy every new object that persists (module last)
        news = sorted((o["id"] for o in new), reverse=True)
        for oid in news:
            subprocess.run(["pw-cli","destroy",str(oid)], capture_output=True, timeout=5)
        time.sleep(0.4)
        # verify gone
        leg(f"nat-{tag}-postclean", ["bash","-c","pw-dump | python3 -c 'import json,sys;d=json.load(sys.stdin);print(len(d))'"], reps=1)

# ============ S5: EnumFormat / renegotiation ============
def s5():
    li = subprocess.run(["pactl","load-module","module-null-sink","sink_name=r90_ns",
                         "sink_properties=device.description=r90_ns"], capture_output=True, text=True)
    midx = li.stdout.strip(); time.sleep(0.8)
    try:
        d = pw_dump()
        ns = next(o["id"] for o in d if o["type"].endswith("Node")
                  and (o.get("info",{}).get("props",{}) or {}).get("node.name")=="r90_ns")
        ns_ports = [o for o in d if o["type"].endswith("Port")
                    and str((o.get("info",{}).get("props",{}) or {}).get("node.id"))==str(ns)]
        # node-level EnumFormat pre-link (no stream yet)
        leg("s5-ns-enumformat", ["pw-cli","enum-params",str(ns),"EnumFormat"])
        leg("s5-ns-format", ["pw-cli","enum-params",str(ns),"Format"])
        # port EnumFormat on the sink's input ports pre-link
        for po in ns_ports[:2]:
            pid=po["id"]
            leg(f"s5-port{pid}-enumformat", ["pw-cli","enum-params",str(pid),"EnumFormat"], reps=1)
            leg(f"s5-port{pid}-format", ["pw-cli","enum-params",str(pid),"Format"], reps=1)
        # spawn own stream to the null sink; capture stream node id
        tone = RUNS/"tone.wav"
        if not tone.exists():
            import wave,struct,math
            with wave.open(str(tone),"wb") as w:
                w.setnchannels(2); w.setsampwidth(2); w.setframerate(48000)
                frames=b"".join(struct.pack("<hh",int(8000*math.sin(2*math.pi*440*i/48000)),
                                            int(8000*math.sin(2*math.pi*880*i/48000)))
                                for i in range(48000*8))
                w.writeframes(frames)
        proc = subprocess.Popen(["pw-play","-P","node.name=r90_stream","--target","r90_ns",
                                 str(tone)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                start_new_session=True)
        time.sleep(1.4)
        d2 = pw_dump()
        st = next((o["id"] for o in d2 if o["type"].endswith("Node")
                   and (o.get("info",{}).get("props",{}) or {}).get("node.name")=="r90_stream"), None)
        if st:
            leg("s5-stream-enumformat", ["pw-cli","enum-params",str(st),"EnumFormat"])
            leg("s5-stream-format", ["pw-cli","enum-params",str(st),"Format"])
            stports = [o["id"] for o in d2 if o["type"].endswith("Port")
                       and str((o.get("info",{}).get("props",{}) or {}).get("node.id"))==str(st)]
            for pid in stports[:2]:
                leg(f"s5-stport{pid}-enumformat", ["pw-cli","enum-params",str(pid),"EnumFormat"], reps=1)
                leg(f"s5-stport{pid}-format", ["pw-cli","enum-params",str(pid),"Format"], reps=1)
                leg(f"s5-stport{pid}-latency", ["pw-cli","enum-params",str(pid),"Latency"], reps=1)
            # link objects for the pair
            links = [o for o in d2 if o["type"].endswith("Link")]
            (RUNS/"s5-links.json").write_text(json.dumps(links,indent=1))
            # disconnect the link then re-enumerate: does EnumFormat/Format revert?
            out_port = stports[0] if stports else None
            in_port = next((o["id"] for o in d2 if o["type"].endswith("Port")
                            and str((o.get("info",{}).get("props",{}) or {}).get("node.id"))==str(ns)
                            and "input" in ((o.get("info",{}).get("props",{}) or {}).get("port.name",""))), None)
            if out_port and in_port:
                leg("s5-pwlink-disc", ["pw-link","-d",f"r90_stream:output_FL",f"r90_ns:playback_FL"], reps=1)
                time.sleep(0.6)
                leg(f"s5-stport{out_port}-format-postdisc", ["pw-cli","enum-params",str(out_port),"Format"], reps=1)
                leg(f"s5-stport{out_port}-enumformat-postdisc", ["pw-cli","enum-params",str(out_port),"EnumFormat"], reps=1)
                leg("s5-pwlink-relink", ["pw-link",f"r90_stream:output_FL",f"r90_ns:playback_FL"], reps=1)
                time.sleep(0.6)
                leg(f"s5-stport{out_port}-format-relinked", ["pw-cli","enum-params",str(out_port),"Format"], reps=1)
            # passive link + props link
            leg("s5-pwlink-passive", ["pw-link","-P",f"r90_stream:output_FR",f"r90_ns:playback_FR"], reps=1)
            time.sleep(0.4)
            d3 = pw_dump()
            (RUNS/"s5-links-passive.json").write_text(json.dumps(
                [o for o in d3 if o["type"].endswith("Link")],indent=1))
            leg("s5-pwlink-props", ["pw-link","-p",'{"r90.marker":"yes"}',
                                    f"r90_stream:output_FL",f"r90_ns:playback_FL"], reps=1)
            # does a node-level EnumFormat write mid-stream do anything? (r87: Format sealed)
            leg("s5-setparam-enumformat", ["pw-cli","set-param",str(st),"EnumFormat","{}"], reps=1)
        proc.send_signal(signal.SIGTERM)
        try: proc.wait(3)
        except subprocess.TimeoutExpired: proc.kill()
    finally:
        if midx.isdigit():
            subprocess.run(["pactl","unload-module",midx], capture_output=True)
        time.sleep(0.5)
        Path(RUNS/"s5-post.json").write_text(json.dumps(census_r90()[0]))

# ============ S6: pw-link semantics ============
def s6():
    li = subprocess.run(["pactl","load-module","module-null-sink","sink_name=r90_ns",
                         "sink_properties=device.description=r90_ns"], capture_output=True, text=True)
    midx = li.stdout.strip(); time.sleep(0.8)
    proc = subprocess.Popen(["pw-play","-P","node.name=r90_stream","--target","r90_ns",
                             str(RUNS/"tone.wav")], stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, start_new_session=True)
    time.sleep(1.3)
    try:
        leg("pl-o", ["pw-link","-o"])
        leg("pl-i", ["pw-link","-i"], reps=1)
        leg("pl-l", ["pw-link","-l"])
        leg("pl-lI", ["pw-link","-lI"], reps=1)
        leg("pl-t", ["pw-link","-t"], reps=1)
        leg("pl-v", ["pw-link","-ov"], reps=1)
        # pattern semantics
        for pat in ("r90_stream","r90*","*r90*","r90","*FL*","r90_stream:output_FL","bogus*","r90_ns"):
            leg(f"pl-pat-{pat.replace('*','S').replace(':','_')}", ["pw-link","-o",pat], reps=1)
        # list with two patterns
        leg("pl-pat-pair", ["pw-link","-l","r90_stream*","r90_ns*"], reps=1)
        # connect forms
        leg("pl-conn-names", ["pw-link","r90_stream:output_FL","r90_ns:playback_FL"], reps=1)
        # port-id numeric connect?
        d = pw_dump()
        outp = next((o["id"] for o in d if o["type"].endswith("Port") and
                     (o.get("info",{}).get("props",{}) or {}).get("port.name")=="output_FL" and
                     (o.get("info",{}).get("props",{}) or {}).get("node.name")=="r90_stream"), None)
        inp = next((o["id"] for o in d if o["type"].endswith("Port") and
                    (o.get("info",{}).get("props",{}) or {}).get("port.name")=="playback_FR" and
                    (o.get("info",{}).get("props",{}) or {}).get("node.name")=="r90_ns"), None)
        if outp and inp:
            leg("pl-conn-ids", ["pw-link",str(outp),str(inp)], reps=1)
            time.sleep(0.4)
            # disconnect by id vs pair
            links = [o for o in pw_dump() if o["type"].endswith("Link")]
            (RUNS/"s6-links.json").write_text(json.dumps(links,indent=1))
            lid = next((o["id"] for o in links if "r90" in json.dumps(o)), None)
            if lid is not None:
                leg("pl-disc-linkid", ["pw-link","-d",str(lid)], reps=1)
                time.sleep(0.3)
                leg("pl-disc-verify", ["pw-link","-l"], reps=1)
            leg("pl-disc-pair", ["pw-link","-d","r90_stream:output_FL","r90_ns:playback_FL"], reps=1)
        leg("pl-disc-boguspair", ["pw-link","-d","r90_stream:nope","r90_ns:nope"], reps=1)
        leg("pl-disc-bogusid", ["pw-link","-d","999999"], reps=1)
        leg("pl-conn-bogus", ["pw-link","r90_stream:nope","r90_ns:playback_FL"], reps=1)
        leg("pl-conn-same", ["pw-link","r90_stream:output_FL","r90_stream:output_FR"], reps=1)
        # batching: multiple pairs in one argv
        leg("pl-batch3", ["pw-link","r90_stream:output_FL","r90_ns:playback_FL",
                          "r90_stream:output_FR","r90_ns:playback_FR"], reps=1)
        # -m monitor semantics: connect + monitor, then kill — does link die?
        pm = subprocess.Popen(["pw-link","-m","r90_stream:output_FL","r90_ns:playback_FL"],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                              start_new_session=True)
        time.sleep(1.0)
        links_live = len([o for o in pw_dump() if o["type"].endswith("Link")])
        pm.send_signal(signal.SIGTERM)
        try: mo,me = pm.communicate(timeout=3); how="sigterm"
        except subprocess.TimeoutExpired: pm.kill(); mo,me=pm.communicate(); how="sigkill"
        time.sleep(0.4)
        links_dead = len([o for o in pw_dump() if o["type"].endswith("Link")])
        (RAW/"pl-monitor.1.out").write_text(mo); (RAW/"pl-monitor.1.err").write_text(me)
        RECEIPT.open("a").write(json.dumps({"leg":"pl-monitor","rep":1,"rc":pm.returncode,
            "how":how,"links_live":links_live,"links_dead":links_dead,
            "out_sha":hashlib.sha256(mo.encode()).hexdigest()[:16]})+"\n")
        # -w wait on a resolvable and unresolvable pair
        leg("pl-w-ok", ["pw-link","-w","r90_stream:output_FL","r90_ns:playback_FL"], reps=1, timeout=8)
        leg("pl-w-bad", ["pw-link","-w","r90_stream:nope","r90_ns:nope"], reps=1, timeout=8)
        leg("pl-w-time", ["bash","-c","time pw-link -w r90_stream:nope r90_ns:nope 2>&1"], reps=1, timeout=12)
    finally:
        proc.send_signal(signal.SIGTERM)
        try: proc.wait(3)
        except subprocess.TimeoutExpired: proc.kill()
        if midx.isdigit():
            subprocess.run(["pactl","unload-module",midx], capture_output=True)
        time.sleep(0.5)
        Path(RUNS/"s6-post.json").write_text(json.dumps(census_r90()[0]))

if __name__ == "__main__":
    which = sys.argv[1:] or ["s0","s1","s1m","s2","s3","s4","s5","s6"]
    if "s0" in which: s0()
    if "s1" in which: s1()
    if "s1m" in which: s1_mutate()
    if "s2" in which: s2()
    if "s3" in which: s3()
    if "s4" in which: s4()
    if "s5" in which: s5()
    if "s6" in which: s6()
    RECEIPT.with_suffix(".json").write_text(json.dumps(records,indent=1))
    hits,n = census_r90()
    print(f"DONE {len(records)} runs; census {n} objects; r90-residue: {hits}")
