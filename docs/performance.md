# Performance Test Spec: JSONbreadCrumb (one-pager)

| | |
|---|---|
| **Owner** | Anunjay Chouhan (Product) |
| **For** | Engineering (implementer), QA |
| **Related** | PRD.md |
| **Status** | Ready to build |

---

## Why we're doing this

JSONbreadCrumb's whole point is handling large JSON without hanging. The first version froze on real files. We rebuilt it and it *feels* fast — but "feels fast" isn't evidence. I want a repeatable test that proves it, and catches regressions before release.

## What we're proving (the user's questions)

1. Does it open a big file quickly, without hanging?
2. Does it scroll smoothly?
3. Is it actually faster than the first version?
4. Did any of that break search, navigation, or correctness?

## Test input

A generated ~2.2 MB / ~80,000-line JSON file (synthetic — no real or sensitive data). A tiny file for the small-input sanity path.

## Pass bar (this is the gate)

A build passes only if, on the big file:

| # | Criterion | Bar |
|---|---|---|
| 1 | Load to usable (file in → tree visible) | **under 1 second** |
| 2 | Scrolling | **smooth, no visible jank** |
| 3 | Faster than the original "render everything" approach | **clearly, measurably faster** (target: ~10× on load) |
| 4 | Correctness under load | search, find, and click-to-navigate all still work; **no errors** |

If any of these fail, the build does not ship. "It feels fast" is not an acceptable result — show me a number.

## Non-goals

- Not production/user telemetry (the tool is offline by design).
- Not a cross-browser matrix in v1 — Chromium is the reference.
- Not micro-benchmarking individual functions — we measure what the user feels.

## Risks I want handled

- **Machine variance:** absolute times differ by hardware. Gate on the *ratio* vs. the old version, plus a generous absolute ceiling — not on tight exact numbers.
- **Extension noise:** measure in a clean browser profile; extensions pollute the comparison.

---

## Engineering section 


**Method (proposed):** drive a real headless browser (e.g. Playwright + Chromium). Load the fixture the way a user does. Discard warmup samples. Fresh context per run. Record browser version + machine with results.

**Metrics to capture:**
- **Load-to-render** (ms): content handed in → status "Valid" and tree visible.
- **Scroll step cost** (ms): main-thread time per scroll increment; report **median + p95**. Smooth ≈ under one 60fps frame (16.7 ms); hard ceiling 33 ms median / 60 ms p95.
- **Editor DOM node count**: proxy for the layout/GC pressure that caused the original freeze. Expect a few hundred, not tens of thousands.
- **A/B ratio:** run the same fixture through the old ("render everything") and new (virtualized) approaches; compute baseline ÷ new. Target ≥ 10× load, ≤ 1% of the DOM nodes.
- **Correctness assertions:** correct content at deep scroll; tree search returns the right node/path; find returns the right count and steps; double-click navigates to the right path; zero console errors.

**Deliverables:** a fixture generator, an app benchmark that prints a report and **exits non-zero on any failed criterion** (so it can gate CI), an A/B benchmark, and a short README with how-to-run + reference numbers.

**Reference (context only, not the gate):** on Chromium 145, ~2.2 MB file — app load ~290 ms, scroll median ~24 ms, editor nodes ~370; A/B ~5,600 ms → ~430 ms (~13×), DOM 108,000 → ~90.
