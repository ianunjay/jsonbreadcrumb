# Case study: JSONbreadCrumb — an offline JSON path tool for large, sensitive payloads

| | |
|---|---|
| **Role** | Product manager (problem framing, direction, QA); AI assistant wrote the code |
| **Type** | Internal developer tool, self-initiated |
| **Timeline** | A few days, ~12 iterations |
| **Deliverable** | One offline HTML file, no dependencies, no server |
| **Users** | Me and any teammate who works with nested JSON on internal data |

**TL;DR** — I needed a JSON path lookup tool that runs offline so internal payloads never leave my machine. I cloned the hosted version, it froze on a real 3 MB file, and I traced it to eager DOM rendering. Switching to lazy rendering cut first-paint DOM nodes ~99% (40,007 to ~400) and took load from a multi-second freeze to instant. A later round made search ~6x faster by indexing once instead of re-walking on every keystroke. The result shipped as **JSONbreadCrumb**.

---

## Problem

To use JSON with dot/bracket notation, you often need the exact path to a buried field. The popular tool for this is jsonpathfinder.com, but it's hosted. I work with formula trees, Customer Value Vault exports, and telemetry dumps, some up to 95,000 lines, and I don't want that data leaving my machine.

**Job to be done:** paste JSON, click a field, get its path, copy it — on real internal files, fully offline.

## Objective and success criteria

| Goal | Success looks like |
|---|---|
| Runs offline | Single file, opens in a browser, no network calls |
| Handles my real files | A 3 MB / 95k-line file opens without freezing |
| Fast path lookup | Click any node, get its path in 4 notations, one-click copy |
| Usable, not just functional | Search, navigation, and readable syntax colors |

## Constraints

- **No data egress.** Everything runs client-side; nothing is uploaded.
- **No build step or dependencies.** One HTML file, so anyone can use it without installs.
- **Must survive large inputs**, not just the demo sample.

## Approach and key decisions

The first version cloned the look and worked on the sample, then froze on a real file. Each decision below came from using it on my own data, not from a spec written up front.

| Problem observed | Decision | Why |
|---|---|---|
| Tab froze for seconds on a 3 MB file | Lazy rendering: build tree nodes only on expand | Profiling showed the first version created every row up front — 40,007 rows, ~160k DOM elements, in one synchronous pass. The freeze was rendering, not parsing or search. |
| Huge file still overwhelming when opened | Collapse everything by default | Show top-level keys only; drill in as needed. |
| Search felt sluggish on big files | Index once, then linear scan | The tree search re-walked the whole JSON and allocated a path array per node on every keystroke. Building a flat index once and scanning it was ~6x faster per keystroke in a benchmark. Find-in-editor was re-tokenizing the whole file on each step; caching the highlight and moving a CSS class made navigation instant. |
| Megabyte files rendered as gray text | Raised the syntax-highlighting size limit | Keep keys, strings, numbers, booleans, and null colored on real files. |
| Hard to scan raw JSON | Added editor code-folding in the gutter | Collapse a blob to `"children": [ ... ]`. |
| One merged search felt confusing | Split into two independent searches | Right = structured tree search with clickable results that jump to the node. Left = find-in-text with highlight and next/previous. |
| Jumping between raw text and structure | Double-click a value on the left to select its node on the right | Needed a position-aware parser mapping a character offset back to its path. |
| Theme toggle lagged | Removed a full re-highlight on every switch | Colors use CSS variables, so switching themes recolors instantly. |
| The tool needed a name | Named it **JSONbreadCrumb** | A breadcrumb is the path trail back to any value — exactly what the tool produces. |

**Biggest call:** lazy vs. eager rendering. It was the difference between a broken tool and a usable one. Everything else was refinement.

## What I shipped

- Interactive, collapsible JSON tree; click any node for its path.
- Four path notations: x.notation, JSONPath, bracket, and JSON Pointer, with one-click copy.
- Two separate searches (tree search on the right, find-in-text on the left), both tuned for large files.
- Double-click in the raw editor to jump to that node in the tree.
- Editable path field that navigates to any path you type.
- Editor code-folding, syntax highlighting, keyboard tree navigation, and instant dark mode.
- Single offline file, no dependencies.

## Impact

| Metric | Before | After |
|---|---|---|
| DOM nodes on first paint (3 MB file) | ~40,007 rows / ~160k elements | ~400 rows / ~1,600 elements |
| Load behavior | Multi-second freeze | Instant |
| Tree search per keystroke (~1 MB file) | ~6 ms (full re-walk) | ~1 ms (indexed scan) |
| Find navigation (next/prev) | Re-tokenize whole file each step | Move one CSS class; no re-render |
| Data egress | N/A | None — fully offline |

## Tradeoffs I made

Each of these was a deliberate choice to give something up, not an oversight.

| Tradeoff | What I chose | What I gave up | Why it was right here |
|---|---|---|---|
| Speed vs. completeness on load | Collapse everything and render lazily | Seeing the whole structure at a glance | On a 95k-line file, "show everything" is unusable anyway. Fast and shallow beats complete and frozen. |
| Memory vs. search speed | Build a flat search index in memory | Some extra RAM per open document | Trading memory for a ~6x faster, allocation-free query loop is the right call for an interactive search box. |
| Two searches vs. one | Kept the tree search and the text search separate | A single unified search box | Merging them read as clever but confused me in testing. Two predictable tools beat one ambiguous one. |
| One file vs. a real codebase | Single HTML file, no build, no dependencies | Modularity, tests, easier long-term maintenance | The goal was something any teammate can open and trust offline. Portability mattered more than engineering polish. |
| Client-side only vs. richer features | Everything runs in the browser | Server-side power like cross-file diffing or history | Non-negotiable: internal payloads can't leave the machine. This constraint shaped every other call. |

## What I'd do differently

- **"Clone this" is not a spec.** The real requirements surfaced through use: my frozen tab, then rounds of reacting to what felt wrong. I couldn't have written them up front.
- **Test against the ugliest real input first.** It passed on the sample and looked done. The failures — the freeze, then the slow search — only showed on a production-sized file.

## Working method (AI-assisted)

An AI assistant wrote the implementation; I did the product work — framing the problem, profiling the failure, setting direction, and rejecting versions that missed. Worth noting: the assistant happily built the slow render, the slow search, matched the wrong styling, and merged the two searches into one confusing box. None of that fixed itself. It got fixed because I profiled the freeze, knew lazy rendering and indexing were the answers, and kept sending it back until each piece was right. When implementation is cheap, the scarce inputs are judgment, taste, and knowing what "done" means.

## Next

A "list all paths" export: every leaf path and its value as a copyable table, so I can diff two payloads or hand an engineer a field map without screenshots.
