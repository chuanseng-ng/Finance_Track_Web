import sqlite3


# Function to get SQL database and create table if no exists
def get_db(year):
    db_name = f"expenses_{year}.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        category TEXT,
                        item TEXT,
                        location TEXT,
                        price REAL,
                        currency TEXT,
                        price_sgd REAL)"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS recurring_expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_date TEXT,
                        end_date TEXT,
                        category TEXT,
                        item TEXT,
                        location TEXT,
                        ori_price REAL,
                        currency TEXT,
                        price_sgd REAL)"""
    )
    conn.commit()
    return conn
