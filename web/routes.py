from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
import setup.setup_stg as setup_stg
from setup.setup_db import get_db

api_key, error_bypass = setup_stg.cfg_setup()

if api_key:
    API_URL = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/"
else:
    API_URL = None

bp = Blueprint("main", __name__)


@bp.route("/add_expense", methods=["POST"])
def add_expense():
    try:
        data = request.json
        year = datetime.strptime(data["date"], "%Y-%m-%d").year
        conn = get_db(year)
        cursor = conn.cursor()
        if API_URL:
            price_sgd = setup_stg.convert_to_sgd(
                API_URL, data["price"], data["currency"]
            )
        else:
            price_sgd = data["price"]
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/add_recurring", methods=["POST"])
def add_recurring():
    try:
        data = request.json
        start_year = datetime.strptime(data["start_date"], "%Y-%m").year
        end_year = datetime.strptime(data["end_date"], "%Y-%m").year
        conn = get_db(start_year)
        cursor = conn.cursor()
        if API_URL:
            price_sgd = setup_stg.convert_to_sgd(
                API_URL, data["price"], data["currency"]
            )
        else:
            price_sgd = data["price"]
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/")
def index():
    try:
        current_year = datetime.now().year
        current_month = datetime.now().strftime("%m")
        conn = get_db(current_year)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT SUM(price_sgd) FROM expenses WHERE strftime('%m', date) = ?",
            (current_month,),
        )
        month_spend = cursor.fetchone()[0] or 0
        cursor.execute(
            "SELECT SUM(price_sgd) FROM recurring_expenses WHERE (CAST(strftime('%m', start_date) AS INTEGER) <= ? AND CAST(strftime('%Y', start_date) AS INTEGER) <= ?) AND (CAST(strftime('%m', end_date) AS INTEGER) >= ? AND CAST(strftime('%Y', end_date) AS INTEGER) >= ?)",
            (
                int(current_month),
                int(current_year),
                int(current_month),
                int(current_year),
            ),
        )
        month_recur_spend = cursor.fetchone()[0] or 0
        total_month_spend = month_spend + month_recur_spend
        conn.close()
        return render_template(
            "index.html", monthly_spending=total_month_spend, datetime=datetime
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
