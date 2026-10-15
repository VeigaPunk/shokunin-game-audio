"""Read-only citation-count probe; not a promotion or semantic-evidence gate."""

import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
PREDICATES = (
    "SKILL.md contains real decision tables, error patterns, checklists, cited sources",
    "At least one end-to-end domain task executed and logged in LOG.md",
    "Instructions executable by an agent without oral context",
    "No cross-domain bleed (PROVINCE.md still accurate)",
)


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)


def count(text, paths):
    parts = re.split(r"(?m)^- \[([x~ ])\] ", text)
    rows = []
    for mark, body in zip(parts[1::2], parts[2::2]):
        references = re.findall(r"`([^`]+\.md)(?::[0-9]+(?:-[0-9]+)?)?`", body)
        rows.append({
            "mark": mark,
            "predicate": body.splitlines()[0],
            "references": references,
            "resolved": [path for path in references if path in paths],
        })
    return {
        "boxes": len(rows),
        "canonical_predicates": [row["predicate"] for row in rows] == list(PREDICATES),
        "boxes_with_resolvable_evidence": sum(bool(row["resolved"]) for row in rows),
        "checked_without_resolvable_evidence": sum(
            row["mark"] == "x" and not row["resolved"] for row in rows
        ),
        "checked_boxes": sum(row["mark"] == "x" for row in rows),
        "asserted_boxes": sum(row["mark"] == "~" for row in rows),
        "open_boxes": sum(row["mark"] == " " for row in rows),
        "rows": rows,
    }


if __name__ == "__main__":
    revision = git("rev-parse", "--verify", sys.argv[1] + "^{commit}").strip()
    text = git("show", revision + ":SHONEN.md")
    paths = set(git("ls-tree", "-r", "-z", "--name-only", revision).split("\0"))
    print(json.dumps({"revision": revision, **count(text, paths)}, indent=2))
