
import os
import sqlite3
import tempfile
import unittest

import llm_sql
import seed_data
from query_library import QUERY_LIBRARY


class RetailIQTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.db_path = os.path.join(cls.temp_dir.name, "test_retailiq.db")

        cls.original_db_path = seed_data.DB_PATH
        seed_data.DB_PATH = cls.db_path

        seed_data.build()

        cls.connection = sqlite3.connect(cls.db_path)

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()
        seed_data.DB_PATH = cls.original_db_path
        cls.temp_dir.cleanup()

    def test_all_60_queries_are_present(self):
        self.assertEqual(len(QUERY_LIBRARY), 60)

    def test_all_saved_queries_are_safe(self):
        for query in QUERY_LIBRARY:
            with self.subTest(query=query["id"]):
                safe, reason = llm_sql.is_safe_select(query["sql"])
                self.assertTrue(safe, reason)

    def test_all_saved_queries_execute(self):
        for query in QUERY_LIBRARY:
            with self.subTest(query=query["id"]):
                self.connection.execute(query["sql"]).fetchall()

    def test_expected_database_records(self):
        expected = {
            "customers": 220,
            "products": 30,
            "employees": 18,
            "orders": 650,
        }

        for table, count in expected.items():
            with self.subTest(table=table):
                actual = self.connection.execute(
                    f"SELECT COUNT(*) FROM {table}"
                ).fetchone()[0]

                self.assertEqual(actual, count)

    def test_unsafe_queries_are_rejected(self):
        unsafe_queries = [
            "DELETE FROM customers",
            "DROP TABLE products",
            "UPDATE products SET price = 0",
            "SELECT * FROM customers; DELETE FROM customers",
            "",
        ]

        for sql in unsafe_queries:
            with self.subTest(sql=sql):
                safe, reason = llm_sql.is_safe_select(sql)
                self.assertFalse(safe)



    def test_no_orphan_records(self):
        checks = [
            """
            SELECT COUNT(*) FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
            """,
            """
            SELECT COUNT(*) FROM order_items oi
            LEFT JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_id IS NULL
            """,
            """
            SELECT COUNT(*) FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.product_id
            WHERE p.product_id IS NULL
            """,
        ]

        for sql in checks:
            with self.subTest(sql=sql):
                count = self.connection.execute(sql).fetchone()[0]
                self.assertEqual(count, 0)

    def test_foreign_key_constraints(self):
        self.connection.execute("PRAGMA foreign_keys = ON")

        result = self.connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        self.assertEqual(result, [])

    def test_existing_database_is_not_overwritten(self):
        with self.assertRaises(SystemExit):
            seed_data.build()