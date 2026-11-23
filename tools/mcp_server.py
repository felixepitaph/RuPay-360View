#!/usr/bin/env python3
"""RuPay 360 tools as an MCP server (stdio), the native way to register tools in AiNxt.

AiNxt connects to "external MCP servers" and registers each tool it finds as <server>__<tool>
(e.g. rupay360__r360_sql). This file speaks the same newline-delimited JSON-RPC 2.0 protocol that
AiNxt's own servers use (protocol 2024-11-05), with no third-party dependency.

Run by AiNxt (see ainxt/README.md, step "Register the tools"):
    command: python3      args: ["<repo>/tools/mcp_server.py"]
    env:     R360_SOURCE=trino  TRINO_JWT=...  (plus TRINO_HOST etc., see .env.example)

It exposes exactly the tools in engine/r360/tools.py, so the guards (read-only SQL, personal-data
column refusal, row cap, query log, write tools create proposals only) apply unchanged.
stdout carries protocol messages only; everything else goes to stderr.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
os.chdir(ROOT)  # tools write proposals/ and runs/ relative to the repo

_real_stdout = sys.stdout
sys.stdout = sys.stderr  # stray prints from libraries must not corrupt the protocol stream

from r360.tools import FUNCS, spec_json  # noqa: E402

PROTOCOL = "2024-11-05"
SERVER_NAME = "rupay360"


def _ok(id_, result):
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def _err(id_, code, msg):
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": msg}}


def _text(obj, is_error=False):
    text = obj if isinstance(obj, str) else json.dumps(obj, default=str, indent=1)
    out = {"content": [{"type": "text", "text": text}]}
    if is_error:
        out["isError"] = True
    return out


def handle(msg):
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
        return _err(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request")
    method, id_, params = msg.get("method", ""), msg.get("id"), msg.get("params") or {}
    if method == "initialize":
        return _ok(id_, {"protocolVersion": PROTOCOL,
                         "capabilities": {"tools": {"listChanged": False}},
                         "serverInfo": {"name": SERVER_NAME, "version": "1.0.0"}})
    if method in ("initialized", "notifications/initialized") or method.startswith("notifications/"):
        return None
    if method == "ping":
        return _ok(id_, {})
    if method == "tools/list":
        return _ok(id_, {"tools": [{"name": s["name"], "description": s["description"],
                                    "inputSchema": s["input_schema"]} for s in spec_json()]})
    if method == "tools/call":
        name, args = params.get("name", ""), params.get("arguments") or {}
        if name not in FUNCS:
            return _err(id_, -32602, f"Unknown tool: {name}")
        try:
            return _ok(id_, _text(FUNCS[name](**args)))
        except TypeError as e:
            return _err(id_, -32602, f"Invalid arguments for {name}: {e}")
        except Exception as e:  # a tool failure is reported to the agent, never crashes the server
            return _ok(id_, _text(f"Tool error: {type(e).__name__}: {e}", is_error=True))
    return None if id_ is None else _err(id_, -32601, f"Method not found: {method}")


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            resp = handle(json.loads(line))
        except json.JSONDecodeError as e:
            resp = _err(None, -32700, f"Parse error: {e}")
        if resp is not None:
            _real_stdout.write(json.dumps(resp, default=str) + "\n")
            _real_stdout.flush()


if __name__ == "__main__":
    main()
