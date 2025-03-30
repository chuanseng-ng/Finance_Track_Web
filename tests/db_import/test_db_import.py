"""This module contains unit tests for the db_import module."""

from unittest.mock import patch, MagicMock, call
import pandas as pd
import pytest
from db_import.db_import import (
    month_name_to_int,
    merge_start_date,
    merge_end_date,
    update_database_from_excel,
)


def test_month_name_to_int():
    """Test the month_name_to_int function."""
    assert month_name_to_int("Jan") == 1
    assert month_name_to_int("Feb") == 2
    assert month_name_to_int("Dec") == 12
    assert month_name_to_int("Invalid") is None  # Invalid month name
    assert month_name_to_int("") is None  # Empty string


def test_merge_start_date():
    """Test the merge_start_date function."""
    mock_row = {
        "Start Month": "Jan",
        "Start Year": "2023",
    }
    assert merge_start_date(mock_row) == "2023-01-01"

    mock_row = {
        "Start Month": "-",
        "Start Year": "2023",
    }
    assert merge_start_date(mock_row) == "2023-01-01"  # Default to January 1, 2023

    mock_row = {
        "Start Month": "Invalid",
        "Start Year": "2023",
    }
    assert merge_start_date(mock_row) is None  # Invalid month name


def test_merge_end_date():
    """Test the merge_end_date function."""
    mock_row = {
        "End Month": "Dec",
        "End Year": "2023",
    }
    assert merge_end_date(mock_row) == "2023-12-01"

    mock_row = {
        "End Month": "-",
        "End Year": "2023",
    }
    assert merge_end_date(mock_row) is None  # Default to None if month is missing

    mock_row = {
        "End Month": "Invalid",
        "End Year": "2023",
    }
    assert merge_end_date(mock_row) is None  # Invalid month name


@pytest.fixture
def mock_excel_file(tmp_path):
    """Fixture to create a mock Excel file."""
    # Create data for the "Recurring" sheet
    recurring_data = {
        "Category": ["Category", "Personal", "Utilities", "Subscription"],
        "Item": ["Item", "Piano Lessons", "Electricity", "Streaming Service"],
        "Location": ["Location", "Music School", "Home", "Online"],
        "Price": ["Price", 125, 100, 50],
        "Start Month": ["Start Month", "-", "Jan", "Feb"],
        "Start Year": ["Start Year", "-", "2022", "2023"],
        "End Month": ["End Month", "Dec", "Mar", "-"],
        "End Year": ["End Year", "2024", "2023", "-"],
    }

    # Create data for the "January" sheet
    january_data = {
        "Date": [None, "Date", "2023-01-01", "2023-01-02", "2024-02-24"],
        "Category": [None, "Category", "Food", "Transport", "Entertainment"],
        "Item": [None, "Item", "Groceries", "Bus Fare", "Day Pass"],
        "Location": [None, "Location", "Supermarket", "City Bus", "Climbing Gym"],
        "Price": [None, "Price", 50, 20, None],
        "Remarks": [None, "Remarks", None, "20 USD", None],
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

    expected_calls = [
        call(
            "SELECT COUNT(*) FROM recurring_expenses WHERE\n                    "
            "category = ? AND item = ? AND location = ?",
            ("Personal", "Piano Lessons", "Music School"),
        ),
        call(
            "SELECT COUNT(*) FROM recurring_expenses WHERE\n                    "
            "category = ? AND item = ? AND location = ?",
            ("Utilities", "Electricity", "Home"),
        ),
        call(
            "SELECT COUNT(*) FROM recurring_expenses WHERE\n                    "
            "category = ? AND item = ? AND location = ?",
            ("Subscription", "Streaming Service", "Online"),
        ),
    ]

    # Assertions
    mock_connect.assert_called_once_with("expenses_2023.db")
    mock_cursor.execute.assert_has_calls(expected_calls, any_order=True)
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

    # Mock the cursor's fetchone method to simulate no existing records
    mock_cursor.fetchone.return_value = [0]

    # Call the function
    update_database_from_excel(mock_excel_file, 2023)
    for test_call in mock_cursor.execute.mock_calls:
        print(test_call)
    expected_calls = [
        call(
            "SELECT COUNT(*) FROM expenses WHERE\n                    "
            "category = ? AND item = ? AND location = ?",
            ("Food", "Groceries", "Supermarket"),
        ),
        call(
            "SELECT COUNT(*) FROM expenses WHERE\n                    "
            "category = ? AND item = ? AND location = ?",
            ("Transport", "Bus Fare", "City Bus"),
        ),
    ]

    # Verify the SQL queries executed
    mock_cursor.execute.assert_has_calls(expected_calls, any_order=True)
    mock_conn.commit.assert_called_once()  # Ensure changes were committed
    mock_conn.close.assert_called_once()  # Ensure the connection was closed
