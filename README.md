# 🍞 JSONbreadCrumb

**A local-first JSON path finder for large, sensitive JSON files.**

[Try JSONbreadCrumb](https://ianunjay.github.io/jsonbreadcrumb/) · [View the PRD](./docs/JSONbreadCrumb-PRD.md) 

---

## Problem

I needed to inspect a JSON file with ~90,000 lines. VS Code could open it, but finding the path to a deeply nested value was painful. Once I found the value I needed, I still had to trace it back through every key and array index to construct the path. 
I normally used JSONPathFinder for this, but I had two problems with it. I didn't want to paste sensitive JSON into a hosted tool, and it was slow on the large files I actually needed to inspect. The second problem was a dealbreake. 

So I decided to build a local-first version that solved both problems.

## My initial build

The initial product definition was fairly simple. I wanted to open large JSON files locally, click a value and get its exact path, copy that path in the notation I needed, and search the JSON without sending any of it outside my machine. I also wanted the product to stay small enough that I could actually maintain it. I wasn't trying to build another JSON IDE. I wanted a tool that solved a very specific problem well.

That meant the real constraint was not just "make it work on large files." It was "make the things I actually need work on large files without building a much larger product than I need."

## First version

I used AI-assisted development to build the first version. It solved the privacy problem. The data stayed local. It also choked on the large files I actually needed it for. My first attempt to fix that was, in retrospect, not particularly sophisticated:

> "make loading & search faster"

That was the entire prompt. Of course, it didn't work. I took a shot witout deep diving into it. So instead of continuing to ask AI to make it faster, I dug into the implementation to understand what was actually happening.

## Reframe

I found that the application was rendering the entire JSON document at once.My screen could show roughly 60 lines. The file had around 90,000. The browser was doing a huge amount of work to render content I didn't even need and couldn't even see. That changed how I thought about the problem. I needed to stop asking it to render 90,000 lines at once in the first place and do it in chunks. I counted the number of lines that I could see on my monitor at once. 

The solution was to virtualize the large-file viewer and render only the content visible in the viewport. That became the main performance decision behind the rebuild. I also realized that large files and normal files did not need exactly the same experience. A normal-sized JSON file can remain editable, but when I am looking at 80,000 lines, I care much more about being able to search and navigate quickly than I do about editing the document.
So large files became a fast, read-only viewer.

## Product decisions

Once I understood the actual problem, I went back to the requirements and separated what I needed from what would merely be nice to have. I chose an interactive JSON tree, multiple path formats, separate searches for the tree and raw JSON, client-side processing, a single-file deployment, and custom virtualization for large files.

I deliberately did not build a full editor for 90,000-line files, a cloud version, server-side processing, or a large editor framework just because it was available. I also avoided turning search into one clever unified interface when two simpler search experiences made more sense. Some of these choices were technically harder than the alternatives. Others meant giving up features I could have built. I was willing to make those tradeoffs because the goal was to solve the actual workflow, and not maximize the feature count.


## Product Requirement Document

Once the problem, requirements, and tradeoffs were clear, I turned them into a PRD.
It covers the product goals and non-goals, target users, functional requirements, privacy and performance requirements, acceptance criteria, and the decisions that shaped the implementation.

[**Read the full PRD →**](./docs/JSONbreadCrumb-PRD.md)

## Measuring the result

The final version felt blazingly fast. So I wanted to put numbers to it, and get some metrics. 

I defined performance measurements and compared the initial implementation with the final version using the same large JSON file and browser environment. The test file was approximately **2.22 MB and 80,000 lines**.

| Metric | First version | Final version |
|---|---:|---:|
| Load + parse + first render | ~5,600 ms | **~290 ms** |
| Scroll step | 40–60 ms | **~24 ms** |
| Editor DOM nodes | ~108,000 | **~370** |

The initial load and first render improved by approximately **19x**.

**5.6 seconds → 290 milliseconds.**

The reduction in DOM size was significant too. Instead of maintaining roughly 108,000 editor elements, the final version maintained around 370. The performance measurements were run using headless Chromium with the same test file and comparison methodology. 

## What I built

The final product supports interactive JSON tree navigation, four path formats (dot notation, JSONPath, bracket notation, and JSON Pointer), one-click path copying, tree search, raw JSON search, and navigation between the raw JSON and tree representations. 
It also includes large-file virtualization, lazy tree rendering, line numbers, code folding, beautify and minify, file upload and drag-and-drop, and light and dark themes.

For large files, the editor becomes a fast, read-only viewer rather than trying to provide a full editing experience.

## My role

The implementation was built using AI-assisted coding. I am not presenting the code as my engineering work. 
My focus was the product: identifying the problem, defining the objective and constraints, framing the requirements, investigating why the first version failed, reframing the performance problem, deciding what to build and what not to build, making the scope tradeoffs, writing the PRD, defining the performance requirements, and validating the result against those requirements.

What interested me about this project was what happens when building becomes cheap.

The code can be generated quickly. That does not remove the need to decide what should exist in the first place, what is worth building, what should be left out, and how to tell whether the thing you built actually solved the problem.

Those are the decisions I wanted this project to demonstrate.

## Product artifacts

The repository includes the product work behind the implementation:

- [**PRD**](./docs/JSONbreadCrumb-PRD.md): product requirements, goals, non-goals, and acceptance criteria.
- [**Performance Validation**](./docs/performance.md): the measurements and methodology used to compare the first and final versions.

The code is here because there needs to be a real product to evaluate the decisions against.

## Try it

[**Open JSONbreadCrumb →**](https://ianunjay.github.io/jsonbreadcrumb/)

No installation, account, or server required. JSONbreadCrumb runs entirely in the browser, so your JSON stays on your machine.

## License

The implementation is MIT licensed.

## Acknowledgement

JSONbreadCrumb was inspired by [JSON Path Finder](https://jsonpathfinder.com/) by Joe Beach. This is an independent, offline rebuild designed around local processing and large-file performance.