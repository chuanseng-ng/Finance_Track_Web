"""This module contains the routes for the admin panel of the application."""

import os
import sqlite3
import yaml
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from werkzeug.security import generate_password_hash, check_password_hash

admin_bp = Blueprint("admin", __name__)

# Load admin credentials from user_config.yaml
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../cfg/user_config.yaml")

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
        ADMIN_USERNAME = config.get("admin_username", "adm1n")  # Default to "admin"
        ADMIN_PASSWORD = config.get(
            "admin_password", "securepassw0rd"
        )  # Default to "securepassword"
except FileNotFoundError:  # pragma: no cover
    ADMIN_USERNAME = "adm2n"
    ADMIN_PASSWORD = "securepassw1rd"

# Hash the admin password
ADMIN_PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD)


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    """Admin login page."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # pylint: disable=no-else-return
        if username == ADMIN_USERNAME and check_password_hash(
            ADMIN_PASSWORD_HASH, password
        ):
            session["admin_logged_in"] = True
            flash("Login successful!", "success")
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("admin_login.html")


@admin_bp.route("/edit_table", methods=["GET", "POST"])
def edit_table():
    """Display and edit the SQL database as a table based on a date range."""
    if not session.get("admin_logged_in"):
        flash("Please log in to access the admin dashboard.", "warning")
        return redirect(url_for("admin.login"))

    db_year = request.args.get("year")  # Get the year from query parameters
    start_date = request.args.get(
        "start_date"
    )  # Get the start date from query parameters
    end_date = request.args.get("end_date")  # Get the end date from query parameters

    if not db_year or not start_date or not end_date:
        # If year or date range is not provided, render a form to input them
        return render_template("select_date_range.html")

    try:
        conn = sqlite3.connect(
            f"expenses_{db_year}.db"
        )  # Connect to the selected database
        cursor = conn.cursor()

        if request.method == "POST":
            # Handle updates to the database
            record_id = request.form.get("id")
            column = request.form.get("column")
            value = request.form.get("value")

            # Validate the column name against a predefined list of allowed columns
            allowed_columns = ["name", "amount", "date"]  # Example allowed columns
            if column not in allowed_columns:
                return jsonify({"success": False, "error": "Invalid column name."}), 400

            try:
                cursor.execute(
                    f"UPDATE expenses SET {column} = ? WHERE id = ?",
                    (value, record_id),
                )
                conn.commit()
                return jsonify({"success": True})
            except sqlite3.Error as e:
                app.logger.error(f"Database error: {str(e)}")
                return jsonify({"success": False, "error": "An internal error occurred."})

        # Fetch data for the table based on the date range
        cursor.execute(
            "SELECT * FROM expenses WHERE date BETWEEN ? AND ?",
            (start_date, end_date),
        )
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()

        return render_template(
            "edit_table.html",
            rows=rows,
            columns=columns,
            year=db_year,
            start_date=start_date,
            end_date=end_date,
        )

    except sqlite3.Error as e:
        flash(
            f"Error connecting to the database for year {db_year}: {str(e)}", "danger"
        )
        return redirect(url_for("admin.edit_table"))


@admin_bp.route("/logout")
def logout():
    """Admin logout."""
    session.pop("admin_logged_in", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("admin.login"))


@admin_bp.route("/dashboard")
def dashboard():
    """Admin dashboard."""
    if not session.get("admin_logged_in"):
        flash("Please log in to access the admin dashboard.", "warning")
        return redirect(url_for("admin.login"))

    return render_template("admin_dashboard.html")
