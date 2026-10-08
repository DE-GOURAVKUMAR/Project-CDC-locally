import time
import random
import uuid
from datetime import datetime
import psycopg2
from faker import Faker

fake = Faker()

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "swiggy_admin",
    "password": "supersecretpassword",
    "dbname": "swiggy_db",
}

STATUS_FLOW = ["PLACED", "ACCEPTED", "PREPARING", "OUT_FOR_DELIVERY", "DELIVERED"]

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def run_simulation():
    conn = get_connection()
    conn.autocommit = True
    cursor = conn.cursor()
    print("🚀 Swiggy Order Simulator started. Press Ctrl+C to stop.")

    active_orders = []

    try:
        while True:
            # 1. Randomly decide to place a new order (70% chance)
            if random.random() < 0.7 or len(active_orders) == 0:
                order_id = str(uuid.uuid4())
                user_id = random.randint(1, 4)
                restaurant_id = random.randint(1, 4)
                amount = round(random.uniform(150.0, 1200.0), 2)
                delivery_fee = round(random.uniform(20.0, 80.0), 2)
                initial_status = "PLACED"

                cursor.execute("""
                    INSERT INTO orders (order_id, user_id, restaurant_id, total_amount, delivery_fee, order_status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (order_id, user_id, restaurant_id, amount, delivery_fee, initial_status, datetime.now(), datetime.now()))

                active_orders.append({"order_id": order_id, "step": 0})
                print(f"📦 [NEW ORDER] {order_id[:8]}... Status: PLACED | Total: ₹{amount}")

            # 2. Progress an existing active order to the next status
            if active_orders:
                idx = random.randint(0, len(active_orders) - 1)
                tracked_order = active_orders[idx]
                tracked_order["step"] += 1
                next_status = STATUS_FLOW[tracked_order["step"]]

                cursor.execute("""
                    UPDATE orders 
                    SET order_status = %s, updated_at = %s 
                    WHERE order_id = %s
                """, (next_status, datetime.now(), tracked_order["order_id"]))

                print(f"🔄 [UPDATE]    {tracked_order['order_id'][:8]}... Transitioned to -> {next_status}")

                # Remove from tracking once delivered
                if next_status == "DELIVERED":
                    active_orders.pop(idx)

            time.sleep(random.uniform(1.0, 2.5))

    except KeyboardInterrupt:
        print("\nStopping order simulation...")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_simulation()