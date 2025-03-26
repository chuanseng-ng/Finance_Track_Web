"""This module contains the routes for the web application"""

import io
import base64
import sqlite3
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template
import matplotlib.pyplot as plt

from setup import setup_stg
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
    """Function to add an expense to the database"""
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
            """INSERT INTO expenses (date, category, item, location, price,
                    currency, price_sgd) VALUES (?, ?, ?, ?, ?, ?, ?)""",
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
    except (KeyError, ValueError, TypeError, sqlite3.DatabaseError):
        logging.error("Exception occurred", exc_info=True)
        return jsonify({"error": "An internal error has occurred!"}), 500


@bp.route("/add_recurring", methods=["POST"])
def add_recurring():
    """Function to add a recurring expense to the database"""
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
            """INSERT INTO recurring_expenses (start_date, end_date, category,
                item, location, ori_price, currency, price_sgd)
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
    except (KeyError, ValueError, TypeError, sqlite3.DatabaseError):
        logging.error("Exception occurred", exc_info=True)
        return jsonify({"error": "An internal error has occurred!"}), 500


@bp.route("/add_salary", methods=["POST"])
def add_salary():
    """Function to add a salary to the database"""
    try:
        data = request.json
        start_year = datetime.strptime(data["start_date"], "%Y-%m-%d").year
        conn = get_db(start_year)
        cursor = conn.cursor()
        amount_sgd = setup_stg.convert_to_sgd(API_URL, data["amount"], data["currency"])

        # Update end_date of previous salary entry if exists
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

        # Insert new salary entry
        cursor.execute(
            """INSERT INTO salary (start_date, end_date, amount)
                                  VALUES (?, ?, ?)""",
            (data["start_date"], "", amount_sgd),
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Salary added successfully"})

    except (KeyError, ValueError, TypeError, sqlite3.DatabaseError):
        logging.error("Exception occurred", exc_info=True)
        return jsonify({"error": "An internal error has occurred!"}), 500


@bp.route("/plot_expenditure")
def plot_expenditure():
    """Function to plot the monthly and yearly expenditure"""
    try:
        current_year = datetime.now().strftime("%Y")
        current_month = datetime.now().strftime("%m")
        conn = get_db(current_year)
        cursor = conn.cursor()

        # Get monthly expenditure
        cursor.execute(
            "SELECT strftime('%d', date) as day, SUM(price_sgd) FROM expenses WHERE strftime('%m', date) = ? GROUP BY day",
            (current_month,),
        )
        month_data = cursor.fetchall()

        # Get yearly expenditure
        cursor.execute(
            "SELECT strftime('%m', date) as month, SUM(price_sgd) FROM expenses WHERE strftime('%Y', date) = ? GROUP BY month",
            (current_year,),
        )
        year_data = cursor.fetchall()

        conn.close()

        # Plot monthly expenditure
        days = [int(day) for day, _ in month_data]
        month_expenses = [expense for _, expense in month_data]
        plt.figure(figsize=(10, 5))
        plt.plot(days, month_expenses, marker="o")
        plt.title("Current Month's Expenditure")
        plt.xlabel("Day")
        plt.ylabel("Expenditure (SGD)")
        plt.grid(True)
        month_img = io.BytesIO()
        plt.savefig(month_img, format="png")
        month_img.seek(0)
        month_plot_url = base64.b64encode(month_img.getvalue()).decode()

        # Plot yearly expenditure
        month_names = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        months = [month_names[int(month) - 1] for month, _ in year_data]
        year_expenses = [expense for _, expense in year_data]
        plt.figure(figsize=(10, 5))
        plt.plot(months, year_expenses, marker="o")
        plt.title("Current Year's Expenditure")
        plt.xlabel("Month")
        plt.ylabel("Expenditure (SGD)")
        plt.grid(True)
        year_img = io.BytesIO()
        plt.savefig(year_img, format="png")
        year_img.seek(0)
        year_plot_url = base64.b64encode(year_img.getvalue()).decode()

        return render_template(
            "graph_plot.html",
            month_plot_url=month_plot_url,
            year_plot_url=year_plot_url,
        )
    except (KeyError, ValueError, TypeError, sqlite3.DatabaseError):
        logging.error("Exception occurred", exc_info=True)
        return jsonify({"error": "An internal error has occurred!"}), 500


@bp.route("/")
def index():
    """Function to render the index page"""
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
            "SELECT SUM(price_sgd) FROM recurring_expenses WHERE \
            (CAST(strftime('%m', start_date) AS INTEGER) <= ? AND \
            CAST(strftime('%Y', start_date) AS INTEGER) <= ?) AND \
            (end_date IS ? OR \
            (CAST(strftime('%m', end_date) AS INTEGER) >= ? AND \
            CAST(strftime('%Y', end_date) AS INTEGER) >= ?))",
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
            "SELECT SUM(amount) FROM salary WHERE \
            (CAST(strftime('%m', start_date) AS INTEGER) <= ? AND \
            CAST(strftime('%Y', start_date) AS INTEGER) <= ?) AND \
            (end_date IS ? OR \
            (CAST(strftime('%m', end_date) AS INTEGER) > ? AND \
            CAST(strftime('%Y', end_date) AS INTEGER) = ?) OR \
            (CAST(strftime('%Y', end_date) AS INTEGER) > ?))",
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

    except (KeyError, ValueError, TypeError, sqlite3.DatabaseError):
        logging.error("Exception occurred", exc_info=True)
        return jsonify({"error": "An internal error has occurred!"}), 500
