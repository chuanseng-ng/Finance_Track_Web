"""This module contains the routes for add_expense."""

import sqlite3
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify

from setup.setup_db import get_db
from setup import setup_stg

api_key, error_bypass = setup_stg.cfg_setup()
if api_key:
    API_URL = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/"
else:
    API_URL = None

expense_bp = Blueprint("expense", __name__)


logging.basicConfig(level=logging.ERROR)


@expense_bp.route("/add_expense", methods=["POST"])
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
