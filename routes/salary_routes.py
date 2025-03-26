"""This module contains the routes for add_salary."""

import sqlite3
import logging

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify

from setup.setup_db import get_db
from setup import setup_stg

api_key, error_bypass = setup_stg.cfg_setup()
if api_key:
    API_URL = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/"
else:
    API_URL = None

salary_bp = Blueprint("salary", __name__)


@salary_bp.route("/add_salary", methods=["POST"])
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
