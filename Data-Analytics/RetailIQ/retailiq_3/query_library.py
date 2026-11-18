"""
query_library.py
All 60 practiced SQL queries, each paired with a plain-English description
and a few extra phrasings ("keywords") a person might actually type. The
keywords widen the retrieval corpus so short questions like "top customers"
don't just match on trivial word overlap with the wrong query — they're
part of the search index but never shown to the user.
"""

# Extra natural phrasings for the queries people are most likely to ask,
# used only to widen the TF-IDF corpus (not shown in the UI).
ALIASES = {
    "Q6": "low stock products running out of stock inventory alert restock",
    "Q28": "categories with many products wide catalog categories",
    "Q34": "inactive customers customers with no orders churned customers",
    "Q35": "dead stock unsold products products with no sales never sold",
    "Q40": "bestselling products top products best sellers",
    "Q44": "top customers best customers highest spender who are my top customers biggest customer",
    "Q45": "best employee top performing employee which employee sold the most best salesperson top staff",
    "Q46": "employee with highest sales value top earner staff performance",
    "Q47": "best selling product most sold product most popular item",
    "Q48": "top selling category best category most popular category",
    "Q49": "revenue by month monthly sales trend revenue over time",
    "Q56": "most expensive category premium category priciest category",
    "Q57": "big spenders high value customers heavy spenders",
    "Q22": "payroll average pay department costs",
    "Q25": "department payroll costs salary by team",
}


QUERY_LIBRARY = [
    {
        "id": "Q1",
        "keywords": ALIASES.get("Q1", ""),
        "question": "Display all customers.",
        "sql": """SELECT * FROM customers""",
    },
    {
        "id": "Q2",
        "keywords": ALIASES.get("Q2", ""),
        "question": "Display only customer_name, city, state",
        "sql": """SELECT customer_name, city, state FROM customers""",
    },
    {
        "id": "Q3",
        "keywords": ALIASES.get("Q3", ""),
        "question": "Customers who live in Ahmedabad",
        "sql": """SELECT * FROM customers WHERE city = 'Ahmedabad'""",
    },
    {
        "id": "Q4",
        "keywords": ALIASES.get("Q4", ""),
        "question": "Premium customers",
        "sql": """SELECT * FROM customers WHERE customer_type = 'Premium'""",
    },
    {
        "id": "Q5",
        "keywords": ALIASES.get("Q5", ""),
        "question": "Products with price greater than ₹50,000",
        "sql": """SELECT * FROM products WHERE price > 50000""",
    },
    {
        "id": "Q6",
        "keywords": ALIASES.get("Q6", ""),
        "question": "Products whose stock is less than 10",
        "sql": """SELECT * FROM products WHERE stock < 10""",
    },
    {
        "id": "Q7",
        "keywords": ALIASES.get("Q7", ""),
        "question": "Products with rating greater than 4.5",
        "sql": """SELECT * FROM products WHERE rating > 4.5""",
    },
    {
        "id": "Q8",
        "keywords": ALIASES.get("Q8", ""),
        "question": "Products between ₹5,000 and ₹50,000",
        "sql": """SELECT * FROM products WHERE price BETWEEN 5000 AND 50000""",
    },
    {
        "id": "Q9",
        "keywords": ALIASES.get("Q9", ""),
        "question": "Customers whose name starts with 'A'",
        "sql": """SELECT * FROM customers WHERE customer_name LIKE 'A%'""",
    },
    {
        "id": "Q10",
        "keywords": ALIASES.get("Q10", ""),
        "question": "Customers whose name contains 'Shah'",
        "sql": """SELECT * FROM customers WHERE customer_name LIKE '%Shah%'""",
    },
    {
        "id": "Q11",
        "keywords": ALIASES.get("Q11", ""),
        "question": "Products sorted from highest price to lowest",
        "sql": """SELECT * FROM products ORDER BY price DESC""",
    },
    {
        "id": "Q12",
        "keywords": ALIASES.get("Q12", ""),
        "question": "The 5 most expensive products",
        "sql": """SELECT * FROM products ORDER BY price DESC LIMIT 5""",
    },
    {
        "id": "Q13",
        "keywords": ALIASES.get("Q13", ""),
        "question": "All different payment methods",
        "sql": """SELECT DISTINCT payment_method FROM orders""",
    },
    {
        "id": "Q14",
        "keywords": ALIASES.get("Q14", ""),
        "question": "All different customer types",
        "sql": """SELECT DISTINCT customer_type FROM customers""",
    },
    {
        "id": "Q15",
        "keywords": ALIASES.get("Q15", ""),
        "question": "Products supplied by Apple or Samsung",
        "sql": """SELECT * FROM products WHERE supplier IN ('Apple', 'Samsung')""",
    },
    {
        "id": "Q16",
        "keywords": ALIASES.get("Q16", ""),
        "question": "How many customers are there?",
        "sql": """SELECT COUNT(*) AS total_customers FROM customers""",
    },
    {
        "id": "Q17",
        "keywords": ALIASES.get("Q17", ""),
        "question": "How many products are there?",
        "sql": """SELECT COUNT(*) AS total_products FROM products""",
    },
    {
        "id": "Q18",
        "keywords": ALIASES.get("Q18", ""),
        "question": "Average product price",
        "sql": """SELECT AVG(price) AS avg_price FROM products""",
    },
    {
        "id": "Q19",
        "keywords": ALIASES.get("Q19", ""),
        "question": "Highest product price",
        "sql": """SELECT MAX(price) AS highest_price FROM products""",
    },
    {
        "id": "Q20",
        "keywords": ALIASES.get("Q20", ""),
        "question": "Lowest product price",
        "sql": """SELECT MIN(price) AS lowest_price FROM products""",
    },
    {
        "id": "Q21",
        "keywords": ALIASES.get("Q21", ""),
        "question": "Total stock of all products",
        "sql": """SELECT SUM(stock) AS total_stock FROM products""",
    },
    {
        "id": "Q22",
        "keywords": ALIASES.get("Q22", ""),
        "question": "Average salary of employees",
        "sql": """SELECT AVG(salary) AS avg_salary FROM employees""",
    },
    {
        "id": "Q23",
        "keywords": ALIASES.get("Q23", ""),
        "question": "Highest employee salary",
        "sql": """SELECT MAX(salary) AS highest_salary FROM employees""",
    },
    {
        "id": "Q24",
        "keywords": ALIASES.get("Q24", ""),
        "question": "Count employees in each department",
        "sql": """SELECT department, COUNT(*) AS employee_count
FROM employees
GROUP BY department""",
    },
    {
        "id": "Q25",
        "keywords": ALIASES.get("Q25", ""),
        "question": "Average salary for each department",
        "sql": """SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department""",
    },
    {
        "id": "Q26",
        "keywords": ALIASES.get("Q26", ""),
        "question": "Highest-priced product in each category",
        "sql": """SELECT c.category_name, MAX(p.price) AS highest_price
FROM products p
JOIN categories c ON p.category_id = c.category_id
GROUP BY c.category_name""",
    },
    {
        "id": "Q27",
        "keywords": ALIASES.get("Q27", ""),
        "question": "Number of products in each category",
        "sql": """SELECT c.category_name, COUNT(*) AS product_count
FROM products p
JOIN categories c ON p.category_id = c.category_id
GROUP BY c.category_name""",
    },
    {
        "id": "Q28",
        "keywords": ALIASES.get("Q28", ""),
        "question": "Categories having more than 2 products",
        "sql": """SELECT c.category_name, COUNT(*) AS product_count
FROM products p
JOIN categories c ON p.category_id = c.category_id
GROUP BY c.category_name
HAVING COUNT(*) > 2""",
    },
    {
        "id": "Q29",
        "keywords": ALIASES.get("Q29", ""),
        "question": "Each product with its category name",
        "sql": """SELECT p.product_name, c.category_name
FROM products p
JOIN categories c ON p.category_id = c.category_id""",
    },
    {
        "id": "Q30",
        "keywords": ALIASES.get("Q30", ""),
        "question": "Every product, including products never ordered (LEFT JOIN from products)",
        "sql": """SELECT p.product_name, oi.order_item_id
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id""",
    },
    {
        "id": "Q31",
        "keywords": ALIASES.get("Q31", ""),
        "question": "Each order with order_id, customer_name, order_date, payment_method",
        "sql": """SELECT o.order_id, c.customer_name, o.order_date, o.payment_method
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id""",
    },
    {
        "id": "Q32",
        "keywords": ALIASES.get("Q32", ""),
        "question": "order_id, customer_name, product_name, quantity (multiple tables)",
        "sql": """SELECT o.order_id, c.customer_name, p.product_name, oi.quantity
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id""",
    },
    {
        "id": "Q33",
        "keywords": ALIASES.get("Q33", ""),
        "question": "Customers who have placed at least one order",
        "sql": """SELECT DISTINCT c.*
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id""",
    },
    {
        "id": "Q34",
        "keywords": ALIASES.get("Q34", ""),
        "question": "Customers who have never placed an order",
        "sql": """SELECT c.*
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL""",
    },
    {
        "id": "Q35",
        "keywords": ALIASES.get("Q35", ""),
        "question": "Products that have never been ordered",
        "sql": """SELECT p.*
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
WHERE oi.order_item_id IS NULL""",
    },
    {
        "id": "Q36",
        "keywords": ALIASES.get("Q36", ""),
        "question": "Each order with the employee who handled it",
        "sql": """SELECT o.order_id, e.employee_name, o.order_date
FROM orders o
JOIN employees e ON o.employee_id = e.employee_id""",
    },
    {
        "id": "Q37",
        "keywords": ALIASES.get("Q37", ""),
        "question": "customer_name, order_id, product_name, category_name, quantity",
        "sql": """SELECT c.customer_name, o.order_id, p.product_name, cat.category_name, oi.quantity
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id""",
    },
    {
        "id": "Q38",
        "keywords": ALIASES.get("Q38", ""),
        "question": "Total quantity sold for each product",
        "sql": """SELECT p.product_name, SUM(oi.quantity) AS total_quantity
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_name""",
    },
    {
        "id": "Q39",
        "keywords": ALIASES.get("Q39", ""),
        "question": "Total revenue generated by each product (quantity * unit_price * (1 - discount))",
        "sql": """SELECT p.product_name,
       SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_name""",
    },
    {
        "id": "Q40",
        "keywords": ALIASES.get("Q40", ""),
        "question": "Top 5 products by revenue",
        "sql": """SELECT p.product_name,
       SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_revenue DESC
LIMIT 5""",
    },
    {
        "id": "Q41",
        "keywords": ALIASES.get("Q41", ""),
        "question": "Total revenue generated by each category",
        "sql": """SELECT cat.category_name,
       SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id
GROUP BY cat.category_name""",
    },
    {
        "id": "Q42",
        "keywords": ALIASES.get("Q42", ""),
        "question": "Number of orders placed by each customer",
        "sql": """SELECT c.customer_name, COUNT(o.order_id) AS order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_name""",
    },
    {
        "id": "Q43",
        "keywords": ALIASES.get("Q43", ""),
        "question": "Customers who have placed more than 1 order",
        "sql": """SELECT c.customer_name, COUNT(o.order_id) AS order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_name
HAVING COUNT(o.order_id) > 1""",
    },
    {
        "id": "Q44",
        "keywords": ALIASES.get("Q44", ""),
        "question": "The customer who generated the highest total revenue",
        "sql": """SELECT c.customer_name,
       SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_name
ORDER BY total_revenue DESC
LIMIT 1""",
    },
    {
        "id": "Q45",
        "keywords": ALIASES.get("Q45", ""),
        "question": "The employee who handled the highest number of orders",
        "sql": """SELECT e.employee_name, COUNT(o.order_id) AS order_count
FROM employees e
JOIN orders o ON e.employee_id = o.employee_id
GROUP BY e.employee_name
ORDER BY order_count DESC
LIMIT 1""",
    },
    {
        "id": "Q46",
        "keywords": ALIASES.get("Q46", ""),
        "question": "The employee who generated the highest order value",
        "sql": """SELECT e.employee_name,
       SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total_value
FROM employees e
JOIN orders o ON e.employee_id = o.employee_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY e.employee_name
ORDER BY total_value DESC
LIMIT 1""",
    },
    {
        "id": "Q47",
        "keywords": ALIASES.get("Q47", ""),
        "question": "Most popular product based on total quantity sold",
        "sql": """SELECT p.product_name, SUM(oi.quantity) AS total_quantity
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_quantity DESC
LIMIT 1""",
    },
    {
        "id": "Q48",
        "keywords": ALIASES.get("Q48", ""),
        "question": "Most popular category based on total quantity sold",
        "sql": """SELECT cat.category_name, SUM(oi.quantity) AS total_quantity
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id
GROUP BY cat.category_name
ORDER BY total_quantity DESC
LIMIT 1""",
    },
    {
        "id": "Q49",
        "keywords": ALIASES.get("Q49", ""),
        "question": "Total revenue for each month",
        "sql": """SELECT strftime('%Y-%m', o.order_date) AS month,
       SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY month
ORDER BY month""",
    },
    {
        "id": "Q50",
        "keywords": ALIASES.get("Q50", ""),
        "question": "Total revenue generated from Premium customers",
        "sql": """SELECT SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS premium_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE c.customer_type = 'Premium'""",
    },
    {
        "id": "Q51",
        "keywords": ALIASES.get("Q51", ""),
        "question": "Second-highest product price",
        "sql": """SELECT DISTINCT price FROM products
ORDER BY price DESC
LIMIT 1 OFFSET 1""",
    },
    {
        "id": "Q52",
        "keywords": ALIASES.get("Q52", ""),
        "question": "Third-highest product price",
        "sql": """SELECT DISTINCT price FROM products
ORDER BY price DESC
LIMIT 1 OFFSET 2""",
    },
    {
        "id": "Q53",
        "keywords": ALIASES.get("Q53", ""),
        "question": "Second-highest salary",
        "sql": """SELECT DISTINCT salary FROM employees
ORDER BY salary DESC
LIMIT 1 OFFSET 1""",
    },
    {
        "id": "Q54",
        "keywords": ALIASES.get("Q54", ""),
        "question": "Employees earning more than the average employee salary",
        "sql": """SELECT * FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees)""",
    },
    {
        "id": "Q55",
        "keywords": ALIASES.get("Q55", ""),
        "question": "Products whose price is greater than the average product price",
        "sql": """SELECT * FROM products
WHERE price > (SELECT AVG(price) FROM products)""",
    },
    {
        "id": "Q56",
        "keywords": ALIASES.get("Q56", ""),
        "question": "Category having the highest average product price",
        "sql": """SELECT cat.category_name, AVG(p.price) AS avg_price
FROM products p
JOIN categories cat ON p.category_id = cat.category_id
GROUP BY cat.category_name
ORDER BY avg_price DESC
LIMIT 1""",
    },
    {
        "id": "Q57",
        "keywords": ALIASES.get("Q57", ""),
        "question": "Customers whose total spending is greater than the average customer spending",
        "sql": """WITH customer_spend AS (
    SELECT c.customer_id, c.customer_name,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total_spend
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.customer_name
)
SELECT * FROM customer_spend
WHERE total_spend > (SELECT AVG(total_spend) FROM customer_spend)""",
    },
    {
        "id": "Q58",
        "keywords": ALIASES.get("Q58", ""),
        "question": "Highest-priced product in each category (with product name, using window function)",
        "sql": """SELECT category_name, product_name, price
FROM (
    SELECT cat.category_name, p.product_name, p.price,
           RANK() OVER (PARTITION BY cat.category_name ORDER BY p.price DESC) AS rnk
    FROM products p
    JOIN categories cat ON p.category_id = cat.category_id
)
WHERE rnk = 1""",
    },
    {
        "id": "Q59",
        "keywords": ALIASES.get("Q59", ""),
        "question": "Customer with the most orders",
        "sql": """SELECT c.customer_name, COUNT(o.order_id) AS order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_name
ORDER BY order_count DESC
LIMIT 1""",
    },
    {
        "id": "Q60",
        "keywords": ALIASES.get("Q60", ""),
        "question": "Product with the highest total quantity sold",
        "sql": """SELECT p.product_name, SUM(oi.quantity) AS total_quantity
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_quantity DESC
LIMIT 1""",
    },
]