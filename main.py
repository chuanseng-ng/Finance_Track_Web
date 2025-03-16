from flask import Flask, render_template, request, jsonify
from datetime import datetime

import setup.setup_stg as setup_stg

import sqlite3

app = Flask(__name__)


api_key = setup_stg.cfg_setup()

API_URL = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/"


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


# Function to hook up to SQL database and perform web-based interaction
## Add daily expenses (1-time)
@app.route("/add_expense", methods=["POST"])
def add_expense():
    data = request.json
    year = datetime.strptime(data["date"], "%Y-%m-%d").year
    conn = get_db(year)
    cursor = conn.cursor()
    price_sgd = setup_stg.convert_to_sgd(API_URL, data["price"], data["currency"])
    cursor.execute(
        """INSERT INTO expenses (date, category, item, location, price, currency, price_sgd)
                      VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            data["date"],
            data["category"],
            data["item"],
            data["location"],
            data["price"],
            data["currency"],
            price_sgd,
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Expense added successfully"})


## Add recurring expenses
@app.route("/add_recurring", methods=["POST"])
def add_recurring():
    data = request.json
    start_year = datetime.strptime(data["start_date"], "%Y-%m").year
    end_year = datetime.strptime(data["end_date"], "%Y-%m").year
    conn = get_db(start_year)
    cursor = conn.cursor()
    price_sgd = setup_stg.convert_to_sgd(API_URL, data["price"], data["currency"])
    months_count = (end_year - start_year) * 12 + (
        datetime.strptime(data["end_date"], "%Y-%m").month
        - datetime.strptime(data["start_date"], "%Y-%m").month
        + 1
    )
    monthly_price = int(price_sgd) / int(months_count)
    cursor.execute(
        """INSERT INTO recurring_expenses (start_date, end_date, category, item, location, ori_price, currency, price_sgd)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["start_date"],
            data["end_date"],
            data["category"],
            data["item"],
            data["location"],
            data["price"],
            data["currency"],
            monthly_price,
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Recurring expense added successfully"})


# Main function
@app.route("/")
def index():
    current_year = datetime.now().year
    current_month = datetime.now().strftime("%m")
    conn = get_db(current_year)
    cursor = conn.cursor()
    ## Get sum of expenses in the current month
    cursor.execute(
        "SELECT SUM(price_sgd) FROM expenses WHERE strftime('%m', date) = ?",
        (current_month,),
    )
    month_spend = cursor.fetchone()[0] or 0
    ## Get sum of recurring expenses valid in current month
    cursor.execute(
        "SELECT SUM(price_sgd) FROM recurring_expenses WHERE (CAST(strftime('%m', start_date) AS INTEGER) <= ? AND CAST(strftime('%Y', start_date) AS INTEGER) <= ?) AND (CAST(strftime('%m', end_date) AS INTEGER) >= ? AND CAST(strftime('%Y', end_date) AS INTEGER) >= ?)",
        (int(current_month), int(current_year), int(current_month), int(current_year)),
    )
    month_recur_spend = cursor.fetchone()[0] or 0
    total_month_spend = month_spend + month_recur_spend
    conn.close()
    return render_template(
        "index.html", monthly_spending=total_month_spend, datetime=datetime
    )


if __name__ == "__main__":
    app.run(debug=True)
