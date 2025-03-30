"""This module contains the routes for plotting expenditure."""

import io
import base64
import sqlite3
import logging

from datetime import datetime
from flask import Blueprint, request, render_template, jsonify
import matplotlib.pyplot as plt
import plotly.graph_objects as go

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

        # Parse the start and end dates
        start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        start_year = int(start_date.split("-")[0])
        end_year = int(end_date.split("-")[0])

        # Initialize list to store all data
        custom_data = []

        # Loop through each year in the range and query the respective database
        for year in range(start_year, end_year + 1):
            conn = get_db(year)
            cursor = conn.cursor()

            # Adjust the date range for the current year
            year_start_date = max(start_date, f"{year}-01-01")
            year_end_date = min(end_date, f"{year}-12-31")

            # Query expenditures within the custom date range for the current year
            cursor.execute(
                """
                SELECT date, SUM(price_sgd)
                FROM expenses
                WHERE date BETWEEN ? AND ?
                GROUP BY date
                """,
                (year_start_date, year_end_date),
            )
            # Format the date to ensure consistency
            custom_data.extend(
                [
                    (
                        datetime.strptime(row[0].split(" ")[0], "%Y-%m-%d").strftime(
                            "%Y-%m-%d"
                        ),
                        row[1],
                    )
                    for row in cursor.fetchall()
                ]
            )
            conn.close()

        # Prepare data for plotting
        custom_data.sort(key=lambda x: x[0])  # Sort by date
        dates = [date for date, _ in custom_data]
        expenses = [expense for _, expense in custom_data]

        # Create an interactive plot using Plotly
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=expenses,
                mode="lines+markers",
                marker={"size": 8},
                line={"color": "blue"},
                hovertemplate="<b>Date:</b> %{x}<br><b>Expenditure:</b> SGD %{y}<extra></extra>",
            )
        )
        fig.update_layout(
            title=f"Expenditure from {start_date} to {end_date}",
            xaxis_title="Date",
            yaxis_title="Expenditure (SGD)",
            xaxis={"tickformat": "%d %b"},
            template="plotly_white",
        )

        # Convert the plot to HTML
        plot_html = fig.to_html(full_html=False)

        return render_template(
            "custom_plot.html",
            plot_html=plot_html,
            start_date=start_date,
            end_date=end_date,
        )
    except (KeyError, ValueError, TypeError, sqlite3.DatabaseError):
        logging.error("Exception occurred", exc_info=True)
        return jsonify({"error": "An internal error has occurred!"}), 500
