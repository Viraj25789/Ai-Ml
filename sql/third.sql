-- Display the name and price of the cheapest product in the entire table
select name, price from products 
where price = (select min(price) from products)


-- Find the average price of products that belong to the 'Home & Kitchen' or 'Fitness' category, round of to 2
select category, round(avg(price),2) from products 
where category in ('Home & Kitchen','Fitness')
group by category


-- Show product names and stock quantity where the product is available, stock is more than 50, and price is not equal to ₹299.
select name, stock_quantity from products 
where available = TRUE and stock_quantity>50 and price!=299


-- Find the most expensive product in each category (name and price).
select category, max(price) from products 
group by category


-- Show all unique categories in uppercase, sorted in descending order.
select distinct upper(category) as upper_catategory
from products 
order by upper_catategory desc