#!/usr/bin/env bash
# snapshot foreign client/module/sink state; $1 = label
L="$1"
D="runs/${L}"
mkdir -p "$D"
date -u +%Y-%m-%dT%H:%M:%S.%NZ > "$D/timestamp.txt"
pactl list short modules > "$D/pactl-modules.txt" 2> "$D/pactl-modules.err"; echo "rc=$?" >> "$D/pactl-modules.err"
pactl list short sinks  > "$D/pactl-sinks.txt"   2>&1
pactl list short sources > "$D/pactl-sources.txt" 2>&1
pactl list short clients > "$D/pactl-clients.txt" 2>&1
pactl info > "$D/pactl-info.txt" 2>&1
pw-dump > "$D/pw-dump.json" 2> "$D/pw-dump.err"; echo "rc=$?" >> "$D/pw-dump.err"
python3 - "$D/pw-dump.json" "$D/ledger.json" <<'PY'
import json,sys
try:
    d=json.load(open(sys.argv[1]))
except Exception as e:
    json.dump({"error":str(e)},open(sys.argv[2],"w")); raise SystemExit
nodes=[];clients=[];mods=[]
for o in d:
    t=o.get("type");p=o.get("info",{})
    if t=="PipeWire:Interface:Node":
        nodes.append({"id":o["id"],"name":p.get("node.name"),"class":p.get("media.class"),"client.id":p.get("client.id"),"desc":p.get("node.description")})
    elif t=="PipeWire:Interface:Client":
        clients.append({"id":o["id"],"name":p.get("application.name") or p.get("client.name"),"pid":p.get("application.process.id")})
    elif t=="PipeWire:Interface:Module":
        mods.append({"id":o["id"],"name":p.get("module.name")})
json.dump({"nodes":nodes,"clients":clients,"modules":mods},open(sys.argv[2],"w"),indent=1)
PY
