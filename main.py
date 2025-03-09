from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime


app = Flask(__name__)


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
                        price REAL)"""
    )
    conn.commit()
    return conn


# Function to hook up to SQL database and perform web-based interaction
@app.route("/add_expense", methods=["POST"])
def add_expense():
    data = request.json
    year = datetime.strptime(data["date"], "%Y-%m-%d").year
    conn = get_db(year)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO expenses (date, category, item, location, price)
                      VALUES (?, ?, ?, ?, ?)""",
        (
            data["date"],
            data["category"],
            data["item"],
            data["location"],
            data["price"],
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Expense added successfully"})


@app.route("/")
def index():
    current_year = datetime.now().year
    current_month = datetime.now().strftime("%m")
    conn = get_db(current_year)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SUM(price) FROM expenses WHERE strftime('%m', date) = ?",
        (current_month,),
    )
    monthly_spending = cursor.fetchone()[0] or 0
    conn.close()
    return render_template(
        "index.html", monthly_spending=monthly_spending, datetime=datetime
    )


if __name__ == "__main__":
    app.run(debug=True)
