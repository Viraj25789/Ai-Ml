-- LEVEL 2 — Aggregation

-- Q16: How many customers are there?
SELECT COUNT(*) AS total_customers FROM customers;

-- Q17: How many products are there?
SELECT COUNT(*) AS total_products FROM products;

-- Q18: Average product price
SELECT AVG(price) AS avg_price FROM products;

-- Q19: Highest product price
SELECT MAX(price) AS highest_price FROM products;

-- Q20: Lowest product price
SELECT MIN(price) AS lowest_price FROM products;

-- Q21: Total stock of all products
SELECT SUM(stock) AS total_stock FROM products;

-- Q22: Average salary of employees
SELECT AVG(salary) AS avg_salary FROM employees;

-- Q23: Highest employee salary
SELECT MAX(salary) AS highest_salary FROM employees;

-- Q24: Count employees in each department
SELECT department, COUNT(*) AS employee_count
FROM employees
GROUP BY department;

-- Q25: Average salary for each department
SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department;

-- Q26: Highest-priced product in each category
SELECT c.category_name, MAX(p.price) AS highest_price
FROM products p
JOIN categories c ON p.category_id = c.category_id
GROUP BY c.category_name;

-- Q27: Number of products in each category
SELECT c.category_name, COUNT(*) AS product_count
FROM products p
JOIN categories c ON p.category_id = c.category_id
GROUP BY c.category_name;

-- Q28: Categories having more than 2 products
SELECT c.category_name, COUNT(*) AS product_count
FROM products p
JOIN categories c ON p.category_id = c.category_id
GROUP BY c.category_name
HAVING COUNT(*) > 2;
