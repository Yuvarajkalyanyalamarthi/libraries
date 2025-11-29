import pyodbc
import pandas as pd

# ---------------------------------------
# DATABASE CREDENTIALS (EDIT HERE)
# ---------------------------------------
SERVER = "kalyan"
DATABASE = "project"
USERNAME = "yuvaraj"
PASSWORD = "yuvaraj@12"

# ---------------------------------------
# CONNECT TO SQL SERVER
# ---------------------------------------
def connect_db():
    conn_str = f"""
        DRIVER={{ODBC Driver 17 for SQL Server}};
        SERVER={SERVER};
        DATABASE={DATABASE};
        UID={USERNAME};
        PWD={PASSWORD};
        Trust_Connection=no;
    """
    return pyodbc.connect(conn_str)

# ---------------------------------------
# LOGIN FUNCTION
# ---------------------------------------
def login(user_id):
    conn = connect_db()
    df = pd.read_sql(f"SELECT * FROM users WHERE user_id = {user_id}", conn)
    conn.close()

    if df.empty:
        print("❌ User not found!")
        return None
    else:
        print(f"✅ Welcome {df.iloc[0]['name']}!")
        return df.iloc[0]

# ---------------------------------------
# GET RESTAURANTS
# ---------------------------------------
def get_restaurants():
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM restaurants", conn)
    conn.close()

    print("\n🍽 Available Restaurants:")
    print(df[["restaurant_id", "name", "area", "rating"]])
    return df

# ---------------------------------------
# GET MENU FOR A RESTAURANT
# ---------------------------------------
def get_menu(restaurant_id):
    conn = connect_db()
    df = pd.read_sql(
        f"SELECT * FROM menu_items WHERE restaurant_id = {restaurant_id}", conn
    )
    conn.close()

    print("\n📜 Menu Items:")
    print(df[["item_id", "item", "price"]])
    return df

# ---------------------------------------
# PLACE ORDER
# ---------------------------------------
def place_order(user_id, restaurant_id, item_id, quantity):
    conn = connect_db()
    cursor = conn.cursor()

    # get price
    price_df = pd.read_sql(f"SELECT price FROM menu_items WHERE item_id={item_id}", conn)
    if price_df.empty:
        print("❌ Item not found!")
        return

    amount = float(price_df.iloc[0]["price"]) * quantity

    # insert order
    cursor.execute("""
        INSERT INTO orders (user_id, restaurant_id, amount, status)
        OUTPUT INSERTED.order_id
        VALUES (?, ?, ?, 'Placed')
    """, (user_id, restaurant_id, amount))

    order_id = cursor.fetchone()[0]

    # insert into order items
    cursor.execute("""
        INSERT INTO order_items (order_id, item_id, quantity)
        VALUES (?, ?, ?)
    """, (order_id, item_id, quantity))

    conn.commit()
    conn.close()

    print(f"\n✅ Order placed successfully! Order ID: {order_id}")
    return order_id

# ---------------------------------------
# TRACK ORDER
# ---------------------------------------
def track_order(order_id):
    conn = connect_db()
    df = pd.read_sql(f"SELECT * FROM delivery_tracking WHERE order_id={order_id}", conn)
    conn.close()

    if df.empty:
        print("🚚 No tracking info yet.")
    else:
        print("\n📍 Delivery Tracking:")
        print(df[["delivery_boy", "current_area", "updated_at"]])

# ---------------------------------------
# GET USER ORDER HISTORY
# ---------------------------------------
def order_history(user_id):
    conn = connect_db()
    df = pd.read_sql(f"SELECT * FROM orders WHERE user_id={user_id}", conn)
    conn.close()

    print("\n📦 Your Order History:")
    print(df)
    return df

# ---------------------------------------
# MAIN PROGRAM
# ---------------------------------------
print("====== FOOD ORDERING APP ======")

user_id = int(input("Enter your User ID to Login: "))
user = login(user_id)

if user:
    print("\n1. View Restaurants")
    print("2. View Menu")
    print("3. Place Order")
    print("4. Track Order")
    print("5. Order History")

    choice = int(input("\nEnter choice: "))

    if choice == 1:
        get_restaurants()

    elif choice == 2:
        r = int(input("Enter restaurant ID: "))
        get_menu(r)

    elif choice == 3:
        r = int(input("Restaurant ID: "))
        i = int(input("Item ID: "))
        q = int(input("Quantity: "))
        place_order(user_id, r, i, q)

    elif choice == 4:
        o = int(input("Enter Order ID: "))
        track_order(o)

    elif choice == 5:
        order_history(user_id)

    else:
        print("❌ Invalid Option!")
