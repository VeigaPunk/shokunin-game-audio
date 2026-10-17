#!/usr/bin/env python3
"""pw-dump -> compact node/port/client table (r79-scout recon helper)."""
import json, subprocess, sys

def dump():
    p = subprocess.run(["pw-dump"], capture_output=True, timeout=15)
    return json.loads(p.stdout)

def main(pattern=None):
    objs = dump()
    for o in objs:
        t = o.get("type", "").split(":")[-1]
        info = o.get("info", {}) or {}
        props = info.get("props", {}) or {}
        name = props.get("node.name") or props.get("application.name") or props.get("module.name") or ""
        if t == "Node":
            if pattern and pattern not in (name + props.get("node.description","")):
                continue
            print(f"NODE id={o['id']} name={name} class={props.get('media.class')} "
                  f"n_in={info.get('n-input-ports')} n_out={info.get('n-output-ports')} "
                  f"state={info.get('state')} desc={props.get('node.description','')!r}")
            for p in info.get("ports", []) or []:
                pp = p.get("props", {}) or {}
                print(f"   PORT id={p['id']} dir={p.get('direction')} name={pp.get('port.name')} "
                      f"chan={pp.get('audio.channel')} group={pp.get('port.group')}")
        elif t == "Module":
            nm = props.get("module.name","")
            if pattern and pattern not in nm:
                continue
            print(f"MODULE id={o['id']} {nm}")
        elif t == "Client":
            if pattern and pattern not in name:
                continue
            print(f"CLIENT id={o['id']} {name}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
