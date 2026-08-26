-- Show the name and price of all products.
SELECT name, price FROM products;

-- Show all products where the category is 'Electronics'.
SELECT * FROM products WHERE category = 'Electronics';

-- Group products by category. Show each category once.
SELECT category FROM products GROUP BY category;

-- Show categories that have more than 1 product.
SELECT category, COUNT(*) FROM products
GROUP BY category
HAVING COUNT(*) > 1;

-- Show all products sorted by price in ascending order.
SELECT * FROM products ORDER BY price ASC;

-- Show only the first 3 products from the table.
SELECT * FROM products LIMIT 3;

-- Show product name as "Item\_Name" and price as "Item\_Price".
SELECT name AS Item_Name, price AS Item_Price FROM products;

-- Show all the unique categories from the products table.
SELECT DISTINCT category FROM products;