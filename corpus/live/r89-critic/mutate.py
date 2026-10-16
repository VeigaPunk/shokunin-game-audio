#!/usr/bin/env python3
"""r89 critic: mutation battery.

Each mutation is applied to a deep copy of ONE committed receipt entry;
the verbatim committed verdict block for that entry is then exec'd and
the outcome classified:

  RED   = failures non-empty (the arm caught it)
  CB    = no failures but a new coverage_blocked entry (unmeasured,
          named — the deliberate "contention, not measurement" path)
  GREEN = neither (the arm did not catch the mutation)
  CRASH = the block raised (loud, but not a failure row)

Every mutation declares its DESIGNED outcome; the battery reports any
mutation that does not behave as designed. Two runs -> 2 evaluations
per mutation. Volatile-field controls are mutations that MUST stay
GREEN (proving the arms are not pinned to volatile text).
"""
import copy
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
COMMIT = "0d732989"
FIXTURE = "corpus/fixtures/measure_audio.py"
RUNS = ["20261016T074733533774Z", "20261016T074816877001Z"]
ENTRIES = ["pwprof_gate_r89_probe", "pwprof_oart_r89_probe",
           "pwprof_schema_r89_probe", "pwprof_xw_r89_probe"]

src = subprocess.run(["git", "show", f"{COMMIT}:{FIXTURE}"], cwd=ROOT,
                     capture_output=True, text=True).stdout
lines = src.splitlines(keepends=True)


def fn_name(key):
    return key.replace("_probe", "_entry")


def slice_verdict_block(entry_name):
    start = next(i for i, l in enumerate(lines)
                 if l.startswith(f"def {entry_name}()"))
    end = next(j for j in range(start + 1, len(lines))
               if lines[j].startswith("def "))
    body = lines[start:end]
    vm = next(k for k, l in enumerate(body)
              if l.strip() == "# ---------------- verdicts ----------------")
    tail = next(k for k in range(vm, len(body))
                if body[k].strip() == 'entry["legs"] = legs')
    return "".join(body[vm:tail])


BLOCKS = {e: slice_verdict_block(fn_name(e)) for e in ENTRIES}


def run_block(entry_key, entry):
    env = {"legs": entry["legs"], "entry": copy.deepcopy(entry),
           "failures": []}
    try:
        exec(compile("if True:\n" + BLOCKS[entry_key],
                     f"verdict-{entry_key}", "exec"), env)
    except Exception as exc:                       # loud crash path
        return "CRASH", [f"{type(exc).__name__}: {exc}"], None
    cb = env["entry"].get("coverage_blocked")
    return ("RED" if env["failures"] else
            "CB" if cb else "GREEN"), env["failures"], cb


def set_leg(mut, entry_key, leg, **kw):
    mut[entry_key]["legs"][leg].update(kw)


def del_key(mut, entry_key, leg, key):
    mut[entry_key]["legs"][leg].pop(key, None)


def set_stat(mut, entry_key, **kw):
    mut[entry_key]["legs"]["s_window"]["stats"].update(kw)


MUTATIONS = []


def M(name, entry_key, designed, fn):
    MUTATIONS.append((name, entry_key, designed, fn))


# ---------------------------------------------------------------- gate
G = "pwprof_gate_r89_probe"
M("g_own.rc", G, "RED", lambda m: set_leg(m, G, "g_own", exit_code=1))
M("g_own.term_ok", G, "RED", lambda m: set_leg(m, G, "g_own", term_ok=False))
M("g_own.n_info7", G, "RED", lambda m: set_leg(m, G, "g_own", n_info=7))
M("g_two.rc", G, "RED", lambda m: set_leg(m, G, "g_two", exit_code=1))
M("g_two.n_info3", G, "RED", lambda m: set_leg(m, G, "g_two", n_info=3))
M("g_two.wall_s9", G, "RED", lambda m: set_leg(m, G, "g_two", wall_s=9.0))
M("g_two.term_ok", G, "RED", lambda m: set_leg(m, G, "g_two", term_ok=False))
M("g_term.rc-9", G, "RED", lambda m: set_leg(m, G, "g_term", exit_code=-9))
M("g_term.term_ok", G, "RED", lambda m: set_leg(m, G, "g_term", term_ok=False))
M("g_int.term_ok", G, "RED", lambda m: set_leg(m, G, "g_int", term_ok=False))
M("g_kill.rc-15", G, "RED", lambda m: set_leg(m, G, "g_kill", exit_code=-15))
M("g_kill.parse_ok", G, "RED",
  lambda m: set_leg(m, G, "g_kill", parse_error=None))
M("g_hup.rc-9", G, "RED", lambda m: set_leg(m, G, "g_hup", exit_code=-9))
M("g_usr1.rc-15", G, "RED", lambda m: set_leg(m, G, "g_usr1", exit_code=-15))
M("g_blocks.4095", G, "RED",
  lambda m: set_leg(m, G, "g_blocks",
                    stream_samples=[{"t": 0.3, "bytes": 4095}]))
M("g_blocks.all_zero", G, "RED",
  lambda m: set_leg(m, G, "g_blocks",
                    stream_samples=[{"t": 0.3, "bytes": 0},
                                    {"t": 0.6, "bytes": 0}]))
M("g_o_ignored.created", G, "RED",
  lambda m: set_leg(m, G, "g_o_ignored", file_created=True))
M("g_o_ignored.logging", G, "RED",
  lambda m: set_leg(m, G, "g_o_ignored", stderr="Logging to art\n"))
M("g_extra.n_info3", G, "RED", lambda m: set_leg(m, G, "g_extra", n_info=3))
M("g_remote_empty.rc255", G, "RED",
  lambda m: set_leg(m, G, "g_remote_empty", exit_code=255))
M("g_remote_bogus.rc0", G, "RED",
  lambda m: set_leg(m, G, "g_remote_bogus", exit_code=0))
M("g_remote_bogus.noclass", G, "RED",
  lambda m: set_leg(m, G, "g_remote_bogus", error_class=None))
M("g_env_bogus.rc254", G, "RED",
  lambda m: set_leg(m, G, "g_env_bogus", exit_code=254))
M("g_opt_bogus.wrongclass", G, "RED",
  lambda m: set_leg(m, G, "g_opt_bogus",
                    error_class="pwprof_connect_down"))
M("g_version.nolib", G, "RED",
  lambda m: set_leg(m, G, "g_version", stdout="pw-profiler\n"))
M("g_lastwins.notalive", G, "RED",
  lambda m: set_leg(m, G, "g_lastwins", alive_at_sig=False))
M("g_lastwins.n_info4", G, "RED",
  lambda m: set_leg(m, G, "g_lastwins", n_info=4))
M("n_007.n_info8", G, "RED", lambda m: set_leg(m, G, "n_007", n_info=8))
M("n_007.alive", G, "RED",
  lambda m: set_leg(m, G, "n_007", alive_at_sig=True))
M("n_plus3.rc255", G, "RED", lambda m: set_leg(m, G, "n_plus3", exit_code=255))
M("n_space3.n_info4", G, "RED", lambda m: set_leg(m, G, "n_space3", n_info=4))
M("n_2_5.exited", G, "RED",
  lambda m: set_leg(m, G, "n_2_5", alive_at_sig=False))
M("n_3abc.alive_none", G, "RED",
  lambda m: set_leg(m, G, "n_3abc", alive_at_sig=None))
M("n_1e1.n_info4", G, "RED", lambda m: set_leg(m, G, "n_1e1", n_info=4))
M("n_huge.rc-9", G, "RED", lambda m: set_leg(m, G, "n_huge", exit_code=-9))
M("n_neg.n_infoNone", G, "RED", lambda m: set_leg(m, G, "n_neg", n_info=None))
M("n_abc.exited", G, "RED",
  lambda m: set_leg(m, G, "n_abc", alive_at_sig=False))
M("n_zero.exited", G, "RED",
  lambda m: set_leg(m, G, "n_zero", alive_at_sig=False))
M("g_link.unlinked", G, "CB",
  lambda m: set_leg(m, G, "g_link", player=False))
M("g_own.leg_removed", G, "CRASH",
  lambda m: m[G]["legs"].pop("g_own"))

# ---------------------------------------------------------------- oart
O = "pwprof_oart_r89_probe"
M("o_live.rows9", O, "RED", lambda m: set_leg(m, O, "o_live", rows=9))
M("o_live.aux_missing", O, "RED",
  lambda m: set_leg(m, O, "o_live",
                    aux_present=["Timings.html", "generate_timings.sh",
                                 "art"]))
M("o_live.no_logging", O, "RED",
  lambda m: set_leg(m, O, "o_live", stderr="x\n"))
M("o_live.no_gentimings", O, "RED",
  lambda m: set_leg(m, O, "o_live", stdout="written\n"))
M("o_live.rc1", O, "RED", lambda m: set_leg(m, O, "o_live", exit_code=1))
M("o_int.bytes0", O, "RED", lambda m: set_leg(m, O, "o_int", bytes=0))
M("o_int.rc1", O, "RED", lambda m: set_leg(m, O, "o_int", exit_code=1))
M("o_kill.bytes0", O, "RED", lambda m: set_leg(m, O, "o_kill", bytes=0))
M("o_kill.rows0", O, "RED", lambda m: set_leg(m, O, "o_kill", rows=0))
M("o_kill.rc-15", O, "RED", lambda m: set_leg(m, O, "o_kill", exit_code=-15))
M("o_exist.marker_survived", O, "RED",
  lambda m: set_leg(m, O, "o_exist", marker_gone=False))
M("o_eager.never", O, "RED",
  lambda m: set_leg(m, O, "o_eager", watch_seen=None))
M("o_default.empty", O, "RED",
  lambda m: set_leg(m, O, "o_default", profiler_log=0))
M("o_dash.none", O, "RED", lambda m: set_leg(m, O, "o_dash", dash_file=None))
M("o_devnull.aux_missing", O, "RED",
  lambda m: set_leg(m, O, "o_devnull", aux_present=["Timings.html"]))
M("o_dir.rc0", O, "RED", lambda m: set_leg(m, O, "o_dir", exit_code=0))
M("o_empty.noclass", O, "RED",
  lambda m: set_leg(m, O, "o_empty", error_class=None))
M("o_proc.wrongclass", O, "RED",
  lambda m: set_leg(m, O, "o_proc", error_class="pwprof_opt"))
M("o_link.unlinked", O, "CB",
  lambda m: set_leg(m, O, "o_link", player=False))

# -------------------------------------------------------------- schema
S = "pwprof_schema_r89_probe"
M("s_window.rc1", S, "RED",
  lambda m: set_leg(m, S, "s_window", exit_code=1))
M("s_window.parse_err", S, "RED",
  lambda m: set_leg(m, S, "s_window", parse_error="boom"))
M("s_window.starved", S, "RED",
  lambda m: set_leg(m, S, "s_window", stats={"own_blocks": 2}))
M("s_window.seq_order", S, "RED",
  lambda m: set_stat(m, S, seq_order_ok=False))
M("s_window.count_step", S, "RED",
  lambda m: set_stat(m, S, count_step_ok=False))
M("s_window.quantum", S, "RED",
  lambda m: set_stat(m, S, quantum_relation_ok=False))
M("s_window.pos_step", S, "RED",
  lambda m: set_stat(m, S, pos_step_ok=False))
M("s_window.transport", S, "RED",
  lambda m: set_stat(m, S, transports=["running"]))
M("s_window.diff", S, "RED", lambda m: set_stat(m, S, diffs=[0.999]))
M("s_window.order", S, "RED", lambda m: set_stat(m, S, order_ok=False))
M("s_window.prev_chain", S, "RED",
  lambda m: set_stat(m, S, prev_is_last_signal=False))
M("s_window.status", S, "RED",
  lambda m: set_stat(m, S, driver_statuses=["triggered"]))
M("s_window.latency", S, "RED",
  lambda m: set_stat(m, S, driver_latencies=["0/1024"]))
M("s_window.clock_id", S, "RED",
  lambda m: set_stat(m, S, clock_ids=[999999]))
M("s_window.driver_id", S, "RED",
  lambda m: set_stat(m, S, driver_ids=[999999]))
M("s_window.clock_name", S, "RED",
  lambda m: set_stat(m, S, clock_names=["clock.system.realtime"]))
M("s_window.nsec_window", S, "RED",
  lambda m: set_stat(m, S, nsec_in_window=False))
M("s_window.xrun", S, "RED", lambda m: set_stat(m, S, xruns=[3]))
M("s_window.xrun_count", S, "RED",
  lambda m: set_stat(m, S, xrun_counts=[1]))
M("s_window.fclock", S, "RED", lambda m: set_stat(m, S, fclock_rows=2))
M("s_window.nsb", S, "RED", lambda m: set_stat(m, S, nsb_blocks=3))
M("s_window.unmeasured_stat", S, "RED",
  lambda m: set_stat(m, S, seq_order_ok=None))
M("s_window.refs_none", S, "RED",
  lambda m: m[S].update(refs={"own_node_id": None}))
M("s_window.stats_missing", S, "RED",
  lambda m: m[S]["legs"]["s_window"].pop("stats"))
M("s_second.empty", S, "RED",
  lambda m: set_leg(m, S, "s_second", own_counts=[]))
M("s_second.equal", S, "RED",
  lambda m: set_leg(m, S, "s_second", own_counts=[39]))
M("s_second.regress", S, "RED",
  lambda m: set_leg(m, S, "s_second", own_counts=[38]))
M("s_suspend.nohook", S, "RED",
  lambda m: set_leg(m, S, "s_suspend", kill_mono=None))
M("s_suspend.vacuous_pre", S, "RED",
  lambda m: set_leg(m, S, "s_suspend", own_pre_kill=0))
M("s_suspend.after5", S, "RED",
  lambda m: set_leg(m, S, "s_suspend", own_after_kill=5))
M("s_link.unlinked", S, "CB",
  lambda m: set_leg(m, S, "s_link", player=False))

# ------------------------------------------------------------------ xw
X = "pwprof_xw_r89_probe"
M("x_modreg.in_dump", X, "RED",
  lambda m: set_leg(m, X, "x_modreg", own_in_dump_modules=True))
M("x_modreg.node_absent", X, "RED",
  lambda m: set_leg(m, X, "x_modreg", own_node_in_dump=False))
M("x_modreg.not_added", X, "RED",
  lambda m: set_leg(m, X, "x_modreg", pactl_added=["536870999"]))
M("x_blank.no_blank", X, "RED",
  lambda m: set_leg(m, X, "x_blank", blank_lines=[]))
M("x_blank.unfound", X, "RED",
  lambda m: set_leg(m, X, "x_blank", own_found=None))
M("x_foot.two_clients", X, "RED",
  lambda m: set_leg(m, X, "x_foot", pwprof_during=2))
M("x_foot.node_delta", X, "RED",
  lambda m: set_leg(m, X, "x_foot", nodes_delta=1))
M("x_conc.rc1", X, "RED", lambda m: set_leg(m, X, "x_conc", rc1=1))
M("x_conc.parse1", X, "RED",
  lambda m: set_leg(m, X, "x_conc", parse1="Unterminated string"))
M("x_conc.zero_overlap", X, "CB",
  lambda m: set_leg(m, X, "x_conc", shared=0))
M("x_conc.divergent", X, "RED",
  lambda m: set_leg(m, X, "x_conc", shared_identical=False))
M("x_top.no_row", X, "CB", lambda m: set_leg(m, X, "x_top", own_row=None))
M("x_top.ratio_off", X, "RED",
  lambda m: set_leg(m, X, "x_top", own_row={
      "status": "R", "id": 1, "quant": 2048, "rate": 48000,
      "wait": "100.0us", "busy": "0.9us", "wait_us": 100.0,
      "busy_us": 0.9}))
M("x_top.partial", X, "CB",
  lambda m: set_leg(m, X, "x_top", prof_wait_us_med=None))
M("x_profobj.no_ids", X, "CB",
  lambda m: set_leg(m, X, "x_profobj", ids=[]))
M("x_profobj.info_rc1", X, "RED",
  lambda m: m[X]["legs"]["x_profobj"]["info"].update(exit_code=1))
M("x_profobj.info_notext", X, "RED",
  lambda m: m[X]["legs"]["x_profobj"]["info"].update(stderr="Error: x\n"))
M("x_profobj.enum_rc255", X, "RED",
  lambda m: m[X]["legs"]["x_profobj"]["enum"].update(exit_code=255))
M("x_sigpipe.rc0", X, "RED", lambda m: set_leg(m, X, "x_sigpipe", rc=0))
M("x_devfull.rc1", X, "RED", lambda m: set_leg(m, X, "x_devfull", rc=1))
M("x_devfull.stderr", X, "RED",
  lambda m: set_leg(m, X, "x_devfull", stderr_bytes=5))
M("x_link.unlinked", X, "CB",
  lambda m: set_leg(m, X, "x_link", player=False))

# ------------------------------------------------- controls (stay GREEN)
M("C1.wall_s", G, "GREEN", lambda m: [
    set_leg(m, G, k, wall_s=99.0) for k in m[G]["legs"]
    if k != "g_two"])          # g_two.wall_s IS armed (its own mutation)
M("C1b.g_two_wall_armed", G, "RED",
  lambda m: set_leg(m, G, "g_two", wall_s=1.6))
M("C2.stdout_bytes", G, "GREEN", lambda m: [
    set_leg(m, G, k, stdout_bytes=123456) for k in m[G]["legs"]])
M("C3.loadavg", G, "GREEN",
  lambda m: m[G].update(loadavg=["999.0", "999.0", "999.0"]))
M("C4.unloads", G, "GREEN",
  lambda m: m[G].update(unloads={"r89a_ns_1": {
      "verified_index": 999, "captured": 999, "exit_code": 7}}))
M("C5.driver_names", G, "GREEN",
  lambda m: set_leg(m, G, "g_own", drivers=["foreign_driver"]))
M("C6.two_hist", G, "GREEN",
  lambda m: set_leg(m, G, "g_two", driver_info_hist=[["other", 4]]))
M("C7.schema_volatiles", S, "GREEN", lambda m: set_stat(
    m, S, driver_names=["x"], follower_names=["y"],
    own_counts=[7, 8, 9], durations=[1024], rates=["1/44100"],
    block_types=["info"], statuses=["awake"],
    follower_latencies=["1/2"], wait_us_range=[1, 2],
    busy_us_range=[1, 2], cpu_load_sorted_desc=True,
    own_seq_shapes=[["info", "clock", "driver"]]))
M("C8.schema_text", S, "GREEN",
  lambda m: set_leg(m, S, "s_window", stdout="<ns>", stderr="<ns>"))
M("C9.suspend_foreign", S, "GREEN",
  lambda m: set_leg(m, S, "s_suspend", foreign_after_kill=7, own_blocks=21))
M("C10.conc_bytes", X, "GREEN",
  lambda m: set_leg(m, X, "x_conc", bytes1=1, bytes2=2,
                    byte_identical=False))
M("C11.top_meta", X, "GREEN",
  lambda m: set_leg(m, X, "x_top", frames=9, top_rc=255, prof_own_blocks=1))
M("C12.foot_meta", X, "GREEN",
  lambda m: set_leg(m, X, "x_foot", clients_added=["other"], rc=1))
M("C13.modreg_meta", X, "GREEN",
  lambda m: set_leg(m, X, "x_modreg", dump_module_count=99,
                    pactl_added=["536870922", "536870999"]))
M("C14.refs_consistent", S, "GREEN", lambda m: (
    m[S].update(refs={"own_node_id": 4242}),
    set_stat(m, S, clock_ids=[4242], driver_ids=[4242])))

battery = {"commit": COMMIT, "mutations": [], "evaluations": 0}
mismatches = []
for run in RUNS:
    rec = json.loads((ROOT / "corpus/live/runs" /
                      f"{run}-pwprof-r89/measurements.json").read_text())
    for name, entry_key, designed, fn in MUTATIONS:
        mut = copy.deepcopy(rec["measurements"])
        fn(mut)
        got, fails, cb = run_block(entry_key, mut[entry_key])
        battery["evaluations"] += 1
        ok = (got == designed)
        battery["mutations"].append(
            {"run": run, "name": name, "entry": entry_key,
             "designed": designed, "got": got, "as_designed": ok,
             "failures": fails[:2],
             "coverage_blocked": (cb[-1] if cb else None)})
        if not ok:
            mismatches.append((run, name, designed, got, fails[:1]))

(OUT / "mutations.json").write_text(json.dumps(battery, indent=2) + "\n")
print(f"mutations={len(MUTATIONS)} evals={battery['evaluations']} "
      f"mismatches={len(mismatches)}")
for mm in mismatches:
    print("  MISMATCH", mm)
by_design = {}
for m in battery["mutations"]:
    by_design.setdefault(m["designed"], [0, 0])
    by_design[m["designed"]][0] += 1
    by_design[m["designed"]][1] += 1 if m["as_designed"] else 0
print("by designed outcome (evals, as-designed):", by_design)
