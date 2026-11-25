# from prices import total
# print(total(80, 2)) 

import os , psycopg 
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv
from db import connect_db


load_dotenv(interpolate=False)
with psycopg.connect(
    host=os.getenv("PGHOST", "localhost"),
    port=os.getenv("PGPORT", 5432),
    dbname=os.getenv("PGDATABASE", "poc"),
    user=os.getenv("PGUSER", "postgres"),
    password=os.getenv("PGPASSWORD", "369153")
) as conn:
    print("connected")
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_name ,unit_price, phone FROM orders")
    orders_rows = cursor.fetchall()
    for id , customer_name, unit_price, phone in orders_rows:
        print(id, customer_name, unit_price, phone )
#     name = input("Enter your cake: ").strip()

#     cursor.execute(
#         "SELECT id , name , price , description FROM products WHERE name = %s" , (name,)
#     )
#     products_rows = cursor.fetchone()
#     print(products_rows)
#     if products_rows is None:
#         print("No product found for cake")
#     else:
#         print(products_rows)
#     cursor.execute(
#         "SELECT id FROM orders WHERE name = %s" , (name,)
#     )

# valid = True
# name = input("Name:").strip()
# try:
#     price = Decimal(input("Price:").strip())
#     valid = price.is_finite() and price > 0 
# except InvalidOperation:
#     valid = False

# print(valid)

# name = input("Enter your cake: ").strip()
# cursor.execute(
#  "SELECT id , customer_name , unit_price , phone FROM orders WHERE name = %s" , (name,)
# )
# row = cursor.fetchone()
# if row is None:
#     print("No order found for cake")
# else:
#     print(row)

    cake_inser = input("Cake Name:").strip()
    desc_inser = input("Description:").strip()
    price_inser = input("Price:").strip()
    cursor.execute(
        "INSERT INTO products (name , description , price)"
        "VALUES (%s , %s , %s)",
        (cake_inser, desc_inser, price_inser )
    ) 
    conn.commit