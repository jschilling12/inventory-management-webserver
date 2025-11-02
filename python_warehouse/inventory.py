from collections import defaultdict
from db import connect_db

# Product <> Quantity storage
class HashTable:
    def __init__(self):
        self.map = defaultdict(int)

    # Overrides the inventory with a set amount
    # could possibly be used for new warehouses adding a base inventory
    def set(self, key, value):
        self.map[key] = value

    def get(self, key):
        return self.map.get(key, 0)

    # Restocking
    def increment(self, key, amount = 1):
        self.map[key] += amount

    def remove_stock(self, key, quantity):
        self.map[key] -= quantity

# Product <> Product_ID storage
class Inventory:
    def __init__(self):
        self.product_list = {}
        self.hash_table = HashTable()
        self.next_product_id = 1
        self.load_products_from_db()

    def load_products_from_db(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name, id, quantity FROM products")
        for name, pid, qty in cursor.fetchall():
            name = name.lower()
            self.product_list[name] = pid
            self.hash_table.set(name, qty)
            if pid >= self.next_product_id:
                self.next_product_id = pid + 1
        conn.close()

    # Adds a new product and product id.
    # Can also handle restocking.
    def add_product(self, product_name):
        conn = connect_db()
        cursor = conn.cursor()

        # Fetch warehouse capacity
        cursor.execute("SELECT max_capacity, used_capacity FROM warehouse "
                       "WHERE id = 1")
        warehouse = cursor.fetchone()
        if not warehouse:
            print("Warehouse not initialized.")
            return
        max_cap, used = warehouse

        quantity = int(input("How much would you like to add? "))
        if used + quantity > max_cap:
            print("Not enough space in the warehouse to add this product.")
            conn.close()
            return

        product_name = product_name.lower()

        if product_name not in self.product_list:
            product_id = self.next_product_id
            self.next_product_id += 1
            self.product_list[product_name] = product_id
            self.hash_table.set(product_name, quantity)

            cursor.execute(
                "INSERT INTO products (id, name, quantity, warehouse_id) "
                "VALUES (?, ?, ?, 1)",
                (product_id, product_name, quantity)
            )
        else:
            self.hash_table.increment(product_name, quantity)
            cursor.execute(
                "UPDATE products SET quantity = quantity + ? WHERE name = ?",
                (quantity, product_name)
            )

        # Update used warehouse space
        cursor.execute("UPDATE warehouse SET used_capacity = used_capacity + ? "
                       "WHERE id = 1", (quantity,))

        conn.commit()
        conn.close()

    def get(self):
        return self.product_list

    def get_inventory(self):
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, quantity FROM products")
        rows = cursor.fetchall()

        # Clear current state
        self.product_list.clear()
        self.hash_table.map.clear()

        for prod_id, name, quantity in rows:
            name = name.lower()
            self.product_list[name] = prod_id
            self.hash_table.set(name, quantity)

        conn.close()

        return {
            "Products: ": self.product_list,
            "Quantities: ": dict(self.hash_table.map)
        }