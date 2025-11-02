from db import connect_db
import pandas as pd

def space_optimization_report():
    with connect_db() as conn:
        df = pd.read_sql_query(
            "SELECT location_name, max_capacity, used_capacity FROM warehouse WHERE id = 1",
            conn
        )

        print("\n--- Warehouse Space Report ---")
        if not df.empty:
            df["utilization_pct"] = (df["used_capacity"] / df["max_capacity"]) * 100
            df["status"] = df["utilization_pct"].apply(lambda pct:
               "Low Utilization" if pct < 50 else
               "Efficient" if pct < 90 else
               "Near Capacity"
               )

            print(df[["location_name", "used_capacity", "max_capacity",
                      "utilization_pct", "status"]].to_string(index=False))
        else:
            print("No warehouse found.")
