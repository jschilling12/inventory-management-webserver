from db import connect_db, init_db, clear_inventory_and_orders
from inventory import Inventory, HashTable
from order_numbers import unique_order_id_generator, order_id
from order_queue import Queue, ProcessQueue

init_db()

conn = connect_db()
cursor = conn.cursor()

quantity = HashTable()
products = Inventory()
orders = Queue()
process = ProcessQueue(orders)

customer = False
employee = False
start_program = True

# Determine who is accessing the application. '
# There is a generic placeholder password for employees
# Although that can be put into a JSON later on.
while start_program:
    print("Corollary Warehousing")
    enter = input("Are you a customer or employee?: ").lower()

    if enter == "customer":
        customer = True
        start_program = False
    elif enter == "employee":
        pwd = input("What is your employee code?: ")
        if pwd == "0000":
            employee = True
            start_program = False
    else:
        print("Enter either customer or employee!\n")

# Customer path for starting an order.
while customer:
    while True:
        name = input("Input a PRODUCT (or type 0 to cancel): \n")
        if name == "0":
            print("Order canceled!")
            customer = False
            break
        elif name.isalpha():
            break
        else:
            print("Invalid input. Please enter a valid product name! \n or \n"
                  "Select 0 to cancel\n")

    if not customer:
        break

    cursor.execute("SELECT quantity FROM products WHERE name = ?", (name,))
    result = cursor.fetchone()

    if result:
        while True:
            amount_input = input("Input a QUANTITY of said PRODUCT: \n")
            if amount_input.isalpha():
                print("Invalid input. Please enter a valid number!\n")
            if int(amount_input) == 0:
                print("Canceling operation!")
                customer = False
                break
            if amount_input.isdigit():
                amount = int(amount_input)
            elif int(amount_input) > 0:
                amount = int(amount_input)
                break
            else:
                print("Invalid input. Please enter a valid number!\n")
        if not customer:
            print("Please select a valid quantity!")
            break
        stock = result[0]

        if stock >= amount:
            new_stock = stock - amount

            # Update product quantity
            cursor.execute(
                "UPDATE products SET quantity = ? WHERE name = ?",
                (new_stock, name)
            )

            # Update warehouse used_capacity
            cursor.execute(
                "UPDATE warehouse SET used_capacity = used_capacity - ? WHERE id = 1",
                (amount,)
            )

            # Generate or retrieve order ID
            while True:
                email = input("Order EMAIL: \n")
                index = email.find('@')
                if index != -1:
                    break
                else:
                    print("Please enter a valid email address!\n")

            if email not in order_id:
                order_num = unique_order_id_generator(email)
            if email == '0':
                print("Canceling operation!")
                customer = False
                break
            else:
                order_num = order_id[email]
        # if not customer:
        #     break
        #     print(f"\nOrder Successful!")
            print(f"\nOrder ID: {order_num}")
            print(f"Product: {name}")
            print(f"Quantity: {amount}\n")
            print("Invoices will be sent to your email once the order is processed!\n")

            cursor.execute(
                "INSERT INTO orders (id, product, quantity, email, status) "
                "VALUES (?, ?, ?, ?, ?)",
                (order_num, name, amount, email, 'pending')
            )

            conn.commit()

            # Place order in queue
            orders.set_order(order_num, product=name, amount=amount)
            process.add_order_in_queue(order_num)
            conn.close()
            customer = False

        else:
            print("Item is out of stock or insufficient quantity available!\n")
    else:
        print("Item is not available in inventory!\n")

# Employee path for inventory management and order processing.
while employee:
    options = int(input(
        "\nOptions:\n"
        "1 - Add or restock a product\n"
        "2 - Check inventory and order queues\n"
        "3 - Process an order (not implemented)\n"
        "4 - Exit console\n"
        "5 - Space optimization report\n"
        "6 - Would you like to clear all orders and inventory and start fresh?\n"
    ))

    if options == 1:
        product_name = input("Enter product name to add or restock: ")
        products.add_product(product_name)
        inventory_view = products.get_inventory()
        print("\n--- INVENTORY ---")
        print("Product List:", inventory_view["Products: "])
        print("Stock Quantities:", inventory_view["Quantities: "])

    elif options == 2:
        inventory_view = products.get_inventory()
        print("\n--- INVENTORY ---")
        print("Product List:", inventory_view["Products: "])
        print("Stock Quantities:", inventory_view["Quantities: "])

        # Show order history
        print("\n--- ORDER HISTORY ---")
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, product, quantity, email, status "
                       "FROM orders ORDER BY status, id")
        rows = cursor.fetchall()

        if rows:
            for order_id, product, quantity, email, status in rows:
                print(f"[{status.upper()}] Order ID: {order_id} | Product: {product} "
                      f"| Quantity: {quantity} | Email: {email}")
        else:
            print("No orders found.")

        conn.close()

    elif options == 3:
        if process.processing_queue:
            process.process_order()
            print("Order invoice sent to customer email. "
                  "Order complete and notification"
                  " sent to accounting!\n")
        else:
            print("No orders in the queue to process.\n")

    elif options == 4:
        print("Exiting employee console...\n")
        break

    elif options == 5:
        from warehousing import space_optimization_report
        space_optimization_report()

    elif options == 6:
        confirm = input("Are you sure you want to clear ALL inventory and orders? "
                        "Type 'YES' to confirm: ")
        if confirm == "YES":
            clear_inventory_and_orders()
            print("INVENTORY AND ORDERS HAVE BEEN CLEARED!!! \n")
        else:
            print("Operation canceled!\n")

    else:
        print("Please select a valid option.\n")
