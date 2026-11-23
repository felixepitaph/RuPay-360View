#!/usr/bin/env python3
"""Tiny HTTP tool server so AiNxt Factory Tools (or any agent runtime) can call the RuPay 360 tools.

  GET  /tools               -> tool specs (name, description, input_schema)
  POST /tools/<name>        -> run the tool with the JSON body as arguments, returns JSON
Every request must carry  Authorization: Bearer <R360_TOOL_TOKEN>.
Binds to 127.0.0.1 unless R360_TOOL_HOST is set; run it on the internal machine that can reach Trino.

  PYTHONPATH=engine R360_TOOL_TOKEN=... R360_SOURCE=trino python tools/server.py
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))
from r360.tools import FUNCS, spec_json  # noqa: E402

TOKEN = os.environ.get("R360_TOOL_TOKEN")


class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _auth(self):
        if not TOKEN or self.headers.get("Authorization") != f"Bearer {TOKEN}":
            self._send(401, {"error": "Missing or invalid Authorization header"})
            return False
        return True

    def do_GET(self):
        if self._auth():
            self._send(200, spec_json()) if self.path == "/tools" else self._send(404, {"error": "not found"})

    def do_POST(self):
        if not self._auth():
            return
        name = self.path.rsplit("/", 1)[-1]
        if name not in FUNCS:
            return self._send(404, {"error": f"unknown tool {name}"})
        try:
            args = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)) or 0) or b"{}")
            self._send(200, FUNCS[name](**args))
        except TypeError as e:
            self._send(400, {"error": f"bad arguments: {e}"})
        except Exception as e:  # report, never crash the server
            self._send(500, {"error": f"{type(e).__name__}: {e}"})


if __name__ == "__main__":
    if not TOKEN:
        sys.exit("Set R360_TOOL_TOKEN first.")
    host, port = os.environ.get("R360_TOOL_HOST", "127.0.0.1"), int(os.environ.get("R360_TOOL_PORT", 8360))
    print(f"RuPay 360 tools on http://{host}:{port}/tools")
    ThreadingHTTPServer((host, port), H).serve_forever()
