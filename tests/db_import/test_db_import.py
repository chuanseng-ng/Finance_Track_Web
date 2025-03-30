"""This module contains unit tests for the db_import module."""

from unittest.mock import patch, MagicMock
import pandas as pd
import pytest
from db_import.db_import import update_database_from_excel


@pytest.fixture
def mock_excel_file(tmp_path):
    """Fixture to create a mock Excel file."""
    # Create data for the "Recurring" sheet
    recurring_data = {
        "Category": ["Category", "Utilities", "Subscription"],
        "Item": ["Item", "Electricity", "Streaming Service"],
        "Location": ["Location", "Home", "Online"],
        "Price": ["Price", 100, 50],
        "Start Month": ["Start Month", "Jan", "Feb"],
        "Start Year": ["Start Year", "2022", "2023"],
        "End Month": ["End Month", "Mar", "Dec"],
        "End Year": ["End Year", "2023", "2023"],
    }

    # Create data for the "January" sheet
    january_data = {
        "Date": ["", "Date", "2023-01-01", "2023-01-02"],
        "Category": ["", "Category", "Food", "Transport"],
        "Item": ["", "Item", "Groceries", "Bus Fare"],
        "Location": ["", "Location", "Supermarket", "City Bus"],
        "Price": ["", "Price", 50, 20],
        "Remarks": ["", "Remarks", "", "20 USD"],
    }

    # Create the Excel file in the temporary directory
    mock_file_path = tmp_path / "mock_file.xlsx"
    with pd.ExcelWriter(mock_file_path) as writer:
        pd.DataFrame(recurring_data).to_excel(
            writer, sheet_name="Recurring", index=False
        )
        pd.DataFrame(january_data).to_excel(writer, sheet_name="January", index=False)

    return mock_file_path


@patch("db_import.db_import.sqlite3.connect")
def test_update_database_from_excel_recurring(mock_connect, mock_excel_file):
    """Test updating the database with the Recurring sheet."""
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Call the function
    update_database_from_excel(mock_excel_file, 2023)

    # Assertions
    mock_connect.assert_called_once_with("expenses_2023.db")
    mock_cursor.execute.assert_called()  # Ensure SQL queries were executed
    mock_conn.commit.assert_called_once()  # Ensure changes were committed
    mock_conn.close.assert_called_once()  # Ensure the connection was closed


@patch("db_import.db_import.sqlite3.connect")
def test_update_database_from_excel_monthly(mock_connect, mock_excel_file):
    """Test updating the database with monthly sheets."""
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Call the function
    update_database_from_excel(mock_excel_file, 2023)

    # Assertions
    mock_connect.assert_called_once_with("expenses_2023.db")
    mock_cursor.execute.assert_called()  # Ensure SQL queries were executed
    mock_conn.commit.assert_called_once()  # Ensure changes were committed
    mock_conn.close.assert_called_once()  # Ensure the connection was closed
