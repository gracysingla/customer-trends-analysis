"""
Generates a customer sales dataset for the trends analysis.

Two files:
  data/customers.csv  — one row per customer
  data/orders.csv     — one row per order, linked to a customer

Two tables rather than one so the analysis needs a JOIN, which is how real
sales data is actually stored.
"""

import csv
import random
from datetime import date, timedelta

random.seed(7)

REGIONS = {
    "North": 0.27, "South": 0.24, "West": 0.29, "East": 0.20,
}

SEGMENTS = {
    "Consumer": 0.52, "Corporate": 0.31, "Small Business": 0.17,
}

# category -> (list of products, typical unit price range)
CATALOGUE = {
    "Electronics": (["Wireless Earbuds", "Smart Watch", "Bluetooth Speaker", "Power Bank"], (1800, 9500)),
    "Home & Kitchen": (["Air Fryer", "Mixer Grinder", "Vacuum Cleaner", "Water Purifier"], (2200, 14000)),
    "Furniture": (["Office Chair", "Study Table", "Bookshelf", "Bed Frame"], (4500, 26000)),
    "Apparel": (["Running Shoes", "Jacket", "Backpack", "Sunglasses"], (900, 6500)),
    "Stationery": (["Notebook Set", "Pen Pack", "Desk Organiser", "Planner"], (150, 1200)),
}

START = date(2024, 1, 1)
END = date(2025, 12, 31)


def month_multiplier(d):
    """Seasonality — festive season lifts sales, early year is slow."""
    return {
        1: 0.80, 2: 0.85, 3: 0.95, 4: 0.92, 5: 0.90, 6: 0.94,
        7: 1.00, 8: 1.05, 9: 1.18, 10: 1.45, 11: 1.30, 12: 1.10,
    }[d.month]


def pick(weighted):
    return random.choices(list(weighted), weights=list(weighted.values()))[0]


def make_customers(n=420):
    rows = []
    for i in range(n):
        signup = START + timedelta(days=random.randint(0, 540))
        rows.append({
            "CustomerID": f"C{1000 + i}",
            "Region": pick(REGIONS),
            "Segment": pick(SEGMENTS),
            "SignupDate": signup.isoformat(),
        })
    return rows


def make_orders(customers, n=2600):
    rows = []
    for i in range(n):
        cust = random.choice(customers)
        signup = date.fromisoformat(cust["SignupDate"])

        # order must fall after signup
        span = (END - signup).days
        if span < 1:
            continue
        order_date = signup + timedelta(days=random.randint(1, span))

        category = random.choice(list(CATALOGUE))
        products, (lo, hi) = CATALOGUE[category]
        product = random.choice(products)

        unit_price = round(random.uniform(lo, hi), 2)

        # corporate buys in bulk, consumers buy singles
        if cust["Segment"] == "Corporate":
            qty = random.randint(2, 12)
        elif cust["Segment"] == "Small Business":
            qty = random.randint(1, 6)
        else:
            qty = random.randint(1, 3)

        # seasonal lift applied as an order-size effect
        if random.random() < (month_multiplier(order_date) - 0.8) / 1.2:
            qty += 1

        discount = random.choice([0, 0, 0, 0.05, 0.10, 0.15])
        revenue = round(unit_price * qty * (1 - discount), 2)

        rows.append({
            "OrderID": f"O{10000 + i}",
            "CustomerID": cust["CustomerID"],
            "OrderDate": order_date.isoformat(),
            "Category": category,
            "Product": product,
            "Quantity": qty,
            "UnitPrice": unit_price,
            "Discount": discount,
            "Revenue": revenue,
        })
    return rows


def write(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    customers = make_customers()
    orders = make_orders(customers)

    write("data/customers.csv", customers)
    write("data/orders.csv", orders)

    total = sum(r["Revenue"] for r in orders)
    print(f"Wrote {len(customers)} customers to data/customers.csv")
    print(f"Wrote {len(orders)} orders to data/orders.csv")
    print(f"Total revenue: {total:,.0f}")
