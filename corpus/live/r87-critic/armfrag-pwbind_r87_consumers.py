def _pwbind_r87_consumers(leg):
    """The union of in_node names across a watch leg's edges_out —
    the link-witness routing verdict."""
    out = set()
    for s in (leg.get("snaps") or []):
        for e in s.get("edges_out") or []:
            if e.get("in_node"):
                out.add(e["in_node"])
    return sorted(out)
