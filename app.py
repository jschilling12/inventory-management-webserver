import os
import json
from pathlib import Path

from flask import Flask, redirect, render_template, request
from python_warehouse.db import connect_db, init_db


app = Flask(__name__)

# Database path and initialization
_DATABASE_PATH = Path(__file__).parent / "inventory.db"
os.environ.setdefault("DATABASE_NAME", str(_DATABASE_PATH.resolve()))
if os.environ.get("FLASK_DEBUG") == "1":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
init_db()

# Navigation links used by templates
VIEWS = {
    "Summary": "/",
    "Stock": "/product",
    "Warehouses": "/location",
    "Logistics": "/movement",
}

EMPTY_SYMBOLS = {None, ""}


@app.route("/", methods=["GET"])
def summary():
    # Use our python_warehouse schema
    with connect_db() as conn:
        warehouses = conn.execute(
            "SELECT id, location_name FROM warehouse ORDER BY id"
        ).fetchall()
        products = conn.execute(
            "SELECT id, name, quantity FROM products ORDER BY id"
        ).fetchall()
        # Basic summary: name, unallocated (same as quantity), total (quantity)
        q_data = [(row[1], row[2], row[2]) for row in products]

    return render_template(
        "index.jinja",
        link=VIEWS,
        title="Summary",
        warehouses=warehouses,
        products=products,
        summary=q_data,
    )


@app.route("/product", methods=["POST", "GET"])
def product():
    with connect_db() as conn:
        if request.method == "POST":
            prod_name = request.form.get("prod_name", "").strip()
            quantity = request.form.get("prod_quantity", "").strip()
            if (
                prod_name not in EMPTY_SYMBOLS
                and quantity not in EMPTY_SYMBOLS
            ):
                try:
                    qty = int(quantity)
                except ValueError:
                    qty = 0
                if qty > 0:
                    # Insert new or increase existing quantity
                    existing = conn.execute(
                        "SELECT id FROM products WHERE name = ?",
                        (prod_name,),
                    ).fetchone()
                    if existing:
                        conn.execute(
                            (
                                "UPDATE products SET quantity = quantity + ? "
                                "WHERE id = ?"
                            ),
                            (qty, existing[0]),
                        )
                    else:
                        conn.execute(
                            (
                                "INSERT INTO products (name, quantity, warehouse_id) "
                                "VALUES (?, ?, 1)"
                            ),
                            (prod_name, qty),
                        )
                    return redirect(VIEWS["Stock"])

        products = conn.execute(
            "SELECT id, name, quantity FROM products ORDER BY id"
        ).fetchall()

    return render_template(
        "product.jinja",
        link=VIEWS,
        products=products,
        title="Stock",
    )


@app.route("/location", methods=["POST", "GET"])
def location():
    with connect_db() as conn:
        if request.method == "POST":
            warehouse_name = request.form.get("warehouse_name", "").strip()
            if warehouse_name not in EMPTY_SYMBOLS:
                conn.execute(
                    (
                        "INSERT OR IGNORE INTO warehouse (location_name, max_capacity, "
                        "used_capacity) VALUES (?, 1000, 0)"
                    ),
                    (warehouse_name,),
                )
                return redirect(VIEWS["Warehouses"])

        warehouse_data = conn.execute(
            "SELECT id, location_name FROM warehouse ORDER BY id"
        ).fetchall()

    return render_template(
        "location.jinja",
        link=VIEWS,
        warehouses=warehouse_data,
        title="Warehouses",
    )


@app.route("/movement", methods=["POST", "GET"])
def movement():
    # Stub view since logistics tables are not part of python_warehouse schema
    if request.method == "POST":
        return redirect(VIEWS["Logistics"])

    products = []
    locations = []
    logistics_data = []
    item_location_qty_map = json.dumps({})
    warehouse_summary = []

    return render_template(
        "movement.jinja",
        title="Logistics",
        link=VIEWS,
        products=products,
        locations=locations,
        allocated=item_location_qty_map,
        logistics=logistics_data,
        summary=warehouse_summary,
    )


@app.route("/delete")
def delete():
    delete_record_type = request.args.get("type")
    with connect_db() as conn:
        if delete_record_type == "product":
            product_id = request.args.get("prod_id")
            if product_id:
                conn.execute(
                    "DELETE FROM products WHERE id = ?",
                    (product_id,),
                )
            return redirect(VIEWS["Stock"])
        elif delete_record_type == "location":
            location_id = request.args.get("loc_id")
            if location_id:
                conn.execute(
                    "DELETE FROM warehouse WHERE id = ?",
                    (location_id,),
                )
            return redirect(VIEWS["Warehouses"])
        else:
            return redirect(VIEWS["Summary"])


@app.route("/edit", methods=["POST"])
def edit():
    edit_record_type = request.args.get("type")
    with connect_db() as conn:
        if edit_record_type == "location":
            loc_id = request.form.get("loc_id")
            loc_name = request.form.get("loc_name", "").strip()
            if loc_id and loc_name:
                conn.execute(
                    "UPDATE warehouse SET location_name = ? WHERE id = ?",
                    (loc_name, loc_id),
                )
            return redirect(VIEWS["Warehouses"])
        elif edit_record_type == "product":
            prod_id = request.form.get("prod_id")
            prod_name = request.form.get("prod_name", "").strip()
            prod_quantity = request.form.get("prod_quantity", "").strip()
            if prod_id:
                if prod_name:
                    conn.execute(
                        "UPDATE products SET name = ? WHERE id = ?",
                        (prod_name, prod_id),
                    )
                if prod_quantity:
                    try:
                        qty = int(prod_quantity)
                        conn.execute(
                            "UPDATE products SET quantity = ? WHERE id = ?",
                            (qty, prod_id),
                        )
                    except ValueError:
                        pass
            return redirect(VIEWS["Stock"])
        else:
            return redirect(VIEWS["Summary"]) 
