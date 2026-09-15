"""
load_real_data.py
Replaces the synthetic dataset with a real one: the well-known "Superstore
Sales" dataset (5,496 orders, 795 customers, 1,263 products, 2009-2012).

This is the honest, slightly messy version of "connect it to real data" —
a flat CSV with one row per order line, no separate customer/product/
employee tables, and category values that don't match the synthetic
generator's assumptions. Loading it means real ETL: deriving dimension
tables from a fact table, and being upfront about what the source data
doesn't have (no employee/salesperson field, no true payment method).

What's real vs. filled in, so you can describe this accurately in an
interview:
  - Customers, products, categories, orders, order dates, quantities,
    prices, and discounts are all real, from the source dataset.
  - Employees don't exist in the source data — this script generates a
    small placeholder staff list and assigns orders to them randomly,
    purely so the schema's employee_id foreign key has something to
    reference. Don't present "employee who handled the most orders" as a
    real business insight if you load this dataset.
  - The source has no payment-method field, only a shipping mode
    (Regular Air / Delivery Truck / Express Air) — stored as-is in the
    payment_method column since the schema doesn't distinguish them.
    It's shipping mode data wearing a different column name, not payment
    data.
  - stock and rating on products aren't in the source data either;
    they're filled with plausible placeholder values.

Source: https://raw.githubusercontent.com/curran/data/gh-pages/superstoreSales/superstoreSales.csv
(a long-standing public mirror of the classic Kaggle/Tableau "Superstore"
sample dataset — this URL is fetched directly, no Kaggle login needed)

Run: python load_real_data.py
"""
import os
import random
import sys

import pandas as pd
import requests

import db

random.seed(7)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_URL = "https://raw.githubusercontent.com/curran/data/gh-pages/superstoreSales/superstoreSales.csv"
LOCAL_CACHE = os.path.join(BASE_DIR, "superstoreSales.csv")

EMPLOYEE_NAMES = [
    "Alex Morgan", "Jordan Lee", "Sam Patel", "Taylor Kim", "Casey Nguyen",
    "Riley Chen", "Morgan Davis", "Jamie Rivera",
]
DEPARTMENTS = ["Sales", "Support", "Logistics", "Marketing"]

# The source dataset's "Customer Segment" is a real business dimension, but
# the values don't match the synthetic generator's Premium/Regular/New
# scheme. Rather than force a fake mapping, we keep the real segment names
# — the schema's customer_type column no longer has a CHECK constraint
# restricting it, specifically to allow this.


def fetch_source_csv() -> pd.DataFrame:
    if os.path.exists(LOCAL_CACHE):
        print(f"Using cached {LOCAL_CACHE}")
        return pd.read_csv(LOCAL_CACHE, encoding="latin1")

    print(f"Downloading {SOURCE_URL} ...")
    response = requests.get(SOURCE_URL, timeout=30)
    response.raise_for_status()
    with open(LOCAL_CACHE, "wb") as f:
        f.write(response.content)
    return pd.read_csv(LOCAL_CACHE, encoding="latin1")


def build(force: bool = False):
    if not force:
        try:
            existing = db.run_query("SELECT COUNT(*) AS n FROM customers").iloc[0]["n"]
            if existing > 0:
                print("Database already has data. Run with force=True to replace it.")
                return
        except Exception:
            pass  # tables don't exist yet — fine, continue

    raw = fetch_source_csv()
    raw["Order Date"] = pd.to_datetime(raw["Order Date"], format="%m/%d/%Y")

    schema_file = "schema_postgres.sql" if db.is_postgres() else "schema.sql"
    with open(os.path.join(BASE_DIR, schema_file)) as f:
        db.executescript(f.read())

    # ---- Categories ----
    category_names = sorted(raw["Product Category"].unique())
    categories = pd.DataFrame({
        "category_id": range(1, len(category_names) + 1),
        "category_name": category_names,
    })
    cat_id_map = {name: i + 1 for i, name in enumerate(category_names)}

    # ---- Products ---- (one row per unique product name; price = mean
    # unit price observed for that product; stock/rating aren't in the
    # source data, filled with plausible placeholders)
    product_agg = raw.groupby("Product Name").agg(
        category=("Product Category", "first"),
        price=("Unit Price", "mean"),
    ).reset_index()
    product_agg["product_id"] = range(1, len(product_agg) + 1)
    product_id_map = dict(zip(product_agg["Product Name"], product_agg["product_id"]))
    products = pd.DataFrame({
        "product_id": product_agg["product_id"],
        "product_name": product_agg["Product Name"],
        "category_id": product_agg["category"].map(cat_id_map),
        "supplier": "Unknown",  # not present in source data
        "price": product_agg["price"].round(2),
        "stock": [random.randint(5, 150) for _ in range(len(product_agg))],
        "rating": [round(random.uniform(3.5, 5.0), 1) for _ in range(len(product_agg))],
    })

    # ---- Customers ---- (Province/Region stand in for city/state; the
    # source is a North American dataset so these aren't literal cities)
    customer_agg = raw.groupby("Customer Name").agg(
        city=("Province", "first"),
        state=("Region", "first"),
        customer_type=("Customer Segment", "first"),
    ).reset_index()
    customer_agg["customer_id"] = range(1, len(customer_agg) + 1)
    customer_id_map = dict(zip(customer_agg["Customer Name"], customer_agg["customer_id"]))
    customers = pd.DataFrame({
        "customer_id": customer_agg["customer_id"],
        "customer_name": customer_agg["Customer Name"],
        "city": customer_agg["city"],
        "state": customer_agg["state"],
        "customer_type": customer_agg["customer_type"],
        "signup_date": raw["Order Date"].min().date(),  # unknown in source; uses earliest order as a floor
    })

    # ---- Employees ---- (not in source data — see module docstring)
    employees = pd.DataFrame({
        "employee_id": range(1, len(EMPLOYEE_NAMES) + 1),
        "employee_name": EMPLOYEE_NAMES,
        "department": [random.choice(DEPARTMENTS) for _ in EMPLOYEE_NAMES],
        "salary": [random.randint(28, 95) * 1000 for _ in EMPLOYEE_NAMES],
        "hire_date": raw["Order Date"].min().date(),
    })

    # ---- Orders + order_items ----
    order_dates = raw.groupby("Order ID")["Order Date"].first()
    unique_order_ids = sorted(raw["Order ID"].unique())
    order_id_map = {orig: i + 1 for i, orig in enumerate(unique_order_ids)}

    order_customer = raw.groupby("Order ID")["Customer Name"].first()
    ship_mode_by_order = raw.groupby("Order ID")["Ship Mode"].first()
    orders = pd.DataFrame({
        "order_id": [order_id_map[o] for o in unique_order_ids],
        "customer_id": [customer_id_map[order_customer[o]] for o in unique_order_ids],
        "employee_id": [random.randint(1, len(EMPLOYEE_NAMES)) for _ in unique_order_ids],
        "order_date": [order_dates[o].date() for o in unique_order_ids],
        "payment_method": [ship_mode_by_order[o] for o in unique_order_ids],
    })

    order_items = pd.DataFrame({
        "order_item_id": range(1, len(raw) + 1),
        "order_id": raw["Order ID"].map(order_id_map),
        "product_id": raw["Product Name"].map(product_id_map),
        "quantity": raw["Order Quantity"],
        "unit_price": raw["Unit Price"].round(2),
        "discount": raw["Discount"],
    })

    engine = db.get_engine()
    categories.to_sql("categories", engine, if_exists="append", index=False)
    products.to_sql("products", engine, if_exists="append", index=False)
    customers.to_sql("customers", engine, if_exists="append", index=False)
    employees.to_sql("employees", engine, if_exists="append", index=False)
    orders.to_sql("orders", engine, if_exists="append", index=False)
    order_items.to_sql("order_items", engine, if_exists="append", index=False)

    if db.is_postgres():
        import seed_data
        seed_data._reset_postgres_sequences()

    print(
        f"Loaded real Superstore data: {len(customers)} customers, {len(products)} products, "
        f"{len(categories)} categories, {len(employees)} placeholder employees, "
        f"{len(orders)} orders, {len(order_items)} order items."
    )
    print(
        "Note: employee assignments and payment_method (actually shipping mode) are "
        "not real business signals in this dataset — see the module docstring."
    )


if __name__ == "__main__":
    force = "--force" in sys.argv
    build(force=force)
