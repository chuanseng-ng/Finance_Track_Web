"""This module contains tests for the expense_routes module."""

from unittest.mock import patch, MagicMock
import pytest
from flask import Flask
from routes.expense_routes import expense_bp


@pytest.fixture
def client():
    """Fixture to create a Flask test client."""
    app = Flask(__name__)
    app.register_blueprint(expense_bp)
    # pylint: disable=redefined-outer-name
    with app.test_client() as client:
        yield client


@patch("routes.expense_routes.get_db")
@patch("routes.expense_routes.setup_stg.convert_to_sgd")
# pylint: disable=redefined-outer-name
def test_add_expense_success(mock_convert_to_sgd, mock_get_db, client):
    """Test successful addition of an expense."""
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock currency conversion
    mock_convert_to_sgd.return_value = 75.0

    # Test data
    expense_data = {
        "date": "2025-03-26",
        "category": "Food",
        "item": "Lunch",
        "location": "Restaurant",
        "price": 50.0,
        "currency": "USD",
    }

    # Send POST request
    response = client.post("/add_expense", json=expense_data)

    # Assertions
    assert response.status_code == 200
    assert response.json == {"message": "Expense added successfully"}
    mock_get_db.assert_called_once_with(2025)
    # Skip convert_to_sgd call due to API key
    # mock_convert_to_sgd.assert_called_once_with(
    #    "https://v6.exchangerate-api.com/v6/<api_key>/latest/", 50.0, "USD"
    # )
    mock_cursor.execute.assert_called_once()


@patch("routes.expense_routes.get_db")
# pylint: disable=redefined-outer-name
def test_add_expense_error(mock_get_db, client):
    """Test error handling when a KeyError occurs."""
    # Mock database connection
    mock_get_db.side_effect = KeyError("Mocked KeyError")

    # Test data
    expense_data = {
        "date": "2025-03-26",
        "category": "Food",
        "item": "Lunch",
        "location": "Restaurant",
        "price": 50.0,
        "currency": "USD",
    }

    # Send POST request
    response = client.post("/add_expense", json=expense_data)

    # Assertions
    assert response.status_code == 500
    assert response.json == {"error": "An internal error has occurred!"}
