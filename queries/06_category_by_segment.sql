-- Do different customer types buy different things?

SELECT
    c.Segment,
    o.Category,
    COUNT(*)                                      AS orders,
    ROUND(SUM(o.Revenue), 0)                      AS revenue
FROM orders o
JOIN customers c ON o.CustomerID = c.CustomerID
GROUP BY c.Segment, o.Category
ORDER BY c.Segment, revenue DESC;
