"""
Converts the real Superstore dataset (downloaded from Kaggle) into the same
two-table shape this project's queries expect:

  data/customers.csv  -> CustomerID, Region, Segment, SignupDate
  data/orders.csv      -> OrderID, CustomerID, OrderDate, Category, Product,
                          Quantity, UnitPrice, Discount, Revenue

Reads: superstore_raw.csv (place the downloaded Kaggle file here, renamed)
"""

import pandas as pd
import os

RAW_FILE = "superstore_raw.csv"

# Kaggle exports sometimes use latin1 encoding because of special characters
# in a few product names (e.g. curly apostrophes).
try:
    df = pd.read_csv(RAW_FILE, encoding="utf-8")
except UnicodeDecodeError:
    df = pd.read_csv(RAW_FILE, encoding="latin1")

# Different copies of this dataset online use slightly different column
# spellings/casing. Normalise them here so the rest of the script doesn't
# need to guess.
rename_map = {}
for col in df.columns:
    key = col.strip().lower().replace(" ", "").replace("-", "").replace("_", "")
    if key == "orderid":
        rename_map[col] = "OrderID"
    elif key == "orderdate":
        rename_map[col] = "OrderDate"
    elif key == "customerid":
        rename_map[col] = "CustomerID"
    elif key == "segment":
        rename_map[col] = "Segment"
    elif key == "region":
        rename_map[col] = "Region"
    elif key == "category":
        rename_map[col] = "Category"
    elif key == "subcategory":
        rename_map[col] = "Product"
    elif key == "sales":
        rename_map[col] = "Revenue"
    elif key == "quantity":
        rename_map[col] = "Quantity"
    elif key == "discount":
        rename_map[col] = "Discount"

df = df.rename(columns=rename_map)

required = ["OrderID", "OrderDate", "CustomerID", "Segment", "Region",
            "Category", "Product", "Revenue", "Quantity", "Discount"]
missing = [c for c in required if c not in df.columns]
if missing:
    raise SystemExit(
        f"These expected columns weren't found after renaming: {missing}\n"
        f"Columns actually in the file: {list(df.columns)}\n"
        "Open the CSV and check the real column names, then tell Claude."
    )

# Real-world date parsing: this dataset is typically MM/DD/YYYY (US format).
df["OrderDate"] = pd.to_datetime(df["OrderDate"], errors="coerce")
bad_dates = df["OrderDate"].isna().sum()
df = df.dropna(subset=["OrderDate"])
df["OrderDate"] = df["OrderDate"].dt.strftime("%Y-%m-%d")

# UnitPrice isn't in the source file directly - derive it for completeness,
# even though none of the six SQL queries actually use it.
df["UnitPrice"] = (df["Revenue"] / df["Quantity"]).round(2)

orders = df[["OrderID", "CustomerID", "OrderDate", "Category", "Product",
             "Quantity", "UnitPrice", "Discount", "Revenue"]].copy()
orders["Revenue"] = orders["Revenue"].round(2)

# Build customers.csv: one row per customer. Region/Segment should be
# constant per customer in this dataset - take the first value seen.
# SignupDate isn't tracked in real retail data the way the old generator
# invented it, so it's approximated as each customer's first order date.
customers = (
    df.groupby("CustomerID")
    .agg(Region=("Region", "first"),
         Segment=("Segment", "first"),
         SignupDate=("OrderDate", "min"))
    .reset_index()
)

os.makedirs("data", exist_ok=True)
customers.to_csv("data/customers.csv", index=False)
orders.to_csv("data/orders.csv", index=False)

print(f"Wrote {len(customers)} customers to data/customers.csv")
print(f"Wrote {len(orders)} orders to data/orders.csv")
if bad_dates:
    print(f"Note: {bad_dates} rows had an unreadable date and were skipped.")
print(f"Total revenue: {orders['Revenue'].sum():,.2f}")
print(f"Date range: {orders['OrderDate'].min()} to {orders['OrderDate'].max()}")
print(f"Categories found: {sorted(orders['Category'].unique())}")
print(f"Segments found: {sorted(customers['Segment'].unique())}")
print(f"Regions found: {sorted(customers['Region'].unique())}")
