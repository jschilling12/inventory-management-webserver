from collections import deque
from db import connect_db

class Queue:
    def __init__(self):
        self.by_order = {}

    def get_order(self):
        return self.by_order

    def get_product(self, order_id):
        return self.by_order.get(order_id, None)

    def set_order(self, order_id, product, amount):
        if order_id not in self.by_order:
            self.by_order[order_id] = {}
        self.by_order[order_id][product] = amount

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            ("queued", order_id)
        )
        conn.commit()
        conn.close()

    def remove(self, order_id):
        if order_id in self.by_order:
            del self.by_order[order_id]
            return True
        return False

class ProcessQueue:
    def __init__(self, order_queue):
        self.order_queue = order_queue
        self.processing_queue = deque()

        # Load queued orders from DB
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, product, quantity FROM orders WHERE status = 'queued'")
        for order_id, product, amount in cursor.fetchall():
            # Rebuild in-memory queue
            self.order_queue.set_order(order_id, product, amount)
            self.processing_queue.append((order_id, {product: amount}))
        conn.close()

    def add_order_in_queue(self, order_id):
        order = self.order_queue.get_product(order_id)
        if order and not any(o[0] == order_id for o in self.processing_queue):
            self.processing_queue.append((order_id, order))
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE orders SET status = ? WHERE id = ?",
                ("queued", order_id)
            )
            conn.commit()
            conn.close()
            return True
        return False

    def process_order(self):
        if self.processing_queue:
            order_id, order_data = self.processing_queue.popleft()
            print(f"Processing Order {order_id}: {order_data}")
            self.order_queue.remove(order_id)

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE orders SET status = 'processed' WHERE id = ?", (order_id,))

            conn.commit()
            conn.close()
            return True
        return False