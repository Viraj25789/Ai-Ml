-- RetailIQ Schema
-- A realistic Indian electronics-retail schema: customers, categories, products,
-- employees, orders, order_items. Built to match the SQL practice questions
-- (customer types, cities, suppliers, payment methods, discounts, etc.)

CREATE TABLE categories (
    category_id     INTEGER PRIMARY KEY,
    category_name   TEXT NOT NULL
);

CREATE TABLE customers (
    customer_id     INTEGER PRIMARY KEY,
    customer_name   TEXT NOT NULL,
    city            TEXT NOT NULL,
    state           TEXT NOT NULL,
    customer_type   TEXT NOT NULL CHECK (customer_type IN ('Premium', 'Regular', 'New')),
    signup_date     TEXT NOT NULL
);

CREATE TABLE products (
    product_id      INTEGER PRIMARY KEY,
    product_name    TEXT NOT NULL,
    category_id     INTEGER NOT NULL REFERENCES categories(category_id),
    supplier        TEXT NOT NULL,
    price           REAL NOT NULL,
    stock           INTEGER NOT NULL,
    rating          REAL NOT NULL
);

CREATE TABLE employees (
    employee_id     INTEGER PRIMARY KEY,
    employee_name   TEXT NOT NULL,
    department      TEXT NOT NULL,
    salary          REAL NOT NULL,
    hire_date       TEXT NOT NULL
);

CREATE TABLE orders (
    order_id        INTEGER PRIMARY KEY,
    customer_id     INTEGER NOT NULL REFERENCES customers(customer_id),
    employee_id     INTEGER NOT NULL REFERENCES employees(employee_id),
    order_date      TEXT NOT NULL,
    payment_method  TEXT NOT NULL CHECK (payment_method IN ('UPI', 'Credit Card', 'Debit Card', 'Cash', 'Net Banking'))
);

CREATE TABLE order_items (
    order_item_id   INTEGER PRIMARY KEY,
    order_id        INTEGER NOT NULL REFERENCES orders(order_id),
    product_id      INTEGER NOT NULL REFERENCES products(product_id),
    quantity        INTEGER NOT NULL,
    unit_price      REAL NOT NULL,
    discount        REAL NOT NULL DEFAULT 0 -- e.g. 0.10 = 10% off
);
