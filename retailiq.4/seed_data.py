"""
seed_data.py
Generates a realistic synthetic dataset for an Indian electronics retail
business and loads it into whichever database db.py resolves to — a local
SQLite file by default, or a cloud Postgres instance if DATABASE_URL is set.

Uses pandas' to_sql() for the actual inserts so the same code works against
either backend without dialect-specific insert statements.

Run: python seed_data.py
"""
import os
import random
from datetime import date, timedelta

import pandas as pd

import db

random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FIRST_NAMES = ["Aarav", "Aditi", "Aman", "Ananya", "Arjun", "Bhavna", "Chirag", "Deepika",
               "Dev", "Esha", "Farhan", "Gauri", "Harsh", "Isha", "Jatin", "Kavya",
               "Karan", "Lavanya", "Manav", "Meera", "Nikhil", "Neha", "Om", "Priya",
               "Rahul", "Riya", "Sahil", "Shreya", "Tanvi", "Uday", "Varun", "Yash",
               "Ansh Shah", "Priyal Shah", "Ravi Shah", "Zeel Shah", "Krisha Shah"]
LAST_NAMES = ["Patel", "Shah", "Mehta", "Desai", "Trivedi", "Joshi", "Chauhan", "Rana",
              "Vyas", "Pandya", "Thakkar", "Gandhi", "Bhatt", "Iyer", "Nair", "Reddy"]
CITIES_STATES = [("Ahmedabad", "Gujarat"), ("Surat", "Gujarat"), ("Vadodara", "Gujarat"),
                  ("Rajkot", "Gujarat"), ("Mumbai", "Maharashtra"), ("Pune", "Maharashtra"),
                  ("Delhi", "Delhi"), ("Bengaluru", "Karnataka"), ("Hyderabad", "Telangana"),
                  ("Jaipur", "Rajasthan")]
CUSTOMER_TYPES = ["Premium", "Regular", "New"]
PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"]
DEPARTMENTS = ["Sales", "Support", "Logistics", "Marketing"]

CATEGORIES = ["Smartphones", "Laptops", "Audio", "Wearables", "Tablets", "Accessories"]

PRODUCTS = [
    ("iPhone 15", "Smartphones", "Apple", 74999, 25, 4.7),
    ("iPhone 15 Pro", "Smartphones", "Apple", 134900, 12, 4.8),
    ("iPhone 14", "Smartphones", "Apple", 59999, 30, 4.6),
    ("Galaxy S24", "Smartphones", "Samsung", 79999, 20, 4.6),
    ("Galaxy S24 Ultra", "Smartphones", "Samsung", 129999, 8, 4.8),
    ("Galaxy A55", "Smartphones", "Samsung", 34999, 45, 4.3),
    ("OnePlus 12", "Smartphones", "OnePlus", 64999, 18, 4.5),
    ("Redmi Note 13", "Smartphones", "Xiaomi", 17999, 60, 4.2),
    ("MacBook Air M2", "Laptops", "Apple", 114900, 10, 4.8),
    ("MacBook Pro M3", "Laptops", "Apple", 169900, 6, 4.9),
    ("Galaxy Book4", "Laptops", "Samsung", 84999, 9, 4.4),
    ("ThinkPad E14", "Laptops", "Lenovo", 62999, 15, 4.3),
    ("Dell XPS 13", "Laptops", "Dell", 99999, 7, 4.6),
    ("HP Pavilion 15", "Laptops", "HP", 54999, 22, 4.1),
    ("AirPods Pro 2", "Audio", "Apple", 24900, 40, 4.7),
    ("Galaxy Buds3", "Audio", "Samsung", 14999, 35, 4.3),
    ("Sony WH-1000XM5", "Audio", "Sony", 29990, 14, 4.8),
    ("boAt Rockerz 550", "Audio", "boAt", 1999, 100, 4.0),
    ("JBL Flip 6", "Audio", "JBL", 11999, 28, 4.5),
    ("Apple Watch Series 9", "Wearables", "Apple", 41900, 16, 4.7),
    ("Galaxy Watch6", "Wearables", "Samsung", 29999, 20, 4.4),
    ("Mi Band 8", "Wearables", "Xiaomi", 2499, 80, 4.1),
    ("iPad Air", "Tablets", "Apple", 59900, 11, 4.6),
    ("iPad 10th Gen", "Tablets", "Apple", 38900, 19, 4.5),
    ("Galaxy Tab S9", "Tablets", "Samsung", 72999, 9, 4.5),
    ("Anker 20W Charger", "Accessories", "Anker", 1799, 150, 4.4),
    ("Apple 20W Adapter", "Accessories", "Apple", 1900, 90, 4.2),
    ("Samsung 25W Charger", "Accessories", "Samsung", 1599, 85, 4.1),
    ("Logitech MX Master 3S", "Accessories", "Logitech", 8995, 30, 4.7),
    ("SanDisk 128GB Pendrive", "Accessories", "SanDisk", 999, 200, 4.0),
]


def random_date(start_year=2023, end=None):
    start = date(start_year, 1, 1)
    end = end or date(2025, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def already_seeded() -> bool:
    try:
        result = db.run_query("SELECT COUNT(*) AS n FROM customers")
        return int(result.iloc[0]["n"]) > 0
    except Exception:
        return False  # table doesn't exist yet


def build(force: bool = False):
    schema_file = "schema_postgres.sql" if db.is_postgres() else "schema.sql"
    with open(os.path.join(BASE_DIR, schema_file)) as f:
        db.executescript(f.read())

    if not force and already_seeded():
        print("Database already has data — skipping seed.")
        return

    engine = db.get_engine()

    # Categories
    categories = pd.DataFrame({
        "category_id": range(1, len(CATEGORIES) + 1),
        "category_name": CATEGORIES,
    })
    cat_ids = {name: i + 1 for i, name in enumerate(CATEGORIES)}

    # Products
    products = pd.DataFrame([
        {
            "product_id": pid,
            "product_name": name,
            "category_id": cat_ids[cat],
            "supplier": supplier,
            "price": price,
            "stock": stock,
            "rating": rating,
        }
        for pid, (name, cat, supplier, price, stock, rating) in enumerate(PRODUCTS, start=1)
    ])

    # Customers
    n_customers = 220
    used_names = set()
    customer_rows = []
    for cid in range(1, n_customers + 1):
        while True:
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            if name not in used_names:
                used_names.add(name)
                break
        city, state = random.choice(CITIES_STATES)
        ctype = random.choices(CUSTOMER_TYPES, weights=[0.25, 0.55, 0.20])[0]
        customer_rows.append({
            "customer_id": cid, "customer_name": name, "city": city, "state": state,
            "customer_type": ctype, "signup_date": random_date(2022, date(2024, 6, 30)),
        })
    customers = pd.DataFrame(customer_rows)

    # Employees
    n_employees = 18
    used_emp_names = set()
    employee_rows = []
    for eid in range(1, n_employees + 1):
        while True:
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            if name not in used_emp_names:
                used_emp_names.add(name)
                break
        employee_rows.append({
            "employee_id": eid, "employee_name": name, "department": random.choice(DEPARTMENTS),
            "salary": random.randint(28, 95) * 1000, "hire_date": random_date(2021, date(2024, 1, 1)),
        })
    employees = pd.DataFrame(employee_rows)

    # Orders + order_items
    n_orders = 650
    order_rows, item_rows = [], []
    order_item_id = 1
    for oid in range(1, n_orders + 1):
        cust_id = random.randint(1, n_customers)
        emp_id = random.randint(1, n_employees)
        odate = random_date(2024, date(2025, 12, 31))
        payment = random.choices(PAYMENT_METHODS, weights=[0.35, 0.2, 0.2, 0.1, 0.15])[0]
        order_rows.append({
            "order_id": oid, "customer_id": cust_id, "employee_id": emp_id,
            "order_date": odate, "payment_method": payment,
        })

        n_items = random.choices([1, 2, 3, 4], weights=[0.45, 0.3, 0.15, 0.10])[0]
        chosen_products = random.sample(range(1, len(PRODUCTS) + 1), k=n_items)
        for pid in chosen_products:
            base_price = PRODUCTS[pid - 1][3]
            qty = random.choices([1, 2, 3], weights=[0.7, 0.22, 0.08])[0]
            discount = random.choices([0, 0.05, 0.10, 0.15], weights=[0.5, 0.25, 0.15, 0.10])[0]
            item_rows.append({
                "order_item_id": order_item_id, "order_id": oid, "product_id": pid,
                "quantity": qty, "unit_price": base_price, "discount": discount,
            })
            order_item_id += 1

    orders = pd.DataFrame(order_rows)
    order_items = pd.DataFrame(item_rows)

    categories.to_sql("categories", engine, if_exists="append", index=False)
    products.to_sql("products", engine, if_exists="append", index=False)
    customers.to_sql("customers", engine, if_exists="append", index=False)
    employees.to_sql("employees", engine, if_exists="append", index=False)
    orders.to_sql("orders", engine, if_exists="append", index=False)
    order_items.to_sql("order_items", engine, if_exists="append", index=False)

    if db.is_postgres():
        _reset_postgres_sequences()

    print(f"Seeded {db.get_engine().dialect.name}: {n_customers} customers, {len(PRODUCTS)} products, "
          f"{n_employees} employees, {n_orders} orders, {order_item_id - 1} order items.")


def _reset_postgres_sequences():
    """After inserting rows with explicit IDs, Postgres's SERIAL sequences
    don't know those IDs were used — without this, the next auto-generated
    insert (e.g. a simulated live order) could collide with an existing ID."""
    tables_and_pks = [
        ("categories", "category_id"), ("products", "product_id"),
        ("customers", "customer_id"), ("employees", "employee_id"),
        ("orders", "order_id"), ("order_items", "order_item_id"),
    ]
    for table, pk in tables_and_pks:
        db.run_statement(
            f"SELECT setval(pg_get_serial_sequence('{table}', '{pk}'), "
            f"COALESCE((SELECT MAX({pk}) FROM {table}), 1))"
        )


if __name__ == "__main__":
    build()
