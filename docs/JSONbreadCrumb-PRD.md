# JSONbreadCrumb Product Requirements Document

**Status:** Implemented
**Product:** JSONbreadCrumb
**Owner:** Product
**Document purpose:** Define the problem, product scope, requirements, constraints, and success criteria for a local-first JSON path navigation tool.

---

## 1. Product Overview

JSONbreadCrumb is a single-file, fully offline tool for navigating large, deeply nested JSON documents and finding the path to individual fields.

The product came from a fairly specific problem: I regularly need to inspect large JSON payloads, find a particular value, and then copy its path. Existing tools make the path part easy, but the two tools I cared about most were privacy and performance. I did not want sensitive JSON leaving my machine, and I needed something that could handle files with tens of thousands of lines without becoming unusable.

The product is therefore intentionally focused on three things: **privacy, large-file performance, and fast path discovery.** It is not intended to become a full JSON IDE or a general-purpose editor.

---

## 2. Problem

When working with deeply nested JSON, finding a value is often only half the problem. Once the value is located, getting its complete path requires tracing through every parent object and array index.

For a small JSON document this is annoying. For a large payload with deep nesting, it becomes tedious and error-prone.

I was using JSONPathFinder to avoid doing this manually, but it introduced two problems of its own. First, it is a hosted tool, which made me uncomfortable using it with sensitive internal data. Second, it became slow on the larger files I needed to inspect.

The product needed to solve both problems without turning into a much larger product than the use case justified.

---

## 3. Target Users

The primary users are people who regularly inspect JSON as part of their work, including 

* Product Managers
* Software Engineers
* Data Analysts
* QA teams
* Technical Support Teams

They may understand JSON well enough to navigate it, but they do not necessarily need a full programming environment or a sophisticated JSON editor. The main job is usually to find something, understand where it lives, and copy its path somewhere else.

That distinction matters because it shapes the product around **inspection and navigation rather than editing**.

---

## 4. Product Objective

The objective is to provide a fast, local-first way to inspect large JSON and retrieve the path to any field. A successful workflow should be straightforward:

**Open JSON → Find the field → Select it → Copy the path**

The user should not need to manually construct the path, upload the document to a third-party service, or wait several seconds for a large file to become usable.

---

## 5. Goals and Non-Goals

### Goals

The product should:

* Allow users to open large JSON files locally.
* Allow users to navigate the JSON structure.
* Generate the path for any selected node.
* Support multiple path notations.
* Provide search across both the tree and raw JSON.
* Keep JSON data entirely on the user's machine.
* Remain responsive on files of approximately 80,000 to 90,000 lines.
* Run as a self-contained application without a server or runtime dependencies.

### Non-goals

* The product is not intended to become a full JSON IDE, a replacement for command-line tools such as `jq`, or a cloud-based JSON collaboration product.
* Large-file editing is also not a primary goal. For a document containing 80,000 or 90,000 lines, the value is in being able to inspect and navigate it quickly, not in providing a comfortable editing experience.

This scope is deliberate. Features should be added because they improve the core workflow, not because they are technically possible.

---

## 6. Product Requirements

### JSON input and navigation

Users should be able to paste JSON, upload a file, or drag and drop a JSON file into the application. 

Once loaded, the JSON should be represented as an interactive tree. Users should be able to expand and collapse objects and arrays, select individual nodes, and move through deeply nested structures without unnecessary rendering work.

The tree should be built lazily where appropriate so that a large document does not require every visible representation to be created immediately.

### Path generation

Selecting a node should immediately expose its path.

The product should support four path representations:

* Dot notation
* JSONPath
* Bracket notation
* JSON Pointer

The user should be able to copy each representation directly. The generated path must preserve nested object keys and array indexes correctly from the root to the selected node.

### Search

Search needs to work in two different contexts. The first is the JSON tree, where users may want to search keys and values and then jump directly to a matching node.

The second is the raw JSON document, where users may want to find a piece of text and move through its occurrences.

These are intentionally separate search experiences. They operate on different representations of the same document, and combining them into one interface would make the behavior less predictable.

The raw JSON view should support match highlighting and next/previous navigation. Users should also be able to move between the raw representation and the corresponding tree node.

---

## 7. Large-File Performance

Large files are a core product constraint, not an edge case.

The first implementation exposed why this mattered. It attempted to render the entire JSON document even when only a small portion of it was visible. A typical viewport showed roughly 60 lines, while a large test file contained around 90,000 lines.

The application therefore needed to stop rendering content that the user could not see. For large documents, the viewer should render only the lines currently required by the viewport and maintain the correct document position as the user scrolls. 

This means the amount of rendered content should depend primarily on the screen rather than the total number of lines in the document. The large-file viewer is therefore read-only. Normal-sized files can remain editable, but very large files prioritize fast viewing and navigation.

---

## 8. Privacy and Deployment

Privacy is a product requirement rather than an implementation preference.

JSON should be processed entirely in the browser and should not be transmitted to a remote server. The product should not require an account, backend, or cloud service.

The application is designed to run from a single HTML file with no runtime dependencies or build requirements for the end user. This also makes the product practical for environments where sensitive data cannot be sent to external services or where network access is restricted.

---

## 9. Usability

The primary workflow should remain visible and straightforward even as additional functionality is introduced. The interface should provide clear access to the selected node's path and make copying it a single-action task.

Supporting functionality includes line numbers, code folding, keyboard navigation, upload and drag-and-drop, beautify/minify, and light/dark themes. These features should support the primary workflow rather than compete with it.

For large files, the interface should clearly indicate that the document is being shown in the fast, read-only viewer.

---

## 10. Product Tradeoffs

The product deliberately gives up some capabilities in exchange for performance, privacy, and simplicity.

| Decision                          | Tradeoff                                                  | Rationale                                                                                          |
| --------------------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Read-only viewer for large files  | No editing of very large documents                        | The primary need is inspection, not editing tens of thousands of lines.                            |
| Custom virtualization             | More implementation work than using a full editor library | Keeps the application self-contained and gives direct control over large-file rendering.           |
| Separate tree and raw-text search | No single unified search box                              | The two searches represent different user tasks and are easier to understand separately.           |
| Client-side processing            | No server-side features                                   | Sensitive JSON should remain on the user's machine.                                                |
| Focused feature set               | No broad collection of advanced features                  | The product should remain useful and maintainable rather than becoming a general-purpose JSON IDE. |

These were treated as product decisions, not engineering limitations. The question was not "what can we build?" but "what is worth building for this problem?"

---

## 11. Technical Direction

The product requirements led to a small number of important technical decisions.

For large files, the editor uses virtualization so that only visible lines need to be rendered. The JSON tree is built lazily, so expanding one part of a large document does not require constructing the entire visible hierarchy.

Search also avoids repeatedly doing unnecessary work. The tree search builds an index that can then be searched, while raw JSON search limits visual rendering to the content that needs to be shown.

The implementation remains client-side and contained in a single HTML file, which supports both the privacy and deployment requirements. These implementation decisions exist to support the product requirements above. They are not goals in themselves.

---

## 12. Success Criteria

- The product needed measurable performance criteria rather than a subjective definition of "fast."
- For a representative large file of approximately 2.2 MB and 80,000 lines, I defined three primary measurements:
- Load and first render:** time from loading the file until the initial tree becomes visible.
- Scroll cost:** main-thread work required during scrolling, with approximately one 60 FPS frame, or 16.7 ms, as the target.
- DOM footprint:** the number of elements the browser needs to manage in the editor.
- The comparison should use the same file, browser environment, and test procedure for both the initial and final implementations.

---

## 13. Acceptance Criteria

- [ ] The product is ready when a user can open a large JSON document, navigate its structure, find a field, retrieve the correct path, and copy it without manually constructing the path.

- [ ] The application must also keep JSON processing local, support the defined search workflows, and remain usable on large documents without freezing the browser.

- [ ] For large files, the viewer must use virtualized rendering and maintain accurate line positioning and navigation.

- [ ] The implementation should meet the defined performance targets or document the reason for any deviation.

---

## 14. Validation Results

The final implementation was tested against a representative JSON file containing approximately **2.22 MB and 80,000 lines**.

| Metric                      | Initial Version | Final Version |
| --------------------------- | --------------: | ------------: |
| Load + parse + first render |       ~5,600 ms |   **~290 ms** |
| Scroll step                 |        40–60 ms |    **~24 ms** |
| Editor DOM nodes            |        ~108,000 |      **~370** |

Load and first-render time improved by approximately **19x**, from around 5.6 seconds to 290 milliseconds.

The editor DOM footprint dropped from approximately 108,000 elements to around 370.

Performance was validated using headless Chromium with the same test file and comparison methodology.

The result confirmed that the product requirements were addressing the right problem. The performance improvement did not come from trying to make the browser render 90,000 lines faster. It came from changing how much the browser needed to render in the first place.

---

## 15. Future Scope

Future additions should be evaluated against the original product objective before being added.

Potential areas include better handling of extremely large files, additional navigation shortcuts, expanded search capabilities, and further performance instrumentation. The product should remain focused on private, fast JSON inspection. Moving toward a full editor, cloud platform, or collaboration tool would represent a different product and would require a new problem definition rather than incremental feature additions.

---

## Related Documents

* [Performance Validation](./performance.md)
* [README](../README.md)

**Product:** [JSONbreadCrumb](https://ianunjay.github.io/jsonbreadcrumb/)
