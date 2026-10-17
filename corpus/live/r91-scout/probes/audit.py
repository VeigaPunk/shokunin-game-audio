#!/usr/bin/env python3
"""r91 scout audit: consolidate per-leg receipts into summary.json, RECEIPTS.md
and manifest.sha256.  Reads only files under corpus/live/r91-scout/."""
import glob
import hashlib
import json
import os

SCRATCH = "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r91-scout"
RUNS = os.path.join(SCRATCH, "runs")
RECEIPTS = os.path.join(SCRATCH, "receipts")

KEY_PROPS = ["node.name", "media.class", "node.dont-reconnect", "node.dont-fallback",
             "stream.capture.sink", "target.object", "node.target", "node.autoconnect",
             "node.linger", "application.name"]


def load(p):
    with open(p) as f:
        return json.load(f)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_state(info_head):
    for line in (info_head or "").splitlines():
        if "state:" in line:
            return line.split("state:")[1].strip().strip('"')
    return None


def link_blocks(link_lines):
    """Group flat kept lines into blocks {src_port: [...dest lines]}."""
    blocks = {}
    cur = None
    for line in link_lines:
        if line.startswith(" ") and cur:
            blocks[cur].append(line.strip())
        else:
            cur = line
            blocks.setdefault(cur, [])
    return blocks


def main():
    summary = {"host": "plazir27", "scratch": SCRATCH}

    # ---- prop lattice
    lattice = {}
    for leg_dir in sorted(glob.glob(os.path.join(RUNS, "props", "*"))):
        rec = load(os.path.join(leg_dir, "receipt.json"))
        n = rec.get("node") or {}
        p = n.get("props") or {}
        row = {k: p.get(k) for k in KEY_PROPS}
        row["state"] = n.get("state")
        lattice.setdefault(rec["family"], []).append(row)
    summary["prop_lattice"] = {
        fam: {"rows": rows,
              "stable": all(r == rows[0] for r in rows),
              "n_reps": len(rows)}
        for fam, rows in lattice.items()
    }

    # ---- loss ladder
    loss = {}
    for leg_dir in sorted(glob.glob(os.path.join(RUNS, "loss", "*"))):
        rec = load(os.path.join(leg_dir, "receipt.json"))
        run = rec["run"]
        unload_t = run.get("unload_t")
        tl = run["timeline"]
        sizes = [(s["t"], s.get("file_bytes")) for s in tl if s.get("file_bytes") is not None]
        pre = [x[1] for x in sizes if unload_t is not None and x[0] < unload_t]
        post = [x[1] for x in sizes if unload_t is not None and x[0] >= unload_t + 0.3]
        states = []
        for s in tl:
            st = parse_state(s.get("info_head"))
            if st and (not states or states[-1][1] != st):
                states.append([s["t"], st])
        post_blocks = {}
        for s in tl:
            if unload_t is not None and s["t"] >= unload_t + 0.3:
                for src, dests in link_blocks(s.get("links_relevant") or []).items():
                    post_blocks.setdefault(src, set()).update(dests)
        entry = {
            "family": rec["family"], "rep": rec["rep"],
            "node_props_at_connect": {k: (rec.get("node_props_at_connect") or {}).get(k)
                                      for k in KEY_PROPS},
            "pre_loss_growth": (max(pre) > min(pre)) if pre else None,
            "post_loss_frozen": (max(post) == min(post)) if post else None,
            "final_bytes": rec.get("final_bytes"),
            "size_at_loss_window": [x[1] for x in sizes if unload_t and unload_t - 0.1 <= x[0] <= unload_t + 0.2][:3],
            "state_seq": states,
            "post_loss_link_sources": {k: sorted(v) for k, v in post_blocks.items()},
            "unload_ok": (run.get("unload_result") or {}).get("ok"),
            "rc": run.get("rc"), "killed": run.get("killed"),
            "tone_state": rec.get("tone_state"), "src_state": rec.get("src_state"),
        }
        loss.setdefault(rec["family"], []).append(entry)
    summary["loss_ladder"] = loss

    # ---- recover discriminator
    recov = []
    for leg_dir in sorted(glob.glob(os.path.join(RUNS, "recover", "*"))):
        rec = load(os.path.join(leg_dir, "receipt.json"))
        run = rec["run"]
        unload_t = run.get("unload_t")
        manual_t = rec.get("manual_t")
        tl = run["timeline"]
        sizes = [(s["t"], s.get("file_bytes")) for s in tl if s.get("file_bytes") is not None]
        before = [x[1] for x in sizes if unload_t and manual_t and unload_t + 0.3 <= x[0] <= manual_t]
        after = [x[1] for x in sizes if manual_t and x[0] >= manual_t + 0.3]
        manual_links = {}
        for s in tl:
            if manual_t and s["t"] >= manual_t:
                for src, dests in link_blocks(s.get("links_relevant") or []).items():
                    manual_links.setdefault(src, set()).update(dests)
        states = []
        for s in tl:
            st = parse_state(s.get("info_head"))
            if st and (not states or states[-1][1] != st):
                states.append([s["t"], st])
        recov.append({
            "rep": rec["rep"], "manual_t": manual_t,
            "tone_state": rec.get("tone_state"),
            "frozen_before_manual": (max(before) == min(before)) if before else None,
            "resumed_after_manual": (after[-1] > after[0]) if after else None,
            "bytes_before": before[:2] + before[-2:] if before else None,
            "bytes_after": after[:2] + after[-2:] if after else None,
            "manual_link_blocks": {k: sorted(v) for k, v in manual_links.items()},
            "state_seq": states,
            "linkinfo_capture": rec.get("linkinfo"),
            "rc": run.get("rc"), "killed": run.get("killed"),
        })
    summary["recover_discriminator"] = recov

    # ---- census exit
    for tag in ("entry", "exit", "props-entry", "props-exit", "loss-entry", "loss-exit",
                "recover-inloop-entry", "recover-inloop-exit"):
        p = os.path.join(RECEIPTS, f"census-{tag}.json")
        if os.path.exists(p):
            c = load(p)
            summary.setdefault("census", {})[tag] = {
                "default_sink": c["default_sink"]["stdout"].strip(),
                "default_source": c["default_source"]["stdout"].strip(),
                "modules": len(c["modules_short"]["stdout"].splitlines()),
                "pw_dump_objects": c["pw_dump_objects"],
                "r91_residue": c["r91_residue"],
            }

    with open(os.path.join(RECEIPTS, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)

    # ---- manifest
    files = []
    for pat in ("probes/*", "receipts/*.json", "sources/*"):
        files.extend(sorted(glob.glob(os.path.join(SCRATCH, pat))))
    for leg_dir in sorted(glob.glob(os.path.join(RUNS, "*", "*"))):
        for name in ("receipt.json", "combined.log", "tone.log"):
            p = os.path.join(leg_dir, name)
            if os.path.exists(p):
                files.append(p)
    lines = []
    for p in sorted(set(files)):
        if not os.path.isfile(p):
            continue
        lines.append(f"{sha256_file(p)}  {os.path.relpath(p, SCRATCH)}")
    with open(os.path.join(SCRATCH, "manifest.sha256"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"manifest: {len(lines)} files")

    # ---- RECEIPTS.md
    md = []
    md.append("# r91-scout RECEIPTS\n")
    md.append("Scratch root: `corpus/live/r91-scout/` (untracked). Host `plazir27`, "
              "2026-10-15 (UTC window ~17:0x-17:2x).\n")
    md.append("## Consolidated receipts\n")
    md.append("| artifact | content |\n| --- | --- |")
    md.append("| `receipts/props.json` | live prop lattice, 5 client families x 3 reps |")
    md.append("| `receipts/loss.json` | target-loss timeline, 4 families x 3 reps |")
    md.append("| `receipts/recover-inloop.json` | manual-relink discriminator x 3 reps |")
    md.append("| `receipts/summary.json` | audit roll-up (this file's source) |")
    md.append("| `receipts/census-*.json` | entry/exit censuses (modules, defaults, dump size, residue) |")
    md.append("| `sources/*.c`, `sources/SOURCES.sha256`, `sources/WP-LUA.sha256` | version-matched upstream sources + on-host Lua shas |")
    md.append("| `probes/driver.py`, `probes/diag_src*.py` | harnesses (all legs triple-bounded) |")
    md.append("| `runs/<stage>/<leg>/receipt.json` | per-leg raw receipt (argv, rc, timeline) |")
    md.append("\n## Key numbers\n")
    for fam, rows in summary["prop_lattice"].items():
        r0 = rows["rows"][0]
        md.append(f"- `{fam}`: stable={rows['stable']} x{rows['n_reps']}; "
                  f"state={r0['state']}; node.dont-reconnect={r0['node.dont-reconnect']!r}; "
                  f"stream.capture.sink={r0['stream.capture.sink']!r}")
    for fam, rows in summary["loss_ladder"].items():
        r0 = rows[0]
        md.append(f"- loss `{fam}`: frozen={[r['post_loss_frozen'] for r in rows]}; "
                  f"final={[r['final_bytes'] for r in rows]}; "
                  f"states={[r['state_seq'] for r in rows][:1]}")
    for r in summary["recover_discriminator"]:
        md.append(f"- recover r{r['rep']}: frozen_before={r['frozen_before_manual']} "
                  f"resumed_after={r['resumed_after_manual']} "
                  f"manual_links={list(r['manual_link_blocks'].keys())[:3]}")
    md.append("\n## Manifest\n")
    md.append(f"`manifest.sha256` covers {len(lines)} files (probes, receipts, sources, "
              "per-leg receipts/logs). Report at `reports/round-91/r91-scout.md` is outside "
              "the scratch tree and is not in this manifest.\n")
    with open(os.path.join(SCRATCH, "RECEIPTS.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print("RECEIPTS.md written")


if __name__ == "__main__":
    main()
