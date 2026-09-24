--1.Top 5 products by revenue
SELECT p.name, SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.id
GROUP BY p.name
ORDER BY revenue DESC
LIMIT 5;

-- 2.Monthly revenue for the last 12 months
SELECT DATE_TRUNC('month', order_date) AS month, SUM(total) AS revenue
FROM orders
GROUP BY month
ORDER BY month;

-- 3.Customers who have never ordered
SELECT u.name
FROM users u
LEFT JOIN orders o ON u.id = o.customer_id
WHERE o.id IS NULL;

-- 4.Categories with average order value above 100
SELECT c.name, AVG(oi.quantity * oi.unit_price) AS avg_order_value
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN categories c ON p.category_id = c.id
GROUP BY c.name
HAVING AVG(oi.quantity * oi.unit_price) > 100;

-- 5.Each customer's most recent order
SELECT customer_id, order_date, id
FROM (
  SELECT customer_id, order_date, id,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
  FROM orders
) ranked
WHERE rn = 1;

-- 6.Running total of revenue by day
SELECT order_date, SUM(total) OVER (ORDER BY order_date) AS running_total
FROM orders
ORDER BY order_date;

-- 7.Label each order as Small/Medium/Large by amount
SELECT id, total,
  CASE
    WHEN total < 50 THEN 'Small'
    WHEN total < 200 THEN 'Medium'
    ELSE 'Large'
  END AS size_label
FROM orders;

-- 8.Customers whose total spend is above the overall average
WITH customer_totals AS (
  SELECT customer_id, SUM(total) AS spend
  FROM orders
  GROUP BY customer_id
),
overall_avg AS (
  SELECT AVG(total) AS avg_total FROM orders
)
SELECT customer_id, spend
FROM customer_totals, overall_avg
WHERE spend > avg_total;

--9.Orders with missing shipping addresses shown as "N/A"
SELECT id, COALESCE(shipping_address, 'N/A') AS shipping_address
FROM orders;

--10. Rank products within each category by units sold
SELECT p.name, c.name AS category, SUM(oi.quantity) AS units_sold,
  RANK() OVER (PARTITION BY p.category_id ORDER BY SUM(oi.quantity) DESC) AS rank
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN categories c ON p.category_id = c.id
GROUP BY p.name, c.name, p.category_id
ORDER BY category, rank;