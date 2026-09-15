-- RetailIQ Schema (Postgres variant)
-- Same tables as schema.sql, adapted for Postgres syntax (SERIAL primary
-- keys instead of SQLite's auto-incrementing INTEGER PRIMARY KEY).
-- Used automatically by db.py when a DATABASE_URL is configured.

CREATE TABLE IF NOT EXISTS categories (
    category_id     SERIAL PRIMARY KEY,
    category_name   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id     SERIAL PRIMARY KEY,
    customer_name   TEXT NOT NULL,
    city            TEXT NOT NULL,
    state           TEXT NOT NULL,
    customer_type   TEXT NOT NULL,
    signup_date     DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id      SERIAL PRIMARY KEY,
    product_name    TEXT NOT NULL,
    category_id     INTEGER NOT NULL REFERENCES categories(category_id),
    supplier        TEXT NOT NULL,
    price           REAL NOT NULL,
    stock           INTEGER NOT NULL,
    rating          REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id     SERIAL PRIMARY KEY,
    employee_name   TEXT NOT NULL,
    department      TEXT NOT NULL,
    salary          REAL NOT NULL,
    hire_date       DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id        SERIAL PRIMARY KEY,
    customer_id     INTEGER NOT NULL REFERENCES customers(customer_id),
    employee_id     INTEGER NOT NULL REFERENCES employees(employee_id),
    order_date      DATE NOT NULL,
    payment_method  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id   SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL REFERENCES orders(order_id),
    product_id      INTEGER NOT NULL REFERENCES products(product_id),
    quantity        INTEGER NOT NULL,
    unit_price      REAL NOT NULL,
    discount        REAL NOT NULL DEFAULT 0
);
