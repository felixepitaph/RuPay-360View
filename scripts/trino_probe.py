#!/usr/bin/env python3
"""Read-only Trino helper for schema discovery and saving query results.

Usage:
  python scripts/trino_probe.py catalogs
  python scripts/trino_probe.py schemas <catalog>
  python scripts/trino_probe.py tables <catalog.schema>
  python scripts/trino_probe.py describe <catalog.schema.table>
  python scripts/trino_probe.py sample <catalog.schema.table> [--limit 5]
  python scripts/trino_probe.py query "<SELECT ...>" --out data/result.json
  python scripts/trino_probe.py query-file sql/some_query.sql --out data/result.json

Safety:
  * Only SELECT / WITH / SHOW / DESCRIBE / EXPLAIN statements are allowed.
  * Columns that look like card numbers, phone numbers or account numbers are
    redacted in anything printed or saved by `sample`.
  * Credentials are read from environment variables (.env), never from arguments.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import trino
from trino.auth import BasicAuthentication

ALLOWED = re.compile(r"^\s*(select|with|show|describe|explain)\b", re.IGNORECASE)
FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|create|alter|truncate|merge|grant|revoke|call|set\s+session)\b",
    re.IGNORECASE,
)
SENSITIVE_COL = re.compile(r"(pan|mobile|phone|msisdn|acct|account|aadhaar|vpa|email)", re.IGNORECASE)
IDENT = re.compile(r"^[A-Za-z0-9_\.\"]+$")


def connect():
    missing = [k for k in ("TRINO_HOST", "TRINO_USER") if not os.environ.get(k)]
    if missing:
        sys.exit(f"Missing environment variables: {', '.join(missing)}. See .env.example")
    scheme = os.environ.get("TRINO_HTTP_SCHEME", "https")
    password = os.environ.get("TRINO_PASSWORD")
    ca = os.environ.get("TRINO_CA_BUNDLE") or True
    kwargs = dict(
        host=os.environ["TRINO_HOST"],
        port=int(os.environ.get("TRINO_PORT", 443)),
        user=os.environ["TRINO_USER"],
        http_scheme=scheme,
        verify=ca,
    )
    if os.environ.get("TRINO_CATALOG"):
        kwargs["catalog"] = os.environ["TRINO_CATALOG"]
    if os.environ.get("TRINO_SCHEMA"):
        kwargs["schema"] = os.environ["TRINO_SCHEMA"]
    if password:
        kwargs["auth"] = BasicAuthentication(os.environ["TRINO_USER"], password)
    return trino.dbapi.connect(**kwargs)


def run(sql: str):
    """Run a read-only statement. Returns (columns, rows)."""
    if not ALLOWED.match(sql) or FORBIDDEN.search(sql):
        sys.exit("Blocked: only read-only statements (SELECT/WITH/SHOW/DESCRIBE/EXPLAIN) are allowed.")
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        return cols, rows
    finally:
        conn.close()


def ident(name: str) -> str:
    if not IDENT.match(name):
        sys.exit(f"Invalid name: {name!r}")
    return name


def redact(cols, rows):
    hide = [i for i, c in enumerate(cols) if SENSITIVE_COL.search(c)]
    return [[("<redacted>" if i in hide else v) for i, v in enumerate(r)] for r in rows]


def jsonable(v):
    try:
        json.dumps(v)
        return v
    except TypeError:
        return str(v)


def emit(cols, rows, out=None):
    data = [dict(zip(cols, [jsonable(v) for v in r])) for r in rows]
    if out:
        p = Path(out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2, default=str))
        print(f"Wrote {len(data)} rows to {p}")
    else:
        print(" | ".join(cols))
        for r in rows:
            print(" | ".join(str(jsonable(v)) for v in r))
        print(f"({len(rows)} rows)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("catalogs")
    sub.add_parser("schemas").add_argument("catalog")
    sub.add_parser("tables").add_argument("schema", help="catalog.schema")
    sub.add_parser("describe").add_argument("table", help="catalog.schema.table")
    s = sub.add_parser("sample")
    s.add_argument("table")
    s.add_argument("--limit", type=int, default=5)
    q = sub.add_parser("query")
    q.add_argument("sql")
    q.add_argument("--out")
    qf = sub.add_parser("query-file")
    qf.add_argument("path")
    qf.add_argument("--out")
    a = ap.parse_args()

    if a.cmd == "catalogs":
        emit(*run("SHOW CATALOGS"))
    elif a.cmd == "schemas":
        emit(*run(f"SHOW SCHEMAS FROM {ident(a.catalog)}"))
    elif a.cmd == "tables":
        emit(*run(f"SHOW TABLES FROM {ident(a.schema)}"))
    elif a.cmd == "describe":
        emit(*run(f"DESCRIBE {ident(a.table)}"))
    elif a.cmd == "sample":
        cols, rows = run(f"SELECT * FROM {ident(a.table)} LIMIT {max(1, min(a.limit, 20))}")
        emit(cols, redact(cols, rows))
    elif a.cmd == "query":
        emit(*run(a.sql), out=a.out)
    elif a.cmd == "query-file":
        emit(*run(Path(a.path).read_text()), out=a.out)


if __name__ == "__main__":
    main()
