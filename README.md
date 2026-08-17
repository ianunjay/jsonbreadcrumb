# 🍞 JSONbreadCrumb

A single-file, fully offline tool for finding the path to any field in a JSON document. Paste JSON on the left, click a node on the right, and copy its path in the notation you need. Named for the breadcrumb trail it leaves to any value — built to stay fast on large, deeply nested payloads and to keep sensitive data on your own machine.



## Why

The hosted tools are great, but they run in someone else's browser session. When you work with internal or sensitive JSON, you don't want to paste it into a site. JSONbreadCrumb runs entirely client-side from one HTML file, so nothing leaves your machine. It also stays responsive on files that freeze naive tree viewers.

## Features

- **Interactive JSON tree** — click any node to get its path.
- **Four path notations** with one-click copy:
  - `x.notation` — `x.store.book[0].title`
  - `JSONPath` — `$.store.book[0].title`
  - `Bracket` — `x['store']['book'][0]['title']`
  - `Pointer` — RFC 6901 `/store/book/0/title`
- **Fast on large files.** The tree renders lazily (children build only when a node is expanded) and starts fully collapsed, so multi-megabyte files open instantly instead of freezing.
- **Fast search.** The tree search builds a flat index once per document, then each keystroke is a linear scan. Find-in-editor tokenizes once and navigates by moving a highlight, so next/previous is instant even on big files.
- **Two independent searches:**
  - **Tree search** (right): lists clickable results; click one to jump to that node.
  - **Find in raw JSON** (left): highlights matches with next/previous stepping.
- **Double-click to navigate.** Double-click any key or value in the raw editor to jump to that node in the tree.
- **Editable path field.** Type a path in any notation and press Enter to jump to it.
- **Editor niceties:** syntax highlighting, line numbers, code folding in the gutter, beautify/minify, drag-and-drop or upload a `.json` file.
- **Rows / Code views**, optional type labels, expand/collapse all, keyboard tree navigation (arrow keys).
- **Light and dark themes** (remembers your choice; switches instantly).

## Usage

No build, no dependencies, no server.

1. Open `index.html` in any modern browser (double-click it, or serve the folder).
2. Paste JSON into the left editor, or click **Sample**, **Upload**, or drag a `.json` file in.
3. Click a node in the right tree to see its path; click **Copy**.

### Optional: serve locally

```bash
# Python (no extra files needed)
python3 -m http.server 8000
# then open http://localhost:8000

# or use the bundled helper
python3 tools/serve.py            # serves this folder at http://localhost:8000

# or Node
npx serve .
```

## Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl/⌘ + F` | Open **Find in raw JSON** (left panel) |
| `Enter` / `Shift+Enter` | Next / previous find match |
| `Esc` | Close find |
| `Ctrl/⌘ + Enter` | Re-parse the editor |
| `Tab` (in editor) | Insert two spaces |
| Arrow keys (tree focused) | Move / expand / collapse nodes |
| Double-click (in editor) | Jump to that node in the tree |

## How it works

- **Lazy tree rendering.** Only the top level renders on load; each node's children are created the first time it's expanded. First paint is proportional to what's visible, not to file size.
- **Search performance.** Two classic techniques:
  - *Build an index once, query many times.* The tree search flattens the parsed JSON into an array of `{path, lowercased key, lowercased value}` a single time per document. Each keystroke is then a tight linear scan with no recursion or per-node allocation.
  - *Tokenize once, decorate cheaply.* The editor's syntax highlighting is computed once and cached. Find-in-editor reuses that cached HTML and, when stepping between matches, only moves a CSS class between existing `<mark>` elements instead of re-highlighting the whole file.
- **Position-aware parser.** A small tokenizer maps every character offset in the raw text back to its JSON path. That powers double-click-to-navigate and scroll-into-view.
- **CSS-variable theming.** Syntax colors are CSS variables, so switching themes just flips `data-theme` and recolors instantly with no re-processing.
- **Guardrails for huge files.** Syntax highlighting falls back to plain text above a size threshold, find decoration is skipped past a match cap (native selection still navigates), and search results are capped — so the UI stays responsive.

Everything user-facing is in `index.html` — HTML, CSS, and vanilla JavaScript, no libraries.

## Project structure

```
jsonbreadcrumb/
├── index.html            # the entire app (open this)
├── README.md
├── LICENSE               # MIT
├── CHANGELOG.md
├── .gitignore
├── docs/
│   └── case-study.md      # product write-up of how this was built
└── tools/
    ├── check.py           # validation + search benchmark (stdlib only)
    ├── serve.py           # tiny local static server
    └── README.md
```

## Browser support

Any current version of Chrome, Edge, Firefox, or Safari. No IE.

## Development notes

There is no build step. Edit `index.html` and refresh. To sanity-check + benchmark:

```bash
python3 tools/check.py
```

## Acknowledgements

- Concept and UI inspired by **JSON Path Finder** by Joe Beach — https://github.com/joebeachjoebeach/json-path-finder (MIT).
- Implementation written with an AI coding assistant; product direction, profiling, and QA by the repo owner. See `docs/case-study.md`.

## License

MIT — see [LICENSE](LICENSE).
