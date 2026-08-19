#!/usr/bin/env python3
"""Structural sanity checks for JSONbreadCrumb's index.html (stdlib only)."""
import sys, re
from pathlib import Path

def main():
    here=Path(__file__).resolve().parent
    target=Path(sys.argv[1]) if len(sys.argv)>1 else here.parent/"index.html"
    if not target.exists():
        print("index.html not found"); sys.exit(1)
    html=target.read_text(encoding="utf-8"); ok=True
    def rep(name,p):
        nonlocal ok; ok=ok and p; print(f"  [{'PASS' if p else 'FAIL'}] {name}")
    rep("exactly one <script> block", len(re.findall(r"<script>[\s\S]*?</script>",html))==1)
    rep("<div> balanced", html.count("<div")==html.count("</div>"))
    for f in ("vPaint","rebuildDisplay","buildSearchIndex","buildPositionIndex","loadText","setMode"):
        rep(f"contains {f}()", f in html)
    rep("titled JSONbreadCrumb", "JSONbreadCrumb" in html)
    rep("virtualized viewer present", 'class="vslab"' in html)
    print("\nRESULT:", "OK" if ok else "FAILED"); sys.exit(0 if ok else 1)

if __name__=="__main__": main()
