"""Read-only data access for engines and agents.

Two backends, same interface (`run_sql(sql) -> pandas.DataFrame`):
  * TrinoSource  - the real data lake. Auth by JWT / API token (what AiNxt asked for) or user/password.
  * LocalSource  - DuckDB over snapshot or synthetic files in a folder (demo, tests, offline work).

Guards applied to every query, whoever wrote it (analyst, engine or agent):
  1. Read-only: only SELECT / WITH / SHOW / DESCRIBE / EXPLAIN.
  2. Column restrictions come from engine/config/restrictions.json (owned by the data team and the internal
     models; empty by default). Nothing is hard-coded here.
  3. Row cap (default 50,000) so an agent cannot pull a raw table.
Every query is appended to a query log so each number can be traced to the SQL that produced it.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
from pathlib import Path

import pandas as pd

ALLOWED = re.compile(r"^\s*(select|with|show|describe|explain)\b", re.IGNORECASE)
FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|create|alter|truncate|merge|grant|revoke|call|"
                       r"set\s+session|copy|attach|install|load|export|pragma)\b", re.IGNORECASE)
MAX_ROWS = int(os.environ.get("R360_MAX_ROWS", 50000))
# Column restrictions are NOT hard-coded here. They live in a config file owned by the data team and the
# internal models (default engine/config/restrictions.json, override with R360_RESTRICTIONS). The shipped
# default refuses nothing by column name; real enforcement is Trino permissions and the AiNxt platform's own
# gates. engine/config/restrictions.example.json holds a suggested starter list.
RESTRICTIONS_FILE = Path(os.environ.get("R360_RESTRICTIONS", Path(__file__).resolve().parents[1] / "config" / "restrictions.json"))


def refused_columns(columns) -> list[str]:
    try:
        pats = json.loads(RESTRICTIONS_FILE.read_text()).get("refuse_column_patterns", [])
    except FileNotFoundError:
        pats = []
    rx = [re.compile(p, re.IGNORECASE) for p in pats]
    return [c for c in columns if any(r.search(str(c)) for r in rx)]


class QueryBlocked(Exception):
    pass


def check_sql(sql: str) -> None:
    if not ALLOWED.match(sql) or FORBIDDEN.search(sql):
        raise QueryBlocked("Only read-only statements (SELECT/WITH/SHOW/DESCRIBE/EXPLAIN) are allowed.")


def check_result(df: pd.DataFrame) -> pd.DataFrame:
    bad = refused_columns(df.columns)
    if bad:
        raise QueryBlocked(f"Result has columns restricted by {RESTRICTIONS_FILE.name}: {bad}.")
    if len(df) > MAX_ROWS:
        raise QueryBlocked(f"Result has {len(df)} rows (cap {MAX_ROWS}). Aggregate further.")
    return df


class _Base:
    name = "base"

    def __init__(self, log_path: str | None = None):
        self.log_path = Path(log_path or os.environ.get("R360_QUERY_LOG", "runs/query_log.jsonl"))

    def run_sql(self, sql: str, purpose: str = "") -> pd.DataFrame:
        check_sql(sql)
        df = check_result(self._execute(sql))
        self._log(sql, purpose, len(df))
        return df

    def _log(self, sql, purpose, n):
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        rec = {"at": dt.datetime.now().isoformat(timespec="seconds"), "backend": self.name, "purpose": purpose,
               "rows": n, "sql_hash": hashlib.sha1(sql.encode()).hexdigest()[:12], "sql": sql}
        with self.log_path.open("a") as f:
            f.write(json.dumps(rec) + "\n")

    def _execute(self, sql):  # pragma: no cover
        raise NotImplementedError


class LocalSource(_Base):
    """DuckDB over every .csv / .parquet in `folder`; each file becomes a view named after the file."""
    name = "local"

    def __init__(self, folder: str, **kw):
        super().__init__(**kw)
        import duckdb
        self.con = duckdb.connect()
        for p in sorted(Path(folder).glob("*")):
            if p.suffix in (".csv", ".parquet"):
                reader = "read_csv_auto" if p.suffix == ".csv" else "read_parquet"
                self.con.execute(f"CREATE VIEW {p.stem} AS SELECT * FROM {reader}('{p.as_posix()}')")

    def _execute(self, sql):
        return self.con.execute(sql).df()


class TrinoSource(_Base):
    """Reads TRINO_* settings from the environment (.env locally, API Token Vault in AiNxt)."""
    name = "trino"

    def _connect(self):
        import trino
        from trino.auth import BasicAuthentication, JWTAuthentication
        kw = dict(host=os.environ["TRINO_HOST"], port=int(os.environ.get("TRINO_PORT", 443)),
                  user=os.environ.get("TRINO_USER", "r360-readonly"),
                  http_scheme=os.environ.get("TRINO_HTTP_SCHEME", "https"),
                  verify=os.environ.get("TRINO_CA_BUNDLE") or True)
        for k in ("catalog", "schema"):
            if os.environ.get(f"TRINO_{k.upper()}"):
                kw[k] = os.environ[f"TRINO_{k.upper()}"]
        if os.environ.get("TRINO_JWT"):
            kw["auth"] = JWTAuthentication(os.environ["TRINO_JWT"])
        elif os.environ.get("TRINO_PASSWORD"):
            kw["auth"] = BasicAuthentication(kw["user"], os.environ["TRINO_PASSWORD"])
        return trino.dbapi.connect(**kw)

    def _execute(self, sql):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchmany(MAX_ROWS + 1)
            cols = [d[0] for d in cur.description] if cur.description else []
            return pd.DataFrame(rows, columns=cols)
        finally:
            conn.close()


def get_source(spec: str | None = None):
    """spec: 'trino' or 'local:<folder>'. Default from R360_SOURCE, else local:demo/data."""
    spec = spec or os.environ.get("R360_SOURCE", "local:demo/data")
    if spec == "trino":
        return TrinoSource()
    if spec.startswith("local:"):
        return LocalSource(spec.split(":", 1)[1])
    raise ValueError(f"Unknown source {spec}")
