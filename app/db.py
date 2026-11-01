import sqlite3
from pathlib import Path


def init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS llm_usage (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            ts            TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            model         TEXT    NOT NULL,
            input_tokens  INTEGER NOT NULL DEFAULT 0,
            output_tokens INTEGER NOT NULL DEFAULT 0,
            cost_usd      REAL    NOT NULL DEFAULT 0.0,
            fallback_used INTEGER NOT NULL DEFAULT 0,
            latency_ms    REAL    NOT NULL DEFAULT 0.0,
            status        TEXT    NOT NULL DEFAULT 'ok'
        )
        """
    )
    con.commit()
    con.close()


def log_call(
    db_path: str,
    *,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
    fallback_used: bool,
    latency_ms: float,
    status: str = "ok",
) -> None:
    con = sqlite3.connect(db_path)
    con.execute(
        """
        INSERT INTO llm_usage
            (model, input_tokens, output_tokens, cost_usd, fallback_used, latency_ms, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (model, input_tokens, output_tokens, cost_usd, int(fallback_used), latency_ms, status),
    )
    con.commit()
    con.close()


def get_usage(db_path: str) -> dict:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row

    totals = con.execute(
        """
        SELECT
            COUNT(*)                        AS total_calls,
            COALESCE(SUM(input_tokens), 0)  AS total_input_tokens,
            COALESCE(SUM(output_tokens), 0) AS total_output_tokens,
            COALESCE(SUM(cost_usd), 0.0)    AS total_cost_usd,
            COALESCE(SUM(fallback_used), 0) AS fallback_calls
        FROM llm_usage
        """
    ).fetchone()

    by_model = con.execute(
        """
        SELECT
            model,
            COUNT(*)          AS calls,
            SUM(input_tokens) AS input_tokens,
            SUM(output_tokens) AS output_tokens,
            SUM(cost_usd)     AS cost_usd
        FROM llm_usage
        GROUP BY model
        """
    ).fetchall()

    con.close()

    return {
        "total_calls": totals["total_calls"],
        "total_input_tokens": totals["total_input_tokens"],
        "total_output_tokens": totals["total_output_tokens"],
        "total_cost_usd": totals["total_cost_usd"],
        "fallback_calls": totals["fallback_calls"],
        "by_model": [
            {
                "model": row["model"],
                "calls": row["calls"],
                "input_tokens": row["input_tokens"],
                "output_tokens": row["output_tokens"],
                "cost_usd": row["cost_usd"],
            }
            for row in by_model
        ],
    }
