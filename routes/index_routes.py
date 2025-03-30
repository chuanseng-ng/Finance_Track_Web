"""This module contains the routes for the index page."""

import logging
import sqlite3

from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, redirect, url_for

from setup.setup_db import get_db
from db_import.db_import import update_database_from_excel

index_bp = Blueprint("index", __name__)


@index_bp.route("/")
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


@index_bp.route("/upload_excel", methods=["GET", "POST"])
def upload_excel():
    """Render the page to input the Excel file path and handle the upload."""
    if request.method == "POST":
        excel_path = request.form.get("excel_path")
        year = request.form.get("year")

        if not excel_path or not year:
            jsonify({"error": "Please provide both the Excel file path and the year."})
            return redirect(url_for("index.upload_excel"))

        try:
            # Call the function to update the database
            update_database_from_excel(excel_path, int(year))
            jsonify({"message": "Database updated successfully!"})
        except (KeyError, ValueError, TypeError, sqlite3.DatabaseError):
            logging.error("Exception occurred", exc_info=True)
            return jsonify({"error": "An internal error has occurred!"}), 500

        return redirect(url_for("index.index"))

    return render_template("upload_excel.html")
