from flask import Flask, render_template, request, jsonify
from datetime import datetime

import requests
import sqlite3
import yaml

app = Flask(__name__)


# Function to map yaml file's user-config to parameters
def cfg_setup():
    # Load config file
    with open("cfg/user_config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Accessing config settings
    api_key = config["api_key"]

    # Make sure API key exists before continuing script
    if not (api_key):
        print(
            "Create personal API key at exchangerate-api.com and input to user_config.yaml"
        )
        print("Do not upload personal API key!")
        raise ValueError("API Key is empty in user_config.yaml!")
    else:
        return api_key


api_key = cfg_setup()

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
    conn.commit()
    return conn


# Function to convert other currencies to SGD
## Use exchangerate-api.com for exchange rate data
def convert_to_sgd(cost, currency):
    if currency == "SGD":
        return cost

    curr_url = API_URL + currency
    response = requests.get(curr_url)
    if response.status_code == 200:
        rates = response.json().get("conversion_rates", {})
        sgd_rate = rates.get("SGD")
        if sgd_rate:
            return float(cost) * sgd_rate

    return None


# Function to hook up to SQL database and perform web-based interaction
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


# Main function
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


if __name__ == "__main__":
    app.run(debug=True)
