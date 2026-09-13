"""
seed_data.py
Generates a realistic synthetic dataset for an Indian electronics retail
business and loads it into retailiq.db (SQLite).

Run: python seed_data.py
"""
import os
import sqlite3
import random
from datetime import date, timedelta

random.seed(42)

# Resolve paths relative to this file's own folder, not the current working
# directory — Streamlit Cloud (and some other hosts) run the app from a
# different cwd, so plain "schema.sql" / "retailiq.db" can fail with
# FileNotFoundError depending on where the repo is checked out.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "retailiq.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

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
    # (name, category, supplier, price, stock, rating)
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
    return (start + timedelta(days=random.randint(0, delta))).isoformat()


def build():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    with open(SCHEMA_PATH) as f:
        cur.executescript(f.read())

    # Categories
    cat_ids = {}
    for i, cname in enumerate(CATEGORIES, start=1):
        cur.execute("INSERT INTO categories VALUES (?, ?)", (i, cname))
        cat_ids[cname] = i

    # Products
    for pid, (name, cat, supplier, price, stock, rating) in enumerate(PRODUCTS, start=1):
        cur.execute("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (pid, name, cat_ids[cat], supplier, price, stock, rating))

    # Customers (~220)
    n_customers = 220
    used_names = set()
    for cid in range(1, n_customers + 1):
        while True:
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            if name not in used_names:
                used_names.add(name)
                break
        city, state = random.choice(CITIES_STATES)
        ctype = random.choices(CUSTOMER_TYPES, weights=[0.25, 0.55, 0.20])[0]
        cur.execute("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)",
                    (cid, name, city, state, ctype, random_date(2022, date(2024, 6, 30))))

    # Employees (~18)
    n_employees = 18
    used_emp_names = set()
    for eid in range(1, n_employees + 1):
        while True:
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            if name not in used_emp_names:
                used_emp_names.add(name)
                break
        dept = random.choice(DEPARTMENTS)
        salary = random.randint(28, 95) * 1000
        cur.execute("INSERT INTO employees VALUES (?, ?, ?, ?, ?)",
                    (eid, name, dept, salary, random_date(2021, date(2024, 1, 1))))

    # Orders + order_items (~650 orders, 1-4 items each)
    n_orders = 650
    order_item_id = 1
    for oid in range(1, n_orders + 1):
        cust_id = random.randint(1, n_customers)
        emp_id = random.randint(1, n_employees)
        odate = random_date(2024, date(2025, 12, 31))
        payment = random.choices(PAYMENT_METHODS, weights=[0.35, 0.2, 0.2, 0.1, 0.15])[0]
        cur.execute("INSERT INTO orders VALUES (?, ?, ?, ?, ?)",
                    (oid, cust_id, emp_id, odate, payment))

        n_items = random.choices([1, 2, 3, 4], weights=[0.45, 0.3, 0.15, 0.10])[0]
        chosen_products = random.sample(range(1, len(PRODUCTS) + 1), k=n_items)
        for pid in chosen_products:
            base_price = PRODUCTS[pid - 1][3]
            qty = random.choices([1, 2, 3], weights=[0.7, 0.22, 0.08])[0]
            discount = random.choices([0, 0.05, 0.10, 0.15], weights=[0.5, 0.25, 0.15, 0.10])[0]
            cur.execute("INSERT INTO order_items VALUES (?, ?, ?, ?, ?, ?)",
                        (order_item_id, oid, pid, qty, base_price, discount))
            order_item_id += 1

    conn.commit()
    conn.close()
    print(f"Built {DB_PATH}: {n_customers} customers, {len(PRODUCTS)} products, "
          f"{n_employees} employees, {n_orders} orders, {order_item_id - 1} order items.")


if __name__ == "__main__":
    build()
