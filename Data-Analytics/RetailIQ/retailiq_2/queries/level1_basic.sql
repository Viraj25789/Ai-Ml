-- LEVEL 1 — Basic SQL

-- Q1: Display all customers.
SELECT * FROM customers;

-- Q2: Display only customer_name, city, state
SELECT customer_name, city, state FROM customers;

-- Q3: Customers who live in Ahmedabad
SELECT * FROM customers WHERE city = 'Ahmedabad';

-- Q4: Premium customers
SELECT * FROM customers WHERE customer_type = 'Premium';

-- Q5: Products with price greater than ₹50,000
SELECT * FROM products WHERE price > 50000;

-- Q6: Products whose stock is less than 10
SELECT * FROM products WHERE stock < 10;

-- Q7: Products with rating greater than 4.5
SELECT * FROM products WHERE rating > 4.5;

-- Q8: Products between ₹5,000 and ₹50,000
SELECT * FROM products WHERE price BETWEEN 5000 AND 50000;

-- Q9: Customers whose name starts with 'A'
SELECT * FROM customers WHERE customer_name LIKE 'A%';

-- Q10: Customers whose name contains 'Shah'
SELECT * FROM customers WHERE customer_name LIKE '%Shah%';

-- Q11: Products sorted from highest price to lowest
SELECT * FROM products ORDER BY price DESC;

-- Q12: The 5 most expensive products
SELECT * FROM products ORDER BY price DESC LIMIT 5;

-- Q13: All different payment methods
SELECT DISTINCT payment_method FROM orders;

-- Q14: All different customer types
SELECT DISTINCT customer_type FROM customers;

-- Q15: Products supplied by Apple or Samsung
SELECT * FROM products WHERE supplier IN ('Apple', 'Samsung');
