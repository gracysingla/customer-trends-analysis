-- Which products earn the most, and how do they rank inside their category?
--
--   1. The CTE works out revenue per product first.
--   2. RANK() OVER (PARTITION BY Category ...) ranks products WITHIN each
--      category rather than against the whole catalogue, and keeps every row.

WITH product_stats AS (
    SELECT
        Category,
        Product,
        COUNT(*)                                  AS orders,
        SUM(Quantity)                             AS units_sold,
        ROUND(SUM(Revenue), 0)                    AS revenue
    FROM orders
    GROUP BY Category, Product
)
SELECT
    Category,
    Product,
    orders,
    units_sold,
    revenue,
    RANK() OVER (PARTITION BY Category ORDER BY revenue DESC)
                                                  AS rank_in_category,
    ROUND(100.0 * revenue / SUM(revenue) OVER (PARTITION BY Category), 1)
                                                  AS pct_of_category
FROM product_stats
ORDER BY Category, rank_in_category;
