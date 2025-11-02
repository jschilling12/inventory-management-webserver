import sqlite3
import os
from pathlib import Path
from typing import Optional


def connect_db(db_path: Optional[str] = None):
    """Return a sqlite3 connection.

    If db_path is provided, use it. Otherwise read from env var DATABASE_NAME;
    if not set, default to a file 'inventory.db' in the project root.
    """
    if db_path is None:
        db_path = os.environ.get(
            "DATABASE_NAME",
            str((Path(__file__).parent.parent / "inventory.db").resolve()),
        )
    return sqlite3.connect(db_path)

def init_db():
    with connect_db() as conn:
        cursor = conn.cursor()

        # Warehouse table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS warehouse (
                                                                id INTEGER PRIMARY KEY,
                                                                location_name TEXT UNIQUE,
                                                                max_capacity INTEGER,
                                                                used_capacity INTEGER DEFAULT 0
                       )
                       ''')

        # Products table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS products (
                                                               id INTEGER PRIMARY KEY,
                                                               name TEXT UNIQUE COLLATE NOCASE,
                                                               quantity INTEGER,
                                                               warehouse_id INTEGER DEFAULT 1,
                                                               FOREIGN KEY (warehouse_id) REFERENCES warehouse(id)
                       )
                       ''')

        # Orders table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS orders (
                                                             id TEXT PRIMARY KEY,
                                                             product TEXT,
                                                             quantity INTEGER,
                                                             email TEXT,
                                                             status TEXT
                       )
                       ''')

        # Warehouse table
        cursor.execute('''
                       INSERT OR IGNORE INTO warehouse (id, location_name, max_capacity, used_capacity)
                       VALUES (1, 'Main Warehouse', 1000, 0)
                       ''')

def clear_inventory_and_orders():
    with connect_db() as conn:
        cursor = conn.cursor()

        # Delete all records from all tables
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM warehouse")

        conn.commit()
    print("Inventory and order history cleared.")
