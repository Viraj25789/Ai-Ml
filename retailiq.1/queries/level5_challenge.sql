-- LEVEL 5 — Interview Challenge

-- Q51: Second-highest product price
SELECT DISTINCT price FROM products
ORDER BY price DESC
LIMIT 1 OFFSET 1;

-- Q52: Third-highest product price
SELECT DISTINCT price FROM products
ORDER BY price DESC
LIMIT 1 OFFSET 2;

-- Q53: Second-highest salary
SELECT DISTINCT salary FROM employees
ORDER BY salary DESC
LIMIT 1 OFFSET 1;

-- Q54: Employees earning more than the average employee salary
SELECT * FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- Q55: Products whose price is greater than the average product price
SELECT * FROM products
WHERE price > (SELECT AVG(price) FROM products);

-- Q56: Category having the highest average product price
SELECT cat.category_name, AVG(p.price) AS avg_price
FROM products p
JOIN categories cat ON p.category_id = cat.category_id
GROUP BY cat.category_name
ORDER BY avg_price DESC
LIMIT 1;

-- Q57: Customers whose total spending is greater than the average customer spending
WITH customer_spend AS (
    SELECT c.customer_id, c.customer_name,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total_spend
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.customer_name
)
SELECT * FROM customer_spend
WHERE total_spend > (SELECT AVG(total_spend) FROM customer_spend);

-- Q58: Highest-priced product in each category (with product name, using window function)
SELECT category_name, product_name, price
FROM (
    SELECT cat.category_name, p.product_name, p.price,
           RANK() OVER (PARTITION BY cat.category_name ORDER BY p.price DESC) AS rnk
    FROM products p
    JOIN categories cat ON p.category_id = cat.category_id
)
WHERE rnk = 1;

-- Q59: Customer with the most orders
SELECT c.customer_name, COUNT(o.order_id) AS order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_name
ORDER BY order_count DESC
LIMIT 1;

-- Q60: Product with the highest total quantity sold
SELECT p.product_name, SUM(oi.quantity) AS total_quantity
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_quantity DESC
LIMIT 1;
