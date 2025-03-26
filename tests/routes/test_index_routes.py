"""This module contains the tests for the index_routes module."""

import sqlite3
from unittest.mock import patch, MagicMock
import pytest
from flask import Flask
from routes.index_routes import index_bp


@pytest.fixture
def client():
    """Fixture to create a Flask test client."""
    app = Flask(__name__, template_folder="../../templates")
    app.register_blueprint(index_bp)
    with app.test_client() as client:  # pylint: disable=redefined-outer-name
        yield client


@patch("routes.index_routes.get_db")
def test_index_success(mock_get_db, client):  # pylint: disable=redefined-outer-name
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
def test_index_error(mock_get_db, client):  # pylint: disable=redefined-outer-name
    """Test error handling when a database error occurs."""
    # Mock database connection to raise an exception
    mock_get_db.side_effect = sqlite3.DatabaseError("Mocked database error")

    # Send GET request
    response = client.get("/")

    # Assertions
    assert response.status_code == 500
    assert response.json == {"error": "An internal error has occurred!"}
    mock_get_db.assert_called_once()
