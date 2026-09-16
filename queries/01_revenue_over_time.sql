-- How has revenue moved month by month?

SELECT
    substr(OrderDate, 1, 7)                       AS month,
    COUNT(*)                                      AS orders,
    ROUND(SUM(Revenue), 0)                        AS revenue,
    ROUND(AVG(Revenue), 0)                        AS avg_order_value
FROM orders
GROUP BY month
ORDER BY month;
