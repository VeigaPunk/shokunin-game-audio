#!/usr/bin/env python3
"""Apply the r79 simplifier fold batch to a scratch copy of measure_audio.py.

Every fold is (old, new, expected_occurrences). The script asserts each
occurrence count before replacing, so a drifted tree fails loudly instead of
half-applying. Run against corpus/live/r79-simplifier/cand/... only.

    python3 apply_fold.py corpus/live/r79-simplifier/cand/corpus/fixtures/measure_audio.py
"""
import sys
from pathlib import Path

FOLDS = [
    # ---------------- F1: dead constant (0 references outside its def) ----
    ("F1", "LOOPBACK_R79_TIMEOUT_S = CONSUMER_R73_TIMEOUT_S\n", "", 1),
    # ---------------- F2: dead local `line` (r79 never emits it) ----------
    ("F2",
     "    err = proc.stderr.read().decode(errors=\"replace\")\n"
     "    cls, line = _playback_r78_errclass(err)\n"
     "    shown = \" \".join(argv)\n",
     "    err = proc.stderr.read().decode(errors=\"replace\")\n"
     "    cls, _ = _playback_r78_errclass(err)\n"
     "    shown = \" \".join(argv)\n",
     1),
    # ---------------- F3: unload iterates values, not (unused) keys -------
    ("F3",
     "    for nm, leaf in loads.items():\n"
     "        _playback_r78_unload(leaf.get(\"module_id\"))\n",
     "    for leaf in loads.values():\n"
     "        _playback_r78_unload(leaf.get(\"module_id\"))\n",
     1),
    # ---------------- F4: capture lattice tap_t ternary, both arms ns_b ---
    ("F4",
     "                tap_t = ns_b if kind != \"none\" else ns_b\n"
     "                legs[name] = _loopback_r79_leg(\n"
     "                    name, tail + [\"-P\", ns_b] if \"-P\" not in tail\n"
     "                    else tail, ctx,\n"
     "                    feed_sink=ns_a if feed else None,\n"
     "                    tap_target=tap_t,\n",
     "                legs[name] = _loopback_r79_leg(\n"
     "                    name, tail + [\"-P\", ns_b] if \"-P\" not in tail\n"
     "                    else tail, ctx,\n"
     "                    feed_sink=ns_a if feed else None,\n"
     "                    tap_target=ns_b,\n",
     1),
    # ---------------- F5: dead `s0 is None` conjunct (s0 truthy here) -----
    ("F5",
     "                if \"@SRC@\" in tail and nondef is None and s0 is None:\n",
     "                if \"@SRC@\" in tail and nondef is None:\n",
     1),
    # ---------------- F6: dead `extra_tw` binding ------------------------
    ("F6",
     "                # c07's content control needs a second tap on the flag\n"
     "                # sink — bound+ran in the witness list, silent on `mine`.\n"
     "                extra_tw = []\n"
     "                if name == \"c07_prop_beats_flag\":\n"
     "                    extra_tw = [(\"c07_flag_sink_tap\", ns_b)]\n",
     "                # c07's content control needs a second tap on the flag\n"
     "                # sink — bound+ran in the witness list, silent on `mine`.\n",
     1),
    # ---------------- F7: matrix entry's unused inventory call ------------
    ("F7",
     "    failures = []\n"
     "    inv = _capture_inventory()\n"
     "    ora0 = _loopback_r79_oracle()\n"
     "    entry = {\"probe\": \"pw-loopback channel matrix — audio.position \"\n",
     "    failures = []\n"
     "    ora0 = _loopback_r79_oracle()\n"
     "    entry = {\"probe\": \"pw-loopback channel matrix — audio.position \"\n",
     1),
    # ---------------- F8: filter-chain entry's unused inventory call ------
    ("F8",
     "    failures = []\n"
     "    inv = _capture_inventory()\n"
     "    ora0 = _loopback_r79_oracle()\n"
     "    entry = {\"probe\": \"filter-chain module — client-scoped conf.d/pw-cli \"\n",
     "    failures = []\n"
     "    ora0 = _loopback_r79_oracle()\n"
     "    entry = {\"probe\": \"filter-chain module — client-scoped conf.d/pw-cli \"\n",
     1),
    # ---------------- F9: filter-chain entry's dead ctx dict --------------
    ("F9",
     "            _playback_r78_write_tone(tone, LOOPBACK_R79_TONE_S)\n"
     "            ctx = {\"tmp\": tmp, \"tone\": tone,\n"
     "                   \"bound_s\": LOOPBACK_R79_HP_BOUND_S,\n"
     "                   \"own_sinks\": {fc}, \"redact\": [fc],\n"
     "                   \"default_at_start\": ora0[\"sink_meta\"] or\n"
     "                   ora0[\"sink_pactl\"],\n"
     "                   \"source_at_start\": ora0[\"source_meta\"] or\n"
     "                   ora0[\"source_pactl\"]}\n"
     "\n"
     "            def mkcfg(legname, fragments):\n",
     "            _playback_r78_write_tone(tone, LOOPBACK_R79_TONE_S)\n"
     "\n"
     "            def mkcfg(legname, fragments):\n",
     1),
    # ---------------- F10: f3 verdict loop's unused tuple field -----------
    ("F10",
     "    for name, want_node in ((\"f3_good_then_bad\", True),\n"
     "                            (\"f3b_bad_then_good\", True)):\n",
     "    for name in (\"f3_good_then_bad\", \"f3b_bad_then_good\"):\n",
     1),
    # ---------------- F11: hotplug e1's unused ltag binding ---------------
    ("F11",
     "        ltag, out_n = e1[\"ltag\"], f\"output.{e1['ltag']}\"\n",
     "        out_n = f\"output.{e1['ltag']}\"\n",
     1),
    # ---------------- F12: record verdict loop re-declares RECS -----------
    ("F12",
     "    for name, target, capprop, (kind, *karg) in (\n"
     "            (\"d2a_input_node\", in_n, False, (\"source\",)),\n"
     "            (\"d2b_output_node\", out_n, False, (\"node\", out_n)),\n"
     "            (\"d2c_input_capsink\", in_n, True, (\"node\", in_n)),\n"
     "            (\"d2d_output_capsink\", out_n, True, (\"dsink\",))):\n",
     "    for name, target, capprop, (kind, *karg) in RECS:\n",
     1),
    # ---------------- F13: check_tap's vacuous require parameter ----------
    ("F13a",
     "def _loopback_r79_check_tap(entry, failures, lname, leg, *,\n"
     "                            want_tone=None, require=True):\n",
     "def _loopback_r79_check_tap(entry, failures, lname, leg, *,\n"
     "                            want_tone=None):\n",
     1),
    ("F13b",
     "    tap = leg.get(\"tap\") or {}\n"
     "    if not tap:\n"
     "        if require:\n"
     "            failures.append(f\"{lname}: no tap recorded — the content \"\n"
     "                            \"pin is absent\")\n"
     "        return\n",
     "    tap = leg.get(\"tap\") or {}\n"
     "    if not tap:\n"
     "        failures.append(f\"{lname}: no tap recorded — the content \"\n"
     "                        \"pin is absent\")\n"
     "        return\n",
     1),
    # ---------------- F14: leg unions single-sourced on the helper --------
    ("F14",
     "            \"input_producers_union\": sorted(\n"
     "                {n for s in run[\"samples\"]\n"
     "                 for n in (s[\"watch\"].get(f\"input.{ltag}\") or {})\n"
     "                 .get(\"producers\") or []}),\n"
     "            \"output_consumers_union\": sorted(\n"
     "                {n for s in run[\"samples\"]\n"
     "                 for n in (s[\"watch\"].get(f\"output.{ltag}\") or {})\n"
     "                 .get(\"consumers\") or []})}\n",
     "            \"input_producers_union\": _loopback_r79_union(\n"
     "                run[\"samples\"], f\"input.{ltag}\", \"producers\"),\n"
     "            \"output_consumers_union\": _loopback_r79_union(\n"
     "                run[\"samples\"], f\"output.{ltag}\", \"consumers\")}\n",
     1),
    # ---------------- F15: stale 'byte-identical Latency param' doc ------
    ("F15a",
     "#   PWCAT LATENCY. --latency/-P node.latency store the prop VERBATIM\n"
     "#     (prop beats flag); the reported Latency param is byte-identical on\n"
     "#     every leg — intent, not a negotiated param. stream.capture.sink on\n"
     "#     a playback stream is recorded decoration.\n",
     "#   PWCAT LATENCY. --latency/-P node.latency store the prop VERBATIM\n"
     "#     (prop beats flag); the reported Latency param is RECORDED as a\n"
     "#     named verdict, never asserted (r78 measured one value, r79 run 2\n"
     "#     measured three that track the request) — the prop is the hard\n"
     "#     pin. stream.capture.sink on a playback stream is decoration.\n",
     1),
    ("F15b",
     "    is stored unvalidated); the reported Latency param is byte-identical\n"
     "    on every leg — intent, never a negotiated param; and\n"
     "    stream.capture.sink on a PLAYBACK stream is decoration.\"\"\"\n",
     "    is stored unvalidated); the reported Latency param is RECORDED as\n"
     "    a named verdict, never asserted — the prop is the hard pin; and\n"
     "    stream.capture.sink on a PLAYBACK stream is decoration.\"\"\"\n",
     1),
    # ---------------- F16: one named coverage-block helper ----------------
    ("F16a",
     "    rest = _loopback_r79_own_nodes()\n"
     "    entry[\"own_nodes_after\"] = rest\n"
     "    if rest:\n"
     "        failures.append(f\"teardown: r79-tagged nodes survived: {rest}\")\n"
     "\n"
     "\n",
     "    rest = _loopback_r79_own_nodes()\n"
     "    entry[\"own_nodes_after\"] = rest\n"
     "    if rest:\n"
     "        failures.append(f\"teardown: r79-tagged nodes survived: {rest}\")\n"
     "\n"
     "\n"
     "def _loopback_r79_block(entry, failures, msg, loads=None):\n"
     "    \"\"\"The named coverage block every entry shares: record it, unload\n"
     "    anything this entry loaded, and return the entry — a blocked leg is\n"
     "    named coverage, never a silent pass.\"\"\"\n"
     "    entry[\"blocked\"] = msg\n"
     "    entry[\"coverage_blocked\"] = [msg]\n"
     "    if loads is not None:\n"
     "        _loopback_r79_sinks_unload(loads)\n"
     "    entry[\"failures\"] = failures\n"
     "    return entry\n"
     "\n"
     "\n",
     1),
    ("F16b",
     "    if not d0 or not s0:\n"
     "        entry[\"blocked\"] = \"no default sink/source authority readable\"\n"
     "        entry[\"coverage_blocked\"] = [entry[\"blocked\"]]\n"
     "        entry[\"failures\"] = failures\n"
     "        return entry\n",
     "    if not d0 or not s0:\n"
     "        return _loopback_r79_block(\n"
     "            entry, failures, \"no default sink/source authority readable\")\n",
     3),
    ("F16c",
     "    if not d0:\n"
     "        entry[\"blocked\"] = \"no default sink authority readable\"\n"
     "        entry[\"coverage_blocked\"] = [entry[\"blocked\"]]\n"
     "        entry[\"failures\"] = failures\n"
     "        return entry\n",
     "    if not d0:\n"
     "        return _loopback_r79_block(\n"
     "            entry, failures, \"no default sink authority readable\")\n",
     3),
    ("F16d",
     "    if not all(l.get(\"monitor_seen\") for l in loads.values()):\n"
     "        entry[\"blocked\"] = \"a probe null sink/monitor did not enumerate\"\n"
     "        entry[\"coverage_blocked\"] = [entry[\"blocked\"]]\n"
     "        _loopback_r79_sinks_unload(loads)\n"
     "        entry[\"failures\"] = failures\n"
     "        return entry\n",
     "    if not all(l.get(\"monitor_seen\") for l in loads.values()):\n"
     "        return _loopback_r79_block(\n"
     "            entry, failures,\n"
     "            \"a probe null sink/monitor did not enumerate\", loads)\n",
     6),
    ("F16e",
     "    if not all(l.get(\"monitor_seen\") for l in loads.values()):\n"
     "        entry[\"blocked\"] = \"the probe null sink/monitor did not enumerate\"\n"
     "        entry[\"coverage_blocked\"] = [entry[\"blocked\"]]\n"
     "        _loopback_r79_sinks_unload(loads)\n"
     "        entry[\"failures\"] = failures\n"
     "        return entry\n",
     "    if not all(l.get(\"monitor_seen\") for l in loads.values()):\n"
     "        return _loopback_r79_block(\n"
     "            entry, failures,\n"
     "            \"the probe null sink/monitor did not enumerate\", loads)\n",
     1),
    ("F16f",
     "    if not all(l.get(\"monitor_seen\") for l in loads.values()):\n"
     "        entry[\"blocked\"] = \"the fc null sink/monitor did not enumerate\"\n"
     "        entry[\"coverage_blocked\"] = [entry[\"blocked\"]]\n"
     "        _loopback_r79_sinks_unload(loads)\n"
     "        entry[\"failures\"] = failures\n"
     "        return entry\n",
     "    if not all(l.get(\"monitor_seen\") for l in loads.values()):\n"
     "        return _loopback_r79_block(\n"
     "            entry, failures,\n"
     "            \"the fc null sink/monitor did not enumerate\", loads)\n",
     1),
    ("F16g",
     "    if not Path(base).exists():\n"
     "        entry[\"blocked\"] = \"no shipped filter-chain.conf\"\n"
     "        entry[\"coverage_blocked\"] = [entry[\"blocked\"]]\n"
     "        _loopback_r79_sinks_unload(loads)\n"
     "        entry[\"failures\"] = failures\n"
     "        return entry\n",
     "    if not Path(base).exists():\n"
     "        return _loopback_r79_block(entry, failures,\n"
     "                                   \"no shipped filter-chain.conf\", loads)\n",
     1),
]


def main():
    path = Path(sys.argv[1])
    src = path.read_text()
    for tag, old, new, want in FOLDS:
        got = src.count(old)
        if got != want:
            raise SystemExit(f"{tag}: pattern occurs {got}x, expected {want}x")
        src = src.replace(old, new)
        print(f"{tag}: {want} replacement(s) ok")
    path.write_text(src)
    print(f"folded {len(FOLDS)} patterns -> {path}")


if __name__ == "__main__":
    main()
