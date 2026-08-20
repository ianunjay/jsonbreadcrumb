# 🍞 JSONbreadCrumb

A single-file, fully offline tool for finding the path to any field in a JSON document. Paste JSON on the left, click a node on the right, and copy its path in the notation you need. Built to stay fast on **very large, deeply nested payloads** and to keep sensitive data on your own machine.

> Inspired by [jsonpathfinder.com](https://jsonpathfinder.com) ([source](https://github.com/joebeachjoebeach/json-path-finder)). Independent, offline rebuild with a virtualized editor for large files.

## Why

The hosted tools run in someone else's browser session. When you work with internal or sensitive JSON, you don't want to paste it into a site. JSONbreadCrumb runs entirely client-side from one HTML file — nothing leaves your machine — and it doesn't hang on multi-megabyte files.

## Performance (measured, headless Chrome 145)

On a **2.22 MB / 80,000-line** JSON file:

| Metric | Old (textarea + full overlay) | JSONbreadCrumb 1.2 |
|---|---|---|
| Load + parse + first render | ~5,600 ms | **~290 ms** (≈19× faster) |
| Scroll frame cost | 40–60 ms (janky) | **~24 ms** (near 60fps) |
| Left-panel DOM nodes | ~108,000 | **~370** |

## How it stays fast

- **Virtualized editor.** For large files the left panel renders only the ~60 lines
  in view (not the whole document), positioned with a CSS transform. Scroll cost is
  proportional to the screen, not the file. Small files keep a normal editable textarea.
- **Big pastes bypass the textarea** so a multi-MB blob never hits the slow native path.
- **Lazy tree** on the right builds child rows only when you expand a node; starts collapsed.
- **Indexed search.** The tree search flattens the JSON once, then each keystroke is a
  linear scan. Find-in-editor tokenizes once and only decorates visible lines.

## Features

- Interactive JSON tree — click any node to get its path.
- Four path notations with one-click copy: `x.notation`, `JSONPath`, `Bracket`, RFC 6901 `Pointer`.
- Two independent searches: tree search (right, clickable results that jump) and find-in-raw-JSON (left, highlight + next/previous).
- Double-click any value in the raw JSON to jump to that node in the tree.
- Editable path field — type a path in any notation and press Enter to jump.
- Line numbers, gutter code-folding, beautify/minify, upload, drag-and-drop.
- Rows / Code tree views, optional type labels, expand/collapse all, keyboard nav.
- Light/dark themes, remembered and instant.

## Usage

No build, no dependencies, no server. Open `index.html` in any modern browser. Paste JSON, click **Sample**, **Upload**, or drag a `.json` file in. Click a node on the right for its path; click **Copy**.

For large files the left panel becomes a fast read-only viewer (badge: "large file · fast viewer"). Editing is for normal-sized inputs — you don't hand-edit an 80k-line file.

### Serve locally (optional)

```bash
python3 tools/serve.py     # http://localhost:8000
```

## Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl/⌘ + F` | Find in raw JSON (left) |
| `Enter` / `Shift+Enter` | Next / previous find match |
| `Esc` | Close find |
| Arrow keys (tree focused) | Move / expand / collapse |
| Double-click (in editor/viewer) | Jump to that node in the tree |

## Project structure

```
jsonbreadcrumb/
├── index.html            # the entire app
├── README.md · LICENSE · CHANGELOG.md · .gitignore
├── docs/case-study.md
└── tools/  check.py · serve.py · README.md
```

## Acknowledgements

- Concept and UI inspired by **JSON Path Finder** by Joe Beach (MIT).
- Implementation written with an AI coding assistant; product direction, profiling, and QA by the repo owner. Performance verified by driving headless Chromium. See `docs/case-study.md`.

## License

MIT — see [LICENSE](LICENSE).


# tools/

Helper scripts for JSONbreadCrumb (Python 3 stdlib only). Not part of the app —
`index.html` is a single hand-written offline file.

- `check.py`  — structural sanity checks on index.html. `python3 tools/check.py`
- `serve.py`  — serve the folder over http. `python3 tools/serve.py [port]`
