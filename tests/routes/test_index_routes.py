"""This module contains the tests for the index_routes module."""

import sqlite3
from unittest.mock import patch, MagicMock
import pytest
from flask import Flask
from routes.index_routes import index_bp
from routes.admin_routes import admin_bp  # Import the admin blueprint


@pytest.fixture
def client():
    """Fixture to create a Flask test client."""
    app = Flask(__name__, template_folder="../../templates")
    app.secret_key = "test_secret_key"
    app.register_blueprint(index_bp)
    app.register_blueprint(
        admin_bp, url_prefix="/admin"
    )  # Register the admin blueprint
    with app.test_client() as client:  # pylint: disable=redefined-outer-name
        yield client


@patch("routes.index_routes.get_db")
# pylint: disable=redefined-outer-name
def test_index_success(mock_get_db, client):
    """Test successful rendering of the index page."""
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock database queries
    mock_cursor.fetchone.side_effect = [
        (100.0,),  # Monthly spending
        (50.0,),  # Recurring expenses
        (200.0,),  # Monthly salary
    ]

    # Send GET request
    response = client.get("/")

    # Assertions
    assert response.status_code == 200
    assert (
        b"Personal Web-based Expense Tracker" in response.data
    )  # Ensure the template is rendered
    mock_get_db.assert_called_once()
    assert mock_cursor.execute.call_count == 3  # Ensure all queries were executed


@patch("routes.index_routes.get_db")
# pylint: disable=redefined-outer-name
def test_index_error(mock_get_db, client):
    """Test error handling when a database error occurs."""
    # Mock database connection to raise an exception
    mock_get_db.side_effect = sqlite3.DatabaseError("Mocked database error")

    # Send GET request
    response = client.get("/")

    # Assertions
    assert response.status_code == 500
    assert response.json == {"error": "An internal error has occurred!"}
    mock_get_db.assert_called_once()


# pylint: disable=redefined-outer-name
def test_upload_excel_get(client):
    """Test the GET request to the /upload_excel route."""
    response = client.get("/upload_excel")
    assert response.status_code == 200
    assert b"Upload Excel File" in response.data  # Ensure the page renders correctly


@patch("routes.index_routes.update_database_from_excel")
# pylint: disable=redefined-outer-name
def test_upload_excel_post_success(mock_update_database, client):
    """Test the POST request to the /upload_excel route with valid data."""
    # Mock the update_database_from_excel function
    mock_update_database.return_value = None

    # Send POST request with valid data
    response = client.post(
        "/upload_excel",
        data={"excel_path": "mock_file.xlsx", "year": "2023"},
        follow_redirects=True,
    )

    # Assertions
    assert response.status_code == 200
    mock_update_database.assert_called_once_with("mock_file.xlsx", 2023)


@patch("routes.index_routes.update_database_from_excel")
# pylint: disable=redefined-outer-name
def test_upload_excel_post_missing_data(mock_update_database, client):
    """Test the POST request to the /upload_excel route with missing data."""
    # Send POST request with missing data
    response = client.post(
        "/upload_excel",
        data={"excel_path": "", "year": ""},
        follow_redirects=True,
    )

    # Assertions
    assert response.status_code == 200  # Redirect back to /upload_excel
    mock_update_database.assert_not_called()


@patch("routes.index_routes.update_database_from_excel")
# pylint: disable=redefined-outer-name
def test_upload_excel_post_exception(mock_update_database, client):
    """Test the POST request to the /upload_excel route when an exception occurs."""
    # Mock the update_database_from_excel function to raise an exception
    mock_update_database.side_effect = ValueError("Mock exception")

    # Send POST request with valid data
    response = client.post(
        "/upload_excel",
        data={"excel_path": "mock_file.xlsx", "year": "2023"},
        follow_redirects=True,
    )

    # Assertions
    assert response.status_code == 500
    assert b"An internal error has occurred!" in response.data
    mock_update_database.assert_called_once_with("mock_file.xlsx", 2023)
