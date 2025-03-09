from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import requests
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

API_URL = "https://api.exchangerate-api.com/v4/latest/"


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
                        price REAL,
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


def convert_to_sgd(amount, currency):
    if currency == "SGD":
        return amount
    response = requests.get(API_URL + currency)
    if response.status_code == 200:
        rates = response.json().get("rates", {})
        sgd_rate = rates.get("SGD")
        if sgd_rate:
            return amount * sgd_rate
    return None


@app.route("/add_expense", methods=["POST"])
def add_expense():
    data = request.json
    year = datetime.strptime(data["date"], "%Y-%m-%d").year
    conn = get_db(year)
    cursor = conn.cursor()
    price_sgd = convert_to_sgd(data["price"], data["currency"])
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


@app.route("/add_recurring", methods=["POST"])
def add_recurring():
    data = request.json
    start_year = datetime.strptime(data["start_date"], "%Y-%m").year
    end_year = datetime.strptime(data["end_date"], "%Y-%m").year
    conn = get_db(start_year)
    cursor = conn.cursor()
    price_sgd = convert_to_sgd(data["price"], data["currency"])
    months_count = (end_year - start_year) * 12 + (
        datetime.strptime(data["end_date"], "%Y-%m").month
        - datetime.strptime(data["start_date"], "%Y-%m").month
        + 1
    )
    monthly_price = int(price_sgd) / int(months_count)
    cursor.execute(
        """INSERT INTO recurring_expenses (start_date, end_date, category, item, location, price, currency, price_sgd)
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


@app.route("/")
def index():
    current_year = datetime.now().year
    current_month = datetime.now().strftime("%m")
    conn = get_db(current_year)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SUM(price_sgd) FROM expenses WHERE strftime('%m', date) = ?",
        (current_month,),
    )
    monthly_spending = cursor.fetchone()[0] or 0
    conn.close()
    return render_template(
        "index.html", monthly_spending=monthly_spending, datetime=datetime
    )


@app.route("/summary/<int:year>")
def summary(year):
    conn = get_db(year)
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(price_sgd) FROM expenses GROUP BY category")
    category_summary = cursor.fetchall()

    cursor.execute(
        "SELECT strftime('%m', date), SUM(price_sgd) FROM expenses GROUP BY strftime('%m', date)"
    )
    monthly_summary = cursor.fetchall()

    cursor.execute("SELECT start_date, end_date, amount FROM salary")
    salary_data = cursor.fetchall()
    conn.close()

    categories, category_totals = (
        zip(*category_summary) if category_summary else ([], [])
    )
    months, month_totals = zip(*monthly_summary) if monthly_summary else ([], [])

    salary_dict = {}
    for start_date, end_date, amount in salary_data:
        start_year, start_month = map(int, start_date.split("-"))
        end_year, end_month = map(int, end_date.split("-"))
        for y in range(start_year, end_year + 1):
            for m in range(1, 13):
                if (
                    (y == start_year and m >= start_month)
                    or (y == end_year and m <= end_month)
                    or (start_year < y < end_year)
                ):
                    key = f"{y}-{m:02d}"
                    salary_dict[key] = salary_dict.get(key, 0) + amount / (
                        (end_year - start_year) * 12 + (end_month - start_month + 1)
                    )

    month_names = [datetime.strptime(month, "%m").strftime("%B") for month in months]
    balance_totals = [
        salary_dict.get(f"{year}-{month}", 0) - total
        for month, total in zip(months, month_totals)
    ]

    plt.figure(figsize=(8, 5))
    plt.plot(
        month_names,
        balance_totals,
        marker="o",
        linestyle="-",
        color="green",
        label="Balance Remaining",
    )
    plt.xlabel("Month")
    plt.ylabel("Remaining Balance (SGD)")
    plt.title(f"Balance Trend for {year}")
    plt.legend()
    plt.xticks(rotation=45)

    img = io.BytesIO()
    plt.savefig(img, format="png")
    plt.close()
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template(
        "summary.html",
        year=year,
        category_summary=zip(categories, category_totals),
        monthly_summary=zip(month_names, month_totals),
        balance_plot_url=plot_url,
    )


if __name__ == "__main__":
    app.run(debug=True)
