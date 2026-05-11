"""
Работа с базой данных PostgreSQL
"""
import json
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2 import pool

from core.config import settings

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


_pool: pool.SimpleConnectionPool | None = None


def _init_pool():
    global _pool
    if _pool is None:
        _pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            sslmode=settings.DB_SSLMODE,
        )
    return _pool


@contextmanager
def get_connection():
    p = _init_pool()
    conn = p.getconn()
    try:
        yield conn
    finally:
        p.putconn(conn)


def init_db():
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id SERIAL PRIMARY KEY,
                    results JSONB NOT NULL,
                    weights JSONB NOT NULL,
                    cargo_value DOUBLE PRECISION,
                    capital_rate DOUBLE PRECISION,
                    created_at TIMESTAMP
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    filename TEXT PRIMARY KEY,
                    applied_at TIMESTAMP NOT NULL DEFAULT now()
                )
            """)
            conn.commit()
            _apply_migrations(conn)


def _apply_migrations(conn):
    if not MIGRATIONS_DIR.exists():
        return
    with conn.cursor() as c:
        c.execute("SELECT filename FROM schema_migrations")
        applied = {r[0] for r in c.fetchall()}
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if path.name in applied:
            continue
        sql = path.read_text(encoding="utf-8")
        with conn.cursor() as c:
            c.execute(sql)
            c.execute("INSERT INTO schema_migrations (filename) VALUES (%s)", (path.name,))
        conn.commit()


# ─────────────────────────────────────────────
# routes
# ─────────────────────────────────────────────

def upsert_route(route_code: str, mode: str, origin: str, destination: str, **fields) -> int:
    """Создаёт или обновляет маршрут по route_code, возвращает id."""
    allowed = {
        "distance_km", "transit_days_base", "border_crossings",
        "port_calls", "gauge_change_count", "carrier", "active", "meta",
    }
    cols, vals = ["route_code", "mode", "origin", "destination"], [route_code, mode, origin, destination]
    for k, v in fields.items():
        if k in allowed and v is not None:
            cols.append(k)
            vals.append(json.dumps(v) if k == "meta" else v)
    placeholders = ", ".join(["%s"] * len(cols))
    updates = ", ".join(f"{c}=EXCLUDED.{c}" for c in cols if c != "route_code") + ", updated_at=now()"
    sql = f"""
        INSERT INTO routes ({", ".join(cols)}) VALUES ({placeholders})
        ON CONFLICT (route_code) DO UPDATE SET {updates}
        RETURNING id
    """
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(sql, vals)
            route_id = c.fetchone()[0]
            conn.commit()
            return route_id


def get_route_by_code(route_code: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as c:
            c.execute("SELECT * FROM routes WHERE route_code = %s", (route_code,))
            r = c.fetchone()
            return dict(r) if r else None


def list_routes(mode: str | None = None, active_only: bool = True) -> list:
    sql = "SELECT * FROM routes WHERE TRUE"
    args: list = []
    if active_only:
        sql += " AND active = TRUE"
    if mode:
        sql += " AND mode = %s"
        args.append(mode)
    sql += " ORDER BY id"
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as c:
            c.execute(sql, args)
            return [dict(r) for r in c.fetchall()]


# ─────────────────────────────────────────────
# route_rates
# ─────────────────────────────────────────────

def insert_route_rate(
    route_id: int,
    rate_usd: float,
    source: str,
    valid_from: datetime | None = None,
    valid_to: datetime | None = None,
    unit: str = "per_teu",
    raw: dict | None = None,
) -> int:
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                """
                INSERT INTO route_rates (route_id, rate_usd, unit, source, valid_from, valid_to, raw)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (route_id, rate_usd, unit, source, valid_from or datetime.now(),
                 valid_to, json.dumps(raw) if raw is not None else None),
            )
            rate_id = c.fetchone()[0]
            conn.commit()
            return rate_id


def get_latest_rate(route_id: int, source: str | None = None) -> dict | None:
    sql = "SELECT * FROM route_rates WHERE route_id = %s"
    args: list = [route_id]
    if source:
        sql += " AND source = %s"
        args.append(source)
    sql += " ORDER BY valid_from DESC LIMIT 1"
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as c:
            c.execute(sql, args)
            r = c.fetchone()
            return dict(r) if r else None


def get_rate_history(route_id: int, limit: int = 100) -> list:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as c:
            c.execute(
                "SELECT * FROM route_rates WHERE route_id = %s ORDER BY valid_from DESC LIMIT %s",
                (route_id, limit),
            )
            return [dict(r) for r in c.fetchall()]


# ─────────────────────────────────────────────
# analysis_results
# ─────────────────────────────────────────────

def save_analysis_results(analysis_id: int, results: list) -> int:
    """Bulk-вставка нормализованных результатов одного анализа."""
    if not results:
        return 0
    rows = [
        (
            analysis_id,
            r.get("route_id"),
            r.get("route_id_code") or r.get("route_code") or r.get("route_id"),
            r.get("mode"),
            r.get("origin"),
            r.get("destination"),
            r.get("cost_usd"),
            r.get("time_days"),
            r.get("risk_index"),
            r.get("emissions"),
            r.get("score"),
            json.dumps(r.get("breakdown", {})),
        )
        for r in results
    ]
    with get_connection() as conn:
        with conn.cursor() as c:
            execute_values(
                c,
                """
                INSERT INTO analysis_results
                    (analysis_id, route_id, route_code, mode, origin, destination,
                     cost_usd, time_days, risk_index, emissions, score, breakdown)
                VALUES %s
                """,
                rows,
                template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)",
            )
            conn.commit()
            return len(rows)


def get_results_for_analysis(analysis_id: int) -> list:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as c:
            c.execute(
                "SELECT * FROM analysis_results WHERE analysis_id = %s ORDER BY score DESC",
                (analysis_id,),
            )
            return [dict(r) for r in c.fetchall()]


def save_analysis(results: list, weights: dict, cargo_value: float, capital_rate: float) -> int:
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                """
                INSERT INTO analyses (results, weights, cargo_value, capital_rate, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (json.dumps(results), json.dumps(weights), cargo_value, capital_rate, datetime.now()),
            )
            analysis_id = c.fetchone()[0]
            conn.commit()
            return analysis_id


def get_all_analyses(limit: int = 50, offset: int = 0) -> list:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as c:
            c.execute(
                "SELECT * FROM analyses ORDER BY id DESC LIMIT %s OFFSET %s",
                (limit, offset),
            )
            return [_row_to_dict(r) for r in c.fetchall()]


def get_analysis_by_id(analysis_id: int) -> dict | None:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as c:
            c.execute("SELECT * FROM analyses WHERE id = %s", (analysis_id,))
            r = c.fetchone()
            return _row_to_dict(r) if r else None


def delete_analysis_by_id(analysis_id: int) -> bool:
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute("DELETE FROM analyses WHERE id = %s", (analysis_id,))
            affected = c.rowcount
            conn.commit()
            return affected > 0


def get_total_count() -> int:
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute("SELECT COUNT(*) FROM analyses")
            return c.fetchone()[0]


def _row_to_dict(row) -> dict:
    results = row["results"]
    weights = row["weights"]
    if isinstance(results, str):
        results = json.loads(results)
    if isinstance(weights, str):
        weights = json.loads(weights)
    created_at = row["created_at"]
    return {
        "id": row["id"],
        "results": results,
        "weights": weights,
        "cargo_value": row["cargo_value"],
        "capital_rate": row["capital_rate"],
        "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else created_at,
    }
