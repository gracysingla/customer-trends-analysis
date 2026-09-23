# Customer Trends & Sales Analysis

SQL analysis of customer and sales data, with a dashboard summarising the results.

**The question:** where is revenue coming from, who is buying, and what should the
business do differently?

![Dashboard](output/dashboard.png)

### Power BI version

An interactive version built in Power BI Desktop, with slicers for region, segment and product category.

![Power BI dashboard](output/powerbi-dashboard.png)

The .pbix file is in the repository root.

---

## The data

Two tables, which is how sales data is normally stored:

- **`customers.csv`** — 793 customers, with region, segment and first-order date.
  This dataset doesn't track signups separately, so the date is approximated as
  each customer's earliest recorded order.
- **`orders.csv`** — 9,994 orders, with date, product, category, quantity and revenue.

Because region and segment live on the customer while revenue lives on the order, most
of the analysis needs a **JOIN** between the two.

Source: Kaggle's "Superstore Dataset Final" (real US retail orders). Revenue figures
are in USD, not INR.

Covers January 2014 to December 2017. Total revenue $2,297,200.65.

---

## What I found

**1. Revenue splits almost evenly across three categories — no single leader.** Technology brings in $836,154 (36.4%), Furniture $742,000 (32.3%), and Office
Supplies $719,047 (31.3%). No category dominates the way a simpler story might
suggest — the business isn't carried by one product line.

**2. Home Office is the smallest segment, but spends the most per order.** At $241 average order value, Home Office edges out Corporate ($234) and Consumer
($224) — despite having the fewest customers (148) of the three segments. Segment
size and segment value don't move together here.

**3. Consumer drives half of total revenue, but through volume, not order size.** 409 consumers place 5,191 orders — more than double Corporate's order count — and
generate 50.6% of all revenue. Their average order value is the lowest of the three
segments, so the revenue comes from how often they buy, not how much each order is worth.

**4. Revenue climbs sharply every September–November, in line with the US holiday
shopping season.** The pattern repeats across all four years in the data. November 2017 was the single
highest-revenue month on record at $118,448 — a genuine, recurring seasonal effect,
not a one-off spike.

**What I'd recommend:** revenue per customer is close across all four regions
($2,781–$3,000), so regional differences in total revenue mostly come down to how
many customers each region has, not how valuable those customers are. Central and
South have the fewest customers — growing the customer base there looks like a more
direct lever than trying to change regional buying behaviour.

---

## How it works

Queries live in `/queries`, numbered in the order they build on each other.

| File | What it answers |
|---|---|
| `01_revenue_over_time.sql` | How revenue has moved month by month |
| `02_revenue_by_region.sql` | Which regions bring in the most, and per customer |
| `03_customer_segments.sql` | How the three customer types differ |
| `04_product_performance.sql` | Which products lead within their own category |
| `05_top_customers.sql` | Who the most valuable customers are |
| `06_category_by_segment.sql` | Whether different customer types buy different things |

### The SQL, in plain terms

- **`JOIN`** — combines the two tables on `CustomerID`, so customer details and order
  revenue can be looked at together. Used in most queries here.
- **`GROUP BY`** — collapses many rows into one summary row, e.g. one line per region.
- **CTE (the `WITH` block)** — a named temporary result you build first, then query. In
  `04_product_performance.sql` revenue per product is worked out first, then ranked.
- **Window functions** — a calculation across rows that keeps every row visible.
  `RANK() OVER (PARTITION BY Category ...)` ranks products **within** each category rather
  than against the whole catalogue, and `SUM(...) OVER (PARTITION BY Category)` gives each
  product's share of its own category on the same line.

---

## Running it
python prepare_real_data.py # converts the downloaded Kaggle CSV into data/customers.csv and data/orders.csv
python run_analysis.py # loads into SQLite, runs every query, prints results
python build_dashboard.py # writes output/dashboard.png


Needs `pandas` (`pip install pandas`) and the raw Kaggle file saved as
`superstore_raw.csv` in the project folder — download from Kaggle's
"Superstore Dataset Final". SQLite is used for the analysis itself so there's
nothing else to install; the SQL is standard and runs in MySQL Workbench too.

---

## Files
customer-trends-analysis/
├── README.md
├── prepare_real_data.py
├── run_analysis.py
├── build_dashboard.py
├── data/
│ ├── customers.csv
│ └── orders.csv
├── queries/
│ ├── 01_revenue_over_time.sql
│ ├── 02_revenue_by_region.sql
│ ├── 03_customer_segments.sql
│ ├── 04_product_performance.sql
│ ├── 05_top_customers.sql
│ └── 06_category_by_segment.sql
└── output/
└── dashboard.png

---

## Data source

Dataset: Superstore Sales Dataset (Kaggle, vivek468/superstore-dataset-final).
Converted from its original single-file format into this project's customer/order
structure using `prepare_real_data.py`.
