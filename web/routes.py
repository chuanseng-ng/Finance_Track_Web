from flask import Blueprint, request, jsonify, render_template
from datetime import datetime, timedelta
import logging

import setup.setup_stg as setup_stg
from setup.setup_db import get_db

api_key, error_bypass = setup_stg.cfg_setup()

if api_key:
    API_URL = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/"
else:
    API_URL = None

bp = Blueprint("main", __name__)

logging.basicConfig(level=logging.ERROR)


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
        logging.error("Exception occurred", exc_info=True)
        return jsonify({"error": "An internal error has occurred!"}), 500


@bp.route("/add_recurring", methods=["POST"])
def add_recurring():
    try:
        data = request.json
        start_year = datetime.strptime(data["start_date"], "%Y-%m-%d").year
        end_date = data.get("end_date")
        if end_date:
            end_year = datetime.strptime(end_date, "%Y-%m-%d").year
        else:
            end_year = None
        conn = get_db(start_year)
        cursor = conn.cursor()
        price_sgd = setup_stg.convert_to_sgd(API_URL, data["price"], data["currency"])
        if end_year:
            months_count = (end_year - start_year) * 12 + (
                datetime.strptime(end_date, "%Y-%m-%d").month
                - datetime.strptime(data["start_date"], "%Y-%m-%d").month
                + 1
            )
            monthly_price = int(price_sgd) / int(months_count)
        else:
            monthly_price = price_sgd
        cursor.execute(
            """INSERT INTO recurring_expenses (start_date, end_date, category, item, location, ori_price, currency, price_sgd)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["start_date"],
                end_date,
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
        logging.error("Exception occurred", exc_info=True)
        return jsonify({"error": "An internal error has occurred!"}), 500


@bp.route("/add_salary", methods=["POST"])
def add_salary():
    try:
        data = request.json
        start_year = datetime.strptime(data["start_date"], "%Y-%m-%d").year
        conn = get_db(start_year)
        cursor = conn.cursor()
        amount_sgd = setup_stg.convert_to_sgd(API_URL, data["amount"], data["currency"])

        ## Update end_date of previous salary entry if exists
        cursor.execute("SELECT COUNT(*) FROM salary")
        salary_count = cursor.fetchone()[0]

        if salary_count > 0:
            end_date = (
                datetime.strptime(data["start_date"], "%Y-%m-%d") - timedelta(days=1)
            ).strftime("%Y-%m-%d")
            cursor.execute(
                "UPDATE salary SET end_date = ? WHERE end_date IS ?",
                (
                    end_date,
                    "",
                ),
            )

        ## Insert new salary entry
        cursor.execute(
            """INSERT INTO salary (start_date, end_date, amount)
                                  VALUES (?, ?, ?)""",
            (data["start_date"], "", amount_sgd),
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Salary added successfully"})

    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        return jsonify({"error": "An internal error has occurred!"}), 500


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
            "SELECT SUM(price_sgd) FROM recurring_expenses WHERE (CAST(strftime('%m', start_date) AS INTEGER) <= ? AND CAST(strftime('%Y', start_date) AS INTEGER) <= ?) AND \
                    (end_date IS ? OR (CAST(strftime('%m', end_date) AS INTEGER) >= ? AND CAST(strftime('%Y', end_date) AS INTEGER) >= ?))",
            (
                int(current_month),
                int(current_year),
                "",
                int(current_month),
                int(current_year),
            ),
        )
        month_recur_spend = cursor.fetchone()[0] or 0
        total_month_spend = month_spend + month_recur_spend

        cursor.execute(
            "SELECT SUM(amount) FROM salary WHERE (CAST(strftime('%m', start_date) AS INTEGER) <= ? AND CAST(strftime('%Y', start_date) AS INTEGER) <= ?) AND \
                    (end_date IS ? OR (CAST(strftime('%m', end_date) AS INTEGER) > ? AND CAST(strftime('%Y', end_date) AS INTEGER) = ?) OR (CAST(strftime('%Y', end_date) AS INTEGER) > ?))",
            (
                int(current_month),
                int(current_year),
                "",
                int(current_month),
                int(current_year),
                int(current_year),
            ),
        )
        month_salary = cursor.fetchone()[0] or 0
        total_month_balance = month_salary - total_month_spend

        conn.close()
        return render_template(
            "index.html",
            monthly_spending=total_month_spend,
            monthly_balance=total_month_balance,
            datetime=datetime,
        )

    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        return jsonify({"error": "An internal error has occurred!"}), 500
