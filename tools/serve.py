#!/usr/bin/env python3
"""
serve.py — tiny static server for local use (JSONbreadCrumb).

Opens the app at http://localhost:8000 without a file:// origin.
Handy if you want localStorage/theme persistence to behave like a real site.

Usage:
    python3 tools/serve.py          # serves the repo root on port 8000
    python3 tools/serve.py 9000     # custom port
"""
import sys
import http.server
import socketserver
from pathlib import Path

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
root = Path(__file__).resolve().parent.parent  # repo root (contains index.html)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(root), **kwargs)

    def log_message(self, fmt, *args):  # quieter output
        pass


with socketserver.TCPServer(("", port), Handler) as httpd:
    print(f"Serving {root} at http://localhost:{port}  (Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
