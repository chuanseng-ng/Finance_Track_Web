"""This module contains tests for the plot_routes module."""

import sqlite3
from unittest.mock import patch, MagicMock
import pytest
from flask import Flask
from routes.plot_routes import plot_bp


@pytest.fixture
def client():
    """Fixture to create a Flask test client."""
    app = Flask(__name__, template_folder="../../templates")
    app.register_blueprint(plot_bp)
    # pylint: disable=redefined-outer-name
    with app.test_client() as client:
        yield client


@patch("routes.plot_routes.get_db")
@patch("routes.plot_routes.go.Figure")
# pylint: disable=redefined-outer-name
def test_plot_expenditure_success(mock_figure, mock_get_db, client):
    """Test the plot_expenditure route with Plotly."""
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock monthly data
    mock_cursor.fetchall.side_effect = [
        [("01", 100.0), ("02", 200.0)],  # Monthly data
        [("01", 300.0), ("02", 400.0)],  # Yearly data
    ]

    # Mock Plotly figure methods
    mock_fig_instance = MagicMock()
    mock_figure.return_value = mock_fig_instance
    mock_fig_instance.to_html.side_effect = [
        "<div>Mock Monthly Plot</div>",  # Mock monthly plot HTML
        "<div>Mock Yearly Plot</div>",  # Mock yearly plot HTML
    ]

    # Send GET request
    response = client.get("/plot_expenditure")

    print(response.data)
    # Assertions
    assert response.status_code == 200
    assert (
        b"<div>Mock Monthly Plot</div>" in response.data
    )  # Ensure the plot HTML is rendered
    assert (
        b"<div>Mock Yearly Plot</div>" in response.data
    )  # Ensure the plot HTML is rendered
    mock_get_db.assert_called_once()
    assert mock_cursor.execute.call_count == 2  # Ensure both queries were executed
    mock_figure.assert_called()  # Ensure Plotly figure was created
    assert mock_fig_instance.add_trace.call_count == 2  # Ensure traces were added
    assert mock_fig_instance.update_layout.call_count == 2  # Ensure layout was updated
    assert mock_fig_instance.to_html.call_count == 2  # Ensure HTML was generated


@patch("routes.plot_routes.get_db")
@patch("routes.plot_routes.go.Figure")
# pylint: disable=redefined-outer-name
def test_plot_custom_expenditure_success(mock_figure, mock_get_db, client):
    """Test the plot_custom_expenditure route with Plotly."""
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock custom data
    mock_cursor.fetchall.return_value = [
        ("2023-11-01", 150.0),
        ("2023-11-02", 250.0),
    ]

    # Mock Plotly figure methods
    mock_fig_instance = MagicMock()
    mock_figure.return_value = mock_fig_instance
    mock_fig_instance.to_html.return_value = "<div>Mock Custom Plot</div>"

    # Send GET request with query parameters
    response = client.get(
        "/plot_custom_expenditure?start_date=2023-11-01&end_date=2023-11-02"
    )

    # Assertions
    assert response.status_code == 200
    assert (
        b"<div>Mock Custom Plot</div>" in response.data
    )  # Ensure the plot HTML is rendered
    mock_get_db.assert_called_once()
    mock_cursor.execute.assert_called_once()  # Ensure the query was executed
    mock_figure.assert_called()  # Ensure Plotly figure was created
    mock_fig_instance.add_trace.assert_called()  # Ensure traces were added
    mock_fig_instance.update_layout.assert_called()  # Ensure layout was updated
    mock_fig_instance.to_html.assert_called_once()  # Ensure HTML was generated


@patch("routes.plot_routes.get_db")
# pylint: disable=redefined-outer-name
def test_plot_expenditure_error(mock_get_db, client):
    """Test error handling for the /plot_expenditure route."""
    # Mock database connection to raise an exception
    mock_get_db.side_effect = sqlite3.DatabaseError("Mocked database error")

    # Send GET request
    response = client.get("/plot_expenditure")

    # Assertions
    assert response.status_code == 500
    assert response.json == {"error": "An internal error has occurred!"}
    mock_get_db.assert_called_once()


@patch("routes.plot_routes.get_db")
# pylint: disable=redefined-outer-name
def test_plot_custom_expenditure_missing_params(mock_get_db, client):
    """Test error handling for missing query parameters in /plot_custom_expenditure."""
    # Send GET request without query parameters
    response = client.get("/plot_custom_expenditure")

    # Assertions
    assert response.status_code == 400
    assert response.json == {"error": "Start date and end date are required"}
    mock_get_db.assert_not_called()


@patch("routes.plot_routes.get_db")
# pylint: disable=redefined-outer-name
def test_plot_custom_expenditure_error(mock_get_db, client):
    """Test error handling for the /plot_custom_expenditure route."""
    # Mock database connection to raise an exception
    mock_get_db.side_effect = sqlite3.DatabaseError("Mocked database error")

    # Send GET request
    response = client.get(
        "/plot_custom_expenditure?start_date=2025-03-01&end_date=2025-03-02"
    )

    # Assertions
    assert response.status_code == 500
    assert response.json == {"error": "An internal error has occurred!"}
    mock_get_db.assert_called_once()
