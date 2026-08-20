# Changelog

## [1.2.0] - 2026-08-18
### Changed — big performance rework (measured in headless Chrome 145)
- **Virtualized editor for large files.** The left panel no longer puts the whole
  document in a `<textarea>` + full-file highlight overlay. For large inputs it
  switches to a virtualized viewer that renders only the ~60 visible lines.
  A 2.22 MB / 80k-line file now loads in ~290 ms (was ~5.6 s) — about 19x faster —
  and scrolls near 60fps. Left-panel DOM nodes dropped from ~108,000 to ~370.
- **Big pastes bypass the textarea entirely**, so a multi-MB blob never hits the
  slow native-textarea path.
- Small documents keep the full editable textarea + overlay (unchanged UX).
- Double-click-in-viewer uses the native caret API for exact path navigation.

## [1.1.0] - 2026-08-15
### Changed
- Renamed the tool to **JSONbreadCrumb**.
- Faster tree search (build a flat index once, scan per keystroke).
- Instant find navigation (tokenize once, move a CSS class between marks).

## [1.0.0] - 2026-08-14
Initial release: interactive lazy tree, four path notations, two searches,
double-click navigation, editor folding, dark mode, single offline file.
