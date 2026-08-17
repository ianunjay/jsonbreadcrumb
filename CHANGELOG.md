# Changelog

All notable changes to this project are documented here.

## [1.1.0] - 2026-08-15
### Changed
- Renamed the tool to **JSONbreadCrumb**.
- **Much faster search.** Tree search now builds a flat index once per document
  and scans it linearly on each keystroke (~6x faster per keystroke than the
  previous full-tree re-walk, measured on a ~1 MB file).
- **Instant find navigation.** Find-in-editor tokenizes the file once and caches
  the highlighted HTML; stepping between matches now only moves a CSS class
  instead of re-highlighting the whole file.

### Added
- Match-count cap for find decoration so very large match sets stay responsive
  (native selection still steps through every match).

## [1.0.0] - 2026-08-14
Initial release.

### Added
- Interactive, lazily-rendered JSON tree; click a node to get its path.
- Four path notations (x.notation, JSONPath, bracket, JSON Pointer) with copy.
- Collapse-by-default tree for fast loads on large files.
- Two independent searches: tree search (right) and find-in-raw-JSON (left).
- Double-click a key/value in the editor to jump to its node in the tree.
- Editable path field to navigate to a typed path.
- Editor syntax highlighting, line numbers, and gutter code folding.
- Beautify / minify, file upload, and drag-and-drop.
- Rows / Code tree views, optional type labels, expand/collapse all.
- Keyboard tree navigation and Ctrl/Cmd+F find.
- Light and dark themes with instant switching.
