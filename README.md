# Corollary Warehousing System

- Author: Jordan Schilling
- Student ID: 012678863
- Python Version: 3.12

---

## Project Overview

Corollary Warehousing is a comprehensive inventory and order management system designed for scalability, real-time analytics, and warehouse manipulation. 
Built using Python, SQLite, and ADS (Abstract Data Structures) like Queues and Hash Tables, the system supports customers placing orders and employees managing inventory.
Included is backend support and warehouse space tracking.


## Function Descriptions


### HashTable (Inventory, Quantities)
-- Purpose:
- The HashTable class manages product <> quantities using an in-memory hash map with defaultdict(int). 
- It supports setting, retrieving, incrementing, and decrementing stock levels.

-- Steps to Run:
- The run function is within the Inventory class and automatically updated when inventory is added, restocked, or queried.

-- Error Handling & Edge Cases:
- Missing keys return 0.
- Assumes keys are product names in lowercase to ensure case-insensitive matching.


### Inventory (Product, Product ID, and Quantity Tracking)
-- Purpose:
- The Inventory class handles the creation of products <> product IDs and tracking of quantities, syncing with the products table in SQLite. 
- It manages
    - Loading products to/from the DB
    - Adding new items
    - Restocking
    - Capacity checks based on warehouse limits

-- Steps to Run:
- Triggered in main.py via employees
    - Option 1: Add or restock product
    - Option 2: View inventory

-- Error Handling & Edge Cases:
- Validates against warehouse max_capacity before restocking.
- Inventory can only be a positive integer.
- Prevents adding a product if warehouse space is full.
- Converts all product names to lowercase to avoid duplication.
- Inventory updates are committed immediately.


### Queue (Order Staging System)
-- Purpose:
- The Queue class manages unprocessed customer orders in memory using a dictionary.
    - Adds new orders
    - Retrieves product info by order ID
    - Updates order status in SQLite to 'queued'

-- Steps to Run:
- Orders are staged in this queue when a customer places an order. Managed automatically in main.py.

-- Error Handling & Edge Cases:
- Duplicate order IDs are handled safely (no overwrites).
- Missing order IDs return None.
- SQLite updates are wrapped with commits for persistence.


### ProcessQueue (Order Fulfillment Pipeline)
-- Purpose:
- The ProcessQueue handles order execution using a deque (FIFO).
    - Loads pending orders from the DB on startup
    - Queues new orders as they come in
    - Processes and updates orders as 'processed'

-- Steps to Run:
- Used in main.py
    - Orders are enqueued upon customer purchase.
    - Processed via employee menu option 3.

-- Error Handling & Edge Cases:
- Only processes if the queue is non-empty.
- Ensures database is updated with order status on completion.
- Handles an empty queue by returning False.


## How to Run Each Function
-- Initialize the System:

   - python main.py
   - navigate through the prompts