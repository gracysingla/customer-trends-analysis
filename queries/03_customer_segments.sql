-- How do the three customer types differ?
-- Segment sits on the customer table, so this is another JOIN.

SELECT
    c.Segment,
    COUNT(DISTINCT c.CustomerID)                  AS customers,
    COUNT(o.OrderID)                              AS orders,
    ROUND(SUM(o.Revenue), 0)                      AS revenue,
    ROUND(AVG(o.Revenue), 0)                      AS avg_order_value,
    ROUND(100.0 * SUM(o.Revenue) / (SELECT SUM(Revenue) FROM orders), 1)
                                                  AS pct_of_total_revenue
FROM orders o
JOIN customers c ON o.CustomerID = c.CustomerID
GROUP BY c.Segment
ORDER BY revenue DESC;
