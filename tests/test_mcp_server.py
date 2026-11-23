"""Starts tools/mcp_server.py as a subprocess (the way AiNxt would) and speaks MCP to it."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))


def _session(msgs):
    env = {**os.environ, "R360_SOURCE": "local:demo/data", "R360_QUERY_LOG": str(ROOT / "runs" / "mcp_test_log.jsonl")}
    p = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "mcp_server.py")], input="\n".join(json.dumps(m) for m in msgs) + "\n",
                       capture_output=True, text=True, env=env, timeout=60)
    lines = [json.loads(l) for l in p.stdout.splitlines() if l.strip()]  # stdout must be pure JSON-RPC
    return {l["id"]: l for l in lines if "id" in l}


def test_handshake_list_and_call():
    r = _session([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}},
        {"jsonrpc": "2.0", "method": "initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "r360_deal_engine", "arguments": {"scenario": "base"}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "nope", "arguments": {}}},
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "r360_sql", "arguments": {"query": "DROP TABLE x", "purpose": "t"}}},
    ])
    assert r[1]["result"]["serverInfo"]["name"] == "rupay360"
    tools = r[2]["result"]["tools"]
    assert len(tools) == 16 and all({"name", "description", "inputSchema"} <= set(t) for t in tools)
    assert "15.99" in r[3]["result"]["content"][0]["text"]       # deal model reference number comes through
    assert r[4]["error"]["code"] == -32602                        # unknown tool
    assert "blocked" in r[5]["result"]["content"][0]["text"].lower()  # write SQL refused through MCP too


def test_restrictions_are_config_driven(tmp_path, monkeypatch):
    import pandas as pd
    from r360.data_access import QueryBlocked, check_result
    df = pd.DataFrame({"card_key": ["x"], "mobile_no": ["y"], "spend": [1]})
    monkeypatch.setenv("R360_RESTRICTIONS", str(tmp_path / "missing.json"))
    check_result(df)                                    # no file: nothing refused
    f = tmp_path / "r.json"
    f.write_text(json.dumps({"refuse_column_patterns": ["mobile"]}))
    monkeypatch.setenv("R360_RESTRICTIONS", str(f))
    import importlib, r360.data_access as da
    importlib.reload(da)
    with pytest.raises(da.QueryBlocked):
        da.check_result(df)                             # file lists mobile: refused
    f.write_text(json.dumps({"refuse_column_patterns": []}))
    da.check_result(df)                                 # internal models/data team edited it: allowed


def test_shipped_default_refuses_nothing():
    import pandas as pd
    from r360.data_access import check_result
    check_result(pd.DataFrame({"user_ref": ["a"], "spend": [1]}))
