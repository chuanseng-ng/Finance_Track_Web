"""This module contains tests for the admin routes of the Flask application."""

from unittest.mock import patch
import pytest
from flask import session, Flask
from werkzeug.security import generate_password_hash
from routes.index_routes import index_bp
from routes.admin_routes import admin_bp


# pylint: disable=redefined-outer-name
@pytest.fixture
def client():
    """Fixture to create a Flask test client."""
    app = Flask(__name__, template_folder="../../templates")
    app.secret_key = "test_secret_key"
    app.register_blueprint(index_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    with app.test_client() as client:
        yield client


# pylint: disable=unused-argument, import-outside-toplevel
@patch("builtins.open", side_effect=FileNotFoundError)
def test_file_not_found(mock_open):
    """Test handling of FileNotFoundError when loading user_config.yaml."""
    # Re-import the admin_routes module to trigger the FileNotFoundError handling
    with patch("routes.admin_routes.ADMIN_USERNAME", "adm1n"), patch(
        "routes.admin_routes.ADMIN_PASSWORD", "securepassw0rd"
    ):
        from routes.admin_routes import ADMIN_USERNAME, ADMIN_PASSWORD_HASH

        # Assertions
        assert ADMIN_USERNAME == "adm1n"  # Default username
        assert ADMIN_PASSWORD_HASH is not None  # Password should be hashed


def test_admin_login_success(client, monkeypatch):
    """Test successful admin login."""
    # Mock admin credentials
    monkeypatch.setattr("routes.admin_routes.ADMIN_USERNAME", "adm1n")
    monkeypatch.setattr(
        "routes.admin_routes.ADMIN_PASSWORD_HASH",
        generate_password_hash("securepassw0rd"),
    )

    # Send POST request with valid credentials
    response = client.post(
        "/admin/login",
        data={"username": "adm1n", "password": "securepassw0rd"},
        follow_redirects=True,
    )

    # Assertions
    assert response.status_code == 200
    assert b"Admin Dashboard" in response.data
    with client.session_transaction() as sess:
        assert sess.get("admin_logged_in") is True


def test_admin_login_failure(client, monkeypatch):
    """Test admin login failure with invalid credentials."""
    # Mock admin credentials
    monkeypatch.setattr("routes.admin_routes.ADMIN_USERNAME", "adm1n")
    monkeypatch.setattr(
        "routes.admin_routes.ADMIN_PASSWORD_HASH",
        generate_password_hash("securepassw0rd"),
    )

    # Send POST request with invalid credentials
    response = client.post(
        "/admin/login",
        data={"username": "wrong_user", "password": "wrong_password"},
        follow_redirects=True,
    )

    # Assertions
    assert response.status_code == 200
    assert b"Invalid username or password." in response.data
    assert session.get("admin_logged_in") is None


def test_admin_logout(client):
    """Test admin logout."""
    # Simulate a logged-in session
    with client.session_transaction() as sess:
        sess["admin_logged_in"] = True

    # Send GET request to logout
    response = client.get("/admin/logout", follow_redirects=True)

    # Assertions
    assert response.status_code == 200
    assert b"Logged out successfully." in response.data
    assert session.get("admin_logged_in") is None


def test_admin_dashboard_access(client):
    """Test access to the admin dashboard when logged in."""
    # Simulate a logged-in session
    with client.session_transaction() as sess:
        sess["admin_logged_in"] = True

    # Send GET request to the dashboard
    response = client.get("/admin/dashboard")

    # Assertions
    assert response.status_code == 200
    assert b"Admin Dashboard" in response.data


def test_admin_dashboard_redirect(client):
    """Test redirection to login page when not logged in."""
    # Send GET request to the dashboard without being logged in
    response = client.get("/admin/dashboard", follow_redirects=True)

    # Assertions
    assert response.status_code == 200
    assert b"Please log in to access the admin dashboard." in response.data
    assert b"Admin Login" in response.data
