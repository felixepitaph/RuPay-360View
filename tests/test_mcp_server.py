"""Starts tools/mcp_server.py as a subprocess (the way AiNxt would) and speaks MCP to it."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
from r360.data_access import SENSITIVE_COL  # noqa: E402


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


@pytest.mark.parametrize("col", ["pan", "card_key", "mobile_no", "cvv", "account_number", "ifsc_code", "api_key", "access_token", "pin", "customer_email"])
def test_sensitive_columns_refused(col):
    assert SENSITIVE_COL.search(col)


@pytest.mark.parametrize("col", ["spend", "merchant_id", "shopping_spend", "week_start", "cards", "issuer_bank", "txn_count"])
def test_ordinary_columns_not_flagged(col):
    assert not SENSITIVE_COL.search(col)


def test_encrypted_id_column_can_be_allowed(monkeypatch):
    import pandas as pd
    from r360.data_access import QueryBlocked, check_result
    df = pd.DataFrame({"user_ref": ["a1", "b2"], "spend": [10, 20]})
    monkeypatch.delenv("R360_ALLOWED_ID_COLUMNS", raising=False)
    check_result(pd.DataFrame({"user_ref": ["x"], "spend": [1]}))          # not matched by the sensitive pattern, passes anyway
    with pytest.raises(QueryBlocked):
        check_result(pd.DataFrame({"card_key": ["x"], "spend": [1]}))      # raw card_key still refused by default
    monkeypatch.setenv("R360_ALLOWED_ID_COLUMNS", "card_key,mobile_no")
    check_result(pd.DataFrame({"card_key": ["x"], "spend": [1]}))          # allowed once the data team lists it
    with pytest.raises(QueryBlocked):
        check_result(pd.DataFrame({"mobile_no": ["x"]}))                   # raw identifiers can never be allow-listed
