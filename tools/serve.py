#!/usr/bin/env python3
"""Tiny static server for local use: python3 tools/serve.py [port]"""
import sys, http.server, socketserver
from pathlib import Path
port=int(sys.argv[1]) if len(sys.argv)>1 else 8000
root=Path(__file__).resolve().parent.parent
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**k): super().__init__(*a,directory=str(root),**k)
    def log_message(self,*a): pass
with socketserver.TCPServer(("",port),H) as h:
    print(f"Serving {root} at http://localhost:{port}  (Ctrl+C to stop)")
    try: h.serve_forever()
    except KeyboardInterrupt: print("\nstopped")
