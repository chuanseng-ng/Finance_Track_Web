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
    if response.status_code != 200:
        error_msg = (
            f"Expected status code 200, got {response.status_code}"  # pragma: no cover
        )
        raise AssertionError(error_msg)
    if b"Expense Tracker" not in response.data:  # Ensure the template is rendered
        error_msg = f"Template not found in response data, got {response.data}"  # pragma: no cover
        raise AssertionError(error_msg)
    mock_get_db.assert_called_once()
    if mock_cursor.execute.call_count != 3:  # Ensure all queries were executed
        error_msg = f"Expected 3 queries, got {mock_cursor.execute.call_count}"  # pragma: no cover
        raise AssertionError(error_msg)


@patch("routes.index_routes.get_db")
# pylint: disable=redefined-outer-name
def test_index_error(mock_get_db, client):
    """Test error handling when a database error occurs."""
    # Mock database connection to raise an exception
    mock_get_db.side_effect = sqlite3.DatabaseError("Mocked database error")

    # Send GET request
    response = client.get("/")

    # Assertions
    if response.status_code != 500:
        error_msg = (
            f"Expected status code 500, got {response.status_code}"  # pragma: no cover
        )
        raise AssertionError(error_msg)
    if response.json != {"error": "An internal error has occurred!"}:
        error_msg = f"Expected error message, got {response.json}"  # pragma: no cover
        raise AssertionError(error_msg)
    mock_get_db.assert_called_once()


# pylint: disable=redefined-outer-name
def test_upload_excel_get(client):
    """Test the GET request to the /upload_excel route."""
    response = client.get("/upload_excel")
    if response.status_code != 200:
        error_msg = (
            f"Expected status code 200, got {response.status_code}"  # pragma: no cover
        )
        raise AssertionError(error_msg)
    if b"Upload Excel File" not in response.data:  # Ensure the page renders correctly
        error_msg = (
            f"Upload page content not found, got {response.data}"  # pragma: no cover
        )
        raise AssertionError(error_msg)


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
    if response.status_code != 200:
        error_msg = (
            f"Expected status code 200, got {response.status_code}"  # pragma: no cover
        )
        raise AssertionError(error_msg)
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
    if response.status_code != 200:  # Redirect back to /upload_excel
        error_msg = (
            f"Expected status code 200, got {response.status_code}"  # pragma: no cover
        )
        raise AssertionError(error_msg)
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
    if response.status_code != 500:
        error_msg = (
            f"Expected status code 500, got {response.status_code}"  # pragma: no cover
        )
        raise AssertionError(error_msg)
    if b"An internal error has occurred!" not in response.data:
        error_msg = f"Unexpected error message, got {response.data}"  # pragma: no cover
        raise AssertionError(error_msg)
    mock_update_database.assert_called_once_with("mock_file.xlsx", 2023)
