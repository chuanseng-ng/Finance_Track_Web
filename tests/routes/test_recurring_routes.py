"""This module contains tests for the recurring_routes module."""

import sqlite3
from unittest.mock import patch, MagicMock
import pytest
from flask import Flask
from routes.recurring_routes import recurring_bp


@pytest.fixture
def client():
    """Fixture to create a Flask test client."""
    app = Flask(__name__)
    app.register_blueprint(recurring_bp)
    # pylint: disable=redefined-outer-name
    with app.test_client() as client:
        yield client


@patch("routes.recurring_routes.get_db")
@patch("routes.recurring_routes.setup_stg.convert_to_sgd")
# pylint: disable=redefined-outer-name
def test_add_recurring_success(mock_convert_to_sgd, mock_get_db, client):
    """Test successful addition of a recurring expense."""
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock currency conversion
    mock_convert_to_sgd.return_value = 100.0

    # Test data
    recurring_data = {
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "category": "Subscription",
        "item": "Streaming Service",
        "location": "Online",
        "price": 1200.0,
        "currency": "USD",
    }

    # Send POST request
    response = client.post("/add_recurring", json=recurring_data)

    # Assertions
    assert response.status_code == 200
    assert response.json == {"message": "Recurring expense added successfully"}
    mock_get_db.assert_called_once_with(2025)
    # Skip convert_to_sgd call due to API key
    # mock_convert_to_sgd.assert_called_once_with(
    #     "https://v6.exchangerate-api.com/v6/<api_key>/latest/", 1200.0, "USD"
    # )
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("routes.recurring_routes.get_db")
# pylint: disable=redefined-outer-name
def test_add_recurring_error(mock_get_db, client):
    """Test error handling when a database error occurs."""
    # Mock database connection to raise an exception
    mock_get_db.side_effect = sqlite3.DatabaseError("Mocked database error")

    # Test data
    recurring_data = {
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "category": "Subscription",
        "item": "Streaming Service",
        "location": "Online",
        "price": 1200.0,
        "currency": "USD",
    }

    # Send POST request
    response = client.post("/add_recurring", json=recurring_data)

    # Assertions
    assert response.status_code == 500
    assert response.json == {"error": "An internal error has occurred!"}
    mock_get_db.assert_called_once()


@patch("routes.recurring_routes.get_db")
@patch("routes.recurring_routes.setup_stg.convert_to_sgd")
# pylint: disable=redefined-outer-name
def test_add_recurring_missing_end_date(mock_convert_to_sgd, mock_get_db, client):
    """Test adding a recurring expense without an end date."""
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock currency conversion
    mock_convert_to_sgd.return_value = 100.0

    # Test data
    recurring_data = {
        "start_date": "2025-01-01",
        "category": "Subscription",
        "item": "Streaming Service",
        "location": "Online",
        "price": 100.0,
        "currency": "USD",
    }

    # Send POST request
    response = client.post("/add_recurring", json=recurring_data)

    # Assertions
    assert response.status_code == 200
    assert response.json == {"message": "Recurring expense added successfully"}
    mock_get_db.assert_called_once_with(2025)
    # Skip convert_to_sgd call due to API key
    # mock_convert_to_sgd.assert_called_once_with(
    #    "https://v6.exchangerate-api.com/v6/<api_key>/latest/", 100.0, "USD"
    # )
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()
