"""
Builds the sales dashboard image from the same queries used in the SQL analysis.

Usage:  python build_dashboard.py
Output: output/dashboard.png
"""

import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DB = "sales.db"
INK = "#1d2530"
MUTED = "#8a97a3"
BAR = "#3d6b8f"
HI = "#d08c34"
LINE = "#3d6b8f"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": "#d6dce1",
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def q(conn, sql):
    return conn.execute(sql).fetchall()


def lakhs(v):
    return v / 100000.0


def barh(ax, labels, values, title, suffix="L"):
    colors = [BAR] * len(values)
    colors[values.index(max(values))] = HI
    bars = ax.barh(labels, values, color=colors, height=0.58)
    ax.invert_yaxis()
    ax.set_title(title, fontsize=10.5, weight="bold", loc="left", pad=9)
    ax.set_xlim(0, max(values) * 1.28)
    ax.xaxis.set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=9)
    for b, v in zip(bars, values):
        ax.text(b.get_width() + max(values) * 0.02, b.get_y() + b.get_height() / 2,
                f"{v:,.1f}{suffix}", va="center", fontsize=8.5, color=INK)


def main():
    conn = sqlite3.connect(DB)

    fig = plt.figure(figsize=(13.5, 9))
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(3, 2, height_ratios=[0.26, 1, 1],
                          hspace=0.6, wspace=0.34,
                          left=0.11, right=0.96, top=0.95, bottom=0.07)

    # ---- headline ----
    total_rev, orders, customers = q(conn, """
        SELECT SUM(Revenue), COUNT(*), (SELECT COUNT(*) FROM customers) FROM orders
    """)[0]
    aov = total_rev / orders

    head = fig.add_subplot(gs[0, :])
    head.axis("off")
    head.text(0, 0.78, "Customer & Sales Trends", fontsize=19, weight="bold", color=INK)
    head.text(0, 0.32, "Where revenue comes from, who is buying, and what they buy",
              fontsize=10, color=MUTED)

    for i, (label, value) in enumerate([
        ("Revenue", f"{total_rev/10000000:.1f} Cr"),
        ("Orders", f"{orders:,}"),
        ("Customers", f"{customers:,}"),
        ("Avg order", f"{aov/1000:.0f}k"),
    ]):
        x = 0.55 + i * 0.115
        head.text(x, 0.72, value, fontsize=15, weight="bold", color=HI if i == 0 else INK)
        head.text(x, 0.28, label, fontsize=8.5, color=MUTED)

    # ---- revenue over time ----
    rows = q(conn, """
        SELECT substr(OrderDate,1,7), SUM(Revenue) FROM orders GROUP BY 1 ORDER BY 1
    """)
    months = [r[0] for r in rows]
    revs = [lakhs(r[1]) for r in rows]

    ax = fig.add_subplot(gs[1, :])
    ax.plot(range(len(months)), revs, color=LINE, linewidth=2.2, marker="o",
            markersize=3.5, markerfacecolor="white", markeredgewidth=1.4)
    ax.fill_between(range(len(months)), revs, alpha=0.10, color=LINE)
    ax.set_title("Monthly revenue (₹ lakh)", fontsize=10.5, weight="bold", loc="left", pad=9)
    ax.set_xticks(range(0, len(months), 2))
    ax.set_xticklabels([months[i] for i in range(0, len(months), 2)],
                       rotation=45, ha="right", fontsize=8)
    ax.tick_params(axis="y", labelsize=8.5)
    ax.grid(axis="y", color="#eef2f4", linewidth=1)
    ax.set_axisbelow(True)

    # ---- segments ----
    rows = q(conn, """
        SELECT c.Segment, SUM(o.Revenue) FROM orders o
        JOIN customers c ON o.CustomerID = c.CustomerID
        GROUP BY 1 ORDER BY 2 DESC
    """)
    ax = fig.add_subplot(gs[2, 0])
    barh(ax, [r[0] for r in rows], [lakhs(r[1]) for r in rows],
         "Revenue by customer segment (₹ lakh)")

    # ---- categories ----
    rows = q(conn, """
        SELECT Category, SUM(Revenue) FROM orders GROUP BY 1 ORDER BY 2 DESC
    """)
    ax = fig.add_subplot(gs[2, 1])
    barh(ax, [r[0] for r in rows], [lakhs(r[1]) for r in rows],
         "Revenue by product category (₹ lakh)")

    fig.savefig("output/dashboard.png", dpi=155, facecolor="white")
    print("Wrote output/dashboard.png")
    conn.close()


if __name__ == "__main__":
    main()
