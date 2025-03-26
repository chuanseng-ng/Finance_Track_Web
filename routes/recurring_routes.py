"""This module contains the routes for add_recurring."""

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

recurring_bp = Blueprint("recurring", __name__)


@recurring_bp.route("/add_recurring", methods=["POST"])
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
