"""Module used to create a SQLite database for the expenses and salary data"""

import sqlite3


def get_db(year):
    """Function to get SQL database and create table if no exists"""
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
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS salary (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_date TEXT,
                        end_date TEXT,
                        amount REAL)"""
    )
    conn.commit()
    return conn
