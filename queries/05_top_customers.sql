-- Who are the most valuable customers, and how concentrated is revenue?

WITH customer_totals AS (
    SELECT
        c.CustomerID,
        c.Region,
        c.Segment,
        COUNT(o.OrderID)                          AS orders,
        ROUND(SUM(o.Revenue), 0)                  AS total_spend
    FROM orders o
    JOIN customers c ON o.CustomerID = c.CustomerID
    GROUP BY c.CustomerID, c.Region, c.Segment
)
SELECT
    CustomerID,
    Region,
    Segment,
    orders,
    total_spend,
    RANK() OVER (ORDER BY total_spend DESC)       AS spend_rank
FROM customer_totals
ORDER BY spend_rank
LIMIT 10;
