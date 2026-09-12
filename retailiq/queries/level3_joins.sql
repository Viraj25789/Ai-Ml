-- LEVEL 3 — JOIN Practice

-- Q29: Each product with its category name
SELECT p.product_name, c.category_name
FROM products p
JOIN categories c ON p.category_id = c.category_id;

-- Q30: Every product, including products never ordered (LEFT JOIN from products)
SELECT p.product_name, oi.order_item_id
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id;

-- Q31: Each order with order_id, customer_name, order_date, payment_method
SELECT o.order_id, c.customer_name, o.order_date, o.payment_method
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;

-- Q32: order_id, customer_name, product_name, quantity (multiple tables)
SELECT o.order_id, c.customer_name, p.product_name, oi.quantity
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;

-- Q33: Customers who have placed at least one order
SELECT DISTINCT c.*
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id;

-- Q34: Customers who have never placed an order
SELECT c.*
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;

-- Q35: Products that have never been ordered
SELECT p.*
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
WHERE oi.order_item_id IS NULL;

-- Q36: Each order with the employee who handled it
SELECT o.order_id, e.employee_name, o.order_date
FROM orders o
JOIN employees e ON o.employee_id = e.employee_id;

-- Q37: customer_name, order_id, product_name, category_name, quantity
SELECT c.customer_name, o.order_id, p.product_name, cat.category_name, oi.quantity
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id;
