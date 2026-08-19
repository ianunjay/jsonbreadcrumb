# Case study: JSONbreadCrumb — an offline JSON path tool that survives 80k-line files

| | |
|---|---|
| **Role** | Product manager (problem framing, direction, QA); AI assistant wrote the code |
| **Type** | Internal developer tool, self-initiated |
| **Timeline** | About two weeks, ~15 iterations |
| **Deliverable** | One offline HTML file, no dependencies, no server |
| **Users** | Me and any teammate who works with nested JSON on internal data |

**TL;DR** — I needed a JSON path lookup tool that runs offline so internal payloads never leave my machine. I cloned the hosted version; it froze on a real 3 MB file. Two rounds of profiling traced the cost to how the editor rendered text. Rebuilding the editor to be virtualized took a 2.22 MB / 80k-line file from a ~5.6 s freeze to a ~290 ms load — about 19x — while cutting left-panel DOM nodes from ~108,000 to ~370. Every number here was measured by driving a real headless browser.

---

## Problem

To use JSON with dot/bracket notation, you often need the exact path to a buried field. The popular tool is jsonpathfinder.com, but it's hosted. I work with formula trees, Customer Value Vault exports, and telemetry dumps — some up to 95,000 lines — and I don't want that data leaving my machine.

**Job to be done:** paste JSON, click a field, get its path, copy it — on real internal files, fully offline, without the tab hanging.

## Objective and success criteria

| Goal | Success looks like |
|---|---|
| Runs offline | Single file, opens in a browser, no network calls |
| Handles my real files | A 2–3 MB / 80k-line file loads in well under a second |
| Fast path lookup | Click any node, get its path in 4 notations, one-click copy |
| Stays smooth | Scrolling and search don't stutter on large files |

## Constraints

- **No data egress.** Everything runs client-side; nothing is uploaded.
- **No build step or dependencies.** One HTML file, so anyone can use it without installs.
- **Must survive large inputs**, not just the demo sample.

## Approach and key decisions

Each decision came from using the tool on my own data and, later, from profiling a real browser trace — not from a spec written up front.

| Problem observed | Decision | Why |
|---|---|---|
| Tab froze on a 3 MB file | Lazy tree rendering (build rows on expand) | The first build created every tree row up front. Rendering was the cost, not parsing. |
| Still overwhelming on open | Collapse the tree by default | Show top-level keys; drill in as needed. |
| Search felt sluggish | Index once, then linear scan | Re-walking the JSON per keystroke was wasteful; a flat index made queries ~6x faster. |
| A trace showed the editor was the real wall | **Rebuild the editor to be virtualized** | The DevTools trace pinned the cost on the syntax-highlight overlay: it rendered the entire file as ~108k DOM spans and forced a full-page layout on every scroll. See the chapter below. |
| Merged search felt confusing | Two independent searches | Tree search (right) with clickable jumps; find-in-text (left) with next/previous. |
| Jumping between text and structure | Double-click a value to select its tree node | Uses a position-aware parser (and the browser's caret API in the viewer) to map a click to a path. |

**Biggest call:** virtualizing the editor. It was the difference between a tool that hung on my real files and one that opens them instantly.

## The performance chapter (what actually made it fast)

I almost shipped a version that "felt" fixed. Then I captured a browser performance trace on a real file and read it instead of guessing. The trace was unambiguous:

- `syncScroll` (keeping the highlight overlay aligned) cost **2.16 s** of main-thread time.
- **Layout** ran **4.9 s** across just 37 events — ~133 ms each — because writing `scrollTop` on a giant overlay forced a full-page reflow every scroll.
- **Garbage collection** burned **6.4 s** churning the huge DOM.

The root cause: the editor was a transparent `<textarea>` layered over a `<pre>` that re-rendered the **whole file** as colored spans. Big-O of the search was irrelevant; the bottleneck was DOM and layout.

I then ran a controlled experiment in headless Chrome — current architecture vs. a virtualized one vs. a bare textarea — on a 2.22 MB / 80k-line file:

| Metric | Baseline (textarea + overlay) | **Virtualized** | Bare textarea (native floor) |
|---|---|---|---|
| Paste + first render | ~5,700 ms | **~470 ms** | ~2,400 ms |
| Scroll step (median) | ~55 ms | **~10 ms** | ~70 ms |
| Overlay DOM nodes | ~108,000 | **~90** | 0 |

Two findings mattered. First, virtualization (render only the visible ~60 lines, sync with a CSS transform instead of `scrollTop`) beat everything. Second, a bare `<textarea>` holding 2.2 MB is itself slow (~2.4 s to paste) — a floor you can't optimize away while using one. So the final design **never puts a large document in a textarea at all**: big files load into the virtualized viewer, and big pastes bypass the textarea entirely.

## What I shipped

- A virtualized left editor: renders only visible lines for large files, keeps a normal editable textarea for small ones, and switches automatically.
- Lazy, collapse-by-default JSON tree; click any node for its path.
- Four path notations with one-click copy.
- Two separate searches (indexed tree search; find-in-text with next/previous).
- Double-click a value to jump to its tree node (native caret hit-testing in the viewer).
- Line numbers, gutter folding, beautify/minify, upload, drag-and-drop, dark mode.
- Single offline file, no dependencies.

## Impact (measured in headless Chrome 145, 2.22 MB / 80k lines)

| Metric | Before | After |
|---|---|---|
| Load + parse + first render | ~5,600 ms | **~290 ms** (≈19× faster) |
| Scroll frame cost | 40–60 ms (janky) | **~24 ms** (near 60fps) |
| Left-panel DOM nodes | ~108,000 | **~370** |
| Data egress | N/A | None — fully offline |

## Tradeoffs I made

| Tradeoff | What I chose | What I gave up | Why it was right here |
|---|---|---|---|
| Editing vs. speed on huge files | Large files open in a read-only fast viewer | Hand-editing an 80k-line file in place | Nobody hand-edits 80k lines; instant, smooth viewing is what the job needs. Small files stay fully editable. |
| Custom virtualization vs. a library | Wrote a small virtualized renderer | CodeMirror/Monaco features | Keeps the zero-dependency, single-file, offline constraint. A library would add 200–500 KB and break "one hand-written file." |
| Memory vs. search speed | Build a flat search index | Some extra RAM per document | A ~6x faster, allocation-free query loop is worth it for an interactive search box. |
| Two searches vs. one | Kept tree search and text search separate | A single unified box | Merging them tested as confusing. Two predictable tools beat one ambiguous one. |
| Client-side only vs. richer features | Everything in the browser | Server-side power (cross-file diff, history) | Non-negotiable: internal payloads can't leave the machine. |

## What I'd do differently

- **Profile before optimizing.** I nearly shipped a fix that only *felt* faster. The trace redirected me from the search algorithm to the editor's rendering, which was the real cost.
- **Test against the ugliest real input first.** Every failure — the freeze, the slow search, the slow scroll — only showed on a production-sized file, never on the sample.

## Working method (AI-assisted)

An AI assistant wrote the implementation; I did the product work — framing the problem, reading the performance trace, deciding to virtualize, designing the small-vs-large mode switch, and rejecting versions that missed. The assistant happily built the slow render, the slow search, and a mode-switch bug that put a 2 MB file down the wrong path. None of that fixed itself. It got fixed because I profiled, knew virtualization was the answer, and verified each build by driving a real headless browser until the numbers and the screenshots were right. When implementation is cheap, the scarce inputs are judgment, taste, measurement, and knowing what "done" means.

## Next

A "list all paths" export: every leaf path and its value as a copyable table, so I can diff two payloads or hand an engineer a field map without screenshots.
