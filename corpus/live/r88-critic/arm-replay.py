#!/usr/bin/env python3
"""r88 critic — arm replay.

The three r88 verdict blocks are sliced VERBATIM out of the committed
source (git c19bec96 -> corpus/live/r88-critic/_committed_measure_audio.py,
sha ad9d59b1...), written to verdict-*.py for the MANIFEST, and exec'd
against the committed receipts (both green runs + the dev run) with the
receipt's own legs/entry bound.  Then a targeted mutation battery drives
each headline claim to its opposite and asserts the verdict turns RED
(either-way proof), with volatile-field controls that must stay PASS.

No host mutation, no tracked writes.
"""
import copy
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
COMMITTED = os.path.join(HERE, "_committed_measure_audio.py")
RUNS = os.path.join(ROOT, "corpus", "live", "runs")

RUN_IDS = {
    "A": "20261016T072313132218Z-btwit-r88",
    "B": "20261016T072341162452Z-btwit-r88",
    "dev": "20261016T071710822152Z-btwit-r88",
}
ENTRIES = ["btabs_bluez_r88_probe", "witdiff_dump_r88_probe",
           "pwtop_r88_probe"]

src = open(COMMITTED).read()


def slice_verdict(fn, nxt):
    i = src.index(f"def {fn}():")
    j = src.index(f"def {nxt}():", i)
    body = src[i:j]
    k = body.index("    # ---------------- verdicts ----------------")
    m = body.index('    entry["legs"] = legs')
    return body[k:m]


BLOCKS = {
    "btabs_bluez_r88_probe": slice_verdict(
        "btabs_bluez_r88_entry", "witdiff_dump_r88_entry"),
    "witdiff_dump_r88_probe": slice_verdict(
        "witdiff_dump_r88_entry", "pwtop_r88_entry"),
    "pwtop_r88_probe": slice_verdict("pwtop_r88_entry", "main"),
}

BLOCK_SHA = {}
for e, b in BLOCKS.items():
    p = os.path.join(HERE, f"verdict-{e}.py")
    with open(p, "w") as f:
        f.write(b)
    BLOCK_SHA[e] = hashlib.sha256(b.encode()).hexdigest()

# import the committed module as a library (main() is __main__-guarded)
spec = importlib.util.spec_from_file_location("ma_c19bec96", COMMITTED)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

sys.setrecursionlimit(10000)


def run_verdict(entry_name, legs, entry, extra=None):
    g = dict(mod.__dict__)
    g["legs"] = copy.deepcopy(legs)
    g["entry"] = copy.deepcopy(entry)
    g["failures"] = []
    if extra:
        g.update(extra)
    # wrap (never dedent) so the sliced text stays byte-verbatim inside
    # a valid suite; the block's own 4-space indent is preserved
    exec(compile("if True:\n" + BLOCKS[entry_name],
                 f"<verdict:{entry_name}>", "exec"), g)
    return (g["failures"], g["entry"].get("coverage_blocked"),
            g["entry"], g["legs"])


PID_RE = re.compile(r"r88a_ns_(\d+)")


def pid_of(entry):
    """The run's own pid, recovered from the receipt (the verdict block
    compares against BTWIT_R88_NS = r88a_ns_<pid>, so the replay must
    bind the *author run's* pid, not the critic's)."""
    m = PID_RE.search(json.dumps(entry))
    return m.group(1) if m else None


def pid_globals(pid):
    return {
        "BTWIT_R88_PID": pid,
        "BTWIT_R88_PREFIX": f"r88a_{pid}",
        "BTWIT_R88_NS": f"r88a_ns_{pid}",
        "BTWIT_R88_NS2": f"r88a_ns2_{pid}",
        "BTWIT_R88_ROLE": f"r88arole{pid}",
    }


def load(tag):
    with open(os.path.join(RUNS, RUN_IDS[tag], "measurements.json")) as f:
        return json.load(f)["measurements"]


RESULT = {"block_sha": BLOCK_SHA, "rederive": {}, "mutations": [],
          "controls": []}

# ---------------- re-derivation on the committed receipts ------------
for tag in ("A", "B", "dev"):
    m = load(tag)
    RESULT["rederive"][tag] = {}
    for e in ENTRIES:
        if e not in m:
            RESULT["rederive"][tag][e] = {"absent": True}
            continue
        fails, cb, _e, _l = None, None, None, None
        err = None
        try:
            pid = pid_of(m[e])
            fails, cb, _e, _l = run_verdict(
                e, m[e]["legs"], m[e], extra=pid_globals(pid))
        except Exception as exc:  # earlier code state -> not re-derivable
            err = f"{type(exc).__name__}: {exc}"
        rec = m[e]
        RESULT["rederive"][tag][e] = {
            "receipt_failures": rec.get("failures"),
            "rederived_failures": fails,
            "receipt_coverage_blocked": rec.get("coverage_blocked"),
            "rederived_coverage_blocked": cb,
            "rederive_error": err,
            "match": err is None and fails == (rec.get("failures") or []),
        }

# ---------------- mutation battery -----------------------------------
MUT = []


def mut(mid, entry, fn, expect, note):
    MUT.append((mid, entry, fn, expect, note))


# ---- btabs_bluez_r88_probe (the absent-class claims) ----------------
def _dev0(l):
    return l["bz_device"]["devices"][0]


mut("B1_device_audio_uuid", "btabs_bluez_r88_probe",
    lambda l: _dev0(l).update({"audio_uuids": ["110a"]}), "RED",
    "the paired device gains an A2DP UUID")
mut("B2_bluez_card_exists", "btabs_bluez_r88_probe",
    lambda l: l["bz_cards"]["cards"].append(
        {"index": 99, "name": "bluez_card.BC_C7_46_34_C5_66"}), "RED",
    "a bluez card appears")
mut("B3_bluez_sink_exists", "btabs_bluez_r88_probe",
    lambda l: l["bz_sinks"]["sinks"].append(
        "bluez_output.BC_C7_46_34_C5_66.a2dp-sink"), "RED",
    "a bluez sink appears")
mut("B4_bridge_not_midi", "btabs_bluez_r88_probe",
    lambda l: l["bz_midi_bridge"]["bluez_objects"][0].update(
        {"media_class": "Audio/Sink"}), "RED",
    "the one bluez5 object is audio-class")
mut("B5_adapter_unpowered", "btabs_bluez_r88_probe",
    lambda l: l["bz_adapter"].update({"stdout": "b false\n"}), "RED",
    "adapter Powered=false")
mut("B6_media1_no_a2dp", "btabs_bluez_r88_probe",
    lambda l: l["bz_media1"].update(
        {"stdout": 'as 1 "0000110e-0000-1000-8000-00805f9b34fb"\n'}), "RED",
    "A2DP endpoints not advertised")
mut("B7_fabrication_succeeds", "btabs_bluez_r88_probe",
    lambda l: l["bz_create_a2dpsink"].update(
        {"exit_code": 0, "error_class": None, "stderr": ""}), "RED",
    "create-node a2dp-sink is not refused")
mut("B8_fabrication_residue", "btabs_bluez_r88_probe",
    lambda l: l.update({"bz_own_residue": ["r88a_1_bz_create_a2dpsink"]}),
    "RED", "a create-node attempt left an object")
mut("B9_bluez_module_loaded", "btabs_bluez_r88_probe",
    lambda l: l["bz_mods_after"].update(
        {"bluez_modules": ["42 module-bluez5-discover"]}), "RED",
    "a bluez-named module is loaded")
mut("B10_loadmod_succeeds", "btabs_bluez_r88_probe",
    lambda l: l["bz_loadmod_device"].update(
        {"exit_code": 0, "error_class": None}), "RED",
    "module-bluez5-device loads")
mut("B11_sendmsg_ok", "btabs_bluez_r88_probe",
    lambda l: l["bz_sendmsg"].update({"exit_code": 0}), "RED",
    "send-message succeeds")
mut("B12_spa_count_13", "btabs_bluez_r88_probe",
    lambda l: l["bz_spa_inventory"].update({"count": 13}), "RED",
    "the boundary's 14-file correction is 13 again")
mut("B13_codecs_absent", "btabs_bluez_r88_probe",
    lambda l: l.update({"bz_spa_codecs_str": {
        "substring_hits": [], "standalone_lines": 0,
        "bluez5_names": 0}}), "RED",
    "the parsed bluez5.codecs property vanishes (scout's claim)")
mut("B14_module_on_disk", "btabs_bluez_r88_probe",
    lambda l: l["bz_find_module"].update(
        {"hits": ["/usr/lib/pipewire-0.3/module-bluez5-device.so"]}), "RED",
    "module-bluez5*.so exists on disk")
mut("B15_media_transport", "btabs_bluez_r88_probe",
    lambda l: l["bz_media_transport"].update(
        {"media_transport_objects": ["MediaTransport1"]}), "RED",
    "a MediaTransport object exists")
mut("B16_pactl_two_lines", "btabs_bluez_r88_probe",
    lambda l: l["bz_pactl_lines"].update(
        {"matches": l["bz_pactl_lines"]["matches"] +
         ["bluez_card.BC_C7_46_34_C5_66"], "count": 2}), "RED",
    "pactl list grows a second bluez line")
mut("B17_nullctl_fails", "btabs_bluez_r88_probe",
    lambda l: l["bz_nullsink_ctl"].update({"rc": 1}), "RED",
    "the live positive control (module-null-sink) fails")
mut("B18_setcard_bogus_ok", "btabs_bluez_r88_probe",
    lambda l: l["bz_setcard_bogusctl"].update(
        {"exit_code": 0, "error_class": None}), "RED",
    "the bogus-profile confound does not reproduce")
mut("B19_tree_no_adapter", "btabs_bluez_r88_probe",
    lambda l: l["bz_tree"].update({"adapters": []}), "RED",
    "no hci adapter")
mut("B20_device_record_gone", "btabs_bluez_r88_probe",
    lambda l: l["bz_device"].update({"devices": []}), "PASS?",
    "SILENT-SKIP probe: device list emptied -> is the HID-only "
    "claim then vacuous without coverage_blocked?")

# ---- witdiff_dump_r88_probe ----------------------------------------
mut("W1_setrule_extra_id", "witdiff_dump_r88_probe",
    lambda l: l["wd_setrule_own_id"].update(
        {"got": l["wd_setrule_own_id"]["got"] + ["154"]}), "RED",
    "pw-dump returns one id too many")
mut("W2_setrule_missing_id", "witdiff_dump_r88_probe",
    lambda l: l["wd_setrule_own_id"].update({"got": []}), "RED",
    "pw-dump returns nothing")
mut("W3_nested_ports", "witdiff_dump_r88_probe",
    lambda l: l["wd_no_nested"].update({"port_objects": 1}), "RED",
    "pw-dump <id> expands ports")
mut("W4_mode_variant", "witdiff_dump_r88_probe",
    lambda l: l["wd_mode_raw"].update({"ids": ["154"]}), "RED",
    "membership is mode-dependent")
mut("W5_spa_form_broken", "witdiff_dump_r88_probe",
    lambda l: l["wd_mode_spa"].update(
        {"stdout_raw": "", "stdout": ""}), "RED",
    "-s form lacks id/serial")
mut("W6_cli_serial_resolves", "witdiff_dump_r88_probe",
    lambda l: l["wd_cli_serial"].update(
        {"exit_code": 0, "error_class": None}), "RED",
    "pw-cli info accepts a serial")
mut("W7_ls_serial_hidden", "witdiff_dump_r88_probe",
    lambda l: l["wd_ls_serial"].update(
        {"stdout_raw": "id 153, type PipeWire:Interface:Node/3\n"}),
    "RED", "ls stops exposing object.serial")
mut("W8_propblock_swapped", "witdiff_dump_r88_probe",
    lambda l: l["wd_propblock"].update(
        {"ls_layout": "star", "info_layout": "flat"}), "RED",
    "the two layouts swap")
mut("W9_keyset_diverges", "witdiff_dump_r88_probe",
    lambda l: l["wd_keyset_own"].update({"cli_only": ["ghost"]}), "RED",
    "prop key sets diverge")
mut("W10_param_names_diverge", "witdiff_dump_r88_probe",
    lambda l: l["wd_params_own"].update(
        {"dump": l["wd_params_own"]["dump"] + ["Ghost"]}), "RED",
    "param names diverge")
mut("W11_silent_dump_speaks", "witdiff_dump_r88_probe",
    lambda l: l["wd_silent_dump_id"].update({"stdout": "[{}]"}), "RED",
    "a dead-id dump is not silent")
mut("W12_dump_empty_partial", "witdiff_dump_r88_probe",
    lambda l: l["wd_dump_empty"].update({"parsed_ids": []}), "RED",
    "'' is not the full dump")
mut("W13_dump_two_both", "witdiff_dump_r88_probe",
    lambda l: l["wd_dump_two"].update({"ids": ["153", "29"]}), "RED",
    "multi-id honors both ids")
mut("W14_color_parses", "witdiff_dump_r88_probe",
    lambda l: l["wd_dump_color"].update({"json_parses": True}), "RED",
    "ANSI does not break JSON")
mut("W15_neg_rc0", "witdiff_dump_r88_probe",
    lambda l: l["wd_dump_neg"].update(
        {"exit_code": 0, "error_class": None}), "RED",
    "pw-dump -1 is accepted")
mut("W16_meta_not_superset", "witdiff_dump_r88_probe",
    lambda l: l["wd_ls_metadata"].update({"extra": []}), "RED",
    "ls Metadata == dump Metadata (no visibility split)")
mut("W17_info_all_metadata", "witdiff_dump_r88_probe",
    lambda l: l["wd_info_all"].update({"metadata_described": ["31"]}),
    "RED", "info all stops omitting Metadata")
mut("W18_enum_name_ne_num", "witdiff_dump_r88_probe",
    lambda l: l["wd_enum_num2"].update(
        {"stdout": "Object: something else"}), "RED",
    "numeric != name on a readable param")
mut("W19_enum_bogus_class", "witdiff_dump_r88_probe",
    lambda l: l["wd_enum_bogus"].update(
        {"error_class": "pwcli_unknown_global"}), "RED",
    "unknown param name changes class")
mut("W20_serial_violation", "witdiff_dump_r88_probe",
    lambda l: l["wd_serial_law"].update(
        {"violations": [{"name": "x", "pactl_index": 1,
                         "serial": "2"}]}), "RED",
    "pactl index != object.serial")
mut("W21_state3_disagrees", "witdiff_dump_r88_probe",
    lambda l: l["wd_state3"]["vocab"].update({"cli": "idle"}), "RED",
    "vocabularies disagree in the tight window")
mut("W22_writeonly_pod", "witdiff_dump_r88_probe",
    lambda l: l["wd_enum_fmt"].update({"stdout": "Object: pod"}),
    "RED", "a write-only param returns a pod")
mut("W23_setrule_foreign_absent", "witdiff_dump_r88_probe",
    lambda l: [l.pop("wd_setrule_foreign_id", None),
               l.pop("wd_setrule_foreign_serial", None)], "PASS?",
    "SILENT-SKIP probe: foreign set-rule legs removed (the "
    "no-foreign-node host shape)")
mut("W24_dump_two_absent", "witdiff_dump_r88_probe",
    lambda l: l.pop("wd_dump_two", None), "PASS?",
    "SILENT-SKIP probe: wd_dump_two removed (the f_id-None host "
    "shape)")
mut("W25_enum_props_vacuous", "witdiff_dump_r88_probe",
    lambda l: l["wd_enum_props"].update(
        {"stdout": "", "stderr": "", "error_class": None}), "PASS+CB",
    "readable-param leg answers nothing -> expect coverage_blocked")
mut("W26_enum_fmt_rc1", "witdiff_dump_r88_probe",
    lambda l: l["wd_enum_fmt"].update(
        {"exit_code": 1, "stdout": "", "stderr": "", "error_class": None}),
    "PASS?",
    "ARM-STRENGTH probe: a rc=1, classless, empty enum call is admitted "
    "as the no-pod signature")

# ---- pwtop_r88_probe -------------------------------------------------
mut("P1_n1_two_frames", "pwtop_r88_probe",
    lambda l: l["pt_n1"].update(
        {"stdout_raw": l["pt_n1"]["stdout_raw"] + l["pt_n1"]
         ["stdout_raw"]}), "RED", "-n 1 prints two frames")
mut("P2_n1_has_S", "pwtop_r88_probe",
    lambda l: l["pt_n1"].update(
        {"stdout_raw": l["pt_n1"]["stdout_raw"].replace(
            "C   29", "S   29", 1)}), "RED",
    "the first frame is not all-CREATING")
mut("P3_n0_two_frames", "pwtop_r88_probe",
    lambda l: l["pt_n0"].update(
        {"stdout_raw": l["pt_n0"]["stdout_raw"] + l["pt_n0"]
         ["stdout_raw"]}), "RED", "-n 0 prints two frames")
mut("P4_nneg_exits", "pwtop_r88_probe",
    lambda l: l["pt_nneg"].update({"killed_at_bound": False}), "RED",
    "-n -1 is not infinite")
mut("P5_nabc_no_frames", "pwtop_r88_probe",
    lambda l: l["pt_nabc"].update({"stdout_raw": "", "stdout": ""}),
    "RED", "-n abc is infinite but emitted no frame")
mut("P6_rbogus_ok", "pwtop_r88_probe",
    lambda l: l["pt_rbogus"].update(
        {"exit_code": 0, "error_class": None}), "RED",
    "the loud remote refusal goes quiet")
mut("P7_idle_vocab_split", "pwtop_r88_probe",
    lambda l: l["pt_state_idle"]["vocab"].update({"top": "running"}),
    "RED", "idle-side four-witness agreement fails")
mut("P8_active_not_linked", "pwtop_r88_probe",
    lambda l: l.update({"pt_state_active": {"linked": False}}),
    "PASS+CB", "stream never linked -> expect coverage_blocked")
mut("P9_n3_own_still_C", "pwtop_r88_probe",
    lambda l, e: _set_n3(l, e), "RED",
    "own row still CREATING in the last frame (synthetic cache)")
mut("P10_active_vocab_split", "pwtop_r88_probe",
    lambda l: l["pt_state_active"]["vocab"].update({"dump": "suspended"}),
    "RED", "RUNNING-side agreement fails")

# controls: volatile fields must NOT be armed
mut("C1_btabs_wall_noise", "btabs_bluez_r88_probe",
    lambda l: l["bz_adapter"].update({"wall_s": 999.9, "argv": "x"}),
    "PASS", "control: volatile fields unarmed")
mut("C2_dump_stderr_noise", "witdiff_dump_r88_probe",
    lambda l: l["wd_setrule_own_id"].update({"stderr": "noise"}),
    "PASS", "control: non-armed field change")
mut("C3_top_wall_noise", "pwtop_r88_probe",
    lambda l: l["pt_n1"].update({"wall_s": 999.9}), "PASS",
    "control: volatile field unarmed")


def _set_n3(l, e):
    """Synthesize a _frames_cache matching the recorded frames /
    status_sets / last_frame_status_hist of the green receipt (the
    committed verdict pops the real cache before recording). The own
    row is forced to CREATING so the P9 arm has something to catch."""
    hist = l["pt_n3"]["last_frame_status_hist"]
    own = int(e["refs"]["own_id"])
    first = [{"status": "C", "id": 100 + i} for i in range(12)]
    last = []
    for st, c in hist:
        last += [{"status": st, "id": 100 + i} for i in range(c)]
    last[0]["id"] = own
    last[0]["status"] = "C"          # the mutation: own row still C
    mid = [{"status": s, "id": 100 + i}
           for i, s in enumerate(["S"] * 9 + ["I"] * 3)]
    l["pt_n3"]["_frames_cache"] = [first, mid, last]


def _set_n3_clean(l, e):
    """Same synthesis, own row at the recorded idle state (S) — the
    positive control for P9 (must stay PASS once the cache is bound)."""
    hist = l["pt_n3"]["last_frame_status_hist"]
    own = int(e["refs"]["own_id"])
    first = [{"status": "C", "id": 100 + i} for i in range(12)]
    last = []
    for st, c in hist:
        last += [{"status": st, "id": 100 + i} for i in range(c)]
    last[0]["id"] = own
    last[0]["status"] = "S"
    mid = [{"status": s, "id": 100 + i}
           for i, s in enumerate(["S"] * 9 + ["I"] * 3)]
    l["pt_n3"]["_frames_cache"] = [first, mid, last]


mut("P9c_n3_cache_clean", "pwtop_r88_probe",
    lambda l, e: _set_n3_clean(l, e), "PASS",
    "control: reconstructed cache with own row at idle state -> PASS")
mut("P11_active_no_vocab", "pwtop_r88_probe",
    lambda l: l.update({"pt_state_active": {"linked": True,
                                            "top_frames": 3}}), "PASS?",
    "STRUCTURAL probe: linked + real frames but no vocab -> is the "
    "four-witness arm silently skipped?")
mut("P12_idle_no_vocab", "pwtop_r88_probe",
    lambda l: l.update({"pt_state_idle": {"top_frames": 3}}), "PASS?",
    "STRUCTURAL probe: idle frames but no vocab -> silent pass?")


for mid, entry, fn, expect, note in MUT:
    for tag in ("A", "B"):
        m = load(tag)
        legs = m[entry]["legs"]
        ent = m[entry]
        pid = pid_of(ent)
        try:
            fn(legs, ent)
        except TypeError:
            fn(legs)
        fails, cb, _e, _l = run_verdict(
            entry, legs, ent, extra=pid_globals(pid))
        RESULT["mutations"].append({
            "id": mid, "run": tag, "entry": entry, "expect": expect,
            "note": note, "failures": fails,
            "coverage_blocked": cb,
            "as_designed": (expect == "RED" and bool(fails)) or
                           (expect.startswith("PASS") and not fails) or
                           (expect == "PASS+CB" and not fails and bool(cb)),
        })

# as-recorded re-derivation of pt_n3 is separately interesting
m = load("A")
fails, cb, _e, _l = run_verdict(
    "pwtop_r88_probe", m["pwtop_r88_probe"]["legs"],
    m["pwtop_r88_probe"],
    extra=pid_globals(pid_of(m["pwtop_r88_probe"])))
RESULT["pt_n3_as_recorded_rederive"] = {
    "failures": fails, "coverage_blocked": cb}

with open(os.path.join(HERE, "arm-replay.json"), "w") as f:
    json.dump(RESULT, f, indent=2, sort_keys=True)

print("block shas:")
for e, s in BLOCK_SHA.items():
    print(f"  {e}: {s}")
print("\nre-derivation (A/B green, dev red):")
for tag in ("A", "B", "dev"):
    for e in ENTRIES:
        r = RESULT["rederive"][tag][e]
        if r.get("absent"):
            print(f"  {tag} {e}: ABSENT")
            continue
        print(f"  {tag} {e}: receipt_failures={len(r['receipt_failures'] or [])}"
              f" rederived={r['rederived_failures'] if r['rederive_error'] else len(r['rederived_failures'])}"
              f" cb_receipt={r['receipt_coverage_blocked']} "
              f"cb_rederived={r['rederived_coverage_blocked']}"
              f" err={r['rederive_error']}")
print("\nmutations:")
bad = 0
for x in RESULT["mutations"]:
    flag = "OK " if x["as_designed"] else "!! "
    if not x["as_designed"]:
        bad += 1
    print(f"  {flag}{x['id']:28s} {x['run']} expect={x['expect']:8s} "
          f"fails={len(x['failures'])} cb={x['coverage_blocked']}")
print(f"\nnot-as-designed: {bad}/{len(RESULT['mutations'])}")
print("\npt_n3 as-recorded rederive:", RESULT["pt_n3_as_recorded_rederive"])
