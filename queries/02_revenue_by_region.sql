-- Which regions bring in the most money?
-- Needs a JOIN: region lives on the customer, revenue lives on the order.

SELECT
    c.Region,
    COUNT(DISTINCT c.CustomerID)                  AS customers,
    COUNT(o.OrderID)                              AS orders,
    ROUND(SUM(o.Revenue), 0)                      AS revenue,
    ROUND(SUM(o.Revenue) / COUNT(DISTINCT c.CustomerID), 0)
                                                  AS revenue_per_customer
FROM orders o
JOIN customers c ON o.CustomerID = c.CustomerID
GROUP BY c.Region
ORDER BY revenue DESC;
