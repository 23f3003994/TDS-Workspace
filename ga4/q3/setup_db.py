# setup_db.py
# Creates a SQLite database with messy raw customer data
# Think of this as data that came from your SaaS app

import sqlite3
from datetime import datetime, timedelta
import random


conn = sqlite3.connect("saas_customers.db")
cursor = conn.cursor()

# This is our RAW table — messy column names, inconsistent values, NULLs
# In real life this would come from your app's production database
cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw_customers (
        cust_id     TEXT,     -- bad name, should be customer_id
        usr_email   TEXT,     -- some rows will be NULL (missing emails)
        signup_dt   TEXT,     -- date stored as text string (messy!)
        cancel_dt   TEXT,     -- NULL = still active, has date = churned
        plan_typ    TEXT,     -- 'monthly','MONTHLY','Monthly' all mixed up
        mrr         REAL      -- Monthly Recurring Revenue (dollars they pay)
    )
""")

# Insert 20 fake customers
# Some churned recently, some are still active
data = [
    ("C001", "alice@example.com",   "2024-01-10", None,          "monthly", 29.99),
    ("C002", "bob@example.com",     "2024-01-15", "2024-11-20",  "MONTHLY", 49.99),
    ("C003", None,                  "2024-02-01", "2024-11-25",  "Monthly", 29.99),
    ("C004", "diana@example.com",   "2024-02-10", None,          "annual",  99.99),
    ("C005", "eve@example.com",     "2024-02-20", "2024-12-01",  "ANNUAL",  99.99),
    ("C006", "frank@example.com",   "2024-03-01", None,          "monthly", 49.99),
    ("C007", None,                  "2024-03-10", "2024-12-05",  "Annual",  29.99),
    ("C008", "grace@example.com",   "2024-03-15", None,          "MONTHLY", 99.99),
    ("C009", "henry@example.com",   "2024-04-01", "2024-12-10",  "monthly", 49.99),
    ("C010", "iris@example.com",    "2024-04-10", None,          "annual",  199.99),
    ("C011", "jack@example.com",    "2024-04-20", "2024-12-12",  "ANNUAL",  29.99),
    ("C012", "kate@example.com",    "2024-05-01", None,          "Monthly", 49.99),
    ("C013", None,                  "2024-05-10", "2024-12-15",  "monthly", 99.99),
    ("C014", "leo@example.com",     "2024-05-20", None,          "MONTHLY", 29.99),
    ("C015", "mia@example.com",     "2024-06-01", "2024-12-18",  "annual",  49.99),
    ("C016", "noah@example.com",    "2024-06-10", None,          "Annual",  99.99),
    ("C017", "olivia@example.com",  "2024-06-20", "2024-12-20",  "monthly", 199.99),
    ("C018", "pete@example.com",    "2024-07-01", None,          "ANNUAL",  29.99),
    ("C019", "quinn@example.com",   "2024-07-10", "2024-12-22",  "Monthly", 49.99),
    ("C020", "rosa@example.com",    "2024-07-20", None,          "monthly", 99.99),
]

cursor.executemany("INSERT INTO raw_customers VALUES (?,?,?,?,?,?)", data)
conn.commit()
conn.close()

print("Done! saas_customers.db created with 20 customers.")
print("Open it in DB Browser for SQLite to see the raw messy data!")


# Run it:
# python3 setup_db.py
# Open saas_customers.db in DB Browser — you'll see the messy raw table.
