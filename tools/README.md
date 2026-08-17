# tools/

Helper scripts for JSONbreadCrumb. These are **not** part of the app —
`index.html` is a single hand-written static file with no build step. These
just validate, profile, and serve it. Python 3 standard library only; no
dependencies.

## check.py

```bash
python3 tools/check.py            # checks ../index.html + runs the search benchmark
python3 tools/check.py path.html  # check a specific file
```

- Structural checks on `index.html` (one <script>, balanced tags, key functions present).
- A benchmark comparing the old recursive tree-search against the indexed scan,
  and asserting both return identical results.

## serve.py

```bash
python3 tools/serve.py            # http://localhost:8000
python3 tools/serve.py 9000       # custom port
```

Serves the repo folder so you can open the app over http:// instead of file://.
