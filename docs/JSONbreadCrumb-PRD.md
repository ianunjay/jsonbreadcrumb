# Product Requirements Document: JSONbreadCrumb

| | |
|---|---|
| **Product** | JSONbreadCrumb — offline JSON path finder |
| **Version** | 1.2.0 (shipped) · this PRD covers shipped scope + roadmap |
| **Author** | Anunjay Chouhan (Product) |
| **Status** | Living document |
| **Last updated** | 2026-08-18 |

---

## 1. Summary

JSONbreadCrumb is a single-file, fully offline web tool that finds the exact path to any field in a JSON document. You paste or open JSON, click a value, and copy its path in the notation you need. It is built to stay fast on very large, deeply nested payloads and to keep sensitive data on the user's own machine.

One sentence: **click any value in your JSON, get its path, copy it — instantly, offline, even on 80,000-line files.**

## 2. Problem

Developers and analysts constantly need the access path to a buried field (e.g. `x.outcomes[15].realized.peer_benchmark.source`) so they can read it in code, a formula, or a query. Today they either count brackets by hand or paste JSON into a hosted tool.

Two things are wrong with the status quo:

- **Hosted tools require sending data to a third-party site.** That is a non-starter for internal, sensitive, or regulated payloads.
- **Existing tools hang on large files.** Real internal files (telemetry, exports, config trees) run to tens of thousands of lines and freeze naive viewers.

## 3. Goals and non-goals

### Goals
- Get the path to any field in one click, in the notation the user needs.
- Run entirely client-side; no data ever leaves the browser.
- Open and stay responsive on multi-megabyte / 80k-line files.
- Ship as one portable HTML file with no build step or dependencies.

### Non-goals
- Not a full code editor or IDE.
- Not a JSON validator/linter beyond parse-error location.
- Not a data transformation tool (no jq-style queries, no editing of huge files).
- Not a collaboration or cloud product. No accounts, no server, no sync.

## 4. Target users

| Persona | Context | Primary need |
|---|---|---|
| **Product/technical PM** | Reads internal JSON exports (CVV, telemetry) to trace a value | Copy a field's path without engineering help |
| **Engineer** | Works with API payloads and config trees | Fast path lookup + find, offline, behind the firewall |
| **Data/QA analyst** | Inspects large response bodies | Search a key/value and jump to it in structure |

Common thread: they handle **large and/or sensitive JSON** and cannot use a hosted site.

## 5. User stories

- As a user, I paste JSON and immediately see it as an interactive tree so I can explore structure.
- As a user, I click any node and see its path, which I can copy in one click.
- As a user, I switch the path format (dot / JSONPath / bracket / JSON Pointer) to match where I'll paste it.
- As a user, I search for a key or value and click a result to jump straight to that node.
- As a user, I find text in the raw JSON and step through matches.
- As a user, I double-click a value in the raw JSON and the tree jumps to it.
- As a user, I open an 80,000-line file and it loads in under a second without freezing.
- As a user, I work entirely offline, confident nothing is uploaded.

## 6. Functional requirements

### 6.1 Input
- Accept JSON via **paste**, **file upload**, and **drag-and-drop**.
- Provide a **Sample** loader, **Beautify**, and **Minify**.
- On invalid JSON, show a clear error with **line and column** of the failure.

### 6.2 Structure view (right panel)
- Render parsed JSON as a **collapsible tree**; start **collapsed** by default.
- Build child rows **lazily** (only when a node is expanded).
- Click a node to select it and display its path; click again (or the arrow) to expand/collapse.
- Two display styles: **Rows** (clean key/value) and **Code** (JSON-like).
- Optional **type labels** (string/number/boolean/…), off by default.
- **Expand all / Collapse all** (expand capped for very large files).
- **Keyboard navigation**: arrow keys move, expand, and collapse.

### 6.3 Path output
- Show the selected node's path and a **Copy** button.
- Support four notations, switchable: **x.notation**, **JSONPath**, **Bracket**, **JSON Pointer (RFC 6901)**.
- **Editable path field**: user types a path in any notation and presses Enter to jump to that node.
- Show the selected **value** with a **Copy value** action.

### 6.4 Search (two independent tools)
- **Tree search** (right): matches keys and values; shows a clickable results list; clicking a result jumps to that node. Results capped for responsiveness.
- **Find in raw JSON** (left): highlights matches in the text with **next/previous** stepping and a match counter.
- The two searches are separate and must not interfere.

### 6.5 Raw editor (left panel)
- **Syntax highlighting**, **line numbers**, and **gutter code-folding**.
- **Double-click a value** to jump to its node in the tree.
- **Adaptive rendering** (see performance requirements): editable textarea for normal files, virtualized read-only viewer for large files, switched automatically.

### 6.6 Global
- **Light/dark theme**, remembered across sessions, switches instantly.
- **Resizable split** between the two panels.

## 7. Non-functional requirements

### 7.1 Performance (measured, headless Chrome 145, 2.22 MB / 80k-line file)

| Metric | Target | Achieved (v1.2.0) |
|---|---|---|
| Load + parse + first render | < 1 s | ~290 ms |
| Scroll frame cost | < ~33 ms | ~24 ms (near 60fps) |
| Left-panel DOM nodes | minimal | ~370 (was ~108,000) |
| Tree search per keystroke (~1 MB) | < a few ms | ~1 ms (indexed) |

### 7.2 Privacy and security
- **No network calls at runtime.** All processing is client-side.
- No analytics, telemetry, cookies, or third-party scripts.
- Only persistent state is the theme preference in `localStorage`.

### 7.3 Portability and footprint
- **Single `index.html`**, no build step, no dependencies, no server.
- Works from `file://` or any static host (e.g. GitHub Pages).
- App file on the order of tens of KB.

### 7.4 Compatibility
- Current Chrome, Edge, Firefox, Safari. No IE.

### 7.5 Accessibility
- Keyboard-operable tree; readable color contrast in both themes.
- (Roadmap: full ARIA roles and screen-reader labeling — see §10.)

## 8. Design and architecture (how requirements are met)

- **Lazy tree rendering.** Only the top level renders on load; children are created on first expand. First paint is proportional to what's visible, not file size.
- **Virtualized editor.** For large files the left panel renders only the ~60 visible lines, positioned with a CSS transform, and scrolls via transform (not layout-forcing `scrollTop`). Small files keep a normal editable textarea + overlay. Big pastes bypass the textarea entirely.
- **Indexed search.** The JSON is flattened once into `{path, lowercased key, lowercased value}`; each keystroke is a linear scan. Find-in-editor tokenizes once and decorates only visible lines.
- **Position-aware parser.** A tokenizer maps a character offset back to its JSON path, powering double-click-to-navigate; the viewer uses the browser's native caret API for exactness.
- **CSS-variable theming.** Theme switch flips `data-theme` and recolors instantly with no reprocessing.

Rationale for building a custom virtualized editor instead of embedding CodeMirror/Monaco: those would add 200–500 KB and break the single-file, zero-dependency, hand-auditable constraint that the privacy goal depends on.

## 9. Constraints and tradeoffs

| Decision | Tradeoff accepted | Why |
|---|---|---|
| Large files open **read-only** in the fast viewer | No in-place editing of huge files | Nobody hand-edits 80k lines; instant viewing is the real need. Small files stay editable. |
| **Custom** virtualization, not a library | Fewer editor features than Monaco | Preserves single-file, no-dependency, offline, auditable constraints. |
| **Two** searches, not one unified box | Slightly more UI | A merged search tested as confusing; two predictable tools win. |
| **Client-side only** | No cross-file diff, history, or server features | Non-negotiable: internal payloads must not leave the machine. |

## 10. Roadmap (future scope)

- **"List all paths" export** — every leaf path + value as a copyable table/CSV, for diffing two payloads or handing engineers a field map.
- **Manual "force fast viewer" toggle** and a configurable size threshold.
- **JSON diff** between two pasted payloads (client-side).
- **Full accessibility pass** (ARIA tree roles, screen-reader labels).
- **Optional Web Worker** for parsing/indexing so the UI never blocks on the largest files.
- **JSONL / NDJSON** support.

## 11. Success metrics

Because there is no telemetry (by design), success is measured qualitatively and via benchmarks:

- **Adoption**: teammates use it for internal JSON instead of hosted tools.
- **Performance**: the benchmark (`tools/check.py` + browser test) keeps load < 1 s and scroll near 60fps on an 80k-line file across releases.
- **Trust**: it can be opened, read, and audited as a single file with no external calls.

## 12. Open questions

- What file size should trigger the read-only viewer by default, and should it be user-adjustable?
- Is JSON5 / trailing-comma tolerance worth adding, or does it muddy "strict JSON" clarity?
- Should the "list all paths" export live in this tool or a companion?

## Appendix: glossary

- **Path notation** — the syntax used to access a nested value (dot, JSONPath, bracket, JSON Pointer).
- **Virtualization** — rendering only the on-screen slice of a large document instead of the whole thing.
- **Lazy rendering** — building UI nodes only when they become visible/expanded.
