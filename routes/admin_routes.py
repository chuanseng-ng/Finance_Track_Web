"""This module contains the routes for the admin panel of the application."""

import os
import yaml
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
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
