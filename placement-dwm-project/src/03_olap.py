"""Experiment 3: run the OLAP queries in sql/02_olap_queries.sql and save the results."""
import re
import sqlite3
import pandas as pd
from config import DB_PATH, SQL_DIR, TABLE_DIR


def main():
    text = (SQL_DIR / "02_olap_queries.sql").read_text()
    blocks = re.split(r"-- name:\s*(\w+)\n", text)[1:]       # [name, sql, name, sql, ...]
    with sqlite3.connect(DB_PATH) as con:
        for name, sql in zip(blocks[::2], blocks[1::2]):
            sql = "\n".join(l for l in sql.splitlines() if not l.startswith("--")).strip()
            result = pd.read_sql_query(sql, con)
            result.to_csv(TABLE_DIR / f"olap_{name}.csv", index=False)
            print(f"\n=== {name} ===")
            print(result.to_string(index=False))


if __name__ == "__main__":
    main()
