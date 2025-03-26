"""This module contains the routes for plotting expenditure."""

import io
import base64
import sqlite3
import logging

from datetime import datetime
from flask import Blueprint, request, render_template, jsonify
import matplotlib.pyplot as plt

from setup.setup_db import get_db

plot_bp = Blueprint("plot", __name__)


@plot_bp.route("/plot_expenditure")
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


@plot_bp.route("/plot_custom_expenditure")
def plot_custom_expenditure():
    """Function to plot expenditure for a custom date range"""
    try:
        # Get start_date and end_date from query parameters
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if not start_date or not end_date:
            return jsonify({"error": "Start date and end date are required"}), 400

        conn = get_db(datetime.now().year)
        cursor = conn.cursor()

        # Query expenditures within the custom date range
        cursor.execute(
            """
            SELECT date, SUM(price_sgd)
            FROM expenses
            WHERE date BETWEEN ? AND ?
            GROUP BY date
            """,
            (start_date, end_date),
        )
        custom_data = cursor.fetchall()
        conn.close()

        # Prepare data for plotting
        dates = [
            datetime.strptime(date, "%Y-%m-%d").strftime("%d %b")
            for date, _ in custom_data
        ]
        expenses = [expense for _, expense in custom_data]

        # Plot custom date range expenditure
        plt.figure(figsize=(10, 5))
        plt.plot(dates, expenses, marker="o")
        plt.title(f"Expenditure from {start_date} to {end_date}")
        plt.xlabel("Date")
        plt.ylabel("Expenditure (SGD)")
        plt.xticks(rotation=45)
        plt.grid(True)

        custom_img = io.BytesIO()
        plt.savefig(custom_img, format="png")
        custom_img.seek(0)
        custom_plot_url = base64.b64encode(custom_img.getvalue()).decode()

        return render_template(
            "custom_plot.html",
            custom_plot_url=custom_plot_url,
            start_date=start_date,
            end_date=end_date,
        )
    except (KeyError, ValueError, TypeError, sqlite3.DatabaseError):
        logging.error("Exception occurred", exc_info=True)
        return jsonify({"error": "An internal error has occurred!"}), 500
