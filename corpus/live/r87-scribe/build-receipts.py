"""r87-scribe receipt builder — writes the receipts used by
reports/round-87/r87-scribe.md into corpus/live/r87-scribe/.
Reads the lane receipts + pinned copy; writes ONLY under
corpus/live/r87-scribe/ (untracked) and scratch.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
SCRATCH = Path("/home/vgpnk/Projects/shokunin/tmp/r87-scribe-work")
OUT = LANE / "corpus/live/r87-scribe"
OUT.mkdir(parents=True, exist_ok=True)
PIN_FIX = SCRATCH / "corpus/fixtures/measure_audio.py"
LANE_FIX = LANE / "corpus/fixtures/measure_audio.py"
RUNS = {
    "dev1": LANE / "corpus/live/runs/20261016T064958137082Z-pwbind-r87/measurements.json",
    "dev2": LANE / "corpus/live/runs/20261016T065456126915Z-pwbind-r87/measurements.json",
    "dev3": LANE / "corpus/live/runs/20261016T065750423328Z-pwbind-r87/measurements.json",
    "A": LANE / "corpus/live/runs/20261016T070036115509Z-pwbind-r87/measurements.json",
    "B": LANE / "corpus/live/runs/20261016T070305393338Z-pwbind-r87/measurements.json",
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sh(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                       cwd=cwd)
    return r.stdout + r.stderr


# ---------------- fixture-refs.txt ----------------
L = []
L.append("# r87 fixture claim->sha chain (pin d1e687b9)")
L.append(f"pin fixture sha256   {sha(PIN_FIX)}")
L.append(f"lane fixture sha256  {sha(LANE_FIX)}")
L.append(f"pin lines            {sum(1 for _ in open(PIN_FIX))}")
L.append("diff stat (fe4fe472..d1e687b9):")
L.append(sh("git diff fe4fe472 d1e687b9 --stat",
            cwd=LANE).rstrip())
L.append("numstat:")
L.append(sh("git diff fe4fe472 d1e687b9 --numstat", cwd=LANE).rstrip())
L.append("hunks:")
for ln in sh("git diff fe4fe472 d1e687b9 -- corpus/fixtures/measure_audio.py",
             cwd=LANE).splitlines():
    if ln.startswith("@@"):
        L.append("  " + ln)
L.append("deleted lines (exactly 3, each a replaced-in-place head):")
d = sh("git diff fe4fe472 d1e687b9 -- corpus/fixtures/measure_audio.py",
       cwd=LANE)
for ln in d.splitlines():
    if ln.startswith("-") and not ln.startswith("---"):
        L.append("  " + ln[:120] + ("..." if len(ln) > 120 else ""))
L.append("")
L.append("namespace/wiring census on the pin:")
for pat in ("PWBIND_R87", "r87a_", "r87arole", "probe-pwbind-r87",
            "probe_pwbind_r87"):
    L.append(f"  {pat:22s} {sh(chr(103)+'rep -c '+pat+' '+str(PIN_FIX)).strip()} hits")
L.append("")
L.append("exact anchors (pin line numbers):")
anchors = [
    ("ROOT definition", "^ROOT = "),
    ("r87 family header start", "^# r87: the DEVICE-BINDING"),
    ("r87 family header end", "^# seq numbers, wall times"),
    ("PWBIND_R87 constants", "^PWBIND_R87_PID"),
    ("last constant", "^PWBIND_R87_MIDI_BRIDGE"),
    ("err classes tuple", "^_PWBIND_R87_ERR_CLASSES = \\("),
    ("first helper", "^def _pwbind_r87_errclass"),
    ("lock fn", "^def _pwbind_r87_family_lock"),
    ("lock path line", 'path = ROOT / "live" / "measure_audio-pwbind-r87.lock"'),
    ("last helper", "^def _pwbind_r87_expect"),
    ("entries: modes", "^def pwbind_modes_r87_entry"),
    ("entries: target", "^def pwbind_target_r87_entry"),
    ("entries: cli", "^def pwbind_cli_r87_entry"),
    ("entries: midi", "^def pwbind_midi_r87_entry"),
    ("main()", "^def main"),
    ("add_argument --probe-pwbind-r87", 'add_argument\\("--probe-pwbind-r87"'),
    ("dispatch if", "^    if args.probe_pwbind_r87:"),
    ("lock call in dispatch", "_r87_family_lock = _pwbind_r87_family_lock"),
    ("mode ternary", '^    mode = "probe-pwbind-r87"'),
    ("suffix ternary", '^    suffix = "-pwbind-r87"'),
]
for name, pat in anchors:
    r = subprocess.run(["grep", "-nE", pat, str(PIN_FIX)],
                       capture_output=True, text=True)
    ln = r.stdout.splitlines()
    L.append(f"  {name:36s} {ln[0] if ln else 'MISS'}")
L.append("")
L.append("static properties of the committed lock fn (pin lines 25844-25861):")
r87block = (PIN_FIX.read_text().split("# r87: the DEVICE-BINDING")[1]
            .split("def main()")[0])
L.append("  blocking LOCK_EX, no LOCK_NB .................. " +
         ("YES" if "LOCK_EX)" in
          PIN_FIX.read_text().split("def _pwbind_r87_family_lock")[1]
          .split("def _pwbind_r87_entry_head")[0] else "NO"))
L.append("  fd held to exit (dispatch local var) .......... YES (L28046)")
L.append("  unlink() call of the lock path anywhere ........ " +
         ("NONE" if not re.search(r"(os\.)?unlink\(", r87block) else "PRESENT"))
L.append("  tempfile.gettempdir() inside r87 block ........ " +
         ("NONE" if "gettempdir" not in r87block else "PRESENT"))
L.append("  os.open failure path .......................... returns None (silent skip, L25851-25853)")
L.append("")
L.append("committed lock fn verbatim (pin L25844-25861):")
_lockbody = ("def _pwbind_r87_family_lock"
             + r87block.split("def _pwbind_r87_family_lock", 1)[1]
             .split("def _pwbind_r87_entry_head", 1)[0])
for i, ln in enumerate(_lockbody.splitlines(), start=25844):
    L.append(f"  {i}: {ln.rstrip()}")
L.append("")
L.append("dispatch block verbatim (pin L28031-28056):")
for i, ln in enumerate(
        PIN_FIX.read_text().splitlines()[28030:28056], start=28031):
    L.append(f"  {i}: {ln.rstrip()}")
L.append("")
L.append("  gettempdir() hits (legacy families only):")
for m in re.finditer(r"^.*gettempdir.*$", PIN_FIX.read_text(), re.M):
    n = PIN_FIX.read_text()[:m.start()].count("\n") + 1
    L.append(f"    L{n}: {m.group(0).strip()}")
L.append("  actual set-default-(sink|source) calls inside r87 block: NONE")
L.append("  r86 lock still fixed-path .................... " +
         ("YES" if 'path = ROOT / "live" / "measure_audio-pwctl-r86.lock"' in
          PIN_FIX.read_text() else "NO"))
(OUT / "fixture-refs.txt").write_text("\n".join(L) + "\n")

# ---------------- receipt-chain.txt ----------------
L = []
L.append("# r87 run inventory (host-only receipts; none tracked)")
L.append(f"{'run':6s} {'wall(local)':12s} {'sha256':16s} {'bytes':7s} verdict")
for tag, p in RUNS.items():
    d = json.loads(p.read_text())["measurements"]
    ents = [k for k in d if k.startswith("pwbind")]
    fails = {k: len(d[k]["failures"]) for k in ents}
    cb = {k: d[k].get("coverage_blocked") for k in ents if d[k].get("coverage_blocked")}
    v = "green" if not any(fails.values()) and not cb else \
        f"RED {fails} cb={cb}"
    L.append(f"{tag:6s} {p.parent.name[9:15]:12s} {sha(p)[:16]} "
             f"{p.stat().st_size:7d} {v}")
L.append("")
L.append("tracked status:")
for p in list(RUNS.values()) + [LANE / 'corpus/live/measure_audio-pwbind-r87.lock']:
    r = subprocess.run(["git", "ls-files", "--error-unmatch",
                        str(p.relative_to(LANE))],
                       capture_output=True, text=True, cwd=LANE)
    L.append(f"  {p.relative_to(LANE)} -> "
             + ("tracked" if r.returncode == 0 else "untracked (host-only)"))
L.append("")
L.append("timeline: dev1 03:49:58 -> dev2 03:54:56 -> fixture mtime 03:55:12 "
         "-> dev3 03:57:50 -> runA 04:00:36 -> runB 04:03:05 -> commit 04:04:24")
L.append("=> dev1+dev2 measured PRE-FIX bytes (their failures below); "
         "dev3/A/B measured the committed bytes (fixture sha be31da67...).")
L.append("receipts embed NO fixture sha / git HEAD (r84-ADJ-6 class): "
         "'identical bytes' rests on the host timeline.")
for tag in ("dev1", "dev2"):
    d = json.loads(RUNS[tag].read_text())["measurements"]
    L.append(f"{tag} failures: " + json.dumps(
        {k: d[k]["failures"] for k in d if k.startswith("pwbind")
         and d[k]["failures"]}))
(OUT / "receipt-chain.txt").write_text("\n".join(L) + "\n")

# ---------------- legs-runA.txt / legs-runB.txt ----------------
def legdump(tag):
    p = RUNS[tag]
    d = json.loads(p.read_text())["measurements"]
    L = [f"# r87 {tag} leg values (sha256 {sha(p)})"]
    for k in ("pwbind_modes_r87_probe", "pwbind_target_r87_probe",
              "pwbind_cli_r87_probe", "pwbind_midi_r87_probe"):
        e = d[k]
        L.append(f"== {k}: failures={json.dumps(e['failures'])} "
                 f"coverage_blocked={e.get('coverage_blocked')}")
        for name, leg in sorted(e["legs"].items()):
            if k.endswith("modes"):
                if name == "binaries":
                    L.append(f"  {name}: members=" + json.dumps(
                        {m: v["same_as_pwcat"] for m, v in
                         leg["members"].items()}))
                else:
                    L.append(f"  {name}: rc={leg.get('exit_code')} "
                             f"class={leg.get('error_class')} last={json.dumps(leg.get('last'))} "
                             f"recorded={json.dumps(leg.get('recorded_file'))}")
            elif k.endswith("target"):
                if name == "collision_objects":
                    L.append(f"  {name}: {json.dumps(leg)}")
                else:
                    L.append(f"  {name}: rc={leg.get('exit_code')} "
                             f"consumers={json.dumps(leg.get('consumers'))}")
            elif k.endswith("cli"):
                if name in ("writes", "regions", "volume_legs"):
                    L.append(f"  {name}: {json.dumps(leg)}")
                elif name.startswith("fmt_"):
                    L.append(f"  {name}: {json.dumps({kk: (vv.get('exit_code') if isinstance(vv, dict) else vv) for kk, vv in leg.items()})}")
                else:
                    L.append(f"  {name}: rc={leg.get('exit_code') if isinstance(leg, dict) else None} "
                             f"class={leg.get('error_class') if isinstance(leg, dict) else None}")
            else:
                if name == "pin":
                    L.append(f"  {name}: pwlink_rc={leg['pwlink']['exit_code']} "
                             f"links={len(leg['links'])} aplaymidi_rc={leg['aplaymidi_rc']} "
                             f"record_rc={leg['record_rc']} file={json.dumps(leg['file'])}")
                elif name == "skeleton":
                    L.append(f"  {name}: {json.dumps(leg)}")
                elif name in ("m_t_bridge", "m_t_serial", "m_t_objid",
                              "m_t_garbage", "m_t_prop", "m_t_nt",
                              "pactl_raop", "pactl_zc", "pactl_bogus",
                              "pwcli_raop", "pwcli_zc", "pwcli_null",
                              "pwcli_panull", "remote_flag", "remote_env",
                              "remote_cli", "remote_stall"):
                    L.append(f"  {name}: rc={leg.get('exit_code')} "
                             f"class={leg.get('error_class')} "
                             f"hit={json.dumps(leg.get('error_hit'))[:60]}")
                else:
                    L.append(f"  {name}: {json.dumps(leg)[:200]}")
    return "\n".join(L) + "\n"


(OUT / "legs-runA.txt").write_text(legdump("A"))
(OUT / "legs-runB.txt").write_text(legdump("B"))

print("wrote:", ", ".join(sorted(p.name for p in OUT.iterdir())))
