#!/usr/bin/env python3
"""
check.py — sanity checks and a search benchmark for JSONbreadCrumb.

This does NOT build index.html (that file is hand-written and self-contained).
It mirrors the validation and profiling done while developing the tool:

  1. Structural checks on index.html (one <script>, balanced tags, key features).
  2. A benchmark comparing the OLD tree-search (recursive re-walk per keystroke)
     against the NEW approach (build a flat index once, then linear scan) and
     asserting they return identical results.

Usage:
    python3 tools/check.py            # runs checks against ../index.html
    python3 tools/check.py path.html  # check a specific file
"""

import sys
import re
import time
import json
from pathlib import Path


# ---------------------------------------------------------------------------
# 1. Structural checks on the HTML file
# ---------------------------------------------------------------------------
def check_html(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    ok = True

    def report(name, passed):
        nonlocal ok
        ok = ok and passed
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")

    scripts = re.findall(r"<script>([\s\S]*?)</script>", html)
    report("exactly one <script> block", len(scripts) == 1)

    report("<div> tags balanced",
           html.count("<div") == html.count("</div>"))

    for feature in ("buildSearchIndex", "rebuildBaseHighlight",
                    "repaintOverlay", "buildPositionIndex"):
        report(f"contains {feature}()", feature in html)

    report("single #search input", html.count('id="search"') == 1)
    report("single #findInput input", html.count('id="findInput"') == 1)
    report("titled JSONbreadCrumb", "JSONbreadCrumb" in html)

    return ok


# ---------------------------------------------------------------------------
# 2. Search benchmark: recursive re-walk vs. build-index-once
#    (Python reimplementation of the JS logic, for parity + timing.)
# ---------------------------------------------------------------------------
def make_big():
    outcomes = []
    for i in range(1500):
        outcomes.append({
            "outcome_id": f"OUT{i}",
            "outcome": "Improve ability to manage work items",
            "product_id": f"PROD-{i}",
            "realized": {"peer_benchmark": {
                "metric": "Work items over budget",
                "result": {"v": 1},
                "period": {"start": "2026-05-01", "end": "2026-07-31"},
            }},
        })
    return {"customer_id": "ACCT0138141", "outcomes": outcomes}


def type_of(v):
    if v is None:
        return "null"
    if isinstance(v, list):
        return "array"
    if isinstance(v, dict):
        return "object"
    return "scalar"


def old_search(data, q):
    """Recursive walk, allocating a fresh path list per node (the slow way)."""
    matches = []

    def walk(v, segs):
        t = type_of(v)
        if t in ("object", "array"):
            items = enumerate(v) if t == "array" else v.items()
            for k, cv in items:
                csegs = segs + [k]
                leaf = type_of(cv) not in ("object", "array")
                key_match = q in str(k).lower()
                val_match = leaf and q in str(cv).lower()
                if key_match or val_match:
                    matches.append(tuple(csegs))
                if not leaf:
                    walk(cv, csegs)

    walk(data, [])
    return sorted(matches)


def build_index(data):
    """Flatten once into (path, lowercased key, lowercased value)."""
    entries = []

    def walk(v, segs):
        t = type_of(v)
        if t in ("object", "array"):
            items = enumerate(v) if t == "array" else v.items()
            for k, cv in items:
                csegs = segs + [k]
                leaf = type_of(cv) not in ("object", "array")
                entries.append((
                    tuple(csegs),
                    str(k).lower(),
                    str(cv).lower() if leaf else None,
                ))
                if not leaf:
                    walk(cv, csegs)

    walk(data, [])
    return entries


def indexed_search(index, q):
    out = []
    for segs, kl, vl in index:
        if q in kl or (vl is not None and q in vl):
            out.append(segs)
    return sorted(out)


def benchmark():
    data = make_big()
    size_mb = len(json.dumps(data)) / 1048576
    print(f"  synthetic file: {size_mb:.2f} MB")

    # simulate typing "work items" one char at a time
    typed = "work items"
    queries = [typed[:i].lower() for i in range(1, len(typed) + 1)]

    t = time.perf_counter()
    old_counts = [len(old_search(data, q)) for q in queries]
    old_ms = (time.perf_counter() - t) * 1000

    t = time.perf_counter()
    index = build_index(data)
    build_ms = (time.perf_counter() - t) * 1000

    t = time.perf_counter()
    new_counts = [len(indexed_search(index, q)) for q in queries]
    new_ms = (time.perf_counter() - t) * 1000

    identical = old_counts == new_counts
    print(f"  nodes indexed: {len(index)}")
    print(f"  OLD  recursive re-walk (10 keystrokes): {old_ms:6.1f} ms  "
          f"(~{old_ms/10:.2f} ms/keystroke)")
    print(f"  index build (one-time):                 {build_ms:6.1f} ms")
    print(f"  NEW  indexed scan (10 keystrokes):      {new_ms:6.1f} ms  "
          f"(~{new_ms/10:.2f} ms/keystroke)")
    if new_ms > 0:
        print(f"  per-keystroke speedup: {old_ms/new_ms:.1f}x")
    print(f"  [{'PASS' if identical else 'FAIL'}] indexed search matches "
          f"recursive search")
    return identical


# ---------------------------------------------------------------------------
def main():
    here = Path(__file__).resolve().parent
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else here.parent / "index.html"

    print(f"Checking {target} ...")
    if not target.exists():
        print("  index.html not found")
        sys.exit(1)

    html_ok = check_html(target)

    print("\nSearch benchmark (old vs. indexed):")
    bench_ok = benchmark()

    print("\nRESULT:", "OK" if (html_ok and bench_ok) else "FAILED")
    sys.exit(0 if (html_ok and bench_ok) else 1)


if __name__ == "__main__":
    main()
