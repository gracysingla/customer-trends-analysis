"""
Loads the customer and order CSVs into SQLite and runs every query in /queries.

Usage:  python run_analysis.py
"""

import csv
import glob
import os
import sqlite3

DB = "sales.db"

TABLES = {
    "customers": ("data/customers.csv", {"CustomerID", "Region", "Segment", "SignupDate"}),
    "orders": ("data/orders.csv", {"OrderID", "CustomerID", "OrderDate", "Category", "Product"}),
}
NUMERIC = {"Quantity", "UnitPrice", "Discount", "Revenue"}


def load_table(conn, name, path):
    with open(path) as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames
        coltypes = ", ".join(
            f"{c} {'REAL' if c in NUMERIC else 'TEXT'}" for c in cols
        )
        conn.execute(f"CREATE TABLE {name} ({coltypes})")

        placeholders = ", ".join("?" for _ in cols)
        rows = [
            tuple(float(r[c]) if c in NUMERIC else r[c] for c in cols)
            for r in reader
        ]
        conn.executemany(f"INSERT INTO {name} VALUES ({placeholders})", rows)
    return len(rows)


def load():
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    for name, (path, _) in TABLES.items():
        n = load_table(conn, name, path)
        print(f"Loaded {n} rows into {name}")
    conn.commit()
    print()
    return conn


def show(conn, path):
    sql = open(path).read()
    title = os.path.basename(path).replace(".sql", "").replace("_", " ")

    print("=" * 84)
    print(title.upper())
    print("=" * 84)

    cur = conn.execute(sql)
    headers = [d[0] for d in cur.description]
    rows = cur.fetchall()

    def fmt(v):
        if isinstance(v, float) and v == int(v):
            return f"{int(v):,}"
        if isinstance(v, float):
            return f"{v:,.2f}"
        return str(v)

    widths = [
        max(len(h), max((len(fmt(r[i])) for r in rows), default=0))
        for i, h in enumerate(headers)
    ]
    print("  ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print("  ".join(fmt(v).ljust(w) for v, w in zip(r, widths)))
    print()


if __name__ == "__main__":
    conn = load()
    for path in sorted(glob.glob("queries/*.sql")):
        show(conn, path)
    conn.close()
